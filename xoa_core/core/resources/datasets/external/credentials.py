import hashlib
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
)
from ..enums import EProductType


class Credentials(BaseModel):
    product: EProductType
    host: str
    port: int = Field(default=22606, gt=0, lt=65535)
    password: SecretStr = SecretStr("xena")

    @property
    def id(self) -> str:
        val_bytes = f"{self.host}:{self.port}".encode("utf-8")
        return hashlib.md5(val_bytes).hexdigest()
