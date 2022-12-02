from __future__ import annotations

from typing import (
    Protocol,
    Type,
)

from pydantic import SecretStr
from xoa_driver import testers

from ..datasets.enums import EProductType


class IProps(Protocol):
    product: EProductType
    host: str
    port: int
    password: SecretStr


def get_tester_inst(props: IProps, username: str = "xoa-manager", debug=False) -> testers.GenericAnyTester | None:
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
