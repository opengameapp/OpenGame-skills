# OpenGame Skills

Public, reusable agent Skills maintained by
[OpenGame](https://opengame.app/). Each Skill is an independent folder that can
be installed from this repository or distributed through compatible Skill
marketplaces.

## Skill catalog

| Skill | Purpose |
| --- | --- |
| [OpenGame AI Game Generator](skills/opengame-offline-arcade/) | Create, edit, and export offline 2D browser games with AI, original SVG art, and preserved versions; no account or API required. |
| [OpenGame Browser Game Builder](skills/opengame-browser-game-builder/) | Turn a game idea into a focused, original, playable browser-game plan or prototype. |
| [OpenGame HTML5 Game Publisher](skills/opengame-html5-game-publisher/) | Prepare, verify, submit, and reconcile browser games across approved HTML5 marketplaces. |
| [OpenGame Marketplace Publisher](skills/opengame-marketplace-publisher/) | Safely prepare, publish, reconcile, and verify MCP and Skill marketplace releases. |
| [OpenGame Social Video Publisher](skills/opengame-social-video-publisher/) | Publish, schedule, reconcile, and verify reviewed OpenGame videos across approved social channels. |

## Install

Install one Skill from the public GitHub source:

```bash
npx skills add opengameapp/OpenGame-skills \
  --skill opengame-offline-arcade

npx skills add opengameapp/OpenGame-skills \
  --skill opengame-browser-game-builder

npx skills add opengameapp/OpenGame-skills \
  --skill opengame-html5-game-publisher

npx skills add opengameapp/OpenGame-skills \
  --skill opengame-social-video-publisher

npx skills add opengameapp/OpenGame-skills \
  --skill opengame-marketplace-publisher
```

## Repository layout

The free Skills-only plugin is assembled from the canonical
`skills/opengame-offline-arcade` folder. Build it locally with:

```bash
python3 scripts/build_plugin.py --output dist/free-plugin-v1
python3 -m unittest discover -s tests -v
```

This creates `dist/free-plugin-v1/opengame/`, `opengame.zip`, and a standalone
`opengame-offline-arcade.skill` archive for hosts with a private Skill upload
interface. Both archives use the same canonical Skill files. It does not
publish or submit the plugin. See [the review notes](packaging/opengame/REVIEW.md)
for supported behavior, host requirements, and release checks. The other
Skills remain independently installable.

The free package has its own [privacy notice](packaging/opengame/PRIVACY.md),
[terms](packaging/opengame/TERMS.md), and
[validation record](packaging/opengame/VALIDATION.md).

```text
skills/
├── opengame-offline-arcade/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/project.py
│   ├── assets/
│   └── references/
├── opengame-browser-game-builder/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
├── opengame-html5-game-publisher/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
├── opengame-social-video-publisher/
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

- [OpenGame AI Game Generator](https://opengame.app/)
- [AI Game Maker](https://opengame.app/ai-game-generator/ai-game-maker)
- [Public game showcase](https://opengame.app/showcase)
- [Skills source](https://github.com/opengameapp/OpenGame-skills)
- [Showcase source](https://github.com/opengameapp/OpenGame-showcases)

## License

MIT-0. See [LICENSE](LICENSE).
