"""
Exceptions which are thrown to outside for being handled by user
"""

from .core.exceptions import (
    MultiModeError,
    TestSuiteNotExistError,
)

__all__ = (
    "MultiModeError",
    "TestSuiteNotExistError",
)
