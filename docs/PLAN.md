# Ancient Works: from private artifact to self-hosted site

Ethan chose (2026-10-10):

- Private, self-hosted on his Mac; reachable on the home LAN (phone on home Wi-Fi). No public build.
- Scope: US + Europe where open LiDAR exists.
- Images: historical depictions only for now (survey plates, old maps, historic aerials). The only modern
  layers are satellite imagery and LiDAR.
- Style stays the USGS-plate look (cream paper, serif caps, pastel legend swatches), not Espresso & Foil.
- He asked why only 15-20 full-depth sites. Answer: an effort guess. Each of the first six plates needed
  hand-traced walls, crop and blank boxes, sometimes control points, and per-site tuning. Not a data limit.

Proposed by Claude (not yet agreed):

- Remove the cap by extracting the wall template from the plate's ink automatically (phase 2). This is
  unproven; if it fails, plates go back to hand tracing at the old rate.
- Local models (Qwen3.8-27B vision on the AI box; Ethan: "if you want it") do classification and grunt work:
  page triage of scanned books, relief-crop triage per site, Finder pre-screen. Claude builds and checks.

The artifact database (plates/*, verdicts/*) was empty when checked on 2026-10-10: nothing to migrate.

## Phase 1: the site shell

- `server/serve.py` (stdlib only): serves `web/`, plus a small JSON document API under `/api/db/...`
  that replaces the artifact database (plate alignments, Finder verdicts). Documents live in `data/db/`.
  Default bind 127.0.0.1; `--lan` binds the Mac's LAN address; writes accepted only from private addresses.
- Serve `web/` directly (no copy into `dist/`; data grows to GBs). Vendor maplibre and three.js locally.
- Page: drop the claude.ai db, call the API through a shim with the same shape. Hash routes per site.
  Site list grows search + filters (region, culture, kind of work, kind of depiction).
- Live satellite imagery tiles (USGS imagery in the US, a global source elsewhere).
- Pre-built per-site products (relief, fitted plate sheet, block diagram) stay as they are.

## Phase 1b: live relief tiles (own phase: hardest engineering, not needed for more sites)

  - a **relief tile layer** served by `serve.py`: `/tiles/relief/{z}/{x}/{y}.png` fetches the bare-earth DEM
    for the tile plus a margin, removes the slope (same local relief model as the pipeline), caches to disk.
    Sources by area: USGS 3DEP (US), Environment Agency 1 m DTM WCS (England), AHN 0.5 m WCS (Netherlands),
    IGN LiDAR HD (France). Anywhere else: no relief layer.
  - Never one service request per 256-px tile (3DEP is slow and 5xx-prone): fetch DEM chunks per area,
    cache the DEM, cut tiles locally.

## Phase 2: many more US sites

- Site catalog seeded from Wikidata (CC0): archaeological sites that are earthworks, mounds, enclosures,
  hillforts, with coordinates, inside LiDAR coverage. Each entry: name, coords, kind, culture/period,
  sources, a short summary written by Claude from cited sources (local models do not write facts).
- Historical depictions per site:
  - survey plates from scanned books (Squier & Davis 1848, Lapham 1855, Thomas 1894, Fowke 1902), fitted;
  - USGS historical topographic quadrangles: TNM serves GeoPDF (needs GDAL, not installed) - check for a
    GeoTIFF format first. Most topos do not draw the works; they are context, not depictions;
  - historic aerials where a free source exists (phase 4).
- Plate pipeline at scale:
  1. Qwen triages every scanned page: plate or text, site name(s), transcribed title, scale bar and north
     arrow present, boxes around titles, legends and sections to blank out.
  2. Wall template made automatically from the plate's ink (instead of hand tracing), with Qwen's boxes
     blanked.
  3. Seed from site coordinates + scale bar + north arrow; wide automated search (rotation, scale, shift);
     per-feature warp where needed.
  4. Contact sheet of every fit against a null distribution; Claude accepts or rejects. Rejected plates are
     listed, never shown as fitted.
- Relief-crop triage: Wikidata coordinates for mounds are often hundreds of metres off or deliberately
  vague. Qwen classifies each site's relief crop (earthwork visible / nothing / modern feature / unsure)
  so bad coordinates are caught before any plate fit.
- Before any batch, Qwen's labels are checked against a hand-labelled sample; batch only if it holds up.

## Phase 3: Europe

- England (EA LiDAR, Historic England scheduled monuments as a seed list, Open Government Licence),
  Netherlands (AHN), France (IGN LiDAR HD + Cassini 18th c., Etat-major 1820-1866, 1950-65 aerials, all open).
- Other countries only where open LiDAR and open historical maps both exist; checked one at a time.

## Phase 4: historic aerials

- France 1950-1965 (IGN, open, georeferenced) is the sure source. US: no free, georeferenced, scriptable
  source verified yet (USGS single frames need an account and are not georeferenced); look at state GIS
  portals (Ohio, Indiana first) before promising any. UK aerial archives are mostly view-only: skip unless
  terms allow.

## Finder: looking for earthworks nobody has recorded (Ethan 2026-10-10: "lean into it")

Its own section on the site. Candidates stay on the Mac (gitignored), never on GitHub.
Where it stands: the ring scanner failed its pre-agreed test (Hopeton great circle #966, High Bank #729
of 7,231 on the test tiles; small natural rings flood the list).

1. Test set before any claim: known earthworks with good coordinates (catalog + fitted plates) as
   positives, random ground on similar terrain as negatives, held-out areas. Metric: recall at k per km2.
2. More detectors: mounds (1-10 m bumps, far easier than plowed walls), rings, squares and octagons,
   linear walls; then a re-ranking stage that gives a probability per candidate.
3. Re-ranker bake-off on the test set: Qwen3.8-27B (label probabilities from token log-probs) vs
   Cloudflare Clef-flash 9B (decision model: one probability per option in one forward pass, Qwen3.5-9B
   backbone with its vision encoder, Apache-2.0, released 2026-09-30) vs embeddings + a small trained
   head. Keep whichever separates known sites from random ground best.
4. Independent evidence per candidate: Mills 1914 Archeological Atlas of Ohio county maps (every mound and
   enclosure known in 1914 as red symbols; georeference + extract), old USGS topo "mound" labels,
   1930s aerials (Iowa), Squier & Davis plates, the catalog (known = not new).
5. "Lost" vs "new": a LiDAR feature at a Mills 1914 symbol that no modern public source lists is a lost
   site found again; a strong candidate with no record anywhere is a possible new one. Both get reviewed
   on the site (relief, aerial, historical layers side by side; verdict buttons).
6. Search areas: Scioto, Paint Creek, Little and Great Miami, Muskingum terraces (Ohio); Mississippi
   bluffs (effigy mound country, Iowa/Wisconsin); later England and the Netherlands.

## Not doing

- Ground photos, for now (Ethan: historical depictions only for now).
- A public build. The Finder and its candidates stay in this private site.
