from __future__ import annotations


BLOCKED_UDS_SERVICES = {
    0x27: "SecurityAccess is blocked in this project.",
    0x2E: "WriteDataByIdentifier is blocked in this project.",
    0x31: "RoutineControl is blocked unless explicitly reviewed.",
    0x34: "RequestDownload is blocked in this project.",
    0x36: "TransferData is blocked in this project.",
    0x37: "RequestTransferExit is blocked in this project.",
}


def assert_read_only_frame(payload: bytes) -> None:
    if len(payload) < 2:
        return
    service = payload[1]
    if service in BLOCKED_UDS_SERVICES:
        raise PermissionError(BLOCKED_UDS_SERVICES[service])
