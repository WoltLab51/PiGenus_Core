def test_submit_job(client, admin_user):
    response = client.post(
        "/api/v1/jobs",
        json={"title": "My Job", "job_type": "shell_command"},
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Job"
    assert data["status"] == "pending"


def test_lease_job(client, admin_user, test_job, test_worker):
    worker_token = test_worker["worker_token"]
    response = client.post(
        "/api/v1/jobs/lease",
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("job") is not None
    assert data["job"]["status"] == "leased"


def test_lease_job_no_jobs_returns_204(client, admin_user, test_worker):
    """When no pending jobs exist the lease endpoint returns 204 No Content."""
    worker_token = test_worker["worker_token"]
    response = client.post(
        "/api/v1/jobs/lease",
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response.status_code == 204


def test_ack_complete_job(client, admin_user, test_job, test_worker):
    worker_token = test_worker["worker_token"]
    lease_resp = client.post(
        "/api/v1/jobs/lease",
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    job_id = lease_resp.json()["job"]["id"]

    ack_resp = client.post(
        f"/api/v1/jobs/{job_id}/ack",
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "running"

    complete_resp = client.post(
        f"/api/v1/jobs/{job_id}/complete",
        json={"result": {"output": "done"}},
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"


def test_fail_job(client, admin_user, test_worker):
    client.post(
        "/api/v1/jobs",
        json={"title": "Fail Job", "job_type": "shell_command"},
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    worker_token = test_worker["worker_token"]
    lease = client.post(
        "/api/v1/jobs/lease",
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    job_id = lease.json()["job"]["id"]
    fail = client.post(
        f"/api/v1/jobs/{job_id}/fail",
        json={"error": "Something went wrong"},
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert fail.status_code == 200
    assert fail.json()["status"] == "failed"


def test_requeue_stuck_jobs(client, admin_user):
    response = client.post(
        "/api/v1/admin/jobs/requeue-stuck",
        headers={"x-admin-token": "test-admin-token"},
    )
    assert response.status_code == 200
    assert "requeued" in response.json()
