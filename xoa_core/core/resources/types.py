from __future__ import annotations
from typing import TypedDict
from pydantic import SecretStr
from .datasets.enums import EProductType
from .resource.models.tester import TesterID

__all__ = (
    "TesterID",
    "StorageResource",
)


class StorageResource(TypedDict):
    id: str
    product: EProductType
    host: str
    port: int
    password: SecretStr
    name: str
    keep_disconnected: bool
