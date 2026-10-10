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
