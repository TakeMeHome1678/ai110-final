# Applied AI Workbench

## Summary

Applied AI Workbench evolved the original guessing-game repository into a local AI workbench that summarizes text, retrieves evidence from a knowledge base, plans bounded steps, and produces debugging guidance. It matters because it demonstrates RAG and agentic behavior as integrated application features rather than isolated scripts.

## Architecture Overview

The Streamlit interface validates input and sends the request to the agent controller. The controller classifies the task, creates a plan, retrieves relevant passages, executes the appropriate local tool, computes a confidence score, and records JSONL and log output. Humans can review evidence and edit the source library; automated tests check retrieval, summarization, planning, confidence, and missing-evidence behavior. The full Mermaid source is at [diagrams/architecture.mmd](diagrams/architecture.mmd).

## Setup Instructions

1. Install Python 3.10 or newer.
2. Clone the repository:

```bash
git clone https://github.com/TakeMeHome1678/ai110-final.git
cd ai110-final
```

3. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Run the application:

```bash
python -m streamlit run app.py
```

6. Open the local URL printed by Streamlit.

## Features

- **RAG:** Added documents are stored in `data/knowledge.json` and retrieved with cosine similarity. Retrieval evidence is shown beside the answer.
- **Agentic workflow:** Requests are classified, planned, executed by a tool, checked for confidence, and logged.
- **Reliability system:** Empty input is rejected, missing evidence produces a low-confidence response, execution failures are logged, and pytest protects key behavior.
- **Specialized behavior:** The agent uses constrained summaries and a Python debugging workflow rather than giving undifferentiated text answers.

## Sample Interactions

### 1. Summarize text

**Input:** Paste “Retrieval augmented generation ranks relevant passages before creating an answer. It should not invent facts when evidence is missing.”

**Result:** The system returns an extractive summary containing the source’s key statements and a direct confidence value.

### 2. Retrieve debugging knowledge

**Input:** “How should I debug a failing Python test?”

**Result:** The agent returns a three-step debugging workflow and cites the Python debugging source from `data/knowledge.json`.

### 3. No-evidence retrieval

**Input:** “Retrieve the price of a secret planet.”

**Result:** The system says it cannot retrieve supporting information and assigns low confidence instead of inventing an answer.

## Design Decisions

I used standard Python and Streamlit to keep setup reproducible and avoid an API-key dependency. Lexical cosine retrieval is transparent and easy to test, but it is weaker than semantic embeddings for paraphrases. Extractive summarization preserves source wording and avoids unsupported generation. A compact JSONL trace makes agent behavior inspectable without exposing hidden or private chain-of-thought text.

## Testing Summary

Run the suite with:

```bash
python -m pytest -q
```

The test harness checks matching and unrelated retrieval, summary behavior, request classification, multi-step plans, low-evidence handling, and confidence bounds. Human evaluation is recorded in [model_card.md](model_card.md).

```text
12 passed in 0.01s
```

Run the predefined evaluation harness with:

```bash
python evaluate.py
```

```text
PASS | Debug retrieval | kind=debug | confidence=0.57 | evidence=1
PASS | Summarization | kind=summarize | confidence=0.35 | evidence=0
PASS | Missing evidence | kind=retrieve | confidence=0.25 | evidence=0
SUMMARY: 3/3 passed; 100% pass rate
```

If a test fails, the implementation should show the exact assertion and traceback so a developer can reproduce and isolate the issue.

## Reflection

This project changed my view of AI systems from “one model response” to a coordinated pipeline of inputs, retrieval, planning, tool execution, testing, and human review. The clearest lesson was that guardrails and evidence are useful not only as safety features, but also as engineering controls that make outputs easier to verify.

During development, I used AI to propose the RAG/agent structure and to locate the original app’s logic. I accepted the suggestion to separate retrieval, planning, and UI concerns because it produced focused testable modules. I revised an initial decimal-parser suggestion that used `int(float(raw))`, because it silently truncated a decimal instead of rejecting invalid input. Future improvements would add semantic embeddings, a larger multi-source index, and stronger human-evaluation procedures.

### RAG Enhancement: Before and After

Before custom sources were added, the system could only answer from four built-in documents in `data/knowledge.json`. It now supports user-defined title/text sources through the Streamlit UI. In a before-style request for an unrelated topic, the no-evidence result is stable; after adding a relevant document, the same topic can retrieve that source and include its score and text in the answer instead of returning the generic no-evidence response.

Responsible-AI limitations and misuse considerations are documented in [model_card.md](model_card.md). Development interaction traces are documented in [ai_interactions.md](ai_interactions.md).

## Repository Structure

```text
app.py                 Streamlit application
rag_utils.py           Retrieval and extractive summarization
agent_utils.py         Agent planning, execution, confidence, and logs
data/knowledge.json    Built-in and user-added sources
diagrams/architecture.mmd  Mermaid system architecture
assets/                Exported architecture images
logs/                  Runtime logs and execution traces
model_card.md          Limitations, misuse, and human evaluation
ai_interactions.md     Agent workflow and interaction trace log
tests/test_applied_ai.py Automated reliability tests
```
