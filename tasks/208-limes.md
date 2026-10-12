Status: open
# 208: The German Limes - fort plans from the old reports
Depends on: 200
Touches: fit/src_limes.py, data/catalog/extras_limes.jsonl, data/commons/files_limes.jsonl, data/commons/classified_limes.jsonl, docs/lead_limes.md, tests/test_src_limes.py

## Goal
GOAL.md point 4, the least certain of the seven leads: fort plans from the German Limes
reports (ORL and its successors; the forts of the Upper and Lower Germanic Limes are a
natural growth area - many are not in the catalog yet). Verify first whether free,
machine-readable fort plans exist (old government reports are public domain, but the scans
must actually be available: a library site, an archive, Internet Archive, or Commons). If
yes: stage the plans tied to their forts. If no: document exactly what was searched and
drop the lead - the other six leads stand on their own (PLAN.md assumption 7).

## Acceptance criteria
- [ ] docs/lead_limes.md records the verification either way: what sources were checked
      (names, URLs, dates), what is free and machine-readable, and the decision (proceed /
      drop). A dropped lead ends this task with `Status: dropped`, the documentation
      committed, and no staging files.
- [ ] If proceeding: staged rows - files_limes.jsonl for every staged fort plan (with the
      200 evidence field: the report's list/caption names the fort; coordinates from the
      report cross-checked where possible) and extras_limes.jsonl for forts not in the
      catalog (QID from Wikidata where it exists, kind "roman fort", lon/lat from the
      report); a classified row by hand per picture; the plan's date recorded on the row
      (the 150-year rule: fort plans of structures are exempt, recorded anyway).
- [ ] At least 10 fort plans staged from at least 2 sources, or the documentation accounts
      for every missing one with a reason (a verified drop beats a guessed row).
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join and the evidence check passes, with a golden sample. If the lead
      was dropped, the test asserts the documentation exists and the staging files are
      absent or empty.

## Notes
- If the reports turn out to be Internet Archive books indexable with pipeline/books.py,
  work in per-book files only (triage/<ia>.*, lists/<book>.json) and add those exact paths
  to this task's Touches line before writing them - never the shared index.jsonl or
  validation.json (211 rebuilds both).
- The forts' QIDs are patchy on Wikidata: name+coordinates from the report is an acceptable
  tie when no QID exists, recorded as such on the row (the evidence kind says so).

## Hand-over

(2026-10-12, iteration 158, agent a — session 1 of 208: the verification sweep, IA side DONE, de.wiki/Commons side half done. No staging files written yet; the lead doc is NOT written yet — writing docs/lead_limes.md is the first job of the next session, from this hand-over and the cached files below.)

### What session 1 established (all verified live 2026-10-12)

**Dependency 200 is merged** (fit/evidence.py in main, 850 lines; tests/test_evidence.py green per driver). OQ-1 RESOLVED: the src_* pattern (copy fit/src_artists.py, the cleanest) = module with a hand-verified SITES/FORTS table + SOURCES table, stage() writing THIS task's 3 staging files (append-only, idempotent on (site,title)), evidence field hand-recorded, check_staged() = offline join + `evidence.check(FILES_LIMES, NO_BOOKS, catalog=EXTRAS_LIMES)` (NO_BOOKS = data/books/.no-books, never exists → books skipped). Evidence kind for a report scan whose caption names the fort = `caption_coords`, fields (check_caption, fit/evidence.py L190): {"rec":"evidence/1","kind":"caption_coords","checked":date,"named_place":<fort name>,"place_qid","place_label","place_lon","place_lat","site_lon","site_lat","dist_m"} — check requires norm(named_place) ⊂ norm(title+" "+desc), dist_m reproduces within 1000 m, dist ≤ 50 km. Row date = the plan's date (150-year exempt, recorded anyway).

