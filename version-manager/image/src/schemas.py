"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field

class ImageVersion(BaseModel):
    """Image reference within a domain."""

    name: str | None = None
    version: str = Field(..., description="Image version in YYYY-MM-DD-hh-mm-ss format")

class ImageTested(BaseModel):
    """Schema for setting image tested status."""

    name: str | None = None
    version: str = Field(..., description="Image version in YYYY-MM-DD-hh-mm-ss format")
    tested: bool = Field(..., description="Tested status")

class ImageCreate(BaseModel):
    """Schema for creating new image-domain entry."""

    name: str = Field(..., description="Image name")
    domain: str = Field(..., description="Domain name")

class ImageDomain(BaseModel):
    """Schema for updating image domain."""

    name: str | None = None
    domain: str = Field(..., description="Domain name")

class ImageDomainResponse(BaseModel):
    """Schema for image-domain entry response."""

    image: str = Field(..., description="Image name")
    domain: str = Field(..., description="Domain name")
    domains: list[str] = Field(..., description="List of domains")
    class Config:
        from_attributes = True

class ImageRename(BaseModel):
    """Schema for renaming image."""

    name: str = Field(..., description="New name for the image")

class ImageResponse(BaseModel):
    """Schema for image response."""

    name: str
    version: str
    domain: str
    tested: bool

    class Config:
        from_attributes = True

class ImagesListElement(BaseModel):
    """Schema for image list element."""

    name: str
    version: str
    tested: bool

    class Config:
        from_attributes = True

class DomainCreate(BaseModel):
    """Schema for creating a new domain version."""

    name: str | None = None
    version: str = Field(..., description="Domain version in YYYY-MM-DD-hh-mm-ss format")


class DomainResponse(BaseModel):
    """Schema for domain response."""

    name: str
    version: str
    deployed: str = Field(..., description="Deployment environment: dev, staging, prod")
    tested: bool
    active: bool
    images: list[ImagesListElement] = []

    class Config:
        from_attributes = True


class DomainUpdate(BaseModel):
    """Schema for updating domain images."""

    name: str = Field(..., description="Domain name")
    version: str = Field(..., description="Domain version in YYYY-MM-DD-hh-mm-ss format")
    images: list[ImageVersion] = Field(..., description="List of images with versions")


class DomainTested(BaseModel):
    """Schema for setting domain as tested."""

    name: str = Field(..., description="Domain name")
    version: str = Field(..., description="Domain version in YYYY-MM-DD-hh-mm-ss format")
    tested: bool = Field(..., description="Tested status")


class DomainActive(BaseModel):
    """Schema for setting domain as active."""

    name: str = Field(..., description="Domain name")
    version: str = Field(..., description="Domain version in YYYY-MM-DD-hh-mm-ss format")


class DomainPromote(BaseModel):
    """Schema for promoting domain to an environment."""

    name: str = Field(..., description="Domain name")
    version: str = Field(..., description="Domain version in YYYY-MM-DD-hh-mm-ss format")

class DomainRename(BaseModel):
    """Schema for renaming domain."""

    name: str = Field(..., description="New name for the domain")
