#!/usr/bin/env bash
# Build, check, and package Character Lab. Run on Linux or through WSL.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

setup=0
initialize=0
jobs="$(nproc)"
while (($#)); do
    case "$1" in
        --setup) setup=1; shift ;;
        --init) initialize=1; shift ;;
        --jobs) jobs="${2:?Pass a job count after --jobs}"; shift 2 ;;
        --help)
            echo 'Usage: bash tools/build-character-lab.sh [--setup] [--init] [--jobs N]'
            echo 'Output: dist/character-lab.z64 and dist/character-lab.zip'
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo 'Job count must be positive.' >&2; exit 2; }

if ((setup)); then
    python3 -m venv .venv
    source .venv/bin/activate
    bash installDependencies.sh
elif [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
fi

python3 tools/packageRelease.py --check-base
if ((initialize)) || [[ ! -f .splat/us/smashbrothers.ld ]]; then
    make extract VERSION=us COLOR=0
fi
make -j"$jobs" VERSION=us COLOR=0
python3 tools/prepareSharedAnimationTest.py
gcc -m32 -nostdlib -static -fno-pie -fno-stack-protector -O1 \
    -Iinclude -Isrc -D__sgi -D_LANGUAGE_C -D_MIPS_SZLONG=32 -DREGION_US \
    tools/testCustomMove.c -o build/testCustomMove
build/testCustomMove
python3 tools/testNeutralLifecycle.py
python3 tools/testSpecialTiming.py
python3 tools/testSuperJump.py
python3 tools/testDirectSpecials.py
python3 tools/testRemainingSpecials.py
python3 tools/testNormalMechanics.py
python3 tools/testSpecialAnimations.py
python3 tools/testPairedMoves.py
python3 tools/testNativeAnimation.py
python3 tools/verifyCustomMoveRom.py
python3 tools/packageRelease.py
