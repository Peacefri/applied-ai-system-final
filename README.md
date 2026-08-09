# PawPal Plus

## Title and Summary

**Base project:** PawPal+ Module 2 starter project (`ai110-module2show-pawpal-starter`).

**PawPal Plus** is a Streamlit pet-care planning app for an owner who needs to
track pets, care tasks, schedules, completion status, and time conflicts. The
original app goal was to make everyday pet care easier to organize by creating
an owner, adding pets, adding tasks, completing tasks, and generating a daily
schedule. It now also includes a retrieval-augmented Q&A assistant that uses
the owner's actual PawPal data before answering questions.

This matters because a generic chatbot could invent whether a pet was walked
or what is due next. PawPal Plus retrieves the stored records first and tells
the AI to answer only from that context.

## Main Features

- Create an owner and add pets with species, health status, and energy level.
- Add one-time, daily, or weekly care tasks with duration, priority, due date,
  and optional start time.
- Complete tasks and automatically create the next occurrence for recurring
  tasks.
- Generate a daily schedule and detect overlapping scheduled tasks.
- Ask questions such as `Did I already walk Mochi today?` or
  `What's due this afternoon?`.
- Use OpenAI for natural-language answers when `OPENAI_API_KEY` is configured,
  with a deterministic grounded fallback when it is not.

## Architecture Overview

The system architecture and data flow are shown in
[diagrams/system_diagram.mmd](diagrams/system_diagram.mmd). The Streamlit UI
sends an owner's question to `PawPalAssistant`. The retriever ranks the
owner's real pet and task records, formats them as grounded context, and sends
that context to the answer generator. A prompt guardrail tells the generator
not to invent data; if the API is unavailable, a local fallback answers from
the same retrieved records. Automated tests check retrieval and fallback
behavior, while a human reviews whether answers are accurate and useful.

The existing object model is documented in
[diagrams/uml.mmd](diagrams/uml.mmd).

## Setup Instructions

1. Clone the repository and open the project folder in VS Code.
2. Create a virtual environment:

   **Windows PowerShell:**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Optional: configure OpenAI-generated answers. The app still runs without a
   key by using the local grounded fallback.

   **Windows PowerShell:**

   ```powershell
   $env:OPENAI_API_KEY = "your-api-key"
   ```

   **macOS/Linux:**

   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

   You can also set `OPENAI_MODEL`; the default is `gpt-4o-mini`.

## Sample Interactions

These examples assume an owner named Jordan has a pet named Mochi, with a
completed Walk task and an open Feed dinner task stored in PawPal.

**Example 1: completed-task lookup**

```text
Input: Did I already walk Mochi today?
Output: Yes. I found completed care for Mochi's Walk.
```

**Example 2: open-task schedule lookup**

```text
Input: What's due this afternoon?
Output: Open PawPal tasks: Mochi's Feed dinner (18:00).
```

**Example 3: pet-task retrieval**

```text
Input: What tasks are on Mochi's schedule?
Output: I found these related PawPal tasks: Mochi's Walk, Mochi's Feed dinner.
```

The OpenAI response may use slightly different wording, but it receives the
retrieved records in its prompt. Without an API key, the deterministic
fallback produces the style of output shown above.

## Design Decisions

- **Structured retrieval instead of a separate document store:** PawPal's
  source of truth is already the in-memory `Owner`, `Pet`, and `Task` model, so
  retrieving directly from it avoids stale copies and keeps the demo easy to
  reproduce.
- **Keyword ranking instead of embeddings:** The task collection is small and
  questions are simple. Keyword scoring is transparent and has no model
  download or vector database requirement. The trade-off is that synonyms and
  complex language are not retrieved as well as they would be with embeddings.
- **Optional OpenAI provider plus local fallback:** OpenAI gives more natural
  answers, but requires a key and network access. The fallback makes the app
  runnable for grading and demos without external services.
- **Prompt grounding and logging:** The prompt instructs the generator to use
  only retrieved context. The assistant logs each question and logs an
  exception if generation fails before using the fallback. It never prints or
  logs the API key.
- **In-memory state:** Streamlit session state keeps the current demo data
  during a session. This keeps the project small, but data is not persistent
  across restarts.

## Testing Summary

Run the full test suite with:

```bash
python -m pytest
```

The project currently passes the scheduling tests and the AI tests. The AI
tests verify that retrieved context contains actual pet/task fields, that a
custom generator receives that context, and that the no-key fallback gives a
grounded response. They also simulate a provider failure and verify that the
assistant logs the failure and returns grounded fallback output. The latest
run passed **18 out of 18 tests**. The system does not test live OpenAI calls
because that would require a secret, network access, and a variable external
service.

The main lesson from testing was that a successful AI answer is not enough:
the test must also prove which application data was retrieved and supplied to
the generator.

## Project Files

- [app.py](app.py): Streamlit interface, scheduling controls, and Q&A box.
- [pawpal_system.py](pawpal_system.py): owner, pet, task, and scheduler logic.
- [pawpal_ai.py](pawpal_ai.py): retrieval, grounded prompt, OpenAI provider,
  logging, and local fallback.
- [tests/test_pawpal_system.py](tests/test_pawpal_system.py): scheduling tests.
- [tests/test_pawpal_ai.py](tests/test_pawpal_ai.py): RAG and fallback tests.
- [model_card.md](model_card.md): reflection, evaluation, and limitations.
- [execution_log.md](execution_log.md): reproducible test commands and Streamlit interaction log.
