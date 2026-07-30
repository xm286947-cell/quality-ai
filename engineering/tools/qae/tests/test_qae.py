from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

QAE_SOURCE = Path(__file__).resolve().parents[1] / "qae.py"


class QAEIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "README.md").write_text("# QUALITY_AGENT\n", encoding="utf-8")
        qae_target = self.root / "engineering/tools/qae/qae.py"
        qae_target.parent.mkdir(parents=True)
        qae_target.write_bytes(QAE_SOURCE.read_bytes())
        self.qae = qae_target

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_qae(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.qae), *args], cwd=self.root,
            text=True, capture_output=True, check=False,
        )

    def make_package(self, name: str, content: str) -> Path:
        staging = self.root / f"stage_{name}"
        file_path = staging / "files/business_agent/demo.txt"
        file_path.parent.mkdir(parents=True)
        file_path.write_text(content, encoding="utf-8")
        manifest = {
            "package_name": name,
            "target_project": "quality-ai",
            "target_scope": "business_agent",
            "version": "1.0",
            "milestone": "M1",
            "files": ["business_agent/demo.txt"],
        }
        (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        package = self.root / f"{name}.zip"
        with zipfile.ZipFile(package, "w") as archive:
            archive.write(staging / "manifest.json", "manifest.json")
            archive.write(file_path, "files/business_agent/demo.txt")
        return package

    def test_install_verify_rollback_new_file(self) -> None:
        package = self.make_package("NEW_FILE", "new")
        self.assertEqual(self.run_qae("install", str(package)).returncode, 0)
        self.assertEqual((self.root / "business_agent/demo.txt").read_text(), "new")
        self.assertEqual(self.run_qae("verify").returncode, 0)
        self.assertEqual(self.run_qae("rollback").returncode, 0)
        self.assertFalse((self.root / "business_agent/demo.txt").exists())

    def test_install_and_restore_overwritten_file(self) -> None:
        target = self.root / "business_agent/demo.txt"
        target.parent.mkdir(parents=True)
        target.write_text("old", encoding="utf-8")
        package = self.make_package("OVERWRITE", "new")
        self.assertEqual(self.run_qae("install", str(package)).returncode, 0)
        self.assertEqual(target.read_text(), "new")
        self.assertEqual(self.run_qae("rollback").returncode, 0)
        self.assertEqual(target.read_text(), "old")

    def test_reject_path_traversal(self) -> None:
        package = self.root / "bad.zip"
        manifest = {
            "package_name": "BAD", "target_project": "quality-ai",
            "target_scope": "x", "version": "1", "milestone": "M1",
            "files": ["../escape.txt"],
        }
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest))
            archive.writestr("files/../escape.txt", "bad")
        self.assertNotEqual(self.run_qae("install", str(package)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
