"""
Database connection and operations.
"""

import os
from typing import Optional
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete, and_, or_

import models as M
import schemas as S

class Database:
    """Database operations handler."""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def connect(self):
        """Initialize database connection. Uses PostgreSQL or SQLite based on USE_POSTGRESQL env var."""
        use_postgresql = os.getenv("USE_POSTGRESQL", "true").lower() == "true"

        if use_postgresql:
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "version_manager")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "postgres")
            database_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            db_path = os.getenv("SQLITE_PATH", "/app/data/version_manager.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            database_url = f"sqlite+aiosqlite:///{db_path}"

        self.engine = create_async_engine(database_url, echo=True)
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables(self):
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(M.Base.metadata.create_all)

    def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    # =========================================================================
    # Image Operations
    # =========================================================================

    async def get_all_images(self) -> list[dict]:
        """Get all image names with their domains."""
        async with self._get_session() as session:
            result = await session.execute(select(M.ImageDomain))
            return [img.to_dict() for img in result.scalars().all()]

    async def get_all_images_versions(self) -> list[dict]:
        """Get all images with their versions and tested status."""
        async with self._get_session() as session:
            result = await session.execute(select(M.Image))
            return [img.to_dict() for img in result.scalars().all()]

    async def get_tested_images(self, tested: bool = True) -> list[dict]:
        """Get all tested images, optionally filtered by tested status."""
        async with self._get_session() as session:
            query = select(M.Image).where(M.Image.tested == tested)
            result = await session.execute(query)
            return [img.to_dict() for img in result.scalars().all()]

    async def get_image_by_name(self, name: str) -> list[dict]:
        """Get all versions of an image by name."""
        async with self._get_session() as session:
            result = await session.execute(select(M.Image).where(M.Image.name == name))
            return [img.to_dict() for img in result.scalars().all()]

    async def get_tested_image_by_name(self, name: str, tested: bool = True) -> list[dict]:
        """Get tested versions of an image by name, optionally filtered by tested status."""
        async with self._get_session() as session:
            query = select(M.Image).where(and_(M.Image.name == name, M.Image.tested == tested))
            result = await session.execute(query)
            return [img.to_dict() for img in result.scalars().all()]

    async def create_image(self, image: S.ImageCreate) -> dict:
        """Create a new image entry."""
        async with self._get_session() as session:
            result = await session.execute(
                select(M.ImageDomain).where(M.ImageDomain.image == image.name)
            )
            db_image_domain = result.scalar_one_or_none()
            if not db_image_domain:
                db_image_domain = M.ImageDomain(
                    image=image.name,
                    domain=image.domain,
                    domains=[image.domain],
                )
                session.add(db_image_domain)
                await session.commit()
                await session.refresh(db_image_domain)
            return db_image_domain.to_dict()

    async def create_image_version(self, name: str, version: str) -> dict:
        """
        Create a new entry for an image version.
        Auto-updates the active domain in dev environment by adding or replacing this image in the domain's images list.
        """
        async with self._get_session() as session:
            result = await session.execute(select(M.ImageDomain).where(M.ImageDomain.image == name))
            db_image_domain = result.scalar_one_or_none()
            if not db_image_domain:
                return None
            
            domain_name = db_image_domain.domain
            
            # Create the image version
            db_image = M.Image(
                name=name,
                version=version,
                domain=domain_name,
                tested=False,
            )
            session.add(db_image)
            await session.flush()  # Flush to get the image ID
            
            # Auto-update the active domain in dev environment
            # Find the active domain version in dev environment
            active_domain_result = await session.execute(
                select(M.Domain).where(
                    and_(
                        M.Domain.name == domain_name,
                        M.Domain.deployed == "dev",
                        M.Domain.active == True
                    )
                )
            )
            active_domain = active_domain_result.scalar_one_or_none()
            
            if active_domain:
                # Update the domain's images list: add or replace this image
                images_list = list(active_domain.images or [])
                # Remove existing entry for this image name if present
                images_list = [img for img in images_list if img.get("name") != name]
                # Add the new image version
                images_list.append({"name": name, "version": version, "tested": False})
                active_domain.images = images_list
            
            await session.commit()
            await session.refresh(db_image)
            return db_image.to_dict()

    async def set_image_tested(self, name: str, version: str, tested: bool) -> Optional[dict]:
        """Set image tested status."""

        def _set_tested(images: list[str] | None, name: str, version: str, tested: bool) -> list[str]:
            images = list(images or [])
            for image in images:
                if image.get("name") == name and image.get("version") == version:
                    image["tested"] = tested
                    break
            return images

        async with self._get_session() as session:
            # Step 1. Retrieve the ImageDomain mapping record
            result = await session.execute(select(M.ImageDomain).where(M.ImageDomain.image == name))
            db_image_domain = result.scalar_one_or_none()
            if not db_image_domain:
                return None
            # Step 2. Retrieve and update Domain records
            result = await session.execute(select(M.Domain).where(M.Domain.name == db_image_domain.domain))
            db_domains = result.scalars().all()
            for domain in db_domains:
                domain.images = _set_tested(domain.images, name, version, tested)      
                flag_modified(domain, "images")

            # Step 3. Update the Image record
            await session.execute(
                update(M.Image).where(and_(M.Image.name == name, M.Image.version == version)).values(tested=tested)
            )
            await session.commit()
            # Fetch and return the updated image
            result = await session.execute(
                select(M.Image).where(and_(M.Image.name == name, M.Image.version == version))
            )
            db_image = result.scalar_one_or_none()
            return db_image.to_dict() if db_image else None


    async def update_image_domain(self, name: str, domain: str) -> list[dict] | None:
        """
        Update domain for all versions of an image and its mapping.
        1. Retrieve and update the ImageDomain mapping record
        2. Bulk update all versions of the image
        3. Fetch and return all updated images
        """
        
        def _add_domain(domains: list[str] | None, domain: str) -> list[str]:
            current_list = list(domains or [])
            if domain not in current_list:
                current_list.append(domain)
            return current_list

        async with self._get_session() as session:
            # Step 1. Retrieve and update the ImageDomain mapping record
            result = await session.execute(
                select(M.ImageDomain).where(M.ImageDomain.image == name)
            )
            db_image_domain = result.scalar_one_or_none()

            if not db_image_domain:
                return None
            db_image_domain.domain = domain
            db_image_domain.domains = _add_domain(db_image_domain.domains, domain)

            # Step 2. Bulk update all versions of the image
            await session.execute(
                update(M.Image)
                .where(M.Image.name == name)
                .values(domain=domain)
            )

            await session.commit()
            
            # Step 3. Fetch and return all updated images
            result = await session.execute(select(M.Image).where(M.Image.name == name))
            return [img.to_dict() for img in result.scalars().all()]


    async def rename_image(self, old_name: str, new_name: str) -> list[dict]:
        """
        Rename image: first updates the name in all domain.images lists,
        then renames all image entries.
        """
        async with self._get_session() as session:
            # Step 1: Update image name in all domain.images lists
            result = await session.execute(select(M.Domain))
            db_domains = result.scalars().all()
            for domain in db_domains:
                if domain.images and any(img.get("name") == old_name for img in domain.images):
                    domain.images = [
                        {"name": new_name, "version": img["version"]} 
                        if img.get("name") == old_name else img 
                        for img in domain.images
                    ]


            # Step 2. Update ImageDomain
            await session.execute(
                update(M.ImageDomain)
                .where(M.ImageDomain.image == old_name)
                .values(image=new_name)
            )

            # Step 3. Update Image
            await session.execute(
                update(M.Image)
                .where(M.Image.name == old_name)
                .values(name=new_name)
            )

            await session.commit()
            result = await session.execute(select(M.Image).where(M.Image.name == new_name))
            return [img.to_dict() for img in result.scalars().all()]

    async def delete_image(self, name: str) -> dict:
        """
        Delete image: first removes it from all domain.images lists,
        then deletes all image versions.
        """
        async with self._get_session() as session:
            # Step 1: Check if ImageDomain exists
            result = await session.execute(
                select(M.ImageDomain).where(M.ImageDomain.image == name)
            )
            if not result.scalar_one_or_none():
                return None

            # Step 2: Remove image from all domain.images lists
            result = await session.execute(select(M.Domain))
            db_domains = result.scalars().all()
            for domain in db_domains:
                domain.images = [img for img in domain.images if img["name"] != name]

            # Step 3: Delete all image versions
            result = await session.execute(delete(M.Image).where(M.Image.name == name))
            versions_removed = result.rowcount

            # Step 4: Delete from ImageDomain
            await session.execute(
                delete(M.ImageDomain).where(M.ImageDomain.image == name)
            )

            await session.commit()
            return {"deleted": name, "versions_removed": versions_removed}

    # =========================================================================
    # Domain Operations
    # =========================================================================

    async def get_all_domains(self) -> list[dict]:
        """Get all domains with their images."""
        async with self._get_session() as session:
            result = await session.execute(select(M.Domain))
            return [domain.to_dict() for domain in result.scalars().all()]

    async def get_active_domains(self, deployed: Optional[str] = None) -> list[dict]:
        """Get all active domains, optionally filtered by deployment environment."""
        async with self._get_session() as session:
            query = select(M.Domain).where(M.Domain.active == True)
            if deployed:
                query = query.where(M.Domain.deployed == deployed)
            result = await session.execute(query)
            return [domain.to_dict() for domain in result.scalars().all()]

    async def get_domain_by_name(self, name: str) -> list[dict]:
        """Get all versions of a domain by name."""
        async with self._get_session() as session:
            result = await session.execute(select(M.Domain).where(M.Domain.name == name))
            return [domain.to_dict() for domain in result.scalars().all()]

    async def get_active_domain_by_name(self, name: str, deployed: Optional[str] = None) -> Optional[dict]:
        """Get active version of a domain by name."""
        async with self._get_session() as session:
            query = select(M.Domain).where(M.Domain.name == name).where(M.Domain.active == True)
            if deployed:
                query = query.where(M.Domain.deployed == deployed)
            result = await session.execute(query)
            return [domain.to_dict() for domain in result.scalars().all()]

    async def create_domain(self, name: str, version: str) -> dict:
        """Create a new domain version with tested images. Sets new version as Active."""
        async with self._get_session() as session:
            # Deactivate all previous versions of this domain in 'dev' environment
            await session.execute(
                update(M.Domain).where(and_(M.Domain.name == name, M.Domain.deployed == "dev")).values(active=False)
            )

            # Get all images for this domain
            result = await session.execute(
                select(M.Image)
                .where(and_(
                    M.Image.domain == name
                ))
                .order_by(M.Image.name, M.Image.version.desc())
            )

            # Get the latest version for each image name
            latest_images = {}
            for img in result.scalars().all():
                if img.name not in latest_images:
                    latest_images[img.name] = img

            # Create domain with images stored as JSON, set as Active
            db_domain = M.Domain(
                name=name,
                version=version,
                deployed="dev",
                tested=False,
                active=True,  # New domain version is automatically Active
                images=[{"name": img.name, "version": img.version, "tested": img.tested} for img in latest_images.values()],
            )
            session.add(db_domain)
            await session.commit()
            await session.refresh(db_domain)
            return db_domain.to_dict()

    async def update_domains(self, domains: list[S.DomainUpdate]) -> list[dict]:
        """Update image versions in domains."""

        async with self._get_session() as session:
            updated_domains = []
            async def _enrich_images_list(images: list[S.ImageVersion]) -> list[dict]:
                filters = or_(*[
                    and_(M.Image.name == item.name, M.Image.version == item.version)
                    for item in images
                ])
                result = await session.execute(select(M.Image).where(filters))
                return [{'name': item.name, 'version': item.version, 'tested': item.tested} for item in result.scalars().all()]
            
            for domain_update in domains:
                result = await session.execute(
                    select(M.Domain).where(
                        and_(M.Domain.name == domain_update.name, M.Domain.version == domain_update.version)
                    )
                )
                domain = result.scalar_one_or_none()
                if domain:
                    # Merge images: update existing or add new
                    existing_images = {img['name']: img for img in (domain.images or [])}
                    for img in await _enrich_images_list(domain_update.images):
                        existing_images[img['name']] = {"name": img['name'], "version": img['version'], "tested": img['tested']}
                    domain.images = list(existing_images.values())
                    await session.commit()
                    await session.refresh(domain)
                    updated_domains.append(domain.to_dict())
            return updated_domains

    async def set_domains_tested(self, domains: list[S.DomainTested]) -> list[dict]:
        """Set domains as tested."""

        async with self._get_session() as session:
            for domain in domains:
                await session.execute(
                    update(M.Domain)
                    .where(and_(M.Domain.name == domain.name, M.Domain.version == domain.version))
                    .values(tested=domain.tested)
                )
            await session.commit()
            conditions = or_(*[
                and_(M.Domain.name == d.name, M.Domain.version == d.version)
                for d in domains
            ])
            result = await session.execute(select(M.Domain).where(conditions))
            return [domain.to_dict() for domain in result.scalars().all()]

    async def set_domains_active(self, domains: list[S.DomainActive]) -> list[dict]:
        """Set domains as active, deactivating previous active versions."""
        async with self._get_session() as session:
            async def _enrich_domains_list(domains: list[S.DomainActive]) -> list[dict]:
                filters = or_(*[
                    and_(M.Domain.name == item.name, M.Domain.version == item.version)
                    for item in domains
                ])
                result = await session.execute(select(M.Domain).where(filters))
                return [{'name': domain.name, 'version': domain.version, 'deployed': domain.deployed, 'tested': domain.tested, 'active': domain.active} for domain in result.scalars().all()]

            db_domains = await _enrich_domains_list(domains)

            list_conditions = or_(*[
                and_(M.Domain.name == d['name'], M.Domain.deployed == d['deployed'])
                for d in db_domains
            ])
            deactivate_conditions = or_(*[
                and_(M.Domain.name == d['name'], M.Domain.deployed == d['deployed'], M.Domain.active == True)
                for d in db_domains
            ])
            activate_conditions = or_(*[
                and_(M.Domain.name == d['name'], M.Domain.version == d['version'], M.Domain.deployed == d['deployed'])
                for d in db_domains
            ])
            # Step 1. Deactivate all previous active versions
            await session.execute(
                update(M.Domain).where(deactivate_conditions).values(active=False)
            )
            # Step 2. Activate the specified versions
            await session.execute(
                update(M.Domain).where(activate_conditions).values(active=True)
            )

            await session.commit()
            result = await session.execute(select(M.Domain).where(list_conditions))
            return [domain.to_dict() for domain in result.scalars().all()]
            
    async def promote_domains(self, domains: list[S.DomainPromote]) -> list[dict]:
        """
        Promote domains to specified environment and set as active.
        The rule is:
        - dev -> staging, tested = false
        - staging -> prod, tested = true
        - prod -> prod (do not change, tested = true)
        The steps are:
        1. Deactivate all previous active version in promoted environment
        2. Promote the specified version
        3. Set the promoted version as active
        """

        async with self._get_session() as session:
            filter_deactivated = []
            filter_promoted = []
            
            def _promote_to(current_deployed: str) -> str:
                """Calculate target environment based on current deployed status."""            
                return "staging" if current_deployed == "dev" else "prod"

            def _is_tested(target_deployed: str) -> bool:
                """Determine tested status based on target environment."""
                return True if target_deployed == "prod" else False

            # Step #1. Fetch all domains to get their current deployed status
            conditions = or_(*[
                and_(M.Domain.name == d.name, M.Domain.version == d.version)
                for d in domains
            ])
            result = await session.execute(select(M.Domain).where(conditions))
            db_domains = {f"{d.name}:{d.version}": d for d in result.scalars().all()}

            for domain_promote in domains:
                domain_key = f"{domain_promote.name}:{domain_promote.version}"
                db_domain = db_domains.get(domain_key)
                if not db_domain:
                    continue
                
                current_deployed = db_domain.deployed
                target_deployed = _promote_to(current_deployed)
                
                # Add to filters for deactivation and promotion
                filter_deactivated.append(
                    and_(M.Domain.name == domain_promote.name, M.Domain.deployed == target_deployed)
                )
                filter_promoted.append(
                    and_(M.Domain.name == domain_promote.name, M.Domain.version == domain_promote.version)
                )

            # Step 2: Deactivate all previous active versions in target environments
            if filter_deactivated:
                await session.execute(
                    update(M.Domain).where(or_(*filter_deactivated)).values(active=False)
                )
            
            # Step 3: Promote and activate the specified domain versions
            if filter_promoted:
                for domain_promote in filter_promoted:
                    await session.execute(
                        update(M.Domain)
                        .where(and_(
                            domain_promote
                        ))
                        .values(
                            deployed=target_deployed,
                            tested=_is_tested(target_deployed),
                            active=True
                        )
                    )
            
            await session.commit()
            
            # Fetch and return the promoted domains
            if filter_promoted:
                result = await session.execute(select(M.Domain).where(or_(*filter_promoted)))
                return [domain.to_dict() for domain in result.scalars().all()]
            return []

    async def rename_domain(self, old_name: str, new_name: str) -> list[dict]:
        """
        Rename domain:
        1. rename all domain entries in Domain table.
        2. update the domain field in all related images in ImageDomain table,
        3. update the domain field in all related images in Image table,
        """
        def _add_domain(domains: list[str] | None, domain: str) -> list[str]:
            current_list = list(domains or [])
            return current_list if domain in current_list else current_list.append(domain)

        async with self._get_session() as session:
            # Step 1: Rename all domain entries
            result = await session.execute(update(M.Domain).where(M.Domain.name == old_name).values(name=new_name))
            if result.rowcount == 0:
                return None
            # Step 2: Update ImageDomain table with new domain name and add new domain to domains list
            result = await session.execute(select(M.ImageDomain).where(M.ImageDomain.domain == old_name))
            for image_domain in result.scalars().all():
                image_domain.domain = new_name
                image_domain.domains = _add_domain(image_domain.domains, new_name)
                flag_modified(image_domain, "domains")

            # Step 3: Update domain field in all related images
            await session.execute(update(M.Image).where(M.Image.domain == old_name).values(domain=new_name))

            await session.commit()
            result = await session.execute(select(M.Domain).where(M.Domain.name == new_name))
            return [domain.to_dict() for domain in result.scalars().all()]

    async def delete_domain_version(self, name: str, version: str) -> dict:
        """
        Delete domain version
        """
        async with self._get_session() as session:
            result = await session.execute(
                delete(M.Domain).where(and_(M.Domain.name == name, M.Domain.version == version))
            )
            if result.rowcount == 0:
                return None
            await session.commit()
            return {"deleted": True, "name": name, "version": version}

    async def delete_domain(self, name: str) -> dict:
        """
        Delete all domain versions:
        1. Make sure the domain exists
        2. Make sure the domain has no images in ImageDomain table
        3. Delete all domain versions
        """
        import sys
        async with self._get_session() as session:
            # Check if domain exists
            result = await session.execute(select(M.Domain).where(M.Domain.name == name))
            if len(result.scalars().all()) == 0:
                return None
            
            # Check if domain has images in ImageDomain table
            result = await session.execute(select(M.ImageDomain).where(M.ImageDomain.domain == name))
            if len(result.scalars().all()) > 0:
                return {"deleted": False, "name": name, "error": f"Domain {name} is in use by {result.rowcount} images"}
            
            # Delete domain
            result = await session.execute(delete(M.Domain).where(M.Domain.name == name))
            if result.rowcount == 0:
                return None
            else:
                await session.commit()
                return {"deleted": True, "name": name}

# Global database instance
db = Database()


async def init_db():
    """Initialize database connection and create tables."""
    await db.connect()
    await db.create_tables()
