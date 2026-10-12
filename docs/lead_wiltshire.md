# Wiltshire: Hoare, Stukeley, Petrie - old drawings of Stonehenge and Avebury (task 209, GOAL point 4)

GOAL point 4: the old drawings of the two most famous sites on the map. This lead stages the
site-plan plates of three works - Hoare's *Ancient Wiltshire* (1812-21), Stukeley's Wiltshire work
(1740s) and Petrie's *Stonehenge, Avebury, and other Stone Age monuments of the British Isles*
(1880) - one book per subtask (209a/b/c), each into its own per-suffix staging files
(`data/commons/files_wiltshire_{a,b,c}.jsonl` + `classified_wiltshire_{a,b,c}.jsonl`, rows tagged
with the book; a `*_wiltshire_{a,b,c}` extras file only if a plate shows a Wiltshire earthwork not in
the catalog yet). Per-book book artifacts only (`data/books/triage/<id>.*.jsonl`,
`data/books/lists/<id>.json` + `.map.json`): the shared `data/books/index.jsonl` and
`validation.json` are never written by this lead - 211 rebuilds the shared index from the per-book
files once. The existing hand fits (Allcroft Avebury fig. 187, Allcroft Windmill Hill fig. 186, in
`data/db/platefits/`) are never re-staged or re-fitted: new rows only. The stage-A/B recall against
each book's own printed list of plates is recorded in that book's section below, in place of the
shared validation.json.

## Hoare, Ancient Wiltshire (1812-21) - 209a

**Source (verified 2026-10-13, re-verified 2026-10-12):** NOT on the Internet Archive - exhaustive
advancedsearch (the title phrase returns only two modern books; the hundred names Pewmarsh/Pewsey/
Cherhill return nothing). HathiTrust holds the work (public domain, full view) and Google Books
serves it, but both refuse this VM: HathiTrust answers HTTP 403 to every request (checked with
several user agents, including a browser UA, on both 2026-10-12 and -13) and the Google Books API
429s it. So the copy arrives human-downloaded, the 207c pattern: **ask_human 001 (filed 2026-10-12)**
asks for **volume 3, *The Hundred of Cherhill* (1821)** - the volume that carries the
Stonehenge/Avebury/Silbury/West Kennet plans - placed in `data/raw/books/hoare_cherhill1821/` as one
image per leaf page, filenames sorting in book order (covers included; the module re-encodes to
triage size). Vols. 1-2 (Pewmarsh 1812, Pewsey 1819) are a bonus, same placement in their own
folders. Fallbacks in the request: "drop" (this lead then stands on 209b/209c) or any other complete
scan of the Cherhill volume.

**The fetch leg (built 2026-10-12, `fit/src_wiltshire_hoare.py`, tested in
`tests/test_src_wiltshire_hoare.py`):** the module registers the book in process
(`books.BOOKS["hoare_cherhill1821"]`, ia/region/year/cite/why) and wraps the machinery's three
IA-only calls (`books_ia.pages`, `books_ia.page_texts`, `books.fetch_triage`) for this id only: the
local leaf list (n = 0-based leaf index, leafNum = 1-based) and the local re-encode (1400 px long
side, JPEG q88) land at the exact `books.triage_path` slot, so `books.run_stage` (triage A/F/B on
the live Qwen replicas, 127.0.0.1:8080-8082) and everything after it run UNMODIFIED. No per-page
OCR exists for a local copy (`page_texts -> {}`): the plate anchors come from Qwen's stage A
(`map_plates` handles that - its OCR-only evidence simply stays empty). Commands: `--fetch`
(local, resumable, idempotent), `--status` (offline: leaf count, triage progress, LLM ports),
`--triage A|F|B` (working phase). The remaining legs - list transcription (`--list`, the
books_lists PLATES pattern from the copy's own list pages), staging (`--stage`, 200 evidence field:
list entry names the place, caption / coordinates distance recorded on the row; the 1821 date on
every row), `--check` (offline join + fit/evidence.py) and `--golden`
(`tests/golden/src_wiltshire_hoare_sample.json`) - are added to the module when the copy arrives.

**State (2026-10-12):** waiting on ask_human 001. LLM replicas 8080/8081 were up this session
(8082 resetting, 18080/18081 down - the built-in `LLM_PORTS` covers all, run_stage uses whichever
answer). On arrival: verify the leaf count and the list page, `--fetch`, `--triage A` (resumable
background job, nohup), transcribe the printed list of plates into
`data/books/lists/hoare_cherhill1821.json`, `--triage F`/`B` as the list and stage A suggest, then
stage / check / golden and record the stage-A/B recall below.

**Stage-A/B recall against the printed list of plates:** pending the copy (the Cherhill volume's
own list names the plates; the numbers go here once triage A/B has run).
