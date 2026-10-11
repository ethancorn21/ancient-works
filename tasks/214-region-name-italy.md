Status: open
# 214: Add Italy to build_catalog's REGION_NAME (and audit the regions the data uses)
Depends on: none
Touches: pipeline/build_catalog.py, tests/test_region.py

## Goal
`build_catalog.make_site` shows a site's region as `REGION_NAME.get(region.lower()) or "US"`: every region
outside the REGION_NAME table silently displays as "US". 213 stages two Italian sites (Imola, Venice) with
region "Italy", which is not in REGION_NAME (its keys are lower-case; the value it falls back to is the raw
string, which place_of handles but make_site does not), so once 211 builds them the page will show them as US
sites. Add the missing mapping and pin it with a test that also guards against silent US fallback for any
region the data actually uses.

## Acceptance criteria
- [ ] `REGION_NAME` maps "italy" to "Italy" (add other region keys the data audit below finds missing)
- [ ] Test (no network; socket-blocking fixture): `make_site` on a synthetic entry with region "Italy" yields
      site region "Italy", not "US"; and every distinct region string across data/catalog/*.jsonl and
      web/data/sites.json resolves to itself or a known name (no silent "US" fallback for a non-US site)

## Notes
- `make_site` calls `wiki_summary` (network): under a socket-blocking fixture that fails gracefully to
      (None, None); the test asserts on the region field only.
- If a later source task stages sites in another missing region, it adds the key in this task's follow-up
      (or reopens this task) - the audit box is the guard.

## Hand-over
