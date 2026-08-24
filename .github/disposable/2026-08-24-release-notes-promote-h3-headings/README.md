# Promote level-three release-note headings

## Purpose

Standardize existing GitHub Release notes by promoting Markdown level-three
headings (`###`) to level-two headings (`##`).

## What this script does

- Lists every release in the current repository through the GitHub REST API.
- Promotes every ATX level-three heading outside fenced code blocks.
- Leaves level-four-or-deeper headings, code examples, release titles, tags,
  and assets unchanged.
- Supports a dry-run mode controlled by `DRY_RUN`:
  - When `DRY_RUN=true`, logs releases that would change without updating them.
  - When `DRY_RUN=false`, updates the release bodies.

## How to run

Run the **Disposable Run** workflow from the repository's **Actions** tab,
select `promote-h3-headings`, and keep `dry_run` enabled first. To apply the
changes, disable `dry_run` and enter `YES` in `confirm`.
