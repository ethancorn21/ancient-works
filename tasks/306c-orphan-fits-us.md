Status: in-progress
# 306c: Look at the orphan agent fits, US - 16 docs, 9 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306c.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 16
US platefit documents with `by: agent` that are ORPHANS - in the store, but with no overlay
built on the site and not referenced by any review item, so a visitor sees them not at all.
Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief (every site here has a `relief.jpg`), with the doc's
stored pairs placed. The verdict records where the doc stands today (invisible) and whether
the placement is good enough to keep.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief), taken with `tools/shot.mjs` against `server/serve.py --port 0` on this checkout
      (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real mounds, banks, ditches) and
      the verdict (keeps its document / deleted - and it is an orphan today, invisible on the
      page).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (16, 9 sites)
- cahokia-q333661.annualreportofbu1218901891smit_n0200_1 - Map of Cahokia group, Madison county, Illinois
- etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 - Plat of the Etowah group (original)
- fort-ancient-q5470727.b24849959_n0264_1 - Fort Ancient, Warren county (Squier & Davis)
- hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 - Plan of Cemetery Mound, Mt. Vernon
- hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 - Plan of mound at Mt. Vernon (Squier & Davis)
- marietta.b24849959_n0195_1 - The Marietta works (Squier & Davis)
- mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 - Plan of Cemetery mound, Mt. Vernon, Knox county
- mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e - Peter Village enclosure, Squier & Davis Plate XIV fig 3
- pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 - (Squier & Davis, untitled)
- serpent-mound-q968802.b24849959_n0313_1 - Serpent Mound; from Holmes
- serpent-mound-q968802.c_15ff865e5f3d8ddb - Serpent Mound by William Jacob Baer
- serpent-mound-q968802.c_2c260a03d1f8df1c - SD35 Serpent Mound, Squier & Davis Plate XXXV
- serpent-mound-q968802.c_52dfe1fc979edf2c - Harper's New Monthly Magazine, vol 104
- serpent-mound-q968802.c_7b01a4bb50d68b56 - 26 of A School History of the United States
- serpent-mound-q968802.c_8ebd42607fbb96d8 - 26 of A School History of the United States (2nd copy)
- serpent-mound-q968802.c_dd2c553d611e610b - 26 of A School History of the United States (3rd copy)

## Notes
- serpent-mound carries the site's one hand fit (n0210_1) on the map; its 7 agent docs are all
  orphans. The hand doc is never touched and its overlay stays whatever this audit decides about
  the agent docs.

## Hand-over
(2026-10-12, iteration 146, agent c - FIRST session on 306c. Driver built and 32-shot run launched; 1 of 16 judged (marietta: DELETE case). Session died at the context limit during judging.)

