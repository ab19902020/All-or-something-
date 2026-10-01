from __future__ import annotations

import argparse
import threading
import webbrowser

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run United Road Studio locally.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        threading.Timer(1.1, lambda: webbrowser.open(url)).start()
    uvicorn.run("studio.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
