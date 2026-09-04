# AITestBlueprint4X

A hands-on, chapter-based guide to applying LLMs to software testing — from prompt engineering fundamentals to a working, local-first AI test case generator.

## What's inside

This repository walks through three learning tracks:

| Chapter | Focus | Contents |
| --- | --- | --- |
| `chapter_01_LLM_BASICS/` | LLM fundamentals for QA | Anti-hallucination rules, sample PRD-based test cases (with and without hallucination), based on the VWO Login Dashboard PRD |
| `chapter_02_Prompt_Eng/` | Prompt engineering for testing | The **RICE-POT** prompt framework (Role, Instructions, Context, Expected, Parameters, Output, Tone), test plan / test case generation prompts, and a large library of reusable prompt templates (STLC, API testing, Selenium, Playwright, safety guardrails) |
| `chapter_03_Local_TestCase_Generator/` | Build a real AI tool | A Streamlit app that turns a Jira ticket into structured test cases using a local LLM (Ollama) with a hosted fallback (Groq) |

## Quick start: Local Test Case Generator

The app in `chapter_03_Local_TestCase_Generator/` lets you type `create test cases for JIRA-102` and get a structured test case draft.

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com) running locally with the `gemma3:1b` model (default backend)
- A Jira Cloud account with an API token
- (Optional) A Groq API key for fallback

### Setup

```bash
cd chapter_03_Local_TestCase_Generator/src
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

### How it works

1. **Chat screen** — enter a message like `create test cases for QA-102` and click Send.
2. The app parses the Jira ticket key, fetches the ticket (summary, description, acceptance criteria) via the Jira REST API.
3. Ticket content is merged into `templates/test_case_template.md`.
4. The prompt goes to **Ollama first**; if Ollama is unreachable or Groq is selected in Settings, it falls back to **Groq**.
5. Generated test cases render back in the chat pane.

### Configuration

- Open the **Settings** page to enter and persist: Jira URL, Jira email, Jira API token, LLM provider (Ollama default / Groq), and Groq API key.
- Credentials are stored locally in `config.json` (gitignored) — never hardcode secrets. Environment variables are also supported (`JIRA_EMAIL`, `JIRA_TOKEN`, `GROQ_API_KEY`, `OLLAMA_URL`).

## Prompt engineering framework (RICE-POT)

The core prompt recipe used across this repo:

- **R**ole — the expertise the model should adopt
- **I**nstructions — what to do, step by step
- **C**ontext — background information
- **E**xpected — success criteria
- **P**arameters — constraints and inputs
- **O**utput — required format
- **T**one — style guidance

## Prompt template library

`chapter_02_Prompt_Eng/prompt_templates_Pramod/` contains a large set of reusable, task-specific skills:

- **STLC** — requirement analysis, test planning, test design, test case development, execution, defect management, closure
- **API testing** — contract validation, workflow testing, authorization boundary, performance planning
- **Selenium** — page object building, locator strategy, flaky debugging, grid configuration
- **Playwright** — test generation, trace analysis, visual regression, network mocking
- **Safety guardrails** — prompt injection, sensitive-data leakage, AI bias, content safety

## Notes

- Chapter 1 emphasizes **anti-hallucination** guardrails for LLM-based QA: only assert what's traceable to the PRD, mark inferences, and self-validate.
- The generator app is a lightweight internal QA tool, not a production SaaS product — minimal dependencies, no over-engineering.
