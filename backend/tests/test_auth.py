"""Tests for authentication endpoints."""


def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "name": "Isaac",
        "email": "isaac@test.com",
        "password": "senha123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_name"] == "Isaac"


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "name": "Isaac",
        "email": "isaac@test.com",
        "password": "senha123",
    })
    response = client.post("/api/auth/register", json={
        "name": "Outro",
        "email": "isaac@test.com",
        "password": "outra123",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    client.post("/api/auth/register", json={
        "name": "Isaac",
        "email": "isaac@test.com",
        "password": "senha123",
    })
    response = client.post("/api/auth/login", data={
        "username": "isaac@test.com",
        "password": "senha123",
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "name": "Isaac",
        "email": "isaac@test.com",
        "password": "senha123",
    })
    response = client.post("/api/auth/login", data={
        "username": "isaac@test.com",
        "password": "errada",
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401


def test_login_nonexistent_email(client):
    response = client.post("/api/auth/login", data={
        "username": "naoexiste@test.com",
        "password": "qualquer",
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 401


def test_protected_route_with_token(client, auth_headers):
    response = client.get("/api/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
