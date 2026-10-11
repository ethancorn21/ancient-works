Status: open
# 801: Evidence coverage for the 280 no-tie picture rows (OS-sheet maps and book scans)
Depends on: 200
Touches: fit/evidence.py

## Goal
Task 200 (done) records machine-checkable ties on every picture row; 280 of the 1381 commons rows
carry kind `none` *without* a stored conflict - the caption names no full site name, so the
conservative full-name route of `named_places_in` finds no place to resolve. Most are Ordnance-Survey
sheet maps ("Ordnance Survey Drawings - <town>") whose description enumerates many places, and book
plate scans. The acceptance wording of 200 allows reported no-tie rows, but GOAL.md's intent is that
*every picture* be tied to its place - so improve the coverage while staying fail-closed: a row only
gets a passing field when the named place actually resolves near the site, and a resolved place that
is far away must keep the row `none` with the conflict stored (the existing 74 conflict rows show the
mechanics).

## Acceptance criteria
- [ ] `fit/evidence.py` records a passing evidence kind (caption+coords, or a new well-named kind such
      as "sheet mention") for a majority of the currently no-tie rows whose title/description genuinely
      names the site (the OS sheets that list it among the places on the map qualify; a sheet that does
      not name the site does not), with the specifics and checked date stored as before
- [ ] It stays fail-closed: re-run `fit/evidence.py record --live` then `check`; every row whose named
      place resolves more than 50 km from the site is recorded `none` with the conflict (never a pass);
      `check` exits 0 on the committed files; the sample golden (tests/golden/evidence_check.txt) is
      unchanged or regenerated only for an intended change
