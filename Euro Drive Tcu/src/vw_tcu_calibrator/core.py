from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProjectMode(str, Enum):
    READ_ONLY = "read_only"
    ENGINEERING = "engineering"


@dataclass(frozen=True)
class ProjectContext:
    mode: ProjectMode = ProjectMode.READ_ONLY
    name: str = "Euro Drive TCU Toolkit"

    @property
    def read_only(self) -> bool:
        return self.mode == ProjectMode.READ_ONLY

    def require_read_allowed(self) -> None:
        return None

    def require_write_allowed(self) -> None:
        if self.read_only:
            raise PermissionError(
                "Project mode is read_only. Write, unlock, flash, and protected control commands are disabled."
            )


DEFAULT_CONTEXT = ProjectContext()
