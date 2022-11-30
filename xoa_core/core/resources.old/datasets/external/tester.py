
from typing import Tuple
from pydantic import (
    BaseModel,
    SecretStr,
    constr,
)
from xoa_core.core import const
from .. import enums
from .module import ModuleExternalModel


class TesterExternalModel(BaseModel):
    id: constr(regex=const.TESTER_ID_PATTERN)  # type: ignore
    product: enums.EProductType
    host: str
    port: int
    password: SecretStr
    name: str = " - "
    reserved_by: str = ""
    is_connected: bool = False
    modules: Tuple[ModuleExternalModel, ...] = tuple()
    keep_disconnected: bool = False
    max_name_len: int = 0  # used by UI validation (Tester Name) & config validation
    max_comment_len: int = 0  # used by UI validation (Tester Description) & config validation
    max_password_len: int = 0  # used by UI validation (Tester Password) & config validation
