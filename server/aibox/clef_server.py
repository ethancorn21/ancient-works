"""Clef-flash decision model behind a tiny HTTP API on the AI box (Finder re-ranker bake-off).

Runs from /opt/llm/clef (venv + weights pinned there by setup.sh):
    CUDA_VISIBLE_DEVICES=<5060 Ti uuid> /opt/llm/clef/.venv/bin/python clef_server.py [--port 8083] [--quant 8bit|4bit|none]

POST /v1/systemone        one SystemOne request body; images as base64 strings in "images_b64"
POST /v1/systemone_batch  {"requests": [...]} -> {"responses": [...]} in one forward pass
GET  /health
Listens on 127.0.0.1 only; reach it from the Mac through the SSH tunnel.
"""
import argparse
import base64
import io
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import torch
from PIL import Image

MODEL_DIR = "/opt/llm/clef/clef-flash"
sys.path.insert(0, MODEL_DIR)
from joint_schema_model import (ClefModel, JointSchemaHead, collate_records, encode_record,  # noqa: E402
                                systemone, systemone_answer)

LOCK = threading.Lock()  # one forward pass at a time on a 16 GB card
M = {}


def load(quant):
    """Like joint_schema_model.load_release_model, plus optional bitsandbytes quantisation of the backbone
    (the 9B does not fit a 16 GB card in bf16). The joint head stays bf16."""
    from safetensors.torch import load_file
    from transformers import AutoProcessor, BitsAndBytesConfig, Qwen3_5ForConditionalGeneration
    kw = {}
    if quant == "8bit":
        kw["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True, llm_int8_skip_modules=["visual", "lm_head"])
    elif quant == "4bit":
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16,
                                                       llm_int8_skip_modules=["visual", "lm_head"])
    backbone = Qwen3_5ForConditionalGeneration.from_pretrained(MODEL_DIR, dtype=torch.bfloat16, device_map={"": "cuda"}, **kw)
    backbone.config.use_cache = False
    head = JointSchemaHead(**json.load(open(f"{MODEL_DIR}/joint_head_config.json")))
    head.load_state_dict(load_file(f"{MODEL_DIR}/joint_head.safetensors"), strict=True)
    head = head.to(device="cuda", dtype=torch.bfloat16)
    return ClefModel(backbone, head).eval(), AutoProcessor.from_pretrained(MODEL_DIR)


def with_images(req):
    req = dict(req)
    imgs = req.pop("images_b64", None) or []
    if imgs:
        req["images"] = [Image.open(io.BytesIO(base64.b64decode(b))).convert("RGB") for b in imgs]
    return req


@torch.inference_mode()
def batch(reqs):
    model, proc = M["model"], M["proc"]
    enc = [encode_record(proc.tokenizer, r, processor=proc) for r in reqs]
    logits = model(collate_records(enc, proc.tokenizer.pad_token_id, torch.device("cuda")))
    out = []
    for r, e, lg in zip(reqs, enc, logits):
        out.append({"model": r.get("model", "clef-flash"), "answers": {
            q.question_id: systemone_answer(r["questions"][q.question_id], dict(zip(q.option_ids, ql.float().softmax(-1).tolist())))
            for q, ql in zip(e.questions, lg)}, "usage": {"input_tokens": len(e.input_ids), "output_tokens": 0}})
    return out


class H(BaseHTTPRequestHandler):
    def reply(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"ok": True, "quant": M["quant"], "vram_gb": round(torch.cuda.memory_allocated() / 2**30, 2)})
        self.reply(404, {"error": "unknown path"})

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)))
            t = time.time()
            with LOCK:
                if self.path == "/v1/systemone":
                    out = systemone(M["model"], M["proc"], with_images(body))
                elif self.path == "/v1/systemone_batch":
                    out = {"responses": batch([with_images(r) for r in body["requests"]])}
                else:
                    return self.reply(404, {"error": "unknown path"})
            out["seconds"] = round(time.time() - t, 3)
            self.reply(200, out)
        except Exception as e:  # report, keep serving
            self.reply(400, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8083)
    ap.add_argument("--quant", default="8bit", choices=["8bit", "4bit", "none"])
    a = ap.parse_args()
    t = time.time()
    M["model"], M["proc"] = load(a.quant)
    M["quant"] = a.quant
    print(f"clef-flash loaded ({a.quant}) in {time.time() - t:.0f}s, "
          f"{torch.cuda.memory_allocated() / 2**30:.1f} GB on {torch.cuda.get_device_name()}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
