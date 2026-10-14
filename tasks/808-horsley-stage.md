Status: open
Depends on: 807
Touches: fit/src_roman_horsley.py, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl, docs/lead_roman.md

# 808: Horsley - stage the 17 site-plan rows into the shared roman staging files

## Goal
Build the module's --stage leg (documented in fit/src_roman_horsley.py's docstring but not yet
implemented): append the book's 17 verified site-plan rows - one per kind-s leaf of 807's
corrected 24-entry list (the 15 wall maps, n0114, n0185) - to the parent's shared roman
staging files (data/commons/files_roman.jsonl + classified_roman.jsonl; new sites in
data/catalog/extras_roman.jsonl), every row tagged with britanniaromanao00hors, each with the
200 evidence field and the book's date 1732. Append-only and idempotent (the 204/205
pattern); --dry previews; fully offline (no LLM, no network). The staging plan to execute is
the Horsley section 807 wrote in docs/lead_roman.md.

## Acceptance criteria
- [ ] --stage and --dry in fit/src_roman_horsley.py: append-only, idempotent (a second run
      changes no file byte-wise), offline, writes ONLY data/commons/files_roman.jsonl,
      data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl (creating each if
      absent; never touching other rows, other books' tagged rows, or any file outside those
      three).
- [ ] files_roman.jsonl gains exactly 17 rows tagged with this book (one per kind-s leaf:
      n236-254 even, n278-286 even, n114, n185), row shape per data/commons/files.jsonl
      (site/qid/title/year/wd_plan/cat/url/thumb/w/h/mime/date/desc/evidence): the 15 wall
      maps tied to their principal named fort per the 216 design (multi-fort maps tie to the
      most-named/planned fort, the others recorded in desc) on the 216-verified catalog QID
      sites where one exists (castrum-segedunum-q637958 SEGEDUNVM, pons-aelius-q7227963
      PONSAELIVM, rudchester-roman-fort-associated-civil-s-q17669775 VINDOBALA,
      haltonchesters-roman-fort-settlement-and-q17648018 HANNAVVM, aesica-q4688554 the Aesica
      plan on N.7, birdoswald-roman-fort-and-the-section-of-q17650767 BORCOVACEVS) and to
      existing-or-new extras otherwise; url/thumb = the IA full page image
      https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg (the STABLE url, not
      the redirect target); n0114 ONE row tied to the new Ardoch "roman site" extras row
      (the Innerpeffery camp recorded on the row's desc); n0185 ONE row tied to the principal
      of the five P.113 forts' new "roman fort" extras row (the other four forts' names on
      desc; the choice recorded in desc + a DECISIONS entry); every row: year 1732 and the
      200 evidence field (rec "evidence/1", kind caption_coords, checked <date>,
      named_place = the plate's printed list entry, place_qid/place_label, place_lon/
      place_lat, site_lon/site_lat, dist_m - fit/evidence.py's check_caption verifies this
      OFFLINE from the stored fields: the named place appears in norm(title+desc) and the
      stored distance reproduces within 1 km and is <= 50 km).
- [ ] classified_roman.jsonl gains 17 rows classifying those (site, title) as "plan" (by
      hand).
