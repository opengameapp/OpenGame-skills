"""Integration checks for the user-visible create/revise/download workflow."""
import hashlib
from html import unescape
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "skills/opengame-offline-arcade/scripts/project.py"
spec = importlib.util.spec_from_file_location("arcade_project", CLI)
project_helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project_helper)


class ArcadeWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="opengame-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "game"
        self.run_cli("create", "--output", self.project)

    def run_cli(self, *args, success=True):
        result = subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def patch(self, value):
        path = self.root / "override.json"
        path.write_text(json.dumps(value))
        self.run_cli("configure", "--project", self.project, "--config", path)

    def tree_hashes(self, root):
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*") if p.is_file()}

    def test_three_versions_preserve_code_art_and_explicit_exports(self):
        v1 = self.tree_hashes(self.project / "versions/v001")
        custom = b"\n<!-- User's previous gameplay edit stays here. -->\n"
        html = self.project / "index.html"
        html.write_bytes(html.read_bytes() + custom)
        self.patch({"roundSeconds": 90, "hazardSpeed": 55, "palette": {"accent": "#3459c7"}})
        self.run_cli("snapshot", "--project", self.project, "--note", "Slower hazards")
        v2 = self.tree_hashes(self.project / "versions/v002")
        self.run_cli("configure", "--project", self.project, "--collectible", "gem")
        self.run_cli("snapshot", "--project", self.project, "--note", "Use gems")
        self.assertEqual(v1, self.tree_hashes(self.project / "versions/v001"))
        self.assertEqual(v2, self.tree_hashes(self.project / "versions/v002"))
        self.assertTrue(html.read_bytes().endswith(custom))
        config = json.loads((self.project / "game.json").read_text())
        self.assertEqual((config["roundSeconds"], config["hazardSpeed"], config["collectible"]), (90, 55, "gem"))
        self.assertEqual(config["palette"]["sky"], "#e7f7ef")
        manifests = [json.loads((self.project / f"versions/v00{i}/manifest.json").read_text()) for i in (1, 2, 3)]
        self.assertEqual([m["parent"] for m in manifests], [None, "v001", "v002"])
        self.assertNotEqual(manifests[1]["activeCollectibleSha256"], manifests[2]["activeCollectibleSha256"])
        for version in ("v001", "v002", "v003"):
            self.run_cli("verify", "--project", self.project, "--version", version)
            self.run_cli("export", "--project", self.project, "--version", version, "--output", self.root / f"{version}.zip")
        with zipfile.ZipFile(self.root / "v001.zip") as archive:
            self.assertNotIn(custom, archive.read("index.html"))
        with zipfile.ZipFile(self.root / "v003.zip") as archive:
            self.assertIn(custom, archive.read("index.html"))
            self.assertIn('"collectible":"gem"', archive.read("index.html").decode())

    def test_download_is_reproducible_and_excludes_unrelated_private_files(self):
        (self.project / ".env").write_text("TEST_ONLY_PRIVATE_MARKER=yes")
        (self.project / "unrelated.txt").write_text("not part of game")
        for name in ("a.zip", "b.zip"):
            self.run_cli("export", "--project", self.project, "--version", "v001", "--output", self.root / name)
        self.assertEqual((self.root / "a.zip").read_bytes(), (self.root / "b.zip").read_bytes())
        with zipfile.ZipFile(self.root / "a.zip") as archive:
            self.assertEqual(len(archive.namelist()), 12)
            self.assertNotIn(".env", archive.namelist())
            self.assertNotIn("unrelated.txt", archive.namelist())
            self.assertFalse(any(name.startswith("/") or ".." in Path(name).parts for name in archive.namelist()))
            self.assertNotIn(b"TEST_ONLY_PRIVATE_MARKER", b"".join(archive.read(n) for n in archive.namelist()))

    def test_title_cannot_break_out_of_embedded_json(self):
        for title in ('</script><script>window.bad=1</script>', '<!--<script>'):
            with self.subTest(title=title):
                self.patch({"title": title})
                index = (self.project / "index.html").read_text()
                body = re.search(r'<script id="opengame-config" type="application/json">(.*?)</script>', index, re.S).group(1)
                self.assertEqual(json.loads(body)["title"], title)
                self.assertNotIn(title, index)
                self.run_cli("snapshot", "--project", self.project, "--note", "Literal title")

    def test_invalid_overrides_do_not_modify_working_files(self):
        before = self.tree_hashes(self.project)
        for value in ('{"goal":2,"goal":3}', '{"playerSpeed":NaN}', '{"apiKey":"unused"}', '{"hazardCount":-1}', '{"collectible":[]}'):
            with self.subTest(value=value):
                path = self.root / "bad.json"
                path.write_text(value)
                result = self.run_cli("configure", "--project", self.project, "--config", path, success=False)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(before, self.tree_hashes(self.project))

    def test_existing_destinations_and_busy_project_are_preserved(self):
        before = self.tree_hashes(self.project)
        self.run_cli("create", "--output", self.project, success=False)
        target = self.root / "existing.zip"
        target.write_bytes(b"keep me")
        self.run_cli("export", "--project", self.project, "--version", "v001", "--output", target, success=False)
        self.assertEqual(target.read_bytes(), b"keep me")
        (self.project / ".opengame-lock").mkdir()
        self.run_cli("configure", "--project", self.project, "--collectible", "gem", success=False)
        self.assertEqual(before, self.tree_hashes(self.project))

    def test_tampered_latest_is_reported_and_explicit_old_version_still_works(self):
        self.patch({"collectible": "gem"})
        self.run_cli("snapshot", "--project", self.project, "--note", "Gem version")
        target = self.project / "versions/v002/files/assets/art/star.svg"
        target.write_bytes(target.read_bytes() + b"tampered")
        self.run_cli("verify", "--project", self.project, success=False)
        self.run_cli("inspect", "--project", self.project, success=False)
        self.run_cli("export", "--project", self.project, "--version", "v002", "--output", self.root / "bad.zip", success=False)
        self.assertFalse((self.root / "bad.zip").exists())
        self.run_cli("verify", "--project", self.project, "--version", "v001")

    def test_export_collision_after_preflight_preserves_existing_file(self):
        target = self.root / "shared-download.zip"
        verify = project_helper.verified_manifest

        def another_export_finishes_during_verification(*args):
            result = verify(*args)
            target.write_bytes(b"Another completed download")
            return result

        with patch.object(project_helper, "verified_manifest", side_effect=another_export_finishes_during_verification):
            with self.assertRaises(FileExistsError):
                project_helper.export(Namespace(project=str(self.project), version="v001", output=str(target)))
        self.assertEqual(target.read_bytes(), b"Another completed download")

    def test_asset_symlink_cannot_enter_exported_payload(self):
        target = self.project / "assets/art/star.svg"
        target.unlink()
        outside = self.root / "outside.svg"
        outside.write_text("private outside contents")
        target.symlink_to(outside)
        self.run_cli("configure", "--project", self.project, success=False)
        self.run_cli("snapshot", "--project", self.project, "--note", "Unsafe source", success=False)

    def test_configure_preflight_failure_preserves_both_working_files(self):
        before = [(self.project / f).read_bytes() for f in ("index.html", "game.json")]
        (self.project / "index.html.opengame-tmp").write_text("occupied")
        self.run_cli("configure", "--project", self.project, "--collectible", "gem", success=False)
        self.assertEqual(before, [(self.project / f).read_bytes() for f in ("index.html", "game.json")])

    def test_interrupted_configure_recovers_without_losing_code_edits(self):
        replace = project_helper.os.replace

        def fail_html_replace(source, destination):
            if Path(destination).name == "index.html":
                raise OSError("injected interruption")
            return replace(source, destination)

        with patch.object(project_helper.os, "replace", side_effect=fail_html_replace):
            with self.assertRaises(OSError):
                project_helper.configure(Namespace(project=str(self.project), config=None, collectible="gem"))
        marker = b"\n<!-- A host edit after interruption -->\n"
        html = self.project / "index.html"
        html.write_bytes(html.read_bytes() + marker)
        self.run_cli("snapshot", "--project", self.project, "--note", "Recovered gem revision")
        self.assertTrue(html.read_bytes().endswith(marker))
        self.assertEqual(json.loads((self.project / "game.json").read_text())["collectible"], "gem")
        self.run_cli("verify", "--project", self.project, "--version", "v002")
        self.assertFalse((self.project / ".opengame-config-journal.json").exists())

    def test_interrupted_metadata_update_recovers_all_version_history(self):
        replace = project_helper.os.replace
        pointer_writes = 0

        def fail_pointer_replace(source, destination):
            nonlocal pointer_writes
            if Path(destination).name == "project.json":
                pointer_writes += 1
                if pointer_writes == 2:
                    raise OSError("injected interruption after snapshot completion")
            return replace(source, destination)

        with patch.object(project_helper.os, "replace", side_effect=fail_pointer_replace):
            with self.assertRaises(OSError):
                project_helper.snapshot(Namespace(project=str(self.project), note="Saved before pointer interruption"))
        self.assertTrue((self.project / "versions/v002/manifest.json").is_file())
        self.run_cli("snapshot", "--project", self.project, "--note", "Continue safely")
        record = json.loads((self.project / "project.json").read_text())
        self.assertEqual([item["version"] for item in record["history"]], ["v001", "v002", "v003"])

    def test_starter_embeds_assets_without_external_runtime_dependencies(self):
        index = (self.project / "index.html").read_text()
        self.assertEqual(index.count("data:image/svg+xml;base64,"), 7)
        self.assertNotRegex(index, r'<(?:script|img|iframe|source|audio|video)\b[^>]*\bsrc=["\']https?://')
        self.assertNotRegex(index, r'<link\b[^>]*\bhref=["\']https?://')
        self.assertNotRegex(index, r'@import\s+(?:url\()?\s*["\']?https?://')
        self.assertNotRegex(index, r'\b(?:fetch|WebSocket|XMLHttpRequest|sendBeacon)\s*\(')
        self.assertNotIn("__OPENGAME_", index)

    def test_starter_has_removable_attribution_and_optional_resources(self):
        index = (self.project / "index.html").read_text()
        self.assertIn('class="made-with"', index)
        self.assertIn("Made with", index)
        links = [unescape(value) for value in re.findall(r'<a\s+href="([^"]+)"[^>]*>', index)]
        self.assertEqual(len(links), 2)
        expected_queries = {
            "https://opengame.app/": {"utm_source": ["opengame-skill"], "utm_medium": ["plugin"], "utm_campaign": ["offline-arcade"]},
            "https://opengame.app/showcase": {"utm_source": ["opengame-skill"], "utm_medium": ["plugin"], "utm_campaign": ["offline-arcade"]},
        }
        for link in links:
            parsed = urlparse(link)
            base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            self.assertIn(base, expected_queries)
            self.assertEqual(parse_qs(parsed.query), expected_queries[base])
            self.assertEqual(parsed.fragment, "")
        self.assertEqual(index.count('target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer"'), 2)

        readme = (self.project / "README.md").read_text()
        for url in (
            "https://opengame.app/?utm_source=opengame-skill&utm_medium=plugin&utm_campaign=offline-arcade",
            "https://opengame.app/showcase?utm_source=opengame-skill&utm_medium=plugin&utm_campaign=offline-arcade",
            "https://github.com/opengameapp/OpenGame-skills",
            "https://github.com/opengameapp/OpenGame-showcases",
        ):
            self.assertIn(url, readme)


