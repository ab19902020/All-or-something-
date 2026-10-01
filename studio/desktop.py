from __future__ import annotations

import socket
import threading
import time

import uvicorn
import webview


def free_port(preferred: int = 8765) -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", preferred))
        return preferred
    except OSError:
        sock.close()
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


def wait_for_server(port: int, timeout: float = 12.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.4):
                return
        except OSError:
            time.sleep(0.15)
    raise RuntimeError("United Road Studio server did not start.")


def main():
    port = free_port()
    config = uvicorn.Config("studio.app:app", host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_server(port)
    webview.create_window(
        "United Road Studio",
        f"http://127.0.0.1:{port}",
        width=1500,
        height=940,
        min_size=(1050, 700),
    )
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()
