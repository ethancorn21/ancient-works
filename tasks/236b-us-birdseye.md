Status: open
# 236b: US bird's-eye and panoramic city views (1847-1929)
Depends on: none
Touches: fit/src_us_birdseye.py, data/catalog/extras_us_birdseye.jsonl, data/commons/files_us_birdseye.jsonl, data/commons/classified_us_birdseye.jsonl, docs/lead_us_birdseye.md, tests/test_src_us_birdseye.py, tests/golden/src_us_birdseye_sample.json

## Goal
Subtask of 236. GOAL.md point 5: artists' aerial and bird's-eye views count as much as surveys. The Library
of Congress "Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; many
mirrored on Wikimedia Commons) is the US equivalent of Braun & Hogenberg. Stage views of the owner's four
cities first (New York, Washington DC, San Francisco, Nashville), then more US cities, in this task's own
staging files, the way 213 staged Civitates.

## Acceptance criteria
- [ ] Verified before use (docs/lead_us_birdseye.md): the collection's location and licence, how files are
      fetched (Commons category or loc.gov IIIF), per staged view its date, artist/publisher and resolution;
      unusable ones listed with the reason.
- [ ] fit/src_us_birdseye.py holds the hand-checked file -> QID table (every QID verified against label,
      P625, enwiki). Views of a city that 236a also stages use the SAME site id - agree it through the
      catalog slug rule (catalog.slug from QID + name) and record the shared ids in the lead doc; never two
      sites for one QID.
- [ ] Staged rows in this task's files only: extras_us_birdseye.jsonl (only for cities not already in the
      catalog and not staged by 236a - check data/catalog/extras_us_cities.jsonl on main before adding one;
      region "United States", kind "town", aerial_ok true), files_us_birdseye.jsonl (files.jsonl shape +
      200 evidence field), classified_us_birdseye.jsonl ("view", by hand).
- [ ] fit/evidence.py check passes offline on every staged row; the four owner-named cities each have at
      least one view staged or the lead doc says why not; at least 25 cities staged in total.
- [ ] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Bird's-eye views are oblique: the fit is harder than for a plan. Prefer views drawn near-vertical; record
  the view's apparent angle on the row's note so 236c/the matcher can order them.
- Templates: fit/src_artists.py + docs/lead_artists.md (Civitates).
- Do NOT write the canonical files - that is 236c.

## Hand-over

(2026-10-14, iteration 178, agent a - FIRST session: research only, live. NO repo file touched yet - no
module, no staging, no lead doc, no tests. Context limit hit while eyeballing the last candidate thumbnails;
nothing uncommitted in the repo.)

