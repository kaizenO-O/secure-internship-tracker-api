
import os

# Set this before importing the application.
os.environ["APP_ENV"] = "test"

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models


# In-memory SQLite database for testing.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture
def client():
    # Create fresh tables for each test.
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# Helper functions
def register_user(
    client,
    email="test@example.com",
    password="StrongPass123!",
):
    return client.post(
        "/register",
        json={"email": email, "password": password},
    )


def login_user(
    client,
    email="test@example.com",
    password="StrongPass123!",
):
    return client.post(
        "/login",
        json={"email": email, "password": password},
    )


def auth_headers(
    client,
    email="test@example.com",
    password="StrongPass123!",
):
    response = login_user(client, email, password)
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# 1. Registration
def test_register_user(client):
    response = register_user(client)

    assert response.status_code == 201
    assert response.json()["user"]["email"] == "test@example.com"
    assert "hashed_password" not in response.json()["user"]


# 2. Duplicate registration
def test_duplicate_registration(client):
    register_user(client)

    response = register_user(client)

    assert response.status_code == 409


# 3. Successful login
def test_login_returns_access_token(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


# 4. Reject incorrect password
def test_login_rejects_wrong_password(client):
    register_user(client)

    response = login_user(
        client,
        password="WrongPassword123!",
    )

    assert response.status_code == 401


# 5. Require authentication for /me
def test_me_requires_authentication(client):
    response = client.get("/me")

    assert response.status_code in (401, 403)


# 6. Return the authenticated user
def test_me_returns_current_user(client):
    register_user(client)
    headers = auth_headers(client)

    response = client.get("/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


# 7. Create and list internships
def test_create_and_list_internships(client):
    register_user(client)
    headers = auth_headers(client)

    payload = {
        "company": "Example Tech",
        "role": "Backend Intern",
        "status": "Applied",
        "application_date": date.today().isoformat(),
    }

    created = client.post(
        "/internships",
        json=payload,
        headers=headers,
    )

    assert created.status_code == 201
    assert created.json()["company"] == "Example Tech"

    listed = client.get(
        "/internships",
        headers=headers,
    )

    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["role"] == "Backend Intern"


# 8. Prevent access to another user's internship
def test_users_cannot_access_each_others_internships(client):
    register_user(client, "user1@example.com")
    headers1 = auth_headers(client, "user1@example.com")

    created = client.post(
        "/internships",
        json={
            "company": "Private Company",
            "role": "Python Intern",
            "status": "Applied",
            "application_date": date.today().isoformat(),
        },
        headers=headers1,
    )

    assert created.status_code == 201
    internship_id = created.json()["id"]

    register_user(client, "user2@example.com")
    headers2 = auth_headers(client, "user2@example.com")

    other_user_list = client.get(
        "/internships",
        headers=headers2,
    )

    other_user_detail = client.get(
        f"/internships/{internship_id}",
        headers=headers2,
    )

    assert other_user_list.status_code == 200
    assert other_user_list.json() == []
    assert other_user_detail.status_code == 404


# 9. Update an internship
def test_update_internship(client):
    register_user(client)
    headers = auth_headers(client)

    payload = {
        "company": "Example Tech",
        "role": "Backend Intern",
        "status": "Applied",
        "application_date": date.today().isoformat(),
    }

    created = client.post(
        "/internships",
        json=payload,
        headers=headers,
    )

    assert created.status_code == 201
    internship_id = created.json()["id"]

    updated_payload = {
        "company": "Updated Tech",
        "role": "Python Backend Intern",
        "status": "Interview",
        "application_date": date.today().isoformat(),
    }

    response = client.put(
        f"/internships/{internship_id}",
        json=updated_payload,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["company"] == "Updated Tech"
    assert response.json()["status"] == "Interview"


# 10. Delete an internship
def test_delete_internship(client):
    register_user(client)
    headers = auth_headers(client)

    payload = {
        "company": "Example Tech",
        "role": "Backend Intern",
        "status": "Applied",
        "application_date": date.today().isoformat(),
    }

    created = client.post(
        "/internships",
        json=payload,
        headers=headers,
    )

    assert created.status_code == 201
    internship_id = created.json()["id"]

    response = client.delete(
        f"/internships/{internship_id}",
        headers=headers,
    )

    assert response.status_code == 200

    detail = client.get(
        f"/internships/{internship_id}",
        headers=headers,
    )

    assert detail.status_code == 404


# 11. Reject an invalid JWT
def test_invalid_token_is_rejected(client):
    headers = {
        "Authorization": "Bearer invalid.token.value"
    }

    response = client.get("/me", headers=headers)

    assert response.status_code == 401


# 12. Prevent updating another user's internship
def test_users_cannot_update_each_others_internships(client):
    register_user(client, "user1@example.com")
    headers1 = auth_headers(client, "user1@example.com")

    created = client.post(
        "/internships",
        json={
            "company": "Private Company",
            "role": "Python Intern",
            "status": "Applied",
            "application_date": date.today().isoformat(),
        },
        headers=headers1,
    )

    assert created.status_code == 201
    internship_id = created.json()["id"]

    register_user(client, "user2@example.com")
    headers2 = auth_headers(client, "user2@example.com")

    response = client.put(
        f"/internships/{internship_id}",
        json={
            "company": "Hacked Company",
            "role": "Senior Intern",
            "status": "Offer",
            "application_date": date.today().isoformat(),
        },
        headers=headers2,
    )

    assert response.status_code == 404

    # Verify the original owner's data was not modified.
    owner_response = client.get(
        f"/internships/{internship_id}",
        headers=headers1,
    )

    assert owner_response.status_code == 200
    assert owner_response.json()["company"] == "Private Company"


# 13. Prevent deleting another user's internship
def test_users_cannot_delete_each_others_internships(client):
    register_user(client, "user1@example.com")
    headers1 = auth_headers(client, "user1@example.com")

    created = client.post(
        "/internships",
        json={
            "company": "Private Company",
            "role": "Python Intern",
            "status": "Applied",
            "application_date": date.today().isoformat(),
        },
        headers=headers1,
    )

    assert created.status_code == 201
    internship_id = created.json()["id"]

    register_user(client, "user2@example.com")
    headers2 = auth_headers(client, "user2@example.com")

    response = client.delete(
        f"/internships/{internship_id}",
        headers=headers2,
    )

    assert response.status_code == 404

    # Verify the internship still exists for its owner.
    owner_check = client.get(
        f"/internships/{internship_id}",
        headers=headers1,
    )

    assert owner_check.status_code == 200
