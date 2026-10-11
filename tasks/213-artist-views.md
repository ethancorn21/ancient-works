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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/213-artist-views.md` (open) - hand-over: **Step 2 done (iteration 24, 2026-10-11): Imola pinned, triaged, staged; Venice staged; boxes 2 + 3 ticked.**

## Next open tasks
- `tasks/202-propose.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 213 DECISION: module shape - SITES table + per-source row tuples, stdlib-only at the top
fit/src_artists.py: SITES{qid: site facts (id/name/lon/lat/place/region/kind/wikipedia/cat/p625/note)};
SOURCES{name: rows + display label + p-field} for the two image-level sources (row tuple (title, qid, label,
opts) - a variant of sources.py: the region lives on the site, since all its rows share it); BOOKS{civitates,
merian} with the IA identifiers (per-book flow is session 4; the books.py:BOOKS entry is a shared-module
change -> file a task, never write it). Top-level imports are stdlib only (json/os/sys/time); commons/evidence
are imported lazily inside functions because commons->aw needs numpy (absent from the system python3) - live
commands run under .venv/bin/python. CLI: --verify (live QID re-check, prints the search traps next to the
table values for the lead doc), [--dry] (stage), --check (offline join + evidence.check over the staged rows;
books arg = a never-existing path), --golden (normalized staged rows -> tests/golden/src_artists_sample.json,
checked/date_commons zeroed). check_staged() join: file rows may name staged OR existing sites (box-3 rule:
existing QID -> picture row on the existing site id, no new catalog entry); staged ids/QIDs must not pre-exist;
classified rows 1:1 with file rows.

### 2026-10-11 213 DECISION: the prep's Imola "centre 44.245 N, 12.367 E / bad P625 53 km NW" was wrong - that point is Cervia; P625 is the correct city point
The prep notes placed Imola's old town at 44.245 N, 12.367 E and, seeing Q50195's P625 (44.353, 11.715) far
from it, called the P625 "bad, ~53 km NW of the town". Verified live (2026-10-11): the prep point is CERVIA
on the Ravenna coast (~50 km SE of Imola); the real city is at 44.353 N, 11.715 E, where THREE independent
sources agree: the enwiki infobox (44°21'11"N 11°42'53"E), Wikidata P625, and the OSM town node (with the F1
circuit beside it and the Santerno - "Fiume Santerno" at 44.3606/11.7104 - running through the urban area).
So the "53 km trap" was the distance between two wrong values. Consequences: (a) the site point is the
walled town's centre, 11.7112/44.3535 (Piazza del Duomo, OSM) - the centre of the sheet's circular view, not
the modern city point; (b) the prep's "Savena crossing" was a second error - the drawing's river is the
Santerno, which Leonardo labels "Sant'Arno" (mirror script, read off the sheet); the view is south-up per
the literature; (c) the evidence story changes: for Imola the live record route resolves the RIGHT QID (the
hand record still stands to pin the walled centre, deterministic and offline); the name-search trap that is
REAL and documented is Venice (first hit with P625 = Q773853 Venice, California, 9891 km). Side note: OSM's
comune boundary for Imola is mis-drawn (Nominatim displays the urban area as "Imola, Nuovo Circondario
Imolese", and the admin relation's centre sits 8 km north of the city) - a reason never to geocode Imola
from OSM/Nominatim. The PITFALLS entry "Q50195 (Imola) carries a bad P625..." must be corrected accordingly
(pending in the next session; I cannot edit PITFALLS from the context-limit hand-over step).

### 2026-10-11 213 DECISION: Imola triage (one paced commons.info run) + staged both image-level sites; --check 2/2 PASS
Triage of the Imola candidates (all Public domain, all pass commons.keep()): "File:Leonardo da vinci, Town
plan of Imola.jpg" (1030x774, circa 1502) verified by eye to be ANOTHER SCAN OF THE SAME RCIN 912284 SHEET
(same view, walls, river, margin legend/notes) -> dropped as a duplicate picture; "File:...RCIN 912686, Recto
Sketches of the street plan of Imola.jpg" (1517x2000 portrait, undated) = a different work (measured survey
sketches with block grids and fortress details) -> dropped; "File:Imola 1705.jpg" (942x710, 1705, Antonio
Ferri) = a flat plan by another hand from another century -> dropped (not one of the task's four GOAL
sources). The GAp Imola scan stays a commons.NO "google" drop. Staging (`.venv/bin/python fit/src_artists.py`)
wrote extras_artists.jsonl (imola-q50195, venice-q641; region "Italy" - transient "US" display until 214
merges), files_artists.jsonl (2 rows with hand-recorded caption_coords evidence; Imola date ""/year 1502 -
the file page has no DateTimeOriginal, the noted box-1 case; Venice date 1500) and classified_artists.jsonl
(2 rows, p_birdseye 1.0, by hand). `--check` then passed: 2/2 caption_coords, no join problems, exit 0
(offline). Boxes 2 and 3 ticked (the hand-checked table + existing-QID rule were done in session 1 and are
unchanged in shape). Remaining: box 5 (Civitates/Merian book work or documented status), box 6
(tests/test_src_artists.py + golden), box 1 (lead doc final), box 4 (count check, last). docs/lead_artists.md
is written for Imola + Venice (uncommitted, harness-saved).

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

### 2026-10-11 agent/a (213) hand-over status
    Books step pushed: civitatesorbiste00brau = Liber secundus (1575); stage-A triage running in background
    (pid 1657419, /tmp/civitates_triage.py, LLM ports 8080-8082 patched in-process - books.py's 18080/18081
    are stale, filed as task 215; A was 262/292 at hand-over, F pending). Tasks 215/216/217 filed (shared
    book-machinery gaps). Lead-doc books section rewritten (UNCOMMITTED: docs/lead_artists.md, task files).
    data/books/triage/civitatesorbiste00brau.A.jsonl is still growing from the background run - wait for
    DONE in /tmp/civitates_triage.log before committing it. Next: hand list transcription, --golden, test.
