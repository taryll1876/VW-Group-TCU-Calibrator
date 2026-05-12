import pytest

from vw_tcu_calibrator.safety import assert_read_only_frame
from vw_tcu_calibrator.uds import (
    EXTENDED_SESSION_REQUEST,
    is_positive_session_response,
    read_did_request,
    security_access_seed_request,
)


def test_extended_session_request_bytes():
    assert EXTENDED_SESSION_REQUEST == bytes.fromhex("02 10 03 00 00 00 00 00")


def test_positive_session_response():
    assert is_positive_session_response(bytes.fromhex("02 50 03 00 00 00 00 00"))


def test_read_did_request():
    assert read_did_request(0x1901) == bytes.fromhex("03 22 19 01 00 00 00 00")


def test_security_access_is_blocked():
    with pytest.raises(PermissionError):
        security_access_seed_request()


def test_write_service_is_blocked():
    with pytest.raises(PermissionError):
        assert_read_only_frame(bytes.fromhex("03 2E 19 01 00 00 00 00"))
