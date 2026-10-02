# Downloads that update after a push

Destination: [lorenzosaraiva/smash-charbuilder](https://github.com/lorenzosaraiva/smash-charbuilder).
The active workflow is `.github/workflows/character-lab-release.yml` at the root.
It builds Character Lab; Remix releases remain a separate future step.

## One-time automatic-build setup

In GitHub **Settings -> Secrets and variables -> Actions**, add **BASEROM_URL**:
a direct HTTPS download of the original US ROM required by the builder. Keep
this source out of public docs. A Drive preview page or modified ROM will fail
the exact SHA-1 check. The original ROM is not a release asset.

Then run **Build and release Character Lab** from Actions, or push to `main`.
No personal access token is needed by the workflow; its release job uses
GitHub's repository token with `contents: write`.

Permanent friend-facing links:

```text
https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.zip
https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.z64
```

GitHub supports these [latest-release asset URLs](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases).
The filenames stay fixed while each successful build gets its own snapshot.
Committing locally does not update downloads; pushing starts the workflow.

The previous download stays available during a build. Only a checked, completed
package is published. Missing base-ROM setup or a build/check failure does not
replace the previous release.

## Local packages and named releases

Run the root [build command](building.md). Its files in `dist/` can also be
attached to a release manually, with the package's exact source commit recorded.

Tags named `v*` publish archived snapshots without replacing the automatic
`main` download. For example:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Troubleshooting

- Base download unavailable: check `BASEROM_URL` returns ROM bytes over HTTPS.
- Wrong checksum: use the original US base identified in the build guide.
- Build/check failure: fix it before publishing; the previous download remains.
- Upload denied: check Actions is enabled and permits the release job's write permission.

Component `.github/` folders are retained as source history; active project
workflows and issue forms live in the root `.github/` folder.