**Source 1 — the anchor, VERIFIED (free + machine-readable):** IA `derobergermanis00fabrgoog` = **ORL Lieferung II = Band IV Abteilung B Nr. 40, "Das Kastell Osterburken" (mit sieben Tafeln), O. Petters, Heidelberg, 1895** (title page leaf 5, read from the djvu XML). Google scan, PD (Google notice leaf 1-2). BookReader works on it: 64 pages, per-page OCR parseable from the `_djvu.xml` (see pitfalls below), full-res page images at `https://archive.org/download/derobergermanis00fabrgoog/page/n{N}.jpg` (5398×7526; N = 0-based index of the BookReader flat list; n54 and n56 already cached in data/raw/books/derobergermanis00fabrgoog/). ALL 7 plates viewed (40 dpi renders in /tmp/agent-a-208/orl/p-*.jpg):
- leaf 53 (n=52) Taf. I: 2 photos (Atrium-Fundament/Schwelle; Mithrasrelief) — not plans
- leaf 55 (n=54) Taf. II: **Situationskizze, MAASSTAB 1:3000**, title "Nr 40 KASTELL O[sterburken]" — fort-area map → stageable as a plan-kind drawing (re-check at full res for a date mark; at 40 dpi I misread "V. 1905"/"1:2000" — do NOT record those)
- leaf 57 (n=56) Taf. III: **the fort plan (Grundriss)** — both fort lines (upper + later Anbau, lower Anlage), gates lettered, scale bar, ~1:500 → THE anchor plan (the monograph text: drawn "im Wesentlichen nach dem Mannheimer Plan")
- leaf 59 (n=58) Taf. IV: gate/wall details + "Profil des Lagers" (sections) — not a plan
- leaf 61 (n=60) Taf. V: bronze finds; leaf 63 (n=62) Taf. VI: iron finds (spearheads, helmet); leaf 64 (n=63) Taf. VII: blank
→ this volume alone = 1 certain plan + 1 situation map, ONE fort (Osterburken). Not enough by itself.

**IA supply exhausted:** no other ORL volume on IA (title:(obergermanisch OR obergermanisch-raetische) → only this + limes90deroberge00henr 2009 photo book; "Limes der Römer" 0; (Kastell) AND (Limes) 0). Limesblatt (Mitteilungen der Streckenkommissare, Trier 1892–1903, 35 Hefte) = 2 identical IA Google scans: `limesblatt00unkngoog` (499 p) + `limesblattmitte00germgoog` (506 p, Harvard/Pierce bequest); djvu texts mined: pure text excavation reports (all 13 "Tafel"/33 "Karte" hits are references to other publications; no map plates) → no stageable plans, documented as such.

**Source 2 — de.wikipedia ORL plate set, CONFIRMED (the second source; decision leans PROCEED):** 874 files named ORL* (MediaWiki `list=allimages&aiprefix=ORL`; **continuation key is `aicontinue`, not aifrom/aipfrom**), 842 plate files ("tab"), **45 fort numbers**, **167 files with "Grundriss" in the name**. Naming: `ORL_<nr>_tab_<n>_pic_<m>_<content>.jpg` (Abt B), `ORL_A_<nr>_...` (Abt A), `ORL<NR>_<name>.jpg`. Samples: ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg, ORL_40_tab_04_pic_01_Grundriss.jpg, ORL_49_Würzberg_Therme_1800.jpg (1800!), ORL_62a_Horreum_Frick_1824.jpg (1824). Sample license check (de.wiki imageinfo extmetadata): Bild-PD-alt (Bodewig d.1923), PD-alt-100 (Conrady; Lehner; Dahm), Bild-frei (unbekannt) → free. **They also exist on Commons with SPACE naming**: Commons search "ORL Grundriss" → File:ORL 12 tab 02 pic 01 Grundriss und Profile.jpg, ORL 33 tab 02 pic 01 Grundriss.jpg, ORL 01 tab 02 pic 01 Grundriss.jpg, ORL 33 tab 03 pic 05 Porta Praetoria Grundriss.jpg; also "ORL B 2 3b Taf 1/2/9 Kastell Wiesbaden.jpg" (Abt B Band 2 = lower? no: B 2 = Band 2). Per R5: stage the COMMONS file (category/P373 or caption evidence) and note the de.wiki twin; check Commons categories of the forts (P373) in session 2. **Cached full de.wiki list: /tmp/agent-a-208/orl_dewiki.json** (874 entries with size/timestamp/url) — re-fetchable via the aicontinue query in 4 API calls.

