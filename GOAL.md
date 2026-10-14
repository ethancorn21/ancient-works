# Ancient Works: an old drawing on every site

Ancient Works is a map of old earthworks, castles, Roman forts, walled towns and lost gardens. Each built site shows
today's ground (LiDAR relief where there is open LiDAR, the aerial photograph everywhere) and, on top of it, old
pictures of the place. What makes a site worth opening is an **old drawing of the structure itself** (an
antiquarian plan, a survey plate, a castle plan, a town plan, a bird's-eye view, an artist's aerial view) laid over
today's ground, so you see
how little has changed. Plain survey sheets (Ordnance Survey, Cassini) do not count; they are background.

Today 25 of 384 built sites have such a drawing fitted. The owner wants that to be the rule: Stonehenge, Numancia, the
Roman forts and every other built site should have at least one, and the map should keep growing with new sites that
come with their own old pictures. (Since 2026-10-10 the owner's copy of the map also colours sites whose only overlay
is a survey sheet 150 or more years old. That does not change this goal: survey sheets are not drawings, and the
number to grow is the count of fitted drawings.)

## What done looks like

1. **Every built site has a fitted old drawing, or a ready review item.** Each site in `web/data/sites.json` either
   has at least one drawing fitted to the ground (`"drawings" >= 1`), or has a review item in `data/review/` with its
   best candidate pictures and proposed point pairs, which the human opens in the page, corrects by dragging, and
   saves with the existing fit tool. Opening a review item and saving it takes the human under a minute.
2. **The image matcher does the fitting, never a language model.** The owner wants far more fitted drawings than
   the ones made by hand, without making them by hand. The only automatic placement is the purpose-built image
   matcher (`fit/matchfit.py`: MatchAnything RoMa and ELoFTR), which finds the same points on the drawing and on a
   georeferenced ground image (the LiDAR relief, or an old survey sheet already placed on the map) and keeps a fit
   only when enough matched points agree. The local Qwen models never place a drawing and never write point pairs or
   coordinates (owner, 2026-10-13: "the image matching model should be the only thing that's doing the matching").
   Why: on 2026-10-11 the agents placed about 100 drawings by reading the fitkit sheets themselves; the look audits
   (306a-f) found nearly all of them wrong and 212b deleted them. The Qwen models find, classify and tie pictures and
   write code; `fit/batch_us.py` / `fit/batch_eu.py`'s model fitting pass is retired. Automatic fitting runs on LiDAR
   sites only (owner, 2026-10-13: fits on aerial photographs alone mostly do not line up); aerial-only sites keep
   their review items for the human. Every matcher fit goes to the gate (point 3); the pictures the matcher cannot
   place go to the review queue. The number to grow is the count of fitted drawings.
3. **A fit is accepted by numbers, never by a model's opinion.** Automatic acceptance goes through a gate validated
   on the existing hand fits with a held-out set (task 001). The human will check a random sample of 20 automatically
   accepted fits on the map; at least 18 must be right (the drawing's walls, streets or gardens on the matching
   features of today's ground). Anything the gate does not accept goes to the review queue.
4. **Every picture is tied to its place with evidence a program can check**, recorded in its row: the file is in the
   Commons category of the site's Wikidata item (P373), or its structured data says it depicts (P180) that item, or
   its title or caption names the place and the coordinates agree. Why: the Rijksmuseum's "Gezicht op Hampton Court"
   is Hampton Court in Herefordshire (its caption says so), not the palace; a name search alone gives the town for
   Barnard Castle and the village for Richard's Castle.
5. **The map grows.** New sites come with their own old pictures, through `pipeline/sources.py` or something better.
   Leads, none of them verified yet (check each one exists and is old enough before using it):
   - Artists' aerial and bird's-eye views count as much as surveys (owner, 2026-10-10, of Leonardo da Vinci's aerial
     plan of Imola, 1502: "should 100% be on our map"). Leonardo's plan of Imola (Royal Collection, RCIN 912284;
     there is no open LiDAR at Imola here, so it is an aerial-photograph site and its streets carry the fit); Jacopo
     de' Barbari's view of Venice (1500); Braun and Hogenberg, *Civitates Orbis Terrarum* (1572-1617), hundreds of
     walled towns; Merian, *Topographia* (1640s-1680s).
   - Jacob van Deventer's town plans: 64 towns not yet added (Commons "Maps by Jacob van Deventer").
   - Kip's bird's-eye views of houses and gardens: the large scans in Commons "Johannes Kip", "Britannia Illustrata".
   - Mackenzie, *The Castles of England* (1897): page 212, a five-towered castle with no caption.
   - Roman sites: Roy, *Military Antiquities of the Romans in North Britain* (1793); Horsley, *Britannia Romana*
     (1732); Maclauchlan's survey of the Roman Wall (1857); the German Limes reports (ORL, fort plans).
   - Stonehenge and Avebury: Hoare, *Ancient Wiltshire* (1812-21); Stukeley (1740s); Petrie's Stonehenge plan (1880).
   - Numancia: the 1860s excavation plans.
