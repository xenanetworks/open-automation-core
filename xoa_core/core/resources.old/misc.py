from __future__ import annotations
from typing import (
    Type,
    Protocol,
)
from pydantic import SecretStr
from xoa_driver import testers
from .datasets import enums





def get_tester_inst(props: IProps, username: str = "xoa-manager", debug=False) -> testers.GenericAnyTester | None:
    tester_type: Type[testers.GenericAnyTester] | None = {
        enums.EProductType.VALKYRIE: testers.L23Tester,
        enums.EProductType.CHIMERA: testers.L23Tester,
        enums.EProductType.VANTAGE: testers.L23Tester,
        enums.EProductType.VULKAN: testers.L47Tester,
        enums.EProductType.SAFIRE: testers.L47Tester,
    }.get(props.product, None)
    return tester_type(
        host=props.host,
        username=username,
        password=props.password.get_secret_value(),
        port=props.port,
        debug=debug,
    ) if tester_type else None
