from __future__ import annotations

import argparse
import socket
import threading
import webbrowser

import uvicorn


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="Run United Road Studio.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Expose Studio on the local network so an Android phone can connect.",
    )
    args = parser.parse_args()

    host = "0.0.0.0" if args.mobile else args.host
    desktop_url = f"http://127.0.0.1:{args.port}"

    if args.mobile:
        phone_url = f"http://{local_ip()}:{args.port}"
        print("")
        print("United Road Studio mobile mode")
        print("--------------------------------")
        print(f"On this computer: {desktop_url}")
        print(f"On your Android phone (same Wi-Fi): {phone_url}")
        print("Open the phone URL in Chrome, then use Add to Home screen / Install app.")
        print("")
    elif not args.no_browser:
        threading.Timer(1.1, lambda: webbrowser.open(desktop_url)).start()

    uvicorn.run("studio.app:app", host=host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
