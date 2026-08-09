from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import date
from typing import Callable

from pawpal_system import Owner, Task, formatTime

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedTask:
    """A task plus the pet it belongs to and its retrieval relevance."""

    pet_name: str
    task: Task
    score: int


class PawPalAssistant:
    """Answer owner questions using retrieved PawPal task data as context."""

    def __init__(
        self,
        owner: Owner,
        generator: Callable[[str], str] | None = None,
        model: str | None = None,
    ) -> None:
        self.owner = owner
        self.generator = generator
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def retrieve(self, question: str, limit: int = 8) -> list[RetrievedTask]:
        """Rank the owner's tasks by overlap with the question."""
        question_lower = question.lower()
        question_words = set(re.findall(r"[a-z0-9]+", question_lower))
        today = date.today()
        results: list[RetrievedTask] = []

        for pet in self.owner.pets:
            for task in pet.tasks:
                searchable = {
                    *re.findall(r"[a-z0-9]+", pet.name.lower()),
                    *re.findall(r"[a-z0-9]+", task.name.lower()),
                    task.dueDate.isoformat(),
                    "completed" if task.isCompleted else "open",
                    task.recurrence.value if task.recurrence else "one-time",
                }
                score = len(question_words & searchable)
                if task.dueDate == today and "today" in question_words:
                    score += 4
                if not task.isCompleted and {"due", "need", "needs"} & question_words:
                    score += 2
                if task.startTime is not None:
                    if "afternoon" in question_words and 12 * 60 <= task.startTime < 18 * 60:
                        score += 4
                    if "morning" in question_words and task.startTime < 12 * 60:
                        score += 4
                results.append(RetrievedTask(pet.name, task, score))

        return sorted(
            results,
            key=lambda item: (-item.score, item.task.dueDate, item.task.startTime is None, item.task.startTime or 0),
        )[:limit]

    def build_context(self, question: str) -> str:
        """Create the grounded context sent to the answer generator."""
        retrieved = self.retrieve(question)
        if not retrieved:
            return "No pets or tasks are currently stored."

        lines = [f"Owner: {self.owner.name}", "Tasks retrieved from PawPal:"]
        for item in retrieved:
            task = item.task
            time_text = formatTime(task.startTime) if task.startTime is not None else "unscheduled"
            status = "completed" if task.isCompleted else "open"
            lines.append(
                f"- pet={item.pet_name}; task={task.name}; due={task.dueDate.isoformat()}; "
                f"time={time_text}; duration={task.durationMinutes} minutes; status={status}; "
                f"priority={task.priority.value}"
            )
        return "\n".join(lines)

    def answer(self, question: str) -> str:
        """Generate a grounded answer, falling back safely when no API is configured."""
        question = question.strip()
        if not question:
            return "Ask me about a pet's tasks, completed care, or today's schedule."

        context = self.build_context(question)
        prompt = (
            "You are PawPal+, a careful pet-care assistant. Answer the owner's question "
            "using only the retrieved PawPal context below. Do not invent tasks, dates, "
            "or completion states. If the context does not contain the answer, say that "
            "clearly. Keep the answer concise and mention the pet and time when useful.\n\n"
            f"Owner question: {question}\n\n{context}"
        )
        logger.info("PawPal Q&A retrieved context for question=%r", question)

        try:
            if self.generator is not None:
                return self.generator(prompt).strip()
            if os.getenv("OPENAI_API_KEY"):
                from openai import OpenAI

                response = OpenAI().responses.create(model=self.model, input=prompt)
                return response.output_text.strip()
        except Exception:
            logger.exception("PawPal AI generation failed; using grounded fallback")

        return self._local_answer(question)

    def _local_answer(self, question: str) -> str:
        """Provide a deterministic grounded answer when an LLM is unavailable."""
        retrieved = self.retrieve(question)
        question_lower = question.lower()
        if not retrieved:
            return "I do not have any pet tasks to check yet."

        if "already" in question_lower or "completed" in question_lower or "done" in question_lower:
            completed = [item for item in retrieved if item.task.isCompleted]
            if completed:
                details = ", ".join(f"{item.pet_name}'s {item.task.name}" for item in completed)
                return f"Yes. I found completed care for {details}."
            return "I could not find a completed task matching that question."

        open_tasks = [item for item in retrieved if not item.task.isCompleted]
        if "due" in question_lower or "schedule" in question_lower:
            if not open_tasks:
                return "There are no open tasks in the retrieved PawPal data."
            details = ", ".join(
                f"{item.pet_name}'s {item.task.name} ({formatTime(item.task.startTime) if item.task.startTime is not None else 'unscheduled'})"
                for item in open_tasks
            )
            return f"Open PawPal tasks: {details}."

        details = ", ".join(f"{item.pet_name}'s {item.task.name}" for item in retrieved)
        return f"I found these related PawPal tasks: {details}."
