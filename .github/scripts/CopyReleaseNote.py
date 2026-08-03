# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause
#
# NOTE: This script is called by CI — .github/workflows/build-for-release.yml
#       Reads a release note file, replaces every occurrence of OLD_VERSION
#       with NEW_VERSION, and writes the result back in-place.
#       Multiple occurrences on the same line are all replaced.

import sys


def replace_all_versions(text, old_version, new_version):
    return text.replace(old_version, new_version)


if len(sys.argv) != 4:
    print("Usage: python CopyReleaseNote.py <old_version> <new_version> <file_path>",
          file=sys.stderr)
    sys.exit(1)

old_version = sys.argv[1]
new_version = sys.argv[2]
file_path = sys.argv[3]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = replace_all_versions(content, old_version, new_version)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
