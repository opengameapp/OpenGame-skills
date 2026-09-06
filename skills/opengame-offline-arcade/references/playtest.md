# Playtest a finished revision

Use the host's browser tools on the generated HTML, through a file URL or a
temporary server bound to loopback. If browser execution is unavailable,
deliver structurally verified files with that limitation stated.

1. Open the actual exported version. Inspect its rendering and runtime errors.
   Confirm artwork appears and title, target, timer, and lives match settings.
2. Start using the visible control. Use real keyboard or pointer input to
   move, collect an item, and observe score progression. The visible
   collectible should agree with the selected asset.
3. Reach a win and loss with genuine inputs or a short test configuration.
   Restart and verify score, lives, timer, and world reset. Do not change game
   state through JavaScript to manufacture a passing result.
4. Pause, resume, and switch focus while holding movement. Time should stop
   while paused; no stale key should move the player after returning.
5. Check a narrow viewport and pointer/touch input. Inspect its screenshot for
   clipped controls, hidden objectives, and unreadable HUD text.
6. For revisions, check the requested change and previous core loop. Verify
   previous version hashes remain unchanged, then export the new version.

`window.render_game_to_text()` is a read-only observation hook. It reports
phase, score, lives, time, positions, and world dimensions. Compare it with
visible rendering; it does not replace real inputs or visual inspection.

The shipped starter makes no external requests. Check new edits for remote
fonts, scripts, trackers, APIs, and missing local media. Opening standalone
HTML with networking disabled is a useful offline check. A no-network claim
applies to the tested artifact, not to all code a host might later generate.
