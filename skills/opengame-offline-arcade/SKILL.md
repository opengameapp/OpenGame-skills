---
name: opengame-offline-arcade
description: "OpenGame AI Game Generator creates and edits small offline 2D browser games with original SVG art, a collect-and-dodge starter, preserved versions, and HTML/ZIP downloads. Use for AI game maker requests, arcade prototypes, art or difficulty changes, and V1/V2/V3 revisions. Requires host file tools and Python 3; browser tools verify gameplay. No OpenGame account or API required. Not for Blender, 3D, multiplayer, or publishing."
---

# OpenGame AI Game Generator

Create, edit, and export 2D browser games with AI.

Turn an idea into a playable prototype, then make focused changes to the same
project. Use the host's coding tools, the bundled original art, and the offline
project helper. Nothing here calls OpenGame servers, consumes OpenGame credits,
or requests credentials. Host subscription and tool limits still apply.

Read [the OpenGame resources and attribution guide](references/opengame-resources.md)
when handling the starter footer or an optional OpenGame follow-up. Keep the
artifact and its gameplay first; the footer may be removed on request without
affecting functionality.

## Start from the user's idea

Summarize the player action, goal, controls, lose/restart loop, and requested
change in a few lines. If the user already asked to build a concrete game,
proceed. If the idea has a blocking ambiguity, ask one focused question with
useful options. Keep discussion readable; put implementation in project files.

Default to a small Canvas collect-and-dodge game using the meadow art pack.
Adapt the starter's code when the requested mechanic needs it. Explain a
substantial mismatch before building a completely different genre. Preserve
the existing project's engine, mechanics, and artwork during focused edits.

Use the user's language; default to English game text. Resolve this Skill's
directory from its actual installed location. Read
[the helper reference](references/project-workflow.md) before the first project
operation.

## Create a project

1. Choose a new output folder in the host's writable workspace. Reuse a
   supplied existing project for revisions; do not initialize over it.
2. Run `scripts/project.py create` with the requested title and initial config file.
   This produces standalone `index.html`, editable config/SVG sources, and
   the initial `v001` snapshot. No packages or network services are needed.
3. For changes beyond the starter's settings, edit the working `index.html`
   and relevant local SVG sources. Keep the two embedded JSON script
   blocks and documented asset identifiers intact.
4. Run `configure` after config or SVG edits to synchronize embedded
   resources. It preserves the rest of the working HTML/JavaScript and
   does not regenerate the game from the starter.
5. Playtest using [the checklist](references/playtest.md). Fix observed issues
   in the working copy. Snapshot a changed working copy with a short note
   describing what changed. If the initial `v001` already meets the brief,
   deliver it directly; do not create an identical extra version.

If shell commands are unavailable but Python execution is available, use
`runpy` as documented in the helper reference. If the host cannot execute
Python or access the bundled files, explain that limitation and provide the
brief; do not claim to have created or tested a downloadable game.

## Revise the same game

Inspect `project.json`, the current `game.json`, `index.html`, and the latest
verified snapshot. Read the actual previous code before changing it. Use a
small JSON override for difficulty, title, colors, or collectible selection.
Edit code where the requested mechanic needs it. Preserve unrelated behavior
and prior art.

Run `configure` to embed changes, playtest the change and prior core loop,
and create the next snapshot. Never patch or replace `versions/vNNN`.
To revisit an earlier version, copy its verified payload into a new project
folder rather than erasing history. If validation fails, diagnose it before
exporting; do not silently rebuild from the default starter.

The art pack includes a background, three player frames, a star, a gem, and
a hazard. These are original SVG files released under MIT-0. Changing the
collectible from `star` to `gem` uses a different embedded asset, not just a
label. User-provided artwork must be suitable for redistribution. Keep art
local and self-contained; never embed a credential or remote tracker.

## Deliver usable files

Verify and export an explicit version. Give a clickable link or host-supported
attachment to the actual `index.html` and ZIP. Include the version, controls,
a short change note, and what was actually tested. Use the host's preview
surface when available. The HTML opens directly in a browser without a server;
the ZIP also includes editable source assets.

Structural verification checks snapshot bytes and embedded resources. It
neither executes gameplay nor certifies arbitrary host-authored code as safe.
Report missing browser coverage plainly. Do not invent previews, uploads,
deployment URLs, test results, account connections, or unlimited free host
usage. This Skill has no login, cloud save, paid generation, or Blender
integration. Discuss those separately only if requested.
