Status: open
Depends on: none
Touches: pipeline/plan_fit.py, tests/test_fit_provenance.py

# 219: The page's source line states the book's year once (the commons case)

## Goal
303's live shotwick run (docs/site_flow.md, 2026-10-11) exposed a blemish in `plan_fit.build`'s
commons source line:

    Shotwick Castle, plan from Mackenzie, The Castles of England (1897) (1897), Wikimedia
    Commons: by The British Library; No restrictions; ...

The picture's title already states the book's year, and the document's label (`"1897"`) repeats
it. A source line should state each fact once: when the label's year is already in the title,
drop the label's parenthesis; only a title without a year shows the label (or "undated"). The
book branch (`{book}: {title or label}`) and the who-placed clause (303) are not touched.

## Acceptance criteria
- [ ] `plan_fit.build`'s commons branch prints `TITLE (LABEL), Wikimedia Commons: CITE.` with the
      `(LABEL)` parenthesis dropped when the title already contains that year, and "undated" only
      when the title carries no year at all; the book branch and the how-clause are byte-identical
      for every existing document (a test proves it for a book doc and for a yearless commons
      title).
- [ ] The built commons depictions in the repo carry the fixed line - at minimum shotwick's
      `web/data/sites/shotwick-castle-q7502621/depictions.json` (gitignored; its overlay is
      current, so a one-off re-bake of the entry's `source` field is the smallest honest
      re-bake: same corners, same fit record, only the string changes) - and a hermetic test
      pins the new string for the shotwick document end to end.
- [ ] The full suite is green (the 303 tests' pinned strings stay intact: none of them pin the
      commons how-clause with a doubled year).

