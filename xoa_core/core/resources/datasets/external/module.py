from typing import (
    Tuple,
    Optional,
)
from pydantic import BaseModel
from .port import PortExternalModel


class ModuleExternalModel(BaseModel):
    id: int
    model: str
    reserved_by: str
    ports: Tuple[PortExternalModel, ...]
    name: str = " - "
    can_media_config: bool = False
    """used by UI validation (Test Module Config - Media Configuration) & config validation"""

    is_chimera: bool = False
    can_local_time_adjust: bool = False
    """used by UI validation (Test Module Config - Local Clock Adjustment) & config validation"""

    max_clock_ppm: Optional[int] = None
    """used by UI validation (Test Module Config - Local Clock Adjustment) & config validation"""
