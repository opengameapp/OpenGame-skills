# OpenGame Skills — Agent Instructions

This public repository is the canonical source for reusable OpenGame agent
Skills. It does not own OpenGame product runtime code, private operations, or
marketplace credentials.

## Repository rules

- Keep each independently useful Skill in `skills/<skill-slug>/` with the
  folder name matching the `name` in `SKILL.md`.
- Keep `SKILL.md` concise. Add only the `agents/`, `references/`, `scripts/`, or
  `assets/` files that the Skill actually needs.
- Do not add local absolute paths, internal repositories, credentials, cookies,
  tokens, private prompts, customer data, production configuration, or assets
  without redistribution rights.
- Preserve unrelated changes and use one writer for shared catalog files.
- Validate every changed Skill with the current skill-creator validator and run
  the smallest meaningful discovery or install check before release.
- Treat GitHub as the source of truth. Do not publish, import, update, transfer,
  or delete an external marketplace listing without explicit target-specific
  authorization.
- ClawHub publication is a manual import from the reviewed public GitHub source.
  Do not add an automated ClawHub publishing workflow unless the repository
  owner explicitly changes this policy.
- Confirm the current marketplace license and account identity before every
  external release. This repository is licensed under MIT-0.
