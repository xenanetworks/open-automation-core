from __future__ import annotations
import os
from pathlib import Path
import sys
import oyaml as yaml
import importlib.util
from typing import (
    TYPE_CHECKING,
    Optional,
    Type,
    Generator,
)

from pydantic import BaseModel
from xoa_core.core.exceptions import InvalidPluginError
if TYPE_CHECKING:
    from types import ModuleType

from .datasets import (
    PluginMeta,
    PluginData,
    build_test_params
)

from ..plugin_abstract import PluginAbstract


META_FILE_NAME = 'meta.yml'


def __load_module(path: str) -> Generator["ModuleType", None, None]:
    """Load module from path to the var"""
    for child in os.listdir(path):
        ilename, _ = os.path.splitext(child)
        module_name = f"{os.path.split(path)[-1]}.{ilename}"
        spec = importlib.util.spec_from_file_location(
            module_name,
            os.path.join(path, child),
        )
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        yield mod


def __make_plugin(module_path: str, meta: PluginMeta) -> Optional["PluginData"]:
    """Create plugin model."""
    entry_class: Optional[Type["PluginAbstract"]] = None
    model_class: Optional[Type["BaseModel"]] = None
    for module in __load_module(module_path):
        if entry_class is None:
            entry_class = getattr(module, meta.entry_object, None)
        if model_class is None:
            model_class = getattr(module, meta.data_model, None)
    if not (entry_class and model_class):
        return None
    if not issubclass(entry_class, PluginAbstract):
        raise InvalidPluginError(entry_class, PluginAbstract)
    if not issubclass(model_class, BaseModel):
        raise InvalidPluginError(model_class, BaseModel)
    return PluginData(
        meta=meta,
        entry_class=entry_class,
        model_class=build_test_params(model_class)
    )


def __read_meta(path: str) -> "PluginMeta":
    """Read metafile"""
    with open(path, "r") as outfile:
        data = yaml.load(outfile, Loader=yaml.SafeLoader)
        return PluginMeta(**data)


def load_plugin(path: str | Path) -> Generator[PluginData, None, None]:
    sys.path.append(str(path))
    for child in os.listdir(path):
        child_path = os.path.abspath(os.path.join(path, child))
        if not os.path.isdir(child_path):
            continue
        meta_path = os.path.join(child_path, META_FILE_NAME)
        if not os.path.exists(meta_path):
            continue
        meta = __read_meta(meta_path)
        plugin = __make_plugin(child_path, meta)
        if not plugin:
            continue
        yield plugin
