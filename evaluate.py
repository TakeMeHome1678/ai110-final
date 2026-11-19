"""Small predefined evaluation harness for the Applied AI Workbench."""

from agent_utils import execute_agent


CASES = [
    ("Debug retrieval", "How should I debug a failing Python test?", "", "debug", True),
    ("Summarization", "Summarize the source", "RAG retrieves supporting evidence before answering. It should be concise.", "summarize", False),
    ("Missing evidence", "Retrieve the price of a secret planet", "", "retrieve", False),
]

DOCUMENTS = [
    {
        "id": "debug-1",
        "title": "Python debugging",
        "text": "Reproduce the failing test, inspect the traceback, isolate the function, and rerun a focused test.",
    },
    {
        "id": "rag-1",
        "title": "RAG design",
        "text": "Retrieval should rank relevant passages and avoid unsupported answers when evidence is missing.",
    },
]


def main() -> int:
    passed = 0

    for name, task, source_text, expected_kind, should_have_evidence in CASES:
        case_documents = [] if name == "Missing evidence" else DOCUMENTS
        result = execute_agent(task, source_text, case_documents, "logs/evaluation-trace.jsonl")
        kind_ok = result["kind"] == expected_kind
        evidence_ok = bool(result["evidence"])
        if should_have_evidence:
            evidence_ok = evidence_ok
        else:
            evidence_ok = not evidence_ok
        confidence_ok = 0.0 <= result["confidence"] <= 1.0
        answer_ok = bool(result["answer"])
        case_passed = kind_ok and evidence_ok and confidence_ok and answer_ok
        passed += int(case_passed)

        status = "PASS" if case_passed else "FAIL"
        print(f"{status} | {name} | kind={result['kind']} | confidence={result['confidence']:.2f} | evidence={len(result['evidence'])}")

    total = len(CASES)
    print(f"SUMMARY: {passed}/{total} passed; {passed / total:.0%} pass rate")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