- [ ] extras_roman.jsonl gains the new no-QID site rows the staged rows need, row shape per
      data/catalog/extras.jsonl's no-QID rows (id/name/place/lon/lat/region/kind/
      location_check{...}/source): region LOWERCASE and per-site (england for the P.113
      forts and the Hadrian's-wall forts, scotland for Ardoch and the Antonine-wall forts -
      the parent's mechanics; the old extras.jsonl capitalized regions are 211's to
      normalize), kind "roman fort" or "roman site" (207a's spec, a space), lon/lat from a
      cross-check (Wikipedia/Wikidata) recorded in location_check, no QID (220's catalog
      check: none of the seven P.113/Ardoch/Innerpeffery sites exists; the Antonine forts
      already in extras.jsonl - bar-hill-fort, inchtuthil, raedykes, rough-castle-fort - are
      REUSED, not re-created). Check how 809's join counts "every new site has its plans"
      BEFORE deciding whether all five P.113 forts get their own row (the 220 note) or only
      the principal one.
- [ ] All 17 verified site-plan leaves staged (100%, which meets 207a's moved 90% box with
      nothing missing); if any row must be dropped, the reason is recorded in a DECISIONS
      entry and appended to the Horsley section of docs/lead_roman.md (this task may touch
      that section for the accounting only - 807 wrote it, 808 runs after it).

## Notes (operational facts carried from the 207a split, 2026-10-14 iteration 221)

**Read fit/evidence.py IN FULL first** (it was only skimmed at 220): check_caption (~line
190), check_book (~265), check_book_caption (~290) - book rows re-derive books_match's
one-pair rule from the row's printed text + the current catalog row at the stored score;
only the runner-up margin stays stored. The 200 evidence contract (task 200) is what
809's --check enforces.

**Row content sources:** the staged titles/desc come from stage B's jsonl
(data/books/triage/britanniaromanao00hors.B.jsonl: 17 rows, printed titles + site_names per
page - n0114 "Innerpeffery camp." + "Ardoch camp.", n0185 the five Roman names, the wall maps
their segment fort names) and from the corrected 24-entry list (807) for the printed list
entry that is the evidence's named place. The 216 wall-map -> fort design and QID mapping is
in the DECISIONS entries 207a 216/219 (search for "castrum-segedunum"); the wall-map extras
that are NOT in the catalog (to check before creating rows: Condercum, Cilurni/Chesters,
Procolitia, Magna, Petriana, Congavata, Tunnocelum, and the Antonine forts Balmuildie,
Kirkintilloch, Falkirk-end where not already in extras.jsonl) are named in the 219
hand-over, in the git history of tasks/207a-horsley.md.

**The staging files do not exist yet on this branch** (207c's hand-over notes the *_roman.
jsonl files are created by the first book to stage; 207b may create them in parallel for the
Maclauchlan book - the same-file rule keeps 808 and 207b serial, and both books' appends are
tagged rows in the same files, so re-run --stage after any merge to stay idempotent).

**New site coordinates (cross-check, record in location_check):** Ardoch (Perthshire, near
the River Allan confluence; the P.44 plate's Ruchel/Ruchill + Knoch rivers place it), and the
P.113 five: Lanchester (Northumberland, the Cariseaux/Lanchester station), Whitley Castle
(Carlisle, the best-preserved of the five), Old Penrith (Bremenetracum, near Penrith), Old
Carlisle (Olenacum, north of the modern town), Elenborough (near Penrith, the station
"now Elenborough" per the plate). Wikipedia/Wikidata for the lon/lat cross-check; the
location_check note should say the coordinates were cross-checked against the book's map +
the web source.

**No LLM in this task and in 809's** (the replicas 8080-8082 are only needed by triage
stages, all already run). url/thumb: store the stable /download/ URL; the image is served
from archive.org on demand (remember the 302: -L for any manual download, but the ROW stores
the stable URL).

**Suite baseline at the split:** 1 failed / 156 passed / 1 skipped (the lone red = agent a's
307d placement test, known pre-existing). No test imports this module until 809; re-baseline
on the final run.

(Unblocked 2026-10-14, iteration 137, agent c, from the parent 207: same owner lift as 807
- DECISIONS 2026-10-14 207. Runs after 807.)

## Hand-over
(2026-10-14, iteration 147, agent c - RESEARCH SESSION, no code yet: every fact the build needs was verified below; next session = write --stage/--dry in fit/src_roman_horsley.py, run --dry, run --stage, commit, tick boxes. No tests were run this session; the suite baseline from the driver's loop-start note is 1 failed / 159 passed / 1 skipped (the red = agent a's 307bb placement test, known pre-existing). Working tree has docs/site_flow/307d_*.png modified (agent a's test-run jitter, NOT my files - do NOT commit them; precedent 77c2f2c restored them to main's bytes if they interfere with my commit: git checkout -- docs/site_flow/307d_*.png).

**Branch state (verified):** 807 landed (17 kind-s in HORSEY_FIGS, 24 list entries, lead section present); the three *_roman.jsonl files EXIST with 207b's rows (files_roman 1 row, classified_roman 1, extras_roman 1 = luguvallium-q71551754); B.jsonl = 17 rows. The prep note's "files may not exist" assumption was WRONG (207b landed first).

**PREP-NOTE ASSUMPTIONS THAT WERE WRONG (say so in the DECISIONS entry):** (1) "the three staging files do not exist on main" - they exist with 207b's rows. (2) "220 catalog check: NONE of the seven P.113/Ardoch/Innerpeffery sites exists" - STALE: current main's sites.jsonl holds 4 of the 5 P.113 forts (below). (3) prep's "12 new extras rows (7 Hadrian's + 3 Antonine + 1 P.113 + 1 Ardoch)" - only 7 new rows are actually needed (below). (4) prep's tag recommendation (a `book` field = IA id) - 207b landed first with the `by`: MODULE convention; follow 207b (see TAG below). Everything else in the prep note (row shapes, the offline check_caption mechanics, the stable-IA url, w/h from bookreader.json, append-only mechanics) verified correct against current main.

