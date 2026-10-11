Status: in-progress
# 300: Stonehenge, finished on the map - the first site through the line
Depends on: none
Touches: tools/site_done.py, tests/test_site_done.py, docs/site_flow.md, docs/site_flow/, pipeline/plan_fit.py, pipeline/build_site.py, fit/review.py, web/data/sites.json, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, data/raw/commons/big/

## Goal
The owner, 2026-10-11: "I would rather the flow be completing 1 spot on the map, then move on to the next
spot. Rather than fit all spots on the map, create all UI elements for the map, etc." From now on work goes
one site at a time, all the way to the map, and the lead gives the next site only when this one is done.

Stonehenge is the first. It already has an automatic fit from the batch (203b):
data/db/platefits/stonehenge-q39671.c_098c4cb138676939.json, 8 pairs, gate score 7.4 m. Nothing from the batch
is on the page yet: the batch wrote fit documents, and 212's single sync was going to put them all on the map
at the end. This task takes Stonehenge through every remaining step, and turns those steps into one command
that the next sites reuse.

## Acceptance criteria
- [x] `tools/site_done.py <site id>` does the whole line for one site with the code that already exists
      (fit/batch_us.py `run_sites` for pictures not fitted yet, pipeline/plan_fit.py for each fit document,
      pipeline/build_site.py for the site entry and its marks), and prints what it did per picture: synced
      to the map, sent to the review queue, or skipped with the reason. It touches only that site's files.
