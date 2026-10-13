"""One-off classifier for 212a's stage phase: the Qwen3.8-27B vision model on this VM's own
card (vLLM at 127.0.0.1:8080, OpenAI-compatible - the same replica the book stage uses),
answering the SAME three questions the Clef-flash default asks (commons.CLEF_STATE/CLEF_Q)
with a 0..1 confidence probability each. The lead's answer to request 003 approved it
ONE-OFF: Clef-flash is not running anywhere (the 5060 Ti now serves the matcher), and this
VM cannot open the ssh tunnel. Classification only - the ban on the local vision model for
fit PLACEMENT (ef84a05) stays in force. Rows it classifies carry the note through
fit.cover.stage's classifier_note, and the run is recorded in data/cover.

usage (the one-off driver for the 212a live run):
    .venv/bin/python -c "import sys; sys.path.insert(0, 'fit');
        import cover, cover_qwen8080
        cover.stage(str(cover.ROOT), classifier=cover_qwen8080.classify, live=True,
                    classifier_note=cover_qwen8080.NOTE)"
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import commons  # noqa: E402  (CLEF_STATE, CLEF_Q - the same questions as the default)
import llm      # noqa: E402  (the proven client for this exact model: ask, parse_json)

URL = os.environ.get("AW_8080_LLM_URL", "http://127.0.0.1:8080/v1/chat/completions")
NOTE = "qwen3.8-27b vLLM 127.0.0.1:8080 (one-off, lead's answer to request 003)"

_PQ = "; ".join("%s: %s" % (k, q["instructions"]) for k, q in commons.CLEF_Q.items())
PROMPT = (commons.CLEF_STATE +
          " For each of these three questions, give your confidence probability (a number "
          "from 0.0 to 1.0) that the answer is YES. - " + _PQ +
          ' Answer with JSON only: {"p_plan": number, "p_birdseye": number, "p_photo": number}')


def _one(r, tries=3):
    """One row's local jpg -> {p_plan, p_birdseye, p_photo} clamped to 0..1, rounded 4.
    A parse failure (chatter instead of JSON) retries up to tries times. The row is
    cover.stage's {"row": files.jsonl row, "local": path}."""
    title = ((r.get("row") or {}).get("title") or r.get("title") or "?")
    last = None
    for i in range(tries):
        try:
            d = llm.parse_json(llm.ask(PROMPT, images=[r["local"]], url=URL,
                                       max_tokens=200, tries=2))
            return {("p_" + k): round(min(1.0, max(0.0, float(d["p_" + k]))), 4)
                    for k in commons.CLEF_Q}
        except Exception as e:
            last = e
    raise RuntimeError("qwen8080: %s: %r" % (title[:80], str(last)[:200]))


def classify(rows, workers=4):
    """fit.cover.stage's injectable classifier contract: rows dicts with a local jpg path
    -> one {p_plan, p_birdseye, p_photo} per row, aligned. 4 workers (the 3090 Ti's vLLM
    handles several requests at once); order preserved by map."""
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(_one, rows))
