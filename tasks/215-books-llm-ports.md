Status: done
# 215: Book machinery - the LLM tunnels moved (18080/18081 dead, the replicas serve on 8080-8082)
Depends on: none
Touches: pipeline/books.py

## Goal
`pipeline/books.py`'s `LLM_URLS` (127.0.0.1:18080/18081) no longer match this machine. The llmtunnel
ssh forwarder (running since Oct 6, user `llmtunn`) serves the Qwen replicas on 127.0.0.1:**8080,
8081, 8082** - `/v1/models` returns 200 on all three; there is no listener on 18080/18081 at all
(checked with `ss -ltnp` + curl, 2026-10-11). So `run_stage()` exits with "LLM tunnels down" and every
book task's triage B/F stages are blocked (207, 208, 209 and 213 all hit it; 213 works around it with a
throwaway in-process port patch). Point the machinery at the live ports and prove a stage call reaches
the model.

## Acceptance criteria
- [ ] `books.py`'s URL list names the ports that are live on this machine (all three replicas, not just
      two - more parallelism), or discovers them; `run_stage` no longer exits on the tunnel check.
- [ ] A smoke run: one page through `run_stage` for any book with triage images cached succeeds
      (a new `.F` or `.B` row appears) - run it on a page of a book already in BOOKS.
- [ ] A `PITFALLS.md` entry records the machine's LLM ports (llmtunnel user, 8080-8082) so the next
      port move is found in seconds, not hours.
