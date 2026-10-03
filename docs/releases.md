# Downloads that update after a push

Destination: [lorenzosaraiva/smash-charbuilder](https://github.com/lorenzosaraiva/smash-charbuilder).
The active workflow is `.github/workflows/character-lab-release.yml` at the root.
It builds Character Lab; the Remix preview uses a separate local publication command.
The first public download was built and checked locally. Automatic updates
still need the setup below; until then, pushes run the source checks and the
release workflow reports the missing configuration without replacing downloads.

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

The root README shows the project version and its last-updated date, plus each
published ROM's date and exact source build. Bump the project version when
publishing a feature or fix release, and update the relevant download row after
publication succeeds. Documentation edits can update the README date without
changing a ROM's published date or source build. Use Sao Paulo dates.

Run the root [build command](building.md). Its files in `dist/` can also be
attached to a release manually, with the package's exact source commit recorded.

Tags named `v*` publish archived snapshots without replacing the automatic
`main` download. For example:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Local Remix preview

The original-roster Remix port has separate moving preview downloads:

- [Remix ROM](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-character-lab.z64)
- [Remix play package](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-character-lab.zip)

Build/check with `tools/build-remix-character-lab.ps1`, commit and push the exact
source, then refresh clean package metadata with `-PackageOnly`. Publish with
`python tools/publish-remix-preview.py`. It checks the destination, pushed
commit, clean source, ZIP and checksums before uploading, then verifies public
downloads. This is an explicit local publication command; a push alone does
not update the Remix preview. The `remix-preview` tag moves when republished;
the package records the exact source commit.

The preview is a prerelease and leaves Character Lab's latest-release download
links intact. Automatic hosted Remix builds remain on the checklist.

## Troubleshooting

- Base download unavailable: check `BASEROM_URL` returns ROM bytes over HTTPS.
- Wrong checksum: use the original US base identified in the build guide.
- Build/check failure: fix it before publishing; the previous download remains.
- Upload denied: check Actions is enabled and permits the release job's write permission.

Component `.github/` folders are retained as source history; active project
workflows and issue forms live in the root `.github/` folder.
