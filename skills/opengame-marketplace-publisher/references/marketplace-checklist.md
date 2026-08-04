# Marketplace checklist

Use only the sections for the requested targets. Platform behavior changes, so
check current official documentation and the owner repository's release policy
before the first write in every release session.

## Shared preflight

- Validate and load `opengame-publishing-manifest.v1.json`. Use its exact
  account, source, and allowed-transport values; any missing target or mismatch
  is `blocked`.
- Capture identity-command output without displaying raw stdout or stderr,
  compare it locally, and retain only `match`, redacted `mismatch`, or a
  sanitized failure.
- Confirm the canonical repository, artifact path, clean release lane, and
  source commit or tag.
- Confirm the artifact name or slug, semantic version, public owner, homepage,
  license, and target list.
- Record an explicit action for each target. Never infer that authorization to
  release one target also authorizes another.
- Search the package for credentials, private data, internal URLs, local
  absolute paths, and unlicensed assets.
- Run the repository's own validation and tests.
- Preview the files that will be packaged or uploaded.
- Compare every target's existing public record before changing it.

## GitHub source

- Use one canonical repository rather than maintaining marketplace-specific
  source copies.
- Keep each independently installable Skill in `skills/<slug>/`.
- Pin the release to a pushed commit or tag and record its public URL.
- Avoid publishing from a dirty worktree or an unpushed local commit.

## npm package

- Confirm the package name, version, included files, executable entry point,
  repository, homepage, license, and maintainer namespace.
- Run the package build and tests, then inspect `npm pack --dry-run` output.
- Check whether the account requires interactive 2FA or trusted publishing.
- After publication, inspect the public npm page and test the documented
  install or execution command in a clean environment when practical.

## Official MCP Registry

- Validate the current `server.json` schema and the package binding it names.
- Ensure the package version is already reachable from its canonical package
  registry before publishing the MCP record.
- For OpenGame, run the current official publisher CLI only inside a reviewed
  GitHub Actions workflow owned by `opengameapp`, using GitHub Actions OIDC.
  Do not substitute local GitHub device OAuth unless the manifest policy is
  explicitly changed first.
- Verify the exact server name, package version, status, repository, and
  website on the public registry after publication.

## ClawHub

- Confirm the reviewed source commit is public in
  `opengameapp/OpenGame-skills` and the complete artifact is in
  `skills/<slug>/`.
- Use ClawHub's authenticated web **Import from GitHub** flow. Confirm the
  connected account is the intended `opengameapp` owner, select the candidate
  from `opengameapp/OpenGame-skills`, review its source path and proposed slug,
  then publish in the web UI.
- Do not use a locally bound personal GitHub identity, the ClawHub CLI, or an
  automated publisher for this repository unless the owner explicitly changes
  the release policy.
- `clawhub whoami` (also `clawhub auth whoami`) may verify that a local ClawHub
  token resolves to the expected handle. Require exit code zero and an exact
  manifest match if the CLI is inspected, but do not treat it as GitHub
  ownership evidence or permission to publish through the CLI.
- Check ClawHub's current mandatory license before every release. If it requires
  MIT-0, obtain and record rights-holder approval for the exact bundle under
  those terms; otherwise do not publish it to ClawHub.
- Confirm the intended owner, stable slug, next semantic version, source
  repository, source commit, and source path.
- Review the public Skill page, install command, owner, version, source link,
  license, and scan or moderation state.
- When migrating an existing listing, retain its legacy source folder until
  the public listing verifies the new GitHub repository and path and the
  documented install flow succeeds. Record that verification before removing
  the legacy source.
- Treat a held or hidden listing as `published_pending` until it becomes
  publicly discoverable.

## LobeHub

- Distinguish an MCP listing from a Skill listing; they can use different
  manifests, import paths, and version flows.
- Confirm the GitHub identity or organization that will own or claim the
  listing.
- Validate supported homepage, repository, icon, category, and install fields
  rather than assuming another marketplace's schema is accepted.
- After submission, verify the public page and install flow rather than relying
  on an import or upload acknowledgement.

## Other directories

- Verify that the directory accepts the artifact kind being submitted.
- Prefer official registry ingestion or repository import over copying and
  maintaining another source package.
- Review requested OAuth scopes and repository permissions before consent.
- Do not call an automatically ingested record verified until it is searchable
  and its public page resolves.

## Release evidence template

Record or return one row per requested target:

| Target | Intended identity | Before | Action | Final state | Public URL | Verification or blocker |
| --- | --- | --- | --- | --- | --- | --- |
| `<marketplace>` | `<owner/name@version>` | `<observed>` | `<none/dry-run/publish>` | `<listing_verified/install_verified/published_pending/unchanged/blocked>` | `<url>` | `<evidence>` |

Keep only public identifiers, URLs, versions, source hashes, timestamps, and
safe blocker summaries. Do not store authentication material or browser-session
data in release evidence.
