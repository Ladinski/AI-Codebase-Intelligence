from app.services.bm25_search import BM25SearchService


def test_tokenize_code_identifier():
    service = BM25SearchService()

    tokens = service._tokenize(
        "decode_access_token(user_id)"
    )

    assert "decode_access_token" in tokens
    assert "user_id" in tokens