- [ ] The row count, the byte-preservation of every existing field and the 12/12 test suite are
      preserved (the record test's fixture stays valid)

## Notes
- The caption route matches only a full site name/alias as a substring of title+description
  (`named_places_in`); that conservatism is what leaves the OS sheets un-tied (their captions name the
  sheet's town, and the site appears at most in a place list). The book matcher
  (pipeline/books_match.py) already has token-level matching machinery; reuse its rules rather than
  inventing looser ones, and keep the distance check (50 km) as the guard.
- A sheet-index alternative: the OS sheet description's place list can be parsed and each entry
  resolved, like the current route, but that multiplies network calls - the batched prefetch of
  task 200's `record_live` (one search per unique name, one batched claims fetch) must stay the shape.
- Rerunning `record --live` is idempotent for recorded rows; to re-evaluate only the no-tie rows a
  `--only`-style filter or a kind-based skip is needed - add it in this task if useful.
- Filed by agent c (task 200) from the measured outcome: 1338 live-recorded rows = 825 category,
  164 caption_coords, 38 hand_tied, 354 none (74 with stored conflicts, 280 plain).

## Hand-over

**Where I am (iteration 16, agent c).** Offline prototype of the sheet-candidate extractor DONE and
eyeballed over ALL census sites (no network, no repo changes this session - the prototype lives in
/tmp/sheet_proto2.py, /tmp/sheet_proto2_out.txt, /tmp/sheet_proto2_dump.txt; recreate if /tmp was
wiped, rules below). Design now FINAL (iter-15 design + 6 deltas found by the data). No code in
fit/evidence.py yet; tests never ran this session (nothing changed in the repo).

**Iter-15 facts that stay true:** Clifford's Tower HAS P625 (6 m) -> part_mention passes the 40
york-castle rows; 332/343 part qids have P625 (311 within 50 km of own site; 19 far -> stay
fail-closed; 11 without P625 -> site-coord safety net); part census dump: 175 catalog sites carry
has_part [{qid, name}] (names are in the catalog - part matching is OFFLINE, only P625 needs the
batched claims prefetch). The 354 stored-none rows: 74 with conflict, 280 plain. Census of the 280
is in DECISIONS (2026-10-10 801 entry) - keep consulting it for expected verdicts.

**Extractor (final rules, verified offline):** input = NFKD-normalize(title + ' ' + desc truncated at
the last word boundary <= 600 chars), strip leading "File:". (1) tokenize
`[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+` (handles Maastricht1749LarcherDAubencourt2).
(2) KEEP a token iff: starts with a letter (digits NEVER kept - v1 bug), len>=3, not all-lower,
not ALL-CAPS (acronyms), lowercase not in STOP. A token "ST" (2 chars) is kept only to merge with the
next kept word -> "St Louis" (the cahokia row needs it). (3) STOP list: mined from the 354 rows'
capitalized-word frequency table - the full list is in /tmp/sheet_proto2.py; it covers EN metadata
(File Book This All Images Page Title Year Authors Identifier Subjects Publisher Catalog Viewer
Digitizing Sponsor Contributing Library About Entry Edition Shelfmark Date Dimensions Medium Credit
Transcription Program Number Copy Printed Engraved Sheet Map Atlas Survey View Plan Drawings One-inich
Published House Design Pattern Textile Garden? NO - keep Garden, City, Church, Tower, River, Park, New,
Great/Little/High/Old/North/South - those are place-name components, NEVER stop them) + NL (Plattegrond
Reproductie Identificatie Titel Objecttype Objectnummer Vervaardiging Vervaardiger Omschrijving
Opschriften Merken Datering Plaats Afbeeldingen Naaukeurige Voornaamste Sterke Steden Gezicht(en)
Onderdeel Zeven) + FR (Sujet Echelle Couverture Langue Editeur Appartient Plattegrond? no - that's NL;
Carte(s) Plano Vue(s) Planche Legende Echelle Hauteur Largeur Detail(s) Extrait Avec Sur Sous Entre
Pour Dans Une Numerisation). (4) RUNS: kept words form a run unless a COMMA or a real lowercase word
(len>=3) sits between two consecutive kept words in the source (protects "New Orleans",
"Cranbourne Hampshire", "Monmouth Castle"; breaks the OS place lists "Sammarobriva Amiens Cenabo").
(5) Per run, in order of appearance: 2-word pairs, then 3-word phrases, then the singles (this order
matters: "New Orleans" must be TRIED BEFORE the lone "Orleans" - the lone word resolves to Orléans
= the cenabum site and would be a FALSE PASS for the New-Orleans junk rows). (6) <=12 candidates per
row, deduped, title candidates before desc ones. A lone leading word that is the row's ONLY kept word
is dropped (heading, not a place).

**Verdict logic (final, mirrors the existing caption route):** candidates resolved by the EXISTING
batched shape (one wbsearchentities per unique name, then ONE batched wbgetentities 50/batch, all via
commons.get pacing; ~1500-2078 unique names -> 25-35 min one-off manual cost, logged). Among resolved
candidates: nearest <=50 km -> sheet_mention PASS ({named_place, place_qid, place_label, place_lon,
place_lat, site_lon, site_lat, dist_m}); else nearest far -> none WITH the conflict (existing shape,
check re-verifies distance from stored coords only); else plain none (reason lists routes tried).
Title-preference for PASSES was considered and REJECTED: the cenabum New-Orleans junk rows carry the
place only in the DESC and box 2 demands the conflict. Known accepted consequence (logged): a
proper noun that is also a city name ("York" on the 1914 tin, "Dudley" on a genealogy book) will
pass when the site sits in that city - keyword+50km cannot see depiction; the never-pass-far guard
holds, and box 1 only needs the majority of genuinely-naming rows (they pass; the extra city-level
passes are in GOAL's spirit).

**Prototype findings (v2, run this session, 2078 unique candidates):** digit tokens leaked ("000",
"1870", "2369494") and my v2 STOP list had DROPPED the preposition block ("The" x26, "Ordnance" x5,
"Quartier" x16, "House" x16, "Design" x5, "Textile" x5, "Pattern" x5, "English" x40, "Roman" x4,
"Numerisation" x6, "Onderdeel" x5). The fix (require first char isalpha; add those words to STOP;
NOTE: store "numerisation" ASCII, the STOP match runs on NFKD text) was NOT YET APPLIED - my edit
call failed atomically (a bad oldText in a sibling edit), so /tmp/sheet_proto2.py still has the old
STOP list. Eyeball of the census sites confirmed the approach: standalone singles appear for
Strasbourg x36-39, Reims x4, Orleans (only AFTER NFKD - v1 tokenized "Orléans" as "O"+"rl"+"ans" =
zero candidates! NFKD is mandatory), Weesp, Arnhem, Casaromago, Barkhale, Monmouth, Manchester,
Nijmegen, Birmingham; per-site verdicts behave as censused (fletio must stay none: its first resolved
candidate Casaromago is 440 km; the same file passes on castrum-levefanum at 0 km). Part hits =
EXACTLY 40 (all Clifford's Tower) - matches census.

**Exact next step (iter 17):** (1) if /tmp/sheet_proto2.py is gone, recreate it from the rules above;
apply the two pending fixes (digit exclusion + STOP additions listed above) and re-run - expect
~1400-1600 unique candidates; eyeball the top ~50 of the frequency list for any remaining non-place
junk (person names like Seyboth/Bolgiano/Dennis are EXPECTED and harmless - they have no P625; the
distance guard is the mechanism, the STOP list only cuts cost). (2) Live prototype (manual, paced):
resolve those uniques via commons.get (search + batched claims, dump to /tmp/sheet_verdicts.txt) and
compare per-row verdicts with the census - WATCH: what does the "Bethlehem" search return first? The
74 stored conflict rows ALREADY encode the answer for the caption route (read their stored
conflict.place_qid in data/commons/files.jsonl before spending searches); if the search top hit with
P625 is the Dutch Bethlehem, the 51 bethlehem rows would falsely PASS - in that case restrict the
bethlehem site's candidates or log it. (3) Implement in fit/evidence.py: refactor-first commit
(extract the caption-route block of live_evidence into _caption_route, no behavior change, tests
green), then part/sheet routes + the two new kinds + checkers (check_part re-verifies part_qid in
the catalog site's has_part qids at check time; check_sheet mirrors check_caption incl. the norm
substring - candidates are norm-substrings of title+desc by construction) + docstring kind list,
then `--redo-none` (only with --live; plain record stdout stays EXACTLY "evidence recorded: N
hand-tied, N book, N live"). (4) Run `record --live --redo-none` on the real files (diff:
ONLY the 354 none rows' evidence field may change; a stored conflict is rewritten only when the
resolution is still >50 km, else the row becomes a pass or plain none per the verdict logic), then
`check` (exit 0, 1490 rows, zero FAIL, golden byte-identical), then .venv/bin/python -m pytest -q
(12/12). (5) If passes land below a majority of the ~85-90 genuinely-naming rows, log the shortfall
in DECISIONS before relaxing anything.

**Gotchas (unchanged + new):** run everything through .venv/bin/python (books_match imports books.py
-> PIL); do NOT touch requirements.* (agent a's task 800); tests never use the network, no fixed
ports, no writes outside project + /tmp; never rebase/merge (driver handles branches); set_field
preserves line bytes; the 74 existing conflict rows must keep re-verifying after the run; desc
truncation is at a WORD boundary (a cut-off word like "Bethl" would otherwise become a phantom
candidate).
