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
