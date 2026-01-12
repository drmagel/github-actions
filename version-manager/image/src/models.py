"""
SQLAlchemy models for database tables.
"""

from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Image(Base):
    """Image table model."""

    __tablename__ = "images"

    name = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    domain = Column(String, nullable=False)
    tested = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "domain": self.domain,
            "tested": self.tested,
        }


class Domain(Base):
    """Domain table model."""

    __tablename__ = "domains"

    name = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    deployed = Column(String, default="dev")  # 'dev', 'staging', 'prod'
    tested = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
    images = Column(JSON, default=list)  # [{"name": "", "version": ""}, ...]

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "deployed": self.deployed,
            "tested": self.tested,
            "active": self.active,
            "images": self.images or [],
        }

class ImageDomain(Base):
    """Image domain table model."""

    __tablename__ = "image_domain"

    image = Column(String, primary_key=True)
    domain = Column(String, primary_key=True)
    domains = Column(JSON, default=list)  # [domain_name, ...]

    def to_dict(self):
        return {
            "image": self.image,
            "domain": self.domain,
            "domains": self.domains or [],
        }
