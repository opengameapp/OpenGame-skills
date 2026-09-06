#!/usr/bin/env python3
"""Small, offline project store for the OpenGame offline arcade skill.

The on-disk format is deliberately boring: a working copy at the project root
and immutable, hash-addressed snapshots in ``versions/vNNN``.  It never scans
project directories: every payload file is named by this module.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

MAX_FILES = 128
MAX_BYTES = 32 * 1024 * 1024
VERSION_RE = re.compile(r"v([0-9]{3,})$")
SCRIPT_RE = re.compile(
    rb'(<script\s+id="(?P<id>opengame-config|opengame-assets)"\s+'
    rb'type="application/json">)(?P<body>.*?)(</script>)', re.DOTALL)
REQUIRED_ASSETS = (
    "background", "player_idle", "player_move_1", "player_move_2",
    "star", "gem", "hazard",
)
DEFAULT_CONFIG: dict[str, Any] = {
    "schema": "opengame.arcade.v1", "title": "Starberry Meadow", "goal": 8,
    "roundSeconds": 60, "playerSpeed": 220, "hazardSpeed": 85,
    "hazardCount": 3, "maxLives": 3, "collectible": "star", "seed": 1729,
    "palette": {"sky": "#e7f7ef", "field": "#bde3b0", "accent": "#7353d6"},
}


class ProjectError(Exception):
    pass


def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProjectError("JSON contains a duplicate key")
        result[key] = value
    return result


def reject_constant(_: str) -> None:
    raise ProjectError("JSON must not contain NaN or Infinity")


def load_json(path: Path) -> Any:
    try:
        raw = path.read_bytes()
        return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates,
                          parse_constant=reject_constant)
    except ProjectError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectError(f"invalid JSON: {path.name}") from exc


def dumps(value: Any, *, html: bool = False) -> bytes:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if html:
        # Also prevents HTML's <!-- / <script double-escaped parsing states.
        text = text.replace("<", "\\u003c")
    return text.encode("utf-8")


def ensure_dir(path: Path, label: str) -> None:
    if not path.is_dir() or path.is_symlink():
        raise ProjectError(f"{label} is not a safe directory")


def safe_child(root: Path, relative: str) -> Path:
    part = Path(relative)
    if part.is_absolute() or ".." in part.parts or not relative or "\\" in relative:
        raise ProjectError("unsafe payload path")
    target = root / part
    # Do not resolve a missing target; inspect every existing component instead.
    cursor = root
    for item in part.parts:
        cursor = cursor / item
        if cursor.exists() and cursor.is_symlink():
            raise ProjectError("symlink in payload path")
    return target


def read_regular(path: Path) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            raise ProjectError(f"unsafe or missing file: {path.name}")
        data = path.read_bytes()
    except OSError as exc:
        raise ProjectError(f"cannot read: {path.name}") from exc
    if len(data) > MAX_BYTES:
        raise ProjectError("payload is too large")
    return data


def validate_config(value: Any, *, partial: bool = False) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectError("config must be a JSON object")
    allowed = set(DEFAULT_CONFIG)
    unknown = set(value) - allowed
    if unknown:
        raise ProjectError("unknown config field")
    if not partial and set(value) != allowed:
        raise ProjectError("config has missing fields")
    for key, val in value.items():
        if key == "schema" and val != DEFAULT_CONFIG[key]:
            raise ProjectError("schema must be opengame.arcade.v1")
        if key == "title" and (not isinstance(val, str) or not val.strip() or len(val) > 80):
            raise ProjectError("title must be a nonempty string up to 80 characters")
        if key in {"goal", "roundSeconds", "playerSpeed", "hazardSpeed", "hazardCount", "maxLives", "seed"}:
            if type(val) is not int:
                raise ProjectError(f"{key} must be an integer")
        limits = {"goal": (1, 40), "roundSeconds": (10, 300), "playerSpeed": (80, 420),
                  "hazardSpeed": (20, 220), "hazardCount": (0, 8), "maxLives": (1, 9),
                  "seed": (0, 2147483647)}
        if key in limits and not limits[key][0] <= val <= limits[key][1]:
            raise ProjectError(f"{key} is out of range")
        if key == "collectible" and (not isinstance(val, str) or val not in {"star", "gem"}):
            raise ProjectError("collectible must be star or gem")
        if key == "palette":
            if not isinstance(val, dict) or set(val) - set(DEFAULT_CONFIG["palette"]):
                raise ProjectError("palette contains an unknown color")
            if not partial and set(val) != set(DEFAULT_CONFIG["palette"]):
                raise ProjectError("palette has missing colors")
            for color in val.values():
                if not isinstance(color, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
                    raise ProjectError("palette colors must be #RRGGBB")
    return value


def merge_config(current: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    validate_config(override, partial=True)
    merged = dict(current)
    merged["palette"] = dict(current["palette"])
    for key, value in override.items():
        if key == "palette":
            merged["palette"].update(value)
        else:
            merged[key] = value
    validate_config(merged)
    return merged


def asset_source_root() -> Path:
    root = Path(__file__).resolve().parents[1] / "assets"
    ensure_dir(root, "skill assets")
    return root


def load_asset_pack(root: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    pack = load_json(root / "asset-pack.json")
    if not isinstance(pack, dict) or pack.get("packId") != "opengame-meadow-v1" or pack.get("license") != "MIT-0":
        raise ProjectError("invalid asset pack")
    entries = pack.get("assets")
    if not isinstance(entries, list) or len(entries) != len(REQUIRED_ASSETS):
        raise ProjectError("invalid asset inventory")
    files: dict[str, bytes] = {}
    ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"id", "file", "width", "height", "role"}:
            raise ProjectError("invalid asset entry")
        asset_id, filename = entry["id"], entry["file"]
        if asset_id not in REQUIRED_ASSETS or asset_id in ids or not isinstance(filename, str):
            raise ProjectError("invalid asset identifier")
        if type(entry["width"]) is not int or type(entry["height"]) is not int or entry["width"] <= 0 or entry["height"] <= 0 or not isinstance(entry["role"], str):
            raise ProjectError("invalid asset dimensions")
        ids.add(asset_id)
        files[asset_id] = read_regular(safe_child(root, filename))
    if tuple(entry["id"] for entry in entries) != REQUIRED_ASSETS:
        raise ProjectError("unexpected asset inventory order")
    return pack, files


def asset_uris(files: dict[str, bytes]) -> dict[str, str]:
    return {key: "data:image/svg+xml;base64," + base64.b64encode(value).decode("ascii") for key, value in files.items()}


def payload_paths(pack: dict[str, Any]) -> list[str]:
    paths = ["index.html", "game.json", "README.md", "assets/asset-pack.json"]
    paths.extend("assets/" + entry["file"] for entry in pack["assets"])
    return paths


def project_pack(project: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    return load_asset_pack(project / "assets")


def patch_html(html: bytes, config: dict[str, Any], uris: dict[str, str], *, require_markers: bool) -> bytes:
    matches = list(SCRIPT_RE.finditer(html))
    by_id = {name: [m for m in matches if m.group("id") == name] for name in (b"opengame-config", b"opengame-assets")}
    if any(len(by_id[name]) != 1 for name in by_id):
        raise ProjectError("HTML must contain exactly one config and assets JSON block")
    if require_markers:
        if html.count(b"__OPENGAME_CONFIG_JSON__") != 1 or html.count(b"__OPENGAME_ASSETS_JSON__") != 1:
            raise ProjectError("template markers are missing or ambiguous")
    replacements = {b"opengame-config": dumps(config, html=True), b"opengame-assets": dumps(uris, html=True)}
    out: list[bytes] = []
    pos = 0
    for match in matches:
        out.append(html[pos:match.start("body")])
        out.append(replacements[match.group("id")])
        pos = match.end("body")
    out.append(html[pos:])
    return b"".join(out)


def project_config(project: Path) -> dict[str, Any]:
    config = load_json(project / "game.json")
    validate_config(config)
    return config


def write_new(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise ProjectError(f"refusing to overwrite: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def copy_new(source: Path, destination: Path) -> None:
    write_new(destination, read_regular(source))


class Lock:
    def __init__(self, project: Path) -> None:
        self.path = project / ".opengame-lock"
    def __enter__(self) -> "Lock":
        try:
            self.path.mkdir()
        except FileExistsError as exc:
            raise ProjectError("project is busy or has an unresolved lock") from exc
        return self
    def __exit__(self, *_: Any) -> None:
        try:
            self.path.rmdir()
        except OSError:
            pass


def check_project_root(project: Path) -> None:
    ensure_dir(project, "project")
    for name in ("index.html", "game.json", "README.md", "assets", "versions", "project.json"):
        if not (project / name).exists() or (project / name).is_symlink():
            raise ProjectError("not an OpenGame project")
    ensure_dir(project / "assets", "assets")
    ensure_dir(project / "versions", "versions")


def inventory(root: Path, pack: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    total = 0
    paths = payload_paths(pack)
    if len(paths) > MAX_FILES:
        raise ProjectError("too many payload files")
    for relative in paths:
        data = read_regular(safe_child(root, relative))
        total += len(data)
        if total > MAX_BYTES:
            raise ProjectError("payload is too large")
        result.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return result


def compare_embedded(index: bytes, config: dict[str, Any], files: dict[str, bytes]) -> None:
    matches = list(SCRIPT_RE.finditer(index))
    found: dict[bytes, bytes] = {}
    for match in matches:
        identifier = match.group("id")
        if identifier in found:
            raise ProjectError("HTML JSON blocks are ambiguous")
        found[identifier] = match.group("body")
    if set(found) != {b"opengame-config", b"opengame-assets"}:
        raise ProjectError("HTML JSON blocks are missing")
    try:
        actual_config = json.loads(found[b"opengame-config"].decode("utf-8"), object_pairs_hook=no_duplicates, parse_constant=reject_constant)
        actual_assets = json.loads(found[b"opengame-assets"].decode("utf-8"), object_pairs_hook=no_duplicates, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ProjectError) as exc:
        raise ProjectError("HTML has invalid embedded JSON") from exc
    if actual_config != config or actual_assets != asset_uris(files):
        raise ProjectError("HTML embedded config or assets do not match editable source")


def verified_manifest(project: Path, version: str) -> tuple[Path, dict[str, Any]]:
    if not VERSION_RE.fullmatch(version):
        raise ProjectError("invalid version")
    version_dir = safe_child(project / "versions", version)
    ensure_dir(version_dir, "version")
    manifest = load_json(version_dir / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("version") != version or not isinstance(manifest.get("files"), list):
        raise ProjectError("invalid version manifest")
    if len(manifest["files"]) > MAX_FILES:
        raise ProjectError("invalid version manifest")
    seen: set[str] = set()
    total = 0
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "bytes"} or not isinstance(entry["path"], str) or entry["path"] in seen or type(entry["bytes"]) is not int or entry["bytes"] < 0 or not re.fullmatch(r"[0-9a-f]{64}", str(entry["sha256"])):
            raise ProjectError("invalid version file inventory")
        seen.add(entry["path"]); total += entry["bytes"]
        data = read_regular(safe_child(version_dir / "files", entry["path"]))
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ProjectError("snapshot hash mismatch")
    if total > MAX_BYTES or seen != set(payload_paths(load_asset_pack(version_dir / "files" / "assets")[0])):
        raise ProjectError("snapshot payload inventory mismatch")
    config = load_json(version_dir / "files" / "game.json"); validate_config(config)
    pack, files = load_asset_pack(version_dir / "files" / "assets")
    compare_embedded(read_regular(version_dir / "files" / "index.html"), config, files)
    active = config["collectible"]
    if manifest.get("activeCollectible") != active or manifest.get("activeCollectibleSha256") != hashlib.sha256(files[active]).hexdigest():
        raise ProjectError("snapshot collectible metadata mismatch")
    return version_dir, manifest


def verified_versions(project: Path) -> list[tuple[str, dict[str, Any]]]:
    """Return every version in order, failing closed on an incomplete one."""
    candidates: list[tuple[int, str]] = []
    for entry in (project / "versions").iterdir():
        match = VERSION_RE.fullmatch(entry.name)
        if match:
            if entry.is_symlink() or not entry.is_dir():
                raise ProjectError(f"unsafe version entry: {entry.name}")
            candidates.append((int(match.group(1)), entry.name))
    candidates.sort()
    result: list[tuple[str, dict[str, Any]]] = []
    parent: str | None = None
    for _, version in candidates:
        _, manifest = verified_manifest(project, version)
        if manifest.get("parent") != parent:
            raise ProjectError("snapshot parent history is inconsistent")
        parent = version
        result.append((version, manifest))
    return result


def latest_complete(project: Path) -> str:
    versions = verified_versions(project)
    if not versions:
        raise ProjectError("no complete verified snapshot")
    return versions[-1][0]


def expected_project_record(project: Path) -> dict[str, Any]:
    versions = verified_versions(project)
    return {
        "format": "opengame.project.v1",
        "latest": versions[-1][0] if versions else None,
        "history": [{"version": version, "note": manifest["note"]} for version, manifest in versions],
    }


def replace_project_record(project: Path) -> None:
    """Rebuild the advisory pointer from immutable manifests, including after a crash."""
    temporary = project / "project.json.opengame-tmp"
    if temporary.exists() or temporary.is_symlink():
        if temporary.is_symlink() or not temporary.is_file():
            raise ProjectError("unsafe project metadata temporary")
        read_regular(temporary)  # Ensure cleanup only touches a bounded regular file.
        temporary.unlink()
    write_new(temporary, dumps(expected_project_record(project)))
    os.replace(temporary, project / "project.json")


def recover_config_transaction(project: Path) -> None:
    """Finish an interrupted configure without discarding host HTML changes."""
    journal = project / ".opengame-config-journal.json"
    if not (journal.exists() or journal.is_symlink()):
        for name in ("game.json.opengame-tmp", "index.html.opengame-tmp"):
            if (project / name).exists() or (project / name).is_symlink():
                raise ProjectError("orphaned configuration temporary")
        return
    if journal.is_symlink() or not journal.is_file():
        raise ProjectError("unsafe configuration journal")
    state = load_json(journal)
    if not isinstance(state, dict) or set(state) != {"format", "oldConfigSha256", "newConfig", "newConfigSha256", "newHtmlSha256"} or state["format"] != "opengame.configure.v1" or not isinstance(state["newConfig"], dict):
        raise ProjectError("invalid configuration journal")
    validate_config(state["newConfig"])
    for key in ("oldConfigSha256", "newConfigSha256", "newHtmlSha256"):
        if not isinstance(state[key], str) or not re.fullmatch(r"[0-9a-f]{64}", state[key]):
            raise ProjectError("invalid configuration journal")
    current = read_regular(project / "game.json")
    current_hash = hashlib.sha256(current).hexdigest()
    new_config = dumps(state["newConfig"])
    if hashlib.sha256(new_config).hexdigest() != state["newConfigSha256"]:
        raise ProjectError("configuration journal hash mismatch")
    if current_hash not in {state["oldConfigSha256"], state["newConfigSha256"]}:
        raise ProjectError("configuration recovery conflict")
    pack, files = project_pack(project)
    # Re-patching current HTML retains any host-authored edits made after interruption.
    repaired_html = patch_html(read_regular(project / "index.html"), state["newConfig"], asset_uris(files), require_markers=False)
    if hashlib.sha256(repaired_html).hexdigest() != state["newHtmlSha256"] and current_hash == state["oldConfigSha256"]:
        # HTML changed independently before any config replacement: retain it but continue only
        # when its named data blocks remain patchable (the call above already checked this).
        pass
    for name in ("game.json.opengame-tmp", "index.html.opengame-tmp"):
        temporary = project / name
        if temporary.exists() or temporary.is_symlink():
            if temporary.is_symlink() or not temporary.is_file():
                raise ProjectError("unsafe configuration temporary")
            read_regular(temporary); temporary.unlink()
    temporary = project / "game.json.opengame-tmp"; write_new(temporary, new_config); os.replace(temporary, project / "game.json")
    temporary = project / "index.html.opengame-tmp"; write_new(temporary, repaired_html); os.replace(temporary, project / "index.html")
    journal.unlink()


def configure_transaction(project: Path, config: dict[str, Any], html: bytes) -> None:
    journal = project / ".opengame-config-journal.json"
    game_data = dumps(config)
    for path in (journal, project / "game.json.opengame-tmp", project / "index.html.opengame-tmp"):
        if path.exists() or path.is_symlink():
            raise ProjectError("configuration transaction files already exist")
    state = {"format": "opengame.configure.v1", "oldConfigSha256": hashlib.sha256(read_regular(project / "game.json")).hexdigest(),
             "newConfig": config, "newConfigSha256": hashlib.sha256(game_data).hexdigest(),
             "newHtmlSha256": hashlib.sha256(html).hexdigest()}
    write_new(journal, dumps(state))
    try:
        # Both payloads exist before either working-copy file is replaced.
        game_tmp = project / "game.json.opengame-tmp"; html_tmp = project / "index.html.opengame-tmp"
        write_new(game_tmp, game_data); write_new(html_tmp, html)
        os.replace(game_tmp, project / "game.json")
        os.replace(html_tmp, project / "index.html")
        journal.unlink()
    except Exception:
        # The journal is retained to make the next configure or snapshot repair atomically.
        raise


def create(args: argparse.Namespace) -> None:
    requested = Path(args.output).expanduser()
    if requested.exists() or requested.is_symlink():
        raise ProjectError("output path already exists")
    project = requested.resolve(strict=False)
    config = dict(DEFAULT_CONFIG); config["palette"] = dict(DEFAULT_CONFIG["palette"])
    if args.title is not None:
        config = merge_config(config, {"title": args.title})
    if args.config:
        config = merge_config(config, load_json(Path(args.config)))
    source = asset_source_root(); pack, files = load_asset_pack(source)
    project.mkdir(parents=True)
    try:
        write_new(project / "game.json", dumps(config))
        readme = (
            f"# {config['title']}\n\n"
            "Open `index.html` directly in a browser to play offline. Use Arrow keys or WASD to move; "
            "on a pointer or touch device, press and drag in the meadow.\n\n"
            "`game.json` and `assets/` are the editable source files. `index.html` is standalone for "
            "sharing or downloading, with the SVG assets embedded as data URIs. Use `configure` to refresh "
            "its two OpenGame JSON blocks after editing the tuning or source assets, then use `snapshot` to "
            "create immutable `v001`, `v002`, etc. `export` writes a reproducible ZIP of one verified version.\n\n"
            "## Optional resources\n\n"
            "- [OpenGame AI Game Generator](https://opengame.app/?utm_source=opengame-skill&utm_medium=plugin&utm_campaign=offline-arcade)\n"
            "- [OpenGame Showcase](https://opengame.app/showcase?utm_source=opengame-skill&utm_medium=plugin&utm_campaign=offline-arcade)\n"
            "- [OpenGame Skills source](https://github.com/opengameapp/OpenGame-skills)\n"
            "- [OpenGame Showcase source](https://github.com/opengameapp/OpenGame-showcases)\n\n"
            "The included asset pack is licensed under [MIT-0](https://spdx.org/licenses/MIT-0.html).\n"
        ).encode("utf-8")
        write_new(project / "README.md", readme)
        write_new(project / "assets" / "asset-pack.json", dumps(pack))
        for entry in pack["assets"]:
            write_new(safe_child(project / "assets", entry["file"]), files[entry["id"]])
        template = read_regular(source / "template.html")
        write_new(project / "index.html", patch_html(template, config, asset_uris(files), require_markers=True))
        write_new(project / "project.json", dumps({"format": "opengame.project.v1", "latest": None, "history": []}))
        (project / "versions").mkdir()
        snapshot(argparse.Namespace(project=str(project), note="Initial project"))
    except Exception:
        shutil.rmtree(project, ignore_errors=True)
        raise


def configure(args: argparse.Namespace) -> None:
    project = Path(args.project).expanduser().resolve(strict=True); check_project_root(project)
    override: dict[str, Any] = {}
    if args.config: override = load_json(Path(args.config))
    if args.collectible is not None:
        override["collectible"] = args.collectible
    with Lock(project):
        recover_config_transaction(project)
        config = merge_config(project_config(project), override)
        pack, files = project_pack(project)
        html = patch_html(read_regular(project / "index.html"), config, asset_uris(files), require_markers=False)
        configure_transaction(project, config, html)


def snapshot(args: argparse.Namespace) -> None:
    project = Path(args.project).expanduser().resolve(strict=True); check_project_root(project)
    if not isinstance(args.note, str) or not args.note.strip() or len(args.note) > 240:
        raise ProjectError("note must be a nonempty string up to 240 characters")
    with Lock(project):
        recover_config_transaction(project)
        # A previous completed snapshot can exist even when project.json was not updated.
        replace_project_record(project)
        config = project_config(project); pack, files = project_pack(project)
        compare_embedded(read_regular(project / "index.html"), config, files)
        versions = verified_versions(project)
        previous = versions[-1][0] if versions else None
        number = 1 if previous is None else int(VERSION_RE.fullmatch(previous).group(1)) + 1
        version = f"v{number:03d}"; version_dir = project / "versions" / version
        if version_dir.exists(): raise ProjectError("version destination already exists")
        version_dir.mkdir(); files_dir = version_dir / "files"
        try:
            for relative in payload_paths(pack): copy_new(safe_child(project, relative), safe_child(files_dir, relative))
            manifest = {"format": "opengame.snapshot.v1", "version": version, "parent": previous,
                        "note": args.note, "activeCollectible": config["collectible"],
                        "activeCollectibleSha256": hashlib.sha256(files[config["collectible"]]).hexdigest(),
                        "files": inventory(files_dir, pack)}
            write_new(version_dir / "manifest.json", dumps(manifest))
            verified_manifest(project, version)
            replace_project_record(project)
        except Exception:
            # A completed directory is intentionally preserved if a pointer update crashes.
            if not (version_dir / "manifest.json").exists(): shutil.rmtree(version_dir, ignore_errors=True)
            raise


def verify(args: argparse.Namespace) -> None:
    project = Path(args.project).expanduser().resolve(strict=True); check_project_root(project)
    version = args.version or latest_complete(project)
    _, manifest = verified_manifest(project, version)
    print(f"verified {version}: {len(manifest['files'])} files (structural only; browser gameplay not executed)")


def export(args: argparse.Namespace) -> None:
    project = Path(args.project).expanduser().resolve(strict=True); check_project_root(project)
    requested = Path(args.output).expanduser()
    if requested.exists() or requested.is_symlink(): raise ProjectError("export destination already exists")
    output = requested.resolve(strict=False)
    version_dir, manifest = verified_manifest(project, args.version)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Acquire the destination before enabling cleanup: another export may have
    # created it while this operation was verifying the snapshot.
    with output.open("xb") as handle:
        owned_file = os.fstat(handle.fileno())
        try:
            with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
                names = [entry["path"] for entry in manifest["files"]] + ["version.json"]
                for name in names:
                    data = dumps(manifest) if name == "version.json" else read_regular(safe_child(version_dir / "files", name))
                    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
                    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        except Exception:
            try:
                if os.path.samestat(output.lstat(), owned_file):
                    output.unlink()
            except FileNotFoundError:
                pass
            raise


def inspect(args: argparse.Namespace) -> None:
    project = Path(args.project).expanduser().resolve(strict=True); check_project_root(project)
    config = project_config(project); latest = latest_complete(project)
    record = load_json(project / "project.json")
    pointer = record.get("latest") if isinstance(record, dict) else None
    print(json.dumps({"project": str(project), "title": config["title"], "collectible": config["collectible"], "latestVerified": latest,
                      "projectPointer": pointer, "pointerMatchesVerified": pointer == latest,
                      "projectPointerTemporaryPresent": (project / "project.json.opengame-tmp").exists()}, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="project.py", description="Offline OpenGame project helper")
    commands = result.add_subparsers(dest="command", required=True)
    item = commands.add_parser("create"); item.add_argument("--output", required=True); item.add_argument("--title"); item.add_argument("--config"); item.set_defaults(func=create)
    item = commands.add_parser("configure"); item.add_argument("--project", required=True); item.add_argument("--config"); item.add_argument("--collectible", choices=("star", "gem")); item.set_defaults(func=configure)
    item = commands.add_parser("snapshot"); item.add_argument("--project", required=True); item.add_argument("--note", required=True); item.set_defaults(func=snapshot)
    item = commands.add_parser("verify"); item.add_argument("--project", required=True); item.add_argument("--version"); item.set_defaults(func=verify)
    item = commands.add_parser("export"); item.add_argument("--project", required=True); item.add_argument("--version", required=True); item.add_argument("--output", required=True); item.set_defaults(func=export)
    item = commands.add_parser("inspect"); item.add_argument("--project", required=True); item.set_defaults(func=inspect)
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        args.func(args)
        return 0
    except ProjectError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
