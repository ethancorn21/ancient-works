Status: open
# 213: Artists' views - Leonardo's Imola, Barbari's Venice, Braun & Hogenberg, Merian
Depends on: 200
Touches: fit/src_artists.py, data/catalog/extras_artists.jsonl, data/commons/files_artists.jsonl, data/commons/classified_artists.jsonl, data/books/triage/civitatesorbiste00brau.A.jsonl, data/books/triage/civitatesorbiste00brau.F.jsonl, data/books/lists/civitatesorbiste00brau.json, data/books/lists/civitatesorbiste00brau.map.json, docs/lead_artists.md, tests/test_src_artists.py, tests/golden/src_artists_sample.json

## Goal
The new lead of GOAL.md point 5 (the 2026-10-10 change; the owner, of Leonardo's 1502
plan of Imola: "should 100% be on our map"): artists' aerial and bird's-eye views count
as drawings as much as surveys do. The sources to verify: Leonardo da Vinci's aerial
plan of Imola (1502, Royal Collection, RCIN 912284); Jacopo de' Barbari's view of
Venice (1500); Braun and Hogenberg, Civitates Orbis Terrarum (1572-1617, hundreds of
walled towns); Merian, Topographia (1640s-1680s). For each: verify it exists, is old
enough (views of the structure are exempt from the 150-year rule) and is freely
machine-readable; tie every picture with 200's machine-checkable evidence; stage the
rows in this task's own files. 211 consolidates and builds the new sites; 212's cover
pass runs the model's fitting loop over the staged pictures. Imola is the anchor: a new
site with no open LiDAR here, so it is an aerial-photograph site (FITKIT_GROUND=aerial)
and its streets carry the fit.

## Acceptance criteria
- [ ] Verified before use (docs/lead_artists.md): for each source, what it is, where its
      files live, the drawing's date (recorded on the row - where a repository only has
      an upload date, the known drawing date is used and noted), and exactly which files
      are staged; unusable sources or files (paywalled, too small, no place tie) are
      listed with the reason - a documented drop beats a guessed row.
- [x] Imola staged as a new site: an extras_artists.jsonl entry (id, name, place,
      lon/lat, region, kind, QID, wikipedia), a files_artists.jsonl row for the plan in
      the files.jsonl shape with the 200 evidence field, and a classified_artists.jsonl
      row; the row notes no open LiDAR here (aerial-photograph ground,
      FITKIT_GROUND=aerial). fit/evidence.py check passes offline on every staged row.
- [x] The hand-checked file -> QID table lives in fit/src_artists.py (the sources.py
      pattern): every QID verified against its label and coordinates - a name search
      alone gives the wrong place (the Barnard Castle trap); a picture of a site whose
      QID is already in the catalog gets a picture row for that existing site id, no new
      catalog entry.
- [ ] At least Imola plus one further source (Venice, one Civitates town, or one Merian
      view) is staged, or docs/lead_artists.md accounts for each unstaged source with a
      verified reason.
- [ ] If Civitates Orbis Terrarum or the Topographia turn out to be Internet Archive
      books indexable with pipeline/books.py, work in per-book files only
      (triage/<ia>.*, lists/<book>.json) and add those exact paths to this task's
      Touches line before writing them - never the shared index.jsonl or
      validation.json (211 rebuilds both).
- [ ] Test (no network): the staged files join (every file row names a staged or
      existing site; every new catalog entry has at least one picture), the evidence
      check passes on the staged rows, and a golden sample of rows is pinned.

## Notes
- Leonardo (Royal Collection, per GOAL.md) and de' Barbari are image-level leads like
  204-206 (one file row per view); Civitates and Merian are book-scale (hundreds of
  views). If this grows past a few sessions: split into subtasks 213a-... by source,
  each with its own staging-file suffix and docs/lead_artists_<source>.md; 211
  consolidates whatever staging files exist.
- Imola's aerial-photograph ground (Esri World Imagery, tools/fitkit.py) means the
  model's fit reads what has not moved: roads, the river crossing, church footprints -
  the feature pairs the sheet shows on both sides, not walls in relief.

## Hand-over
**Iteration 26 (2026-10-11): books step resumed and pushed far; lead doc books section rewritten; tasks 215-217 filed. Commit this state (the triage files keep growing from the background run - commit them when stable).**

