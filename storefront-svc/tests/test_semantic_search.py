""" Unit Tests for semantic_search.py

Validate semantic search functions.
"""
import logging
import semantic_search as ss

logger = logging.getLogger(__name__)

def test_get_connection_string():
    cs = ss.get_connection_string()
    assert cs != None
    assert isinstance(cs, str)
    assert len(cs) > 10

def test_product_semantic_search_one_and_one():
    results = ss.product_semantic_search("air jordans", 1)
    assert results is not None
    assert len(results) == 1
    product = results[0]
    assert product is not None
    assert product["sku"] is not None
    assert isinstance(product["sku"], str)
    assert len(product["sku"]) > 5
    assert product["product_name"] is not None
    assert isinstance(product["product_name"], str)
    assert len(product["product_name"]) > 5
    assert product["msrp"] is not None
    assert isinstance(product["msrp"], float)
    assert product["msrp"] > 0.0
    assert product["cosign_similarity"] is not None
    assert isinstance(product["cosign_similarity"], float)
    assert product["cosign_similarity"] > 0
