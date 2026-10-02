# Character Lab releases

The combined project publishes from
[lorenzosaraiva/smash-charbuilder](https://github.com/lorenzosaraiva/smash-charbuilder).
See the [shared release guide](../../docs/releases.md) for permanent download
links and the one-time `BASEROM_URL` setup.

The active workflow is `.github/workflows/character-lab-release.yml` at the
repository root. This component's `.github/` folder is retained for source
history and is not run by GitHub in the combined repository.

The component build command still writes its checked files to this folder's
`dist/`. The root build command also copies them to the repository's `dist/`;
see [building](../../docs/building.md).
