"""Local vision model on the AI box (Qwen3.8-27B), for classification and grunt work only - never for facts.

Reach it through the SSH tunnel from this Mac:
    ssh -N -L 18080:127.0.0.1:8080 -L 18082:127.0.0.1:8082 aibox
18080 = vLLM on the 3090 Ti (fast, handles several requests at once); 18082 = llama.cpp on the 5060 Ti (slow).

usage:
    from llm import ask_json
    out = ask_json("Is this page a map? Answer {\"map\": true|false}", images=["page.jpg"])
"""
import base64
import io
import json
import os
import re
import time
import urllib.request

from PIL import Image

URL = os.environ.get("AW_LLM_URL", "http://127.0.0.1:18080/v1/chat/completions")
MODEL = "qwen3.8-27b"


def _image_part(img, max_px=1600):
    """Path or PIL image -> data-URL part, downscaled so the long side is at most max_px."""
    im = Image.open(img) if isinstance(img, str) else img
    im = im.convert("RGB")
    if max(im.size) > max_px:
        k = max_px / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}}


def ask(prompt, images=(), max_px=1600, max_tokens=1500, think=False, temperature=0.0, url=URL, tries=3):
    """One chat turn; returns the answer text (thinking, if on, is dropped)."""
    content = [_image_part(i, max_px) for i in images] + [{"type": "text", "text": prompt}]
    body = {"model": MODEL, "messages": [{"role": "user", "content": content}], "temperature": temperature,
            "max_tokens": max_tokens, "chat_template_kwargs": {"enable_thinking": think}}
    if think:
        body["thinking_token_budget"] = 4096
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                msg = json.load(r)["choices"][0]["message"]
            return (msg.get("content") or "").strip()
        except Exception as e:  # server busy or restarting; back off
            if i == tries - 1:
                raise
            time.sleep(10 * (i + 1))


def parse_json(text):
    """First JSON object or array in a model answer (tolerates ```json fences and chatter)."""
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("no JSON in answer: " + text[:200])
    return json.JSONDecoder().raw_decode(text[start:])[0]


def ask_json(prompt, images=(), **kw):
    text = ask(prompt + "\n\nAnswer with JSON only.", images, **kw)
    try:
        return parse_json(text)
    except ValueError:
        return {"_unparsed": text}
