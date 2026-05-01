def test_register_worker(client, admin_user):
    response = client.post(
        "/api/v1/workers/register",
        json={
            "name": "worker1",
            "hostname": "host1",
            "capabilities": ["cpu"],
            "secret": "secret123",
        },
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "worker1"
    assert data["capabilities"] == ["cpu"]
    assert "worker_token" in data
    assert data["worker_token"] is not None


def test_worker_heartbeat(client, test_worker):
    worker_id = test_worker["id"]
    worker_token = test_worker["worker_token"]
    response = client.post(
        f"/api/v1/workers/{worker_id}/heartbeat",
        json={"status": "busy"},
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "busy"


def test_list_workers_admin_only(client, admin_user, test_worker):
    response = client.get(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_workers_no_auth(client):
    response = client.get("/api/v1/workers")
    assert response.status_code == 401
