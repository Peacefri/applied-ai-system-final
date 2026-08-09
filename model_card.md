# PawPal Plus Model Card

## System Summary

PawPal Plus is a pet-care planning app with a retrieval-augmented Q&A feature.
The application retrieves the current owner's pet and task records, places the
relevant records into a constrained prompt, and asks an OpenAI model to answer
the owner's question. When no API key is available or generation fails, the
system uses a deterministic local response based on the same retrieved data.

## Intended Use

The assistant is intended for simple personal organization questions such as:

- whether a pet's task is marked complete;
- what open tasks are scheduled; and
- which care tasks are related to a pet or time of day.

It is not a veterinary diagnostic system and should not replace professional
medical advice.

## Data and Retrieval

The source data is entered by the user during the Streamlit session. It
includes owner names, pet information, task names, due dates, times, priority,
duration, recurrence, and completion status. Retrieval uses transparent
keyword overlap with extra relevance for words such as `today`, `due`,
`morning`, and `afternoon`. The retrieved task records are serialized into the
prompt so the generated answer is grounded in application data.

## Evaluation and Testing

Automated tests verify three important behaviors:

1. Retrieved context contains the actual pet name, task name, date, and status.
2. A generator receives the retrieved context rather than an empty or generic
   prompt.
3. The application gives a grounded fallback answer when no API key is set.
4. A simulated provider failure returns grounded fallback output instead of
  crashing.

The scheduling suite also checks sorting, recurring tasks, completion, and
conflict detection. Live model quality is not measured because it depends on
an external API and would require a separate labeled question-and-answer test
set. The latest automated run passed **18 out of 18 tests**. Human review is
still needed to judge whether the wording is useful and whether a retrieved
record actually answers a particular question.

## Limitations and Biases

- Keyword retrieval can miss synonyms, spelling variations, and complicated
  questions.
- Keyword overlap can favor a task with common words over the task the owner
  intended, especially when several pets have similarly named tasks.
- The model can still misunderstand a retrieved record, so answers should be
  checked against the schedule for important decisions.
- The app stores data only in Streamlit session state and has no authentication
  or persistent database.
- OpenAI mode requires internet access and an API key; API availability and
  output wording can vary.
- The assistant is for organization only. It should not make veterinary,
  emergency, medication, or safety decisions without human judgment.

Because the system learns from user-entered records rather than a broad
training dataset, it does not infer whether a pet's care plan is medically
appropriate. Its main bias comes from the retrieval rules: exact words and a
few time-of-day keywords receive more weight than meaning or synonyms.

## Misuse Prevention

The assistant could be misused if someone treated its answer as veterinary
advice, relied on an incorrect completion status, or entered sensitive
information into an external AI provider. PawPal Plus reduces these risks by:

- restricting the prompt to retrieved PawPal records and instructing the model
  not to invent facts;
- providing a local fallback when the provider is unavailable;
- logging provider failures without logging the API key;
- clearly limiting the intended use to organization, not medical or emergency
  decisions; and
- requiring human review for important care decisions.

The app should not be used to make emergency, medication, or health decisions,
and an API key should be stored as an environment variable rather than in the
source code.

## What Surprised Me During Reliability Testing

The most important surprise was that a fluent AI answer alone did not prove
that retrieval worked. The tests had to inspect the prompt and confirm that it
contained the actual pet name, task name, date, and completion status. It was
also useful to simulate a provider failure: the app could still answer from
the retrieved records instead of crashing. The final automated run passed
**18 out of 18 tests**, but it also showed that live model quality still needs
human evaluation because wording and interpretation are not fully captured by
unit tests.

## Collaboration With AI

AI collaboration helped me identify a clean separation between the core
PawPal data model, retrieval, answer generation, and the Streamlit interface.

**Helpful suggestion:** Injecting a generator function into `PawPalAssistant`
made it possible to test grounding without calling an external API or exposing
a secret. This directly led to a test that checks whether the AI receives the
real retrieved task context.

**Flawed suggestion:** An initial suggestion treated the OpenAI import as if it
were automatically available. The project did not declare or install the
`openai` package, so Pylance reported an unresolved import. I corrected this
by adding `openai>=1.0` to `requirements.txt` and installing it in the selected
virtual environment.

## Reflection

This project taught me that useful AI is not just adding a chatbot box. The
important problem-solving step was deciding what trusted application data the
assistant should retrieve before it answers. Testing the context passed to the
generator made the RAG behavior visible and testable instead of assuming that
an apparently fluent answer was correct.
