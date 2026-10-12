"""Targeted boundary checks for the historical-style exception; no art changes."""
import importlib.util
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ZONE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("assembly", ZONE / "assemble.py")
assembly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembly)


class HistoricalReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="historical-ref-test-", dir=ZONE / "qa")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.retired = self.root / "retired-style.png"
        self.contract = {"previousPrimaryStyleReference": str(self.retired)}
        self.ref = {"file": str(self.retired), "sha256": "a" * 64, "role": "style"}

    def test_only_exact_missing_retired_path_keeps_unverified_hash(self):
        result = assembly.reference_evidence(self.ref, self.root, self.contract)
        self.assertFalse(result["referencePresent"])
        self.assertTrue(result["unverifiedHistoricalSource"])
        self.assertEqual(result["sha256"], self.ref["sha256"])

    def test_other_missing_reference_refused(self):
        ref = {**self.ref, "file": str(self.root / "different.png")}
        with self.assertRaisesRegex(ValueError, "Missing evidence"):
            assembly.reference_evidence(ref, self.root, self.contract)

    def test_missing_retired_without_contract_refused(self):
        with self.assertRaisesRegex(ValueError, "Missing evidence"):
            assembly.reference_evidence(self.ref, self.root, {})

    def test_retired_path_directory_is_not_missing_file_exception(self):
        self.retired.mkdir()
        with self.assertRaisesRegex(ValueError, "Missing evidence"):
            assembly.reference_evidence(self.ref, self.root, self.contract)

    def test_restored_retired_bytes_still_must_hash_match(self):
        self.retired.write_bytes(b"changed bytes")
        with self.assertRaisesRegex(ValueError, "Reference hash changed"):
            assembly.reference_evidence(self.ref, self.root, self.contract)

    def test_present_valid_reference_is_currently_verified(self):
        self.retired.write_bytes(b"known bytes")
        ref = {**self.ref, "sha256": assembly.sha(self.retired)}
        result = assembly.reference_evidence(ref, self.root, self.contract)
        self.assertTrue(result["referencePresent"])
        self.assertFalse(result["unverifiedHistoricalSource"])

    def test_missing_retired_with_invalid_recorded_hash_refused(self):
        ref = {**self.ref, "sha256": "unknown"}
        with self.assertRaisesRegex(ValueError, "Invalid recorded reference SHA-256"):
            assembly.reference_evidence(ref, self.root, self.contract)


class RealNativeGuardTests(unittest.TestCase):
    """Inject bad records in memory; production records and image bytes stay untouched."""
    def setUp(self):
        self.tile, plan = assembly.load_plan("r05_c13")
        self.item = next(p for p in plan["patches"] if p["id"] == "p41")
        self.sidecar = self.tile / "native" / "p41.png.generation.json"
        self.record = assembly.read_json(self.sidecar)
        self.before = assembly.sha(self.sidecar)

    def tearDown(self):
        self.assertEqual(self.before, assembly.sha(self.sidecar))

    def reject_modified_record(self, key, value, expected):
        read = assembly.read_json
        altered = {**copy.deepcopy(self.record), key: value}
        def injected(path):
            return altered if Path(path) == self.sidecar else read(path)
        with patch.object(assembly, "read_json", side_effect=injected):
            with self.assertRaisesRegex((ValueError, OSError), expected):
                assembly.inspect_source(self.tile, self.item)

    def test_native_hash_still_strict(self):
        self.reject_modified_record("sha256", "0" * 64, "Native SHA-256 differs")

    def test_native_dimensions_still_strict(self):
        self.reject_modified_record("nativeSize", [1024, 1024], "Recorded native dimensions")

    def test_coordinates_still_strict(self):
        changed = copy.deepcopy(self.item)
        changed["coreWorldBox"][0] += 1
        self.reject_modified_record("coordinates", changed, "Source coordinates differ")

    def test_missing_prompt_still_strict(self):
        self.reject_modified_record("prompt", str(self.tile / "missing.prompt"), "")

    def test_missing_request_still_strict(self):
        self.reject_modified_record("request", str(self.tile / "missing.request"), "")

    def test_missing_receipt_still_strict(self):
        self.reject_modified_record("evidence", str(self.tile / "missing.receipt"), "")

    def test_request_prompt_mismatch_still_strict(self):
        read = assembly.read_json
        def injected(path):
            obj = read(path)
            return {**obj, "prompt": "changed prompt"} if Path(path) == Path(self.record["request"]) else obj
        with patch.object(assembly, "read_json", side_effect=injected):
            with self.assertRaisesRegex(ValueError, "Saved prompt and actual request prompt differ"):
                assembly.inspect_source(self.tile, self.item)

    def test_invalid_receipt_still_strict(self):
        read = assembly.read_json
        def injected(path):
            if Path(path) == Path(self.record["evidence"]):
                raise json.JSONDecodeError("injected malformed receipt", "{", 1)
            return read(path)
        with patch.object(assembly, "read_json", side_effect=injected):
            with self.assertRaises(json.JSONDecodeError):
                assembly.inspect_source(self.tile, self.item)


if __name__ == "__main__":
    unittest.main(verbosity=2)
