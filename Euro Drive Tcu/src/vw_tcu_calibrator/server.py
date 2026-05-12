from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterable


@dataclass(frozen=True)
class ToolkitSignalSnapshot:
    """Normalized internal signal set that the UI expects."""

    k1_clutch_pressure_candidate_bar: float | None
    k2_clutch_pressure_candidate_bar: float | None
    oil_temp_c: float | None
    oil_pressure_bar: float | None = None
    abuse_index: float | None = None
    rpm: float | None = None
    throttle_pct: float | None = None
    virtual_gear: int | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "ToolkitSignalSnapshot":
        return ToolkitSignalSnapshot(
            k1_clutch_pressure_candidate_bar=_maybe_float(d.get("k1_clutch_pressure_candidate_bar")),
            k2_clutch_pressure_candidate_bar=_maybe_float(d.get("k2_clutch_pressure_candidate_bar")),
            oil_temp_c=_maybe_float(d.get("oil_temp_c")),
            oil_pressure_bar=_maybe_float(d.get("oil_pressure_bar")),
            abuse_index=_maybe_float(d.get("abuse_index")),
            rpm=_maybe_float(d.get("rpm")),
            throttle_pct=_maybe_float(d.get("throttle_pct")),
            virtual_gear=_maybe_int(d.get("virtual_gear")),
        )

    def to_ui_payload(self) -> dict[str, Any]:
        return {
            "k1_clutch_pressure_candidate_bar": self.k1_clutch_pressure_candidate_bar,
            "k2_clutch_pressure_candidate_bar": self.k2_clutch_pressure_candidate_bar,
            "oil_temp_c": self.oil_temp_c,
            "oil_pressure_bar": self.oil_pressure_bar,
            "abuse_index": self.abuse_index,
            "rpm": self.rpm,
            "throttle_pct": self.throttle_pct,
            "virtual_gear": self.virtual_gear,
        }


def _maybe_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _maybe_int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


class _Broadcaster:
    def __init__(self) -> None:
        self._clients: list[queue.Queue[dict[str, Any]]] = []
        self._lock = threading.Lock()

    def register(self) -> queue.Queue[dict[str, Any]]:
        q: queue.Queue[dict[str, Any]] = queue.Queue()
        with self._lock:
            self._clients.append(q)
        return q

    def unregister(self, q: queue.Queue[dict[str, Any]]) -> None:
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)

    def broadcast(self, payload: dict[str, Any]) -> None:
        with self._lock:
            clients = list(self._clients)
        for q in clients:
            if q.qsize() > 10:
                try:
                    q.get_nowait()
                except queue.Empty:
                    pass
            q.put(payload)


class ToolkitServer:
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 8765,
        snapshot_source: Iterable[ToolkitSignalSnapshot],
        tick_seconds: float = 0.25,
    ) -> None:
        self.host = host
        self.port = port
        self._snapshot_source = snapshot_source
        self.tick_seconds = tick_seconds
        self._broadcaster = _Broadcaster()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._httpd: ThreadingHTTPServer | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._httpd:
            try:
                self._httpd.shutdown()
            except Exception:
                pass

    def _run(self) -> None:
        server = self
        parent_snapshot_source = self._snapshot_source

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                if self.path in ("/", "/health"):
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": True, "ts": time.time()}).encode("utf-8"))
                    return

                if self.path == "/stream":
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Connection", "keep-alive")
                    self.end_headers()

                    q = server._broadcaster.register()
                    try:
                        while not server._stop.is_set():
                            try:
                                payload = q.get(timeout=1.0)
                            except queue.Empty:
                                payload = {"type": "keepalive", "ts": time.time()}
                            self.wfile.write((json.dumps(payload) + "\n").encode("utf-8"))
                            self.wfile.flush()
                    finally:
                        server._broadcaster.unregister(q)
                    return

                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
                return

        self._httpd = ThreadingHTTPServer((self.host, self.port), Handler)

        def broadcaster_loop() -> None:
            last = 0.0
            for snap in parent_snapshot_source:
                if self._stop.is_set():
                    break
                now = time.time()
                if now - last < self.tick_seconds:
                    time.sleep(max(0.0, self.tick_seconds - (now - last)))
                last = time.time()
                payload = snap.to_ui_payload()
                payload.update({"type": "snapshot", "ts": time.time()})
                self._broadcaster.broadcast(payload)

        t = threading.Thread(target=broadcaster_loop, daemon=True)
        t.start()

        try:
            self._httpd.serve_forever()
        except Exception:
            pass


def run_toolkit_server(*, snapshot_source: Iterable[ToolkitSignalSnapshot], host: str, port: int) -> None:
    srv = ToolkitServer(host=host, port=port, snapshot_source=snapshot_source)
    srv.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        srv.stop()