**Blocked sources (document in the lead doc, do not retry this session):** limesblatt.uni-hd.de (TCP connect fails both http/https; DNS 129.206.119.232); DNB portal (Anubis JS wall: /sru 404, simpleSearch → honeypot page); www.deutschedigitadebibliothek.de / digital.ub.uni-heidelberg.de (no DNS from this VM).

**Decision:** the box-3 rule (≥ 10 verifiable named fort plans from ≥ 2 free machine-readable sources) is reachable on paper: source 1 (1895 ORL vol: 1–2 plans) + source 2 (de.wiki/Commons ORL set: 167 Grundriss files, 45 forts). Next session commits the decision after the Commons leg verifies ≥ 10 stageable Commons files (fit-sized, free, named) — otherwise document every missing one and drop per the rule.

### Exact next steps (session 2)
1. **Write docs/lead_limes.md** from this hand-over (structure like docs/lead_kip.md): §1 verification-sweep table (rows: 1895 ORL vol / other IA ORL / Limesblatt IA+de.wiki / de.wiki ORL set / Commons P373 / limesblatt.uni-hd.de / DNB — name, URL, date, free?, machine-readable?, plans?, verdict); §2 the 1895 volume plate inventory (7 rows with leaf/n, kind, date, stageable?); §3 de.wiki/Commons ORL census (counts + Grundriss list); §4 decision. Check-date everything 2026-10-12.
2. **Commons leg (paced, commons.get, R7):** for a candidate fort list (start with the forts whose de.wiki ORL files are named "Grundriss": 01, 02a, 03, 05, 05a, 06, 07, 08, 12, 18, 33, 34, 39, 40, 41, 42, 44, 45, 46, 46b, 47, 48, 49, 50, 51, 52, 54-55, 56, 57, 58, 59, 60, 61, 62a, 63, 64, 65, 66, 67, 69, 71, 72 — the ORL B fort numbers; the forts' modern names: e.g. 01 Kastellbad, 06 Holzhausen, 40 Osterburken, 49 Würzberg/Kastellbad-Würrstberg… resolve names via the de.wiki ORL article or the Limes article) find the Commons file (spaces) for each ORL_<nr>_tab_02/_04 Grundriss, get metadata via commons.info(), check P373 category membership, size ≥ 1000 px, date, license. Target: ≥ 10 stageable across ≥ 2 ORL volumes (they are different volumes: Band I Abt B etc. — the tab-plate numbering differs per volume).
3. **QIDs for the chosen forts** via de.wiki pageprops or Wikidata (Saalburg Q542329, Eining Q1735352 known; per-fort verify, no-qid forts stage with name+coords per task Notes).
4. Then stage() + evidence + tests + golden per the prep plan §2-3 (touches only the 6 files in the Touches line). If the Commons leg yields < 10 (or < 2 usable sources), write the drop doc (206/209c pattern: test asserts doc exists + staging files absent/empty) and set Status: dropped.

### Environment notes for the next session
- System python3 has no PIL/numpy; .venv has pillow (I used it for crops). pdftoppm/pdftotext installed. IA downloads + BookReader work fine from this VM (no throttle observed; books_ia.get has backoff).
- data/raw/books/derobergermanis00fabrgoog/ (gitignored) holds: .pdf, _djvu.txt, _djvu.xml, bookreader.json, page_n54.jpg, page_n56.jpg (full-res plate pages). /tmp/agent-a-208/orl/ holds the 40 dpi renders (p-52..p-64) + legend crops — may be wiped between sessions; regenerate from the PDF (pdftoppm) if missing.
- Wikimedia 429s after ~12-20 rapid calls (PITFALLS); commons.get paces + honors Retry-After. Keep the Commons leg to one paced run.

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

2026-10-12 208 (iteration 158, session 1): sweep done on the IA side — anchor ORL 1895 vol (Osterburken) verified free+machine-readable with 2 stageable drawings; no other ORL on IA; Limesblatt text-only. Second source found: de.wiki/Commons ORL plate set (874 files, 167 Grundrisse, 45 forts, sampled licenses free). Decision "proceed" leans yes, commits after the paced Commons leg verifies >=10 fit-sized named plans from >=2 volumes. docs/lead_limes.md NOT yet written (context limit) — session 2 writes it first, from the task's Hand-over. DNB/uni-hd sources blocked (recorded in the decisions entry).

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
