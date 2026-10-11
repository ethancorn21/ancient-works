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
- [ ] `tools/site_done.py <site id>` does the whole line for one site with the code that already exists
      (fit/batch_us.py `run_sites` for pictures not fitted yet, pipeline/plan_fit.py for each fit document,
      pipeline/build_site.py for the site entry and its marks), and prints what it did per picture: synced
      to the map, sent to the review queue, or skipped with the reason. It touches only that site's files.
- [ ] Stonehenge's automatic fit is an overlay on its site: web/data/sites/stonehenge-q39671/ and its entry in
      web/data/sites.json carry it (its drawing counts in the site's score and overlays, as the hand fits do).
      Every other picture of Stonehenge is a fit or an open review item.
- [ ] Checked in a browser, the way a visitor sees it: the page opens Stonehenge, the drawing shows over the
      ground in the right place (a screenshot under docs/site_flow/ with one line on what it shows), and the
      site's square on the map is coloured by its new score.
- [ ] tests/test_site_done.py runs the command on a copy of one site's files (no network) and checks the
      overlay and the entry; the full suite passes.
- [ ] docs/site_flow.md: the line, step by step, as the next site's session will run it, with what broke on
      Stonehenge and how it was fixed (so the next site does not meet it again).

## Notes
- The 20 hand fits and their golden file stay untouched.
- If a step of the existing code cannot do one site alone, fix that step here: this is the work of the first
  piece through a new line.

## Hand-over
(iteration 64, agent c - first session: orientation and design DONE, zero code written yet. The next session writes the code exactly as designed below, then runs the line on the real tree.)

**State**: task file now `Status: in-progress` with the expanded `Touches:` line (added fit/review.py, web/data/review.json, data/raw/commons/big/, docs/site_flow/ - all justified by the design below). Nothing else changed yet. Baseline suite this session: `.venv/bin/python -m pytest -q` -> **59 passed, 0 failed** (59.76 s; .venv builds on this branch, 800 is done here). System python3 lacks PIL - run everything with `.venv/bin/python` (usage strings should say so).

**Stonehenge's measured state (fresh this session - trust these over memory)**:
- 7 automatic platefit docs in data/db/platefits/ (all src=commons, model=similarity, each WITH good `ref`/`size`/`url` fields): c_022604d2be0becdc (4 pairs), **c_098c4cb138676939 (8 pairs, the 7.4 m flagship, Dawkins 1880 Fig.143)**, c_20f9f11153a0b7f0 (6), c_6933e3a931a0240a (4), c_83b4d6df7a6d2383 (8), c_897a5c1632e2fdd6 (4), c_f8386b6404e4ee63 (4).
- web/data/sites/stonehenge-q39671/ is built: relief.jpg, block_h/top, two OS maps (six-inch-1st 1842, os1inch 1900) + depictions.json with exactly those 2 kind:"map" entries, NO plans yet. sites.json entry has `drawings: 0`, no `plate` key.
- Review item data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json: 6 candidates - earthworkenglan01allcgoog_n0582_1 (book row; gate 78.9 m), c_9d3c66e9ed1a5215 (gate 55.8), c_97c1bf9ac3714bbe (3 pairs, stated scale not trusted), c_2559c7f8dbce0244 (gate 51.2), c_98b1e7a4534b54b5 (gate 115.6), c_ffb3daac218b481f (3 pairs, texture check not trusted); `resolved: None`.
- Doc plan-ids and item plan-ids are DISJOINT: 7 + 6 = all 13 plans.json rows for the site have a verdict -> **no batch run needed for Stonehenge; its line is sync + entry + review-publish only.** That is exactly why site_done must distinguish "covered" from "uncovered" candidates before deciding to run run_sites (a blind run_sites with model=None would CLOBBER the 6 rich item entries with "no model answer" stubs - batch_us.write_item upsert replaces whole entries; PITFALLS fit/ records that fact).
- NONE of the 7 big images is cached in data/raw/commons/big/ -> plan_fit.load_picture WILL download them from Commons on the real run (network works here; see 429 fix below). data/raw is a symlink to a sibling project (PITFALLS) - `cp`/`du` tricks lie; copy file-by-file.
- data/review/ = 340 items: 339 open, EXACTLY ONE (alligator-effigy-mound-q4732645, doc c_618a6be74dfaff32) is derived-resolved without a recorded `resolved` field -> a global review.export would rewrite that OTHER site's item file, violating "touches only that site's files" -> hence the scoped export below.
- web/data/review.json is stale (2 items, at 06:59, pre-batch). The export will bring it to the current 339-open population (a ~1-2 MB file; the page fetches it at boot - same thing 212 was going to produce, so no page change needed; index.html L438 colours the square red from `s.drawings` - no page change at all).

**The line (implement exactly this)** - new file `tools/site_done.py`:
```
usage: .venv/bin/python tools/site_done.py <site id> [--root DIR] [--working | --model-json FILE]
```
sys.path.insert(0, ROOT/"fit") and (ROOT/"pipeline"), then import batch_us, plan_fit, build_site, review (ROOT = the file's parent.parent, so it works against --root copies too). Steps, printing per picture as the acceptance box demands:
1. **fit**: rows = [r for r in batch_us._plans_rows(root) if sid in (r.get("sites") or [])]; docs = batch_us.pre_docs(root, sid); path, item = review._find_item(root, sid) (the private one IS 201's item lookup - items are keyed by their `site` field, not file name, data/review/README.md; put that in a comment). uncovered = rows with no doc and no item candidate. need_fit = bool(uncovered) or (not rows and not batch_us.is_pre_fit(root, sid) and item is None)  [second case = the no-picture item]. If need_fit: model = batch_us.llm_model(root) if --working, batch_us.recorded_model(json.loads(file)) if --model-json, else None (prints a note: unfitted pictures go to the item as "no model answer"); records = batch_us.run_sites(root, [sid], model); print rec["detail"] per candidate (auto -> "fit written (doc sid.plan, gate X m)", reject/could-not-fit -> "sent to the review queue (why)", skip -> "skipped: already fitted (doc)") plus rec["no_picture"]/rec["error"] when set. Else print e.g. "fit 13 candidate picture(s): 7 fitted (doc), 6 in the review item -> no batch run needed".
2. **sync**: for each doc (sorted): name = "<sid>.<plan>"; if plan_fit.is_done(doc, name, root) print "skipped: overlay already current (at <doc at>)"; else plan_fit.build(doc, root) in try/except SystemExit (print FAILED, count it); success line "synced to the map (plan_<plan>.webp, N pairs, gate X m)".
3. **entry**: before/after = the site's drawings in web/data/sites.json around build_site.set_drawings(sid, root); print "entry web/data/sites.json: drawings A -> B".
4. **review**: if item: n_open, n_total = review.export(root, site_id=sid); resolved = review.resolved_doc(item, root); print the item file's basename + candidate count + open/resolved-by-which-doc + "page now has N open of M items". No item -> "no review item (every picture is a fit)".
5. **per-picture summary**: one line per plans row (sorted): has doc -> "synced to the map"; in item -> "sent to the review queue (<gate X m - why | why | no model answer>)" plus "; the item is resolved by <doc>" when resolved; neither -> an error line "no doc and no review item - the line left this picture uncovered".
Exit codes: 2 = site not built (no sites.json entry OR no web/data/sites/<sid>/ dir - print which), 1 = any doc failed to sync, else 0.

**The three existing-code fixes (all in my Touches; keep every default-arg behaviour byte-identical for existing callers - serve.py calls plan_fit.main([]), batch_us imports plan_fit.similarity only)**:
- **pipeline/plan_fit.py**: add `def _root(root=None): return os.path.abspath(str(root)) if root else ROOT` (module constants DB/RAW/WEB stay for compat); thread `root=None` through `load_picture(doc, root)`, `build(doc, root)` (sites.json lookups, out_dir, dep path; its tail becomes `build_site.set_drawings(sid, r)`), `prune(root)`, `main(args, root)`; extract main's done-check into new `is_done(doc, name, root)` (dep entry with same `at`, kind in (plan,view), fit.doc == name); main keeps "explicit args always rebuild". TWO real bugs fixed here: (a) load_picture's bare urllib has no pacing/Retry-After - Wikimedia 429s a burst (PITFALLS: commons.get is the reference; add a small `_fetch(url, timeout, tries=4)` helper: sleep ~1 s between tries, UA = aw.UA, on HTTPError 429/5xx sleep `int(headers.get("Retry-After") or 30*(k+1))` and retry, other exceptions backoff 3*(k+1) s; use it for both the API json call and the image download; move urllib.request/urllib.parse/io imports to the top). (b) the `how` string says "Placed by hand..." for AUTO fits - wrong on the public page; when doc.get("auto") say "Fitted automatically by the batch on N matching points ... (gate score X m)" instead (keep the hand-fit strings byte-identical - the golden only pins docs/site.json, not source strings, but keep them anyway).
- **pipeline/build_site.py**: same `_root`; thread `root=None` into `drawings(sid, has_plate=False, root)`, `set_drawings(sid, root)` and `write_entry(entry, root)` (index_path from _root(root)); main() unchanged.
- **fit/review.py**: `export(root, site_id=None)` - behaviour identical, EXCEPT the write-once `resolved` record is written into an item file only when site_id is None or item["site"] == site_id (the page file is still computed over the whole queue, so its content for other sites is unchanged apart from the `at` timestamp). CLI export stays global (no flag); site_done calls the function. Update its docstring + the module docstring's "only export writes the page file" note to mention the scoped variant. data/review/README.md is NOT mine to edit (201's) - do not touch it.

**Next steps, in order**:
1. Write the three refactors + site_done.py exactly as above. Smoke-check imports with `.venv/bin/python -c`; never run a full export against the REAL tree before the code is right (it would record resolved on alligator's item).
2. REAL RUN (working VM, network allowed): `.venv/bin/python tools/site_done.py stonehenge-q39671` (no model flag - all covered). Expect: 7 Commons downloads (paced, ~1-2 min), 7 "synced to the map", drawings 0 -> 7, review item open (6 cands) in web/data/review.json, per-picture 7 synced / 6 review-queue. VERIFY on disk: depictions.json = the 2 maps + 7 plan entries (kind plan, file plan_<p>.webp, ink plan_<p>_ink.webp, 4 corners, fit.doc == "stonehenge-q39671.<p>", fit.at == doc at, fit.resid_m len == pairs, year parsed from label e.g. 1880/1800/1845/1872/1891, sorted by year; source string says "Fitted automatically"), 14 new .webp files in the site dir, sites.json entry drawings == 7 and NO other entry's bytes changed (diff before/after), web/data/review.json contains the stonehenge item (name "Stonehenge", lead earthworkenglan01allcgoog_n0582_1, 6 candidates verbatim) and no other item file changed (sha256 all of data/review/ before/after), data/db/platefits byte-identical before/after (the line never rewrites docs), the 20 hand-fit docs + tests/golden/hand_fit_docs.sha256 still `sha256sum -c` OK, full suite 59 green.
3. RE-RUN the command: every doc must print "skipped: overlay already current" and nothing changes (idempotency) - prove it live before the test asserts it.
4. NEXT SESSION: tests/test_site_done.py (copy ONE site's files into a tmp tree: web/data/sites.json (full real copy, 473 KB), web/data/sites/stonehenge-q39671/ (real files), web/data/plans.json, web/data/review.json, the 7 docs, the 1 item, and SYNTHETIC data/raw/commons/big/<plan>.jpg stand-ins sized exactly like each doc's `size` (fs=1) so load_picture never downloads; also copy the tools/, fit/, pipeline/ dirs into the tree since site_done resolves ROOT from its own path and the root arg redirects DATA paths only; block sockets like test_batch_us.py's no_network does); then the browser check (serve.py --port 0 + tools/shot.mjs, Chrome IS installed - PITFALLS: the full page boots headless on this VM; the probe selects stonehenge and a drawing dep, screenshot to docs/site_flow/ + one line in docs/site_flow.md on what it shows); finally write docs/site_flow.md (the line step by step for the next site + what broke on Stonehenge and the fix) and re-verify the suite.

**Pitfalls consulted that matter here**: Wikimedia 429 after ~12-20 back-to-back calls (PITFALLS ~L602); aw.UA is a DICT, not a string (~L441); data/raw is a symlink to a sibling project (~L100); system python3 cannot import PIL (~L94); headless Chrome boots the full page here (~L78/83); serve.py's plan_fit worker needs plan_fit.main([]) to keep working (~L251); review upsert replaces whole candidate entries (~L533) - why the fit step must be skipped when all candidates are covered.
