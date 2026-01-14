"""
API Routes for Version Manager Application.
Defines all endpoints for managing images and domains.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from database import db
import schemas as S

router = APIRouter()


# =============================================================================
# Images Endpoints
# =============================================================================


@router.get("/images/list", response_model=list[S.ImageDomainResponse], tags=["Images"])
async def list_all_images():
    """List all the image names with all versions and their status."""
    try:
        return await db.get_all_images()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all images: {str(e)}")

@router.get("/images/list/versions", response_model=list[S.ImageResponse], tags=["Images"])
async def list_all_images_versions():
    """List all the image names with their versions and tested status."""
    try:
        return await db.get_all_images_versions()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all images versions: {str(e)}")

@router.get("/images/list/tested", response_model=list[S.ImageResponse], tags=["Images"])
async def list_tested_images(
    tested: Optional[bool] = Query(True, description="Filter by tested status: true, false"),
):
    """List all the tested image names with all versions."""
    try:
        return await db.get_tested_images(tested=tested)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tested images: {str(e)}")


@router.get("/images/{image_name}/list", response_model=list[S.ImageResponse], tags=["Images"])
async def get_image_versions(image_name: str):
    """Get the image with all versions and their status."""
    try:
        images = await db.get_image_by_name(image_name)
        if not images:
            raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found")
        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting image {image_name}: {str(e)}")


@router.get("/images/{image_name}/tested", response_model=list[S.ImageResponse], tags=["Images"])
async def get_tested_image_versions(
    image_name: str,
    tested: Optional[bool] = Query(True, description="Filter by tested status: true, false"),
):
    """Get tested image with versions, optionally filtered by tested status."""
    try:
        images = await db.get_tested_image_by_name(name=image_name, tested=tested)
        if not images:
            raise HTTPException(status_code=404, detail=f"Tested image '{image_name}' not found")
        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tested image {image_name}: {str(e)}")


@router.post("/images/create", response_model=S.ImageDomainResponse, status_code=201, tags=["Images"])
async def create_image(
    image: S.ImageCreate):
    """Create a new entry for an image."""
    try:
        return await db.create_image(image)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating image {image.name}: {str(e)}")

@router.post("/images/{image_name}/create", response_model=S.ImageResponse, status_code=201, tags=["Images"])
async def create_image_version(
    image_name: str,
    version: S.ImageVersion):
    """Create a new entry for an image version.

    """
    try:
        result = await db.create_image_version(name=image_name, version=version.version)
        if not result:
                raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating image version {image_name}: {str(e)}")



@router.put("/images/{image_name}/tested", response_model=S.ImageResponse, tags=["Images"])
async def set_image_tested(
    image_name: str,
    data: S.ImageTested):
    """Set image running in staging to tested."""
    try:
        image = await db.set_image_tested(name=image_name, version=data.version, tested=data.tested)
        if not image:
            raise HTTPException(status_code=404, detail=f"Image '{image_name}' version '{data.version}' not found")
        return image
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting image tested {image_name}: {str(e)}")


@router.put("/images/{image_name}/domain", response_model=list[S.ImageResponse], tags=["Images"])
async def update_image_domain(
    image_name: str,
    domain: S.ImageDomain):
    """Update domain for all versions of an image."""
    try:
        images = await db.update_image_domain(name=image_name, domain=domain.domain)
        if not images:
            raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found")
        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating image domain {image_name}: {str(e)}")


@router.put("/images/{image_name}/rename", response_model=list[S.ImageResponse], tags=["Images"])
async def rename_image(
    image_name: str,
    new_name: S.ImageRename):
    """
    Rename image: first updates the name in all domain.images lists,
    then renames all image entries.
    """
    try:
        images = await db.rename_image(old_name=image_name, new_name=new_name.name)
        if not images:
            raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found")
        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renaming image {image_name}: {str(e)}")


@router.delete("/images/{image_name}", tags=["Images"])
async def delete_image(image_name: str):
    """
    Delete image: first removes it from all domain.images lists,
    then deletes all image versions.
    """
    try:
        result = await db.delete_image(name=image_name)
        if not result:
            raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image {image_name}: {str(e)}")


# =============================================================================
# Domains Endpoints
# =============================================================================


@router.get("/domains/list", response_model=list[S.DomainResponse], tags=["Domains"])
async def list_all_domains():
    """List all the domains with names, versions, status, and list of images."""
    try:
        return await db.get_all_domains()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all domains: {str(e)}")


@router.get("/domains/active", response_model=list[S.DomainResponse], tags=["Domains"])
async def list_active_domains(
    env: Optional[str] = Query(None, description="Filter by deployment environment: dev, staging, prod"),
):
    """List all the active domains with names, versions, image versions and status."""
    try:
        return await db.get_active_domains(deployed=env)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active domains: {str(e)}")


@router.get("/domains/{domain_name}", response_model=list[S.DomainResponse], tags=["Domains"])
async def get_domain(domain_name: str):
    """List all the domain entries with all image versions and status."""
    try:
        domains = await db.get_domain_by_name(domain_name)
        if not domains:
            raise HTTPException(status_code=404, detail=f"Domain '{domain_name}' not found")
        return domains
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting domain: {str(e)}")


@router.get("/domains/{domain_name}/active", response_model=list[S.DomainResponse], tags=["Domains"])
async def get_active_domain(
    domain_name: str,
    env: Optional[str] = Query(None, description="Filter by deployment environment: dev, staging, prod"),
):
    """List active domain with version and image versions."""
    try:
        domain = await db.get_active_domain_by_name(domain_name, deployed=env)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Active domain '{domain_name}' not found")
        return domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active domain: {str(e)}")

@router.post("/domains/{domain_name}/create", response_model=S.DomainResponse, status_code=201, tags=["Domains"])
async def create_domain(
    domain_name: str,
    version: S.DomainCreate):
    """Create a new version of domain with all the related tested images."""
    try:
        return await db.create_domain(name=domain_name, version=version.version)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating domain: {str(e)}")


@router.put("/domains/update", response_model=list[S.DomainResponse], tags=["Domains"])
async def update_domains(domains: S.DomainUpdate | list[S.DomainUpdate]):
    """Update image version in the domain list."""
    try:
        if isinstance(domains, S.DomainUpdate): domains = [domains]
        return await db.update_domains(domains)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating domains: {str(e)}")


@router.put("/domains/tested", response_model=list[S.DomainResponse], tags=["Domains"])
async def set_domains_tested(domains: S.DomainTested | list[S.DomainTested]):
    """Set domain status to tested."""
    try:
        if isinstance(domains, S.DomainTested): domains = [domains]
        return await db.set_domains_tested(domains)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting domains tested: {str(e)}")


@router.put("/domains/active", response_model=list[S.DomainResponse], tags=["Domains"])
async def set_domains_active(domains: S.DomainActive | list[S.DomainActive]):
    """
    Set domain to active state.
    Will remove active state from the previous version and set it to the provided.
    """
    try:
        # Normalize to list
        if isinstance(domains, S.DomainActive): domains = [domains]
        return await db.set_domains_active(domains)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting domain active: {str(e)}")


@router.put("/domains/promote", response_model=list[S.DomainResponse], tags=["Domains"])
async def promote_domains(domains: S.DomainPromote | list[S.DomainPromote]):
    """Promote domain version to the provided environment."""
    try:
        # Normalize to list
        if isinstance(domains, S.DomainPromote): domains = [domains]
        return await db.promote_domains(domains)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error promoting domains: {str(e)}")


@router.put("/domains/{domain_name}/rename", response_model=list[S.DomainResponse], tags=["Domains"])
async def rename_domain(
    domain_name: str,
    name: S.DomainRename):
    """
    Rename domain: first updates the domain field in all related images,
    then renames all domain entries.
    """
    try:
        domain = await db.rename_domain(old_name=domain_name, new_name=name.name)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain '{domain_name}' not found")
        return domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renaming domain: {str(e)}")


@router.delete("/domains/{domain_name}", tags=["Domains"])
async def delete_domain(domain_name: str):
    """Delete domain."""
    try:
        domain = await db.delete_domain(name=domain_name)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain '{domain_name}' not found")
        elif domain["deleted"] is False:
            raise HTTPException(status_code=400, detail=domain["error"])
        else:
            return domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting domain {domain_name}: {str(e)}")


@router.delete("/domains/{domain_name}/{version}", tags=["Domains"])
async def delete_domain_version(
    domain_name: str,
    version: str):
    """
    Delete domain version.
    """
    try:
        domain = await db.delete_domain_version(name=domain_name, version=version)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain '{domain_name}' version '{version}' not found")
        return domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting domain version {domain_name} {version}: {str(e)}")
