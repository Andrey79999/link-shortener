import pytest
from fastapi.testclient import TestClient
from app.services.link_service import generate_short_code


def test_generate_short_code():
    """
    Test the generate_short_code function.

    This test checks that the generate_short_code function returns a string of length 6.
    """
    url = "http://example.com"
    short_code = generate_short_code(url)
    assert isinstance(short_code, str)
    assert len(short_code) == 6


def test_create_link(client: TestClient):
    """
    Test the create_link function.

    This test checks that the create_link function returns a response with status code 200,
    and that the response data contains the expected fields and values.
    """
    payload = {"original_url": f"http://example.com/",
               "user_id": 1}
    response = client.post("/api/links/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == payload["user_id"]
    assert "id" in data
    assert data["original_url"] == payload["original_url"]
    assert "short_code" in data
    assert data["clicks"] == 0


def test_create_link_invalid_url(client: TestClient):
    """
    Test the create_link function with an invalid URL.

    This test checks that the create_link function returns a response with status code 422
    when an invalid URL is provided.
    """
    payload = {"original_url": "not-a-valid-url"}
    response = client.post("/api/links/", json=payload)
    assert response.status_code == 422


def test_redirect_link(client: TestClient):
    """
    Test the redirect_link function.

    This test checks that the redirect_link function returns a response with status code 200,
    and that the response data contains the expected fields and values.
    """
    payload = {"original_url": "http://example.com/"}
    response = client.post("/api/links/", json=payload)
    assert response.status_code == 200
    data = response.json()
    short_code = data["short_code"]

    response = client.get(f"/api/links/{short_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == payload["original_url"]


def test_redirect_non_existing_link(client: TestClient):
    """
    Test the redirect_link function with a non-existing short code.

    This test checks that the redirect_link function returns a response with status code 404
    when a non-existing short code is provided.
    """
    response = client.get("/api/links/nonexistent")
    assert response.status_code == 404
    