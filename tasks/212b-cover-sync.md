Status: open
# 212b: The page-facing sync - every fit is an overlay, review.json is the open list
Depends on: 212a
Touches: fit/cover.py, web/data/sites.json, web/data/sites/, web/data/review.json, tests/test_cover.py

## Goal
The one page-facing sync from 212: every fit document becomes its site's overlay
(web/data/sites/<id>/depictions.json) and drawings count in web/data/sites.json through
the existing plan_fit machinery (plan_fit.main(), the way serve.py's after_write does);
web/data/review.json is regenerated (python3 fit/review.py export).

## Acceptance criteria
- [ ] `python3 fit/cover.py sync` runs plan_fit for every site with a fit doc and the review export.
- [ ] The hand fits' overlays are unchanged (000's golden test still passes).
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item; the page's review count
      matches review.json (checked through the served page).
