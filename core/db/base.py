# app/db/base.py
"""
SQLAlchemy declarative base
===========================

This module defines the declarative base class used by all
SQLAlchemy ORM models in the application.

All database models must inherit from this `Base` class in order
to:
- Be registered in SQLAlchemy's metadata
- Support table creation and migrations
- Enable ORM features such as relationships and mappings
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """
