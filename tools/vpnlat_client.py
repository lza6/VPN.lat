# -*- coding: utf-8 -*-
"""VPN.lat hetecn full-chain client (reconstructed from blutter AOT decompile)."""
import json, base64, os, ssl, urllib.request, urllib.error, re, random, time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = bytes([228,106,158,106,164,178,100,138,
             242,202,206,238,96,148,128,232,
             220,128,210,98,206,160,222,236,
             210,168,128,198,66,72,216,174])
VPN_LAT_HDR = ("YlhWNUlIQmxjbThnYlhWNUlIQmxibVJsYW04TkNuUmhiblJ2SUhSeVlXSmhhbThnY0dGeVlTQnNaV1Z5SUdWemRHOE5DbTExZVNCd1pYSnZJRzExZVNCd1pXNWtaV3B2"
               "/_VPN.lat-/-com.vpn.lat-/wg/-0003")
AUTH = "Bearer V1ZOQ01HRlRRakJhVTBKdVpGaE9NRmxUUW5oa1YxVm5aRWRWWjFwSFZuVT0="
BASE = "https://hetecn.com"

def encrypt(plain: str) -> str:
    nonce = os.urandom(12)
    ct = AESGCM(KEY).encrypt(nonce, plain.encode(), None)
    return base64.b64encode(ct[:-16] + nonce + ct[-16:]).decode()

def headers(lang="es"):
    info_json = json.dumps({
        "isRooted": False, "isRealDevice": False, "hasCorrectlyInstalled": True,
        "rootedOrJailbroken": False, "fridaSuspected": False, "emulator": False,
        "debuggerAttached": False, "compromised": False, "system": "Android",
        "seenAds": True, "loadAds": True, "isPro": False}, separators=(",", ":"))
    check = encrypt("com.vpn.lat - 3.9.57 - 7789 - _android - 0")
    return {"Content-Type": "application/json", "vpn-lat": VPN_LAT_HDR,
            "Accept-Language": lang, "info": check, "mx": info_json,
            "Corp": "2", "Authorization": AUTH, "User-Agent": "Dart/3.5 (dart:io)"}

def get(path, proxy=None, timeout=15):
    h = headers()
    if proxy:
        px = urllib.request.ProxyHandler({"http": f"http://{proxy}", "https": f"http://{proxy}"})
        op = urllib.request.build_opener(px)
    else:
        op = urllib.request.build_opener()
    r = op.open(urllib.request.Request(BASE + path, headers=h), timeout=timeout)
    return json.loads(r.read().decode())

if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "/server"
    proxy = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(get(p, proxy), ensure_ascii=False)[:2000])