- [x] Stonehenge's automatic fit is an overlay on its site: web/data/sites/stonehenge-q39671/ and its entry in
      web/data/sites.json carry it (its drawing counts in the site's score and overlays, as the hand fits do).
      Every other picture of Stonehenge is a fit or an open review item.
- [x] Checked in a browser, the way a visitor sees it: the page opens Stonehenge, the drawing shows over the
      ground in the right place (a screenshot under docs/site_flow/ with one line on what it shows), and the
      site's square on the map is coloured by its new score.
- [ ] tests/test_site_done.py runs the command on a copy of one site's files (no network) and checks the
      overlay and the entry; the full suite passes.
- [x] docs/site_flow.md: the line, step by step, as the next site's session will run it, with what broke on
      Stonehenge and how it was fixed (so the next site does not meet it again).

## Notes
- The 20 hand fits and their golden file stay untouched.
- If a step of the existing code cannot do one site alone, fix that step here: this is the work of the first
  piece through a new line.

## Hand-over
(iteration 65, agent c - the line is BUILT and RAN on the real tree; the browser check passed; ONLY box 4 remains: tests/test_site_done.py, then the task is done.)

**Done this session (all verified, all committed)**:
1. The three refactors, exactly as designed last session: `pipeline/plan_fit.py` (`_root` threading through load_picture/build/prune/main, new `is_done`, paced `_fetch` with Retry-After, auto docs get "Fitted automatically by the batch ... (gate score X m)" instead of "Placed by hand"), `pipeline/build_site.py` (`drawings`/`set_drawings`/`write_entry` take `root=None`), `fit/review.py` (`export(root, site_id=None)` scopes the write-once resolved record; page file still the whole queue). All default-arg behaviour preserved: suite 59 green before AND after.
2. `tools/site_done.py` written and run on the real tree, no model flag: "fit 13 candidate picture(s): 7 fitted (doc), 6 in the review item -> no batch run needed"; 7 syncs (7 Commons big-image downloads, paced, no 429); "entry ... drawings 0 -> 7"; "review ... 6 candidate(s), open; page now has 339 open of 340 items"; 13 per-picture lines (7 synced, 6 review-queue, zero uncovered); exit 0.
   - On-disk verified: depictions.json = the 2 maps + 7 plans (kind plan, file/ink names, 4 corners, fit.doc/at/resid_m, years 1800/1845/1872/1880x3/1891 sorted, "Fitted automatically" source); 14 new .webp in the site dir; sites.json ONLY the stonehenge entry changed (drawings 0->7, all other keys byte-equal); web/data/review.json has the item verbatim (name Stonehenge, lead earthworkenglan01allcgoog_n0582_1, 6 candidates); ALL 130 platefits docs and ALL 340 item files byte-identical before/after; hand-fit golden `sha256sum -c` green; suite 59 green.
   - RE-RUN: every doc "skipped: overlay already current", platefits byte-identical, sites.json byte-identical - idempotent.
   - One output bug found and fixed this session: the entry line first printed "7 -> 7" because plan_fit.build refreshes the drawings count as it goes, so the "before" read after sync saw the final value; the before is now captured before the sync (docs/site_flow.md records it).
3. Browser check (box 3): `.venv/bin/python server/serve.py --port 0` + `NODE_PATH=/home/agent/tools/shot/node_modules node tools/shot.mjs http://127.0.0.1:<port>/ docs/site_flow/stonehenge.png 10000 1400 900 "select('stonehenge-q39671')"` with an AFTER eval. Result: ready true, drawings 7, marker class WITHOUT `plain` (coloured square), first drawing (1800 plan) auto-selected, overlay source present. The screenshot shows the 1800 Rijksmuseum plan in red ink sitting exactly on the real sarsen circles over the aerial photograph, the panel listing all 7 drawings, the coloured map square. (The 1900 OS map is absent from the panel - the page hides surveys <150 y; noted in the doc.)
4. `docs/site_flow.md` written (the line step by step + what broke on Stonehenge: 429 pacing, the "placed by hand" lie, the 7->7 read, the scoped export, the <150y survey rule). PITFALLS 429 entry's Where line now names plan_fit._fetch.

**Remaining work - ONE session: `tests/test_site_done.py` (box 4), then Status: done.**
Design (a tmp_path tree, NO network - monkeypatch sockets like test_batch_us.no_network does; no server, no fixed port):
- Build the tree under tmp_path: copy the REAL current files - web/data/{sites.json,plans.json,review.json}, data/review/ (ALL 340 item files - so "no other site's item file changed" is checkable), data/db/platefits/stonehenge-q39671.*.json (the 7 docs), data/sites/stonehenge-q39671/site.json, and web/data/sites/stonehenge-q39671/ EXCEPT stripped back to pre-sync: delete the plan_*.webp files and filter depictions.json to its non-plan/non-view entries (that leaves exactly the 2 maps - the pre-sync state), and in the copied sites.json set the stonehenge entry's drawings to 0. Also copy the CODE dirs tools/, fit/, pipeline/ into the tree (site_done resolves ROOT from its own path, so the COPYED code must be the code under test; run the copied tools/site_done.py, --root defaults to the tree).
- Synthetic pictures: for each of the 7 docs write data/raw/commons/big/<plan>.jpg = Image.new("RGB", doc["size"], a distinct colour per plan). size == the picture size, so fs = 1 and the fit math is exactly the real one; content is irrelevant to depictions.json (it is derived from the docs' pairs/at/labels only).
- Run `.venv/bin/python <tree>/tools/site_done.py stonehenge-q39671` (subprocess, no model flag) in the no-network guard. Assert: exit 0; stdout has 7 "synced to the map" and 6 "sent to the review queue" and the fit line "13 candidate picture(s)" and "entry ... drawings 0 -> 7"; the tree's depictions.json equals the REAL repo's web/data/sites/stonehenge-q39671/depictions.json byte-for-byte (deterministic: same docs -> same entries); the 14 plan webp files exist; sites.json stonehenge entry drawings == 7 and no other entry changed (diff vs the copied original); web/data/review.json in the tree lists the stonehenge item (339 open of 340 - the copied queue is the real one); ALL item files except none changed (the stonehenge item has no resolving doc -> byte-identical; so: every data/review/*.json byte-identical after); all 7 platefit docs byte-identical; the run wrote nothing outside the tree.
- Caveats: review.export prints a stderr line only for a site missing from sites.json (not here); the tree's sites.json is the full real one (473 KB) so names resolve; keep the test hermetic - if it ever needs network it fails the guard, that is the point.
- Then: `.venv/bin/python -m pytest -q` full suite green -> tick box 4, set Status: done, commit.

**Pitfalls that matter for the test** (all in PITFALLS.md): system python3 has no PIL (run .venv/bin/python; the test itself runs under .venv via the driver); data/raw is a symlink to a sibling project (copy file-by-file into the tree, never the link); no_network pattern in tests/test_batch_us.py L81-86; shot.mjs/Chrome not needed for this test.
