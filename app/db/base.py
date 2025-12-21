#!/usr/bin/env python3
"""
SQLAlchemy Declarative Base
Day 6.1 - Foundation for persistence layer
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    
    This is intentionally minimal:
    - No engine binding
    - No session logic
    - No metadata overrides
    
    All database models must inherit from this class.
    """
    pass