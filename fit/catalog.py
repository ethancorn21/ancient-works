"""The catalog's site lookup, shared by the fit/ modules (task 309's right-place check).

The catalog (data/catalog/sites.jsonl) lists every known earthwork, built or not; a
record's ``id`` is the site id the page uses (``<slug>-q<Qid>``). A review item may
legitimately name a site that is not in web/data/sites.json yet: 309's right-place
check moves a picture off a namesake built site onto its right site, which the batch
cannot cover because it is unbuilt - that item is not an orphan, and its display
name is the catalog's, not the raw id. This module is the one place that answers
"is this site id in the catalog, and what is its name" for the fit/ consumers
(review's export, batch_eu's union check). tools/right_place.py's load() is the
heavier reader (it also builds the matcher's name/token indexes) and stays separate.

Stdlib only: importable by 203a/203b/212 in any environment (no numpy, no network).
The store is optional: with no data/catalog/sites.jsonl the catalog is empty and
every lookup misses (the consumers keep their old behaviour: the id, a warning).
"""

import json
import re
from pathlib import Path


def load(root):
    """The catalog records, keyed two ways: ``catalog`` by the record's id (the site
    id) and ``by_qid`` by its lower-cased Q-id. Empty dicts when the store is absent."""
    out = {"catalog": {}, "by_qid": {}}
    path = Path(root) / "data" / "catalog" / "sites.jsonl"
    if path.is_file():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("id"):
                out["catalog"][rec["id"]] = rec
            if rec.get("qid"):
                out["by_qid"][rec["qid"].lower()] = rec
    return out


def lookup(data, site_id):
    """The catalog record for a site id: by the id itself, then by the Q-id the id
    carries (a site id's slug may differ from the catalog's; the Q-id is the stable
    part - the same two-step as tools/right_place.py's site_facts). None when the id
    is unknown to the catalog."""
    if not site_id:
        return None
    rec = data["catalog"].get(site_id)
    if rec is None and re.search(r"-(q\d+)$", site_id, re.I):
        rec = data["by_qid"].get(site_id.rsplit("-", 1)[1].lower())
    return rec
