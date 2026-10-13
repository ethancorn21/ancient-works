Status: done
Depends on: none
Touches: fit/src_artists.py, tests/test_src_artists.py

# 228: Artists check accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends the staged artists' rows (Leonardo's
1502 Imola aerial plan and Jacopo de' Barbari's Venice view, plus their site rows) into the
canonical `data/catalog/extras.jsonl` / `data/commons/files.jsonl` /
`data/commons/classified.jsonl` - byte-identical, first-row-wins; the staging files stay and
the module's `--check` still reads them. `fit/src_artists.py`'s `check_staged()` (around
L334-376) has three guards that self-trigger on any merged tree (on 211's branch
`test_check_staged_files_join_and_pass` is red for exactly this):

- `staged_ids & set(known.values())` - "staged site ids collide with existing sites";
- `s.get("qid") in known` - "staged site re-uses existing QID";
- `k in canonical` - "staged title already in the canonical files.jsonl".

All three fire because `known_sites()` reads the canonical `extras.jsonl` (plus the catalog and
`web/data/sites.json`), which after the merge contains the module's OWN staged sites
(imola-q50195, venice-q641), and because the merged file rows are in the canonical
`files.jsonl`.

Fix the guards, not the data:

- a staged `(site, title)` row whose key is in the canonical file is OK (no-op, "already
  merged by 211") when the staged row is equal to the canonical row under the merge's identity
  rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same `norm()` fit/merge.py
  uses), and still a problem when the key is held by a DIFFERENT row;
- the known-site checks treat a self-reference as no collision: `known[qid]` equal to the
  staged site's own id (its merged row, or the same site via the catalog) is fine; the id/QID
  is a problem only when it resolves to a DIFFERENT site (a real duplicate, which is what the
  guard exists to catch - keep it failing loud in that case).

The book-town part (the civitates Liber secundus towns in `BOOKS`) is unaffected: those rows
land in the book index via 211's box 2, not in files.jsonl, and no check here reads them. The
test covers all three states hermetically (no network, no fixed ports, no writes outside the
project or a temp dir): (a) staged rows absent from canonical - current assertions unchanged;
(b) staged rows in the canonical files with identical content (point the module's canonical
path constants at a constructed temp copy) - check rc 0, no QID/id false positives; (c) same
key or same QID held by a different row - still fails loudly. The test must not depend on
211's live merge having run on this checkout.

## Acceptance criteria
- [x] `check_staged()` returns 0 when the staged sites and file rows are already in the
      canonical files with identical content (constructed temp canonical files) - no
      "re-uses existing QID" / "ids collide" false positives for the module's own merged rows.
- [x] A QID or site id held by a DIFFERENT site, and a same-key/different-row title, are still
      reported (rc 1) - the cross-source duplicate protection is unchanged.
- [x] The pre-merge behavior is unchanged: with the canonical files not containing the staged
      rows, every test_src_artists.py test that passed before still passes.
- [x] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 225 limes, 226 numancia, 227 stukeley), filed by agent a on 211, iteration
  174, after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.

## Hand-over
(2026-10-12, iteration 198, agent a - DONE, all boxes ticked, suite green 150 passed / 1 skipped; committed.)

- What changed: `fit/src_artists.py` `check_staged()` only (plus a new `_canon_norm` helper next to
  `_norm`; `stage()` needed no change - it is already a no-op on the merged tree via `have`/`staged_ids`).
  The three self-triggering guards now treat a self-reference as a no-op: a staged `(site, title)` key in
  the canonical files.jsonl passes only when the staged row equals the first canonical row under the merge's
  identity (`_canon_norm` = merge.py's `norm` on the parsed row); a staged QID passes when `known[qid]` is
  the site's own id; a staged id passes when no known site holding that id has a different QID.
- The id guard deviates from the 222-227 set-difference pattern (`staged_ids & (known.values() - staged_ids)`):
  that one cannot report "a staged id held by a DIFFERENT site" (the id is in staged_ids, so it is subtracted
  away) - 228's acceptance box 2 requires it, so the guard compares each staged site's id against the known
  holders' QIDs per site. The QID guard and the canonical-identity rule follow the siblings exactly. Message
  formats kept identical to the originals.
- Tests: `test_check_staged_three_states` (new, the 225/227 pattern): monkeypatches the module constants
  `SITES_JSONL`, `EXTRAS`, `WEB_SITES`, `FILES_CANONICAL` at temp copies of the real files with the module's
  own rows stripped (the hermetic pre-merge state, independent of whether 211's live merge ran here); (a)
  pre-merge -> rc 0; (b) identical rows merged -> rc 0, no join problems; (c1) same key different row,
  (c2) QID held by a different site, (c3) id held by a different site -> rc 1, exactly one named join line.
  No network (autouse socket-blocking fixture), no ports, writes only to the test's tmp dir.
- Verified: 5/5 test_src_artists.py (the four pre-existing tests unchanged and passing, both on the merged
  tree of this checkout and hermetically pre-merge); live `fit/src_artists.py --check` rc 0 with no join lines
  on this checkout's merged tree; full suite 150 passed / 1 skipped.
- For 211: this was the last of the seven 222-228 gate tasks. On 211's branch the live merge already exists
  (this checkout has it: extras.jsonl/files.jsonl/classified.jsonl + the built web/data/sites.json entries);
  a re-run of `fit/merge.py merge` should be a no-op (idempotent first-row-wins). Re-verify the 222-228 tests
  green on the real merged files there, then 211 can claim done.
- No re-reads needed; the next agent on a follow-on task touching this module: the guards live in
  `check_staged` and the identity helper is `_canon_norm`.
