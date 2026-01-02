# Update release notes subheading for bot-only releases

## Purpose

This repository currently only receives pull requests from bots
(such as Dependabot or ImgBot), and each GitHub Release contains both:

- A manually written `### Release Notes` section, and
- An auto-generated `### What's Changed` section.

To reduce semantic duplication and better reflect that the changes come
from bots, we update the subheading `### What's Changed` to `### Bot Updates`
in all existing release notes.

## What this script does

- Lists all releases in the current repository via the GitHub REST API.
- For each release whose body contains `### What's Changed`,
  replaces it with `### Bot Updates`.
- Supports a dry-run mode controlled by the `DRY_RUN` environment variable:
  - When `DRY_RUN=true`, the script only logs which releases would be updated.
  - When `DRY_RUN=false`, the script actually updates the release bodies.

No tags, assets, or release titles are modified.

## How to run

This script is intended to be executed via the reusable
"Disposable Run" GitHub Actions workflow in this repository.

1. Open the **Actions** tab.
2. Select **Disposable Run**.
3. Click **Run workflow**.
4. Keep `dry_run` checked for the first run to verify which releases
   would be touched.
5. When you are satisfied with the output, uncheck `dry_run`,
   type `YES` into the `confirm` field, and run the workflow again
   to apply the changes.
