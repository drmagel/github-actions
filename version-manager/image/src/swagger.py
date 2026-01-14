"""
Swagger/OpenAPI configuration for Version Manager API.
Provides enhanced API documentation with metadata, tags, security schemes, and examples.
"""

from typing import Dict, Any


def get_swagger_config() -> Dict[str, Any]:
    """
    Returns FastAPI configuration dictionary with OpenAPI metadata.
    
    Returns:
        Dictionary of FastAPI initialization parameters for OpenAPI/Swagger docs.
    """
    return {
        "title": "Version Manager API",
        "description": """
API server for managing application versions in PostgreSQL or SQLite database.

## Features

- **Image Management**: Create, update, and manage container images and their versions
- **Domain Management**: Manage deployment domains and their configurations
- **Version Control**: Track image and domain versions across dev, staging, and prod environments
- **Testing Status**: Mark images and domains as tested
- **Promotion Workflow**: Promote versions through environments (dev → staging → prod)

## Database Support

- **PostgreSQL** (default): Production database
- **SQLite**: Set `USE_POSTGRESQL=false` for testing

## Authentication

Use `/auth/login` endpoint to authenticate. Default credentials:
- Username: Set via `ADMIN_USERNAME` environment variable (default: `admin`)
- Password: Set via `ADMIN_PASSWORD` environment variable (default: `12VersionManager-=`)

## API Version

All endpoints are prefixed with `/v1`
        """.strip(),
        "version": "1.0.0",
        "contact": {
            "name": "Version Manager Support",
        },
        "license_info": {
            "name": "Proprietary",
        },
        "tags_metadata": [
            {
                "name": "Images",
                "description": """
Endpoints for managing container images and their versions.

**Key Operations:**
- List all images and their versions
- Create new image entries
- Update image properties (domain, tested status)
- Delete images

**Version Format:** `YYYY-MM-DD-hh-mm-ss` (e.g., `2025-01-15-14-30-00`)
                """.strip(),
            },
            {
                "name": "Domains",
                "description": """
Endpoints for managing deployment domains and versions.

**Key Operations:**
- List all domains and their versions
- Create new domain versions
- Update domain configurations and image associations
- Set domain as active/tested
- Promote domains across environments (dev → staging → prod)
- Delete domains

**Environments:** `dev`, `staging`, `prod`

**Cascade Behavior:**
- Promoting a domain also promotes all associated images
- Setting a domain as tested also sets all associated images as tested
                """.strip(),
            },
            {
                "name": "Authentication",
                "description": """
Authentication endpoints for user login and session management.

**Login:** POST `/auth/login` with username and password
                """.strip(),
            },
        ],
        "openapi_tags": [
            {"name": "Images"},
            {"name": "Domains"},
            {"name": "Authentication"},
        ],
        "servers": [
            {
                "url": "http://localhost:8080",
                "description": "Local development server",
            },
            {
                "url": "https://version-manager.qqq.pm",
                "description": "Production server",
            },
        ],
    }


def get_openapi_schema_extra() -> Dict[str, Any]:
    """
    Returns additional OpenAPI schema configuration.
    Can be used to customize the OpenAPI schema further if needed.
    
    Returns:
        Dictionary with additional OpenAPI schema configuration.
    """
    return {
        "components": {
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "Basic authentication using username and password",
                },
            },
        },
        "security": [
            {
                "basicAuth": [],
            },
        ],
    }


# Example request/response data for documentation
API_EXAMPLES = {
    "ImageCreate": {
        "summary": "Create a new image",
        "value": {
            "name": "webapp",
            "version": "2025-01-15-14-30-00",
            "domain": "production",
        },
    },
    "ImageResponse": {
        "summary": "Image response example",
        "value": {
            "name": "webapp",
            "version": "2025-01-15-14-30-00",
            "domain": "production",
            "deployed": "dev",
            "tested": False,
        },
    },
    "DomainCreate": {
        "summary": "Create a new domain version",
        "value": {
            "name": "production",
            "version": "2025-01-15-14-30-00",
        },
    },
    "DomainResponse": {
        "summary": "Domain response example",
        "value": {
            "name": "production",
            "version": "2025-01-15-14-30-00",
            "deployed": "dev",
            "tested": False,
            "active": True,
            "images": [
                {
                    "name": "webapp",
                    "version": "2025-01-15-14-30-00",
                },
            ],
        },
    },
    "DomainUpdate": {
        "summary": "Update domain images",
        "value": {
            "name": "production",
            "version": "2025-01-15-14-30-00",
            "images": [
                {
                    "name": "webapp",
                    "version": "2025-01-15-14-30-00",
                },
                {
                    "name": "api",
                    "version": "2025-01-15-13-00-00",
                },
            ],
        },
    },
    "DomainTested": {
        "summary": "Mark domain as tested",
        "value": {
            "name": "production",
            "version": "2025-01-15-14-30-00",
        },
    },
    "DomainActive": {
        "summary": "Set domain as active",
        "value": {
            "name": "production",
            "version": "2025-01-15-14-30-00",
        },
    },
    "DomainPromote": {
        "summary": "Promote domain to environment",
        "value": {
            "name": "production",
            "version": "2025-01-15-14-30-00",
            "deployed": "staging",
        },
    },
}

