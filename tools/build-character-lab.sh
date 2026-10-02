#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
for argument in "$@"; do
    if [[ "$argument" == --help ]]; then
        bash ssb-decomp-re/tools/build-character-lab.sh --help
        echo "Root entry point also copies checked files to this repository's dist/."
        exit 0
    fi
done
bash ssb-decomp-re/tools/build-character-lab.sh "$@"
mkdir -p dist
for name in character-lab.z64 character-lab.zip build-info.json SHA256SUMS.txt PLAY.md release-notes.md; do
    cp "ssb-decomp-re/dist/$name" "dist/$name"
done
echo 'Checked files ready in root dist/.'
