# OpenGame Skills

Public, reusable agent Skills maintained by
[OpenGame](https://opengame.app/). Each Skill is an independent folder that can
be installed from this repository or distributed through compatible Skill
marketplaces.

## Skill catalog

| Skill | Purpose |
| --- | --- |
| [OpenGame Browser Game Builder](skills/opengame-browser-game-builder/) | Turn a game idea into a focused, original, playable browser-game plan or prototype. |
| [OpenGame Marketplace Publisher](skills/opengame-marketplace-publisher/) | Safely prepare, publish, reconcile, and verify MCP and Skill marketplace releases. |

## Install

Install one Skill from the public GitHub source:

```bash
npx skills add opengameapp/OpenGame-skills \
  --skill opengame-browser-game-builder

npx skills add opengameapp/OpenGame-skills \
  --skill opengame-marketplace-publisher
```

## Repository layout

```text
skills/
├── opengame-browser-game-builder/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
└── opengame-marketplace-publisher/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
```

GitHub is the canonical source of truth. Marketplace copies are imported from
the reviewed public folders after their source commit is live. This repository
does not contain credentials, production runtime code, customer data, private
prompts, or automatic marketplace-publishing credentials.

## OpenGame

- [Official website](https://opengame.app/)
- [AI Game Maker](https://opengame.app/ai-game-generator/ai-game-maker)
- [Public game showcases](https://github.com/opengameapp/OpenGame-showcases)

## License

MIT-0. See [LICENSE](LICENSE).
