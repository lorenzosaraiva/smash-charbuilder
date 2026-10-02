# Downloads that update after a push

The workflow is prepared in `.github/workflows/character-lab-release.yml`.
It has not published a release yet. Local packages can already be created with
the [build command](building.md).

## One-time setup

1. Choose the public GitHub repository for this project and push this source to
   its `main` branch. This clone currently points to the upstream decompilation
   repo; use your own repository or fork if that is where you want to publish.
2. In the destination repo, go to **Settings -> Secrets and variables -> Actions**
   and add the repository secret **BASEROM_URL**. Its value must be a direct HTTPS
   download of the original US ROM needed by the builder. Keep this source out
   of public docs. A normal Drive preview page or the current modified ROM will
   fail validation; the workflow checks the exact base SHA-1 before extraction.
3. Enable GitHub Actions. Run **Build and release Character Lab** from the
   **Actions** tab, or push another commit to `main`.
4. After the first successful run, put the permanent links below in the README
   and share them with friends. Substitute the destination owner/repo once.

```text
https://github.com/OWNER/REPO/releases/latest/download/character-lab.zip
https://github.com/OWNER/REPO/releases/latest/download/character-lab.z64
https://github.com/OWNER/REPO/releases/latest
```

The ZIP is the friendlier link because it includes the play guide and checklist.
Each successful workflow also prints the exact links in its summary. GitHub
supports this [permanent latest-release asset URL](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases).

You can keep the current Drive copy as a temporary mirror; add its shared link
to the README once available. It is not the original-ROM build input.

## What happens on each push

On pushes to `main`, the workflow checks out source/submodules, retrieves the
original ROM through the configured secret, builds from scratch on Ubuntu,
runs the host and ROM checks, and packages fixed filenames. A separate job
uploads the completed files to a draft release and publishes it as latest.

The old latest download remains available while the new build runs. A build or
validation failure publishes nothing. The original ROM is not a release asset;
the workflow publishes the generated Character Lab ROM and play package.
Public release access depends on the repository being public.

The release files include `build-info.json` and `SHA256SUMS.txt`, so reports can
identify the exact commit and downloaded ROM. Releases keep past snapshots.
Committing locally does not run GitHub Actions; pushing does.

## Optional named releases

For a version you want to keep by name:

```bash
git tag v0.1.0
git push origin v0.1.0
```

`v*` tag builds publish an archived release for that tag. They do not replace the
automatic `main` download. Only create a tag after checking the corresponding
gameplay build. The project does not need a formal release schedule.

## If the workflow fails

- **Original ROM unavailable:** set/check `BASEROM_URL`; it must return ROM bytes,
  not a login or preview page.
- **Wrong base checksum:** use the original US version identified in the build guide.
- **Build/check failed:** fix the code before publishing. The previous download stays live.
- **Release upload denied:** check that the repo permits Actions and the release
  job's `contents: write` permission. No personal access token is needed for normal releases.

The upstream progress-report workflow is retained separately; it is not the ROM
download workflow.
