"""Schema validation tests."""

import pytest
from pydantic import ValidationError

from api.schemas import IngestUrlRequest, SearchTechnologiesRequest


def test_ingest_url_valid():
    """Valid IngestUrlRequest passes validation."""
    req = IngestUrlRequest(url="https://example.com", collection_mode="standard", tags=["AI"])
    assert req.url == "https://example.com"
    assert req.collection_mode == "standard"
    assert req.tags == ["AI"]


def test_ingest_url_invalid_url():
    """Non-http URL raises ValidationError."""
    with pytest.raises(ValidationError):
        IngestUrlRequest(url="ftp://example.com")


def test_ingest_url_invalid_mode():
    """Invalid collection_mode raises ValidationError."""
    with pytest.raises(ValidationError):
        IngestUrlRequest(url="https://example.com", collection_mode="ultra")


def test_ingest_url_too_many_tags():
    """More than 20 tags raises ValidationError."""
    with pytest.raises(ValidationError):
        IngestUrlRequest(
            url="https://example.com",
            tags=[f"tag{i}" for i in range(21)],
        )


def test_ingest_url_tag_too_long():
    """Tag longer than 50 chars raises ValidationError."""
    with pytest.raises(ValidationError):
        IngestUrlRequest(
            url="https://example.com",
            tags=["a" * 51],
        )


def test_search_valid():
    """Valid SearchTechnologiesRequest passes."""
    req = SearchTechnologiesRequest(query="behavior tree", mode="keyword", limit=5)
    assert req.query == "behavior tree"
    assert req.mode == "keyword"


def test_search_invalid_mode():
    """Invalid search mode raises ValidationError."""
    with pytest.raises(ValidationError):
        SearchTechnologiesRequest(query="test", mode="invalid_mode")
