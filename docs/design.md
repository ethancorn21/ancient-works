# Design: what the page implements today, against the USGS plate look

Written 2026-10-11 from `web/index.html` (1727 lines; the CSS is lines 10-225, the live server at :8642 serves
the same bytes), `web/review.js`, `web/fitqueue.js`, `web/vendor/fonts.css`, `DECISIONS.md`, `tasks/307`,
`tasks/308` and the owner's recorded words. Every value below is copied from those files; nothing is invented.
Visual summary: `docs/diagrams/07-design-sheet.svg`. The red overlay treatment is specified once, in
`~/code/projects/design/survey-red-ink.md`; this document references it and does not re-derive it.

## 1. Intent

The owner's reference (2026-10-10 00:17, sent from his phone): three USGS Professional Paper isometric block
diagrams, the Cerro Gordo, Empire Mine and Afterthought Mine plates. His decision, recorded in memory and in
`docs/PLAN.md` line 9: "Style stays the USGS-plate look (cream paper, serif caps, pastel legend swatches), not
Espresso & Foil." Read as a design brief that look is: cream paper as the ground of the whole sheet; flat pastel
fills with no gradients or shadows; small serif capital titles, tracked out; an EXPLANATION column with legend
swatches; thin brown strokes for every rule and edge; red kept for the ore bodies (here, the old survey ink).
This overrides the house style `~/code/projects/design/espresso-foil.md` for this project only. The page borrows
nothing from Espresso & Foil: no foil, no chrome rim, no pills, no dark theme, no E&F token values (`--ink`
`#2B2724` is not E&F's `#2B211C`). The one idea they share, calm surfaces with small loud labels, is done here
with ink-filled square chips instead of foil.

## 2. Tokens as implemented

Declared on `:root` (index.html L15-19). "Uses" counts `var(--x)` across the three web files.

| Token | Value | Uses | Where it appears |
|---|---|---|---|
| `--paper` | `#F3EDDC` | 7 | `body` background, `.group`/`.card` wells, `.entry:hover`, fit canvas, hatch swatch; also the favicon |
| `--paper-2` | `#EAE2CC` | 5 | `.step` box, pressed `.kinds` chip, current `.cand`, crop wells; the "Terps" kind colour (literal) |
| `--sheet` | `#F8F4E8` | 27 | `.panel`, `.sheet`, `.fitpane`, every button face, chips, `.tag`, plain marker, attribution at .85 |
| `--ink` | `#2B2724` | 55 | text, every 1px border, pressed tab and `.primary` fills; plus 14 literal uses in JS/canvas/SVG |
| `--ink-2` | `#6B625A` | 26 | italics, `.desc`, labels, `.strip`, hint text |
| `--rule` | `#8E8478` | 21 | hairlines: panel outline, `.group` border, `.fit-top` rule, disabled verdict text, compass ring |
| `--survey` | `#CE2E4E` | 18 | the overlay ink, and as UI accent: `.back`, `.links a`, focus ring, range `accent-color`, `.chip.found`, earthwork verdict, `.gpin`, `.pairs .bad`, t3 marker fill, `#rvcount` |
| `--mauve` | `#D8BCD5` | 7 | pressed `.seg`/`.deps`/fitpane buttons, `.pad` hover, `.chip.v-modern`; block north/south faces (literal) |
| `--mauve-2` | `#B996B6` | 0 | declared, never used by CSS; the value is hard-coded twice (block east/west faces `FACE.ew`, explain swatch) |
| `--pink` | `#F2B5C4` | 1 | `.swatch.urban`; hard-coded 3 times (kind "mottes", block cut face `FACE.cut`, section swatch) |
| `--aqua` | `#9ED8D8` | 3 | `.swatch.standing`, `.chip.v-unsure`, unsure verdict; kind "enclosures" (literal) |
| `--sage` | `#C4D9A6` | 3 | `.swatch.plowed`, `.chip.v-natural`, natural verdict; kind "linear" (literal) |
| `--lav` | `#CFC6E0` | 0 | declared, unused; kind "forts" hard-codes the same hex (L289) |
| `--ochre` | `#F2C48D` | 0 | declared, unused; kind "mounds" hard-codes the same hex (L289) |
| `--title` | `"Old Standard TT", "Century Schoolbook", "Iowan Old Style", Georgia, serif` | 11 | body, titles, serif buttons |
| `--label` | `"Archivo Narrow", "Arial Narrow", "Helvetica Neue", Arial, sans-serif` | 27 | caps labels, chips, tags, small buttons |

Hard-coded colours with no token (file, line): `#10141C` map/space background (L24, 1 use); marker tier fills
`#8A1230` t4, `#E2697F` t2, `#F4B4C0` t1 (L168-177, 2 uses each; t3 uses `--survey`); kind colours `#A9C4EC` walled
towns and `#F0E08A` lost gardens (L291, not in `:root`); Finder line colours `#6F8F4A` natural, `#8A6A88` modern,
`#3E9C9C` unsure (`VCOLOR` L1162, darker siblings of sage/mauve/aqua for lines on imagery); relief ramp
`#2E2622 -> #B0A492 -> #FBF7EC` (L72); block legend `#96807a -> #FAF4E4` ground, `#C4DEDC` water (L1439-1440);
fit-canvas crop dim `rgba(243,237,220,0.72)` (= paper at 72%, L947); hollow pin `rgba(248,244,232,0.9)` (= sheet,
L953); white `#fff` text on survey-red chips and pins (4 uses); shadows `rgba(43,39,36,.18/.2/.25)` on panel, sheet,
fitpane (= ink at low alpha, the only shadows on the page).

Spacing and radius: no radius anywhere except `.swatch.dot`, `.kinds i`, `.gpin` (50%); every box is square.
12px page margin (`top/left/bottom: 12px`); panel padding `12px 14px 18px`, body gap 14px, `.group` padding
`11px 12px` gap 9px; `.entry` grid `34px 1fr` gap 10px; 1px `--ink` border plus a 1px `--rule` outline offset 3px
on `.panel` and `.sheet` (the double plate border); `.tabs`/`.seg` are bordered grids with 1px inner dividers.

## 3. Typography

Fonts are vendored (`web/vendor/fonts.css`, woff2, latin + latin-ext, `font-display: swap`): Old Standard TT
400, 400 italic, 700; Archivo Narrow 400 and 600. Finding: the two Archivo Narrow 600 files are byte-identical to
the 400 files (md5 `b8e61cea...` and `3c9c547f...` for both weights), so every `font: 600 ... var(--label)` rule
(27 uses) renders at regular weight and the three `700` label uses (`.gpin`, `.marker.t4 .tag`, canvas pins) get a
synthetic bold. Sizes as set: `body` 15px/1.5 serif; `.wordmark` 700 22px caps tracking .14em; `.site-title` 700
20px caps .1em; `.caption h2` 400 15px caps .14em; `.section-title` 600 11.5px label caps .16em; `.group-title`
600 11.5px .14em with a `--rule` underline; `.caps`/`.strip` 11px .09em; `.tabs`/`.back` 600 12px .08-.1em;
`.tools`/`.chip`/`.tag` 600 10.5-11.5px .05-.08em; `.seg`/`.deps` buttons 13.5px serif (not caps); italics for
`.tagline` 13.5px, `.desc` 13px, `.fit`/`.source` 13px, `.site-aka`, `.lede`. Numbers use `tabular-nums` in
`.val` and `.ramp-labels`. This matches the brief (serif capitals for titles, condensed caps for labels).

## 4. Map and markers

Base (L304-329): MapLibre 5.6.0 globe projection, one raster source, Esri World Imagery to z19, atmosphere blend
1 at z0-5 fading to 0 at z7, space colour `#10141C`, start `center [-35, 45] zoom 2.3`, maxZoom 18. Per the
decision of 2026-10-10 night the plate-style vector base was removed ("satellite global all the way out is better
and way faster"); `pipeline/world_plate.py` and `web/data/world.jpg` are left over and unused. Live relief tiles
(`tiles/relief/{z}/{x}/{y}.webp`, z12-17, one source per national DEM) show only when ground = relief and the
DEM's box is on screen. Layer order: sat, relief-*, per-site `rel-<id>`, `dep-<id>`, `paper-<id>`, `ink-<id>`,
`fit-prev`, Finder crop/rings/dots, Amazon tiles and marks. Controls: NavigationControl top-right and a compact
AttributionControl bottom-right, restyled square with `--sheet` faces and 1px `--ink` borders (L181-183).

Markers (L159-200, L477-535) are DOM `<button class="marker tN">` elements, anchor `bottom` (the pin's tip is the
site's coordinate), holding a `.sq.pin` map pin (inline svg `PIN`, 72x100 frame, paper eye) and a `.tag` label. Tier
from `build_site` score: `TIERS = [[2.5,'t4'],[1.6,'t3'],[1.2,'t2'],[0.01,'t1']]`, else `plain`. Pin sizes (w x h) and
fills: t4 14x19 `#8A1230`; t3 12x17 `--survey`; t2 11x15 `#E2697F`; t1 9x13 `#F4B4C0`; plain 7x10 `--sheet` (ink eye);
one non-scaling 1.2px ink outline. `PIN_W`/`PIN_H` in the script repeat the sizes for the label collision boxes. Today's
sites.json: 385 sites, t4 3 (Bergues 1545, Old Sarum 1761, Mayburgh 1769), t3 11, t2 12, t1 251, plain 108; plain shows
only with "More sites". Labels (`.tag`, an EU direction sign: 20px tall `--sheet` box with the left end pointed at the pin, 1px ink outline
made by clipping the ink box and its `::before` paper face to the same polygon, 600 11px caps .08em) appear from zoom `LABEL_FROM = {t4:0,
t3:3, t2:5, t1:7, plain:9}` and hide on collision, higher tiers placed first; the open site's own pin hides.
Clicks land only on the pin or a showing label (`pointer-events`). Red rule: a site is coloured when any
overlay is at least 150 years old (plans and drawings of any age, surveys only if >= 150 years). Finder scan
areas reuse `.marker.scan` with a dashed square; catalog pins are not on the map (owner: "we shouldn't be
pinning every single earthwork in the world").

## 5. Overlays: ink and paper

Each fitted picture ships as two files per site (`data/sites/<id>/`): the original scan (`paper`) and a transparent
RGBA ink version in one flat colour `#CE2E4E`. Both are MapLibre `image` sources on the same four corners;
`applyLayers`/`applyDep` toggle visibility by `S.plateMode`/`S.depMode` (`ink` | `paper`) and set `raster-opacity`
from `S.plateOpacity`/`S.depOpacity` (default 0.85, persisted in localStorage), `raster-fade-duration 0`,
`raster-resampling linear`. Every site opens on the aerial photograph with the drawing in ink (`select()`, L805-807).
The fit tool makes the same ink in the browser (`makeInk()` L962-982: paper = 85th percentile grey, ink = 2nd,
gain 1.35, offset -0.18, exponent 0.9, capped at 2048px) and previews it as `fit-prev` while points are pinned.
Why one crimson works on green ground, its limits and the rules (one colour, no fills, hairline, graded alpha,
normal compositing) are in `survey-red-ink.md`; the page follows them. The 3D block (L1329-1495) lays the ink
texture on the LiDAR surface with `polygonOffset` and `renderOrder 2`, faces `FACE = {ns 0xD8BCD5, ew 0xB996B6,
cut 0xF2B5C4, ink 0x2B2724}`: the one place the page is literally a pastel block diagram with ink edges.

## 6. Panels and layout

Fixed elements (desktop, > 760px): `.panel` left 12px, top 12px + safe area, bottom 12px, width 370px, z 2, the
EXPLANATION column; `.fitpane` (old plan page) absolute, left 398px, width `min(46vw, 780px)`, top/bottom 12px,
z 6; `.sheet` (block diagram) left 396px to right 12px, z 3, grid `auto 1fr auto` with a 230px explain column.
Map padding left 390 so flights centre in the free part. Marker z 1-4 inside the map's own stacking context.

    globe idle                        site open                         place mode (fit tool)
    +------+---------------------+    +------+---------------------+    +------+-----------------+----+
    |strip |  .  globe on #10141C|    |< ALL | aerial photo        |    |< site| .fitpane  z6    |map |
    |WORD- |   .    .            |    |TITLE |   ink overlay       |    |TITLE | book page scan  |    |
    |MARK  |  .  sat tiles   .   |    |Map|Bk|  (site square hid)  |    |seg   | crop dashes     |    |
    |tabs  |     . squares .     |    |Ground|  red pins (.gpin)   |    |.step | pins 1..n       |    |
    |tiers |  .      .   .       |    |Plate |                     |    |tools | +/- Whole Crop  |    |
    |kinds |         [+][-][N]   |    |Draw- |                     |    |SAVE  |                 |    |
    |search|                     |    |ings  |                     |    |cite  |                 |    |
    |list  |      attribution .. |    |Plans |      attribution .. |    |      |                 |    |
    +------+---------------------+    +------+---------------------+    +------+-----------------+----+
     370px    map               1440    370    map                       370    min(46vw,780)   ~380px

    review queue (review.js)          Finder (scan)                     block view (.sheet z3)
    +------+---------------------+    +------+---------------------+    +------+---------------------+
    |Sites|Finder               |    |< ALL | dashed scan box     |    |strip | plate - 1848  [Back]|
    |Review (N)   (full row)    |    |TITLE | rings: dashed todo  |    |      +---------------+-----+
    |lede italic                |    |.card | solid judged, VCOLOR|    |Map|Bk|   3D block    |EXPL-|
    |site  "n candidate pics"   |    |crop  | dots below z12.5    |    |      |  pastel faces |ANA- |
    | [plan button]             |    |verd. |                     |    |      |  ink edges    |TION |
    | [plan button] <small>     |    |Known |                     |    |      | compass  hint |keys |
    |site  "no picture found"   |    |Cands |                     |    |      +---------------+-----+
    | chip.missed  [Open search]|    |about |                     |    |      | CAPTION h2 caps     |
    +------+---------------------+    +------+---------------------+    +------+---------------------+

The home card "Ready to fit" (`#fqcard`, fitqueue.js) is injected after the stats line with its own `<style>`:
`--sheet` box, 1px ink, `.primary` = ink fill. The Review tab spans the tab row (`grid-column: 1 / -1`).

## 7. Motion and feedback

No CSS transitions or keyframes at all. Hover: `.entry` gets a `--rule` border and `--paper` fill; buttons turn
`--mauve`. Pressed state is `aria-pressed` with ink or mauve fills. Focus ring 2px `--survey` offset 2px. Camera
moves are MapLibre flights: `select` 4500ms (4000 for catalog), `zoomOut` 2500ms to zoom <= 5, fit-pane
`easeTo` 900ms, Finder 3500/1800/1500ms; all `essential: true`, so `prefers-reduced-motion` is not honoured. The
block redraws only when `dirty`. Status text (`.status`, `#fitst`, `#vsaved`) is the save feedback: "Saving...",
"Saved.", "Could not save (code)". Keyboard: 1-4 verdicts, j/k next/previous candidate, Escape drops a pending pin.

## 8. Mobile (the owner opens it on a phone on home Wi-Fi)

`narrow()` = `max-width: 760px`. The panel becomes a bottom sheet: `max-height 54%`, top border only, a 44x5px
`--rule` grab bar; `.collapsed` leaves `92px + safe-area`. The block sheet goes full screen with the explanation
stacked below the stage at `max-height 32vh`. The fit pane takes the top half (`bottom: 50vh`, full width) and
auto-minimises to its header once a plan point is pending so the map can be tapped (L1116, L1091). Map padding
is `bottom: innerHeight * 0.5`; site flights zoom 14.2 instead of 15. Touch: `touch-action: none` on the fit
canvas and block stage, one-finger drag in align mode, pinch zoom on the block. `viewport-fit=cover` and
`env(safe-area-inset-*)` on panel, sheet and strip. Not handled: marker squares are 7-15px tap targets; in place
mode the fit pane (top 50vh) and the open panel (bottom 54%) together cover the whole map until one is closed.

## 9. Gaps between intent and implementation

Severity: HIGH = the owner has complained or the task is open; MED = visible drift from the brief; LOW = hygiene.

- HIGH, place-mode clutter (task 307; `.fitpane` L100, `openPlan` L929-931). The page scan takes
  `min(46vw, 780px)` next to a 370px panel, leaving about 380px of map at 1440 wide (250px at 1200). Owner:
  "it's super cluttered ... there's like no working space"; "when I go to place the plan onto the map it already
  needs to be overlaid onto the map ... I can move it around I can scale it around ... instead of click on the
  point and then click on the map ... three points. It should already be on the map ... then pinpoint this exact
  spot to here"; "the overlay that's already there doesn't disappear from the map ... you have two overlays. As soon
  as you go into that place mode the already placed overlay needs to go"; "it'll move near it but it does not
  accurately move over". Fix: put the ink preview on the map first (a draggable `fit-prev` with handles), open the
  pane in its existing `.min` state as a reference thumbnail, hide `dep-*`/`ink-*` layers while `P.active`.
- DONE (superseded 2026-10-13: the arrowhead read as a heart, now a map pin + pointed sign label), markers are squares, not arrowheads (task 308; L165-178, L471). Owner: "instead of the squares we're going
  to move to a new shape ... keep the color gradient and all that stuff ... like an old arrowhead ... a notched
  arrowhead ... it would need to be small though, like a contracting stem arrowhead". The marker also anchors at
  `left` with offset `[-6, 0]`, so the coordinate is the square's centre, not a tip. Fix: an inline SVG silhouette
  per tier, anchor `bottom`, keep the five fills and the 1.5px ink stroke; the collision box in `syncMarkers`
  (16px) then needs the new height.
- HIGH, phone place mode has no map (L108 + L214). Fit pane `bottom: 50vh` and panel `max-height: 54%` overlap by
  4%; the map is reachable only because the pane minimises on a pending pin. Fix: collapse the panel to the grab
  bar when `P.active` on narrow screens, or pane 40vh + panel 50%.
- MED, Archivo Narrow 600 is the 400 file (`web/vendor/fonts/ArchivoNarrow-600-*.woff2`, md5 identical to 400).
  All 27 semibold label rules render regular; the brief's "small loud labels" are quieter than designed. Fix:
  re-fetch the real 600 woff2 from Google Fonts, or declare only 400 and let 700 synthesise.
- MED, the page is paper only in the panel. The brief's cream ground is now a satellite globe on `#10141C` space
  (decided, do not change). The header comment L11-12 ("Full-bleed globe on paper") predates that decision. Fix:
  rewrite the comment; keep the paper frame honest by leaving the cream attribution bar and controls as they are.
- MED, the red accent carries two meanings. On the plates red is the ore body only; here `--survey` is also back
  links, focus ring, range thumb, "Found" chip, the earthwork verdict and `.pairs .bad` (a residual > 15 m). The
  survey-red-ink.md fit section says this is tolerable only inside this override, but red for "bad" and red for
  "the ink" sit in the same fit view. Fix: `.pairs .bad` as 700 ink, keep red for ink, navigation and the found/
  earthwork meaning (it is the one thing the red overlay also means: the work is there).
- MED, strokes are near-black, not brown. `--ink #2B2724` is a warm black and `--rule #8E8478` a grey taupe; the
  reference plates' thin brown lines are not matched. Unverified: the plates were not available to measure. Fix:
  measure a plate scan and, if it reads brown, shift `--ink` toward it in one place.
- LOW, pastel tokens duplicated as literals. `--lav`, `--ochre`, `--mauve-2` have 0 CSS uses; `KGROUP` L289-291,
  `FACE` L1331 and the explain swatches L1439-1443 hard-code the same hexes, plus two kind colours (`#A9C4EC`,
  `#F0E08A`) that exist nowhere else. Fix: one JS palette read from `getComputedStyle(document.documentElement)`.
- LOW, no reduced-motion path: 4.5s essential flights and no `prefers-reduced-motion` query. Fix: shorten
  `duration` when the query matches.
- LOW, the screenshots in `docs/site_flow/` show the removed Natural Earth base, catalog dots and squares; 307 and
  308 both require fresh before/after shots at 1440x900.

## 10. What NOT to change

- The survey-red ink overlay: "that cool red ink overlay" (2026-10-10); plates and old maps default to ink mode.
- The satellite globe all the way out: "satellite global all the way out is better and way faster"; the plate-style
  vector base was tried side by side and lost (d939bd2 holds it if ever wanted).
- The manual fit tool is "certified cool"; keep it prominent as the trusted fit path (its UI may be reworked per
  307, its prominence may not).
- Survey sheets and aerials listed open under their own heading, never folded away again: "just as cool" (OS
  six-inch over Maiden Castle, 2026-10-11).
- The 150-year rule for plain surveys: "I want age to show how much nothing has really changed over the last
  couple hundred years"; drawings of the works stay whatever their age.
- The tier colour gradient and sizes ("keep the color gradient and all that stuff"); the score "looks good so far".
- Every site opens on the aerial photograph with the drawing in ink; catalog earthworks stay off the map.
- Single light paper theme (`color-scheme: light`, "Single paper theme, by design", L12); no dark mode.
