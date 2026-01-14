#! /usr/bin/env python3
"""
Application data
"""

"""
Shared test data for all test files.
"""

# Test data - Images for multiple domain versions
TEST_IMAGES = [
    # webapp domain images
    {"name": "frontend", "version": "2025-01-01-10-15-30", "domain": "webapp"},
    {"name": "frontend", "version": "2025-01-02-11-22-45", "domain": "webapp"},
    {"name": "frontend", "version": "2025-01-03-09-33-12", "domain": "webapp"},
    {"name": "backend", "version": "2025-01-01-12-45-18", "domain": "webapp"},
    {"name": "backend", "version": "2025-01-02-14-08-55", "domain": "webapp"},
    {"name": "backend", "version": "2025-01-03-16-52-27", "domain": "webapp"},
    # services domain images
    {"name": "api-service", "version": "2025-01-01-08-30-42", "domain": "services"},
    {"name": "api-service", "version": "2025-01-02-10-17-33", "domain": "services"},
    {"name": "api-service", "version": "2025-01-03-13-41-59", "domain": "services"},
    {"name": "worker", "version": "2025-01-01-15-25-06", "domain": "services"},
    {"name": "worker", "version": "2025-01-02-17-38-21", "domain": "services"},
]

# Each domain has multiple versions (version format: YYYY-MM-DD-hh-mm-ss)
TEST_DOMAINS = [
    {"name": "webapp", "version": "2025-01-01-18-30-00"},
    {"name": "webapp", "version": "2025-01-02-19-45-15"},
    {"name": "webapp", "version": "2025-01-03-20-12-33"},
    {"name": "services", "version": "2025-01-01-17-55-48"},
    {"name": "services", "version": "2025-01-02-21-03-27"},
]

# Images to set as tested before creating each domain version
# webapp domain images
WEBAPP_2025_01_01 = [
    ("frontend", "2025-01-01-10-15-30"),
    ("backend", "2025-01-01-12-45-18"),
]

WEBAPP_2025_01_02 = [
    ("frontend", "2025-01-02-11-22-45"),
    ("backend", "2025-01-02-14-08-55"),
]

WEBAPP_2025_01_03 = [
    ("frontend", "2025-01-03-09-33-12"),
    ("backend", "2025-01-03-16-52-27"),
]

# services domain images
SERVICES_2025_01_01 = [
    ("api-service", "2025-01-01-08-30-42"),
    ("worker", "2025-01-01-15-25-06"),
]

SERVICES_2025_01_02 = [
    ("api-service", "2025-01-02-10-17-33"),
    ("worker", "2025-01-02-17-38-21"),
]

# Domain versions to set as active (one per domain)
ACTIVE_VERSIONS = [
    {"name": "webapp", "version": "2025-01-02-19-45-15"},
    {"name": "services", "version": "2025-01-01-17-55-48"},
]


"""
Load test data to version-manager.qqq.pm

This script loads test data from version-manager/image/src/tests/test_data.py
to the version-manager API at version-manager.qqq.pm
"""

import sys
import os
import requests

# Base URL for the API
BASE_URL = "http://version-manager.qqq.pm/v1"


def health_check():
    """Check that API is healthy."""
    response = requests.get(f"{BASE_URL.replace('/v1', '')}/health")
    if response.status_code != 200:
        print(f"ERROR: API health check failed: {response.status_code}")
        return False
    print("✓ API health check passed")
    return True


def create_domains():
    """Create all test domain versions."""
    print("\nCreating domain versions...")
    for domain in TEST_DOMAINS:
        # Check if domain already exists
        response = requests.get(f"{BASE_URL}/domains/{domain['name']}")
        if response.status_code == 200:
            existing_domains = response.json()
            if any(d["version"] == domain["version"] and d.get("deployed") == "dev" for d in existing_domains):
                print(f"  ⏭️  Domain {domain['name']} version {domain['version']} already exists, skipping")
                continue
        
        response = requests.post(
            f"{BASE_URL}/domains/{domain['name']}/create",
            json={"version": domain["version"]},
        )
        # Retry once on 500 error
        if response.status_code == 500:
            response = requests.post(
                f"{BASE_URL}/domains/{domain['name']}/create",
                json={"version": domain["version"]},
            )
        
        if response.status_code == 201:
            print(f"  ✓ Created domain {domain['name']} version {domain['version']}")
        else:
            print(f"  ✗ Failed to create domain {domain['name']} version {domain['version']}: {response.status_code} - {response.text}")


