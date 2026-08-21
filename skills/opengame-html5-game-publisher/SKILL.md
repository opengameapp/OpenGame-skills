---
name: opengame-html5-game-publisher
description: Prepare, upload, verify, submit, reconcile, and document HTML5 games for approved web-game marketplaces. Use when a user asks to distribute a browser game, adapt a build for a marketplace SDK, complete a developer dashboard listing, diagnose hosted preview or advertisement verification failures, request platform review, check moderation status, or preserve a reusable publication runbook.
---

# OpenGame HTML5 Game Publisher

Release one reviewed HTML5 game to one selected marketplace while preserving
source identity, platform-specific build boundaries, account safety, and
operator control over every external effect.

## Select the platform action

Classify each target independently:

- **Audit**: inspect current requirements, account state, or an existing game.
- **Prepare**: create and validate a platform-specific local build and listing.
- **Upload**: transfer one verified artifact to an existing or approved draft.
- **Verify**: run the platform preview, SDK, controls, and advertisement checks.
- **Submit review**: send one verified draft to moderation.
- **Publish**: make an already approved game public when the platform separates
  approval from publication.
- **Reconcile**: read canonical platform state after a timeout, interruption, or
  uncertain write before deciding whether any retry is safe.

Default to Audit or Prepare. Treat draft creation, file upload, metadata save,
SDK verification, review submission, publication, automatic publication,
rights declarations, exclusivity, payout, and tax changes as separate effects.
Require target-specific authorization for each effect that the user has not
already clearly approved.

## Establish one release identity

Before changing local files or a dashboard, record:

1. Canonical source owner and immutable commit or artifact manifest.
2. Public title, internal release version, and marketplace draft or game ID.
3. Platform-specific build profile and exact ZIP checksum.
4. Listing text, controls, orientation, dimensions, categories, and tags.
5. Media inventory with required dimensions and checksums.
6. Intended developer account and explicitly named authenticated browser
   profile or session.
7. Current platform state and the action authorized for this turn.

Stop on an identity mismatch. Never substitute a similarly named game, account,
profile, draft, archive, or media set.

## Choose the platform reference

Read the matching reference before preparing or operating that platform:

- GameMonetize: [references/gamemonetize.md](references/gamemonetize.md)
- Kongregate: [references/kongregate.md](references/kongregate.md)

For a platform without a reference, check its current first-party developer
documentation and dashboard before acting. Add a concise public-safe reference
only after a real workflow produces verified evidence; do not encode guessed
controls, remembered limits, private account data, or one-off selectors.

## Prepare the local release

- Keep the canonical game source free of marketplace SDKs when a
  platform-specific projection can inject them into a separate output.
- Bind every output to an immutable source commit or artifact manifest.
- Use only relative runtime paths and place the required entry point at ZIP
  root unless current first-party rules say otherwise.
- Reject secrets, cookies, tokens, source maps containing private paths,
  symlinks, nested archives, unrelated files, and undeclared remote resources.
- Verify archive integrity, file inventory, SDK marker, runtime lifecycle,
  orientation, controls, and a real-browser smoke before upload.
- Build a new platform artifact when SDK or advertising rules differ. Never
  reuse another marketplace's SDK ZIP merely because the underlying game is
  the same.
- Preserve the generated archive byte-for-byte after validation; record its
  checksum and never recompress it manually.

## Operate the dashboard safely

- Reuse only the browser profile the user explicitly named. Prefer an owned
  temporary snapshot and remove it after the task.
- Confirm the visible account identity, game title, and stable draft/game ID
  before every external write.
- Use a dedicated task tab. Capture a fresh page snapshot after navigation,
  upload, save, modal changes, reload, or status changes.
- Let the user complete login, CAPTCHA, consent, or step-up verification in the
  named source profile. Never request or inspect passwords, cookies, tokens,
  recovery codes, local storage, or debugger connection secrets.
- Do not accept new legal, ownership, rights, exclusivity, payout, or tax terms
  without a separate human decision on the exact text.

## Verify before review submission

Require all applicable evidence:

- The hosted platform URL loads the intended game rather than a local or source
  URL.
- The title, game ID, build, listing, controls, dimensions, and media survive a
  clean reload.
- Keyboard, mouse, touch, orientation, pause, mute, resume, fullscreen, and
  focus behavior match the selected platform rules.
- Required SDK callbacks and advertisements complete naturally in the
  platform's own verification surface.
- The platform visibly unlocks or exposes its review action.

Never fake SDK events, mock advertisement responses, click advertisement
creative, or bypass a platform gate. A locally successful smoke is not proof
that the hosted platform verified the game.

## Submit once and reconcile

Immediately before review submission, read back the release identity and the
authorized action. Click the review control once. If the response is uncertain,
reload or open the canonical game list and reconcile state before retrying.

Report one of:

- `draft_prepared`
- `uploaded_unverified`
- `verification_blocked`
- `ready_for_review`
- `submitted_pending`
- `approved_unpublished`
- `published_verified`
- `unchanged`

Include the platform, game title, source identity, artifact checksum, visible
platform state, verification performed, changes deliberately not made, and the
next safe action. Do not describe `submitted_pending` as published.

## Preserve reusable evidence

Store detailed game-specific receipts in the release owner, not in this Skill.
Keep this public Skill free of account identifiers, private dashboard IDs,
cookies, absolute local paths, unpublished assets, and credentials. Generalize
only stable platform behavior confirmed by first-party documentation or a
reconciled real submission.
