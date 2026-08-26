RICE-POT Plan: Jira Test Case Generator App

Objective
- Provide a concise, RICE-POT-compliant implementation plan (output-first) for a two-screen Streamlit app that: accepts a natural-language chat request to "create test cases for <JIRA-KEY>", fetches the Jira ticket using stored credentials, merges ticket content into a local template, and generates structured test cases using a local Ollama model with Groq as fallback.

Deliverables (file list)
- app.py                     -- Streamlit main chat screen (single-file app or multipage entry)
- pages/settings.py          -- Streamlit Settings screen (persisted config UI)
- config_store.py            -- Read/write persisted settings (JSON or SQLite); excluded from VCS via .gitignore
- jira_client.py             -- Jira REST API wrapper: fetch ticket fields (summary, description, acceptance criteria, attachments meta)
- llm_client.py              -- Ollama (primary) + Groq (fallback) call layer, provider selection and health-checking
- templates/                 -- Folder containing at least one test-case-template.md (template variables / tokens)
- requirements.txt           -- Minimal dependencies (streamlit, requests, python-dotenv, python-box or pydantic optional)
- README.md                  -- Setup and run instructions, security guidelines (no secrets in repo)
- .gitignore                 -- include config JSON/DB and .env

High-level UX: two screens
- Screen 1 — Chat (app.py)
  - Single-column Streamlit layout: chat history pane, message input box, Send button, optional ticket-key quick-paste
  - When user sends a message: parse JIRA key, if found run the end-to-end flow; otherwise allow free-text that can be used to prompt LLM directly
  - Display LLM responses as chat messages; provide an Export button to save generated test cases to /outputs as .md or .xlsx

- Screen 2 — Settings (pages/settings.py)
  - Inputs: Jira Base URL, Jira Email ID, Jira API Token (password input), LLM Provider selection (radio: Ollama [default] / Groq), Groq API key (password input)
  - Buttons: Save, Test Jira Credentials, Test LLM Endpoint
  - Persist settings via config_store (local JSON or lightweight SQLite). Ensure persisted file is added to .gitignore.

Data flow and runtime sequence (detailed)
1) User types: "create test cases for JIRA-102" and clicks Send.
2) Message parser extracts ticket key (regex: [A-Z]+-\d+). If none, ask clarifying question.
3) Config lookup: read saved Jira and LLM settings from config_store.
   - If settings missing: show an inline error with a link to Settings screen.
4) Jira fetch: jira_client.get_issue(ticket_key) -> returns summary, description, acceptance criteria (AC). If API call fails, surface HTTP status and message.
5) Template load: load templates/test_case_template.md and substitute ticket fields into placeholders (summary, description, AC). This becomes the LLM prompt payload.
6) LLM selection & call: llm_client.send_prompt(prompt_text)
   - llm_client first attempts to call Ollama (http://localhost:11434, model gemma3:1b) with a health-check and small timeout.
   - If Ollama is unreachable OR user selected Groq explicitly, call Groq with the Groq key, and rate-limit/backoff on retry.
   - llm_client returns structured output (preferably JSON or markdown). If the model returns free text, run a light parser to extract test-case structure.
7) Render: Display generated test cases in the chat pane, plus buttons for Save (.md/.xlsx), Edit, or Copy to clipboard.
8) Persistence: Optionally save a record of generation (ticket key, timestamp, provider used, saved artifact path) in config_store's history table/file.

Error handling and fallbacks
- Ollama health-check: GET /health or simple POST with short timeout; if 5xx / timeout → fallback to Groq.
- Jira call errors: 401 -> prompt user to re-enter credentials; 404 -> show "ticket not found"; other -> show status and raw error.
- LLM failure: show model error and offer Retry or Switch Provider.

Security & secrets handling
- Never hardcode Jira tokens or Groq keys in source.
- Persist secrets in a local config file (JSON or SQLite) with file system permissions restricted (e.g., chmod 600 on *nix). Add that config file to .gitignore.
- Support reading secrets from environment variables for CI (JIRA_EMAIL, JIRA_TOKEN, GROQ_API_KEY) and document recommended GitHub Actions secrets usage in README.
- The app must not print secret values to stdout or logs.

Template design
- Provide templates/test_case_template.md with variables like {{summary}}, {{description}}, {{acceptance_criteria}}, {{jira_id}}.
- Template should include sections: Preconditions, Steps, Expected Results, Priority, Notes.

Implementation plan (stepwise; wait for approval before coding)
Step 0 — Confirm: get approval of this plan, file list, and data flow. I will not write code until approval.
Step 1 — Scaffolding: create repository layout, add requirements.txt, .gitignore, templates/test_case_template.md, README.md.
Step 2 — config_store.py: implement a small JSON-backed store with get_settings(), save_settings(), and get_history()/append_history(). Ensure file is excluded from VCS.
Step 3 — jira_client.py: implement get_issue(ticket_key) using requests and Jira REST (basic auth with email:token). Unit-test with a mocked response.
Step 4 — llm_client.py: implement send_prompt(prompt, provider_preference=None) with Ollama primary and Groq fallback. Implement health_check().
Step 5 — app.py: Streamlit chat interface connecting pieces; wire Send to run the flow; provide Export functionality into /outputs.
Step 6 — pages/settings.py: Streamlit settings page to capture and persist settings, plus Test buttons that call jira_client and llm_client health_check.
Step 7 — Manual QA: run the app locally, test typical sequence, add a minimal test for jira_client and llm_client with mocked dependency.
Step 8 — Deliverables: final README with run instructions, notes about Ollama (assumed local gemma3:1b), and Groq fallback.

Acceptance criteria
- UI has two screens with the described fields/controls.
- Sending a message with a JIRA key results in a successful flow using stored credentials when valid.
- Ollama is attempted first; if unreachable, Groq is used only when configured or on failure.
- No secrets are present in repo; saved config file is added to .gitignore.
- Templates are used and the output contains the test-case structure.

Testing notes
- Provide environment variables or a local config with test Jira credentials to validate full round-trip. Use a Jira test project/ticket for safe testing.
- For unit tests, use pytest and responses or requests-mock to simulate Jira and Ollama/Groq responses.

Questions / approvals needed (pick one)
- Approve this plan as-is so implementation can begin.
- Request changes to file names, storage format (prefer SQLite over JSON), or template structure.
- Confirm whether Groq should be allowed for interactive selection per-run, or only as automatic fallback.

Next action after approval
- Start Step 1 (scaffold) and open a PR with the added files for quick review. Implementation will proceed module-by-module with small commits and tests.

--
Generated to match the RICE-POT Prompt in chapter_03_Local_TestCase_Generator/prompts.md. Waiting for your approval before creating any code files.
