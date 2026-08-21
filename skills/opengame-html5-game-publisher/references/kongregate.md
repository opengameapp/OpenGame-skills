# Kongregate HTML5 publication

Use this reference for a Kongregate developer draft or an existing game’s new
version. Recheck current first-party documentation and the visible dashboard
before each submission:

- <https://docs.kongregate.com/docs/integration-overview>
- <https://docs.kongregate.com/docs/javascript-api>

## Prepare a version

1. Confirm the intended developer account, game title, and existing draft or
   game from the visible dashboard. Do not rely on a guessed preview URL.
2. Keep canonical game source independent of Kongregate. Generate a separate
   platform projection with its own checksum and receipt.
3. For an HTML5/WebGL version, use a root `index.html` game file and one
   additional-files ZIP containing every remaining runtime file, without a
   wrapper directory or a second `index.html`.
4. Set the intended dimensions and persist the listing before upload. If the
   reviewer or current form requires an age rating, put the target audience in
   the description and reload the editor to verify it was saved.
5. If the game uses the Client API, load the documented API script once in the
   document head and wait for initialization. API, authentication, virtual
   goods, and statistics integration are separate decisions; do not add
   account or payment behavior just to upload a non-monetized game.

The upload agreement, rights/creator declaration, no-ads declaration, and
no-external-login-or-microtransactions declaration are distinct legal or
operational assertions. Do not check any newly presented assertion without an
explicit operator decision for that version.

## Verify the hosted build

Use the authenticated Kongregate preview after upload. Confirm the visible
listing and game version survived a clean reload, then verify the actual first
input path reviewers will use: start action, focus, keyboard controls, pointer
control when applicable, pause/resume, and the intended dimensions.

Some Kongregate HTML5 previews have served uploaded ES-module files with an
`application/octet-stream` MIME type. If the preview console reports a module
MIME failure, repeated uploads of the same module graph will not repair it.
Create a Kongregate-only projection that eliminates the external native-module
entry graph—for example, an inline classic-script bundle of local modules—then
rebuild both upload files, record their new checksums, and verify the hosted
version again. Keep the canonical source and other marketplace outputs
unchanged. Treat this as a diagnosed compatibility remedy, not a universal
assumption about every Kongregate game.

A direct game-CDN page can prove that uploaded bytes execute, but it does not
replace preview verification because the Kongregate wrapper supplies its API,
iframe, and first-input conditions. If an owned temporary browser snapshot
blocks the wrapper’s advertising container or other injected surface, recreate
a clean owned snapshot and report the limitation; do not disable extensions in
the user’s source profile or bypass an ad/review gate.

## Correct a rejection and resubmit

1. Preserve the rejection text and classify it as listing, input, build,
   rights, or platform-integration feedback.
2. Change only the owning source or platform projection required to address
   it. Update the listing and immutable release receipt when either changes.
3. Run source checks, release checks, archive inspection, and a browser smoke.
   Then upload the exact new `index.html` and additional-files ZIP as one
   version.
4. Reconcile the dashboard after upload. If the portal lands on a fresh upload
   page, inspect the canonical game dashboard before retrying; do not assume
   the prior version still exists or submit twice.
5. Submit for review only after the corrected hosted preview and saved listing
   are verified. Click the review action once, reload, and record
   `submitted_pending` only when the platform no longer exposes that action or
   shows an equivalent in-review state.

Keep game-specific source commits, checksums, moderation messages, browser
profile labels, dashboard identifiers, and submission dates in the release
owner’s private receipt—not in this public reference.
