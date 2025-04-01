# tests/conftest.py
import pytest
import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module")
def headers():
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def token(headers):
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": user_id, "cargo": cargo},
        headers=headers,
    )
    return response.json()["token"]


@pytest.fixture(scope="module")
def refresh_token(headers):
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": user_id, "cargo": cargo},
        headers=headers,
    )
    return response.json()["refresh_token"]
