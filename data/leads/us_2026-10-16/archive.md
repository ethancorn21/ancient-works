# Old maps that draw the US sites' works: archive and map sources (2026-10-15/16)

Scope: the non-book side (plats, charts, manuscript and printed maps) for the 96 non-town US sites in
`us_sites.tsv`. Rows that passed the evidence check are in `archive.jsonl`. Every row there was opened and looked at:
the image was downloaded, the label was read on the image, and the licence basis is stated. Downloads, intermediate
JSON and the scripts' outputs are under `archive_dl/`. The scripts are in `../archive_scripts/` (scratchpad).

## Result in one table

| family | access works programmatically? | sites checked | hits (rows) |
|---|---|---|---|
| 1. BLM GLO survey plats | yes, after reverse-engineering the 2026 portal (below) | 56 sites in PLSS townships queried, 48 with plats, plats for 48 sites downloaded (129 PDFs), about 42 sites viewed | 4 verified: Turtle Mound, Mound Key, Poverty Point, Mounds State Park |
| 2. County atlases / plat books | partly (LoC JSON then Cloudflare 429; IA search works, but few scanned atlases for our counties) | LoC keyword and place search; IA title search for 35 counties | 0 county-atlas hits; 1 town plan (Marietta 1837, LoC) |
| 3. Smithsonian NAA / Thomas mound-survey manuscripts | no (api.si.edu DEMO_KEY rate-limited after a few calls; NAA records are not in the Open Access set; SOVA and collections.si.edu return 403 to scripts) | finding aid MS 2400 identified only | 0 |
| 4. Military / federal surveys (OR Atlas, Shiloh commission, MRC, Coast Survey) | NOAA historical charts: yes (undocumented PHP endpoint, below); Shiloh NMP maps: via Commons (NARA uploads) | Shiloh (2 NARA maps), Turtle Mound (NOAA chart 160 of 1911) | 0 (maps found, mound not drawn or not legible) |
| 5. Wikimedia Commons (P373 categories + full text) | yes (Wikidata + Commons API) | 96 sites: 64 categories, 1,943 candidate files, 101 pre-1931 map/plan candidates after filtering | 2 likely (Portsmouth: Biggs, Horseshoe Mound) via Hempstead 1878; rest are book plates (S&D, Thomas, Fowke) the book agents already cover |
| 6. LoC Geography & Map manuscript maps | LoC JSON API works until rate-limited (HTTP 429 Cloudflare challenge after about 40 requests) | keyword + 30 place-name searches | 1 verified (Marietta 1837, two rows: mound-cemetery and marietta) |

Total: 8 rows (6 verified, 2 likely) covering 8 sites, 6 of which have no picture today (Turtle Mound, Mound Key,
Poverty Point (pictures unplaced), Mounds State Park, Biggs, Horseshoe Mound) plus Mound Cemetery (pictures unplaced)
and Marietta (has an overlay).

## 1. BLM GLO Records (glorecords.blm.gov): the family worth a pipeline

### How access works now (it changed)

The old `glorecords.blm.gov/results/default.aspx?searchCriteria=...` URLs now 301 to `/s/`, a Salesforce Experience
Cloud site. The search UI is an iframe app at `glo-entry-prod.blm.gov/ui` (Next.js) that calls a JSON API with a
Bearer token. The token is the one the public site hands every anonymous visitor:

1. Guest token: `POST https://glorecords.blm.gov/s/sfsites/aura?r=1&aura.ApexAction.execute=1` (form-encoded)
   with `message={"actions":[{"id":"1;a","descriptor":"aura://ApexActionController/ACTION$execute","callingDescriptor":"UNKNOWN","params":{"namespace":"","classname":"DSASController","method":"getToken","params":{},"cacheable":false,"isContinuation":false}}]}`,
   `aura.context={"mode":"PROD","fwuid":"<fwuid from the /s/ page's inline.js URL>","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":"<value from same URL>"},"dn":[],"globals":{},"uad":false}`,
   `aura.pageURI=/s/`, `aura.token=null`. The reply holds `returnValue.returnValue.context.token` (a JWT with role
   `public`) and `url: https://glo-entry-prod.blm.gov/ui`. The fwuid changes when Salesforce releases; read it fresh
   from `https://glorecords.blm.gov/s/` each run. Keep the token in a file and never print it. (The token file used in this run, archive_dl/glo/.tok, was deleted;
   rerun step 1 to get a new one.)
