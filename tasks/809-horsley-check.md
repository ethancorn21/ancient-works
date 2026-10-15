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

(Unblocked 2026-10-14, iteration 137, agent c, from the parent 207: same owner lift as
807/808 - DECISIONS 2026-10-14 207. Runs last of the chain.)

## Hand-over

(2026-10-15, iteration 196, agent c) **PREP-STEP 1 DONE AND COMMITTED-ish (module edit in the working
**
tree, NOT yet committed - the context-limit harness saves it; next session: `git add fit/src_roman_horsley.py`**
**and include it in the next commit):** the `--check` leg is built in fit/src_roman_horsley.py
**
(`_canon_norm` + `join_problems()` + `check_staged()` + the `__main__` dispatch; the "Later legs"**
**docstring rewritten to "All legs built... --check (809: check_staged below) and --golden (809, the next step)";**
**`--golden` still exits with "the golden leg is not built yet (809; see the module docstring)").**

**Verified this session (all under .venv/bin/python, project root):**
- `--check` under the socket-block wrapper: exit 0, no "join:" lines, `evidence: 17 rows, 17 pass, 0 fail, 0 no-tie`.
- The whole staged roman set join is clean on current main (18 file rows, 18 classified, 9 staged sites; 0 problems).
- 6 join negative controls on temp copies (data/books/.809nc-tmp, removed) all fire as designed, incl. the 230-merge guard: tampering a staged site row's name -> `staged site ardoch differs from its canonical row in extras.jsonl` (ALONE).
- 3 evidence negative controls: cilurni `dist_m 48000` -> `FAIL caption_coords  cilurni|A map of the Roman wall, from HANNAVVM to CILVRNVA.  stored distance 48000 m does not reproduce (0 m)`; title/desc stripped of the named place -> `the caption does not name 'A map of the Roman wall, from HANNAVVM to CILVRNVA.'`; clean -> exit 0. (Both FAIL lines end with the 2-space + reason format of evidence._line.)
- `--dry` staging still idempotent (0 appended); the three staging files are byte-identical to HEAD.

**PREP ASSUMPTIONS THAT WERE WRONG (all re-checked on main this session - see DECISIONS 196 for detail):**
1. Prep §0's `grep -c britanniaromanao00hors data/books/index.jsonl # 0` -> it is **38** now (211 box-2's book-index rebuild, main commit 214c6425, landed between 155 and 196). Those are book-mechanism leaf rows, never written by 207a/808. **No design impact** (check_staged passes NO_BOOKS -> the books file is skipped; the applicable route stays check_commons -> check_caption), but do NOT repeat the "0 rows" claim anywhere.
2. Prep §1's "luguvallium's Q71551754 is held by NO canonical row" -> **all 9 staged roman sites (incl. luguvallium-q71551754) are already folded into the canonical data/catalog/extras.jsonl on main** (211's original consolidation ran; 230 is agent a's re-run, still in flight). Consequences: join check (e) is LIVE and passes for all 9 staged sites (byte-identical under _canon_norm - verified); (f) cannot fire alone for a mutated staged site (e subsumes it - verified); the 230-ordering worry (prep risk 4) is moot in the sense that both merge states pass the join (the 155 simulation still holds, plus the now-real merged state passes too).
3. Prep §3's wrapper as written (`runpy.run_path('fit/src_roman_horsley.py')` relative path) **fails with ModuleNotFoundError: No module named 'evidence'** - CPython 3.12.3 runpy.run_path adds the script's dir to sys.path only for an ABSOLUTE path (probed: absolute -> sys.path[0]=the dir, sibling import OK; relative 'fit/...' -> not added). Fix used this session (works): `sys.path.insert(0, os.path.join(os.getcwd(), 'fit'))` BEFORE runpy inside the wrapper. The step-3 test sidesteps this entirely (it imports by path AND adds fit/ + pipeline/ to sys.path in the test itself, per prep §2 step 3).
4. Minor: the 207b staged site id is `luguvallium-q71551754` (prep wrote "luguvallium" shorthand); its files row title is 'FIG. 4. CARLISLE, COURSE OF THE WALL AND OF THE YALLUM.' (it is row 0 of files_roman.jsonl).

