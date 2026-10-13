Status: open
# 212a: Cover search - a targeted picture search for every uncovered site, "no picture found" items
Depends on: 211
Touches: fit/cover.py, fit/cover_qwen8080.py, data/cover/ (searches.json + the run log + the stage record), data/review/, data/commons/files.jsonl, data/commons/classified.jsonl, data/raw/commons/, web/data/plans.json, web/data/fit_queue.json, tests/test_cover.py

## Goal
For every built site with no fit document and no plan candidate in web/data/plans.json:
one targeted search (the site's QID Commons category, P180 depicts, a title search),
recorded. A found picture is staged the normal way (files.jsonl + classified.jsonl with
the 200 evidence field, a local copy under data/raw/commons/, its row in plans.json via
tools/export_plans.py). A site where nothing is found gets a review item marked
"no picture found" with exactly what was searched. The fit itself is NOT this task: the
lead runs fit/matchfit.py + tools/site_done.py over the found pictures afterwards (lead
note ef84a05 - the matcher is the fit, never the vision-model fit).

## Acceptance criteria
- [x] fit/cover.py search: lists the uncovered sites (no platefit doc, no plans.json row),
      searches each, writes found pictures into the canonical files and a local copy,
      re-exports plans.json; prints counts (searched / found / nothing).
- [x] fit/cover.py nothing-found: a review item per site, marked "no picture found",
      listing the queries and the date.
- [x] tests/test_cover.py (no network: a recorded fake search response, sockets dead):
      one site with a hit gets staged rows + a plans row; one site without gets the
      review item with its queries.
- [ ] Run it for real once and commit the results.

## Notes
- Commit working code every session. Notes-only sessions end the job (212 ended that way).

## Hand-over

(2026-10-13, iteration 221, agent a - the live SEARCH phase ran and is committed;
the STAGE phase is blocked on a human classifier decision - ask_human filed
as request 003 (.agent/asks/003.md, blocking) and THIS TASK NOW WAITS ON IT;
when the answer arrives: do (a) or (b) per its text, then the EXACT NEXT
STEPS 1-6 below in one session.

**STATE:** Box 4 half-executed. The search phase ran LIVE today (08:08-08:44
UTC, `.venv/bin/python fit/cover.py search` on this checkout; resumable
per-site atomic writes; the run is logged in data/cover/search.run.log).
Result: 245/245 records = exactly the measured search set (204 qid + 41
no-qid), **107 new files on 16 sites, 0 failed routes** (every record says
"all routes answered"). Committed: data/cover/searches.json (new to git) +
the run log; data/cover/ is on my Touches line. tests/test_cover.py re-ran
with searches.json present in the checkout: 5 passed, 33.7 s (the test's
tree unlinks it, so it stays deterministic). The lead (mid-session message):
203b is done on main and its listed re-run is NOT a dependency of 212a -
the wait is lifted and 203b is off my Depends on line (211 stays; done).

**The 107 new files (16 sites, from searches.json "new"; all carry
meta.url):** arbeia-q1131391 1, aventicum 3, bibracte-q650053 18,
burcht-van-leiden 11, carnac-stones-q833850 2, craig-phadrig 1,
hopewell-mound-group 40, indian-mounds-park-q3150092 2, los-millares 3,
maeshowe 1, motte-castrale-quiquempois-q22961457 1,
moundville-archaeological-site-q1320821 1,
ocmulgee-mounds-national-historical-park-q1517500 9, stones-of-stenness 1,
the-roman-fort-vicus-bridge-abutments-an-q17650519 3, trundle-q7847949 10.

**BLOCKER (ask_human filed, blocking): the stage phase needs the
classifier.** The 107 files need classified.jsonl rows (my box 1 stages
"files.jsonl + classified.jsonl with the 200 evidence field"). The default
is Clef-flash on the AI box (10.0.10.75), reachable only through the ssh
tunnel at 127.0.0.1:18083 (pipeline/clef.py header:
`ssh -N -L 18083:127.0.0.1:8083 aibox`; the client honors AW_CLEF_URL).
From THIS VM: 18083 refused; the box's 8083/8081 are firewalled (TCP
timeout - no alternative endpoint for the override); the VM's only aibox
keys are the forced-command doorbell / labdash-feed / lab-archive (no
shell, no port forwarding) - so no tunnel is openable here. The LLM on
127.0.0.1:8081 (the one the lead FORBIDS for placement) is UP and is the
offered one-off alternative. The request offers: (a) RECOMMENDED - give
this VM an aibox ssh key with normal session/forwarding rights, I open
the tunnel and stage with the real Clef-flash (the classifier the batch
used); (b) approve the 8081 LLM as one-off classifier (I write a small
adapter, pass it to cover.stage, and record that it is not Clef-flash);
(c) only if both are refused - stage without classified rows (needs a
small stage code change and departs from the box-1 contract; not my pick).

**EXACT NEXT STEPS (one session, once the classifier is available):**
 1. (a) open the tunnel on this VM (`ssh -N -f -L 18083:127.0.0.1:8083
    aibox`) and verify the port; (b) write the 8081 adapter as an
    INJECTABLE classifier passed to cover.stage (classifier=...) - do not
    change the module default; record which model answered.
 2. `.venv/bin/python fit/cover.py stage --live` - the 107 local copies
    (1/s), the classifier in batches of 6, evidence.record live for the
    107 rows, plans.json re-export. Expect "stage: 107 file(s) staged".
 3. `.venv/bin/python fit/cover.py nopicture` - expect **229** items
    stamped (245 records minus the 16 sites that now have plans rows and
    are skipped; those 16 stay unstamped - their pictures go to the loop).
 4. Key-set diff: plans.json (id, sites[0]) pairs now vs the committed
    1475 (recompute the baseline from `git show HEAD:web/data/plans.json`
    - /tmp/aw212a-plans-keys-before.json is ephemeral). Expected: pure
    adds (~107, minus any title the keep filter already had in
    files.jsonl); ANY LOST key = a fetch failure to record as a data
    finding, never silently dropped.
 5. Commit: grown data/commons/files.jsonl + classified.jsonl, the 229
    re-stamped item files, the re-exported web/data/plans.json (the new
    data/raw/commons copies are gitignored - note their count in the
    commit message).
 6. Gates: `sha256sum -c tests/golden/hand_fit_docs.sha256` 40/40;
    `.venv/bin/python -m pytest tests/test_cover.py -q` green. Then box 4
    ticked, Status: done.
 The loop (the matcher) over the 16 found-picture sites, the sync, the
 export and the report are NOT 212a: the lead's loop + 212b + 212c.

**World pins still hold (re-verified today):** 499 built; 131 docs (21
by:hand + 110 by:agent); nofit 402; committed plans.json 1475 rows = 1475
unique (id, sites[0]) pairs (working tree == committed, checked); the
search wrote nothing outside data/cover/, so the 40 golden docs, the 52
all-in-item item files and the bethlehem/shotwick states are untouched.

---
(iteration 220 hand-over in git: `git show
32fc092:tasks/212a-cover-search.md`; iteration 219: `git show
dfbc286:tasks/212a-cover-search.md`; iteration 217: `git show
0ca160f:tasks/212a-cover-search.md`; iteration 216: `git show
590284f:tasks/212a-cover-search.md`.)