2. Search: `GET https://glo-entry-prod.blm.gov/ui/func/dsto/api/search?q=*&page=1&pageSize=100&geostatecodes=IL&meridians=03&townships=0020N&ranges=0090W&documenttype=Survey`
   with `Authorization: Bearer <token>`. Facet codes: meridians are the BLM 2-digit codes (the same as CadNSDI
   `PRINMERCD`); townships and ranges are `%03d0` + direction (T2N = `0020N`; the trailing 0 is the fraction digit).
   `.../api/facets?keys=documenttype,surveytype,State` lists facet values. Document types: Survey, Patent, CDI,
   Tractbook. Survey types include Original Survey, Survey of Islands, Diagram, Supplemental Plat, Private Claim.
3. Images: each search document carries `fileNameFull` (a PDF on `blm-azfun-dsvc-entry-prod-eus2-001.azurewebsites.net`
   with an embedded public `access_token`). That host answers 403 "Ip Forbidden" to direct calls. The same path works
   through the proxy `https://glo-entry-prod.blm.gov/ui/func/dsto/api/image/pdf/survey%2F<documentID>%2F<documentID>.pdf?access_token=...`
   (swap the host and prefix `ui/func/dsto/api/`). One page per PDF, about 1-12 MB. macOS `sips` renders it to
   JPEG/PNG at any size (6000 px is enough to read labels).
4. PLSS lookup for a site: `https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/1/query`
   (township; fields PLSSID, TWNSHPNO, TWNSHPDIR, RANGENO, RANGEDIR, PRINMERCD, STATEABBR) and `/2/query`
   (section; FRSTDIVNO). Point query, `inSR=4326`, `f=json`. The server sometimes returns HTTP 500; retry.

Scripts: `archive_scripts/plss.py` (PLSS per site), `glo_search.py` / `glo_full.py` (search per township),
`glo_batch.py` (download + render), results `archive_dl/plss.json`, `archive_dl/glo/glo_full.json`,
`archive_dl/glo/glo_ids.txt` (documentID, plat accession, surveyor, date per plat).

This is the site's normal anonymous path (the guest token is what any browser visitor gets), not a login. A
hard-coded "dev" token also sits in the iframe bundle; it was not used.

### Coverage

- PLSS lookup for 96 non-town sites: 57 fall in a PLSS township. No PLSS: Kentucky, Tennessee, Georgia, Texas, West
  Virginia, South Carolina, the Virginia Military District of Ohio (Ross, Highland, Adams, Greene and the rest), and
  several Spanish/French claims (LSU, Pyramid Mound/Vincennes, Safety Harbor, Madira Bickel, Indian Mound Park AL).
