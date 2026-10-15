Status: in-progress
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
- [x] --check in fit/src_roman_horsley.py, run offline (the socket-block wrapper), passes on
      the staged set: the join holds (every one of this book's 17 staged rows names an
      existing catalog site or a staged extras_roman.jsonl site; every NEW extra site row
      this book created has at least one staged plan row) and fit/evidence.py's check passes
      on all 17 of this book's rows (the 200 evidence field verified offline from the stored
      fields - check_caption / check_book / check_book_caption, per fit/evidence.py).
- [x] --golden writes tests/golden/src_roman_horsley_sample.json: a stable, deterministic
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

(Unblocked 2026-10-14, iteration 137, agent c, from the parent 207: same owner lift as
807/808 - DECISIONS 2026-10-14 207. Runs last of the chain.)

## Hand-over

(2026-10-15, iteration 197, agent c) **Boxes 1-2 done and committed (box 1 was committed by the driver as cf6f996b after 196; box 2 = this session's commit).** Re-verified `--check` on the current post-230-merge main first: exit 0, zero join: lines, `evidence: 17 rows, 17 pass, 0 fail, 0 no-tie` - 230's scoped merge (481fe446) has landed on main (all 9 staged roman sites in the canonical files, the (e) check live and passing; the 207b luguvallium red that was the sole suite red at 814-193/194 is RESOLVED on the current tree). Built and committed the `--golden` leg: `GOLDEN` + `GOLDEN_LEAVES = (114, 185, 236, 278)` (one golden file row per tie flavour: new no-QID "roman site" / new "roman fort" principal / existing catalog QID site / reused canonical extras site), `_norm` (verbatim 207b) and `golden()` (files = the 4 leaves in leaf order; extras = this book's extras_roman rows the subset names - ardoch, virosidum in file order; classified = the subset's (site,title) keys; count = the WHOLE book 8/17/17; dates zeroed, keys sorted, indent=1, trailing "\n"). Golden file `tests/golden/src_roman_horsley_sample.json` committed (sha256 af87ec842e480564421f67296881a8709e8242254642f7f8cb681e4192b48886; deterministic across runs; rows verified equal to the staged rows re-derived with the module's own `_norm`).

**Next session - step 3 (box 3): write tests/test_src_roman_horsley.py.** The 196 step-3 spec still stands (re-verified against the module this session): importlib-by-path (spec_from_file_location on fit/src_roman_horsley.py); the autouse no_network fixture imports `urllib.request, ssl` FIRST, then monkeypatches `socket.socket.connect` + `socket.create_connection` + `socket.getaddrinfo` (the box's pattern - NOT 207b's socket-replacement pattern, which breaks a later ssl import, PITFALLS line 479); the test file inserts fit/ AND pipeline/ into sys.path BEFORE the exec_module (that is what makes the module's lazy `import evidence` resolve); the LLM never runs in the test. Five cases:

1. `test_register`: `h.register()` in-process; assert `books.BOOKS[h.KEY]` carries (ia, region, year, cite, why) and `books_lists.HAND_FIGS[h.IA] == h.HORSEY_FIGS` (24 lines, 17 kind-s). Import books/books_lists inside the test (fit/ + pipeline/ on sys.path by then).
2. `test_check_offline(capsys)`: `code = h.check_staged()`; assert `code == 0`, no "join:" line in out, `"evidence: 17 rows, 17 pass, 0 fail, 0 no-tie" in out`, plus three spot PASS lines with the exact f-string `f"{'PASS':4s} {'caption_coords':15s} {site}|{title}"` (TWO spaces between the kind and the key, the format of evidence._line):
   - `ardoch|Innerpeffery camp. and Ardoch camp.`
   - `virosidum|The five fecondary ftations per lineam valli`
   - `castrum-segedunum-q637958|A general map of the Roman walls in the north of England, and so much of the adjacent countryes as includes the secondary stations per lineam valli.`
3. `test_join_problems`: `h.join_problems() == []` plus explicit per-row facts (17 this-book file rows; 18 classified rows 1:1 with the 18 (site,title) keys; all 9 staged sites have >=1 picture; every file row's site in {sites.jsonl} ∪ {extras.jsonl} ∪ {extras_roman.jsonl} ids) - a guard against a vacuously-passing join.
4. `test_check_negative_controls(tmp_path, monkeypatch)`: monkeypatch h.FILES_ROMAN/CLASSIFIED_ROMAN/EXTRAS_ROMAN/SITES_JSONL/EXTRAS_CANON at tmp copies (tmp_path = the temp dir, allowed); corrupt COPIES and assert the EXACT lines (strings verified 196): cilurni `dist_m 48000` -> `FAIL caption_coords  cilurni|A map of the Roman wall, from HANNAVVM to CILVRNVA.  stored distance 48000 m does not reproduce (0 m)`; title/desc stripped of the named place -> `the caption does not name '...'`; one file row's site set to a nonexistent id -> `join: file row names a site that is neither staged nor existing: ...`; PLUS the 207b-style three-state monkeypatch of the canonical files (pre-merge / merged-identical / same-id-different-row -> `staged site X differs from its canonical row in extras.jsonl`) - the most valuable (e)/(f) coverage, include it. CASCADE: corrupting the ONLY row of a single-picture site fires THREE join problems (unknown site + that site's no-picture + classified-not-1:1) - assert the full fired list; for a 2-problem unknown-site case use the two-picture site (n236 -> castrum-segedunum-q637958, which also holds n238). sha256 the REAL staging files before/after (must be unchanged).
5. `test_golden_matches_staged`: read the golden file; recompute the dict with the module's own rules (`h._norm`, `h.GOLDEN_LEAVES`, the same count/extras/classified selection as `golden()`); assert full dict equality, files order == leaf order [114, 185, 236, 278], count == {files: 17, classified: 17, extras: 8}.

Run the new file alone first: `.venv/bin/python -m pytest tests/test_src_roman_horsley.py -q -p no:cacheprovider` (expect 5 passed, ~seconds, no network - the fixture raises on any socket connect). Commit it.

**Then step 4 (box 4): the full suite** `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider`. FIRST re-measure the baseline with NO 809 changes (expect 0 reds now that the roman red is resolved; agent a's in-flight 307d/242 work is the only expected red source). "No new reds" = nothing red that (a) fails before the 809 edits and (b) is not in that measured baseline (the 241-187/306d-161 precedent and the driver's own done-claim standard). COMMIT EVERYTHING before starting the run (PITFALLS: mid-suite working-tree edits fail the integrity snapshot tests); the owner-check tests re-encode docs/site_flow/307d_*.png during a run - if the run dirties them, restore main's bytes in the commit (the 808 done-commit precedent; 816 owns the permanent fix). After a green run: tick boxes 3+4, `Status: done`, final commit with this hand-over.

**Do NOT touch:** fit/evidence.py, fit/merge.py, the canonical data files (230 is agent a's), the 207b module/test/golden, docs/lead_roman.md, tests/test_gate.py, agent a's stores (web/data/*, data/merge/, data/db/platefits, docs/site_flow/).
