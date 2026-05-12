#!/usr/bin/env python3
"""
Environment pre-check script - run once before using moomooapi skill

Checks:
1. moomoo-api SDK installed
2. OpenD is reachable
"""
import sys
import socket
import os
import json

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

output_json = "--json" in sys.argv


def _check_sdk():
    """Check moomoo-api SDK is installed"""
    try:
        import moomoo
        current = getattr(moomoo, "__version__", "unknown")
        return True, f"moomoo-api {current}"
    except ImportError:
        return False, "moomoo-api not installed. Please run /install-moomoo-opend to install"


def _check_opend():
    """Check OpenD connectivity"""
    host = os.getenv("MOOMOO_OPEND_HOST", os.getenv("FUTU_OPEND_HOST", "127.0.0.1"))
    port = int(os.getenv("MOOMOO_OPEND_PORT", os.getenv("FUTU_OPEND_PORT", "11111")))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
        return True, f"OpenD reachable ({host}:{port})"
    except (ConnectionRefusedError, OSError) as e:
        return False, f"Cannot connect to OpenD ({host}:{port}): {e}. Please start OpenD first"
    finally:
        sock.close()


def main():
    results = []
    all_ok = True

    for name, check_fn in [("SDK", _check_sdk), ("OpenD", _check_opend)]:
        ok, msg = check_fn()
        results.append({"check": name, "ok": ok, "message": msg})
        if not ok:
            all_ok = False

    if output_json:
        print(json.dumps({"ok": all_ok, "checks": results}, ensure_ascii=False))
    else:
        for r in results:
            status = "✓" if r["ok"] else "✗"
            print(f"  {status} {r['check']}: {r['message']}")
        if all_ok:
            print("\nEnvironment check passed")
        else:
            print("\nEnvironment check failed, some features may not work")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
