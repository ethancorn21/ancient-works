"""Client for the Clef-flash decision model on the AI box (server/aibox/clef_server.py), for the Finder re-ranker.

Tunnel: ssh -N -L 18083:127.0.0.1:8083 aibox

usage:
    from clef import decide
    ans = decide("LiDAR local relief image ...", {"earthwork": {"type": "noul", "instructions": "..."}}, images=[img])
    ans["earthwork"]["noul"]  -> probability of true
"""
import base64
import io
import json
import os
import urllib.request

from PIL import Image

URL = os.environ.get("AW_CLEF_URL", "http://127.0.0.1:18083")


def _b64(img, max_px=1024):
    im = Image.open(img) if isinstance(img, str) else img
    im = im.convert("RGB")
    if max(im.size) > max_px:
        k = max_px / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def _post(path, body):
    req = urllib.request.Request(URL + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out


def decide(state, questions, images=(), max_px=1024):
    body = {"model": "clef-flash", "state": state, "questions": questions, "images_b64": [_b64(i, max_px) for i in images]}
    return _post("/v1/systemone", body)["answers"]


def decide_batch(items, max_px=1024):
    """items: [(state, questions, images), ...] -> [answers, ...] in one forward pass."""
    reqs = [{"model": "clef-flash", "state": s, "questions": q, "images_b64": [_b64(i, max_px) for i in imgs]}
            for s, q, imgs in items]
    return [r["answers"] for r in _post("/v1/systemone_batch", {"requests": reqs})["responses"]]
