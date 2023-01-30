from typing import (
    Optional,
    Type,
    Protocol,
)
from pydantic import SecretStr
from xoa_driver import testers
from .datasets import enums


class IProps(Protocol):
    id: str
    product: enums.EProductType
    host: str
    port: int
    password: SecretStr


def get_tester_inst(props: IProps, username: str = "xoa-manager", debug=False) -> Optional[testers.GenericAnyTester]:
    tester_type: Optional[Type[testers.GenericAnyTester]] = {
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
