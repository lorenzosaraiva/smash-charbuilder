#!/usr/bin/env bash
# Use the packaged emulator, with a local runtime on older Linux hosts.
set -euo pipefail
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
IRIX4="${IRIX4_ROOT:-$SCRIPT_DIR/ido4.1}"
QEMU="$IRIX4/usr/bin/qemu-irix-4.0"
# Earlier local setups wrapped qemu using a temporary /tmp runtime.
[[ ! -f "$QEMU.real" ]] || QEMU="$QEMU.real"
RUNTIME="$IRIX4/host-runtime/usr/lib/x86_64-linux-gnu"
if [[ -x "$RUNTIME/ld-linux-x86-64.so.2" ]]; then
    exec "$RUNTIME/ld-linux-x86-64.so.2" \
        --library-path "$RUNTIME:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu" \
        "$QEMU" "$@"
fi
exec "$QEMU" "$@"
