"""In-memory safety tests. Does not scan assets, generate plans, or delete files."""
import importlib.util
from pathlib import Path
import stat
import types
import unittest
from unittest.mock import patch
from PIL import Image

path=Path(__file__).with_name("cleanup_generation.py")
spec=importlib.util.spec_from_file_location("cleanup_under_test",path)
cleanup=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


class CleanupSafetyTests(unittest.TestCase):
    def test_expected_scope_is_14_groups_196_slots(self):
        self.assertEqual(len(cleanup.GROUPS),14)
        self.assertEqual(sum(n for _,_,n in cleanup.GROUPS),196)

    def test_fingerprint_order_and_content(self):
        self.assertEqual(cleanup.fingerprint({"b":2,"a":1}),cleanup.fingerprint({"a":1,"b":2}))
        self.assertNotEqual(cleanup.fingerprint({"a":1}),cleanup.fingerprint({"a":2}))

    def test_slots_reject_duplicate_and_missing(self):
        with self.assertRaises(ValueError):
            cleanup.slots({"frames":[{"slot":1},{"slot":1}]},2)
        with self.assertRaises(ValueError):
            cleanup.slots({"frames":[{"slot":1},{"slot":3}]},2)
        self.assertEqual(sorted(cleanup.slots({"frames":[{"slot":2},{"frame":1}]},2)),[1,2])

    def test_outside_and_nonpng_refused_before_filesystem_access(self):
        with patch.object(cleanup,"regular") as regular:
            for target in [cleanup.BASE/"generation"/"../outside.png",
                           cleanup.BASE.parent/"other"/"generation"/"a.png",
                           cleanup.BASE/"generation"/"a.png.generation.json",
                           cleanup.BASE/"generation"]:
                with self.assertRaises(ValueError):
                    cleanup.deletion_path(target)
            regular.assert_not_called()

    def test_windows_alternate_stream_refused(self):
        with patch.object(cleanup,"regular") as regular:
            with self.assertRaises(ValueError):
                cleanup.deletion_path(cleanup.BASE/"generation"/"a.png:evil.png")
            regular.assert_not_called()

    def test_symlink_and_reparse_refused(self):
        for mode,attrs in [(stat.S_IFLNK,0),(stat.S_IFDIR,cleanup.REPARSE_POINT)]:
            info=types.SimpleNamespace(st_mode=mode,st_file_attributes=attrs)
            with patch.object(cleanup.os.path,"lexists",return_value=True), patch.object(Path,"lstat",return_value=info):
                with self.assertRaises(ValueError):
                    cleanup.no_links(cleanup.BASE/"generation"/"a.png")

    def test_hardlink_refused(self):
        with patch.object(cleanup,"regular"), patch.object(Path,"stat",return_value=types.SimpleNamespace(st_nlink=2)):
            with self.assertRaises(ValueError):
                cleanup.deletion_path(cleanup.BASE/"generation"/"a.png")

    def test_stale_or_edited_plan_cannot_reach_deletion(self):
        saved={"schemaVersion":1,"base":cleanup.BASE.as_posix(),"mode":"unselected",
               "stateFingerprint":"old","delete":[{"path":"evil"}],"keep":[],
               "selected":[],"requiredFiles":[],"controls":[]}
        fresh=dict(saved,stateFingerprint="new")
        with patch.object(cleanup,"read",return_value=saved), patch.object(cleanup,"regular",side_effect=lambda p:p), \
             patch.object(cleanup,"build_plan",return_value=(fresh,[])),patch.object(cleanup,"deletion_path") as delete:
            with self.assertRaises(ValueError):
                cleanup.apply_plan(Path("plan.json"),Path("freeze.json"))
            delete.assert_not_called()
        # Same fingerprint but a manually altered target list is also refused.
        fresh=dict(saved,delete=[])
        with patch.object(cleanup,"read",return_value=saved),patch.object(cleanup,"regular",side_effect=lambda p:p), \
             patch.object(cleanup,"build_plan",return_value=(fresh,[])),patch.object(cleanup,"deletion_path") as delete:
            with self.assertRaises(ValueError):
                cleanup.apply_plan(Path("plan.json"),Path("freeze.json"))
            delete.assert_not_called()

    def test_all_sources_without_valid_freeze_refused(self):
        saved={"schemaVersion":1,"base":cleanup.BASE.as_posix(),"mode":"all-sources",
               "stateFingerprint":"same","delete":[],"keep":[],"selected":[],"requiredFiles":[],"controls":[]}
        with patch.object(cleanup,"read",return_value=saved),patch.object(cleanup,"regular",side_effect=lambda p:p), \
             patch.object(cleanup,"build_plan",return_value=(saved,[])), \
             patch.object(cleanup,"verify_frozen",side_effect=ValueError("missing freeze")), \
             patch.object(cleanup,"deletion_path") as delete:
            with self.assertRaises(ValueError):
                cleanup.apply_plan(Path("plan.json"),Path("freeze.json"))
            delete.assert_not_called()

    def test_export_pixel_mismatch_rejected_even_with_matching_declared_hashes(self):
        native=Image.new("RGBA",(1254,1254),(0,0,0,0))
        native.putpixel((600,600),(255,20,30,255))
        export=native.resize((1024,1024),Image.Resampling.LANCZOS)
        bad=export.copy()
        bad.putpixel((20,20),(255,100,10,255))
        def opened(p):
            result=(native if str(p)=="source" else export).copy()
            result.format="PNG"
            return result
        with patch.object(cleanup,"sha",side_effect=lambda p:"sourcehash" if str(p)=="source" else "exporthash"), \
             patch.object(cleanup.Image,"open",side_effect=opened):
            cleanup.pair_check("source","export","sourcehash","exporthash")
            export=bad
            with self.assertRaises(ValueError):
                cleanup.pair_check("source","export","sourcehash","exporthash")


if __name__=="__main__":
    unittest.main()

