# IRIX 4 frontend

`accom-cc` preprocesses with the native IDO 7.1 tools, runs the IRIX 4.1 `accom`
frontend through qemu-irix, and uses the native 7.1 backend. The Makefile uses it
for `src/ovl8/ovl8_8.c`.

Run `bash tools/ido-irix4/provision.sh` to fetch the
[decomp.me compiler package](https://github.com/decompme/compilers/releases/tag/compilers).
The full Character Lab setup runs this automatically. The package is currently
for x86-64 Linux; Ubuntu 22.04 is the release workflow's build environment.

`qemu-run.sh` checks for a compatibility runtime beside the compiler. On hosts
whose libc/GLib are too old, provisioning downloads the pinned Ubuntu Noble
[libc6](https://packages.ubuntu.com/noble/amd64/libc6/download) and
[GLib](https://packages.ubuntu.com/noble/amd64/libglib2.0-0t64/download) packages,
verifies their SHA-256 checksums, and extracts them under `ido4.1/host-runtime/`.
They are used only to launch this emulator; system libraries are unchanged.
Existing local setups with a `qemu-irix-4.0.real` binary are supported too.

`ido4.1/` is ignored by Git. If a pinned package is no longer downloadable,
provisioning fails; update its URL and checksum from the official Ubuntu package
metadata before retrying. A compiler/runtime failure stops release packaging.