- 56 township queries, 48 returned survey plats (186 documents). Zero for 8 Ohio townships in the Ohio River
  Survey/Congress Lands (Marietta, Mound Cemetery, High Bank, Hodgen's, Piketon, Horseshoe, Zaleski, Arledge). BLM does
  not hold most Ohio originals (they are with the Ohio Auditor of State), so Ohio is mostly a GLO gap. The Ohio plats
  that do come back (Newark, Alligator, Hopeton, Miamisburg, Norwood) are 1800s blank range sheets with no features.
- Downloaded 129 plats for 48 sites and viewed the distinct ones (many are microfilm duplicates; a 16x16 average-hash
  grouping found the duplicates).

### Hits (all in archive.jsonl, verified on the image)

| site | plat | what is drawn |
|---|---|---|
| Turtle Mound FL | T18S R35E, H. Washington 1844, approved 1845 (Survey-12389) | hachured symbol labelled "Turtle Mound" between Eastern Channel and the Atlantic |
| Mound Key FL | island survey T46S R24E Sec. 36, W. E. Loper 1889 (Survey-15187) | island meander "KEY MOUNT", lots 1-4, symbol labelled "Mound" in lot 4 |
| Poverty Point LA | T19N R10E, A. Van Dorn resurvey 1848 (Survey-78687) | hachured symbol "Indian Mound" on the Sec. 11/14 line by Harlin Bayou |
| Mounds State Park IN | T19N R8E, B. Bentley 1821 (Survey-458033) | ring symbol "Mound & intrenchment" on the Sec. 15/16 line |

### Viewed, nothing drawn (useful as negative evidence)

Aztalan (1836 plat: Crawfish River, no works), Cahokia (two plats: 1818 copy shows Cahokia commons, ponds, prairie;
no mounds), Emerald Mound IL, Kincaid (blobs near the site are timber/thicket symbols, not mounds), Lizard Mound,
Grand Mound (1882: Big Fork mouth, no mound), Indian Mounds Park St Paul (18 plats incl. 1847-1861; the bluff group is
not drawn), Winterville, Jaketown, Holly Bluff, Aden, Batesville, Pharr, Pocahontas, Tallahatchie, Nanih Waiya,
Emerald Mound MS (private-claim plat), Marksville (1857), Watson Brake (1825), Frogmore, Plum Bayou/Toltec (1827 plat
draws "Lake or Mound Pond" but no mounds), Parkin, Battle Mound (Sec. 3 shows "McGuyer's Field" only), Moundville
(1820s), Fort Walton (two "Pond" ovals, no mound), Letchworth-Love, Lake Jackson, Bottle Creek (Mobile River plat;
the Tensaw delta site is not drawn), Florence AL (state-certified copy), Fort Toulouse (draws "Fort Jackson", the
fort site, not the mound), Crystal River (1835 and 1926 supplemental: river only), Portavant, Spiro (1898 USGS-made
plats; drawn with vegetation and fields, no mounds visible at the site), Angel Mounds (1806 Ohio-front fraction only),
Newark, Alligator, Hopeton, Miamisburg (1802), Norwood.

Also viewed, nothing drawn at the site: Halvorson (1835, T8N R9E: marsh and 4th Lake, no mounds), Fudge (1811 Fowler blank grid; one oval on the Sec. 10/15 line, not the site's Sec. 17).

Not yet viewed (downloaded or listed): Velda, Sinnissippi, Blackhawk, the extra Mound Key/Turtle
Mound resurveys and diagrams, Survey-78689 (Poverty Point 1856 resurvey), Survey-458035 (Mounds State Park).

### Hit rate and why it is still the best family

4 of about 42 sites viewed (about 10%), all four verified, and each plat comes with a free placement frame: the section
lines, corners and chainages on the plat are the same lines the CadNSDI section polygons give today, so a plat can be
seeded from the PLSS polygon (scale, rotation, window) before any image matching. Mound Key's island meander and
Poverty Point's section-line position are especially strong. Federal = public domain, no licence question. Field
notes (the surveyor's line-by-line text) are also in the system and would mention "mound" even where the plat does
not; they were not checked here.

Pipeline sketch: PLSS per site -> GLO search (Survey, original + islands + diagrams) -> download + render 6000 px ->
crop the site's section +-1 section (we know the section from CadNSDI) -> vision check for a mound/fort label in the
crop -> human confirm. Cropping by section cuts viewing cost by about 36x.

## 2. County atlases and plat books (Beers, Everts, Andreas, Lake)

- LoC JSON API: `https://www.loc.gov/maps/?q=<terms>&fo=json&c=100&sp=<page>&dates=1600/1930`; item detail
  `https://www.loc.gov/item/<id>/?fo=json` gives `resources[].image` and the IIIF service; full image via
  `https://tile.loc.gov/image-services/iiif/<service>/full/pct:50/0/default.jpg`. After roughly 40 requests loc.gov
  returned HTTP 429 with a Cloudflare challenge and stayed blocked for over an hour; tile.loc.gov (IIIF) kept working.
  A pipeline needs about 1 request per 3-5 s and backoff.
- Keyword searches ("Indian mound(s)", "ancient works", "earthworks", "shell mound", "mound", "tumuli") hit catalogue
  text, not map text, so they find maps whose notes mention mounds. Found: 1837 Harmar and Marietta (row), 1863 Coast
  Survey map of Porter's Deer Creek expedition ("Indicates ... Indian mounds" - viewed; the label "Indian Mounds" is at
  the Rolling Fork / Deer Creek junction, not at one of our sites), 1859 Map of Sauk County WI, 1882 Hardesty
  Wood/Pleasants WV atlas, Thomas 1894 distribution map (state scale).
- Place searches turned up, not viewed because of the 429 block: Topographical map of Ross County, Ohio (1860, LoC
  2012592235, the best candidate for Ross County works at farm scale), Portsmouth 1841 (2024593584), Map of Portsmouth
  and Wayne Township 1868 (2016586531), Bryan's Portsmouth 1889 (2016586535), Moundsville WV 1899 bird's-eye
  (75696686), Map of St. Clair County IL 1863 (2013593093), Topographic map of the Parish of Concordia LA 1841
  (2012592311), Map of the battlefield of Shiloh 1920 (99448457). These are the next LoC checks.
- Internet Archive: advanced search by title finds few scanned county atlases for our counties (Adams OH 1880,
  Montgomery OH 1919, Clinton OH 1873-1925, Washington OH 1874, Madison IN 1912, Randolph IN 1909, Marshall WV
  1907/1928, St. Clair IL 1897/1916). No OCR of map labels, so each needs page viewing. David Rumsey's items are on IA as
  `dr_*` image items; a title search found the 1796 "Plan of an Old Fort in the state of Kentucky" (Lexington area,
  not checked against Mount Horeb) and the 1872 Ohio ancient-works state map (state scale).
- Commons mirrors many Rumsey/LoC county maps (search the exact LoC title). Checked: J. W. Holmes, Map of Saint Clair
  County, Illinois, 1863 (Commons, from Rumsey 3751.001, 18299 x 16587 px, public domain): farm-owner map; the
  Cahokia townships (T2N R9W/R10W) show owners, the Ohio & Mississippi R.R. and the oxbow lakes but no mound symbols.
  The 1860 Ross County topographical map is not on Commons or IA under its title.
- Hit rate for farm-plat atlases: 0 so far; the family is slow (manual page viewing) and LoC throttles.

## 3. Smithsonian NAA / Cyrus Thomas Mound Survey manuscripts

- `api.si.edu/openaccess` with DEMO_KEY returned results for library (SIL) records, then OVER_RATE_LIMIT. NAA
  manuscript maps are not in the Open Access dataset (unit searches for NAA returned 0).
- SOVA (`sova.si.edu`) and `collections.si.edu` return 403 to scripted requests. The finding aid for NAA MS 2400
  (Division of Mound Exploration records, 1881-1889, 11 boxes) exists as a PDF at `sirismm.si.edu/EADpdfs/NAA.MS2400.pdf`
  but its text streams are compressed and no PDF text tool is installed here, so its folder list was not read.
- Needs: a personal api.si.edu key (free, from api.data.gov) and a browser for SOVA. Rights: NAA items usually say
  "Usage conditions apply"; unpublished federal (BAE) work would be public domain, but each item must be checked.
- Hit rate: unknown (not reached). Worth one manual pass for Thomas-era sites with no published plan.

## 4. Military / federal surveys

- NOAA historical charts and T-sheets: the site `historicalcharts.noaa.gov` has an undocumented point search:
  `GET https://historicalcharts.noaa.gov/includes/imageDBDT.php?title=&chart=&yearMin=1830&yearMax=1930&singleYear=&type=Any Type&state=Any&scale=All Scales&latitude=<lat>&longitude=<lon>&js=yes`
  (type must be one of the select values, e.g. "Any Type", "T-Sheet"; scale "All Scales"). It returns an HTML table;
  the file id is in `<span id=d<FILEID> ...>`. Download: `includes/downloadsingle.php?filename=<FILEID>&fileExt=.jpg`
  (full-resolution JPEG, e.g. 13602 x 14741 px, 20 MB). Tested at Turtle Mound: Coast Chart No. 160 "Halifax River to
  Mosquito Lagoon" (1911 special edition, first published 1881). Viewed at full resolution around Eldora: no
  "Turtle Mound" label found. T-sheets are listed only if the type is set to T-Sheet; the T-Sheet query at Turtle Mound
  returned none. Not run for Crystal River, Mound Key, Sewee, Indian Mound Park, Bayou Grande Cheniere. Charts are
  federal = public domain.
- Shiloh: Commons has NARA scans of "Map of Shiloh National Military Park ... Corinth to Pittsburg Landing" (Atwell
  Thompson, 1901, 8084 px) and a Civil War "Map of the Battle Field of Shiloh" (NARA 70653109). Both viewed; both are
  regional (miles to the inch) and do not draw the mound group. The large-scale park commission battlefield maps
  (1900-1901, which show "Indian Mounds") were not found online in this pass; LoC 99448457 (1920) is the lead.
- Official Records Atlas (1891-95): on IA as `atlastoaccompany00unit` (from lead_us_mounds.md); not checked for the
  Tallahatchie crossing works in this pass.
- Mississippi River Commission 1880s charts: not checked.

## 5. Wikimedia Commons

- Method: Wikidata `wbgetentities` for the Q-ids in the site_ids -> P373 category -> category members (1 level of
  subcategories), plus Commons full-text search `"<site name>" (plan OR map OR plat OR survey)`, then `imageinfo` with
  extmetadata to filter by date (<= 1930) and keyword. Files: `archive_dl/commons_cand.json`,
  `archive_dl/commons_meta.json`, `archive_dl/commons_filtered.txt`.
- 64 of 96 sites have a Commons category. 101 filtered candidates; almost all are S&D 1848 / Lapham 1855 / Thomas
  1894 / Moore plates already in the book pipeline, or unrelated (Boston "Fort Hill" maps matched the forthill name).
- New: Hempstead 1878 "Earthworks, Portsmouth, Ohio" (J. Anthrop. Inst. VII Pl. IV), a town-plan-scale map of the
  whole Portsmouth group with street grid and railroad: rows for Biggs and Horseshoe Mound (likely; see notes).
  "Fig. 1" Etowah plan from the 1883 compilation "Anthropology" (Commons File:98- FIG 1-map.jpg) is a book figure
  and was left to the book agents.

## 6. LoC manuscript maps (French/Spanish fort plans, Natchez)

- Found by keyword: "Map of the Two Natchez Forts ... 1730" (2021668647), "Plan of the Natchez Fort ... 1731"
  (2021668646) - these are the Natchez/Sicily Island forts of 1730-31, not Emerald or Selsertown. "Coupe et profil de
  la redoute de Rosalie au Natchez 1732" (2002622706) - Fort Rosalie, not a mound site in our list. Not viewed (429).
- Fort Toulouse 1751 and Fort Watson plans: not found by LoC keyword search before the block.

## What failed, in short

- Claude in Chrome was not connected, so browser-only sites (SOVA, collections.si.edu) were not reachable.
- loc.gov rate limit (Cloudflare 429) stopped LoC item lookups mid-run.
- api.si.edu DEMO_KEY rate limit.
- NOAA's `nosimagery.noaa.gov` survey_scans directory did not answer; the historicalcharts.noaa.gov endpoint did.
- No PDF text tool installed (pdftotext / pypdf missing), so finding-aid PDFs were not read.

## Recommendation

Build the pipeline for GLO plats first (federal, free placement frame from PLSS, 10% hit rate so far, scriptable end
to end now that the token flow is known), and add GLO field notes in the same pass. Second: LoC town plans and county
maps with a throttled client (one verified high-value hit from about 40 requests). Commons and NOAA are cheap
add-on checks; NAA needs an API key and a browser.
