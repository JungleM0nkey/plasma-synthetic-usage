#!/usr/bin/env python3
"""Fetch synthetic.new API usage quotas from /v2/quotas."""
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
KEY_FILE = CONFIG_HOME / "synthetic" / "api-key"
LEGACY_KEY_FILE = CONFIG_HOME / "octofriend" / "keys.json5"
API_URL = "https://api.synthetic.new/v2/quotas"
TIMEOUT = 15
KEY_PATTERN = re.compile(r"syn_[A-Za-z0-9_-]+")


def get_api_key():
    candidates = [os.environ.get("SYNTHETIC_API_KEY")]
    for path in (KEY_FILE, LEGACY_KEY_FILE):
        try:
            candidates.append(path.read_text())
        except OSError:
            continue

    for candidate in candidates:
        if not candidate:
            continue
        match = KEY_PATTERN.search(candidate)
        if match:
            return match.group(0)
    return None


def main():
    key = get_api_key()
    if not key:
        print(json.dumps({"ok": False, "error": "API key not found"}))
        return
    try:
        req = urllib.request.Request(API_URL, headers={"Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        print(json.dumps({"ok": True, "data": data}))
    except urllib.error.HTTPError as e:
        print(json.dumps({"ok": False, "error": "HTTP " + str(e.code)}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))


if __name__ == "__main__":
    main()
