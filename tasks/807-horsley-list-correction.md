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
(2026-10-14, iteration 144, agent c - boxes 1+2 done and committed (d137f28 + the list-file
commit below); box 3 = the lead-doc section is the ONE remaining step)

**Prep notes (tasks/prep/807.md) - which assumptions were wrong:**
1. STALE: "207a is on agent/c, NOT in main" - 207a IS merged into main (1e9e63b); my branch
   (agent/c) already carries the 219 module, the 22-entry list files and docs/lead_roman.md.
   No blob extraction from agent/c was needed; no branch-state discrepancy beyond the prep's
   own staleness (the Depends chain worked as intended).
2. STALE: "lead_roman.md has only the ## Roy section (207b's section: not yet in the file)" -
   207b's Maclauchlan section HAS landed (line 17, heading says "(in progress)") before the Roy
   section (line 98, "(dropped)"). Anchor rule (prep §1/207b, matches the lead's "in subtask
   order" line): insert Horsley AFTER the intro paragraph (ends "...in place of the shared
   validation.json.") and BEFORE the first "##" heading = before Maclauchlan. That also
   satisfies the box's "before ## Roy". Re-read the intro before inserting in case 207b edited
   it since (the Maclauchlan section body looks final; its heading's "(in progress)" is just
   its stage marker).
3. CORRECT as written: everything else - the books/books_lists machinery semantics (validate_book
   offline, cmd_ocrmap offline + its stage-A guard, the BLANK_INK=0.005 floor, ink() over local
   triage jpgs, the socket-block one-liner pattern, B.jsonl contents, the 808 staging plan, the
   220-era catalog check) all match main, and the prep's dry-run predictions matched my actual
   runs exactly (both the 22-entry and the 24-entry sides).

**Done this session (all committed, all offline):**
- fit/src_roman_horsley.py (d137f28): HORSEY_FIGS = 24 entries (17 s / 7 o). The two lines from
  the task Notes inserted VERBATIM between the `62|` and `236|` lines (leaf order; each exactly
  4 pipes; long-s spellings; P.44 / P.113 corner marks, no space). The docstring's --list usage
  line ("24 list leaves ... the 17 kind-s maps"), the Later-legs paragraph, and the table's
  comment block (17 kind-s; the 219 mislabel correction - the stage-A FLAGS on n0114/n0185 were
  right, only the invented captions were hallucinations; the 220 hOCR completeness sweep proves
  24 is the whole book's kind-s set) all updated. HORSEY_PLATES still None.
- data/books/lists/britanniaromanao00hors.json = 24 figures (the 22 old ones byte-verbatim + the
  2 new, leaf order 60,62,114,185,236-254 even,256,278-286 even,706,734,832,867; plates: null);
  .map.json = 24 entries sorted by n: site_plan=true exactly [114,185] + [236..254 even] +
  [278..286 even], false on [60,62,256,706,734,832,867]; the 22 old map entries unchanged. The
  regen ran under the socket-block wrapper (/tmp/aw807/list807.py) -> stdout exactly: `horsley_
  britannia_romana_1732 plates 0 figures 24 fig kinds {'s': 17, 'u': 0, 'o': 7} list leaves 24`.
- Box 2 evidence (/tmp/aw807/validate807.py, .venv/bin/python, socket-blocked, both runs): PRE
  = 219 journal reproduced to the digit (precision 0.882 = 15/17, flagged_not_in_list [114,185],
  stageA-only 0.188 = 15/80, flagged 17/80/936, stageF 0); POST = recall_pages 1.0, recall_pages
  _pm1 1.0, precision_strict = precision_lenient 1.0 (17/17), flagged_not_in_list [],
  flagged_on_other_only_pages [], missed_pages []; flagged_site_pages 17 / stageA 80 / triaged
  936; stage_A_only on the corrected list recall 1.0, precision 0.212 (17/80).

**Next session - box 3 (the only remaining work), then done:**
1. Confirm the background suite (pid 3018765 -> /tmp/aw807/suite.log; started this session
   before my data commits, so it ran on the 22-entry files + the pre-commit module - fine: no
   test reads any horsley file, the run is a baseline health check). Expect the known baseline:
   1 failed (agent a's 307d/307bb placement test - known pre-existing, flakes and passes on
   re-run per c344571) / ~159 passed / 1 skipped, plus whatever other tasks' tests main gained.
   If the suite re-encoded docs/site_flow/307d_*.png (it overwrites all ten every run), restore
   main's bytes (git checkout main -- <those pngs> + a small bookkeeping commit, 77c2f2c
   precedent) BEFORE the final commit so the driver's merge stays conflict-free.
2. Write the Horsley section of docs/lead_roman.md (one commit). Anchor: between the intro
   paragraph and "## Maclauchlan" (above). Heading in the neighbours' style, e.g. `## Horsley,
   Britannia Romana (1732) - 207a (list corrected 807)`. Body = the seven bold-label paragraphs
   the box lists (Source / the no-list discovery / the 24-entry list with the two new plates +
   the 219 mislabel correction + the 220 completeness proof / stage A / stage B / the 17-row
   staging plan 808 executes / the deferred ~121 inscription plates). Format model: the
   Maclauchlan and Roy sections (bold label: paragraph, dates on the journal sequence =
   2026-10-14 era). Numbers to quote: all in this hand-over + the DECISIONS entry (214-14 807)
   + the task Notes; for B's per-plate detail read data/books/triage/britanniaromanao00hors
   .B.jsonl (n0114 = 2 plans "Innerpeffery camp." + "Ardoch camp."; n0185 = 5 plans I-V with the
   Roman/modern site names - B's "Old Penreth" spelling is 808's staging source of truth, the
   list keeps the transcribed "Penrith"; the 15 wall maps = 1-4 plans each with segment fort
   names; B's schema has no kind field - verdict = non-empty plans[]); the staging-plan detail
   is in tasks/808-horsley-stage.md (the 15 wall maps on the 216 QID/extras design; n0114 ONE
   row on a NEW Ardoch "roman site" extras row with Innerpeffery recorded; n0185 ONE row on the
   principal P.113 fort's new "roman fort" extras row, the other four forts' names on desc;
   extras rows for all five P.113 forts only if the join requires each new site to have a plan;
   the four Antonine camps reused from extras.jsonl; every row 1732 + the 200 evidence field);
   the 207a archive entries (DECISIONS-archive.md, "# Task 207a horsley" section, the 215/218/
   219/221 entries) have the no-list discovery, the corner-mark conventions and the CITE text
   (title page n0014: printed for John Osborn and Thomas Longman, at the Ship in Pater-Noster
   Row, London 1732, M.DCC.XXXII; shelf mark RB DA 145. H 86 folio on n0015).
3. Tick box 3, set Status: done, commit (module + list files already committed; this session's
   commit = the lead-doc section + the task file + DECISIONS). The driver re-checks the suite
   green itself.

**Environment facts (kept true):** data/raw is a symlink into the shared store (the 936 triage
jpgs + bookreader.json live there - re-download recipe in the task Notes if gone); never call
cmd_validate (it writes the shared validation.json - 211/230's); .venv has numpy+PIL, system
python3 does not; the suite must not bind fixed ports (it doesn't) and the machine clock is
2026-10-14 (matches the journal sequence).
