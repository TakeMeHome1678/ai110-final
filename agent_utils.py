"""Agent planning, tool execution, logging, and guardrails."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from rag_utils import extract_summary, retrieve


LOGGER = logging.getLogger("applied_ai_system")


def configure_logging(log_path: str = "logs/system.log") -> None:
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.setLevel(logging.INFO)
    if not LOGGER.handlers:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        LOGGER.addHandler(handler)


def classify_request(task: str) -> str:
    text = task.lower()
    words = set(text.replace("?", " ").replace(".", " ").split())
    if any(word in text for word in ("debug", "error", "exception", "traceback", "fix")):
        return "debug"
    if any(word in words for word in ("summarize", "summary", "shorten", "tldr")):
        return "summarize"
    if words.intersection({"plan", "steps", "workflow"}) or "how do i" in text:
        return "plan"
    return "retrieve"


def plan_task(task: str) -> list[dict]:
    kind = classify_request(task)
    steps = {
        "summarize": ["Validate source text", "Score and select key sentences", "Check summary length"],
        "retrieve": ["Retrieve relevant source passages", "Check evidence confidence", "Form answer with citations"],
        "plan": ["Clarify the requested outcome", "Order concrete steps", "Include verification and rollback checks"],
        "debug": ["Identify error symptoms", "Map symptoms to likely causes", "Suggest a minimal reproduction and fix"],
    }
    return [{"step": index + 1, "action": action, "status": "planned"} for index, action in enumerate(steps[kind])]


def execute_agent(task: str, source_text: str, documents: list[dict], trace_path: str = "logs/trace.jsonl") -> dict:
    """Plan and execute one bounded workflow, then evaluate its confidence and output."""
    configure_logging()
    kind = classify_request(task)
    plan = plan_task(task)

    try:
        evidence = retrieve(task, documents, limit=3)
        if kind == "summarize":
            answer = extract_summary(source_text or "\n".join(d["text"] for d in documents), max_sentences=3)
        elif kind == "debug":
            answer = explain_debug_issue(task, evidence)
        elif kind == "plan":
            answer = create_plan(task)
        else:
            answer = answer_with_evidence(task, evidence)

        confidence = calculate_confidence(evidence, answer)
        if kind in ("retrieve", "debug") and not evidence:
            confidence = 0.25

        for item in plan:
            item["status"] = "completed"

        result = {
            "task": task,
            "kind": kind,
            "plan": plan,
            "answer": answer,
            "evidence": evidence,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        write_trace(trace_path, result)
        LOGGER.info("Completed %s task confidence=%.2f evidence_count=%d", kind, confidence, len(evidence))
        return result
    except Exception as exc:
        LOGGER.exception("Agent execution failed")
        return {
            "task": task,
            "kind": kind,
            "plan": plan,
            "answer": "The request could not be completed safely.",
            "evidence": [],
            "confidence": 0.0,
            "error": f"{type(exc).__name__}: {exc}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def answer_with_evidence(task: str, evidence: list[dict]) -> str:
    if not evidence:
        return "I could not retrieve supporting information. Please add a relevant source document."
    bullets = [f"- **{item['title']}**: {item['text'][:260]}" for item in evidence]
    return "Based on retrieved sources:\n" + "\n".join(bullets)


def explain_debug_issue(task: str, evidence: list[dict]) -> str:
    context = ""
    if evidence:
        context = "\nRelated project knowledge:\n" + "\n".join(
            f"- {item['title']}: {item['text'][:180]}" for item in evidence
        )
    return (
        "Debugging workflow: reproduce the issue with the smallest input; inspect the exact error; "
        "isolate the responsible function; apply one focused change; rerun the smallest test that exercises it."
        + context
    )


def create_plan(task: str) -> str:
    return (
        "1. State the goal and acceptance criteria.\n"
        "2. Gather the minimum source information.\n"
        "3. Apply one change at a time.\n"
        "4. Run a focused validation.\n"
        "5. Record the result and check for regressions."
    )


def calculate_confidence(evidence: list[dict], answer: str) -> float:
    if not answer:
        return 0.0
    if not evidence:
        return 0.35
    return min(0.95, 0.45 + sum(item["score"] for item in evidence) * 0.35)


def write_trace(path: str, result: dict) -> None:
    trace_file = Path(path)
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    with trace_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False) + "\n")