6. **The page shows what changed.** New sites, new fits and review items appear on the existing page
   (`web/index.html`, served by `server/serve.py`) without breaking anything that works today.

## Rules that do not change

- Survey maps and survey aerials under 150 years old are not shown (age is the point). Plans, drawings and views of
  the structure are exempt.
- Never push to GitHub, never rewrite history. The owner's architect pulls `main` from this VM, reviews and publishes.
- Never read, copy or change the Finder and Amazon data (`web/data/scan`, `web/data/amazon`, `data/finder`,
  `data/db/marks`, `data/db/surveyseen`, `data/db/verdicts`): it is private and some of it may not be published.
- The existing hand fits (`data/db/platefits/`, the plates in `data/sites/*/site.json`) are the human's: never change
  or delete them. They are the reference the gate is measured against.
- New results go in tracked files: fits in `data/db/platefits/`, sites in `data/catalog/extras.jsonl`, pictures in
  `data/commons/files.jsonl` and `classified.jsonl`, review items in `data/review/`.

## What is known (read before choosing an approach)

- `docs/autofit.md`: fully automatic fitting (extract walls from the ink, search a placement against the relief)
  FAILED its pre-registered test, 0 of 5 plates. Its section 6 says what would be needed. Do not re-run that bet as
  it stands.
- Fitting by matching point pairs works: the human and the architect fitted 25 drawings that way
  (`tools/fitkit.py` sheet, save, check; `pipeline/plan_fit.py` turns pairs into the overlay). Some old plans are
  sketches whose two axes disagree by 25-35% (Framlingham, Carisbrooke, Cooling in Mackenzie); some fit within
  10-30 m (Castle Rising, Bergues). Read the grid labels on a fitkit sheet, never its own pixels.
- Where there is no LiDAR the ground is the aerial photograph (`tools/fitkit.py ground`, `FITKIT_GROUND=aerial`);
  fixed landmarks (roads, churches, river crossings, field edges) carry the fit there.
- The image matcher places about 1 drawing in 10 (2026-10-13: 49 fits on the map, 35 RoMa + 14 ELoFTR; 37 matched
  against old survey sheets, 12 against the LiDAR relief). An old drawing matches an old survey sheet far better than
  LiDAR shading. Pictures it already refused do not get better by re-running it: a better yield needs a better
  ground image or a better matcher, never a language model placing points.
- Candidate pictures already found: 1166 plans in `web/data/plans.json` (8 old books plus Commons), with their
  page images in `data/raw/books` and `data/raw/commons`. Most are not fitted yet.
- This VM's copy has the built sites' images (`web/data/sites`) but not their elevation models (`data/sites/*/dem.npy`);
  `pipeline/build_site.py` refetches one when needed. The model servers are at `$LLM_URL` here, not at the Mac
  tunnel ports written in `pipeline/llm.py` and `pipeline/clef.py`. The model is a vision model; what it says about a
  picture is a lead to check, not a fact.
- Tests drive the real thing (end-to-end, integration, golden re-fits of the hand fits); no unit tests.
