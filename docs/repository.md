# One repository, two source folders

`smash/` is now the repository root. Its `origin` is
`https://github.com/lorenzosaraiva/smash-charbuilder.git`. Run Git commands here
or inside either source folder; they all use the same root repository.

- `remix/`: Smash Remix +EXTRA and the earlier creator experiment.
- `ssb-decomp-re/`: the current original-roster Character Lab implementation.
- `tools/`: root build entry points.
- `docs/`: shared guides.
- `.github/`: active workflows and issue forms.
- `dist/`: checked local Character Lab download files, ignored by Git.

The import retains Remix commit `07ded05` and decomp commit `d40cc78fb` as parents,
so both main-branch histories and original authorship remain reachable. Original
repository metadata, all refs and working-change patches were backed up outside
the project before retiring the two project-level `.git` directories.

`remix/smashremix` and the three `ssb-decomp-re/tools/` dependencies remain pinned
submodules. They supply build inputs; they are not separate creator projects.
Their definitions are consolidated in root `.gitmodules`, and recursive clone
initializes them. Component `.gitmodules` files are retained historical copies.

Remix's previously tracked `.venv/` is no longer in the current index. The local
environment is preserved on disk and can be recreated by the build system.
The Sonic creator hook previously edited inside the upstream dependency is now
versioned in `remix/smashremix_overwrite/Sonic/SonicSpecial.asm`.

The repository migration changed source ownership and build paths. Subsequent
gameplay work now includes original donor collision paths for the complete
normal roster; visible animation expansion remains pending. See the [current checklist](status.md).
