import typing
from abc import (
    ABC,
    abstractmethod,
)

if typing.TYPE_CHECKING:
    from enum import Enum

    from pydantic import BaseModel
    from xoa_driver import testers as driver_testers

    from .test_suites.datasets import TestParameters


TestersType = typing.Dict[str, "driver_testers.GenericAnyTester"]
DT = typing.TypeVar("DT", bound="BaseModel")


class TransmitFunc(typing.Protocol):
    def __call__(self, msg: typing.Any, *, msg_type: "Enum") -> None: ...  # noqa: E704


class PPipeFacade(typing.Protocol):
    def __init__(self, transmit: "TransmitFunc") -> None: ...  # noqa: E704

    def send_statistics(self, data: typing.Union[typing.Dict, "BaseModel"]) -> None:
        """Method used for push statistics data into the messages pipe for future distribution"""

    def send_progress(self, progress: int) -> None:
        """Method used for push current progress value into the messages pipe for future distribution"""

    def send_warning(self, warning: Exception) -> None:
        """Method used for push warning exceptions into the messages pipe for future distribution"""

    def send_error(self, error: Exception) -> None:
        """Method used for push error exceptions into the messages pipe for future distribution"""


class PStateConditionsFacade(typing.Protocol):
    async def wait_if_paused(self) -> None:
        """
            Block plugin execution if pause event is set.

            Notice: User must explicitly place this function at the place when pause can be happen.
        """
    async def stop_if_stopped(self) -> None:
        """
            Stop plugins execution by raising a StopPlugin exception if user call running_test_stop method.

            Notice: User must explicitly place this function at the place when pause can be happen.
        """


class PluginAbstract(ABC, typing.Generic[DT]):
    """TestSuitePlugin abstraction class, all test suite must be inherited from it."""

    __slots__ = {
        "state_conditions": """Facade contains methods which can help pause or stop Plugin execution.""",
        "xoa_out": """Facade for transmit messages to user.""",
        "testers": """Dictionary of <TESTER_ID>: <TESTER_INSTANCE>""",
        "port_identities": """PortIdentities a dictionary of <SLOT_ID>: <PortIdentity>""",
        "cfg": """Test-Suite configuration model defined by plugin."""
    }

    def __init__(self, state_conditions: "PStateConditionsFacade", xoa_out: "PPipeFacade", testers: TestersType, params: "TestParameters") -> None:
        self.state_conditions = state_conditions
        """Facade contains methods which can help pause or stop Plugin execution."""
        self.xoa_out = xoa_out
        """Facade for transmit messages to user."""
        self.testers = testers
        """Dictionary of <TESTER_ID>: <TESTER_INSTANCE>"""
        self.port_identities = params.port_identities
        """PortIdentities a dictionary of <SLOT_ID>: <PortIdentity>"""
        self.cfg: DT = params.config
        """Test configuration model defined by plugin."""
        self.prepare()

    def prepare(self) -> None:
        """Optional method used for declare plugins attributes."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Method starts test suite execution."""
        raise NotImplementedError()

    async def on_pause(self) -> None:
        """Optional method will be called and awaited when plugin receive pause event"""
        return None

    async def on_continue(self) -> None:
        """Optional method will be called and awaited when plugin receive continue event"""
        return None

    async def on_stop(self) -> None:
        """Optional method will be called and awaited when plugin receive stop event"""
        return None
