Status: open
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200, 211, 218
Touches: fit/src_mackenzie.py, data/catalog/extras_mackenzie.jsonl, data/commons/files_mackenzie.jsonl, data/commons/classified_mackenzie.jsonl, data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json, docs/lead_mackenzie.md, tests/test_src_mackenzie.py, tests/golden/src_mackenzie_sample.json

## Goal
GOAL.md point 4: page 212 of Mackenzie, The Castles of England (1897) is a five-towered
castle plan with no caption - the only gap in the book's already hand-tied 29 plates
(pipeline/sources.py). Identify the castle with evidence (the book is arranged by county:
the plates around p.212 - p.207 Oxford, p.231 Lancaster - constrain it; five-towered plans
are rare; the surviving ground is the final check), tie it to a site, stage the row, and let
the fit prove the identification. If it cannot be identified with evidence, document the
search and drop the lead: a wrong castle on the map is worse than none.

## Acceptance criteria
- [ ] The p.212 scan is found (the British Library's Flickr scans, the same URL pattern as
      the hand-tied rows) and downloaded to data/raw/books/ in the working phase; the
      five-towered plan is drawn out and available for comparison (its shape, tower count,
      and any scale/north information recorded in docs/lead_mackenzie.md).
- [ ] The castle is identified by evidence recorded in docs/lead_mackenzie.md: the book's
      county context, the plan's shape against candidate castles, and the surviving ground
      (relief/aerial) matching the plan - or the lead is dropped, and the file says exactly
      what was searched, what candidates were considered, and why none was accepted.
- [ ] If identified: the site (an existing one by QID, or a new extras row) and the picture
      row are staged (files_mackenzie.jsonl with the 200 evidence field - caption+coords or
      QID, the source book recorded - and a classified row "plan" by hand), and a fit of the
      plan on the site's ground passes the gate (001): the identification is proven by
      numbers, not just asserted.
- [ ] Test (no network): the staged row joins and passes fit/evidence.py check offline, with
      a golden sample. If the lead was dropped, the test asserts the documentation exists
      and the staging files are absent or empty.

## Notes
- The other 29 Mackenzie plates stay where they are (sources.py hand ties); this task adds
  at most one row. The fit is proposed through 202's machinery if available; otherwise a
  hand proposal (fitkit) is fine - this is one plate, not a batch.
- A castle whose site is not built yet: the extras row gets the picture as its reason to
  build (aerial_ok) so 211 builds it with the plan already tied.

## Hand-over

**Iteration 66 (2026-10-11, agent a) - lead doc written and committed; the test is the only remaining step.**

STATE at stop:
- `docs/lead_mackenzie.md`: WRITTEN and committed this session (second commit) - all five sections per prep §3, every fact re-verified this session (below). It says "26 rows" for the sources.py MACKENZIE table (verified: 26 mackenzie rows in canonical files.jsonl, all evidence kind "hand_tied" with cat null) - the task's "29" is the book-level count; do not "correct" the doc toward 29.
- Everything from iter 65 is committed (driver commit ab899eb included the `_file_row` fix): the 3 staged files (one row each), the platefit doc (c_e6e5490609414bb9), `tests/golden/src_mackenzie_sample.json`, `fit/src_mackenzie.py`.
- `tests/test_src_mackenzie.py`: NOT yet written. That is the next and only code artifact. No boxes ticked yet; Status stays **open**.

THIS SESSION'S RE-VERIFICATIONS (all pass, offline):
- `--gate`: accept, n 4, med 15.810503946029705, slope_o 0.13850057306409141, io -7.041363723612259; `plan_fit.similarity` (returns (a, b, resid, k)): a = 0.38242430630722735-0.0013382950967304546j, rotation -0.2005 deg (math.degrees(cmath.phase(a))), residuals [14.16, 1.98, 17.46, 19.36] max 19.36, k 0.598641799078818 (ground scale |a|*k = 0.229 m/px).
- `--check`: exit 0; output exactly `PASS category        shotwick-castle-q7502621|File:212 ...` then `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`.
- Every OCR quote in the lead doc verified against /tmp/mack/{searchtext.gz,hocr_pageindex.json.gz,pagenums.json}: chapter (leaf 228 -> printed 180; heading "S H O T W I C K" + garbled "(non-existent)"; Leland quote; "pentagon strengthened by six towers" (OCR "bv" = "by"); mound+crescent+entrenchments); index (leaf 539 = printed 447): "Shotlack, ii. 179, Shotwick, ii. 180."; running heads CHESHIRE 163/165/167/171/173/175/179/181; leaf 231 -> printed 183 = LANCASHIRE part opens ("Henry VII. conferred the estate on ... Lord Stanley, afterwards first Earl of Derby"); pagenums: 228->180, 229->181, 231->183, 232->184, 539->447. /tmp/mack/ still holds all artifacts incl. mack_poly6.py.