class PluginPackaging(unittest.TestCase):
    def test_build_is_reproducible_and_contains_only_one_canonical_skill(self):
        with tempfile.TemporaryDirectory(prefix="opengame-package-test-") as temp:
            for name in ("a", "b"):
                result = subprocess.run([sys.executable, str(REPO / "scripts/build_plugin.py"), "--output", str(Path(temp) / name)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            a, b = [Path(temp) / n / "opengame.zip" for n in ("a", "b")]
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as archive:
                names = archive.namelist()
                self.assertEqual(len([n for n in names if n.endswith("SKILL.md")]), 1)
                self.assertNotIn("opengame/.mcp.json", names)
                self.assertNotIn("opengame/.app.json", names)
                self.assertIn("opengame/LICENSE", names)
                self.assertIn("opengame/skills/opengame-offline-arcade/references/opengame-resources.md", names)
                self.assertFalse(any("__pycache__" in n or ".env" in n for n in names))
                manifest = json.loads(archive.read("opengame/.codex-plugin/plugin.json"))
                self.assertEqual(manifest["name"], "opengame")
                self.assertEqual(manifest["version"], "1.0.0")
                self.assertEqual(manifest["interface"]["displayName"], "OpenGame AI Game Generator")
                self.assertEqual(manifest["interface"]["shortDescription"], "Create & edit 2D games with AI")
                skill_a, skill_b = [Path(temp) / n / "opengame-offline-arcade.skill" for n in ("a", "b")]
                self.assertEqual(skill_a.read_bytes(), skill_b.read_bytes())
                with zipfile.ZipFile(skill_a) as skill_archive:
                    skill_names = skill_archive.namelist()
                    self.assertIn("opengame-offline-arcade/SKILL.md", skill_names)
                    self.assertEqual(len(skill_names), 16)
                    for name in skill_names:
                        source = "opengame/LICENSE" if name.endswith("/LICENSE") else f"opengame/skills/{name}"
                        self.assertEqual(skill_archive.read(name), archive.read(source))


if __name__ == "__main__":
    unittest.main()