**EXACT NEXT STEPS (in order; each = one session's step, per the prep's numbered plan):**
1. **Commit the pending module change first** (it is in the working tree, uncommitted): `git add fit/src_roman_horsley.py && git commit -m "809: the --check leg - the whole-staged-roman-set join (a)-(f) + fit/evidence.py over this book's 17 rows, offline"`. Tick box 1 of the task file in the same commit (verified above; the box's check_book/check_book_caption parenthetical does not apply - see the DECISIONS entry and the 207b precedent; the module docstring says so).
2. **Step 2 (box 2): the --golden leg.** Add `GOLDEN = os.path.join(ROOT, "tests", "golden", "src_roman_horsley_sample.json")` next to NO_BOOKS; add `_norm(rows)` and `golden(path=None)` copied verbatim from fit/src_roman_maclauchlan.py (~lines 413-445: _norm zeroes evidence.checked + location_check.checked to "0000-00-00"; golden writes {"count": {...}, "extras": ..., "files": ..., "classified": ...} via json.dump indent=1, sort_keys, ensure_ascii=False + "\n") - with the HORSLEY twist from prep step 2: `files` = the GOLDEN_LEAVES subset only, `GOLDEN_LEAVES = (114, 185, 236, 278)` (one per tie flavour: ardoch new "roman site" / virosidum new "roman fort" principal / castrum-segedunum-q637958 existing catalog QID / bar-hill-fort reused canonical extras) parsed from each row's url `n%04d`; the count block = the WHOLE book's counts ({"extras": 8 (this book's own extras_roman rows), "files": 17, "classified": 17}); extras/sites subset = this book's 8 new sites (bar-hill/rough-castle are canonical, not in extras_roman) but the count.extras = 8; classified subset by (site,title) keys of the 4 golden rows. In `__main__` replace the --golden stub with `raise SystemExit(golden())` and drop the now-dead stub message; finish the docstring's "--golden (809, the next step)" to "--golden (809: tests/golden/src_roman_horsley_sample.json)". Run `.venv/bin/python fit/src_roman_horsley.py --golden`, eyeball the generated file (4 file rows in leaf order, 2 site rows (ardoch, virosidum - file order in extras_roman), 4 classified rows), commit module + golden file together.
3. **Step 3 (box 3): tests/test_src_roman_horsley.py** per prep §2 step 3 (importlib-by-path; the autouse no_network fixture patches socket.socket.connect + socket.create_connection + socket.getaddrinfo AFTER importing urllib.request, ssl; add fit/ AND pipeline/ to sys.path in the test file top BEFORE the importlib exec - that is what makes the module's lazy `import evidence` resolve; the LLM never runs). Cases: (1) test_register; (2) test_check_offline: code == 0, no "join:", `evidence: 17 rows, 17 pass, 0 fail, 0 no-tie`, plus spot PASS lines asserted with the exact f-string `f"{'PASS':4s} {'caption_coords':15s} {site}|{title}"` (two spaces between kind and key) - verified strings for ardoch/virosidum/castrum in the prep; (3) test_join_problems: `h.join_problems() == []` + explicit per-row facts (17 this-book rows, 18 classified 1:1, all 9 staged sites have >=1 picture, every file row's site in {sites.jsonl}∪{extras.jsonl}∪{extras_roman} ids); (4) test_check_negative_controls: monkeypatch h.FILES_ROMAN/CLASSIFIED_ROMAN/EXTRAS_ROMAN/SITES_JSONL/EXTRAS_CANON at tmp copies of the real files (data/books/.809*-style temp INSIDE the project, e.g. under data/books/, or pytest tmp_path - the latter is fine, it is the temp dir), corrupt copies, assert the EXACT problem/FAIL lines (the strings verified above; remember the single-picture-site cascade fires 3 join problems - assert the full list), and sha256 the real staging files before/after; (5) test_golden_matches_staged: full dict equality recomputed with h._norm + GOLDEN_LEAVES. The prep's 207b-style three-state monkeypatch of the canonical files (pre-merge / merged-identical / same-id-different-row) is the most valuable (f)/(e) coverage - include it per prep risk 4 (now doubly relevant: the real merged state exists on main).
4. **Step 4 (box 4): full suite** `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider`. FIRST re-measure the baseline on main with NO 809 changes (the box's "1 failed / 156 passed / 1 skipped" is the stale 221 number; expect 1-2 reds from agent a's in-flight roman/307d work - at this entry's writing the DECISIONS tail records `tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes` RED on main ("staged site luguvallium-q71551754 differs from its canonical row in extras.jsonl") after 211/230 in-flight churn; NOTE: at 196-session time my direct join run on the merged main found that (e) check PASSING again - the canonical row had been re-synced since - so re-verify which roman reds are actually red at your measurement, and base "no new reds" on the measured baseline per the 241-187/306d-161 precedent and the PITFALLS "driver's done-claim baseline is its own newest loop-start suite note" entry - a pre-existing main red that my module cannot affect (my file is imported by no other test) is outside the lane and gets a DECISIONS note, not a test fix). "No new reds" = nothing red that (a) fails before the 809 edits and (b) is not in that measured baseline. **Commit everything BEFORE starting the run** (PITFALLS: mid-suite working-tree edits fail the integrity snapshot tests; the owner-check tests re-encode docs/site_flow/307d_*.png during a run - if the run re-encodes them, restore main's bytes in your commit exactly as the 808 done commit did; this session restored 4 such dirty PNGs (B_1/B_2/B_3/B_5) to HEAD at session start with `git checkout HEAD --`).

**Do NOT touch:** fit/evidence.py, fit/merge.py, the canonical data files (230 is agent a's), the 207b module/test/golden, docs/lead_roman.md, tests/test_gate.py, agent a's stores (web/data/*, data/merge/, data/db/platefits, docs/site_flow/). 816 (created 195) owns the 307d PNG re-encode fix - if the suite churns them again, restore-and-continue, don't fix.

**Status:** box 1 verified (tick in the next commit); boxes 2-4 open. Task file status -> in-progress.
