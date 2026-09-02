from __future__ import annotations

import asyncio

from vw_tcu_calibrator.abuse import AbuseIndexModel
from vw_tcu_calibrator.pipeline import AsyncTelemetryPipeline


def test_abuse_index_model_scores_transient_load():
    model = AbuseIndexModel(window_size=8)
    samples = [
        {"pressure_bar": 30.0, "thermal_index": 20.0, "shaft_rpm": 1200.0},
        {"pressure_bar": 35.0, "thermal_index": 30.0, "shaft_rpm": 1400.0},
        {"pressure_bar": 42.0, "thermal_index": 55.0, "shaft_rpm": 2200.0},
        {"pressure_bar": 49.0, "thermal_index": 70.0, "shaft_rpm": 3200.0},
    ]
    score = model.score(samples)
    assert score > 0.0
    assert score <= 100.0


def test_async_pipeline_processes_messages_in_order():
    async def main() -> None:
        pipeline = AsyncTelemetryPipeline(queue_size=4)
        await pipeline.publish({"signal": "clutch_k1_pressure_bar", "value": 30.0})
        await pipeline.publish({"signal": "clutch_k2_pressure_bar", "value": 32.0})
        items = await pipeline.consume(count=2)
        assert [item["signal"] for item in items] == [
            "clutch_k1_pressure_bar",
            "clutch_k2_pressure_bar",
        ]

    asyncio.run(main())
