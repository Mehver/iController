# Replace shields badge download buttons with a plain download list

## Purpose

Each GitHub Release body in this repository starts with a row of
[shields.io](https://img.shields.io) badge images that act as download
buttons, one per artifact, e.g.:

```markdown
[![](https://img.shields.io/badge/Windows%20(x64)%20CLI-v0.7.2-blue?logo=...)](https://github.com/Mehver/iController/releases/download/v0.7.2/icontroller-v0.7.2-portable-win-x64-cli.zip) [![](https://img.shields.io/badge/Windows%20(x64)%20GUI-v0.7.2-blue?logo=...)](https://github.com/Mehver/iController/releases/download/v0.7.2/icontroller-v0.7.2-portable-win-x64-gui.zip)
```

The number and length of these badges vary per release. The embedded base64
logos make the raw release notes hard to read and edit, so we replace the
whole leading badge block with a plain Markdown unordered list of download
links, preceded by a `### Download` heading:

```markdown
### Download

- [Windows (x64) CLI v0.7.2](https://github.com/Mehver/iController/releases/download/v0.7.2/icontroller-v0.7.2-portable-win-x64-cli.zip)
- [Windows (x64) GUI v0.7.2](https://github.com/Mehver/iController/releases/download/v0.7.2/icontroller-v0.7.2-portable-win-x64-gui.zip)
```

## What this script does

- Lists all releases in the current repository via the GitHub REST API.
- For each release, parses the consecutive shields badge download buttons
  at the very beginning of the body (any count, separated by whitespace).
- Derives a readable label for each link from the badge URL
  (e.g. `Windows (x64) CLI v0.7.2`); falls back to the downloaded file name
  if the badge URL cannot be parsed.
- Replaces the badge block with a `### Download` heading followed by an
  unordered list with one download link per line, keeping the rest of the
  body untouched.
- Releases whose body does not start with such a badge block are skipped.
- Supports a dry-run mode controlled by the `DRY_RUN` environment variable:
  - When `DRY_RUN=true`, the script only logs which releases would be
    updated and what the new list items would look like.
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