def create_image_domains():
    """Create image-domain entries (ImageDomain table)."""
    print("\nCreating image-domain entries...")
    image_names = set(img["name"] for img in TEST_IMAGES)
    for name in image_names:
        # Get domain from first image with this name
        domain = next(img["domain"] for img in TEST_IMAGES if img["name"] == name)
        response = requests.post(
            f"{BASE_URL}/images/create",
            json={"name": name, "domain": domain},
        )
        if response.status_code == 201:
            print(f"  ✓ Created image-domain entry: {name} -> {domain}")
        else:
            print(f"  ✗ Failed to create image-domain entry {name}: {response.status_code} - {response.text}")


def create_image_versions():
    """Create all test image versions."""
    print("\nCreating image versions...")
    for image in TEST_IMAGES:
        response = requests.post(
            f"{BASE_URL}/images/{image['name']}/create",
            json={"version": image["version"]},
        )
        if response.status_code == 201:
            print(f"  ✓ Created image version {image['name']}:{image['version']}")
        else:
            print(f"  ✗ Failed to create image version {image['name']}:{image['version']}: {response.status_code} - {response.text}")


def set_images_tested():
    """Set images as tested according to test data."""
    print("\nSetting images as tested...")
    
    test_sets = [
        ("webapp 2025-01-01", WEBAPP_2025_01_01),
        ("webapp 2025-01-02", WEBAPP_2025_01_02),
        ("webapp 2025-01-03", WEBAPP_2025_01_03),
        ("services 2025-01-01", SERVICES_2025_01_01),
        ("services 2025-01-02", SERVICES_2025_01_02),
    ]
    
    for label, image_list in test_sets:
        for name, version in image_list:
            response = requests.put(
                f"{BASE_URL}/images/{name}/tested",
                json={"version": version, "tested": True},
            )
            if response.status_code == 200:
                print(f"  ✓ Set {name}:{version} as tested ({label})")
            else:
                print(f"  ✗ Failed to set {name}:{version} as tested: {response.status_code} - {response.text}")


def set_domains_tested():
    """Set all domain versions as tested."""
    print("\nSetting domains as tested...")
    for domain in TEST_DOMAINS:
        # Check if domain exists first
        response = requests.get(f"{BASE_URL}/domains/{domain['name']}")
        if response.status_code == 404:
            print(f"  ⏭️  Domain {domain['name']} doesn't exist, skipping")
            continue
        domains_list = response.json()
        if not any(d["version"] == domain["version"] for d in domains_list):
            print(f"  ⏭️  Domain {domain['name']} version {domain['version']} doesn't exist, skipping")
            continue
        
        response = requests.put(
            f"{BASE_URL}/domains/tested",
            json={"name": domain["name"], "version": domain["version"], "tested": True},
        )
        if response.status_code == 200:
            print(f"  ✓ Set domain {domain['name']} version {domain['version']} as tested")
        else:
            print(f"  ✗ Failed to set domain {domain['name']} version {domain['version']} as tested: {response.status_code} - {response.text}")


def set_domains_active():
    """Set one version of each domain as active."""
    print("\nSetting active domain versions...")
    for domain in ACTIVE_VERSIONS:
        # Check if domain exists first
        response = requests.get(f"{BASE_URL}/domains/{domain['name']}")
        if response.status_code == 404:
            print(f"  ⏭️  Domain {domain['name']} doesn't exist, skipping")
            continue
        domains_list = response.json()
        if not any(d["version"] == domain["version"] for d in domains_list):
            print(f"  ⏭️  Domain {domain['name']} version {domain['version']} doesn't exist, skipping")
            continue
        
        response = requests.put(
            f"{BASE_URL}/domains/active",
            json={"name": domain["name"], "version": domain["version"]},
        )
        if response.status_code == 200:
            print(f"  ✓ Set domain {domain['name']} version {domain['version']} as active")
        else:
            print(f"  ✗ Failed to set domain {domain['name']} version {domain['version']} as active: {response.status_code} - {response.text}")


def main():
    """Main function to load all test data."""
    print("=" * 60)
    print("Loading test data to version-manager.qqq.pm")
    print("=" * 60)
    
    if not health_check():
        print("\nERROR: API is not healthy. Exiting.")
        sys.exit(1)
    
    # Execute in order
    create_domains()
    create_image_domains()
    create_image_versions()
    set_images_tested()
    set_domains_tested()
    set_domains_active()
    
    print("\n" + "=" * 60)
    print("Data loading completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
