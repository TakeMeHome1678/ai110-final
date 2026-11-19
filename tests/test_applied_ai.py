from agent_utils import calculate_confidence, classify_request, execute_agent, plan_task
from rag_utils import cosine_similarity, extract_summary, retrieve


DOCUMENTS = [
    {"id": "1", "title": "Python debugging", "text": "Reproduce the failing test and inspect the traceback before changing code."},
    {"id": "2", "title": "Streamlit state", "text": "Use session state to retain values across Streamlit reruns."},
]


def test_retrieval_finds_debug_source():
    results = retrieve("How should I debug a failing Python test?", DOCUMENTS)
    assert results
    assert results[0]["title"] == "Python debugging"


def test_retrieval_has_no_evidence_for_unrelated_query():
    results = retrieve("quantum orbitals", [{"title": "Cooking", "text": "Bake bread for forty minutes."}])
    assert results == []


def test_extract_summary_returns_source_text_for_short_input():
    text = "Retrieval is useful. It finds supporting evidence."
    assert extract_summary(text) == text


def test_cosine_similarity_is_higher_for_matching_text():
    matching = cosine_similarity("debug Python traceback", "debug a Python traceback")
    unrelated = cosine_similarity("debug Python traceback", "bake bread")
    assert matching > unrelated


def test_request_classification():
    assert classify_request("Why did this traceback fail?") == "debug"
    assert classify_request("Summarize this article") == "summarize"


def test_agentic_plan_has_checkable_steps():
    plan = plan_task("Plan a reliable testing workflow")
    assert len(plan) >= 3
    assert all(item["status"] == "planned" for item in plan)


def test_execute_agent_gracefully_handles_missing_evidence(tmp_path):
    trace = tmp_path / "trace.jsonl"
    result = execute_agent("Retrieve the price of a secret planet", "", DOCUMENTS, str(trace))
    assert "could not retrieve" in result["answer"].lower()
    assert result["confidence"] >= 0.0


def test_confidence_is_bounded():
    evidence = [{"score": 0.8}, {"score": 0.6}]
    assert 0.0 <= calculate_confidence(evidence, "answer") <= 1.0
