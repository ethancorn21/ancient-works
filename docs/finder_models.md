# Finder re-ranker: model tests

## Smoke test, 2026-10-10 (too small to decide anything)

Set: the 6 built sites' relief images (positives) and 12 relief crops of random ground 4-7 km from them (negatives).
Same question to both models: does this LiDAR relief image show an ancient earthwork?

| Model | Where | AUC | Probabilities | Speed |
|---|---|---|---|---|
| Clef-flash 9B (Cloudflare decision model, backbone 8-bit) | 5060 Ti | 0.86 | graded, 0.04-0.75 | 0.87 s/image, batches of 6 |
| Qwen3.8-27B, P(Yes) from token log-probs | 3090 + 3090 Ti | 0.57 | all-or-nothing (0.000 / 0.999) | ~1.5 s/image, 4 parallel |

Clef ranked Newark, Hopeton and High Bank above every random spot; it scored subtle Fudge (plowed bands, ~0.3-0.5 m),
urban Marietta and forested Fort Hill low (Fort Hill near the bottom). Qwen called Fort Hill and two random hilltops
certain, everything else near zero.

Caveats: 18 images; positives are whole-site renders with each site's own contrast setting, negatives use the default
stretch, so a style difference could leak the label for both models. The real test uses the Finder's test set
(known earthworks vs random ground, one renderer, held-out areas) and adds an embeddings + small trained head arm.

Run: `ssh -N -L 18083:127.0.0.1:8083 aibox`, then `pipeline/clef.py` (`decide`, `decide_batch`). Server:
`server/aibox/clef_server.py` in `/opt/llm/clef` on the AI box (llama-5060ti stopped while it runs).

## One view vs four views, 2026-10-10 (same 18 places, still too small)

Re-rendered from the DEM at native 1 m/px, 600 m crops centred on each place, every view with a fixed stretch
(`pipeline/viz.py`), so known sites and random ground are drawn identically.

| Clef-flash input | AUC | Time for 18 |
|---|---|---|
| One image: local relief at 15 m radius | 0.82 | 6 s |
| Four images: relief at 5 / 15 / 40 m + sky-view factor | 0.75 | 20 s |

- With the contrast difference removed, Clef still separates (0.82 vs 0.86 before): the first result was not just
  the rendering leaking the label.
- Four views did not help here. The difference (0.07) is about five swapped pairs out of 72: noise at this size.
  Four views made the top two positives more confident (0.95, 0.77) and cost 3.3x the time.
- The 5 m relief view shows Hopeton's plowed circles and square far more crisply than the 24 m view the site pages
  use (checked by eye); worth testing as the single view too.
