Status: open
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
- [ ] `check_staged()` returns 0 when the staged sites and file rows are already in the
      canonical files with identical content (constructed temp canonical files) - no
      "re-uses existing QID" / "ids collide" false positives for the module's own merged rows.
- [ ] A QID or site id held by a DIFFERENT site, and a same-key/different-row title, are still
      reported (rc 1) - the cross-source duplicate protection is unchanged.
- [ ] The pre-merge behavior is unchanged: with the canonical files not containing the staged
      rows, every test_src_artists.py test that passed before still passes.
- [ ] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 225 limes, 226 numancia, 227 stukeley), filed by agent a on 211, iteration
  174, after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.
