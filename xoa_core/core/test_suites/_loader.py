from __future__ import annotations
import os
import sys
import oyaml as yaml
from pathlib import Path
from importlib import util, reload as reload_module

from typing import (
    TYPE_CHECKING,
    Optional,
    Type,
    Generator,
)

from pydantic import BaseModel, class_validators

if TYPE_CHECKING:
    from types import ModuleType

from xoa_core.core.exceptions import InvalidPluginError
from .datasets import (
    PluginMeta,
    PluginData,
    build_test_params
)
from ..plugin_abstract import PluginAbstract


META_FILE_NAME = 'meta.yml'


def __get_root_module_name(folder_path: str) -> str:
    root_module_name = ''
    meta_path = os.path.join(folder_path, META_FILE_NAME)
    if os.path.exists(meta_path): # it must inside root folder right?
        root_module_name = Path(folder_path).parts[-1]

    return root_module_name


def __load_module(path: str) -> Generator["ModuleType", None, None]:
    """Load module from path to the var"""
    for child in os.listdir(path):
        ilename, _ = os.path.splitext(child)
        module_name = f"{os.path.split(path)[-1]}.{ilename}"
        spec = util.spec_from_file_location(
            module_name,
            os.path.join(path, child),
        )
        if not spec or not spec.loader:
            continue
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        yield mod

def __reload_module(path: str) -> Generator["ModuleType", None, None]:
    """reload module that matches path"""
    yield from __load_module(path)
    root_module_name = __get_root_module_name(path)
    for name in list(sys.modules):
        if root_module_name in name:
            # bypass duplicate validator check
            # https://github.com/pydantic/pydantic/blob/1c02b19b035e0e1929b9dd9dce9573349244d496/pydantic/v1/class_validators.py#L155C22-L155C22
            class_validators._FUNCS.clear()
            reload_module(sys.modules[name])

def __make_plugin(module_path: str, meta: PluginMeta, reload: bool = False) -> Optional["PluginData"]:
    """Create plugin model."""
    entry_class: Optional[Type["PluginAbstract"]] = None
    model_class: Optional[Type["BaseModel"]] = None
    loading_func = __reload_module if reload else __load_module
    for module in loading_func(module_path):
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

def __register_path(path: str | Path) -> None:
    str_path = str(path)
    if str_path in sys.path:
        return None
    sys.path.append(str_path)


def reload_plugin(plugin_path: str | Path) -> Generator[PluginData, None, None]:
    meta_path = os.path.join(plugin_path, META_FILE_NAME)
    meta = __read_meta(meta_path)
    plugin = __make_plugin(str(plugin_path), meta, reload=True)
    assert plugin
    yield plugin

def load_plugin(path: str | Path, reload: bool = False) -> Generator[PluginData, None, None]:
    __register_path(path)
    for child in os.listdir(path):
        child_path = os.path.abspath(os.path.join(path, child))
        if not os.path.isdir(child_path):
            continue
        meta_path = os.path.join(child_path, META_FILE_NAME)
        if not os.path.exists(meta_path):
            continue
        meta = __read_meta(meta_path)
        plugin = __make_plugin(child_path, meta, reload=reload)
        if not plugin:
            continue
        yield plugin