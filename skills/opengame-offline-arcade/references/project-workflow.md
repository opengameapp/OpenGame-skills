# Offline project helper

`scripts/project.py` uses Python 3 standard library only. Resolve `SKILL_ROOT`
to the installed Skill folder and `PROJECT` to the user's workspace folder.
These are command patterns, not literal paths to paste unchanged:

```sh
python3 "$SKILL_ROOT/scripts/project.py" create --output "$PROJECT" --title "Starberry Meadow"
python3 "$SKILL_ROOT/scripts/project.py" inspect --project "$PROJECT"
python3 "$SKILL_ROOT/scripts/project.py" configure --project "$PROJECT" --config difficulty.json
python3 "$SKILL_ROOT/scripts/project.py" configure --project "$PROJECT" --collectible gem
python3 "$SKILL_ROOT/scripts/project.py" snapshot --project "$PROJECT" --note "Use gems and slow the hazards"
python3 "$SKILL_ROOT/scripts/project.py" verify --project "$PROJECT" --version v002
python3 "$SKILL_ROOT/scripts/project.py" export --project "$PROJECT" --version v002 --output "$PROJECT-v002.zip"
```

When the host exposes Python instead of a terminal, the same CLI can run in
that interpreter:

```python
import runpy, sys
sys.argv = [str(skill_root / "scripts/project.py"), "inspect", "--project", str(project)]
runpy.run_path(sys.argv[0], run_name="__main__")
```

Use host file APIs to write config overrides; do not interpolate user text
into shell code. An override such as
`{"hazardSpeed":55,"roundSeconds":90,"palette":{"accent":"#3459c7"}}`
changes only those settings. Other palette entries are preserved.

| Setting | Default | Accepted values |
| --- | --- | --- |
| title | Starberry Meadow | Nonempty string, at most 80 characters |
| goal | 8 | Integer 1–40 |
| roundSeconds | 60 | Integer 10–300 |
| playerSpeed | 220 | Integer 80–420 |
| hazardSpeed | 85 | Integer 20–220 |
| hazardCount | 3 | Integer 0–8 |
| maxLives | 3 | Integer 1–9 |
| collectible | star | `star` or `gem` |
| seed | 1729 | Integer 0–2147483647 |
| palette | Meadow colors | `sky`, `field`, `accent`; each `#RRGGBB` |

`schema` remains `opengame.arcade.v1`. Unknown keys, duplicate JSON keys,
non-finite numbers, and invalid values fail. Additional gameplay variables
belong in the code until the helper schema explicitly supports them.

## Files and versions

The mutable project has `index.html`, `game.json`, `README.md`, `assets/`,
`project.json`, and `versions/`. Each version has a manifest and copies of the
explicit payload. The manifest records its parent, change note, SHA-256 file
inventory, and active collectible hash.

`create` makes `v001`. `configure` changes the working copy without creating
a version. `snapshot` saves the next version. Export reads only the named,
verified snapshot; later working edits do not enter an earlier export.
Do not label an unsnapshotted working copy as a saved version.

Preserve exactly these script tag headers when editing HTML:

```html
<script id="opengame-config" type="application/json">
<script id="opengame-assets" type="application/json">
```

Each appears once with a JSON body and closing script tag. `configure`
updates only the bodies. Asset JSON maps `background`, `player_idle`,
`player_move_1`, `player_move_2`, `star`, `gem`, and `hazard` to embedded SVG
data URLs. Edit the corresponding source under `assets/art/`, then run
`configure`. Retain the inventory identifiers.

The helper exports the explicit game/config/README/art inventory plus
`version.json`; it does not recursively archive the workspace. Unrelated
files such as `.env` are excluded. New runtime media must be embedded in the
HTML or added through a deliberate inventory/schema change. Merely placing
an arbitrary file next to `index.html` does not include it in the download.

Creation and export refuse existing destinations. Mutations use a project
lock. If a stale lock is reported, establish that no operation is running
before removing it. Preserve corrupt versions for diagnosis. Use an earlier
version only explicitly, explaining which later work it omits.

A configure interrupted after its journal is written finishes that pending
change on the next configure or snapshot. Recovery re-patches the current
HTML's data blocks while retaining code edits outside them. `inspect` reports
whether the advisory version pointer differs from verified manifests; a
successful snapshot rebuilds the pointer/history from those manifests.
