from __future__ import annotations
from operator import attrgetter
from typing import (
    TYPE_CHECKING,
    Optional,
    Type,
    List,
    Dict,
    Set,
    NamedTuple,
    Any,
)
from pydantic import BaseModel
import semver

if TYPE_CHECKING:
    from ..plugin_abstract import PluginAbstract, PStateConditionsFacade, PPipeFacade

from xoa_core import __version__


class PortIdentity(BaseModel):
    tester_id: str
    tester_index: int
    module_index: int
    port_index: int

    @property
    def name(self) -> str:
        return f"P-{self.tester_index}-{self.module_index}-{self.port_index}"


class TestParameters(BaseModel):
    username: str
    port_identities: List[PortIdentity]
    config: BaseModel

    @property
    def get_testers_ids(self) -> Set[str]:
        return set(map(
            attrgetter("tester_id"),
            self.port_identities
        ))


class PluginMeta(BaseModel):
    name: str
    version: str
    core_version: str
    author: Optional[List[str]] = None
    entry_object: str
    data_model: str

    @property
    def is_supported(self) -> bool:
        return semver.match(__version__, self.core_version)


class PluginData(NamedTuple):
    """
    A test suit container.
    Contain references to starting points and metadata of the plugin
    """
    meta: PluginMeta
    entry_class: Type["PluginAbstract"]
    model_class: Type["TestParameters"]


class Plugin:
    def __init__(self, plugin_data: PluginData, debug: bool = False) -> None:
        self.plugin_data = plugin_data
        self.debug = debug

    def parse_config(self, config: Dict[str, Any]) -> None:
        self.params = self.plugin_data.model_class.parse_obj(config)  # can raise ValidationError

    def assign_testers(self, tester_getter) -> None:
        self.testers = tester_getter(self.params.get_testers_ids, self.params.username, self.debug)

    def create_test_suite(self, state_conditions: "PStateConditionsFacade", xoa_out: "PPipeFacade") -> "PluginAbstract":
        return self.plugin_data.entry_class(
            state_conditions=state_conditions,
            xoa_out=xoa_out,
            testers=self.testers,
            params=self.params
        )


def build_test_params(_test_config: Type["BaseModel"]) -> Type["TestParameters"]:
    class TP(TestParameters):
        config: _test_config
    return TP
