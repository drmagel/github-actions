"""
Test 02: Images API tests.

Expected state from test_01_setup.py:
- 11 total images: frontend(3), backend(3), api-service(3), worker(2)
- All images start as not tested
"""

import pytest
import requests
from test_data import (
    WEBAPP_2025_01_01,
    WEBAPP_2025_01_02,
    WEBAPP_2025_01_03,
    SERVICES_2025_01_01,
    SERVICES_2025_01_02,
)


class TestImagesSetTested:
    """Test setting images as tested."""

    def test_set_webapp_images_tested_2025_01_01(self, api_url):
        """PUT /images/{name}/tested - Set webapp images as tested for 2025-01-01."""
        for name, version in WEBAPP_2025_01_01:
            response = requests.put(
                f"{api_url}/images/{name}/tested",
                json={"version": version, "tested": True},
            )
            assert response.status_code == 200, f"Failed to set tested: {name}:{version}"
            assert response.json()["tested"] is True

    def test_set_services_images_tested_2025_01_01(self, api_url):
        """PUT /images/{name}/tested - Set services images as tested for 2025-01-01."""
        for name, version in SERVICES_2025_01_01:
            response = requests.put(
                f"{api_url}/images/{name}/tested",
                json={"version": version, "tested": True},
            )
            assert response.status_code == 200, f"Failed to set tested: {name}:{version}"
            assert response.json()["tested"] is True

    def test_set_webapp_images_tested_2025_01_02(self, api_url):
        """PUT /images/{name}/tested - Set webapp images as tested for 2025-01-02."""
        for name, version in WEBAPP_2025_01_02:
            response = requests.put(
                f"{api_url}/images/{name}/tested",
                json={"version": version, "tested": True},
            )
            assert response.status_code == 200, f"Failed to set tested: {name}:{version}"
            assert response.json()["tested"] is True

    def test_set_services_images_tested_2025_01_02(self, api_url):
        """PUT /images/{name}/tested - Set services images as tested for 2025-01-02."""
        for name, version in SERVICES_2025_01_02:
            response = requests.put(
                f"{api_url}/images/{name}/tested",
                json={"version": version, "tested": True},
            )
            assert response.status_code == 200, f"Failed to set tested: {name}:{version}"
            assert response.json()["tested"] is True

    def test_set_webapp_images_tested_2025_01_03(self, api_url):
        """PUT /images/{name}/tested - Set webapp images as tested for 2025-01-03."""
        for name, version in WEBAPP_2025_01_03:
            response = requests.put(
                f"{api_url}/images/{name}/tested",
                json={"version": version, "tested": True},
            )
            assert response.status_code == 200, f"Failed to set tested: {name}:{version}"
            assert response.json()["tested"] is True


class TestImagesListAPI:
    """Test Images list endpoints."""

    def test_list_all_images(self, api_url):
        """GET /images/list - list all images."""
        response = requests.get(f"{api_url}/images/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 11 images: frontend + backend + api-service + worker
        assert len(data) == 4

    def test_list_all_images_versions(self, api_url):
        """GET /images/list - list all images versions."""
        response = requests.get(f"{api_url}/images/list/versions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 11 images: frontend(3) + backend(3) + api-service(3) + worker(2)
        assert len(data) == 11

    def test_list_tested_images(self, api_url):
        """GET /images/list/tested - list tested images."""
        response = requests.get(f"{api_url}/images/list/tested")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # After setting images as tested, we should have tested images
        # frontend(3) + backend(3) + api-service(2) + worker(2) = 10
        assert len(data) >= 10

    def test_list_untested_images(self, api_url):
        """GET /images/list/tested - list tested images."""
        response = requests.get(f"{api_url}/images/list/tested?tested=false")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # After setting images as tested, we should have untested images (1)
        # worker(2) = 2
        assert len(data) == 1 

    def test_get_image_versions_frontend(self, api_url):
        """GET /images/{image_name}/list - get all versions of frontend."""
        response = requests.get(f"{api_url}/images/frontend/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # frontend has 3 versions
        assert all(img["name"] == "frontend" for img in data)

    def test_get_image_versions_worker(self, api_url):
        """GET /images/{image_name}/list - get all versions of worker."""
        response = requests.get(f"{api_url}/images/worker/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # worker has 2 versions
        assert all(img["name"] == "worker" for img in data)

    def test_get_image_versions_not_found(self, api_url):
        """GET /images/{image_name}/list - image not found."""
        response = requests.get(f"{api_url}/images/nonexistent/list")
        assert response.status_code == 404

    def test_get_tested_image_versions(self, api_url):
        """GET /images/{image_name}/tested - get tested versions of frontend."""
        response = requests.get(f"{api_url}/images/frontend/tested")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # All 3 frontend versions are tested
        assert all(img["tested"] is True for img in data)

    def test_get_tested_api_service_versions(self, api_url):
        """GET /images/{image_name}/tested - get tested versions of api-service."""
        response = requests.get(f"{api_url}/images/api-service/tested")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Only 2 api-service versions are tested (v1 and v2, not v3)
        assert len(data) == 2
        assert all(img["tested"] is True for img in data)

class TestImagesUpdateAPI:
    """Test Images update endpoints."""

    def test_update_image_domain(self, api_url):
        """PUT /images/{image_name}/domain - update domain."""
        response = requests.put(
            f"{api_url}/images/api-service/domain",
            json={"domain": "new-services"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(img["domain"] == "new-services" for img in data)

        # Revert back
        response = requests.put(
            f"{api_url}/images/api-service/domain",
            json={"domain": "services"},
        )
        assert response.status_code == 200

    def test_rename_image(self, api_url):
        """PUT /images/{image_name}/rename - rename image."""
        # Create a temporary image to rename
        response = requests.post(
            f"{api_url}/images/create",
            json={"name": "temp-image", "domain": "temp"},
        )
        assert response.status_code == 201
        # Create a version
        response = requests.post(
            f"{api_url}/images/temp-image/create",
            json={"version": "2025-01-01-09-33-12"},
        )
        assert response.status_code == 201

        # Rename it
        response = requests.put(
            f"{api_url}/images/temp-image/rename",
            json={"name": "renamed-image"},
        )
        assert response.status_code == 200
        data = response.json()
        assert all(img["name"] == "renamed-image" for img in data)

        # Delete the renamed image
        response = requests.delete(f"{api_url}/images/renamed-image")
        assert response.status_code == 200

