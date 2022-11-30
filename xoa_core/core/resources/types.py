from typing import NewType, Protocol
from pydantic import SecretStr
from .datasets.enums import EProductType


TesterID = NewType("TesterID", str)


class IProps(Protocol):
    product: EProductType
    host: str
    port: int
    password: SecretStr
