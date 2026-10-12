Status: open
# 307b: The queue pairs a drawing with the right place, not a namesake
Depends on: 305
Carved from: 307
Touches: tools/fit_queue.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
307's first box, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [ ] Every queue entry's candidate is checked to show the same place as its site, not just the same name: the
      caption/place words, county and region in the picture's metadata against the site's place, region and
      coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review queue with the reason
      "same name, other place: <caption place> vs <site place>"; where the right site exists in the catalog, the
      candidate is moved to it instead.
- [ ] docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke Camp near Brighton is
      not paired with the Cambridgeshire dyke.
- [ ] tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit there).

## Hand-over

(2026-10-12, iteration 92, agent c - FIRST session on 309. INVESTIGATION ONLY, no code written, no files changed, nothing committed beyond this note. Full suite state at loop start: 4 pre-existing failures per the driver notes in PROGRESS.md (test_gate, test_batch_eu x2, test_serve::test_platefits_docs_match_sites) - none mine. Everything below is read-data, verified by running scripts in .venv/bin/python (system python3 has no PIL; anything importing pipeline/ needs the venv).)

**The facts (all verified this session):**
- Current queue: web/data/fit_queue.json has 117 entries. Entry 1: devil-s-dyke-q3307343 ("Devil's Dyke", place "Stetchworth, Cambridgeshire, England", catalog admin {parish Stetchworth, district East Cambridgeshire, county Cambridgeshire}) with best row earthworkenglan01allcgoog_n0686_1 "The Devil's Dyke Camp, near Brighton" (Allcroft 1908 Fig. 217) - the Sussex hillfort picture. Also in devil-s-dyke's candidates: n0599_1 (CASTLE DYKE, AYSGARTH - Yorkshire) and n0662_1 (SWEALD - Sussex district map).
- THE RIGHT SITE EXISTS IN THE CATALOG: devil-s-dyke-hillfort-q17674160 (Q17674160 "Devil's Dyke hillfort", aliases "Devils Dyke, Poynings", "Devil's Dike Camp", "Poor Man's Walls", admin {Poynings, Mid Sussex, West Sussex}, -0.210486/50.8854). Whether it is BUILT (in web/data/sites.json + web/data/sites/<id>/ dir) was not checked - the move target's build status decides queue-entry vs review-item destination.
- Why the matcher (pipeline/books_match.py) got it wrong: exact name lookup - the title's phrase "Devil's Dyke Camp" -> name_keys strips generic "camp" -> key "devil dyke" == Q3307343's exact name -> is_exact=True, score 1.0 (runner_up 0.4, the hillfort: tokens devil/dyke hit but no exact key, and "wall" != "walls"). The row's place dict is {} (Brighton is a city, place_of() extracts only county/state words) -> no county contradiction check fires -> status matched -> evidence recorded (kind caption_coords, score 1.0, runner_up 0.4, why []) -> check re-verifies PASS. So the evidence contract is satisfied by a namesake: this check is new logic, not a re-run of the evidence check.
- **KEY DATA DISCOVERY: the book's own list of figures is organized by county.** data/books/lists/earthworkenglan01allcgoog.json: {plates: null, figures: [{fig, title, page, kind, page_ocr, kind_by}] x203}. In file order: fig 212 "Burpham Camp, Arundel, Sussex" (explicit uk_county=sussex), then figs 213-223 (Highdown/Worthing, Cissbury, Roman Ditches Worthing, Edburton near Brighton, **217 Devil's Dyke Camp near Brighton**, 218 Giants' Graves Brighton, Ditchling Beacon, Seaford, Hastings, Willingdon, Lewes) with NO county word, then fig 224 "Dolebury, Axbridge, Somerset" (somerset). => the section county of fig 217 = sussex = nearest preceding explicit county word. This is the offline resolution of "near Brighton" -> Sussex that catches the case, and it is the picture's own metadata (the book's list). My throwaway walk script returned somerset for 217 - BUG in the script (it keyed entries by fig AND plate and mis-ordered); the real walk (file order, match fig number, carry last explicit uk_county) gives sussex. RE-VERIFY this before trusting it. Other lists exist for every book: data/books/lists/<ia>.json ({plates, figures}; Squier books have plates, Allcroft has figures-only). For US books the list is NOT organized by county (by river/valley) - section inference is only valid when a county word actually appears in the list's titles; books with no county words in the list give no section (that's fine).
- Review-item candidates (data/review/*.json, 271 candidates across 342 items) carry a copied `evidence` field; 36 have `evidence.conflict` {route, named_place, place_qid, place_label, place_lon/lat, site_lon/lat}. The fit queue currently pulls ALL item candidates (fit/review.py _item_candidates equivalent in tools/fit_queue.py) so conflicted candidates sit in queue entries (e.g. bethlehem-q2523914 [Netherlands, Het Hogeland] has ~17 Holy-Land Bethlehem candidates at 3319km - TRUE namesakes; alauna has "Alauna - theatre" -> Ardoch Roman Fort 174km - true; cenabum has New Orleans maps 7725km - true). BUT conflicts are noisy: stonehenge "Larned" (an author's name) 7252km and "Our" 705km; fletio "Wit" (cartographer) -> Isle of Wight; glevum "Bristol" -> a Bristol 5282km away (US); durocortorum "Reims -> Reims 59km" (just over the 50km tolerance, probably a relevant Reims map); argentoratum "Rhin"/"Ville"/"Ecole" fragments. So H3 (conflict >50km) must be applied with a plausibility filter on named_place (not a fragment/author name; place_qid+label sane) or scoped carefully - eyeball the full flag list before finalizing (my throwaway analysis flagged ~25 entries / ~45 candidates total; the full list is reproducible with the script logic in the next step, or re-derive per the rules below).
- County-word flags found (picture's printed county/state vs site's known county): ARDOCH, PERTHSHIRE (n0354_1) vs coria-q3819299 (Northumberland) AND vs vindomora-q7932358 (catalog: this Vindomora IS Ebchester Roman Fort, County Durham - so the Perthshire Ardoch picture really is another place for BOTH; the catalog has NO ardoch entry, so no move target) - true namesakes. "British Village on Hampton Down, Bath" (n0285_1) vs eaton-socon (Cambridgeshire) - true. "Camp at Eamsheugh, St. Abb's Head" (n0076_1, Scotland) vs gurnard-s-head (Cornwall) - true. "Defences of York..." (n0438_1) vs alauna (Cumbria) - true. "CASTLE DYKE, AYSGARTH" (n0599_1) vs devil-s-dyke/bokerley-dyke - true. COMMONS candidates: "Alnmouth Tithe Map 1843" (northumberland) vs barnard-castle (County Durham) - true; "The South Staffordshire Coalfield" (staffordshire) vs dudley-castle (West Midlands) - borderline false positive (Dudley was historically Staffordshire until 1974); "Plan of Leeds Castle", "Fair Lawn in ye County of Kent", "Chevening by Kip", "Chiswick... Middlesex" vs sites whose catalog row has NO admin county (leeds-castle, fairlawne, chevening, chiswick-house) - these are CORRECT pairs and must NOT be flagged: rule must treat unknown site county as no-contradiction (my throwaway script had a bug flagging these - empty site-county set was treated as contradictory). DO NOT FLAG when the site's county is unknown.
- The "tied-away" trap: sites.json ids sometimes differ from the catalog's Q-ids for the SAME place: marietta (sites.json, no qid, -81.4535/39.4185) vs marietta-earthworks-q6763227 (-81.4519/39.42, ~150m), likewise forthill->fort-hill-state-memorial-q16210178, newark->newark-earthworks-q7016678. Their book evidence is tied to the Q-id site; a tied-away check must resolve aliases (specs/aliases.json - these three have NO alias entries, so the fallback is the distance: tied site's coords vs entry site's coords <= 50km => same place, not a mismatch). Without the distance guard all three Ohio sites (12 candidates) false-flag.
- tools/fit_queue.py is stdlib-only by contract ("the owner's Mac can run it with any python") and the synthetic test (tests/test_fit_queue.py::test_fit_queue_synthetic) builds a tree with ONLY the four inputs - no data/books/, data/catalog/, data/commons/, data/books/lists/. So the new check code (a) must degrade to no-op when the extra inputs are absent, and (b) must not import pipeline/books_match (it imports books -> PIL, absent on the owner's Mac; even the VM's system python3 lacks PIL - use .venv/bin/python for anything that imports pipeline/). Plan: put a stdlib COPY of the matcher core (norm, tokens, place_of + UK_COUNTIES/US_STATES/ABBR tables, phrases, name_keys, score_candidate, BOOK_SCOPE - ~120 lines from pipeline/books_match.py) in a new module tools/right_place.py (add "tools/right_place.py" to Touches first), imported by fit_queue.py; guard against drift with a venv-only test that runs the real books_match.match_row on real index rows and compares to the copy. The check module must also read data/catalog/sites.jsonl, data/books/index.jsonl, data/books/lists/<ia>.json, data/commons/files.jsonl, specs/aliases.json - all optional/missing-tolerant.
- Review-queue mechanics: fit/review.py upsert_item(root, site_id, entries, no_picture) + export(root, site_id) -> web/data/review.json (candidates copied VERBATIM into the page file). The page web/review.js renders candidate title/book/label but NOT why/note - so the reason string "same name, other place: <caption place> vs <site place>" will be stored on the item candidate (the `why` field is the existing convention, 270/271 candidates have one) and in the item file; the page will not display it (web/review.js is agent a's 307 file - do not edit; display can be a later task). CRITICAL LOOP AVOIDANCE: item candidates are also a SOURCE of queue candidates, so a flagged candidate added to the site's own item must be excluded from that site's queue by the per-build check (it re-flags every build - intended: it stays in the review queue, never re-enters the queue, until the human resolves it by saving a fit).
- Test impact: test_fit_queue_real derives the entry set independently as (built & (row_sites | item_sites)) - hand and asserts equality - my change WILL change the real entry set (e.g. devil-s-dyke loses its Brighton row; if the hillfort is built it gains one; the ARDOCH row leaves coria/vindomora's candidates). That test must be updated in the same commit (it is in my Touches): derive with the same check (import the module in-test; the venv has everything). test_fit_queue_synthetic must keep passing UNCHANGED (its tree has no catalog/books -> the check is a no-op there; if it doesn't, that's a bug in the degrade path, not a test to loosen). Part 2 (save -> line) and Part 3 (card) tests read the real queue via _pick_site()/entries[0..2] - they derive, but if entry 1 (devil-s-dyke) leaves the queue the card test's screenshots/claims in docs shift; check whether _pick_site still finds a site (it needs a book row with local page + unresolved item + pairs>=3 + no docs) - re-run after the change.

**Working design (draft, refine when implementing):**
For each (site S, candidate C) queue pairing: collect (a) site place facts: sites.json entry place/region/lon/lat/name/aka + catalog row name/aliases/admin/region/coords/qid; (b) picture place facts: source row (books index.jsonl by id; commons files.jsonl by c_+sha1(title)[:16]; review item candidate's own stored title/evidence) title/title_on_page/place(OCR)/site_names/desc + evidence (named_place, place dict, tied site, conflict) + book-list section county. Mismatch when any of: H1 picture county/state word != site's KNOWN county/state; H2 section county != site's KNOWN county (the Brighton case: sussex vs cambridgeshire); H3 recorded conflict >50km with a plausible named place (plausibility filter TBD - eyeball list first); H4 (soft, maybe skip) tie is name-only (exact, place dict empty, no section county) and the caption names a place word (non-terrain, non-name) that is in neither the site's place words nor explainable by its county - this catches Brighton even without the list, and the section county upgrades it to hard. On mismatch: drop C from S's candidates (recompute best among the rest; S leaves the queue if none remain); record C in S's review item with why="same name, other place: <caption place> vs <site place>"; find the right site R by re-scoring the row against the catalog with score_candidate BUT with a place gate (implied county must be compatible with the candidate site's admin county, west/east-sussex ~ sussex by substring) and take the best passing site (for the Brighton row the hillfort is the expected unique pass); if R exists: move C to R (R's queue entry as a synthesized row with sites=[R] if R is built and hand-fit-free, else R's review item with the same reason). Reason string uses the caption's place as printed ("near Brighton" / the county word / the section county) vs the site's place string.

**Exact next step:** (1) Add "tools/right_place.py" to the Touches line. (2) Fix the section-county walk (file order over the list's figures-or-plates, match the row's fig/plate key, carry the last explicit place_of(uk_county)) and RE-VERIFY it gives sussex for figs 216/217/218 and somerset for 224, dorset-appropriate for Maumbury (n0608_1, "Maumbury Rings, Dorchester" - must NOT flag: maumbury-rings is in Dorset; verify what section that fig/plate falls in and that the walk doesn't carry a stale county across a section boundary - check how sections actually delimit in the list: if a section has no county word in its titles the previous section's county wrongly carries - mitigate by only applying H2 when the walked county also appears in the site's... no: apply H2 only when the row's OWN explicit county word OR the walked county is within N list entries of the last explicit county change and the list shows a section boundary pattern; simplest robust version: H2 fires only when the walked county is EXPLICITLY stated by some entry within the same section (walk back to the nearest explicit county and require no LATER-different explicit county before a long county-free gap? - decide by looking at how Allcroft's list actually sections: measure the max county-free run length in the real lists first). (3) Implement tools/right_place.py (stdlib, missing-tolerant) with the check + find_right_site. (4) Wire into tools/fit_queue.py build() (keep the 4-input no-op degrade). (5) Update tests/test_fit_queue.py: new synthetic namesake case (a temp tree WITH a minimal data/catalog + books list so the check runs: a site "s-same" in county X, a row captioned with a town in county Y where the section county is Y, and a second catalog site in county Y with the same name -> expect: s-same's entry loses the row / leaves the queue, the row lands on the county-Y site's entry or review item with the reason string; plus the H1 county-word case) and fix test_fit_queue_real's derived entry set. (6) Rebuild the real queue (run the tool on the checkout), eyeball EVERY flagged entry (save the full list in DECISIONS), write the docs/site_flow.md section (count + list of wrong entries; Brighton not paired with the Cambridgeshire dyke), commit the regenerated web/data/fit_queue.json + touched data/review/ items + web/data/review.json (regenerate via fit/review.py export).

**Re-read:**
- tools/fit_queue.py:build - the new filtering goes around _candidates(); _synth_row is the row shape for a moved candidate (narrow sites to the target).
- fit/review.py:upsert_item - write-once resolved, candidates merged by plan, file name follows candidates[0].plan (an added mismatch candidate may MOVE the item file if it becomes lead - check item file renames don't clash with existing files; a same-plan replace is in-place).
- data/books/lists/*.json structure - plates vs figures keys, entry key names differ per book (plate vs fig).
- tests/test_fit_queue.py::_pick_site - after entry 1 leaves the queue, does a pick still exist for part 2?

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

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/215-books-llm-ports.md`

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

### 2026-10-12 HANDOVER (iteration 92, agent c, task 309): investigation complete, NO code written. The right-place check design (stdlib tools/right_place.py; the book's list-of-figures section county as the Brighton signal; plausibility filter on noisy recorded conflicts; 50km tied-away guard; test impact on test_fit_queue_real/synthetic) is in tasks/309-queue-right-place.md ## Hand-over, facts in DECISIONS.md (309 entry). Next session: re-verify the section walk (sussex for figs 216-223), then implement. NOTE: uncommitted data/surveyfit/heldout/* changes in this checkout belong to task 304 (one-shot run state), intentionally left for the next 304 session.
