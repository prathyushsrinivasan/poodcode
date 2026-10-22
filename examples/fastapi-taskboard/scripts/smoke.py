"""Exercise the configured database after migrations, without overriding get_db."""
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def smoke(client):
    headers = []
    for prefix in ["alice", "bob"]:
        name = prefix + "_" + uuid4().hex[:12]
        password = uuid4().hex
        result = client.post("/auth/register", json={"username": name, "password": password})
        assert result.status_code == 201, result.text
        result = client.post("/auth/token", data={"username": name, "password": password})
        assert result.status_code == 200, result.text
        headers.append({"Authorization": "Bearer " + result.json()["access_token"]})
    alice, bob = headers
    assert client.get("/health/ready").status_code == 200
    created = client.post("/tasks", headers=alice, json={"title": "Database smoke task"})
    assert created.status_code == 201, created.text
    path = f'/tasks/{created.json()["id"]}'
    assert client.get(path, headers=alice).json()["title"] == "Database smoke task"
    assert client.get("/tasks", headers=bob).json() == []
    assert client.get(path, headers=bob).status_code == 404
    assert client.patch(path, headers=bob, json={"done": True}).status_code == 404
    assert client.delete(path, headers=bob).status_code == 404
    assert client.patch(path, headers=alice, json={"done": True}).json()["done"] is True
    assert client.patch(path, headers=alice, json={"done": False}).json()["done"] is False
    deleted = client.delete(path, headers=alice)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(path, headers=alice).status_code == 404


if __name__ == "__main__":
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        smoke(client)
    print("Database-backed smoke passed (two throwaway accounts remain).")
