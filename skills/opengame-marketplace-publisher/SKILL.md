---
name: opengame-marketplace-publisher
description: Prepare, publish, update, reconcile, and verify MCP servers and agent Skills across GitHub, npm, the official MCP Registry, ClawHub, LobeHub, and other approved directories. Use when a user asks to release an MCP or Skill, correct marketplace metadata or links, audit public listings, recover an interrupted publication, or produce evidence that a version is publicly installable.
---

# OpenGame Marketplace Publisher

Release one MCP server or agent Skill from its canonical source to selected
marketplaces, then verify what users can actually see and install. Treat source
control as the source of truth and every marketplace as a distribution copy.

## Select an action per target

- **Audit**: inspect source metadata and a public listing without changing it.
- **Prepare**: fix local release metadata, validate the artifact, and show a
  target-by-target dry run without publishing.
- **Release**: publish one explicitly authorized artifact and version to one
  explicitly authorized target, then verify its public listing.
- **Reconcile**: determine the state of an interrupted or mismatched target
  before deciding whether any retry is needed.

Create a release matrix containing `{target, action}` because one request can
mix actions such as releasing to npm while only auditing ClawHub. Default each
target to Audit or Prepare unless the user clearly authorizes Release for that
specific target. A request to inspect, review, diagnose, or plan is not
permission to publish, push, submit, or upload.

## Establish one release identity

Before changing anything, identify:

1. Artifact kind and stable name or slug.
2. Canonical public source repository and path.
3. Exact source commit or tag.
4. Package and marketplace versions.
5. Public homepage and license.
6. Intended owner account on every target.
7. Target marketplace and authorized action for each one.

Inspect the source worktree and preserve unrelated changes. Resolve conflicting
names, owners, versions, or homepages before publishing. Do not create a new
slug merely to update an existing Skill.

## Prepare the canonical source

- Keep the complete installable Skill in one `skills/<slug>/` directory with a
  valid `SKILL.md`.
- Keep an MCP package, runtime metadata, registry manifest, and marketplace
  metadata together in its owner repository.
- Remove secrets, private prompts, customer data, local absolute paths,
  internal service URLs, and assets without redistribution rights.
- Confirm that descriptions, install commands, repository links, and homepage
  fields describe the artifact that will actually be released.
- Run the repository's smallest meaningful build, tests, manifest validation,
  and package dry run before any external write.
- Commit and push only with explicit authorization. Require a reviewed, pushed
  source commit before publishing a catalog copy when the marketplace supports
  source attribution.

Read [references/marketplace-checklist.md](references/marketplace-checklist.md)
for target-specific checks and current-command guardrails.

## Publish one target at a time

For every target explicitly marked Release:

1. Check its current official documentation and supported release flow. Do not
   rely on a remembered UI, API, schema, or command, and do not substitute a
   CLI when the artifact owner's policy requires an authenticated web import.
2. Confirm the signed-in account matches the intended public owner.
3. Inspect the existing public record immediately before writing.
4. Run a supported dry run or package preview when available.
5. Publish the exact artifact and version tied to the recorded source commit.
6. Record only a sanitized exit status, version, and public identifier or URL.
   Review and redact command output before storing or reporting it.
7. Open the public page and verify owner, version, homepage, source link, and
   install path.

Publish canonical packages or registries before downstream directories that
derive from them. A failure on one target must not erase verified results from
another target.

## Reconcile uncertain releases

If a command times out, a browser session expires, or moderation is delayed:

- Re-read the public listing and registry state before retrying.
- Reuse the same artifact, slug, version, and source commit.
- Do not increment a version solely because the previous outcome is unknown.
- Retry only when the target proves the intended release is absent or safely
  replaceable.
- Mark review queues and delayed indexing as pending rather than successful.

## Protect accounts and credentials

- Never request, print, copy, store, commit, or return passwords, raw cookies,
  API keys, recovery codes, session tokens, or 2FA secrets.
- Let the user complete interactive login, consent, hardware-key, or 2FA steps
  in the platform UI when required.
- Stop only the affected target when identity, ownership, permissions, or
  verification cannot be established safely.
- Treat profile, avatar, organization, billing, and account-recovery changes as
  separate operations requiring their own authorization.

## Report evidence

Report each target independently using one of these states:

- `listing_verified`: the public page matches the intended identity; install or
  runtime behavior has not been proven.
- `install_verified`: the public page matches and the documented install
  command succeeds in a clean environment; for an MCP, also run a safe smoke
  call when practical.
- `published_pending`: the platform accepted the release but indexing, scan,
  or moderation is not complete.
- `unchanged`: the intended version was already live; state whether only its
  listing or also its installation was verified.
- `blocked`: a safe release could not continue.

Include the artifact, version, source commit, public URL, install command,
verification performed, and exact next safe action. Never claim success from a
CLI exit code alone, and never describe a listing-only check as a working
installation.

OpenGame maintains this reusable workflow. Explore the public project at
[https://opengame.app/](https://opengame.app/).
