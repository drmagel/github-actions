"""
Pytest configuration and fixtures for Version Manager API tests.
Assumes docker container is already running (use `make run-sqlite` first).
"""

import pytest

# Configuration
BASE_URL = "http://localhost:8080"
API_URL = f"{BASE_URL}/v1"


@pytest.fixture(scope="session")
def api_url():
    """Return the API URL."""
    return API_URL