- **Baseline.** 236a is DONE and on main: the four city sites staged in its own files -
  data/catalog/extras_us_cities.jsonl has exactly the site rows new-york-q60 / washington-q61 /
  san-francisco-q62 / nashville-q23197 (name/named/lon/lat/place/region "United States"/kind town/
  wikipedia/aerial_ok true/note); files_us_cities.jsonl 15 rows, classified_us_cities.jsonl 15 rows;
  docs/lead_us_cities.md (763 lines); tests/test_src_us_cities.py (4 tests) + golden
  tests/golden/src_us_cities_sample.json. The "united states" REGION_NAME line 236a added is already on
  main - 236b must NOT add it again (236b's Touches has no build_catalog.py). Test suite at loop start
  (driver note 2026-10-13): 159 passed, 1 skipped, 1 failed - the failure is
  tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's in-flight 307 work
  on main, NOT this task's fault).
- **Collection verification (for the lead doc's box 1):** loc.gov is UNREACHABLE from this machine:
  GET https://www.loc.gov/collections/panoramic-maps/ -> 403 Forbidden (CloudFront bot block; both the
  web_fetch tool and direct urllib with the project UA fail - PITFALLS candidate). The Wayback Machine
  snapshot of the page (2025-01-02) renders: it shows the item list (per-item Date, Contributor =
  artist/publisher, "LC Panoramic maps (2nd ed.)" Phillips numbers, "Available also through the Library
  of Congress Web site as a raster image") but the snapshot's extracted text carries no description
  block - so the collection's size/range (~1,500 US views, 1847-1929) and public-domain status stand on
  GOAL.md's statement + the LOC item records' own "No known copyright restrictions" language pattern.
  **Fetch route decision: Wikimedia Commons mirrors only** (the project's established pattern; 236a/
  artists/kip all fetch via Commons extmetadata). Many LOC Panoramic Maps items are mirrored on Commons
  with LOC IDs in the title ("LOC 75694818", "LCCN2009633685", "ppmsca.03354").
- **Commons organization (verified live):** NYC = Category "Bird's eye view maps of New York City"
  (145 members; the FILES live in its decade subcategories "1850s/1860s/.../1910s bird's eye view maps
  of New York City", ~102 each - members(cat,'file') alone gives only ~12; a weird subcat "New-York.
  Birds' eye view, looking south from Union Square" has 932 members). DC = Category "Bird's eye view
  maps of Washington, D.C." (175 members, ALL direct files, no subcats). SF and Nashville have NO
  bird's-eye category at all (only "Views of ..." subcats, photo-dominated) - file-namespace full-text
  search is the only route (queries like "bird's-eye view of San Francisco" worked; "intitle:bird's-eye
  intitle:Nashville" found nothing - the file titles carry the city, the search must be unquoted-ish).
- **Candidate pool built and analyzed (re-derivable; /tmp may be wiped):** ~383 unique candidate titles
  with full extmetadata via commons.info (50/call, 1/s paced) were collected and filtered by
  commons.keep() + the caption gate (books_match.norm(city short name) in norm(title+desc), the 600-char
  desc window exactly as fit/evidence.py check_caption). Good lists: NYC 95, DC 10, SF 56, Nashville 5.
  Re-derive with commons.members() + commons.info() (the queries are in the DECISIONS entry) if /tmp
  (aw236b_candidates.json / aw236b_good.json) is gone.
- **VERDICTS (thumbnails eyeballed, 1280 px - STAGED candidates for the four cities):**
  - NYC (new-york-q60, named "New York"): STAGE 3 -
    (1) File:New York - drawn by J. Bachmann ; print by G. Schlegel, 97 William St. N.Y. LCCN98508526.jpg
        (10078x6950, 1874, PD; classic near-vertical harbor view, "NEW YORK" printed);
    (2) File:The city of New York. LOC 75694818.jpg (12901x22870, 1879, Taylor/Galt & Hoy, PD; whole
        island in portrait, full grid - "File:Taylor map of New York.jpg" 12901x22870 is the SAME sheet
        (DPLA scan) - one row per sheet, drop the dup);
    (3) File:View of the city of New York and vicinity LOC 78692903.jpg (12720x9136, 1907, Ohman & Co.,
        PD; metro-wide - review-item scale, the 1811-sheet precedent). Other passers for a later batch:
        1849 Bachmann Sarony&Major 9371x6705; 1854 NYPL harbor panorama 6872x5414; 1855 Cheltnam 7230x5428
        (CC0); 1870 C&I LOC 75694809 10224x7024; 1876 C&I LOC 75694810 11248x7920; 1877 C&I LOC 75694807
        11936x8272 + the PGA 10699x7571 edition; 1883/84/86/89/92 C&I 75694812/22/23/25 (11-12k px);
        1897 23rd/24th wards 22240x6176; 1911 Wellge 6740x2750 (CC0); 1912 Ruppert 8654x6481.
        NOTE: File:New York in 1674 - C. Vardel fec(it) - btv1b53143268k.jpg (5250x4250, PD, 1674) is a
        genuine bird's-eye view but OUTSIDE the collection's 1847-1929 range - decide later (record in
        lead doc either way).
  - DC (washington-q61, named "Washington"): STAGE 2 -
    (1) File:Washington, the beautiful capital of the nation LOC 78695113.jpg (13568x8944, 1921, Olsen/
        A. Graham Co., PD; whole city, title printed on sheet - eyeballed, excellent);
    (2) File:The national capital, Washington City, D.C. LOC 75694904.jpg (9888x12560, 1883, A. Sachse
        & Co., PD; city + Georgetown, title printed - eyeballed, excellent).
    Thumbnails DOWNLOADED but NOT yet viewed before the context limit (view or drop at staging time,
    they are all genuine bird's-eye views per title/date/artist): chk_B_H_Warner... (1886, 7936x6168,
        full title: File:B.H. Warner & Co.'s Map showing a bird's-eye view of the city of Washington and
        suburbs - locating the public buildings and places of interest LOC 87693417.jpg),
        chk_View_of_Washington_City_LOC_90683459_jpg.jpg (1871, 7340x5340),
        chk_District_of_Columbia_and_the_seat_of_war_on_the_Potomac_LOC_.jpg (1861 Bohn, 4047x2689 -
        the caption gate passed, "Washington" is in the 600-char desc). Also: 1872 Morrison 6192x4752;
        1866 Capitol East Front 3355x2248; 1915 "The ultimate Washington. LOC 87694199.jpg" 6394x4705
        (Nat'l Geographic, the speculative 1915 map - a fine candidate); 1861 balloon view 1536x1040
        (small - likely a size drop, the Butler precedent).
  - SF (san-francisco-q62, named "San Francisco"): STAGE 3 -
    (1) File:(Bird's eye view of San Francisco) LOC 75693101.jpg (12912x8176, 1868, Goddard/Britton &
        Rey/Snow & May, PD - eyeballed, THE classic; .tif same file; the IA scan "File:Birds eye view
        of the city of San Francisco and surrounding country. Drawn by George H. Goddard. Lith. Britton
        & Rey (IA dr birds-...)" 12587x8962 and "File:Birds eye view of the city of San Francisco.
        NYPL1952949.tiff" 7662x5062 CC0 are presumed SAME sheet - one row, drop dups after a visual
        check at staging);
    (2) File:The city of San Francisco. Birds eye view from the bay looking south-west. LOC 75693104.jpg
        (11376x8272, 1878, Parsons/Currier & Ives, PD - eyeballed, excellent; the LCCN90715988 5581x4009
        .jpg/.tif pair is a smaller scan of the same sheet);
    (3) File:1914 San Francisco Birds Eye Map by Peter.jpg (11302x8777, 1914, C. Merriman Peter, PD;
        pre-1915-exposition whole peninsula, dense grid + index - eyeballed, excellent).
    Plus (eyeballed, stage or drop at staging): File:San Francisco. 1854 (published for the History of
    the world) - DPLA - Original.jpg (7000x4156, 1854, Henry Bill via LOC - city in half the frame, grid
    visible; the DPLA .jpg/.png are smaller scans of the same) - I lean STAGE (oldest good view).
    DROPS with reasons: File:Panoramic view of San Francisco, California, from hilltop, looking
    northeast LCCN2006677456.jpg (1850, 10300x6113) and File:View of San Francisco, formerly Yerba
    Buena, in 1846-7 before the discovery of gold. LOC 74693207.tif (1884, 8464x6304, Bosqui) =
    PICTORIAL views, the city small in the frame (no grid at fit scale); the 1906 earthquake aerials
    (Chadwick/Lawrence "captive airship", "smoldering downtown") = PHOTOGRAPHS not drawings (236a's
    HABS-photo precedent); "'View of San Francisco in 1850', 1878, oil on canvas... Burgess" = a
    PAINTING; the 1856/1858 Henry Bill Geographicus view-map (3500x1974/4000x2325 - the 236a lead) =
    composite map+view, the bird's-eye part small (thumb downloaded: /tmp/aw236b_thumbs/chk_1856_Henry_
    Bill_...) - decide after viewing; the Faust flat maps, the "(Covers to)" book covers, the Seattle/
    Port Townsend hits (search noise) and the "highest priced half mile" (that's the 1861 Southampton
    docks, the ship "Nashville") = not this city/not a view.
  - Nashville (nashville-q23197, named "Nashville"): the thinnest city. STAGE 1 -
    File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg (13851x9666,
        1896, PD, color - eyeballed: bird's-eye of the 1897 exposition grounds in Schreiner Park, the
        Capitol at left, "NASHVILLE, TENNESSEE, 1897" printed; depicts a PART of the city, note it).
    The Henderson Litho 6315x4483 pair and "File:Tennessee Centennial Exposition 1897 (LOC
    ppmsca.03354).jpg" are other scans of the same sheet (ppmsca.03354 = the LOC item id).
    The three Fletcher 1864 Fort Negley views (236a's leads; all PD lithographs drawn by W.H.H.
    Fletcher, 12th Battery Ind. Vols.; captions carry "Nashville, Tenn" in the 600-char desc so the
    gate passes; thumbs at /tmp/aw236b_thumbs/...Fort_Negley...): File:South west view of Fort Negley
    LCCN2003655690.jpg (7950x3822) + .tif (7964x4356), File:North west view of Fort Negley
    LCCN2003655670.tif, File:South east view of Fort Negley LCCN2003655689.jpg (8082x3978) -
    eyeballed the SW one: a CLOSE-UP of the fort on its hill, NO city grid. DECISION AT STAGING TIME:
    drop all three ("view of Fort Negley, not of the city - no street grid; 236a found no fort-only
    plan, so no fort site") OR stage them on nashville-q23197 as defence views (the DC 1865 ring
    precedent) with an explicit note. Either satisfies "at least one view or the lead doc says why" -
    the Centennial view stands regardless.
- **Mechanics notes for the module (fit/src_us_birdseye.py, copy the 236a/src_artists pattern):**
  1. SOURCES rows: (title, qid, label, {date: known-date swap}). p = "birdseye" for all rows (the
     classified row: p_birdseye 1.0 by hand). Labels like "{name}, the Goddard bird's-eye view (1868)".
  2. known_sites() must be EXTENDED vs 236a's: it reads SITES_JSONL + EXTRAS + WEB_SITES - add
     data/catalog/extras_us_cities.jsonl (236a's file, READ ONLY - the four shared site ids come from
     there; a mismatch between 236a's rows and 236b's table fails loud). The four owner cities get NO
     extras row from 236b (acceptance box 3: extras_us_birdseye.jsonl is only for NEW cities); the 4
     site ids are used as-is on the files/classified rows.
  3. check_staged() join guard: `valid` site ids = staged (this module's extras) + known sites - it
     must ALSO include the 236a-staged ids (via the extended known_sites()), or the four cities' file
     rows fail "neither staged nor existing".
  4. The stage() evidence_for caption gate (236a's: books_match.norm(named) in norm(title+" "+desc))
     applies per file; all STAGED candidates above already pass it (desc window 600 chars, exactly as
     fit/evidence.py check_caption re-checks offline; dist_m 0.0, place = site point, kind
     caption_coords).
  5. keep() traps to remember (NO regex): "portrait", "flickr - ", ".pdf", ".djvu", "geograph" - the
     1906 aerial photos and the Flickr scans died on these; the PUBLISHED-in-desc rule can rescue an
     undated title (year_of) but only with the PUBLISHED regex words.
  6. The 25-cities box: the four owner cities + at least 21 MORE US cities, each a NEW site in
     extras_us_birdseye.jsonl (region "United States", kind "town", aerial_ok true, box 2000 m,
     site point = the city's P625 verified like 236a's --verify; the note records the view's apparent
     angle per the task Notes). The LOC collection has bird's-eye views for hundreds of US cities;
     per-city route = Commons file-namespace search "bird's-eye view of <city>" (categories exist only
     for a few cities). Good first batch (pick ~25, verify QIDs via pipeline/catalog_wd, watch the
     Barnard-Castle trap: NY->Q60, DC->Q61, SF->Q62, Nashville->Q23197 all verified by 236a):
     Boston, Philadelphia, Baltimore, Pittsburgh, Cincinnati, Louisville, St. Louis, Chicago, Detroit,
     Cleveland, Milwaukee, Kansas City, Omaha, St. Paul or Minneapolis, Indianapolis, Columbus, Memphis,
     New Orleans, Charleston (SC), Richmond, Norfolk, Portland (OR), Seattle, Denver, Colorado Springs,
     Santa Fe, Albuquerque, Salt Lake City, San Diego, Los Angeles, Houston, Dallas, San Antonio,
     Little Rock, Atlanta, Birmingham, Savannah, Buffalo, Providence, Hartford, Albany, Worcester,
     Rochester, Wilmington (DE/NC), Fredericksburg.
  7. Tests: copy tests/test_src_us_cities.py 1:1 (same 4 tests, socket-blocked, three merge states,
     negative control, golden). Golden = tests/golden/src_us_birdseye_sample.json (module --golden).
     No network in tests, no fixed ports (only file + stdlib socket monkeypatch).
  8. Lead doc docs/lead_us_birdseye.md: 236a's structure - header (source + fetch route + licence +
     the shared-ids record for the four 236a cities), a QID-verification section (--verify transcript),
     a section per city (site point + STAGED/DROP per file with the exact reasons above), an offline
     check transcript. Record the loc.gov 403 fact there too (box 1: location/licence/how fetched).
- **Tests:** never ran this session (research only). Suite at loop start: 159 passed / 1 skipped /
  1 failed (test_fit_queue.py::test_placement_gestures_and_save_in_the_browser - pre-existing, agent a
  307 work on main; NOT this task).
- **NEXT (exact):** (1) view the 4 unchecked DC thumbs + the Henry Bill 1858 thumb in /tmp/aw236b_thumbs
  (chk_* + chk_1856_Henry_Bill_*); if /tmp is gone, re-pull from the titles above. (2) Write
  fit/src_us_birdseye.py: SITES table with ONLY new cities (the four shared ids hardcoded + read from
  extras_us_cities.jsonl for the loud-mismatch guard), SOURCES = the STAGED sets above (NYC 3, DC 2-3,
  SF 3-4, Nashville 1-4 per the decision), the extended known_sites() + check_staged() valid-set, the
  same stage/--check/--verify/--golden CLI as 236a. (3) Run --dry then real stage for the four cities
  (c.info + keep + caption gate live; fail loud on drift), write the lead doc, the test file + golden
  (--golden), --check offline. (4) THEN batches of ~5 new cities per session (search -> verify QID
  live via pipeline/catalog_wd -> one best view each -> stage) until >= 25 cities total, updating the
  lead doc per city. (5) Re-verify the dup-sheet calls (IA Goddard vs LOC 75693101; Taylor vs
  LOC 75694818; Henderson vs LOC 77696328) visually before dropping, one row per sheet (the Ratzer
  precedent).