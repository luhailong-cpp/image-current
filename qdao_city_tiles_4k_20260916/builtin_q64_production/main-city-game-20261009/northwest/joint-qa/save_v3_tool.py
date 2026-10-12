from pathlib import Path
import json, hashlib, copy
z=Path(__file__).resolve().parents[1]
s=(z/"assemble_2x2.py").read_text(encoding="utf-8")
s=s.replace("assemble_2x2.py --", "assemble_2x2_v3.py --")
s=s.replace('other seams keep minimum-error selection. Horizontal overrides are not supported.',
'''other seams keep minimum-error selection. Horizontal overrides can explicitly
replace only one core-column span of a global row path with the fixed center.
Each resulting RGB pixel is still copied unchanged from a native source.''')
start=s.index('def validate_override_specs(')
end=s.index('\n\ndef load_seam_overrides(',start)
s=s[:start]+'''def validate_override_specs(entries, grid=GRID, core=CORE, halo=HALO):
    """Validate explicit zero-based cuts; horizontal scope is exactly one core."""
    if not isinstance(entries, list):
        raise ValueError("overrides must be an array")
    normalized, seen, seen_ids = [], set(), set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or entry.get("axis") not in ("vertical", "horizontal"):
            raise ValueError("Only vertical or local horizontal overrides are supported")
        axis = entry["axis"]
        if axis == "vertical":
            row, column = entry.get("row"), entry.get("leftColumn")
            valid = type(row) is int and type(column) is int and 0 <= row < grid and 0 <= column < grid - 1
            adjacent_key, adjacent_value = "rightColumn", column + 1 if type(column) is int else None
            hash_keys = {"left", "right"}
        else:
            row, column = entry.get("topRow"), entry.get("column")
            valid = type(row) is int and type(column) is int and 0 <= row < grid - 1 and 0 <= column < grid
            adjacent_key, adjacent_value = "bottomRow", row + 1 if type(row) is int else None
            hash_keys = {"top", "bottom"}
        if not valid:
            raise ValueError("Override coordinates must be zero-based integers inside the joint grid")
        if adjacent_key in entry and (type(entry[adjacent_key]) is not int or entry[adjacent_key] != adjacent_value):
            raise ValueError("Adjacent coordinate must be exactly one greater")
        if entry.get("mode") != "core-center":
            raise ValueError("Only the fixed core-center override mode is supported")
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            raise ValueError("Every override needs a nonempty reason")
        identifier = entry.get("id", f"{axis}-r{row}-c{column}")
        key = (axis, row, column)
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen_ids or key in seen:
            raise ValueError("Override IDs and coordinates must be unique")
        expected = entry.get("expectedSourceSha256")
        if not isinstance(expected, dict) or set(expected) != hash_keys:
            raise ValueError(f"Bind each {axis} override to expectedSourceSha256 {sorted(hash_keys)}")
        if any(not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v) for v in expected.values()):
            raise ValueError("Expected source hashes must be lowercase SHA-256 strings")
        item = {**entry, "id": identifier, "configurationEntryIndex": index, adjacent_key: adjacent_value}
        if axis == "vertical":
            world_x = WORLD_BOX[0] + (column + 1) * core
            if "worldSeamX" in entry and (type(entry["worldSeamX"]) is not int or entry["worldSeamX"] != world_x):
                raise ValueError("worldSeamX disagrees with override geometry")
            if "overlapCutX" in entry and (type(entry["overlapCutX"]) is not int or entry["overlapCutX"] != halo):
                raise ValueError("Only the exact core-center cut is permitted")
            item.update({"overlapCutX": halo, "worldSeamX": world_x,
                         "worldFullNativeYRange": [WORLD_BOX[1] + row * core - halo, WORLD_BOX[1] + (row + 1) * core + halo],
                         "worldCoreYRange": [WORLD_BOX[1] + row * core, WORLD_BOX[1] + (row + 1) * core],
                         "leftNativeExclusiveStopX": core + halo, "rightNativeInclusiveStartX": halo,
                         "rowStripPathLength": core + 2 * halo,
                         "scope": "full native row strip before row joins"})
        else:
            joint_range = [column * core, (column + 1) * core]
            world_y = WORLD_BOX[1] + (row + 1) * core
            checks = {"worldSeamY": world_y, "jointSeamY": (row + 1) * core,
                      "overlapCutY": halo, "jointXHalfOpen": joint_range}
            for field, value in checks.items():
                if field in entry and (entry[field] != value or isinstance(entry[field], bool)):
                    raise ValueError(f"{field} disagrees with the local core-center geometry")
            item.update({**checks,
                         "worldXHalfOpen": [WORLD_BOX[0] + x for x in joint_range],
                         "extendedRowPathIndexHalfOpen": [halo + x for x in joint_range],
                         "horizontalOverlapJointYHalfOpen": [(row + 1) * core - halo, (row + 1) * core + halo],
                         "topNativeExclusiveStopY": core + halo, "bottomNativeInclusiveStartY": halo,
                         "scope": "only the specified half-open core-column span of the global horizontal row path; all other x retain the original minimum-error path"})
        seen.add(key); seen_ids.add(identifier)
        normalized.append(item)
    return normalized
''' + s[end:]
start=s.index('        for side, column in (("left", entry["leftColumn"])')
end=s.index('            if source is None:',start)
s=s[:start]+'''        positions = (("left", entry["row"], entry["leftColumn"]), ("right", entry["row"], entry["rightColumn"])) if entry["axis"] == "vertical" else (("top", entry["topRow"], entry["column"]), ("bottom", entry["bottomRow"], entry["column"]))
        for side, row, column in positions:
            source = by_position.get((row, column))
''' + s[end:]
s=s.replace('override_map = {(entry["row"], entry["leftColumn"]): entry for entry in override_list}',
'''override_map = {(entry["row"], entry["leftColumn"]): entry for entry in override_list if entry["axis"] == "vertical"}
    horizontal_map = {}
    for entry in override_list:
        if entry["axis"] == "horizontal":
            horizontal_map.setdefault(entry["topRow"], []).append(entry)''')
