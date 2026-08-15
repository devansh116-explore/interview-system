from app.services.rag.retriever import build_query


def test_build_query_filters_previous_topics_and_deduplicates_skills():
    query = build_query(
        "backend_engineer",
        ["Python", "python", "FastAPI", "FastAPI", "SQL"],
        ["python"],
        "I have built Python APIs with FastAPI and SQL in production systems",
    )

    lowered = query.lower()
    assert lowered.count("python") == 1
    assert lowered.count("fastapi") == 1
    assert "sql" in lowered
    assert "backend engineer" in lowered
