#!/bin/bash
# Provision the IRIX 4 compatibility frontend used to build ovl8_8.o.
#
# Fetches the `ido4.1` package that decomp.me already publishes. That
# tarball carries exactly the three things we need and nothing we have to
# build ourselves:
#
#   usr/lib/accom          the IRIX 4 C frontend (MIPS ECOFF, emulated)
#   usr/lib/acpp, copt     4.1's own preprocessor/optimizer (unused, kept
#                          for provenance -- see README.md)
#   usr/bin/qemu-irix-4.0  a prebuilt native x86-64 Linux qemu-irix
#
# No IDO 4.1 media, no docker, and no qemu-irix build are required: the
# emulator ships inside the package alongside the shared libraries it
# needs at `-L` time.
#
# Usage: tools/ido-irix4/provision.sh

set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
DEST="$SCRIPT_DIR/ido4.1"
URL="https://github.com/decompme/compilers/releases/download/compilers/ido4.1.tar.gz"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

if [ ! -x "$DEST/usr/lib/accom" ] || [ ! -x "$DEST/usr/bin/qemu-irix-4.0" ]; then
    echo "fetching $URL" >&2
    curl -fsSL "$URL" -o "$tmp/ido4.1.tar.gz"

    mkdir -p "$DEST"
    tar xzf "$tmp/ido4.1.tar.gz" -C "$DEST"
    chmod +x "$DEST/usr/bin/qemu-irix-4.0" "$DEST/usr/lib/accom" "$DEST/usr/lib/acpp" "$DEST/usr/lib/copt"
fi

for f in usr/lib/accom usr/bin/qemu-irix-4.0; do
	[ -x "$DEST/$f" ] || { echo "error: $f missing from package" >&2; exit 1; }
done

# The distributed emulator needs GLIBC_2.38 and newer GLib. Ubuntu 22.04 has
# older versions. Keep a verified runtime beside the ignored tools instead of changing
# the system libc or depending on a temporary directory. Newer hosts skip this.
if ! IRIX4_ROOT="$DEST" bash "$SCRIPT_DIR/qemu-run.sh" --version >"$tmp/qemu.log" 2>&1; then
    if ! grep -Eq 'GLIBC_2\.|g_assertion_message_cmpint' "$tmp/qemu.log"; then
        cat "$tmp/qemu.log" >&2
        echo 'Install libglib2.0-0 and libpcre3, then retry provisioning.' >&2
        exit 1
    fi
    RUNTIME_URL='https://security.ubuntu.com/ubuntu/pool/main/g/glibc/libc6_2.39-0ubuntu8.9_amd64.deb'
    RUNTIME_SHA256='ff5557d99b51f761c4b7c92368b9cc45565eda17df9bf9eb4b134d09825008be'
    GLIB_URL='https://security.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-0t64_2.80.0-6ubuntu3.9_amd64.deb'
    GLIB_SHA256='a66ef54888a18e20b55dd3988177f6029caa81dc16198c043a715500b62cf06f'
    echo 'Fetching a local compatibility runtime for the compiler emulator.' >&2
    curl -fsSL "$RUNTIME_URL" -o "$tmp/libc6.deb"
    printf '%s  %s\n' "$RUNTIME_SHA256" "$tmp/libc6.deb" | sha256sum --check
    dpkg-deb -x "$tmp/libc6.deb" "$DEST/host-runtime"
    curl -fsSL "$GLIB_URL" -o "$tmp/glib.deb"
    printf '%s  %s\n' "$GLIB_SHA256" "$tmp/glib.deb" | sha256sum --check
    dpkg-deb -x "$tmp/glib.deb" "$DEST/host-runtime"
    IRIX4_ROOT="$DEST" bash "$SCRIPT_DIR/qemu-run.sh" --version
fi

echo "provisioned $DEST" >&2