**What this session did:** (a) established that iteration 25's orphaned triage process had appended the last
2 pages of A after the driver's snapshot (A = append-only, re-runnable - no repair needed); (b) identified
civitatesorbiste00brau = **Civitates Orbis Terrarum, Liber secundus (1575)**, 292 leaves (imperial-privilege
page in its OCR names Hogenberg/vanden Noeurt/Braun + "Secundus"); (c) found **books.py's LLM_URLS
(18080/18081) are stale on this machine** - no listener; the llmtunnel ssh service (user llmtunn, up since
Oct 6) serves the Qwen replicas on **127.0.0.1:8080/8081/8082** (all /v1/models -> 200). Every book task's
triage B/F is blocked by this; (d) launched the triage in the BACKGROUND (see below) and, while it ran,
filed **tasks 215** (books.py ports), **216** (BOOKS entries for the 6 view books, Depends 213+215),
**217** (books_lists lists + view-as-drawing index, Depends 216) and **rewrote the lead-doc books section**
(6-item table, Liber secundus description, the views-cannot-index gap, status: worked in per-book files).

**THE BACKGROUND RUN (do not kill without reason):** `/tmp/civitates_triage.py` (pid 1657419 at hand-over),
log `/tmp/civitates_triage.log`, writes `data/books/triage/civitatesorbiste00brau.A.jsonl` (finishing pages
211-291; 262/292 done, 0 errors so far) then `.F.jsonl` on every figure_site_plan+other_illustration page.
It patches `books.LLM_URLS` to 8080-8082 in-process and injects `BOOKS["civitates"] = dict(ia=
"civitatesorbiste00brau", region="Italy", year=1575)` - NO shared file is modified. archive.org IIIF is
slow (timeouts + retries are normal; a page that exhausts retries gets an error row and a re-run picks it
up). **Re-run if dead/incomplete:** `nohup .venv/bin/python /tmp/civitates_triage.py >> /tmp/civitates_triage.log 2>&1 &` (idempotent). Wait for it to print DONE (or finish) before committing the A/F files.

**Facts for the list transcription (next main step):** the book has **no printed town list** - transcribe
from the plate inscriptions (A/F captions = the model's reading; verify the ambiguous ones visually - maps
like FEDERATORVM HELVETIAE, arms pages like "Armes de ceste Ville de Milan", fold-outs n187/n199, the
Jerusalem PLAN n237/238 = the only kind-"s" entry). `page_numbers.json` (cached in data/raw) is SPARSE:
printed numbers only at leaves 193-196 (1-4) and 280-284 (I-V) - so list entries key on the LEAF (n),
`page` mostly null. Write `data/books/lists/civitatesorbiste00brau.json` = {"plates": null, "figures":
[{"fig": i, "title": <inscription as printed>, "page": null-or-printed, "kind": "o" (view), kind "s" for
the Jerusalem plan, "u" if unsure, "kind_by": "hand"}]} and `.map.json` = `[]` (honest under the current
machinery: list_pages maps only kind s/u). **Then fix the lead-doc sentence that says the list "is
hand-transcribed"** - make it true or soften it to the state you reach. Then a few hand-verified towns
(paced Wikidata QIDs: Rome/Vienna/Florence/Milan/Brussels/Antwerp candidates) recorded in
fit/src_artists.py:BOOKS and the lead doc. Box 5 end-state = per-book files + documented status (rows come
via 211/217, not staged by 213 - the lead doc says so).

**Still to do (order):** (1) above; (2) `.venv/bin/python fit/src_artists.py --golden` -> commits
tests/golden/src_artists_sample.json (path already in Touches; never hand-edited); (3) write
tests/test_src_artists.py per prep §4 (join; table completeness; offline evidence check exit 0 with the
NEGATIVE CONTROL: Imola row with the Cervia point 44.245/12.367 must be FAIL; golden compare; socket-
blocking fixture; .venv); (4) tick boxes 1, 5, 6, then box 4 LAST; (5) note in 211's Hand-over that the
*_artists* staging files + the civitates per-book files must be merged (R6); (6) add the PITFALLS entries:
LLM ports 8080-8082 vs books.py 18080/18081 (215's box 3 expects it - do it once, here or in 215, not both),
+ long data jobs outlive the session and the driver's snapshot commit catches the file mid-growth (check
mtime/stability before committing a growing file).

**State of the boxes:** 2, 3 ticked (unchanged). Box 5 ~80% (triage A nearly done, F running, lead doc
done, list pending). Boxes 1, 4, 6 open. `--check` last passed (2/2) in iteration 24; staging files are
append-only and untouched since - re-run `--check` before claiming.

**Invariants (unchanged):** staged files append-only + idempotent; never touch fit/evidence.py,
pipeline/books.py, pipeline/books_lists.py, data/books/index.jsonl, validation.json (215/216/217 own the
shared modules); GAp scans never staged; box 4 last; golden only via `--golden`; the LLM service on
8080-8082 is shared by all agents' book work - pace yourself, don't add workers beyond run_stage's default.
