from __future__ import annotations
from typing import TypedDict, NewType, Protocol
from pydantic import SecretStr
from .datasets.enums import EProductType


TesterID = NewType("TesterID", str)


class IProps(Protocol):
    product: EProductType
    host: str
    port: int
    password: SecretStr


class StorageResource(TypedDict):
    id: str
    product: EProductType
    host: str
    port: int
    password: SecretStr
    name: str
    keep_disconnected: bool
