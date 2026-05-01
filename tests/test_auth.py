def test_register_first_user_is_admin(client):
    response = client.post("/api/v1/auth/register", json={
        "username": "firstuser",
        "email": "first@test.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "firstuser"
    assert data["is_admin"] is True


def test_register_second_user_is_not_admin(client):
    client.post("/api/v1/auth/register", json={
        "username": "user1", "email": "u1@test.com", "password": "pass123"
    })
    response = client.post("/api/v1/auth/register", json={
        "username": "user2", "email": "u2@test.com", "password": "pass123"
    })
    assert response.status_code == 201
    assert response.json()["is_admin"] is False


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "mypassword"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "loginuser", "password": "mypassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "username": "badpassuser", "email": "bad@test.com", "password": "correct"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "badpassuser", "password": "wrong"
    })
    assert response.status_code == 401


def test_get_me(admin_user, client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
