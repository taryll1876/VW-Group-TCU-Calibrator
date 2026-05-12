from __future__ import annotations

from .core import ProjectContext


BLOCKED_UDS_SERVICES = {
    0x27: "SecurityAccess is blocked in this project.",
    0x2E: "WriteDataByIdentifier is blocked in this project.",
    0x31: "RoutineControl is blocked unless explicitly reviewed.",
    0x34: "RequestDownload is blocked in this project.",
    0x36: "TransferData is blocked in this project.",
    0x37: "RequestTransferExit is blocked in this project.",
}


READ_ONLY_ALLOWED_SERVICES = {0x10, 0x22, 0x3E}


def assert_read_only_frame(payload: bytes) -> None:
    if len(payload) < 2:
        return
    service = payload[1]
    if service in BLOCKED_UDS_SERVICES:
        raise PermissionError(BLOCKED_UDS_SERVICES[service])


def assert_project_mode_allows_frame(context: ProjectContext, payload: bytes) -> None:
    assert_read_only_frame(payload)
    if context.read_only and len(payload) >= 2 and payload[1] not in READ_ONLY_ALLOWED_SERVICES:
        raise PermissionError(
            "Project mode is read_only; only diagnostic session, tester-present, and read-DID services are allowed."
        )
