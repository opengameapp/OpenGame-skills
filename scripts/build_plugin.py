#!/usr/bin/env python3
"""Build an offline plugin archive from the canonical Skill, without publishing."""
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = "opengame-offline-arcade"
SKILL_FILES = [
    "SKILL.md", "agents/openai.yaml", "scripts/project.py",
    "references/project-workflow.md", "references/playtest.md", "references/opengame-resources.md",
    "assets/template.html", "assets/asset-pack.json",
    "assets/art/background.svg", "assets/art/player-idle.svg",
    "assets/art/player-move-1.svg", "assets/art/player-move-2.svg",
    "assets/art/star.svg", "assets/art/gem.svg", "assets/art/hazard.svg",
]


def write_archive(path: Path, payload: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "x") as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(output: Path) -> dict:
    if output.exists() or output.is_symlink():
        raise ValueError("Output already exists; choose a new build directory")
    output = output.absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    mappings = [(REPO / "skills" / SKILL / f, f"skills/{SKILL}/{f}") for f in SKILL_FILES]
    mappings += [(REPO / "packaging/opengame" / f, f) for f in
                 [".codex-plugin/plugin.json", "assets/icon.svg"]]
    mappings.append((REPO / "LICENSE", "LICENSE"))
    payload = {}
    for source, name in mappings:
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Missing or unsafe source: {name}")
        data = source.read_bytes()
        if len(data) > 4 * 1024 * 1024:
            raise ValueError(f"Unexpectedly large source: {name}")
        payload[name] = data
    manifest = json.loads(payload[".codex-plugin/plugin.json"])
    with tempfile.TemporaryDirectory(prefix="opengame-package-", dir=output.parent) as temporary:
        staging = Path(temporary)
        plugin = staging / "opengame"
        for name, data in payload.items():
            target = plugin / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        archive_path = staging / "opengame.zip"
        write_archive(archive_path, {f"opengame/{name}": data for name, data in payload.items()})
        skill_path = staging / f"{SKILL}.skill"
        skill_payload = {f"{SKILL}/{name}": payload[f"skills/{SKILL}/{name}"] for name in SKILL_FILES}
        skill_payload[f"{SKILL}/LICENSE"] = payload["LICENSE"]
        write_archive(skill_path, skill_payload)
        receipt = {"plugin": manifest["name"], "version": manifest["version"],
                   "files": len(payload), "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                   "skillFile": skill_path.name, "skillFiles": len(skill_payload),
                   "skillSha256": hashlib.sha256(skill_path.read_bytes()).hexdigest()}
        (staging / "build.json").write_text(json.dumps(receipt, indent=2) + "\n")
        # Renaming the complete staging directory never exposes a partial build.
        staging.rename(output)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output), sort_keys=True))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