TEST SPEC (`tests/test_src_mackenzie.py` - write exactly this; no conftest.py edits, no fixed ports, no network, tmp_path only for writes):
- Module docstring: task 206, GOAL point 4; the book's one captionless plan = the gap named in sources.py's MACKENZIE comment; identified as Shotwick Q7502621 per docs/lead_mackenzie.md; offline tests (fixture, stored-field evidence check, gate re-run on the committed doc's own pairs = docs/gate.md §4 true case, negative control never written, golden pin).
- Imports: ROOT; insert fit/ and pipeline/ into sys.path; import evidence, fit_gate, plan_fit, sources, src_mackenzie as mack; `NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")` (absent - fine: `evidence.check` guards `os.path.exists(books)`, default catalog = sites.jsonl).
- `@pytest.fixture(autouse=True) def no_network(monkeypatch)`: boom on `socket.socket` / `socket.create_connection` / `socket.getaddrinfo` (van deventer's exact pattern; the module's own import-time code touches no sockets).
- `test_staged_row_and_join`: one row each in FILES/CLASSIFIED/EXTRAS (`mack._load`). File row: site "shotwick-castle-q7502621", qid "Q7502621", title == mack.TITLE, year 1897, wd_plan False, cat "Shotwick Castle", name "Shotwick Castle, plan from Mackenzie, The Castles of England (1897)", by "fit/src_mackenzie.py", (w,h) == (839,840), mime "image/jpeg", url startswith "https://upload.wikimedia.org/", page startswith "https://commons.wikimedia.org/wiki/File:", evidence {rec "evidence/1", kind "category", checked non-empty, site_cat == file_cat == "Shotwick Castle", via []}. Site: in mack.SITES_CANONICAL with qid Q7502621 (the existing-by-QID path); NOT in the EXTRAS_CANONICAL id set (no merge double); extras row: id == SITE, aerial_ok True, source "fit/src_mackenzie.py". (SITE, TITLE) not in the (site,title) set of mack.FILES_CANONICAL; mack.TITLE not in `{t for t, _, _, _ in sources.SOURCES["mackenzie"]["rows"]}` (the 26 hand-tied). Classified row 1:1, (p_plan, p_birdseye, p_photo, by) == (1.0, 0.0, 0.0, "hand"). Doc (mack.DB_DOC): site/plan with plan == "c_" + hashlib.sha1(mack.TITLE.encode()).hexdigest()[:16], size [839,840], crop [0,0,839,840], src "commons", model "similarity", label "1897", 4 pairs, each 0 <= u < 839 and 0 <= v < 840, and `evidence.hav_m(lon, lat, s["lon"], s["lat"]) < 200` for the site s.
- `test_evidence_offline_and_negative_control(tmp_path)`: `code, text = evidence.check(mack.FILES, NO_BOOKS)`; assert code 0; `"evidence: 1 rows, 1 pass, 0 fail, 0 no-tie"` in text; PASS line exactly `f"{'PASS':4s} {'category':15s} {mack.SITE}|{mack.TITLE}"` in text. Negative control (never written): copy the staged row, set evidence file_cat to "Not the Castle's Category" (tie broken: check_category returns False, reason f"file category {fc!r} differs from the site's with no recorded chain"), write to tmp_path/"bad_row.jsonl" (json.dumps + "\n"), run `evidence.check(str(f), NO_BOOKS)` -> code 1, a FAIL line containing "differs from the site's with no recorded chain", `"evidence: 1 rows, 0 pass, 1 fail, 0 no-tie"`; then assert the staged file's evidence is unchanged (capture before/after).
- `test_gate_accepts_the_committed_doc`: doc = json.load(mack.DB_DOC); `verdict, stats = fit_gate.gate(doc["pairs"])`; assert verdict == fit_gate.ACCEPT; stats["n"] == 4; med == pytest.approx(15.81, abs=0.01); slope_o == pytest.approx(0.1385, abs=0.001) (the 0.11-0.145 "must be said" band - say so in a comment); io == pytest.approx(-7.04, abs=0.01). `a, b, resid, k = plan_fit.similarity(doc["pairs"])`: all residuals finite, float(resid.max()) < 45; math.degrees(cmath.phase(a)) == pytest.approx(-0.2, abs=0.05) (north-up: the compass arrow's page-left north is 90 deg off, lead doc §2).
- `test_golden_sample_matches_staged`: golden = json.load(tests/golden/src_mackenzie_sample.json); assert golden["files"] == mack._norm(mack._load(mack.FILES)); same for "classified" and "extras"; golden["doc"] == dict(json.load(open(mack.DB_DOC)), at="0000-00-00T00:00:00+00:00") (mirrors the module's golden(); _norm normalizes date_commons and evidence.checked).

THEN (same session, in order):
1. `timeout 300 .venv/bin/python -m pytest -q tests/test_src_mackenzie.py` -> green; `timeout 900 .venv/bin/python -m pytest -q` -> my tests green + the 4 known-red still red (test_serve::test_platefits_docs_match_sites, the 2 test_batch_eu union tests, test_gate::test_recorded_measurement_reproduces_and_agrees - dependency-owned by 211/218, DO NOT touch or "fix").
2. Tick all 4 boxes in this task file (box 3 LAST - the gate is proven on the committed doc); Status stays **open** (the done claim waits for 211 + 218 per the Depends on line; the driver brings the task back, a later session sets done).
3. Commit: `git add tasks/206-mackenzie-p212.md tests/test_src_mackenzie.py DECISIONS.md && git commit -m "206: test for the staged p.212 plate (Shotwick) - boxes ticked; done-claim waits on 211+218"`.

Re-verify recipe if anything drifts: `timeout 300 .venv/bin/python fit/src_mackenzie.py --check` and `--gate` (both offline); staging is idempotent (re-running stage() is a no-op); `--verify` re-checks live facts (network, paced); V2 OCR re-download recipe: archive.org item castlesofengland02mack, files castlesofengland02mack_hocr_searchtext.txt.gz / ..._hocr_pageindex.json.gz / ..._page_numbers.json (pageindex rows = [textStart, textEnd, byteStart, byteEnd] text offsets, NOT leaves; pagenums maps leafNum->pageNumber as strings).
