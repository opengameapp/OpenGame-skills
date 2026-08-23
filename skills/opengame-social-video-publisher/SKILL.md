---
name: opengame-social-video-publisher
description: Prepare, publish, schedule, reconcile, and document reviewed OpenGame videos across YouTube, X, Bluesky, TikTok, Instagram, Facebook, Discord, and Reddit. Use when an operator wants native social uploads, a cross-channel release plan, authenticated browser/CDP execution, platform-specific copy, deduplication, or evidence that each requested post actually reached its intended state.
---

# OpenGame Social Video Publisher

Publish one reviewed OpenGame video campaign without changing the underlying
game or confusing a link share with a native upload.

## Establish the campaign

Require one immutable source or reviewed render, its SHA-256, the canonical
OpenGame page URL, approved copy, selected destinations, destination account
identities, and publish-now or schedule intent. Reuse an existing campaign or
platform operation when those inputs match; do not create a duplicate because
a previous browser or API attempt was interrupted.

Read [references/channel-matrix.md](references/channel-matrix.md) when choosing
native media, orientation, link placement, or destination-specific variants.
Read [references/execution-and-reconciliation.md](references/execution-and-reconciliation.md)
before an authenticated API or browser/CDP effect.

## Keep media and delivery distinct

- Treat cropping, layout, overlays, captions burned into video, timing, and
  orientation as editorial Media work that must be reviewed before publishing.
- A publisher may create a deterministic transport derivative only to satisfy
  a platform's codec, resolution, bitrate, file-size, or fast-start constraint.
  Preserve duration, framing, content, and orientation; bind the derivative to
  the reviewed source hash and record its own hash.
- Never replace a requested native upload with a YouTube link. The standard
  OpenGame exception is Discord, which is link-only after YouTube is public.

## Authorize once, execute exactly

Use the repository's current approval, permit, account, and operation contracts
when they exist. A clear operator instruction authorizes only the destinations
and effects it names; it does not authorize another account or a later batch.
When the exact current request and required local evidence already validate, do
not ask the operator to type another evidence-free `yes`, `完成`, or `继续`.

Pause only for a real boundary such as login, MFA, CAPTCHA, account ambiguity,
missing or drifted evidence, a platform disclosure choice that cannot be
derived safely, or an external attempt whose result cannot be reconciled.
Never store cookies, passwords, tokens, browser profiles, or private account
data in the Skill or repository.

## Report actual states

Execute and reconcile one destination at a time. Record the operation identity,
source and delivery hashes, account identity, remote ID, canonical URL, and
authoritative readback. Report `published`, `scheduled`, `submitted`,
`blocked`, or `excluded` per destination. A scheduled TikTok post is complete
to the schedule boundary but is not publicly published and has no public URL
until it goes live.
