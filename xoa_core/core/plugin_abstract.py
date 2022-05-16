import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from enum import Enum

    from pydantic import BaseModel
    from xoa_driver import testers as driver_testers

    from .test_suites.datasets import TestParameters
    

TestersType = typing.Dict[str, "driver_testers.GenericAnyTester"]
DT = typing.TypeVar("DT", bound="BaseModel")

class TransmitFunc(typing.Protocol):
    def __call__(self, msg: typing.Any, *, msg_type: "Enum") -> None: ...

class PPipeFacade(typing.Protocol):
    def __init__(self, transmit: "TransmitFunc") -> None: ...
    def send_data(self, data: typing.Union[typing.Dict, "BaseModel"]) -> None: ...
    def send_statistics(self, data) -> None: ...
    def send_progress(self, progress: int) -> None: ...
    def send_warning(self, worning: Exception) -> None: ...
    def send_error(self, error: Exception) -> None: ...

class PStateConditionsFacade(typing.Protocol):
    async def wait_if_paused(self) -> None: ...
    async def stop_if_stopped(self) -> None: ...

class PluginAbstract(ABC, typing.Generic[DT]):
    """TestSuitePlugin abstraction class, all testsute must be inherited from it."""
    
    __slots__ = {
        "state_conditions": """Facade contains methods which can help pause or stop Plugin execution.""", 
        "xoa_out": """Facade for transmit messages to user.""", 
        "testers": """Dictionary of <TESTER_ID>: <TESTER_INSTANCE>""", 
        "port_identities":  """PortIdentities a dictionary of <SLOT_ID>: <PortIdentity>""", 
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
        """Test-Suite configuration model defined by plugin."""
        self.prepare()
    
    def prepare(self) -> None:
        """Optional method used for declare plugins attributes."""
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Method starts test suite execution."""
        raise NotImplementedError()
    
    async def on_pause(self) -> None:
        """Optioanal method will be called and awaited when plugin receave pause event"""
        return None
    
    async def on_continue(self) -> None:
        """Optioanal method will be called and awaited when plugin receave continue event"""
        return None
    
    async def on_stop(self) -> None: 
        """Optioanal method will be called and awaited when plugin receave stop event"""
        return None