## Notes
- Filed by 303 (agent a), whose live run produced the string; not fixed there (a string-format
  change in `plan_fit.build` is outside 303's provenance scope).
- Depends on 302c only because both touch `pipeline/plan_fit.py` (keep the edits disjoint; 302c
  is the 302 decision/wiring task).

## Hand-over

(2026-10-12, iteration 132, agent c - FIRST session on 219. Investigation + code done; tests not yet written. 302c no longer blocks: the lead dropped 302c/302d in main d39ead8 ("219 no longer waits on 302c"; on main the task says `Depends on: none` - my branch's copy still says 302c, the driver's main-merge rewrites it next session: don't touch that line).)

**Done this session (committed 4b93f5c):** refactored `pipeline/plan_fit.py`: the source-line assembly (citation + who/how clause) extracted from `build()` into pure `source_line(doc, n, m, who)` and the 4-digit-year regex into `_year4(text)` (used by both the sort-year logic and the source line). Proven byte-identical: a throwaway script compared old inline expressions vs new function for ALL 133 store docs in data/db/platefits - 0 mismatches (m computed from `similarity(doc['pairs'])` unscaled: least-squares similarity is scale-equivariant, so m is independent of the picture's fs - verified). No test file touched yet.

**UNCOMMITTED in the working tree (harness-saved; verify it is still there first next session, `git diff pipeline/plan_fit.py`):** the year-once behavior change in `source_line`'s commons branch: `elif _year4(doc.get("title") or "") is None: src = f"{title} ({label or 'undated'}), Wikimedia Commons: {cite}."  else: src = f"{title}, Wikimedia Commons: {cite}."` plus an updated docstring (states each fact once; 303's shotwick read "(1897) (1897)"). Smoke-tested in-process: year-in-title drops the parenthesis; yearless title shows label; yearless+no-label shows "(undated)". The book branch and all how-clauses are untouched (the refactor commit already proved that).

**Next step (exact):** add section `# e. the source line states the book's year once (task 219)` at the end of `tests/test_fit_provenance.py` (import `socket`; add a `no_net` fixture monkeypatching `socket.socket.connect` and `socket.create_connection` to raise; helpers): `_standin(doc)` -> PIL `Image.new("RGB", tuple(doc.get("size") or (64,48)))` saved as JPEG bytes (doc's own frame size => fs=1, exact fit math, no download); `_source_tree(tmp, doc)` -> temp tree with `web/data/sites/<sid>/` created, standin at `data/raw/commons/big/<plan>.jpg` (commons) or `data/raw/books/<ia>/full/<file>` (book), and a COPY of the real `web/data/sites.json` (build's final `build_site.set_drawings` reads it; `overlays/drawings` tolerate a bare site dir); `_build_source(tmp, doc_id)` -> load doc from `ROOT/data/db/platefits/<doc_id>`, `plan_fit.build(doc, root=str(tree))` (plan_fit = the module-level `SITE_DONE.plan_fit` already in the file), return the entry's `source` from the built depictions.json (find it by `file == "plan_" + doc["plan"] + ".webp"`). Three tests, each taking `no_net`, asserting the EXACT pinned strings (recompute with a throwaway script if in doubt - values below): (1) BOOK byte-identical: doc `arbor-low-q630312.earthworkenglan01allcgoog_n0597_1.json` (by:hand, m=6) -> `A. Hadrian Allcroft, Earthwork of England: Prehistoric, Roman, Saxon, Danish, Norman and Mediaeval, London 1908. Fig. 194. Scan: Internet Archive earthworkenglan01allcgoog leaf 597. Placed by hand on 4 matching points; one rotation and scale fits them within 6 m.` (2) COMMONS yearless byte-identical: `bergues-q244934.c_4bbca705be732b1c.json` (by:hand, m=33) -> `Bergues, town plan by Jacob van Deventer (1545), Wikimedia Commons: by Jacob van Deventer; Public domain; https://commons.wikimedia.org/wiki/File:Bergues_-_Deventer.jpg. Placed by hand on 4 matching points; one rotation and scale fits them within 33 m.` AND `bethlehem-q2523914.c_075db5049e2fb635.json` (auto batch, label None, m=24) -> `Survey of Palestine, Bethlehem 01-beit-jala (FL10423295 2369494) (undated), Wikimedia Commons: by Survey of Palestine; Public domain; https://commons.wikimedia.org/wiki/File:Survey_of_Palestine,_Bethlehem_01-beit-jala_(FL10423295_2369494).jpg. Fitted automatically by the batch on 4 matching points; one rotation and scale fits them within 24 m (gate score 17.2 m)` (3) THE FIX: `shotwick-castle-q7502621.c_e6e5490609414bb9.json` (by:agent, m=20, matches agent a's built entry's resid 14.2/2.0/17.5/19.4) -> `Shotwick Castle, plan from Mackenzie, The Castles of England (1897), Wikimedia Commons: by The British Library; No restrictions; https://commons.wikimedia.org/wiki/File:212_of_%27The_Castles_of_England-_their_story_and_structure_..._With_..._illustrations_and_..._plans%27_(11296081346).jpg. Fitted automatically on 4 matching points; one rotation and scale fits them within 20 m.`

Then: commit behavior+tests together (`219: ...`), run the FULL suite (`.venv/bin/python -m pytest tests/ -q`, ~3 min). Baseline when this session started: driver's newest PROGRESS note says 1 pre-existing failure at loop start - `tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees` (owned by 218). MY first baseline run is UNRELIABLE (it overlapped my edit; its one failure `test_site_done.py::test_site_done_line` was a mid-edit SyntaxError in the copied tree - do not treat it as pre-existing). Expect: everything green except possibly that one test_gate failure; if `test_site_done` or `test_fit_provenance` fails, that is my regression. No test in the suite pins a commons source line with a doubled year (grepped: only tests/golden/src_mackenzie_sample.json's `book` field mentions "Wikimedia Commons"), so criterion 3 holds once the suite is green.

**Then the rebake step (acceptance box 2; working phase, NOT in tests):** in THIS checkout the shotwick site is not built (no web/data/sites/shotwick-castle-q7502621/). Build it: the big picture is already cached at `data/raw/commons/big/c_e6e5490609414bb9.jpg` (no download); create the site dir and run `plan_fit.build(doc)` directly - DO NOT run tools/site_done.py (it would write the Allcroft review item - outside this task; 306/307 own review). Verify the built entry's `corners`/`fit` match agent a's existing entry BYTE-FOR-BYTE (read-only: /home/agent/projects/ancient-works.a/web/data/sites/shotwick-castle-q7502621/depictions.json - its plan entry has corners [[-2.9770935,53.2284079],[-2.9742112,53.2284018],[-2.9742213,53.2266743],[-2.9771036,53.2266804]], resid_m [14.2,2.0,17.5,19.4], m_per_px 0.2289, rot -0.2) with only `source` changed. Also re-bake the OTHER built commons depictions in this checkout whose title carries a year (from a scan of web/data/sites/*/depictions.json): aldenhaag, avaricum, barnard, bethlehem (Nativity 1615, Maastrecht 1748 x3, "(1881) PLAN"), bolsover, castle-rising, cahokia, mayburgh, mound-bottom, whitley - each by `plan_fit.build(doc)` (their docs are in data/db/platefits, keyed by each entry's `fit.doc`; big images: 41 cached in data/raw/commons/big/, missing ones pace-download like load_picture does). Caveat: some of those titles only LOOK doubled to a naive regex (berkhamsted's title ends in a file id "(11296081346)", bethlehem FL sheets have no 4-digit year at all - _year4 correctly leaves them showing their label/undated parenthesis; only re-bake entries whose title actually matches _year4). Agent a's checkout and the lead's checkout may keep stale strings in their own gitignored web/data - do NOT touch other checkouts; record in the final hand-over that a one-off `plan_fit.build` per stale entry rebakes them.

**Key facts verified this session:** shotwick doc: src commons, title `Shotwick Castle, plan from Mackenzie, The Castles of England (1897)`, label `1897`, cite `by The British Library; No restrictions; https://...jpg`, by:agent, auto/score None, model similarity, 4 pairs, size [839,840], crop [0,0,839,840]; store totals: 107 commons (48 with a 4-digit year in the title) + 26 book docs. Docs where title-year != label-year (3: argentoratum 1831/1836, bethlehem 1881/1882, mound-bottom 1923/1924): the rule DROPS the label parenthesis (title has a year); the label remains in the entry's `scale` field - decision recorded in DECISIONS.md. `build_site.set_drawings` only needs `web/data/sites.json` to exist; `overlays/drawings` tolerate a bare site dir. 303's site_flow.md section (line ~252) quotes the doubled string - it is a historical record, NOT changed by this task.

**Re-read:** pipeline/plan_fit.py:source_line - confirm the uncommitted working-tree change survived the harness save (docstring + elif _year4 branch); tests/test_fit_provenance.py - section e helpers must not import PIL at module top (the file is stdlib-only; import inside _standin).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/302c-decision-wiring.md` (open) - hand-over: (2026-10-12, iteration 84, agent c - FIRST session on 302c. Investigation + design only: NO code
- `tasks/304-survey-fit.md` (in-progress) - hand-over: (2026-10-12, iteration 91, agent c - session 7. The lead directed: freeze the stub as it is
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/219-source-line-year.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

(no entries yet)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

## 219 (iteration 132, agent c) - context-limit note, 2026-10-12
Source-line year-once fix: investigation done; `source_line`/`_year4` refactor COMMITTED (4b93f5c,
byte-identical for all 133 store docs); the behavior change is UNCOMMITTED in the working tree of
pipeline/plan_fit.py (harness-saved). NEXT: write tests (design + exact pinned strings are in the
task's hand-over), commit, run the full suite (expect only the pre-existing test_gate failure),
then the one-off re-bake of built commons depictions (shotwick first). Details in
tasks/219-source-line-year.md ## Hand-over and DECISIONS.md (three 219 entries, 2026-10-12).
