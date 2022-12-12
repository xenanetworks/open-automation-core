from __future__ import annotations
import os
from pathlib import Path
from typing import (
    Generator,
    Optional,
    Dict,
    Tuple,
    List,
)

from xoa_core.core import exceptions
from . import datasets
from . import _loader as loader


class PluginController:
    __slots__ = ("__paths", "__test_suites")

    def __init__(self) -> None:
        self.__paths: Tuple[str | Path, ...] = tuple()
        self.__test_suites: Dict[str, "datasets.PluginData"] = dict()

    def register_path(self, path: str | Path) -> None:
        """Register custom path of plugins"""
        self.__paths += (
            os.path.abspath(path)
            if not os.path.isabs(path)
            else path,
        )
        self.__init_plugins()

    def available_test_suites(self) -> List[str]:
        return list(self.__test_suites.keys())

    def suite_info(self, name: str) -> Optional[Dict]:
        suite = self.__test_suites.get(name, None)
        if not suite:
            return None
        return dict(
            test_suit=suite.meta.dict(exclude={"entry_object", "data_model"}),
            schema=suite.model_class.schema_json(),
        )

    def get_plugin_data(self, name: str) -> "datasets.PluginData":
        plugin_data = self.__test_suites.get(name, None)
        if plugin_data is None:
            raise exceptions.TestSuiteNotExistError(name)
        elif not plugin_data.meta.is_supported:
            raise exceptions.TestSuiteVersionError(name, plugin_data.meta.core_version)
        return plugin_data

    def get_plugin(self, name: str, debug: bool = False) -> "datasets.Plugin":
        plugin_data = self.get_plugin_data(name)
        return datasets.Plugin(plugin_data, debug)

    def __read_plugins(self) -> Generator["datasets.PluginData", None, None]:
        """Read plugins from provided paths."""
        for path in self.__paths:
            yield from loader.load_plugin(path)

    def __init_plugins(self) -> None:
        """Read plugins in to the local storage"""
        self.__test_suites.clear()
        self.__test_suites = dict(
            (plugin.meta.name, plugin)
            for plugin in self.__read_plugins()
        )
