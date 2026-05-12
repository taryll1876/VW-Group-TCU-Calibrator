from vw_tcu_calibrator.health import compute_health_score, pressure_jump_detected
from vw_tcu_calibrator.models import LiveValues


def test_health_score_nominal():
    values = LiveValues(
        {
            "k1_clutch_pressure_candidate": 36.5,
            "k2_clutch_pressure_candidate": 35.1,
            "gearbox_oil_pressure_or_temp_candidate": 88.0,
        }
    )
    assert compute_health_score(values) >= 90


def test_pressure_jump_detected():
    before = LiveValues({"k1_clutch_pressure_candidate": 20.0})
    after = LiveValues({"k1_clutch_pressure_candidate": 25.0})
    assert pressure_jump_detected(before, after)
