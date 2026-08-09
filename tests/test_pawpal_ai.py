from datetime import date

from pawpal_ai import PawPalAssistant
from pawpal_system import Owner, Pet, Priority, Task


def make_owner() -> Owner:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)
    pet.addTask(
        Task(
            taskID="walk-1",
            name="Walk",
            priority=Priority.High,
            durationMinutes=30,
            startTime=15 * 60,
            dueDate=date.today(),
            isCompleted=True,
        )
    )
    pet.addTask(
        Task(
            taskID="feed-1",
            name="Feed dinner",
            priority=Priority.Med,
            durationMinutes=10,
            startTime=18 * 60,
            dueDate=date.today(),
        )
    )
    owner.addPet(pet)
    return owner


def test_retrieval_context_contains_actual_pet_task_data() -> None:
    assistant = PawPalAssistant(make_owner())

    context = assistant.build_context("Did I already walk Mochi today?")

    assert "pet=Mochi" in context
    assert "task=Walk" in context
    assert "status=completed" in context
    assert "task=Feed dinner" in context


def test_answer_passes_retrieved_context_to_generator() -> None:
    prompts: list[str] = []

    def fake_generator(prompt: str) -> str:
        prompts.append(prompt)
        return "Yes, Mochi's walk is marked completed."

    answer = PawPalAssistant(make_owner(), generator=fake_generator).answer(
        "Did I already walk Mochi today?"
    )

    assert answer == "Yes, Mochi's walk is marked completed."
    assert len(prompts) == 1
    assert "status=completed" in prompts[0]
    assert "Owner question: Did I already walk Mochi today?" in prompts[0]


def test_answer_uses_grounded_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    answer = PawPalAssistant(make_owner()).answer("Did I already walk Mochi today?")

    assert "Mochi's Walk" in answer
    assert "completed" in answer


def test_answer_falls_back_when_generator_fails() -> None:
    def failing_generator(prompt: str) -> str:
        raise RuntimeError("simulated provider failure")

    answer = PawPalAssistant(make_owner(), generator=failing_generator).answer(
        "Did I already walk Mochi today?"
    )

    assert "Mochi's Walk" in answer
    assert "completed" in answer
