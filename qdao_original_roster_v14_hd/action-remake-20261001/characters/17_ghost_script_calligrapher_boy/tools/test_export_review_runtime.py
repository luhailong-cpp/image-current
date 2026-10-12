"""Synthetic preflight regression checks; never calls export() or uses real art."""
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
import export_review_runtime as e


class ExportPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix=".export-test-", dir=Path(__file__).parent)
        cls.base = Path(cls.temp.name)
        (cls.base / "preview").mkdir()
        (cls.base / "staging").mkdir()
        image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((400, 400, 600, 600), fill=(60, 80, 100, 255))
        out = io.BytesIO()
        image.save(out, format="PNG")
        cls.good_png = out.getvalue()
        rows = []
        for slot, (action, direction, n, ms) in e.EXPECTED.items():
            file = cls.base / "staging" / (slot + "-v1.png")
            file.write_bytes(cls.good_png)
            record = {
                "sha256": e.sha(cls.good_png), "width": 1024, "height": 1024,
                "configSnapshot": {"model": "synthetic-test", "quality": "synthetic-test"},
                "submittedParameters": {"model": None, "quality": None},
                "actualModel": None, "actualQuality": None,
                "generatedAt": "synthetic-test", "generatedAtEvidence": "synthetic-test",
                "tool": "synthetic-test", "route": "synthetic-test", "evidence": {},
            }
            file.with_suffix(".png.generation.json").write_bytes(e.json_bytes(record))
            rows.append({
                "slot": slot, "action": action, "direction": direction, "frame": n,
                "duration_ms": ms,
                "selected": {"slot": slot, "action": action, "direction": direction, "frame": n,
                             "path": "../staging/" + file.name, "sha256": e.sha(cls.good_png),
                             "record_path": "../staging/" + file.name + ".generation.json"},
            })
        cls.preview = {"character": e.CHARACTER, "slots": rows}
        cls.preview_path = cls.base / "preview" / "manifest-preview.json"
        cls.preview_raw = e.json_bytes(cls.preview)
        cls.preview_path.write_bytes(cls.preview_raw)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def assert_no_package(self):
        self.assertFalse((self.base / "runtime").exists())
        self.assertFalse((self.base / "manifest.json").exists())

    def test_complete_candidate_preserves_unknown_actual_parameters(self):
        plan = e.preflight(self.base)
        self.assertEqual((len(plan.frames), plan.status), (196, "candidate"))
        self.assertIsNone(plan.frames[0].record["actualModel"])
        self.assert_no_package()

    def test_missing_slot_fails_without_output(self):
        bad = dict(self.preview, slots=self.preview["slots"][:-1])
        self.preview_path.write_bytes(e.json_bytes(bad))
        try:
            with self.assertRaisesRegex(e.ExportError, "196 slots"):
                e.preflight(self.base)
            self.assert_no_package()
        finally:
            self.preview_path.write_bytes(self.preview_raw)

    def test_last_frame_generation_sha_mismatch_fails_without_output(self):
        last = self.preview["slots"][-1]["selected"]["record_path"]
        path = (self.preview_path.parent / last).resolve()
        original = path.read_bytes()
        data = json.loads(original)
        data["sha256"] = "0" * 64
        path.write_bytes(e.json_bytes(data))
        try:
            with self.assertRaisesRegex(e.ExportError, "generation SHA mismatch"):
                e.preflight(self.base)
            self.assert_no_package()
        finally:
            path.write_bytes(original)

    def test_edge_check_is_not_alpha_cleanup(self):
        image = Image.open(io.BytesIO(self.good_png)).copy()
        image.putpixel((0, 500), (10, 20, 30, 129))
        out = io.BytesIO()
        image.save(out, format="PNG")
        with self.assertRaisesRegex(e.ExportError, "touch canvas edge"):
            e.inspect_png(out.getvalue(), "synthetic edge")
        self.assertEqual(image.getpixel((0, 500))[3], 129)
        self.assert_no_package()

    def test_pass_requires_exact_preview_hash_and_explicit_reviews(self):
        path = self.base / "acceptance.json"
        acceptance = {"status": "passed", "previewManifestSha256": "0" * 64,
                      "visualApproval": "passed", "dynamicApproval": "passed",
                      "reviewedAt": "synthetic-test"}
        path.write_bytes(e.json_bytes(acceptance))
        try:
            with self.assertRaisesRegex(e.ExportError, "not bound"):
                e.preflight(self.base)
            acceptance["previewManifestSha256"] = e.sha(self.preview_raw)
            path.write_bytes(e.json_bytes(acceptance))
            self.assertEqual(e.preflight(self.base).status, "passed")
            acceptance["dynamicApproval"] = "pending"
            path.write_bytes(e.json_bytes(acceptance))
            with self.assertRaisesRegex(e.ExportError, "visual/dynamic"):
                e.preflight(self.base)
            self.assert_no_package()
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()

