#!/usr/bin/env python3
"""WebSocket Feeds - Optional real-time market data for TPS19.

This module provides a minimal interface for subscribing to WebSocket
streams. If the 'websocket-client' package is not installed, it will
gracefully degrade to a no-op.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

try:
    from websocket import WebSocketApp  # type: ignore
    _WS_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    WebSocketApp = None  # type: ignore
    _WS_AVAILABLE = False


class WebSocketFeeds:
    def __init__(self) -> None:
        self._threads = []
        self.available = _WS_AVAILABLE

    def subscribe_generic(self, url: str, on_message: Callable[[str], None]) -> Optional[threading.Thread]:
        """Subscribe to a generic WebSocket URL and invoke callback on messages.
        Returns a thread handle if started, else None.
        """
        if not self.available:
            print("⚠️ WebSocket client not installed. Skipping subscription.")
            return None

        def _on_message(ws, message):  # type: ignore
            try:
                on_message(message)
            except Exception as e:  # pragma: no cover - defensive
                print(f"❌ on_message error: {e}")

        def _on_error(ws, error):  # type: ignore
            print(f"❌ WebSocket error: {error}")

        def _on_close(ws, code, msg):  # type: ignore
            print(f"🔌 WebSocket closed: {code} {msg}")

        def _run():
            app = WebSocketApp(url, on_message=_on_message, on_error=_on_error, on_close=_on_close)
            app.run_forever()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        self._threads.append(thread)
        print(f"✅ WebSocket subscription started: {url}")
        return thread

    def close(self) -> None:
        # Best-effort; threads will exit when WS closes or process ends.
        print("🔌 Closing WebSocket feeds (best-effort)")
