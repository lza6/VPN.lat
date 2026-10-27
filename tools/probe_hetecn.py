# -*- coding: utf-8 -*-
"""VPN.lat hetecn API probe — try auth variants in one shot."""
import json, ssl, urllib.request, sys

BASE = "https://hetecn.com"
TROLL = "Bearer V1ZOQ01HRlRRakJhVTBKdVpGaE9NRmxUUW5oa1YxVm5aRWRWWjFwSFZuVT0="
FKEY = "AIzaSyD65AQDKt4kEA7xY3gcLtcthyqUCMySyeI"
CTX = ssl.create_default_context()
UA_DART = "Dart/3.5 (dart:io)"

def req(path, headers=None, method="GET"):
    h = {"User-Agent": UA_DART}
    if headers: h.update(headers)
    r = urllib.request.Request(BASE + path, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=20, context=CTX) as resp:
            body = resp.read(4000)
            return resp.status, body[:1500]
    except urllib.error.HTTPError as e:
        return e.code, e.read(1500)
    except Exception as e:
        return None, str(e).encode()

variants = [
    ("plain", {}),
    ("bearer-troll", {"Authorization": TROLL}),
    ("bearer-troll+keyhdr", {"Authorization": TROLL, "X-Api-Key": FKEY}),
    ("keyhdr", {"X-Api-Key": FKEY}),
    ("referer", {"Referer": "https://vpn.lat/"}),
    ("xrequested", {"X-Requested-With": "com.vpn.lat"}),
]
paths = ["/server", "/random/wire/server"]
for p in paths:
    for name, hdrs in variants:
        code, body = req(p, hdrs)
        print(f"{p} [{name}] -> {code} {body[:200]}")
