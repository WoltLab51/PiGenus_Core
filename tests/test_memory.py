def test_store_memory(client, admin_user):
    response = client.post(
        "/api/v1/memory",
        json={"key": "test-key", "content": "Hello world", "content_type": "text"},
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["key"] == "test-key"
    assert data["content"] == "Hello world"


def test_get_memory(client, admin_user):
    client.post(
        "/api/v1/memory",
        json={"key": "get-key", "content": "get content"},
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    response = client.get(
        "/api/v1/memory/get-key",
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "get content"


def test_list_memory(client, admin_user):
    client.post("/api/v1/memory", json={"key": "list-key-1", "content": "item 1"},
                headers={"Authorization": f"Bearer {admin_user['token']}"})
    client.post("/api/v1/memory", json={"key": "list-key-2", "content": "item 2"},
                headers={"Authorization": f"Bearer {admin_user['token']}"})
    response = client.get("/api/v1/memory", headers={"Authorization": f"Bearer {admin_user['token']}"})
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_delete_memory(client, admin_user):
    client.post("/api/v1/memory", json={"key": "del-key", "content": "delete me"},
                headers={"Authorization": f"Bearer {admin_user['token']}"})
    del_resp = client.delete("/api/v1/memory/del-key",
                              headers={"Authorization": f"Bearer {admin_user['token']}"})
    assert del_resp.status_code == 204
    get_resp = client.get("/api/v1/memory/del-key",
                          headers={"Authorization": f"Bearer {admin_user['token']}"})
    assert get_resp.status_code == 404


def test_get_memory_not_found(client, admin_user):
    response = client.get("/api/v1/memory/nonexistent",
                          headers={"Authorization": f"Bearer {admin_user['token']}"})
    assert response.status_code == 404
