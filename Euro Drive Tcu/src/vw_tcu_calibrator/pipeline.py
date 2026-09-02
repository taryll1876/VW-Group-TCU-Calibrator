from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Iterable


class AsyncTelemetryPipeline:
    """Async orchestration layer with optional process-based heavy workers.

    This keeps I/O and queue orchestration in asyncio while allowing higher-cost
    analysis tasks to be farmed out to a process pool when scaling demands it.
    """

    def __init__(self, *, queue_size: int = 128, max_workers: int = 1) -> None:
        self.queue_size = queue_size
        self.queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=queue_size)
        self._executor = ProcessPoolExecutor(max_workers=max_workers) if max_workers > 0 else None

    async def publish(self, item: dict[str, Any]) -> None:
        await self.queue.put(item)

    async def consume(self, *, count: int | None = None) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        while count is None or len(items) < count:
            item = await self.queue.get()
            items.append(item)
            if count is not None and len(items) >= count:
                break
        return items

    async def process_heavy(self, item: dict[str, Any], func: Callable[[dict[str, Any]], Any]) -> Any:
        if self._executor is None:
            return func(item)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, func, item)

    def close(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True)
