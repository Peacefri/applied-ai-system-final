# PawPal Plus Reproducible Execution Evidence

This log records commands that can be repeated from the project root:
`C:\Users\pamic\OneDrive\applied-ai-system-final`.

## Environment

```text
Python: 3.14.5
Environment: .venv
Operating system: Windows
```

## Automated Tests

### Command

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### Result

```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\pamic\OneDrive\applied-ai-system-final
configfile: pytest.ini
collected 18 items

tests\test_pawpal_ai.py ....                                             [ 22%]
tests\test_pawpal_system.py ..............                               [100%]

============================== 18 passed in 0.06s ==============================
```

The tests cover scheduling, recurring tasks, conflict detection, retrieval of
real pet/task data, grounded prompt construction, no-key fallback behavior,
and recovery after a simulated AI provider failure.

## Syntax Check

### Command

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py pawpal_ai.py
```

### Result

```text
Process completed successfully with no syntax errors.
```

## Streamlit Interaction Log

### Start command

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open `http://localhost:8501`.

### Reproducible interaction

1. Set the owner name to `Jordan`.
2. Add a pet named `Mochi`, species `cat`, health status `healthy`, and energy
   level `80`.
3. Add a task for Mochi named `Walk`, duration `30`, priority `high`, scheduled
   at `15:00`, and mark it complete.
4. Add an open task named `Feed dinner`, duration `10`, priority `medium`,
   scheduled at `18:00`.
5. In **Ask PawPal+**, enter:

   ```text
   Did I already walk Mochi today?
   ```

6. With no `OPENAI_API_KEY`, the deterministic grounded fallback reports that
   Mochi's Walk task is completed. With an API key, the OpenAI response is
   generated from the retrieved task context.

The app's state is held in Streamlit session state, so these steps should be
performed in one browser session.
