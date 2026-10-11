# Review queue items (task 201)

One JSON file per site the automatic pipeline could not fit (the gate's refusals,
the fewer-than-four-pairs pictures, and the sites with no picture at all). The
human's drag on the page's Review section is the authority here; a human save is
trusted as-is (the gate constrains automatic fits only).

## File naming

`<site>.<lead-plan>.json` where `<lead>` is the best candidate's plan id
(`candidates[0].plan`, matching the platefit doc naming `<site>.<plan>`);
`<site>.json` for a site with no candidate picture. The item is keyed by its
`site` field, not the file name; `upsert_item` moves the file when the lead
changes.

## Item shape

```json
{
 "site": "<site id>",
 "candidates": [
  {
   "plan": "<plan id>",
   "title": "<picture title>",
   "url": "<exactly what the page's openPlan loads: books/<ia>/<file> or media/commons/<site>/<hash>.jpg>",
   "evidence": "<the 200 evidence field of the source row, verbatim, only when the row has one>",
   "pairs": [[u, v, lon, lat], "... 0-5, page px of the candidate's image frame -> lon/lat, 1dp/7dp, platefit format"],
   "coarse": true,
   "...producer extras, pass-through (202's ground/scale_m_px/rot_deg/scale_source/note, 203a's gate_score/why, the row's ia/file/book/label/cite/map_box/view/size when known); the page and export ignore unknown keys"
  }
 ],
 "no_picture_found": null | {"searched": "<exactly what was searched>", "at": "<iso>"},
 "resolved": null | {"doc": "<site>.<plan>", "at": "<the doc's at>"}
}
```

Rules:

- One item per site. Candidates merge by `plan`: a same-plan entry replaces its
  twin, new plans are appended. `upsert_item(root, site_id, entries, no_picture)`
  in `fit/review.py` is the writer (203a/203b/212).
- A candidate without a fitted picture may carry 0-3 model pairs, or none
  (`pairs` is optional); `coarse`/`note` say what the human can expect.
- `no_picture_found` is set (a dict) only when the item has no candidates and
  says exactly what was searched; once candidates exist it is null.
- `resolved` is write-once: no upsert ever clears or overwrites it.
- Resolution is derived, never a second store: an item is resolved when a
  `data/db/platefits/<site>.<plan>.json` doc exists for any of its candidates.
  Only `fit/review.py export` writes the `resolved` field (from the doc) and the
  page file `web/data/review.json` (open items only, `{at, items}`); the batch
  tasks never write that file and never delete items.
