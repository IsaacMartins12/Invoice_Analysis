"""Tests for categories endpoints."""


def test_list_default_categories(client, auth_headers):
    """Should return default categories."""
    response = client.get("/api/categories/", headers=auth_headers)
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 10  # At least the 10 defaults
    names = [c["name"] for c in categories]
    assert "Transporte" in names
    assert "Mercado" in names


def test_create_custom_category(client, auth_headers):
    """Should create a new custom category."""
    response = client.post("/api/categories/", json={
        "name": "Pets",
        "emoji": "🐶",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pets"
    assert data["emoji"] == "🐶"
    assert data["is_default"] is False


def test_create_duplicate_category(client, auth_headers):
    """Should reject duplicate category name."""
    client.post("/api/categories/", json={
        "name": "Pets",
        "emoji": "🐶",
    }, headers=auth_headers)
    response = client.post("/api/categories/", json={
        "name": "Pets",
        "emoji": "🐱",
    }, headers=auth_headers)
    assert response.status_code == 400


def test_update_custom_category(client, auth_headers):
    """Should update a custom category."""
    create_resp = client.post("/api/categories/", json={
        "name": "Pets",
        "emoji": "🐶",
    }, headers=auth_headers)
    cat_id = create_resp.json()["id"]

    response = client.put(f"/api/categories/{cat_id}", json={
        "name": "Animais",
        "emoji": "🐾",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Animais"


def test_delete_custom_category(client, auth_headers):
    """Should delete a custom category."""
    create_resp = client.post("/api/categories/", json={
        "name": "Temp",
        "emoji": "🗑️",
    }, headers=auth_headers)
    cat_id = create_resp.json()["id"]

    response = client.delete(f"/api/categories/{cat_id}", headers=auth_headers)
    assert response.status_code == 200


def test_rename_default_category(client, auth_headers):
    """Should allow renaming a default category."""
    response = client.post("/api/categories/rename-default", json={
        "original_name": "Transporte",
        "new_name": "Mobilidade",
        "emoji": "🚌",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Mobilidade"
