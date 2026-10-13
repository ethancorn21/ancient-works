Status: blocked
Depends on: 808
Touches: fit/src_roman_horsley.py, tests/test_src_roman_horsley.py, tests/golden/src_roman_horsley_sample.json, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl

# 809: Horsley - the offline --check, the golden sample, the no-network test

## Goal
Close the Horsley book: build the module's --check leg (offline: the join over the staged
roman rows - every staged row names an existing or staged site, every new extra site has its
plans - and fit/evidence.py's check over this book's staged rows, from stored fields alone,
no network even for the new extra sites), --golden (tests/golden/src_roman_horsley_sample.
json), and tests/test_src_roman_horsley.py (no network: the no_network socket-blocking
fixture as in tests/test_src_van_deventer.py; the module imported by path via importlib and
register() in-process; the LLM never runs in tests). This makes 207a's moved boxes 4-5
stand on a hermetic, re-runnable check.

## Acceptance criteria
- [ ] --check in fit/src_roman_horsley.py, run offline (the socket-block wrapper), passes on
      the staged set: the join holds (every one of this book's 17 staged rows names an
      existing catalog site or a staged extras_roman.jsonl site; every NEW extra site row
      this book created has at least one staged plan row) and fit/evidence.py's check passes
      on all 17 of this book's rows (the 200 evidence field verified offline from the stored
      fields - check_caption / check_book / check_book_caption, per fit/evidence.py).
- [ ] --golden writes tests/golden/src_roman_horsley_sample.json: a stable, deterministic
      subset of this book's staged rows (fixed ordering; regenerated only for an intended
      change).
- [ ] tests/test_src_roman_horsley.py passes with NO network (the no_network fixture: import
      urllib.request/ssl FIRST, then patch socket.socket.connect + socket.create_connection
      to raise - a naive `socket.socket = fn` breaks the ssl import, PITFALLS): it imports
      fit/src_roman_horsley.py by path via importlib, calls register() in-process, and
      asserts the join, the evidence check over the book's rows, and that the golden sample
      matches the current staged files; the LLM never runs in the test.
- [ ] Full suite (.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py
      -p no:cacheprovider): no new reds against the split baseline (1 failed / 156 passed /
      1 skipped; the lone red = agent a's 307d placement test, known pre-existing).

## Notes (operational facts carried from the 207a split, 2026-10-14 iteration 221)

**The --check design (219 step 4):** offline join + fit/evidence.py over the book's rows.
Read fit/evidence.py in full first (it was only skimmed at 220): check_caption (~line 190),
check_book (~265), check_book_caption (~290) - book rows re-derive books_match's one-pair
rule from the row's printed text + the current catalog row at the stored score; only the
runner-up margin stays stored. The join over the roman staging files follows the parent's
mechanics (every row tagged with its book; rows from 207a/207b coexist in the same files -
809 checks the whole staged roman set for the join, but the evidence check and the golden
sample cover this book's rows only).

**Row fixes:** the three staging files are in this task's Touches for ROW FIXES ONLY (a row
808 staged that fails --check gets corrected in place - e.g. distance/named-place fields -
and the fix is recorded in a DECISIONS entry); new rows or drops belong to 808. If a staged
row cannot pass the evidence contract, say so in a DECISIONS entry and propose the fix
here rather than weakening the check.

**The socket-block wrapper (for --check and the test's fixture), as used by 807:**

    import urllib.request, ssl, socket   # FIRST - the ssl import must precede the patch
    def dead(*a, **k): raise RuntimeError("network blocked in this run")
    socket.socket.connect = dead; socket.create_connection = dead

**The validate_book one-liner** (807's Notes) is the same pattern if the test wants the
recall figures; books_lists.validate_book is offline (cached bookreader.json + the A file +
ink() over local triage images).

**Staged state at the split of the parts:** 808 lands first (17 files_roman rows + 17
classified rows + the new extras_roman site rows); the module already documents --check /
--golden in its docstring ("Later legs") - implement per that.

**Suite baseline at the split:** 1 failed / 156 passed / 1 skipped (389 s; the lone red =
agent a's 307d placement test: seed check + /tiles/relief 404, PITFALLS). No test imports
this module yet; re-baseline on the final run.
