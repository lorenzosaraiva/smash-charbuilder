# Helping out

This is a casual project. Gameplay reports, ideas and small fixes are welcome.

For bugs, tell us which build/commit you downloaded, emulator, body, donor, attack
and steps to reproduce it. A short clip is especially useful for animation issues.
See the [feature checklist](docs/status.md) before assuming a donor's full
animation or special mechanic is implemented.

For code changes:

1. Start from `main` and make a branch for your change.
2. Build with `bash tools/build-character-lab.sh` (see the [setup guide](docs/building.md)).
3. Try the affected combination in Training; use HITBOX view when relevant.
4. Explain what changed and how you checked it in the pull request.

Avoid committing original ROMs, generated ROMs, tool binaries or extracted assets.
Keep foreign fighter state functions and raw donor joint indices out of unrelated
bodies; the compatibility notes explain why. Most attacks use normalized gameplay
data, while animation work goes through explicit skeleton mapping.

Update `docs/status.md` and `CHANGELOG.md` when a feature or limitation changes.
There is no need to pretend an untested experimental feature is finished.
