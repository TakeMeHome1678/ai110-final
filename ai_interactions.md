# AI Interaction and Agent Trace Log

## Agent Workflow

The application performs these steps:

1. Classify the request as summarize, retrieve, plan, or debug.
2. Generate a short, checkable plan.
3. Retrieve ranked source passages using cosine similarity.
4. Execute the selected local tool.
5. Calculate confidence and append a JSONL execution trace.

## Example Interaction Trace

```json
{
  "task": "How should I debug a failing Python test?",
  "kind": "debug",
  "plan": [
    {"step": 1, "action": "Identify error symptoms", "status": "completed"},
    {"step": 2, "action": "Map symptoms to likely causes", "status": "completed"},
    {"step": 3, "action": "Suggest a minimal reproduction and fix", "status": "completed"}
  ],
  "confidence": 0.82,
  "review": "Human-readable trace recorded by agent_utils.write_trace"
}
```

Live execution traces are appended to `logs/trace.jsonl`, and system errors are appended to `logs/system.log`.

## AI-Assisted Development

**Task given to the AI:** Transform the guessing-game starter into a reproducible RAG and agentic Streamlit system, while preserving clear setup, tests, architecture, and responsible-AI documentation.

**What it did:** Created local retrieval and summarization utilities, an agent controller and trace logger, a Streamlit interface, automated tests, Mermaid architecture source, and a model card.

**What required human verification:** I reviewed the source retrieval behavior, ran pytest, checked for missing-input handling, and verified the live Streamlit interface before finalizing.
