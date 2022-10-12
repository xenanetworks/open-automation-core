import typing
from pydantic import (
    BaseModel,
    SecretStr
)
from xoa_core.core.resources.datasets import enums
T = typing.TypeVar("T", bound="CredentialsModel")


class CredentialsModel(BaseModel):
    id: str
    product: enums.EProductType
    host: str
    port: int
    password: SecretStr
    keep_disconnected: bool = False

    @classmethod
    def from_external(cls: typing.Type[T], external) -> T:
        return cls(**{"id": external.id, **external.dict()})
