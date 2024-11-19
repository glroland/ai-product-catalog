""" Unit Tests for app.py

Validate API results and conformance during happy path invocations.
"""
import logging
from fastapi.testclient import TestClient
from app import app
from api.default import DEFAULT_RESPONSE
from api.chat import UNRELATED_RESPONSE, IM_SPEECHLESS_RESPONSE
import messages as m

logger = logging.getLogger(__name__)

client = TestClient(app)


def test_read_default():
    response = client.get("/")
    assert response.status_code == 200

    assert response.json() == { "message": DEFAULT_RESPONSE }


def test_unrelated_to_retail():
    data = {
        "user_message": m.UNRELATED_TO_RETAIL,
        "client_id": "test_unrelated"
    }
    response = client.post(url="/chat", json=data)
    assert response.status_code == 200

    json = response.json()
    assert json["qualified_customer_flag"] is False
    assert json["ai_response"] is not None
    assert json["ai_response"] == UNRELATED_RESPONSE
    assert len(json["ai_response"]) > 0
    assert json["identified_attributes"] is not None
    assert len(json["identified_attributes"]) == 0


def test_basic_unresolved_question():
    data = {
        "user_message": m.QUALIFIED_SHOE_INTEREST,
        "client_id": "test_basic_unresolved_question"
    }
    response = client.post(url="/chat", json=data)
    assert response.status_code == 200

    json = response.json()
    assert json["qualified_customer_flag"] is True
    assert json["ai_response"] is not None
    assert json["ai_response"] != UNRELATED_RESPONSE
    assert json["ai_response"] != IM_SPEECHLESS_RESPONSE
    assert len(json["ai_response"]) > 0
    assert json["identified_attributes"] is not None


def test_fully_qualified_question():
    data = {
        "user_message": m.FULLY_QUALIFIED_SHOE_REQUEST,
        "client_id": "test_fully_qualified_question"
    }
    response = client.post(url="/chat", json=data)
    assert response.status_code == 200

    json = response.json()
    assert json["qualified_customer_flag"] is True
    assert json["ai_response"] is not None
    assert json["ai_response"] != UNRELATED_RESPONSE
    assert json["ai_response"] != IM_SPEECHLESS_RESPONSE
    assert len(json["ai_response"]) > 0
    assert json["identified_attributes"] is not None
    assert len(json["identified_attributes"]) > 0
    assert json["matching_products"] is not None
    assert len(json["matching_products"]) > 0
