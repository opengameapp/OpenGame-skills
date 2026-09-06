# OpenGame AI Game Generator 1.0.0 — Validation

Checked September 6, 2026. This is technical validation, not an OpenAI
directory approval or a guarantee about every host-generated game.

## Reproduce the local checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_plugin.py --output dist/review-1.0.0
```

All 14 tests pass. The suite checks creation, three-version history, preservation
of code and artwork, explicit version exports, reproducible archives, exclusion
of unrelated files, symlink rejection, invalid configuration rejection, JSON
embedding, interrupted-operation recovery, and preservation of an existing
download when concurrent exports choose the same destination.

The current Skill Creator validator passes for `opengame-offline-arcade`.
The current Plugin Creator validator passes for the assembled `opengame` plugin.
The final package contains 18 files; the standalone Skill archive contains 16.
Both use the same canonical Skill resources. The archives exclude development
tests, local state, private host transcripts, credentials, and unrelated Skills.

The concurrent-export check reproduced deletion of an existing download before
the fix. Export now acquires its destination exclusively before enabling error
cleanup, and cleanup only removes the file acquired by that operation.

## Host and gameplay evidence

An English private ChatGPT Skill session created a game and completed two
successive revisions. The downloaded V1, V2, and V3 archives were inspected:
version relationships and file hashes matched, the seven SVG source assets
were preserved, difficulty changes remained in later versions, and a focused
best-score HUD edit remained in the latest game.

The actual downloaded files were played in Ego. Desktop keyboard input changed
the score and pause worked. At a 390 by 844 mobile viewport, touch input
completed the five-gem goal; restart reset the run while retaining the
requested in-memory best score, and reload reset that score. No JavaScript
errors or HTTP(S) resource loads were observed during those recorded runs.

That ChatGPT host could execute Python and deliver files, but could not run
the local game in its own browser environment. Ego gameplay was a separate
check. One host network failure required resubmission before the final revision
started; it did not create an extra version.

The final release's changes after that host session are the export-collision
fix and public policy links. Its 14 local checks and both validators were
rerun; the earlier host session is not presented as a fresh run of the final
package. Complete the reviewer cases in [REVIEW.md](REVIEW.md) against the
final uploaded bundle before formal submission.

## Release archive fingerprints

| Archive | SHA-256 |
| --- | --- |
| `opengame.zip` | `33e42ba58b84095061172443ebb9fa0d2057e925bec681ec53f0de9fabf71887` |
| `opengame-offline-arcade.skill` | `6c1c0453c6a2d263057e0f4e191a1e78c3e9677142817f36c6ebf0e217486f1c` |
