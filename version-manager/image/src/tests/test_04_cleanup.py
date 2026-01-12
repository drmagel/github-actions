"""
Test 04: Cleanup - Delete all test data using APIs.
These tests run last to clean up the database.
"""

import pytest
import requests
import time


class TestCleanup:
    """Cleanup tests - delete all test data."""

    def test_remove_all_test_images(self, api_url):
        """Remove all test images (ImageDomain entries)."""
        # After deleting image versions, the images should be removed from ImageDomain table
        # But let's verify and clean up any remaining entries
        # Get all images again to check if any remain
        response = requests.get(f"{api_url}/images/list")
        if response.status_code == 200:
            images = response.json()
            if images:
                # Delete any remaining images
                image_names = set(img["image"] for img in images)
                for name in image_names:
                    requests.delete(f"{api_url}/images/{name}")
        
        # Wait for deletions to complete
        time.sleep(0.5)
        
        # Verify all images are removed
        response = requests.get(f"{api_url}/images/list")
        assert response.status_code == 200
        remaining_images = response.json()
        assert len(remaining_images) == 0, \
            f"Expected 0 images but found {len(remaining_images)}: {[img['name'] for img in remaining_images]}"

    def test_remove_all_test_domains(self, api_url):
        """Remove all test domains."""
        # Get all domains
        response = requests.get(f"{api_url}/domains/list")
        if response.status_code == 200:
            domains = response.json()
            if domains:
                # Get unique domain names (each domain name may have multiple versions)
                domain_names = set(d["name"] for d in domains)
                
                # Delete all versions of each domain
                for domain_name in domain_names:
                    delete_response = requests.delete(f"{api_url}/domains/{domain_name}")
        # Wait for domain deletions to complete
        time.sleep(0.5)
        
        # Verify all domains are removed
        response = requests.get(f"{api_url}/domains/list")
        assert response.status_code == 200
        remaining_domains = response.json()
        assert len(remaining_domains) == 0, \
            f"Expected 0 domains but found {len(remaining_domains)}: {[d['name'] for d in remaining_domains]}"
