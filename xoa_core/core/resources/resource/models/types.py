from enum import IntEnum
from typing import (
    NewType,
    TypedDict,
)
from pydantic import SecretStr


TesterID = NewType("TesterID", str)
ModuleID = NewType("TesterID", str)  # <TesterID>-<Module Slot Index>
PortID = NewType("TesterID", str)  # <TesterID>-<ModuleID>-<Port Index>
JsonStr = NewType("JsonStr", str)


class EProductType(IntEnum):
    VALKYRIE = 1
    VULKAN = 2
    SAFIRE = 3
    VANTAGE = 4
    CHIMERA = 5


class StorageResource(TypedDict):
    id: TesterID
    product: EProductType
    host: str
    port: int
    password: SecretStr
    name: str
    keep_disconnected: bool
