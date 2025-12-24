# Fix Windows logo in shields.io URLs for release nots

## Purpose

The Windows logo is no longer provided by Simpleicons.org as indexed by Shields.io due to copyright reasons, so it has been replaced with an inline logo stored directly in Base64 format.

Replace `?logo=Windows` in GitHub release notes with an embedded SVG
to avoid shields.io rendering inconsistency.

SVG Base64:

```
data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjI1MDAiIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIiB3aWR0aD0iMjQ5MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2aWV3Qm94PSItMSAtMSAyNTggMjU5Ij48cGF0aCBkPSJNLTEtMWgyNTh2MjU5SC0xeiIvPjxwYXRoIGQ9Ik0wIDM2LjM1N0wxMDQuNjIgMjIuMTFsLjA0NSAxMDAuOTE0LTEwNC41Ny41OTVMMCAzNi4zNTh2LS4wMDF6bTEwNC41NyA5OC4yOTNsLjA4IDEwMS4wMDJMLjA4MSAyMjEuMjc1bC0uMDA2LTg3LjMwMiAxMDQuNDk0LjY3N3ptMTIuNjgyLTExNC40MDVMMjU1Ljk2OCAwdjEyMS43NGwtMTM4LjcxNiAxLjFWMjAuMjQ2ek0yNTYgMTM1LjZsLS4wMzMgMTIxLjE5MS0xMzguNzE2LTE5LjU3OC0uMTk0LTEwMS44NHoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=
```