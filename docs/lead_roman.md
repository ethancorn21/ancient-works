# Roman books: Horsley (1732), Maclauchlan (1857-58), Roy (1793) - old site plans of Roman forts and camps (task 207; the Roman-sites lead of GOAL.md's "the map grows" list)

GOAL: every picture tied to its place with machine-checkable evidence. This lead indexes three
books with the book machinery (pipeline/books.py: fetch, triage A/B, list mapping, validate) -
one book per subtask (207a Horsley, 207b Maclauchlan, 207c Roy) - and stages their site-plan
pages tied to Roman sites (an existing catalog site by QID where one exists, or a new extras
row). One section per book below, in subtask order; a section appears when its subtask starts
work and stays where it lands. Each book keeps its own per-book artifacts only
(`data/books/triage/<ia>.*.jsonl`, `data/books/lists/<ia>.json` + `.map.json`) and appends to
the lead's shared staging files (`data/commons/files_roman.jsonl` + `classified_roman.jsonl`,
rows tagged with the book; new sites in `data/catalog/extras_roman.jsonl`): the shared
`data/books/index.jsonl` and `validation.json` are never written by this lead - 211 rebuilds
the shared index from the per-book files once. The stage-A/B recall against each book's own
printed list of plates is recorded in that book's section, in place of the shared
validation.json.

## Roy, Military Antiquities of the Romans in North Britain (1793) - 207c (dropped)

**Source (verified 2026-10-11, re-verified 2026-10-13):** NOT on the Internet Archive -
exhaustive advancedsearch (the exact title, title phrases, creator "Roy, William", a
1790-1800 year-range text query, ten guessed identifier patterns - all empty; the only
related item is the 1917 dissertation ABOUT Roy, macdonald-1917-roy: no facsimile, no plate
list, not the book). The National Library of Scotland holds the only complete online
facsimile (maps.nls.uk/roy/antiquities/: 174 text pages + 51 map plates of the Roman camps
and forts of Scotland) but it refuses this VM: AWS-WAF "Human Verification", HTTP 405 on
every path with browser user agents (checked 10-11 and again 10-13, the drop-decision day);
the open NLS S3 tile bucket holds no antiquities set (roy/ = 1747-55 military-survey tiles
only, the background maps of pipeline/nls.py). HathiTrust 403s this VM and the Google Books
API answers 429 with a 0-queries/day anonymous quota (both recorded 10-12/13 for the
Wiltshire lead; the same wall, re-verified for this book 10-13) - so no complete copy of the
book can be fetched from this VM at all, and the human has declined to download books for
this project (the standing refusal of 209a/209c, PITFALLS).

**Outcome (ask_human 008, answered 2026-10-13 14:36, console):** the request (filed
2026-10-13 from 207c's session: confirm the owner's "Stop 207" covers this subtask, and
either the NLS facsimile into data/raw/books/roy1793/ - any layout, minimum the 51 map
plates plus the printed list of plates - or a drop decision) was answered: "drop Roy. I
dont want to have to ever go out and get a file. If you need it get it. If you can't get
it, then you don't need it." **Task 207c is DROPPED.** No Roy rows exist in any staging
file, and none will be staged unless a complete scan of the book ever appears in the repo
(data/raw/books/roy1793/, any layout); if it does, the resume recipe is the parent
hand-over's (207) "Mechanics for every subtask" plus its exact-next-steps item 3.

**Stage-A/B recall against the printed list of plates:** n/a - the book was never obtained;
207c was dropped before any triage stage ran.

**Effect on the lead:** the Roman lead stands on 207a (Horsley 1732: the engraved maps and
fort plans of England, Wales and the two walls) and 207b (Maclauchlan 1857-58: the
Hadrian's Wall forts); the parent's acceptance boxes 1-4 are met by those two books alone.
The map does not gain Roy's early Scottish camp plans: the catalog's four no-QID Antonine
Wall camps (bar-hill-fort, inchtuthil, raedykes, rough-castle-fort in extras.jsonl) stay
without plans from this book, and no new Scottish roman_fort rows are staged by this lead
(Scottish sites Horsley or Maclauchlan do show are staged by their own subtasks as usual).