old='''        combined, seam = native.append_with_minimum_seam(combined, strips[row].transpose(1, 0, 2), overlap)
        ownership = append_labels(ownership, label_strips[row].T, seam, overlap)
        paths.append({"axis": "y", "nextPatchRow": row + 1, "overlapPath": seam.tolist(), "policy": "minimum-error"})'''
new='''        incoming = strips[row].transpose(1, 0, 2)
        minimum_pixels, seam = native.append_with_minimum_seam(combined, incoming, overlap)
        local_overrides = horizontal_map.get(row - 1, [])
        if local_overrides:
            original_seam = seam.copy()
            for entry in local_overrides:
                begin, end = entry["extendedRowPathIndexHalfOpen"]
                seam[begin:end] = halo
            combined = append_with_recorded_seam(combined, incoming, seam, overlap)
            metadata = {"policy": "minimum-error-with-explicit-local-core-center-overrides",
                        "localOverrides": local_overrides,
                        "minimumErrorPathBeforeLocalOverrides": original_seam.tolist(),
                        "modifiedPathIndices": [entry["extendedRowPathIndexHalfOpen"] for entry in local_overrides]}
        else:
            combined = minimum_pixels
            metadata = {"policy": "minimum-error"}
        ownership = append_labels(ownership, label_strips[row].T, seam, overlap)
        paths.append({"axis": "y", "nextPatchRow": row + 1, "overlapPath": seam.tolist(), **metadata})'''
assert old in s
s=s.replace(old,new)
s=s.replace('"method": "joint-8x8-minimum-error",','"method": "joint-8x8-minimum-error-with-explicit-local-core-cuts-v3",')
s=s.replace('minimum-error binary source cuts except explicitly recorded fixed core-center vertical overrides; complete rows then all rows',
            'minimum-error binary source cuts except explicitly recorded fixed core-center vertical and local horizontal overrides; complete rows then all rows')
