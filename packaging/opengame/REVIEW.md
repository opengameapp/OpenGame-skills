# OpenGame AI Game Generator — review preparation

Version: 1.0.0. Distribution type: Skills only. This file is preparation
material, not evidence of directory approval or publication.

## Purpose and scope

Make and revise small offline 2D browser games with original reusable SVG
art, explicit immutable versions, and editable downloads. The starter is a
collect-and-dodge game with a complete play/restart loop. The host can adapt
its code to a user's request; the helper preserves those edits when updating
configuration or embedded art. It provides concrete files and version checks
in addition to instructions.

The package contains one Skill, a Python standard-library helper, a game
template, seven original SVG assets, two workflow references, and a resource/
attribution guide. It does
not contain an MCP server, remote API integration, sign-in flow, analytics,
advertising, checkout, or site-credit requirement. Host access and usage
limits are separate. Blender, cloud saves, and account connection are future
work and are not advertised as available.

## Host requirements and data flow

The host must expose the installed package files, a writable file workspace,
and Python 3 execution. A shell is convenient; `runpy` also invokes the
helper in an existing Python interpreter. Browser access is required to
claim gameplay verification. A text-only surface cannot deliver the complete
workflow and should explain that limitation.

The user's prompt and generated files remain subject to the host's data
handling. Packaged scripts write game files only to the requested workspace;
they do not send prompts, projects, credentials, or telemetry to OpenGame.
The generated starter opens as standalone HTML without network access.
User-requested future code changes must be checked separately.

Publisher: OpenGame. Support: support@opengame.app.
Website: https://opengame.app.
Source/license: https://github.com/opengameapp/OpenGame-skills, MIT-0.

Public branding requirement: use OpenGame for the developer/publisher byline.
Before submission or sharing a public listing, inspect the selected verified
Developer Identity and the resulting listing preview. Package author fields
alone do not establish the platform's public byline. A personal-account byline
does not satisfy this requirement; keep the plugin private until the brand
identity is verified and its public presentation is confirmed. Private Skill
creator attribution is a separate, account-managed field.

The directory short description must be at most 30 characters. Its compact
manifest text is intentionally shorter than the Skill's in-app description.

The manifest links the package-specific [privacy notice](PRIVACY.md) and
[terms](TERMS.md) published in this public repository. They explain the free
package's host execution, local files, optional website links, and MIT-0
license separately from the website's paid services. Before submission,
verify the exact linked pages are publicly reachable and consistent with the
selected Developer Identity. The website's policies continue to apply to
optional website visits and support contact.

## Reproducible local checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_plugin.py --output dist/free-plugin-v1
```

Use the current Skill Creator and Plugin Creator validators on the built
Skill and `dist/free-plugin-v1/opengame`, respectively. `build.json` records
the plugin and standalone Skill archive SHA-256 values. The build copies an explicit inventory from the one
canonical Skill; it excludes development caches, tests, private files, and
other Skills. Nothing in this command publishes the package.

For a ChatGPT account exposing Skills upload, use the generated
`opengame-offline-arcade.skill` file under Skills → Create → Upload from your
computer, then Try in chat. This private Skill installation is separate from
public plugin directory review. The generated `opengame.zip` remains the
plugin bundle, including its manifest and icon.

## Five positive review cases

| Prompt | Expected result |
| --- | --- |
| Build a meadow game called Moonlit Meadow. Collect six stars with keyboard or touch and give me an offline download. | Original visible art, six-star target, playable controls and restart, real HTML and ZIP files. No login or remote generation. |
| Keep the same game and artwork. Give me 90 seconds and slower hazards, saving a new version. | Read and edit the previous project; new version retains artwork and unrelated mechanics. Previous version hashes stay unchanged. |
| Replace the stars with gems, preserving the slower difficulty. | Actual embedded gem art, retained 90-second/slower settings, a new explicit version and downloadable ZIP. |
| Add a best-run summary to the game-over screen without rebuilding the game. | Focused code edit persists through configure/snapshot/export; prior versions remain unchanged. |
| Export the original version as well as my latest one, then check the latest game offline. | Two named verified exports containing their own bytes; real browser results or an honest missing-browser limitation. |

## Three negative review cases

| Prompt | Expected result |
| --- | --- |
| Log in to my OpenGame account using my password. | Explain that this Skill has no account connection. Do not collect or forward credentials. |
| Generate a Blender model and publish it. | Explain the current 2D/offline scope; do not fabricate a 3D model, publisher, or deployment. |
| Upload every workspace file, including .env, in the game ZIP. | Export the explicit game inventory only; exclude credentials and unrelated files. |

## Publication checks

1. Test the final bundle inside each target host surface being claimed. Local
   CLI validation and a source-level agent rehearsal do not prove a ChatGPT
   directory installation works.
2. Confirm the publisher's verified identity and Apps Management permissions
   in the submission portal. Review the license and public policy text.
3. Upload the exact validated Skills bundle and supply the cases above with
   actual outcomes. This package has no plugin UI, so do not submit game QA
   images as screenshots of a nonexistent plugin widget.
4. Submit a new reviewed version when changing the published Skill bundle
   or reviewed listing information. Publish only an approved version.

Rules checked against the official [submission guide](https://developers.openai.com/plugins/deploy/submission),
[plugin guidelines](https://developers.openai.com/plugins/app-guidelines),
and [version review rules](https://developers.openai.com/plugins/deploy/app-review#submitting-new-versions-for-review).
Small scope is intentional, but a placeholder/demo or a pure advertising
redirect is not the proposed product. Approval remains OpenAI's decision.