**THE 17 TIES (settled this session - QID ties verified in current main's data/catalog/sites.jsonl; reuses in extras.jsonl; new rows in extras_roman.jsonl). Each row: title = the HORSEY_FIGS table's printed heading for that leaf; named_place = the row's title text (it is in norm(title+desc) trivially); place_* = the tied site's own coords; site_* = same; dist_m = 0.0; place_qid = the site's QID or null; place_label = the site name; year 1732; date "1732"; wd_plan false; cat null; url = thumb = https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg; mime image/jpeg; w/h from the cached data/raw/books/britanniaromanao00hors/bookreader.json pages[n] (all 17 verified present: n0114 2400x3926, n0185 2237x3861, n0236 2427x3893, n0238 2389x3931, n0240 2488x3991, n0242 2487x3975, n0244 2487x3969, n0246 2465x3959, n0248 2498x3975, n0250 2465x3937, n0252 2492x3937, n0254 2482x3953, n0278 2405x3942, n0280 2416x4035, n0282 2427x4013, n0284 2438x3991, n0286 2471x4002):**
- n236 (N.1 general map) -> castrum-segedunum-q637958 (Q637958, SEGEDUNVM; the wall's east end, the map's subject runs SEGEDVNAVM->TVNNOCEIVM; I read the plate: ALL ~30 secondary stations labelled, NO inset fort plans -> the east-end anchor is the call; desc: the other station names B read + the legend). DECISIONS: why Segedunum over Pons Aelius.
- n238 (N.2) -> castrum-segedunum-q637958 (title from SEGEDVNAVM to CONDERCVVM; desc: Pons Aelius + Condercum per 216/B)
- n240 (N.3) -> rudchester-roman-fort-associated-civil-s-q17669775 (VINDOBALA "now Rutchester", plan; desc: Condercum)
- n242 (N.4) -> haltonchesters-roman-fort-settlement-and-q17648018 (HANNAVVM "now Halton Cheisters"; desc: Vindobala)
- n244 (N.5) -> NEW extras row cilurni (CILVRNVA "now West Chesters" = the fort at Chesters; the box's 6 QID list excludes it; no extras row exists yet; desc: Hannavum/Onnum). Region england.
- n246 (N.6) -> birdoswald-roman-fort-and-the-section-of-q17650767 (BORCOVACEVS "now Birdoswald"; desc: Cilurni, Procolitia)
- n248 (N.7) -> aesica-q4688554 (the Aesica plan, per the box; desc: Borcovaceus, Magna, Vindolana)
- n250 (N.8) -> NEW extras row petriana (Horsley's HYPOTHETICAL Solway-coast station, Cumberland coast; NOT the real Petriana=Rudchester which is the QID row above; 216: near Longhope/the Cark on the coastal map; coords from the book's map placement, location_check status "approx", region england; desc: Magna, Amboglan na)
- n252 (N.9) -> NEW extras row congavata (CONGAVATA "now Somersets" = the Castlesteads fort, Cumbria; desc: Petriana, Aballaba) region england
- n254 (N.10) -> NEW extras row tunnocelum (TVNNOCEIVM "now Bonholm", near the Esk mouth by Stanwicks; desc: Congavata, Axelodvnm) region england
- n278 (P.176 N.1 general Antonine map) -> bar-hill-fort REUSE (west end, "New Kirkpatrick" on the map; desc: Bemulie/Balmuildie, Kirkintilloch, Auchindavy, Rough-castle, Camelon, Falkirk, Cattle-cary, Wellerwood, Duntocher, Caer-ridden per B+216) region scotland
- n280 (P.176 N.2) -> bar-hill-fort REUSE (New Kilpatrick fort plan; desc: Bemulie, Duntocher)
- n282 (P.176 N.3) -> NEW extras row kirkintilloch (the Peel of Kirkintilloch, concentric plans + compass; desc: Balmuildie/Bemulie, Auchindavy, Barhill) region scotland
- n284 (P.176 N.4) -> rough-castle-fort REUSE (I read the plate: THREE inset fort plans - Cattle-cary, Rough-castle, Welterwood; "Rough castle fort" labelled twice = most named; 216's "Falkirk fort plan" reading is a MISREAD - there is no Falkirk plan, only the town label + a small wall symbol; desc: Castle-cary, Wellerwood, Falkirk) region scotland
- n286 (P.176 N.5) -> NEW extras row falkirk-end (the wall's EAST END at Falkirk down to the Forth; no fort plan on the plate - I read it; the tree-marked enclosures Caer-ridden/Kinniel are not forts; name it "Falkirk (east end of the Antonine Wall)", kind "roman site" - it is a wall end, not a verified fort; desc: Cuffabout/Cumbernauld, Caer-ridden, the Forth end) region scotland
- n0114 (P.44) -> NEW extras row ardoch (kind "roman site" - a legionary camp, not a fort; region scotland; Innerpeffery camp recorded on the row's desc per the box; the plate's two printed headings "Innerpeffery camp." (top) + "Ardoch camp." (bottom); title = "Innerpeffery camp. and Ardoch camp.").
- n0185 (P.113) -> THE P.113 PRINCIPAL QUESTION (the box says "ONE row tied to the principal of the five P.113 forts' new 'roman fort' extras row"). CURRENT MAIN CATALOG (stale-prep finding): I GLANNIBANTA = longovicium-q6674222 (Q6674222, alias 'Lanchester Roman fort', -1.7531,54.8141); II ALIONE = whitley-castle-q7996561 (Q7996561, -2.47669,54.8322, alias 'Epiacum Roman Fort' - NOT alauna-q4708853, which also aliases 'Alione' but is Maryport, a different fort); III BREMETEN RACUM = voreda-roman-fort-q17642742 (Q17642742, alias 'Old Penrith, Plumpton Wall', -2.788881,54.737902); IV OLENACUM = luguvallium-q71551754 (207b's own staged extras_roman row, Q71551754); V VIROSIDUM ("near Elenborough") = NO catalog row anywhere (verified sites/extras/extras_roman). DECISION TO RECORD IN THE BUILD (recommended): principal = VIROSIDUM (the only one of the five that needs a site row; all five have equal plan boxes I-V so the plate order does not rank them) -> NEW extras row virosidum (kind "roman fort", region england), other four forts' names on desc, desc also notes that I-IV now have catalog rows (longovicium/whitley-castle/voreda/luguvallium) so 809's join can reference them. This satisfies the box's literal "new extras row" wording AND 809's join (every new extras row has >=1 staged plan); the alternative (principal = GLANNIBANTA tied to longovicium, no new row) deviates from the box's wording. Do NOT create rows for the other four (the join fails if a new row has no plan) and do NOT create an Innerpeffery row (box: it is on Ardoch's desc). The choice MUST be recorded in the row's desc AND a DECISIONS entry (box requirement).

**NEW EXTRAS ROWS TO CREATE (7 total, all no-QID, region LOWERCASE, kind with a space, shape per 207b's luguvallium row: {id, qid: null, name, lon, lat, region, kind, aerial_ok, place, location_check{status, method, note, checked}, source, note} - note 207b's row has aerial_ok; the box's list omits it but keeping it matches the file's only existing row; source = "fit/src_roman_horsley.py"):** cilurni (Chesters Roman fort, Northumberland, england), petriana (Horsley's N.8 Solway-coast hypothetical station, Cumberland, england, status approx), congavata (Castlesteads Roman fort, Cumbria, england), tunnocelum (near Stanwix/Carlisle at the Esk mouth, england), kirkintilloch (the Peel, scotland), falkirk-end (scotland, kind "roman site"), ardoch (Perth and Kinross, scotland, kind "roman site"). COORDINATES: cross-check each against Wikipedia/Wikidata (network is allowed at BUILD time - not in --stage) and record in location_check (method "Wikipedia/Wikidata cross-checked against the book's map", checked = today); for petriana use the book's own map placement (it is a hypothetical station) with status "approx". Known modern anchors to verify: Chesters fort ~ -2.36,55.00 area; Castlesteads ~ -2.93,54.99; Stanwix ~ -3.02,54.89; Kirkintilloch ~ -3.98,55.95 (the Peel is at ~ -3.99,55.94?); Falkirk ~ -3.79,55.98; Ardoch camp ~ -3.67,56.55 near the River Allan; Virosum/Elenborough ~ near Penrith (-3.4?,55.0?) - VERIFY ALL on the web, do not guess. Slug ids with pipeline/catalog.py's catalog.slug (207b's idiom) or plain lowercase-hyphen like the existing extras rows (bar-hill-fort, rough-castle-fort have no qid suffix - follow that style: "cilurni", "petriana", "congavata", "tunnocelum", "kirkintilloch", "falkirk-end", "ardoch", "virosidum").

**TAG (the prep note's open question 1, now settled by 207b's landed rows):** 207b's rows carry "by": "fit/src_roman_maclauchlan.py" (module path) + the IA id inside desc ("Internet Archive memoirwrittendu00maclgoog, leaf n0093...") and in the page URL; extras rows carry "source": MODULE. The prep note's `book` field recommendation was OVERRULED by the landed convention - follow it exactly: files rows get "by": "fit/src_roman_horsley.py" + IA id britanniaromanao00hors in the desc ("Internet Archive britanniaromanao00hors, leaf nXXXX of the 936-leaf Google scan") and in url/thumb; extras rows get "source": "fit/src_roman_horsley.py". 809 filters by by == MODULE. Record the decision in DECISIONS.

**MECHANICS (copy 207b's stage() pattern, fit/src_roman_maclauchlan.py lines ~250-310):** stage(dry=False): build the 17 files rows + 17 classified rows (p_plan 1.0, p_birdseye 0.0, p_photo 0.0, by "hand") + up to 8 new extras rows (7 + virosidum); have_file = {(site,title)}, have_cls the same, have_site = {id} over the existing files; skip rows already present (byte-identical second run); append with open(path,"a") writing json.dumps(r, ensure_ascii=False) + "\n"; create files if absent; --dry prints instead of writing; NO network in --stage (evidence.hav_m is imported from fit/ and is offline; the coordinate cross-check is build-time research frozen into module constants). The site lon/lat for QID-tied rows is looked up at run time from data/catalog/sites.jsonl; for reused extras rows from data/catalog/extras.jsonl; for new rows from the new row's own coords. Implement --stage/--dry in the module's __main__ (it currently raises "not built yet" for them); --check/--golden stay "not built yet" (809). Keep the module top stdlib-only (lazy imports, the kip idiom). Update the module docstring's usage lines if they change. Commit plan: (1) module with the staging table + stage()/dry (run --dry under the socket-block wrapper in the same session to prove offline); (2) --stage data run (the three *_roman.jsonl files); (3) docs/lead_roman.md Horsley section accounting (17/17 staged = 100%, plus the tie decisions) + DECISIONS entries. After the data commit re-run --stage -> git diff must be empty (idempotence). Full suite after the data commit: .venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider; baseline at session start = the driver's loop-start note (1 failed / 159 passed / 1 skipped; the red = agent a's 307bb placement test, known pre-existing) - re-measure at start, don't trust the number.

**EVIDENCE FIELD per row (fit/evidence.py check_caption, verified offline from stored fields):** {"rec": "evidence/1", "kind": "caption_coords", "checked": "<date>", "named_place": <the row's title text>, "place_qid": <site QID or null>, "place_label": <site name>, "place_lon": <site lon>, "place_lat": <site lat>, "site_lon": <same>, "site_lat": <same>, "dist_m": 0.0}. check_caption needs: named non-empty; norm(named) in norm(title+desc) (true: title==named); hav_m(site,place) reproduces dist_m within 1000 m (0==0); d <= 50 km. NOTE the box says named_place = "the plate's printed list entry" - using the row's own title (the printed heading) satisfies that; for n0114 the printed entry = its two headings (title is both). Do NOT use the 207b-style short-name+Wikidata-place variant (e.g. "Carlisle"->Q192896): the box is newer and wants the list entry itself, and dist 0 is the honest distance for "the map IS the fort". 809 will run evidence.check over files rows via check_commons -> check_caption (catalog NOT consulted), so this shape passes.

**STILL TO VERIFY AT BUILD TIME (small):** (a) the exact desc strings - mine are drafted above from B.jsonl's site_names (data/books/triage/britanniaromanao00hors.B.jsonl: n238 [CONDERCVM,SEGEDVNVM], n240 [CONDERCVVM,VINDOBALA,'now Benwel hill','now Rutchester'], n242 [HVNVM,VINDOBALA,Halden Lough], n244 [CILVRNVM,HVNNVM,Corbridge,Tine], n246 [BORCOVICVS,CILVRNVM,PROCOLITIA], n248 [AESICA,MAGNA,VINDOLANA], n250 [AMBOGLANNA,PETRIANA], n252 [PETRIANA,CONGAVATA,ABALLABA], n254 [TVNNOCEIVM,CONGAVATA,AXELODVNM,Stanwicks], n278 [Barhill fort,Bemulie,Kirkintilloch,Rough-castle fort,Camelon,Falkirk,Castle-cary fort,...], n280 [New Kirkpatrick fort,Duntocher fort,Bemulie], n282 [Peel of Kinkintilloch,Bemulie fort,Auchindavy fort,Barhull fort], n284 [Cattle-cary fort,Rough castle fort(=B's 'Rounthall'),Welterwood fort], n286 [Falkirk,Caer-ridden,...], n185 [GLANNIBANTA/Lanchester,ALIONE/Whitley castle,BREMETENRACUM/'Old Penreth'(B's spelling - the table keeps 'Penrith'),OLENACUM/Old Carlisle,VIROSIDUM/Elenborough], n114 [Innerpeffery camp.,Ardoch camp.]); (b) the web coordinate cross-checks listed above; (c) that pipeline/catalog.py's slug() exists as 207b uses it (or just use plain ids). The full-size plates are in /tmp/horsley_full/ (n0236/n0278/n0284/n0286 read this session; n0236 must be rotated CW - it is a landscape sheet in portrait capture); if /tmp is gone, triage images data/raw/books/britanniaromanao00hors/triage/*.jpg (1400 px) still exist.
