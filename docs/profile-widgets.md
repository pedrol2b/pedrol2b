# Profile widgets

## Activity graph

The graph is a versioned SVG in `assets/activity-graph.svg`, generated from
GitHub's contribution calendar. It preserves the profile's colors and displays
the last 31 UTC days. No external image service, hosting account, dependencies,
or personal access token is required.

`.github/workflows/activity-graph.yml` updates it daily at 06:23 UTC
(03:23 in São Paulo), on generator changes, or manually through
**Actions → Update activity graph → Run workflow**. Standard GitHub-hosted
runners are [free for public repositories](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
The workflow uses the built-in `GITHUB_TOKEN` with `contents: write`; repository
rules must permit the bot to push to `main`. It does not request private-repository
access. Failed requests leave the previous SVG available. Scheduled jobs can be
delayed or disabled by GitHub after prolonged repository inactivity; inspect the
Actions tab if the date stops updating.

To verify locally, run `python3 -B -m unittest discover -s scripts -p 'test_*.py'`.

## Profile views

The counter uses the free [hits.sh service](https://github.com/silentsoft/hits).
The `extraCount=5401` parameter carries over the last observed Komarev total
(5,401). Keep that parameter unchanged: it is a fixed offset added to the new
service's count, not a value to update periodically. Only the total is carried
over; historical visit records are not imported.

Komarev returned a valid SVG directly, but GitHub's image proxy returned 404 even
after a cache purge and URL change. A [similar failure was reported to its
maintainer](https://github.com/antonkomarev/github-profile-views-counter/issues/121).
The replacement still depends on the external service and GitHub's proxy.

The count measures image requests, not unique visitors. Saving a static copy
would stop counting visits, so this widget intentionally remains dynamic.
