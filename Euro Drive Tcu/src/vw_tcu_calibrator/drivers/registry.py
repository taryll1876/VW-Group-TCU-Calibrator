from __future__ import annotations

from ..core import ProjectContext
from .base import TcuDriver
from .j2534 import J2534Driver
from .obdlink import OBDLinkDriver
from .openport import OpenPort2Driver
from .raw_can import RawCanDriver
from .sim import SimDriver


def create_driver(name: str, *, context: ProjectContext | None = None, **kwargs) -> TcuDriver:
    key = name.lower().replace("_", "-")
    if key in {"sim", "simulator", "mock"}:
        return SimDriver(context=context)
    if key in {"raw-can", "can", "python-can"}:
        return RawCanDriver(context=context, **kwargs)
    if key in {"j2534", "passthru", "pass-thru"}:
        return J2534Driver(context=context, **kwargs)
    if key in {"openport", "openport2", "tactrix"}:
        return OpenPort2Driver(context=context, **kwargs)
    if key in {"obdlink", "stn"}:
        return OBDLinkDriver(context=context, **kwargs)
    raise ValueError(f"Unknown driver: {name}")
