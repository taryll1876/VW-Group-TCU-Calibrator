import pytest

from vw_tcu_calibrator.core import DEFAULT_CONTEXT
from vw_tcu_calibrator.drivers.registry import create_driver
from vw_tcu_calibrator.safety import assert_project_mode_allows_frame


def test_project_mode_blocks_write_service():
    with pytest.raises(PermissionError):
        assert_project_mode_allows_frame(DEFAULT_CONTEXT, bytes.fromhex("03 2E 19 01 00 00 00 00"))


def test_project_mode_allows_read_did():
    assert_project_mode_allows_frame(DEFAULT_CONTEXT, bytes.fromhex("03 22 19 01 00 00 00 00"))


def test_sim_driver_read_did_response():
    driver = create_driver("sim")
    response = driver.read_did(0x1901)
    assert response is not None
    assert response[1] == 0x62


def test_sim_driver_write_payload_blocked():
    driver = create_driver("sim")
    with pytest.raises(PermissionError):
        driver.write_payload(0x7E1, bytes.fromhex("03 2E 19 01 00 00 00 00"))
