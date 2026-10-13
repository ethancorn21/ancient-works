Status: done
# 306e: Look at the orphan agent fits, UK part 2 (o-y) - 17 docs, 13 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306e.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 17
UK platefit documents with `by: agent` (sites o-y) that are ORPHANS - in the store, but no
overlay built on the site and not referenced by any review item, so a visitor sees them not at
all. Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`, with the doc's stored
pairs placed. The verdict records where the doc stands today (invisible) and whether the
placement is good enough to keep.

## Acceptance criteria
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [x] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real banks, walls, ditches,
      streets) and the verdict (keeps its document / deleted - and it is an orphan today,
      invisible on the page).
- [x] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [x] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (17, 13 sites)
- offa-s-dyke-q1127343.c_1cca85e7b4b5a89e - OS 1902 Nantcribba 02
- okehampton-castle-q1419982.c_0edd7f87db67ff20 - Plan of Okehampton Castle
- old-sarum-q782719.c_041083ec68b532f8 - Ancient Plan of Old Sarum
- old-sarum-q782719.c_ff62c9585a92b375 - Plan & elevations of Old Sarum (DPLA)
- oxford-castle-q2600886.c_ba6b308580428184 - Oxford Castle, plan from Mackenzie, The Castles of England (1897)
- pilsbury-castle-q7194511.c_7ff765c177ca7bae - Pilsbury Castle plan
- pontefract-castle-q1949590.c_3213330a52fe6018 - The history of the ancient borough of Pontefract (14739695456)
- pontefract-castle-q1949590.c_d135fb32326df430 - The history of the ancient borough of Pontefract (14762763065)
- portus-adurni-q762664.c_42bedb90fffce1d4 - Portchester Castle, derived from the Penny Cyclopaedia (1836) v6 p 354
- portus-adurni-q762664.c_4912bb54aa79f3ea - Burg von Portchester, Penny Cyclopaedia 1836 p 354
- raby-castle-q4583646.c_fe1d6c7f0ba858cb - Raby Castle, plan from Mackenzie, The Castles of England (1897)
- richborough-roman-fort-q1309736.c_edad7da41d234534 - Richborough Castle, derived from the Penny Cyclopaedia (1836) v6 p 353
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 - Penny Magazine 1836: plan of the druidical temple at Stanton Drew
- taunton-castle-q7688781.c_05cb4a02bd58e82e - Taunton Castle, plan from Mackenzie, The Castles of England (1897)
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 - WINDMILL SITES, LEWES DOWN (Allcroft 1908)
- york-castle-q80637.c_8dac5aacd73916b8 - York Castle in 1820
- york-castle-q80637.c_a7db545536f13e24 - Plan of Center, Broome County 1855 (Gifford Wenig)


## Hand-over
(2026-10-13, iteration 198, agent c - **197's merge is COMMITTED (6554a14) and the post-merge
suite = baseline (154 passed, 1 skipped, 1 failed = only 307bb's gesture red, log
/tmp/aw306e_suite198.log). MAJOR STATE CHANGE discovered: main's 6ce742f ("[driver]
uncommitted work after iteration 227" = a snapshot of agent a's 212b live-sync work, on main
after my 197 merge-base 0685a4c, came in WITH the 197 merge) DELETED 71 platefit docs = ALL
68 orphans (306c/d/e/f) + 3 306a wrong fits - so ALL 17 of my 306e docs are GONE from the
store now, including my 4 KEEPS (offa c_1cca, okehampton c_0edd, pilsbury c_7ff7, pontefract
c_3213) and the 3 I had not yet judged. All 17 plans still exist as candidates in their site
item files: the 10 deleted carry my 197-union full audit entry (place_reason + 212b's
why/gate_score); the 4 KEEPS and the 3 remaining carry ONLY 212b-style entries
(why='line check: fabricated anchor pattern...', gate_score, evidence, no place_reason,
no coarse key). All those items are unresolved (no candidate doc exists anymore).
**NEXT session (one step = finish the last 2 sites, then the task is DONE):**
1. Read the 3 composites I built (scripts /tmp/aw306e_final3.py, /tmp/aw306e_fit.py alive):
   /tmp/_n0558_2.{1842,plate,relief}.png, /tmp/_c_8dac5aacd73916b8.{...}.png,
   /tmp/_c_a7db545536f13e24.{...}.png (800-px site box, 100 m grid + rings; 1842 red,
   plate blue warped by the replicated fit, relief grey; doc JSONs restored to
   /tmp/aw306e_doc3_*.json from 6554a14^1). Confirm the placement facts below.
2. Verdicts (from the committed shots + fit replication + sites.json):
   - **windmill-hill n0558_2 = DELETED (wrong place, wrong kind)**. Site = Windmill Hill,
     Avebury, WILTS (Neolithic causewayed enclosure, largest in Britain; site point
     -1.876219/51.441531 per sites.json; 1842 labels the real hill 'Windmill Hill'). The
     plate is Allcroft 1908 'WINDMILL SITES, LEWES DOWN' = a conical hachured hill with a
     ring of ~6 barrow mounds - Lewes Down is EAST SUSSEX, a toponymic collision. Fit:
     1.0000 m/px, 0.0 deg, all 6 residuals 0.0 (the 6 anchors are the grid box
     (2000,2000)..(2800,2800) + (2400,2900) + (1900,2400); site point -> page (2399.5,
     2399.5) = the box centre - no placement info). On the shots the plate sits ~one
     hill-width W-NW of the real hill (open downland/fields); the drawn barrow-hill does
     not match the real causewayed enclosure.
   - **york-castle c_8dac5aacd73916b8 'York Castle in 1820' = KEEP in the item (owner's
call flag)**. Genuine 1820 watercolour (Wikimedia, 'From a 1820 watercolour by Mr Waud',
     public domain) - a PERSPECTIVE view ('View, drawn at an angle' tab) of THIS castle:
     Clifford's Tower on its conical motte, the 1820 curtain walls, the Foss lower-left,
     the city behind. Fit 1.0507 m/px +7.03 deg, res 42.9/16.3/40.9/22.6 (gate 31.7 =
     fabricated grid anchors, 4-point perspective fits are unverifiable by construction);
     site point -> page (412.9, 91.5) = top of the drawn tower (anchor 2 (400,100) ->
     site point). The surviving tower/moat ring (visible on the modern aerial) sits ~300 m
     N of the catalog point (Clifford's Tower ~53.9585/-1.0806 vs site 53.9558/-1.08) -
     the drawn complex inherits the site's catalog offset, like taunton's 640 m but the
     picture is of the right site. Verdict line: right site, right kind, view placed at
     the site point; 212b deleted the doc as a pattern doc - the item holds it with this
     audit note; the KEEP-vs-gate conflict is FLAGGED (task 807 below), do NOT
     unilaterally restore the doc file (it is gone on main; re-adding would fight the
     212b pipeline and the next main merge).
   - **york-castle c_a7db545536f13e24 'Plan of Center, Broome County 1855' (Gifford Wenig)
     = DELETED (wrong place, toponymic collision)**. The plate is a street plan of the
     VILLAGE OF CENTER, BROOME COUNTY, NEW YORK (the item entry's evidence conflict block
     says named_place Broome County Q47894 at -75.888/42.137 NY): 'PLAN of CENTER', Store
     St / Main St / Elm St, the SUNBURY R. creek, named houses. Fit 0.9742 m/px +0.38 deg,
     res 36.1/11/11/16.1. The drawn street grid sits on the 1842 dense old-town fabric of
     York with no matching streets; the SUNBURY R. band does not land on the Foss.
3. EXECUTE the 303 way for all 3 (docs are ALREADY deleted by 6ce742f - skip os.remove):
   fit/review.py, pattern /tmp/aw306e_texec.py (alive): entry = {plan, title (the doc's
   title - restored JSONs in /tmp/aw306e_doc3_*.json; for commons assert
   fr._sha16(title-with-'File:'-if-applicable) == plan; windmill is a BOOKS doc: title
   as-is 'WINDMILL SITES, LEWES DOWN', url the item's 'books/earthworkenglan01allcgoog/
   n0558.jpg' like its sibling entries, evidence = fr.candidate_evidence(plan) (books row;
   the 212b entries show kind 'none' for books - accept non-None as the existing n0557_1/
   n0558_1 entries prove books kind-none entries are stored), pairs (the doc's own),
   coarse False, label, cite, ref, size (commons docs: the restored JSON's size; windmill:
   the crop box [1886,1919,2862,2929] -> size [976,1010] or leave as the item's twin
   n0558_1 does), place_reason '306e audit 2026-10-13: <verdict above>. Document deleted.'
   (for c_8dac: '... right site, right kind, perspective view unverifiable; 212b sync
   deleted the doc as a pattern document - kept in the item, owner's call.')
   fr.upsert_item REPLACES an existing plan's entry in place (same plan present: n0558_2
   in windmill-hill-...n0557_1.json; c_8dac and c_a7db in york-castle-...
c_81ecab4a9284f156.json) - lead and file name stay. NO new items. Then fr.export(fr.ROOT,
   site) scoped per site (windmill-hill-q4348373, york-castle-q80637). Export counts:
   baseline 365 open of 377; in-place entry replacement of plans already in OPEN items
   leaves BOTH counts unchanged (items stay open - no doc exists to resolve them).
   git status must show only: M windmill item, M york item, M web/data/review.json.
4. Write the LAST 3 lines into the 306e block of docs/site_flow.md (after the taunton
   line, before '## The site markers become arrowheads (task 308, 2026-10-13)') in the
   established shape (doc id - source (similarity, N pts, resid, m/px, rot): what the
   lines sit on - verdict). ALSO update my 4 stale KEEPS lines (offa, okehampton, pilsbury,
   pontefract c_3213) with a one-sentence postscript each: 'Post-212b: the 212b live sync
   (main 6ce742f, 2026-10-13) deleted this doc as a fabricated-anchor-pattern document -
   the review item keeps it with the audit entry; flagged in task 807.' (the 306e block
   header at line ~1268 - the 4 lines are at ~1278-1340; re-read before editing; touch
   ONLY my 306e block, not 306a/b/c/d/f or 308+).
5. Create task **tasks/807-306e-keeps-vs-212b-pattern-deletion.md** (Status: open, Depends
   on: none - it is a question for the human, Touches: data/db/platefits/ data/review/
   web/data/review.json): the 5 docs the 306e visual audit endorsed (offa, okehampton,
   pilsbury, pontefract c_3213, york c_8dac) were deleted by the 212b sync on the
   fabricated-anchor-pattern rule, which for 4-point perspective views and grid-anchored
   plates cannot see that the drawn works sit on the real works. Ask the human to
   adjudicate: restore those 5 docs (recoverable from git, e.g. 6554a14^1:data/db/
   platefits/<doc>.json) or keep the 212b deletion as the line's word. My
   recommendation: keep the 212b deletion (the gate is the documented last line; the
   pictures are preserved in the review items with the audit reasons) unless the owner
   wants a specific one back.
6. TICK boxes 2 and 3 (box 1 was already ticked, box 4 holds: no by:hand doc touched -
   n0557_1/n0558_1 stay as-is; suite = baseline at this session's run - re-run the full
   suite after the upserts before ticking box 4: expect 154/1/1 again; the export touches
   only the 2 scoped page entries). Set Status: done when all 4 boxes are ticked.
7. DECISIONS.md: one entry for this state change + the verdicts + the execution.

**Facts for the road:** 6ce742f full deletion list saved at /tmp/aw306e_6ce_deletions.txt
(71 files). The merge (6554a14) is committed; 41bd4de = my 197 journal. The 197 union's
work stands (web/data/review.json = 365 open of 377). windmill-hill item file =
data/review/windmill-hill-q4348373.earthworkenglan01allcgoog_n0557_1.json (holds
n0557_1 lead + n0558_1 + n0558_2[212b: gate 0.0, ev none, 6 grid pairs]); york item =
data/review/york-castle-q80637.c_81ecab4a9284f156.json (7 candidates: c_81ecab4a9284f156
[coarse, ev category], c_b3c056e395d2525d [Castle Creek Broome NY, ev none+conflict],
c_2f24e4f6aa92cb05 [same sheet, gate 86.3], c_be6959b4a59afb6f [RidsdalePanorma, gate
48.7], c_c9a0d376a2f0777d ['York in the XVth century'], c_8dac [gate 31.7, ev category],
c_a7db [gate 13.6, ev none+conflict]); pontefract item = c_ba5dfa2d2dbc645e.json (9
candidates incl my c_d135 audit + 212b's c_3213). offa/okehampton/pilsbury items =
named after their plan, sole candidate = the 212b entry. Composites + fit outputs from
step 1 of this session are in /tmp (fit replication: windmill res all 0.0 @ 1.0000 m/px;
c_8dac 42.9/16.3/40.9/22.6 @ 1.0507 m/px +7.03 deg, site point -> page (412.9, 91.5);
c_a7db 36.1/11/11/16.1 @ 0.9742 m/px +0.38 deg, site point -> page (298.3, 384.9)).

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed** (last run: 198, 307 s, /tmp/aw306e_suite198.log). The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's
in-flight 307). Any other failure = my new red.

**State of the 17 docs (o-y) AFTER 6ce742f:** all 17 doc files GONE (deleted on main by
the 212b sync; my 10 earlier deletions = same fate, consistent). My audit verdicts: offa
KEEPS (181), okehampton KEEPS (181), old-sarum x2 DELETED (183), oxford DELETED (184/185),
pilsbury KEEPS (187), pontefract c_3213 KEEPS (188), pontefract c_d135 DELETED (188),
portus x2 DELETED (190/191), raby DELETED (192), richborough DELETED (193), stanton-drew
DELETED (194), taunton DELETED (judged 195, executed 196) - and now judged 198:
windmill-hill n0558_2 DELETED (wrong place + wrong kind), york c_8dac KEEP in item
(right-site view, owner's call), york c_a7db DELETED (toponymic collision).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2: 14 of 17 lines; the last 3
are written in next step 4 (+ the 4 KEEPS postscripts). Box 3: the 10 earlier deletions
executed in 183-196; the 3 remaining are executed in next step 3 (doc deletion part was
done by 6ce742f; I complete upsert + scoped export). Box 4: no by:hand doc touched;
suite = baseline at the 198 run - re-run after the upserts before ticking.)

**What 197 did (the merge, start-of-prompt order of operations):**
1. `git merge main` -> 26 conflicts: 25 in data/review/*.json + web/data/review.json.
   Merge base = 0685a4c (the 190 main merge). main's 33 commits = agent a's 212b (final
   live sync: sent 76 pattern docs to review items as COARSE entries {plan,title,url,pairs,
   why:'line check: fabricated anchor pattern...',evidence,gate_score}, created 31 NEW item
   files, deleted none; left all `resolved` records in place). My side's 195 commits =
   306c/306d/306e work (upserts of FULL entries {plan,title(File: prefix),url,pairs,coarse,
   evidence,label,cite,ref,size,place_reason}).
2. Every conflict had ONE uniform shape: both sides added/kept the SAME plan; my entry had
   place_reason+audit fields, main's had why+gate_score (same url/pairs/evidence). Resolved
   all 25 with a union script (inline heredoc, NOT saved - but the result is staged and
   verified, the script is not needed): merged entry = my entry + their extra keys
   (why/gate_score; plus their `evidence` for 3 book docs where mine had none: hodgen
   n0092_1, marietta n0195_1, serpent n0313_1). Kept MY `title` where the 7 306e commons
   docs differed (mine = 'File:...' source title, the one whose _sha16 == plan; theirs =
   the doc's own title - fit/cover.py derives the raw image path from _sha16(title), and my
   306e items all use the File: convention, so mine wins). Order = my order, then
   theirs-only plans (2: hodgen b24849959_n0353_1, pontefract c_3213330a52fe6018 - kept
   verbatim; c_3213 is my 306e KEEP doc whose store doc still exists, so the pontefract item
   now RESOLVES via it - the export confirmed it out of the open list; that is the module's
   own derivation of the union, both sides' entries remain visible in the item file).
   Wrote via fr._save_json (indent=1, no trailing newline - the module convention).
3. web/data/review.json: ran a FULL `fr.export(fr.ROOT)` over the union item set ->
   365 open of 377 (== main's count). Verified: the export changed NO item files (212b left
   all `resolved` records); per-site the merged page file differs from both parents only in
   `candidates`, and is a strict superset of both sides' candidate plans (0 plans lost, 0
   extra at page and item level). Page-level census: base 333 open, ours 347, theirs 365,
   merged 365; 43 sites both-changed, 12 theirs-only re-stamps, 310 unchanged, 18
   theirs-only new sites (212b's new items incl. my 306e KEEPs offa/okehampton/pilsbury and
   the 306a on-map sites - all fine: open review items, docs untouched by me).
   Item-file census (json only): base 346, ours 360 (= 346 + my 14 created items, 0 deleted),
   main 377 (= 346 + 31 created, 0 deleted), merged = main's 377 exactly (my 14 all
   conflicted add/add with main's 31 and are the union-resolved files). Staged in the merge:
   17 A (main's item files I lacked), 43 D (MY platefits doc deletions: 306a/c/d/e -
   unchanged), 45 M (25 resolved items + review.json + main's other auto-merges: DECISIONS.md,
   DECISIONS-archive.md, web/data files, docs). data/review/README.md present.
4. Suite NOT yet run this session (context limit) - that is next session step 1, THEN
   `git commit` the merge (MERGE_HEAD is in place; the commit finishes it).

**Backups left in /tmp:** /tmp/aw306e_pre_export/review (all item files as merged, BEFORE the
export) and /tmp/aw306e_pre_export/review.json (both parents' conflicted page file was git-
staged; the stages :1:/:2:/:3: of every conflicted file are still in the index until the
merge commit - after the commit they are only reachable via the merge-base/parents, and are
all recorded here if ever needed).

**Unchanged since 196 - the audit state of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e
KEEPS (181); okehampton-castle c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375
DELETED (183); old-sarum c_041083ec68b532f8 DELETED (183); oxford-castle
c_ba6b308580428184 DELETED (184/185); pilsbury-castle c_7ff765c177ca7bae KEEPS (187);
pontefract-castle c_3213330a52fe6018 KEEPS (188); pontefract-castle
c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4 DELETED (190);
portus-adurni c_4912bb54aa79f3ea DELETED (191); raby-castle c_fe1d6c7f0ba858cb DELETED
(192); richborough-roman-fort c_edad7da41d234534 DELETED (193); stanton-drew
c_59a5c636a9e00703 DELETED (194); taunton-castle c_05cb4a02bd58e82e DELETED (judged 195,
EXECUTED 196). **3 docs (2 sites) remain:** windmill-hill-q4348373.
earthworkenglan01allcgoog_n0558_2, york-castle x2.

**Baseline for the post-merge suite run:** my last run (196, before this merge) = 154 passed,
1 skipped, 1 failed (only tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_
browser = agent a's 307bb, the known pre-existing red). Main's 212b lead also reported the
suite green at 212b done (154 passed, only the 307bb gesture red). The merged world is not
identical to either parent (item census 377/365 vs my 360/347 vs main 377/365 - main's page
count matches the merged one, but main's item set differs from mine by my 14 union-resolved
entries): expect the same 154/1/1; if a test that passed in BOTH parents now fails, it is a
merge consequence (first suspects: tests/test_cover.py union/open-count expectations, tests
that pin specific item content like the yearless-title test 212b re-pinned to watson-brake
c_5e7bb19c) - classify, fix the test or data as the cause demands, re-run, then commit.

**NEXT STEP (session 198) - the LAST 2 sites (3 docs), then the task is DONE (after the
merge commit above):**
1. **windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2** (Allcroft 1908,
   'WINDMILL SITES, LEWES DOWN'; model None - the page's default plan model fits it;
   6 stored pairs, url None = a BOOKS doc, so its row is data/books/index.jsonl by id
   n0558_2, not files.jsonl). The site's item already holds [n0557_1, n0558_1]
   (data/review/windmill-hill-q4348373.earthworkenglan01allcgoog_n0557_1.json, lead
   n0557_1, open, no_picture_found None): if DELETED, APPEND the entry to THAT item
   (lead/file name stay), do NOT create a second item. Judged on the committed shots
   (docs/site_flow/agent_fits/windmill-hill-..._n0558_2.png + _relief.png) + the LAYERS
   composite recipe below. NOTE post-merge: this item file is one of the 377 main-set
   files - its merged content is main's as-is (no conflict); re-read it before upserting.
2. **york-castle-q80637 c_8dac5aacd73916b8** ('York Castle in 1820' watercolour, score
   31.7) + **c_a7db545536f13e24** ('Plan of Center, Broome County 1855' (Gifford Wenig) =
   Center is a TOWN in Broome County, NEW YORK - toponymic-collision class, almost
   certainly DELETED wrong place). Existing item (c_81ecab4a9284f156 + 4 more, open)
   -> append. Check each doc's files.jsonl row for evidence before upserting (assert
   candidate_evidence non-None).
3. After all 17 lines are in: TICK box 2; box 3 is complete when the york/windmill
   verdicts are executed; then tick box 3 (box 4 already holds: no `by: hand` doc
   touched). Set the task `Status: done` (all 4 boxes).

**The 303 way (summary; full recipe in the 189-196 DECISIONS entries):**
fit/review.py API, no hand-edited JSON. entry = {plan, title (the source row title
WITH its 'File:' prefix for commons / as-is for books; fr._sha16(title) asserted ==
plan), url (for a commons doc: doc["url"] = media/commons/<site>/<plan-without-c_>.jpg
repo-relative, the pattern of all 306e items; for a books doc: check what the existing
book-doc items use), pairs (the doc's own), coarse False, evidence (fr.candidate_
evidence(plan) - returns None if the row is missing/unevidenced; assert non-None;
kind category OR hand_tied), label, cite, ref, size, place_reason '306e audit
2026-10-13: ... Document deleted.'}; fr.upsert_item(fr.ROOT, site, [entry]) - new
plans APPEND, the lead/file name stay (an item with this plan already present gets
the entry replaced in place); a site with no item gets CREATED (lead = the one
candidate); then os.remove the doc; then fr.export(fr.ROOT, site) (scoped; keeps
other branches' re-stamps - see PITFALLS under tools/site_done.py, fit/review.py).
**upsert_item returns an ABSOLUTE path** - assert the basename. An item with no
candidate docs stays open (resolved None; the site stays covered for the union
check). Export counts post-merge: baseline is now 365 open of 377 (the 212b union);
a NEW item adds one to BOTH counts; an APPEND leaves both unchanged.
**Post-merge gotcha:** some of my 306e item files (e.g. old-sarum, pontefract) now carry
BOTH my place_reason entry AND 212b's why/gate_score on the same candidate - that is
the intended union, not a bug.

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs
(/tmp/aw306e_fit.py still alive); inverse-map the site point; build the 800 m box
LAYERS composite (/tmp/aw306e_layers.py, output name = d[-17:], /tmp/_<plan-suffix>.
{1842,plate,relief}.png) - 1842 six-inch-1st_ink.webp red-on-white, plate
luminance-ink mask (lo 118 / hi 200) blue-on-white via atv + bilinear, relief grey;
100 m grid + 100-500 m circles centred on the site point; raw jpgs at
data/raw/commons/<site>/<plan-without-c_>.jpg are exactly the doc's sizes (books:
data/books/full/...); for a DENSE/hatched plate read the composite/screenshots, not
an ink histogram (182 PITFALLS); for stone-scale works the relief's dark dots decide
(194 PITFALLS); for a whole-complex displacement the repo 1842 webp may not even
cover the real works - then modern Esri aerial (VM has internet; z18 tile math: x =
((lon+180)/360)*2^z, y = (1 - asinh(tan(lat_rad))/pi)/2*2^z - 195 DECISIONS gotcha,
0.376 m/px at 51 N) and the web are the deciding layers. The committed shots
(docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp
was wiped. KEEPS -> line only. DELETED -> the 303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 14 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2, raby,
richborough, stanton-drew, taunton - between the 306d block and '## The site markers
become arrowheads (task 308, 2026-10-13)') - continue it after the taunton line. DONE
sites (do not touch again): offa (KEEP), okehampton (KEEP), old-sarum (item holds
both), oxford (new item), pilsbury (KEEP), pontefract (item holds the c_d135 append
- and post-merge also 212b's c_3213, which resolves the item, so the site is no
longer on the review page but IS covered for the union check), portus (item holds both
portus candidates), raby (new open item, lead c_fe1d6c7f0ba858cb), richborough (item
now holds [c_1dcd5a7171573663, c_edad7da41d234534]), stanton-drew (new open item, lead
c_59a5c636a9e00703), taunton (new open item, lead c_05cb4a02bd58e82e, created 196).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 14 of 17
lines; tick when all 17 are in. Box 3 PARTIAL: 10 deletions executed (old-sarum x2,
ox ford, pontefract c_d135, portus x2, raby, richborough, stanton-drew, taunton);
the rest awaits the final 2 sites' verdicts (york x2 = two docs; windmill-hill x1).
Box 4 satisfied so far (no `by: hand` doc touched; suite = baseline at the 196 run).)

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed** (last run: 196, 309 s). The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's
in-flight 307). Expect exactly that in every run; any other failure = my new red.

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181);
okehampton-castle c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED
(183); old-sarum c_041083ec68b532f8 DELETED (183); oxford-castle
c_ba6b308580428184 DELETED (184/185); pilsbury-castle c_7ff765c177ca7bae KEEPS (187);
pontefract-castle c_3213330a52fe6018 KEEPS (188); pontefract-castle
c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4 DELETED (190);
portus-adurni c_4912bb54aa79f3ea DELETED (191); raby-castle c_fe1d6c7f0ba858cb DELETED
(192); richborough-roman-fort c_edad7da41d234534 DELETED (193); stanton-drew
c_59a5c636a9e00703 DELETED (194); taunton-castle c_05cb4a02bd58e82e DELETED (judged 195,
EXECUTED 196). **3 docs (2 sites) remain after taunton:**
windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2, york-castle x2.

**What 196 did (executed taunton the 303 way; the 195 hand-over's NEXT STEP 1-7, steps
1-6 done, step 7 = next session):**
1. Preconditions re-checked LIVE: fr._find_item = (None, None) (no item);
   fr.candidate_evidence = the hand_tied row (files.jsonl line 1457, kind hand_tied,
   source 'pipeline/sources.py mackenzie'); fr._sha16('File:Plan of Taunton Castle
   (1897).jpg') == plan. Export baseline (346, 359) confirmed by counting 359 item
   files on disk + 346 open page entries.
2. Script /tmp/aw306e_texec.py (pattern /tmp/aw306e_stexec.py, both still alive):
   entry = {plan, title, url = doc["url"] = media/commons/taunton-castle-q7688781/
   05cb4a02bd58e82e.jpg (REPO-RELATIVE - consistent with all 8 previously created 306e
   items; the 195 'use the row's url verbatim' note is loose, the page must serve the
   image so the local path is the right url), pairs (the doc's 4), coarse False,
   evidence (the row's), label '1897', cite+ref (the doc's), size [1280,1461],
   place_reason '306e audit 2026-10-13: ... Wrong place, right kind. Document
   deleted.'}. fr.upsert_item (returns an ABSOLUTE path) CREATED
   data/review/taunton-castle-q7688781.c_05cb4a02bd58e82e.json (lead = this plan, sole
   candidate); os.remove the doc; fr.export(fr.ROOT, site) -> (347, 360) exactly as
   predicted (a NEW open item adds one to both counts).
3. Verified: item = [c_05cb4a02bd58e82e], resolved None, no_picture_found None; page
   entry under name 'Taunton Castle' (sites.json). git status = exactly 3 files (D
   doc, M web/data/review.json, ?? item) - no other site's item touched.
4. 14th of 17 lines written into the 306e block of docs/site_flow.md (after the
   stanton-drew line, before '## The site markers become arrowheads (task 308,
   2026-10-13)'), same shape as the raby/oxford/portus lines.
5. Suite: 154/1/1 = baseline.

**NEXT STEP (session 197) - the LAST 2 sites (3 docs), then the task is DONE:**
1. **windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2** (Allcroft 1908,
   'WINDMILL SITES, LEWES DOWN'; model None - the page's default plan model fits it;
   6 stored pairs, url None = a BOOKS doc, so its row is data/books/index.jsonl by id
   n0558_2, not files.jsonl). The site's item already holds [n0557_1, n0558_1]
   (data/review/windmill-hill-q4348373.earthworkenglan01allcgoog_n0557_1.json, lead
   n0557_1, open, no_picture_found None): if DELETED, APPEND the entry to THAT item
   (lead/file name stay), do NOT create a second item. Judged on the committed shots
   (docs/site_flow/agent_fits/windmill-hill-..._n0558_2.png + _relief.png) + the LAYERS
   composite recipe below.
2. **york-castle-q80637 c_8dac5aacd73916b8** ('York Castle in 1820' watercolour, score
   31.7) + **c_a7db545536f13e24** ('Plan of Center, Broome County 1855' (Gifford Wenig)
   = Center is a TOWN in Broome County, NEW YORK - toponymic-collision class, almost
   certainly DELETED wrong place). Existing item (c_81ecab4a9284f156 + 4 more, open)
   -> append. Check each doc's files.jsonl row for evidence before upserting (assert
   candidate_evidence non-None).
3. After all 17 lines are in: TICK box 2; box 3 is complete when the york/windmill
   verdicts are executed; then tick box 3 (box 4 already holds: no `by: hand` doc
   touched). Set the task `Status: done` (all 4 boxes).
4. Full suite each session (expect 154/1/1 = baseline).

**The 303 way (summary; full recipe in the 189-196 DECISIONS entries):**
fit/review.py API, no hand-edited JSON. entry = {plan, title (the source row title
WITH its 'File:' prefix for commons / as-is for books; fr._sha16(title) asserted ==
plan), url (for a commons doc: doc["url"] = media/commons/<site>/<plan-without-c_>.jpg
repo-relative, the pattern of all 306e items; for a books doc: check what the existing
book-doc items use), pairs (the doc's own), coarse False, evidence (fr.candidate_
evidence(plan) - returns None if the row is missing/unevidenced; assert non-None;
kind category OR hand_tied), label, cite, ref, size, place_reason '306e audit
2026-10-13: ... Document deleted.'}; fr.upsert_item(fr.ROOT, site, [entry]) - new
plans APPEND, the lead/file name stay (an item with this plan already present gets
the entry replaced in place); a site with no item gets CREATED (lead = the one
candidate); then os.remove the doc; then fr.export(fr.ROOT, site) (scoped; keeps
other branches' re-stamps - see PITFALLS under tools/site_done.py, fit/review.py).
**upsert_item returns an ABSOLUTE path** - assert the basename. An item with no
candidate docs stays open (resolved None; the site stays covered for the union
check). Export counts: a NEW item adds one to BOTH open and total (194: (345,358) ->
(346,359); 196: (346,359) -> (347,360)); an APPEND leaves both unchanged (191, 193).

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs
(/tmp/aw306e_fit.py still alive); inverse-map the site point; build the 800 m box
LAYERS composite (/tmp/aw306e_layers.py, output name = d[-17:], /tmp/_<plan-suffix>.
{1842,plate,relief}.png) - 1842 six-inch-1st_ink.webp red-on-white, plate
luminance-ink mask (lo 118 / hi 200) blue-on-white via atv + bilinear, relief grey;
100 m grid + 100-500 m circles centred on the site point; raw jpgs at
data/raw/commons/<site>/<plan-without-c_>.jpg are exactly the doc's sizes (books:
data/books/full/...); for a DENSE/hatched plate read the composite/screenshots, not
an ink histogram (182 PITFALLS); for stone-scale works the relief's dark dots decide
(194 PITFALLS); for a whole-complex displacement the repo 1842 webp may not even
cover the real works - then modern Esri aerial (VM has internet; z18 tile math: x =
((lon+180)/360)*2^z, y = (1 - asinh(tan(lat_rad))/pi)/2*2^z - 195 DECISIONS gotcha,
0.376 m/px at 51 N) and the web are the deciding layers. The committed shots
(docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp
was wiped. KEEPS -> line only. DELETED -> the 303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 14 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2, raby,
richborough, stanton-drew, taunton - between the 306d block and '## The site markers
become arrowheads (task 308, 2026-10-13)') - continue it after the taunton line. DONE
sites (do not touch again): offa (KEEP), okehampton (KEEP), old-sarum (item holds
both), oxford (new item), pilsbury (KEEP), pontefract (item holds the c_d135
append), portus (item holds both portus candidates), raby (new open item, lead
c_fe1d6c7f0ba858cb), richborough (item now holds [c_1dcd5a7171573663,
c_edad7da41d234534]), stanton-drew (new open item, lead c_59a5c636a9e00703), taunton
(new open item, lead c_05cb4a02bd58e82e, created 196).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 14 of 17
lines; tick when all 17 are in. Box 3 PARTIAL: 10 deletions executed (old-sarum x2,
oxford, pontefract c_d135, portus x2, raby, richborough, stanton-drew, taunton);
the rest awaits the final 2 sites' verdicts (york x2 = two docs; windmill-hill x1).
Box 4 satisfied so far (no `by: hand` doc touched; suite = baseline at the 196 run).

## Lead close (2026-10-13)
Superseded: the 212b sync took every remaining batch-model (by: agent, vision-model) doc in this list off the map through the line check; the only docs left under these ids are matcher re-fits (fitter: matcher) the lead eye-checked on the six-inch map / relief (Old Sarum, Portchester x2, Gouda). Nothing left to audit.
