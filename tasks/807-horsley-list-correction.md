Status: in-progress
Depends on: 207a
Touches: fit/src_roman_horsley.py, data/books/lists/britanniaromanao00hors.json, data/books/lists/britanniaromanao00hors.map.json, docs/lead_roman.md

# 807: Horsley - correct the plate list to 24 entries and record the book's lead-doc section

## Goal
Iteration 219 transcribed Horsley's plate list as 22 entries and dismissed stage A's flags on
leaf n0114 (P.44) and n0185 (P.113) as parametric hallucinations. Iteration 220 proved both are
GENUINE site-plan plates (full-size images + the book's own text, pp.43-44 and 113), and a
whole-book hOCR sweep found no further kind-s leaves - so the true list is 24 entries
(17 kind-s site plans, 7 kind-o). This task: (1) add the two entries to HORSEY_FIGS and update
the module's docstring/comments (24 list leaves, 17 kind-s, the 219 mislabel correction noted),
(2) regenerate the per-book list files offline, (3) verify books_lists.validate_book at
1.0/1.0/1.0/1.0 with no unexplained flags, and (4) write the Horsley section of
docs/lead_roman.md - the book's full record: source, the no-list discovery, the 24-entry list,
stage A/B recall, the staging plan that 808 executes, and the ~121 inscription plates deferred.
All work is offline (no LLM, no network).

## Acceptance criteria
- [x] HORSEY_FIGS in fit/src_roman_horsley.py = 24 entries: the 22 from 219 plus the two below
      (leaf-order: after the 62 line, before 236); the module docstring (its "22 list leaves /
      15 kind-s" wording) and the table's comment block updated to 24/17 with the 219
      mislabel-correction note; --list run fully offline (the socket-block wrapper below) and
      rewrites lists/britanniaromanao00hors.json (figures = 24 entries) and
      lists/britanniaromanao00hors.map.json (24 entries; site_plan=true on exactly the 17
      leaves [114, 185] + [236,238,...,254] + [278,280,...,286]; false on the 7 kind-o leaves
      [60, 62, 256, 706, 734, 832, 867]).
- [x] books_lists.validate_book(KEY) (in-process after register(), offline one-liner below)
      reports on the corrected list: recall_pages 1.0, recall_pages_pm1 1.0,
      precision_strict = precision_lenient 1.0 (17/17), flagged_not_in_list [],
      flagged_on_other_only_pages [], missed_pages [].
- [ ] The Horsley section of docs/lead_roman.md - inserted BEFORE the "## Roy" section (the
      lead's "in subtask order" line: Horsley, Maclauchlan, Roy; the Roy section is the format
      model; the Maclauchlan section will land between the two later) - records: the source
      (IA britanniaromanao00hors, 936 leaves; the Google scan IS the British Museum volume,
      shelf mark RB DA 145. H 86 folio on n0015; CITE from the title page n0014); the no-list
      discovery (215, verified on both the Google and the BM copies - the list is the plates'
      own printed headings, transcribed by eye); the 24-entry list (17 s / 7 o) with the two
      new plates described (the P.44 legionary camps; the P.113 five secondary stations),
      including the 219 mislabel correction and the 220 completeness proof (every hOCR page
      with text <700 chars listed + a plan-vocabulary sweep of every page: no further kind-s
      leaves exist in the book); the stage-A numbers (A typed 80 plate_site_plan, the
      BLANK_INK=0.005 floor keeps exactly 17 - the 63 others are blank/ghost show-through
      versos; stage-A-only on the 80: precision 0.188, quoted as why the ink floor is what
      makes the flagged set usable on this book; on the corrected list: 1.0/1.0/1.0/1.0, no
      flags); the stage-B verdict (17/17 re-read as plans, 0 errors, 18 s, 2026-10-14 on
      replicas 8080/8081; B's printed titles/site_names feed the staging rows); the 17-row
      staging plan that 808 executes (the 15 wall maps on the 216 QID/extras design; n0114 tied
      to a NEW Ardoch "roman site" extras row with Innerpeffery recorded on the row; n0185 ONE
      row tied to the principal fort's new "roman fort" extras row, the other four P.113 forts'
      names on desc; extras rows for all five P.113 forts only if the join requires each new
      site to have a plan); and the ~121 inscription/sculpture plates (Roman numerals
      I-CXXI) deferred as HORSEY_PLATES (kind o, indexed, never staged).

## Notes (operational facts carried from the 207a split, 2026-10-14 iteration 221)

**The two entries to add** (transcribed by eye from the full-size images, 220; long-s
spellings as printed; corner-mark convention "P.<page>" no space, as the existing table):

    114|Innerpeffery camp. (top plan) and Ardoch camp. (bottom plan): the two legionary camps of
        the Mons Graupius campaign per the book's text pp.43-44 ("the legions might poflibly
        have been at Ardoch, or Innerpeffery, before they marched to the battle"); each with
        its scale (200 / 300 yards), rivers Ruchel and Knoch, a military way and a Praetorium
        box|P.44|s|hand
    185|The five fecondary ftations per lineam valli: five fort plans, I GLANNIBANTA near
        Lanchester, II ALIONE now Whitley caftle, III BREMETEN RACUM now Old Penrith, IV
        OLENACUM now Old Carlisle, V VIROSIDUM near Elenborough; Praetorium boxes on I and III,
        Watling Street, a compass, "A feale of 100 paces"|P.113|s|hand

**validate_book one-liner (offline; run with .venv/bin/python):**

    import urllib.request, ssl, socket   # FIRST - the ssl import must precede the patch (PITFALLS)
    def dead(*a, **k): raise RuntimeError("network blocked in this run")
    socket.socket.connect = dead; socket.create_connection = dead
    import importlib.util
    spec = importlib.util.spec_from_file_location("h807", "fit/src_roman_horsley.py")
    h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h); h.register()
    import books_lists
    rep = books_lists.validate_book(h.KEY)   # print rep["figures"] + rep["flagged_site_pages"]

**Stage B (already run, 220):** data/books/triage/britanniaromanao00hors.B.jsonl = 17 rows,
0 errors (2026-10-14, replicas 8080/8081, 18 s; 8082 was down). B's schema has NO kind/is_plan
field (PROMPT_B: label/title/site_names/place/scale_bar/scale_text/north_arrow/north_tip/
south_end/map_box + blank_boxes); B's verdict = non-empty plans[] per page; it re-read all 17
as plans and gave the printed titles + site_names the staging rows use (n0114: "Innerpeffery
camp." + "Ardoch camp."; n0185: all five Roman names; the wall maps: their segment fort
names). B's set is unchanged by the list correction (A's ink-filtered 17 already include
114/185), so B does not need re-running.

**The completeness proof (220, hOCR only, low cost):** every hOCR page with text <700 chars was
listed (the plate-like pages) and every page scanned for plan vocabulary (camp/ftation/fort/
fecondary/map of/plan/scale of/section). The only plan-like plates in the whole book = the 15
wall maps + n0114 + n0185 (plus the already-tabled N.11 wall section and the 6 country maps,
kind o). The ~121 inscription plates are the rest (SCOTLAND/NORTHUMBERLAND/CUMBERLAND/DURHAM/
... headings, kind o, deferred); other short pages = front matter, the Book-II letter-table
(hocr 306), the altar-instruments plate (312), the Book-II collection title (315), the
chronological table (885), the index (895), the hOCR-silent fold-outs (hocr 63/705/834/868).

**Catalog check (220; sites.jsonl 12603 rows + extras.jsonl 193, keyed by "name"):** NONE of
the P.113 five forts (Olenacum/Old Carlisle, Virodidum/Elenborough, Bremenetracum/Old Penrith,
Alione/Whitley Castle, Glannibanta/Lanchester) nor Ardoch nor Innerpeffery exists in the
catalog - all seven are new no-QID extras entries (808 creates the rows this plan names; the
wall maps keep the 216 QID/extras design).

**Images (if /tmp is gone, re-download):** /tmp/horsley_full/ = every full-size jpg + all
crops made in 215/216/218/220 (incl. n0114.jpg/n0185.jpg and crops c2_0114_*, c2_0185_*,
c3-c5_0185_*). Re-download: https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg
with `curl -sL` + a browser UA (-L REQUIRED: 302 redirect, else a 0-byte file - PITFALLS).
Reading conventions: rotated sheets (P.158 N.1-N.10, P.176 N.1) = rotate CW, title box at the
sheet's bottom edge, corner mark at its top edge; upright sheets (P.176 N.2-N.5, N.11, P.44,
P.113, the four Book-III country maps, the two front-matter Ptolemy fold-outs) = corner mark
top-right.

