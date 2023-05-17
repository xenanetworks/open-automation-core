"""
Exceptions which are thrown to outside for being handled by user
"""

from .core.exceptions import (
    MultiModeError,
    TestSuiteNotExistError,
)
from .core.resources.resource.exceptions import (
    InvalidTesterTypeError,
    TesterCommunicationError,
    IsDisconnectedError,
    IsConnectedError,
    UnknownResourceError,
)
__all__ = (
    "MultiModeError",
    "TestSuiteNotExistError",
    "InvalidTesterTypeError",
    "TesterCommunicationError",
    "IsDisconnectedError",
    "IsConnectedError",
    "UnknownResourceError",
)
