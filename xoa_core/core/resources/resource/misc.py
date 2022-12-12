from __future__ import annotations

import hashlib
from typing import Type

from pydantic import (
    BaseModel,
    Field,
    SecretStr,
)
from xoa_driver import testers

from .models.types import (
    EProductType,
    TesterID,
)


class Credentials(BaseModel):
    product: EProductType
    host: str
    port: int = Field(default=22606, gt=0, lt=65535)
    password: SecretStr = SecretStr("xena")


def get_tester_inst(props: Credentials, username: str = "xoa-manager", debug=False) -> testers.GenericAnyTester | None:
    tester_type: Type[testers.GenericAnyTester] | None = {
        EProductType.VALKYRIE: testers.L23Tester,
        EProductType.CHIMERA: testers.L23Tester,
        EProductType.VANTAGE: testers.L23Tester,
        EProductType.VULKAN: testers.L47Tester,
        EProductType.SAFIRE: testers.L47Tester,
    }.get(props.product, None)
    return tester_type(
        host=props.host,
        username=username,
        password=props.password.get_secret_value(),
        port=props.port,
        debug=debug,
    ) if tester_type else None


def make_resource_id(host: str, port: int) -> TesterID:
    val_bytes = f"{host}:{port}".encode("utf-8")
    return TesterID(hashlib.md5(val_bytes).hexdigest())
