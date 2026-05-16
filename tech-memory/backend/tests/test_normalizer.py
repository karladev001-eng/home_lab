"""Normalizer / deduplicator tests."""

import pytest
from logic.normalizer.deduplicator import normalize_name


def test_normalize_lowercase():
    """Name is lowercased."""
    assert normalize_name("Behavior Tree") == "behaviortree"


def test_normalize_removes_symbols():
    """Symbols are removed from name."""
    assert normalize_name("A* Search") == "search"


def test_normalize_japanese():
    """Japanese characters are preserved."""
    result = normalize_name("強化学習")
    assert "強化学習" in result


def test_normalize_already_clean():
    """Already normalized name is unchanged."""
    assert normalize_name("rag") == "rag"


def test_normalize_strip_whitespace():
    """Leading/trailing whitespace is stripped."""
    result = normalize_name("  RAG  ")
    assert result == "rag"