**Module state at the split:** the 219 version (22-entry table; register() injects BOOKS[KEY]
+ HAND_FIGS[IA]; --fetch/--status/--triage A|F|B/--list built; --stage/--check/--golden
documented in the docstring but not yet built - 808/809 build them). The stage-A-only
sub-block numbers for the lead doc: A flagged 80, precision 0.188.

**Suite baseline at the split:** 1 failed / 156 passed / 1 skipped (389 s; .venv/bin/python -m
pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider); the lone red = agent a's 307d
placement test (known pre-existing: seed check + /tiles/relief 404). This task is offline-only:
no new reds expected; re-baseline on the final run.

(Unblocked 2026-10-14, iteration 137, agent c, from the parent 207: the owner's lift of the
"Stop 207" (asks 006/007, answered "b") covers this 207a continuation; the lead's 06c1aa8
block registered no open request and is stale - DECISIONS 2026-10-14 207. All work here
stays offline.)

## Hand-over
(2026-10-14, iteration 145, agent c - box 3 is WRITTEN and in the working tree; remaining =
tick box 3 + set Status: done + DECISIONS entry + final commit. The whole task is otherwise
done and verified.)

**What 145 did (the lead-doc section exists now, UNCOMMITTED in docs/lead_roman.md):**
- docs/lead_roman.md (working tree, `M` in git status) = the Horsley section inserted between
  the intro paragraph (ends "...in place of the shared validation.json.") and "## Maclauchlan"
  (line 17; subtask order Horsley, Maclauchlan, Roy; also satisfies the box's "before ## Roy").
  Heading: `## Horsley, Britannia Romana (1732) - 207a (list corrected 807)`. Seven bold-label
  paragraphs (the box's seven items): Source / the no-list discovery / the 24-entry list (with
  the two new plates, the 219 mislabel correction, the 220 completeness proof + the remaining-
  short-pages inventory) / Stage A / Stage B / Staging (the 17-row plan 808 executes) /
  Deferred (~121 plates). Hard-wrapped at 79 like the neighbours. The diff vs HEAD is PURELY
  ADDITIVE: 103 lines, 0 deletions (verified with diff <(git show HEAD:docs/lead_roman.md)
  <file>). Built by /tmp/aw807b/insert_horsley.py (textwrap 79, break_long_words=False - the
  script's length report counted logical elements, a cosmetic bug; the file is fine). One late
  patch re-wrapped the Stage-A paragraph's dating line to "measured offline, 219's run
  2026-10-13 reproduced with the corrected-list run 2026-10-14" (now at ~line 66).
  VERIFY BEFORE COMMIT: grep -n "219's run" docs/lead_roman.md (expect 1 hit) and re-run the
  pure-additive diff; do NOT rewrite the file from memory.
- Box 1 re-verified this session on the current tree: module table 24 entries (17 s / 7 o /
  0 u); lists/*.json = 24 figures, plates null; lists/*.map.json = 24 dicts sorted by n,
  site_plan=true exactly [114,185]+[236..254 even]+[278..286 even], false [60,62,256,706,734,
  832,867]. Box 2 numbers (144's measured runs) are the ones quoted in the section: 22-entry
  0.882 (15/17) flagged [114,185] stage-A-only 0.188 (15/80); corrected 1.0/1.0/1.0/1.0 no
  flags, stage-A-only 0.212 (17/80).
- B.jsonl format (for 808/809 readers): rows are {"n", "leaf", "out": {"plans": [...],
  "blank_boxes": [...]}} - the plans live under r["out"]["plans"], NOT r["plans"] (my first
  probe printed empty). n0114: 2 plans ("Innerpeffery camp." / "Ardoch camp.", each scale
  "A scale of two hundred yards" + north arrow); n0185: 5 plans, site_names pairs OLENACUM/
  Old Carlisle, VIROSIDUM/Elenborough, BREMETENRACUM/Old Penreth (B's spelling - 808's source
  of truth), ALIONE/Whitley castle, GLANNIBANTA/Lanchester; 31 plans total (24 on the wall
  maps, 1-4 each).

**Suite (145):** the background run (pid 3018765, started before my data commits, on the
22-entry state) FINISHED: 12 failed / 142 passed / 1 skipped / 15 errors (184 s) - ALL shared-
store churn from agent a's concurrent 212/236a/307d work: FileNotFoundErrors/HTTPErrors in
test_fit_queue (5F+4E), test_fit_provenance (2F+2E), test_matchfit_station (2E), test_merge
(4E), test_owner_check (2E), test_review (4F), test_serve (4F) - exactly the files agent a's
tasks own (web/data/fit_queue.json, data/merge/, data/db/platefits, web/data/review.json,
docs/site_flow/). NONE read any 807 artifact (no test imports the horsley module or its list
files; test_src_roman_horsley.py is 809's; the only lead_roman.md references are 207b's
docstring/golden-desc text). docs/site_flow/307d_*.png were NOT re-encoded this run (git
status clean there - test_owner_check died before writing) -> no 77c2f2c-style restore
needed. The driver re-runs the suite itself for the done claim; its newest loop-start note
(2026-10-13) names test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, a red
that lead port bba5961 CLEARED on main (207a iters 120/121 measured the merged tree 158/1/0;
corrected PITFALLS entry: the old signature is stale - if a re-check names it, cite that).

**Exact next step (one small session):**
1. Edit tasks/807-horsley-list-correction.md: line 1 `Status: in-progress` -> `Status: done`;
   box 3's first line `- [ ] The Horsley section of docs/lead_roman.md` -> `- [x]` (the two
   short unique anchors work with the edit tool; the rest of the file is untouched).
2. Append to DECISIONS.md: `## 2026-10-14 807 DECISION: iteration 145 - box 3 done: the Horsley
   section of docs/lead_roman.md written (7 bold-label paragraphs, purely additive 103-line
   diff, hard-wrapped 79) - all three boxes ticked, Status: done` + bullets: anchor choice
   (before "## Maclauchlan" = before the first "##" heading, subtask order; intro re-verified
   unchanged; the box's "Maclauchlan will land later" was stale - 207b had landed, per the
   144 anchor rule); section content = the box's seven items with the 144-measured numbers
   (re-verified 145); B.jsonl out-plans format finding; the suite-churn analysis above;
   307d PNGs not re-encoded; done claim filed, driver re-checks.
3. Optional (record a lasting fact, the 807-prep note got the shape wrong): PITFALLS entry
   under `### pipeline/books.py, pipeline/books_ia.py (the book machinery)` (insert before
   `### pipeline/autowalls.py`, ~line 1309): the lists/<ia>.map.json rows are DICTS
   {"n", "site_plan", "entries"}, not the [n, site_plan, entries] triples the 807 prep
   claims - verified across ALL 12 books' map files in data/books/lists/ (probe `e[1]`
   dies KeyError: 1; read e["n"]/e["site_plan"]).
4. Commit: git add docs/lead_roman.md tasks/807-horsley-list-correction.md DECISIONS.md
   PITFALLS.md && git commit -m "807: the Horsley section of docs/lead_roman.md (box 3) -
   the book's full lead record: source, no-list discovery, the corrected 24-entry list, stage
   A/B recall, the 17-row staging plan 808 executes, the deferred ~121 plates; all boxes
   ticked". Stop - the driver re-checks.

**If the driver reopens on a red:** it names a specific test. First check it is shared-store
churn (stat the file's mtime + git status in the main checkout; PITFALLS shared-store entry).
If real and not owned by another open task's files: A/B in-checkout per the PITFALLS idiom -
my files = fit/src_roman_horsley.py + data/books/lists/britanniaromanao00hors.{json,map.json}
+ docs/lead_roman.md (back up to /tmp, restore main's state, re-run, compare byte-for-byte);
cite the 207a-222 A/B precedent. 3rd failed attempt at the same blocker -> ask_human +
Status: blocked.

**Chain:** 808 (the 17-row staging; its plan = this section's "Staging" paragraph; its Notes
carry the coordinate cross-check + evidence-contract detail; it may append accounting to the
section per its box) then 809 (--check + golden + the no-network test; the test's seed = the
task Notes' socket-block validate_book one-liner) run after this task.

**Environment facts (kept true):** data/raw is a symlink into the shared store (the 936 triage
jpgs + bookreader.json live there - re-download recipe in the task Notes if gone); never call
cmd_validate (it writes the shared validation.json - 211/230's); .venv has numpy+PIL, system
python3 does not; the machine clock is 2026-10-14 (matches the journal sequence); nothing of
mine runs in the background now (pid 3018765 is gone).