**State.** (1) `tools/audit_306c.mjs` exists: a clone of 306b's driver with the 16 US-orphan docs; it works on the POST-307-REWORK page (marietta test shot verified: `refit()` unwrapped when not placed, simFit on the doc's pairs intact, `fit-prev` layer drawn, `[eval]` reports fit stats). Run the full batch: `node tools/audit_306c.mjs` (one `server/serve.py --port 0`; skips existing shots, so it is resumable). Launched in the background at ~iteration start: `nohup node tools/audit_306c.mjs > /tmp/audit_306c.log 2>&1 &` (pid 3980429). At the context limit the last line was serpent-mound c_8ebd42607fbb96d8 ground=imagery written; the relief of that doc plus c_dd2c553d611e610b (both grounds) were still to come - CHECK /tmp/audit_306c.log for the final `[audit 306c] all shots written` line (or re-run the driver, it skips what exists). All 30+ written shots are in docs/site_flow/agent_fits/ (uncommitted, the harness keeps them). (2) FQ contamination: hodgen-s-cemetery-mound b24849959_n0353_1 and pyramid-mound ancientmonuments00squi_n0134_1 have fit-queue propose entries; the driver empties FQ.entries before openPlan, so verify in /tmp/audit_306c.log that their `[eval]` lines say `"placed":false` (`fqEntries` is the total queue count 114, NOT the match count - do not read it as a match signal). (3) Tests not yet run this session; last suite in this checkout (306b, 2026-10-12): 128 passed, 1 skipped with `--ignore=tests/test_gate.py` (pre-existing red per the driver's loop-start note). After any data change run that command.

**Verified facts (all 16).** Every doc exists, `by: agent`, 4+ pairs; all 9 sites have relief.jpg; all 16 confirmed true orphans (a whole-store scan found 0 referenced by any of the 346 data/review/*.json items; the only overlays on the 9 sites are cahokia's c_aff1b996dce7fe3a - not ours - and serpent-mound's HAND fit ancientmonuments00squi_n0210_1, which must stay untouched).

**Judged so far - marietta (DELETED case, 303 way, NOT yet executed).** Fowke 1902 Fig. 15 (b24849959_n0195_1): fit 1.000 m/px, 0 deg, resid 0 (4 pairs, exact); the plate's own scale bar (ticks at page-px x 1375/1516/1659/1946 = 0/500/1000/2000 ft, bar at y~455) measures 1.073 m/px, so the SCALE is trustworthy. But the placement is ~1.3 km off: the drawn Conus mound (Fowke page px ~ (1888,1800), the concentric circle at the SE corner of the 27-Acre square) lands at (-81.4467, 39.4122), while the REAL Conus - the unmistakable ringed disc in Mound Cemetery, LiDAR block web/data/sites/marietta/block_top.jpg px (1163,704) on the georeferenced block [-81.4686167..-81.4383833] x [39.4283808..39.4086178] - is at (-81.4514, 39.4204). The drawn Conus sits on farm south of the town; the drawn 50-Acre square sits ~400 m W of the site centre (it is not a queue propose - (1000,1000) lands 409 m from the site centre, so this is an auto matcher with score 0). The site's own (different, S&D-style) hand-placed plate anchors on the real Conus. => verdict line + removal:
- upsert_item('.', 'marietta', [candidate]) with candidate = the doc's fields (plan, title 'The Marietta works', book 'Fowke 1902', ia b24849959, file n0195.jpg, label 'Fig. 15', cite, url null, view false, ref, size [2456,4075], map_box [0.085,0.1,0.91,0.78]) + the doc's 4 pairs + `place_reason` = the audit verdict (drawn works sit ~1.3 km S-E of the surviving Conus mound and ring ditch; 1 m/px scale is right, position is not).
- DELETE data/db/platefits/marietta.b24849959_n0195_1.json (AFTER the upsert).
- then scoped export: `.venv/bin/python -c "import sys; sys.path.insert(0,'fit'); import review; review.export('.', 'marietta')"` - export(root, site_id) records resolution into that one item file only and always recomputes web/data/review.json over the whole queue; with the doc deleted the item stays OPEN (resolved_doc finds no doc) so the site stays covered for the union check.
- BEFORE the removal, read tests/test_batch_eu.py (union check) and tests/test_serve.py::test_platefits_docs_match_sites to confirm deleting the doc + adding the open item keeps both green.
- the site's depictions.json has no plan depictions (only topo_1904) so there is nothing to rebuild there; do NOT run tools/site_done.py unless a test demands it (306a owns site rebuilds).

**Left for next sessions.** (a) Confirm the run finished (all 32 shots; re-run driver if not). (b) Judge the other 15 in batches (~4 per session, as 306b did: read the aerial+relief shots, verify the scale against the plate's own bar where it has one - measure ticks with PIL in .venv, 306b technique in its archived hand-over - and reverse-geocode/locate the site's real works; remember the site point can be a real modern city, 306b's sites.json pitfall). For serpent-mound's 7 docs: the site's hand fit (n0210_1) is the reference placement - compare each agent doc's fit to it; if an agent doc matches the hand fit's placement it is a duplicate candidate worth keeping in the store (orphan status unchanged - no overlay built) but the line should say so. (c) Write the verdict lines into docs/site_flow.md's "## The agent fits, looked at (task 306)" section: a 306c block (preamble: 16 US orphans, no review item - not shown to the owner at all; one line per doc: what the lines sit on + verdict STAYS/DELETED with the 303-way action), after 306b's last line (zwolle c_f9cddae6b944a648). (d) Execute any deletions the 303 way (order above), then run the suite (128/1 baseline). (e) Tick boxes 1-4 as verified.

**Pitfalls to file (next session).** (1) web/data/sites/<site>/depictions.json is a DICT {'depictions': [...]}, not a list (a throwaway check crashed on .get over a float). (2) some data/review/*.json lines parse to non-dict JSON (a bare float) - a scanner of all item files must isinstance-check. (3) PIL is in the project .venv (12.3.0) for scale-bar measurement; system python3 has no PIL.