anchor='''    # A deliberate pixel change must be detected independently of cut construction.'''
insert='''    horizontal = {"id": "self-check-horizontal-local", "axis": "horizontal", "topRow": 6, "column": 5,
                  "mode": "core-center", "reason": "local row path range and native pixel test",
                  "expectedSourceSha256": {"top": "2" * 64, "bottom": "3" * 64}}
    local_pixels, local_owners, local_paths = assemble_grid(arrays, grid, core, halo, overrides=[spec, horizontal])
    local_checked = verify_exact_pixels(local_pixels, local_owners, arrays, grid, core, halo)
    assert np.array_equal(replay_recorded_paths(arrays, local_paths, grid, core, halo), local_pixels)
    left, right = 5 * core + halo, 6 * core + halo
    for baseline, changed in zip(hard_paths, local_paths):
        if changed["axis"] != "y" or changed["nextPatchRow"] != 8:
            assert baseline == changed
        else:
            before, after = np.asarray(baseline["overlapPath"]), np.asarray(changed["overlapPath"])
            assert np.array_equal(before[:left], after[:left])
            assert np.array_equal(before[right:], after[right:])
            assert np.all(after[left:right] == halo)
            assert changed["modifiedPathIndices"] == [[left, right]]
            assert changed["minimumErrorPathBeforeLocalOverrides"] == baseline["overlapPath"]
    untouched = np.ones((grid * core, grid * core), bool)
    untouched[7 * core - halo:7 * core + halo, 5 * core:6 * core] = False
    assert np.array_equal(hard_pixels[untouched], local_pixels[untouched])
    assert np.array_equal(hard_owners[untouched], local_owners[untouched])
    assert np.all(local_owners[7 * core - 1, 5 * core:6 * core - halo] == 54)
    assert np.all(local_owners[7 * core, 5 * core:6 * core - halo] == 62)
    for change in [{"topRow": -1}, {"topRow": 7}, {"column": 8}, {"column": True},
                   {"bottomRow": 6}, {"overlapCutY": 2}, {"jointXHalfOpen": [0, 12]},
                   {"worldSeamY": 0}, {"expectedSourceSha256": {"left": "0" * 64, "right": "1" * 64}}]:
        try:
            validate_override_specs([{**horizontal, **change}], grid, core, halo)
        except ValueError:
            invalid_count += 1
        else:
            raise AssertionError("Invalid local horizontal override was accepted")
    try:
        validate_override_specs([horizontal, horizontal], grid, core, halo)
    except ValueError:
        invalid_count += 1
    else:
        raise AssertionError("Duplicate local horizontal override was accepted")
'''
assert anchor in s
s=s.replace(anchor,insert+anchor)
s=s.replace('"onlyConfiguredVerticalCutChanged": True, "invalidOverrideCasesRejected": invalid_count,',
'''"onlyConfiguredVerticalCutChanged": True,
            "localHorizontalPixelsVerified": local_checked["pixelsVerified"],
            "localHorizontalReplayPixelIdentical": True,
            "localHorizontalOutsideScopeRGBAndOwnersUnchanged": True,
            "localHorizontalOnlyConfiguredPathIndicesChanged": True,
            "invalidOverrideCasesRejected": invalid_count,''')
target=z/"assemble_2x2_v3.py"
assert not target.exists()
target.write_text(s,encoding="utf-8")

def ref(p):
    p=z/p
    return {"file":str(p.relative_to(z)).replace("\\\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((z/"joint-qa/joint-review-cuts-v2.json").read_text(encoding="utf-8-sig"))
cfg=copy.deepcopy(old)
cfg["description"]="V3 native binary cuts: preserve the two reviewed V2 vertical core-center cuts, add row6/left5 vertical center and a strictly local topRow6/column5 horizontal center. Local review evidence predates the unrelated s02_01 material change, which requires new whole-joint delta QA. All output pixels remain exact native source pixels."
cfg["supersedesForThisAssemblyOnly"]=ref(Path("joint-qa/joint-review-cuts-v2.json"))
sel=json.loads((z/"r06_c05/selection.json").read_text(encoding="utf-8-sig"))
hashes={k:sha(Path(v)) for k,v in sel.items()}
ev=Path("joint-qa/row6-left5-center-exploration")
for e in cfg["overrides"]:
    e["reason"]=e["reason"].replace("keep all horizontal and all other vertical joins at minimum-error.", "Other explicitly configured V3 exceptions are recorded separately.")
cfg["overrides"].append({
 "id":"joint-review-v3-r6-c5","axis":"vertical","row":6,"leftColumn":5,"rightColumn":6,
 "mode":"core-center","worldSeamX":18432,
 "reason":"Previously reviewed native row6 left5 core-center cut removes the broken junction near joint (6144,6144). It is paired with the separately recorded local horizontal cut at joint Y7168.",
 "expectedSourceSha256":{"left":hashes["s03_02"],"right":hashes["s03_03"]},
 "evidence":[ref(ev/"mechanical-evidence.json"),ref(ev/"row6-left5-center-junction-x6144-y6144.png"),ref(ev/"row6-left5-center-vertical-row6.png")]
})
cfg["overrides"].append({
 "id":"joint-review-v3-horizontal-r6-c5","axis":"horizontal","topRow":6,"bottomRow":7,"column":5,
 "mode":"core-center","worldSeamY":23552,"jointSeamY":7168,"jointXHalfOpen":[5120,6144],"overlapCutY":115,
 "reason":"The reviewed fixed core-center horizontal selection removes the remaining broken paving endpoint at junction (6144,7168). It affects only joint X [5120,6144) inside the Y7168 overlap; both 320px endpoint junction views were reviewed. The independently optimized pair cut was rejected and is not used.",
 "expectedSourceSha256":{"top":hashes["s03_02"],"bottom":hashes["s04_02"]},
 "evidence":[ref(ev/"horizontal-local/mechanical-evidence.json"),ref(ev/"horizontal-local/local-core-center-junction-x5120-y7168.png"),ref(ev/"horizontal-local/local-core-center-junction-x6144-y7168.png"),ref(ev/"horizontal-local/local-core-center-strip-x4960-6304-y7168.png")]
})
p=z/"joint-qa/joint-review-cuts-v3.json"
assert not p.exists()
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"script":str(target),"sha256":sha(target),"configuration":str(p),"configurationSha256":sha(p)},indent=2))

