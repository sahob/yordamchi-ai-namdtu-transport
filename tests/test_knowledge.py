from backend.knowledge import KnowledgeBase


def test_knowledge_base_loads_chunks():
    kb = KnowledgeBase()
    assert len(kb.chunks) > 0


def test_search_academic_leave():
    kb = KnowledgeBase()
    results = kb.search("Akademik ta'til olish tartibi")
    assert results
    assert any("Akademik" in r.chunk.meta.title or "ta’til" in r.chunk.text for r in results)
