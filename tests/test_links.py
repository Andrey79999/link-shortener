import pytest
from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str, password: str):
    response = client.post("/api/user/register", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()

def login_user(client: TestClient, email: str, password: str):
    response = client.post("/api/user/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

def telegram_login(client: TestClient, telegram_id: int, user_name: str):
    response = client.post("/api/user/telegram", json={"telegram_id": telegram_id, "user_name": user_name})
    assert response.status_code == 200, response.text
    return response.json()

def create_link(client: TestClient, token: str, original_url: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/links/", json={"original_url": original_url}, headers=headers)
    return response

def create_custom_link(client: TestClient, token: str, original_url: str, short_code: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/links/create-custom-link",
                           json={"original_url": original_url,
                                 "custom_code": short_code},
                           headers=headers)
    return response

@pytest.fixture
def user_credentials():
    return {"email": "test@example.com", "password": "secret"}

@pytest.fixture
def auth_token(client: TestClient, user_credentials):
    token = login_user(client, user_credentials["email"], user_credentials["password"])
    return token

def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to URL Shortener Service"

def test_register_user(client: TestClient, user_credentials):
    user = register_user(client, user_credentials["email"], user_credentials["password"])
    assert "id" in user
    assert user["user_name"] == user_credentials["email"]

def test_register_existing_user(client: TestClient, user_credentials):
    register_user(client, user_credentials["email"], user_credentials["password"])
    register_user(client, user_credentials["email"], user_credentials["password"])
    response = client.post("/api/user/register", json=user_credentials)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "A user with this email already exists"

def test_login_user(client: TestClient, user_credentials):
    token = login_user(client, user_credentials["email"], user_credentials["password"])
    assert isinstance(token, str)

def test_login_invalid_user(client: TestClient, user_credentials):
    response = client.post("/api/user/login", data={"username": user_credentials["email"], "password": "wrong"})
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect credentials"

# def test_telegram_login(client: TestClient):
#     telegram_id = 123456
#     user_name = "telegramUser"
#     user1 = telegram_login(client, telegram_id, user_name)
#     user2 = telegram_login(client, telegram_id, user_name)
#     assert user1["id"] == user2["id"]
#     assert user1["user_name"] == user_name

def test_create_link(auth_token: str, client: TestClient):
    original_url = "http://example.com/"
    response = create_link(client, auth_token, original_url)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["original_url"] == original_url
    assert "short_code" in data
    assert data["clicks"] == 0
    
def test_create_custom_link(auth_token: str, client: TestClient):
    original_url = "http://example.com/"
    custom_code = "custom_code"
    response = create_custom_link(client, auth_token, original_url, custom_code)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["original_url"] == original_url
    assert "short_code" in data
    assert data["clicks"] == 0

def test_create_exist_custom_link(auth_token: str, client: TestClient):
    original_url = "http://example.com/"
    custom_code = "custom_code"
    create_custom_link(client, auth_token, original_url, custom_code)
    create_custom_link(client, auth_token, original_url, custom_code)
    response = create_custom_link(client, auth_token, original_url, custom_code)
    print(response.status_code)
    assert response.status_code == 400, response.text
    
def test_create_link_invalid_url(auth_token: str, client: TestClient):
    original_url = "not-a-valid-url"
    response = create_link(client, auth_token, original_url)
    assert response.status_code == 422

def test_redirect_link(auth_token: str, client: TestClient):
    original_url = "http://example.com/"
    response = create_link(client, auth_token, original_url)
    data = response.json()
    short_code = data["short_code"]
    
    
    response = client.get(f"/api/links/{short_code}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["original_url"] == original_url
    
    assert data["clicks"] >= 1

def test_redirect_non_existing_link(client: TestClient):
    response = client.get("/api/links/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Link not found"

def test_get_user_links(auth_token: str, client: TestClient):
    original_url = "http://example.com/"
    create_resp = create_link(client, auth_token, original_url)
    assert create_resp.status_code == 200, create_resp.text
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/api/links/my-links", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(link["original_url"] == original_url for link in data)


def test_delete_multiple_links(auth_token: str, client: TestClient):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response1 = create_link(client, auth_token, "http://example1.com/")
    response2 = create_link(client, auth_token, "http://example2.com/")
    link1 = response1.json()  
    link2 = response2.json()
    
    payload = [
        {"id": link1["id"]},
        {"id": link2["id"]}
    ]
    print(payload)
    response = client.post("/api/links/delete-links", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json() is True

    response = client.get(f"/api/links/{link1['id']}", headers=headers)
    assert response.status_code == 404
    response = client.get(f"/api/links/{link2['id']}", headers=headers)
    assert response.status_code == 404

