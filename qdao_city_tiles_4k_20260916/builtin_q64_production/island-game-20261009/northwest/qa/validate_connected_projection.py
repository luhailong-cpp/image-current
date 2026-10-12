"""Small in-memory provenance fixtures; never assembles or modifies game art."""
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
import json
import sys
import tempfile
from unittest.mock import patch

import numpy as np

ZONE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ZONE))
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair


def main():
    checks = []

    def rejected(name, action):
        try:
            action()
        except (ValueError, OSError, KeyError, TypeError) as error:
            checks.append({"name": name, "result": "rejected", "reason": str(error)})
            return
        raise AssertionError("Unexpected acceptance: " + name)

    with tempfile.TemporaryDirectory(prefix="connected_projection_fixture_") as temporary, ExitStack() as stack:
        directory = Path(temporary).resolve()
        stack.enter_context(patch.multiple(connected, CORE=8, HALO=2, PADDED=12, OVERLAP=4, CLUSTER=16, PADDED_CLUSTER=20, ZONE=directory))
        stack.enter_context(patch.multiple(repair, TILE=8, ZONE=directory))
        stack.enter_context(patch.object(connected.assembly, "OVERLAP", 4))
        # Coordinate/color arrays are test data only; no PNG or game output is saved.
        rng = np.random.default_rng(7421)
        arrays = [rng.integers(0, 256, (12, 12, 3), dtype=np.uint8) for _ in range(4)]
        pixels, labels, joins = connected.compose(arrays)
        for index in range(4):
            x0,y0,x1,y1 = connected.projection_box(index)
            local = labels[y0:y1,x0:x1]
            assert np.array_equal(connected.projection_labels(joins, index), local)
            connected.verify_projection_pixels(pixels[y0:y1,x0:x1], local, arrays, index)
        checks.append({"name": "four_projection_path_and_coordinate_replays", "result": "pass"})

        def save(name, value):
            path = directory / name
            path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
            return repair.file_info(path)

        sources, matrix, outputs, decoded = [], [[], []], [], {}
        for index in range(4):
            row,col = divmod(index,2)
            tile_id = f"r{row+1:02d}_c{col+1:02d}"
            source_image = save(f"input{index}.bytes", {"imageFixture": index})
            source_record = save(f"input{index}.json", {"output": source_image})
            root = save(f"root{index}.json", {"rootFixture": index})
            halo = save(f"halo{index}.bytes", {"haloFixture": index})
            proof = {"tileId": tile_id, "tileOrigin": [col*8,row*8], "rootAssembly": root,
                     "rootProvenance": halo, "originalRawSourceCount":16, "priorRepairCount":0}
            source = {"tileId":tile_id, "tileOrigin":[col*8,row*8], "sourceId":index,
                      "image":source_image, "record":source_record, "rootAssembly":root,
                      "rootPaddedProvenance":halo, "coreValidation":proof,
                      "originalPaddedCounts":[{"sourceId":0,"pixelCount":144}]}
            sources.append(source)
            matrix[row].append({"image":source_image,"record":source_record})
            output = save(f"output{index}.bytes", {"outputFixture":index})
            box = connected.projection_box(index)
            outputs.append({"tileId":tile_id,"clusterCropBox":box,"output":output})
            decoded[Path(output["path"])] = pixels[box[1]:box[3],box[0]:box[2]].copy()
        manifest = {"schemaVersion":1,"tileMatrix":matrix}
        manifest_info = save("manifest.json",manifest)
        plane_path = directory / "ownership.npz"
        np.savez_compressed(plane_path, source_tile_id=labels)
        cluster = {"schemaVersion":1,"operation":connected.OPERATION,"isAiGeneration":False,
                   "clusterDimensions":[16,16],"clusterOrigin":[0,0],"sources":sources,"outputs":outputs,
                   "manifest":manifest_info,"manifestSnapshot":manifest,"joins":joins,
                   "sourceIndexPlane":repair.file_info(plane_path),
                   "method":{k:False for k in ("registration","resizingFinalArt","feathering","colorCorrection","pixelSynthesis")}}
        cluster_path = directory / "cluster.json"
        projection_path = directory / "projection.json"
        seen_calls = []

        def reconstruct(image_path, record_path, seen=None):
            assert cluster_path in seen and projection_path in seen
            assert record_path not in seen
            seen_calls.append((record_path, set(seen)))
            index = next(i for i,s in enumerate(sources) if Path(s["image"]["path"]) == image_path)
            assert Path(sources[index]["record"]["path"]) == record_path
            return arrays[index], deepcopy(sources[index])

        stack.enter_context(patch.object(connected,"reconstruct_padded",reconstruct))
        stack.enter_context(patch.object(repair,"read_pixels",lambda path,size: decoded[path].copy()))

        def run(index=0, cluster_value=None, projection_change=None, seen=None):
            cluster_info = save("cluster.json", cluster if cluster_value is None else cluster_value)
            record = connected.make_projection_record(cluster_info,sources[index],outputs[index]["output"],index)
            if projection_change:
                projection_change(record)
            save("projection.json",record)
            return repair.validate_base(Path(outputs[index]["output"]["path"]),projection_path,seen)

        for index in range(4):
            result, proof = run(index)
            assert proof["fullNativeCoverage"] and proof["verifiedPixelCount"] == 64
            assert proof["originalRawSourceCount"] == 64 and len(proof["rootAssemblies"]) == 4
            assert proof["rootAssembly"] == sources[index]["rootAssembly"]
            assert np.array_equal(result, decoded[Path(outputs[index]["output"]["path"])])
        assert len(seen_calls) == 16
        checks.append({"name":"public_validate_base_dispatch_four_sources_and_acyclic_records","result":"pass"})

        run(0)
        chain = repair.verified_ancestor_chain(outputs[0]["output"],repair.file_info(projection_path),sources[0]["image"],sources[0]["record"])
        assert len(chain) == 2
        checks.append({"name":"projection_preserves_explicit_own_tile_ancestry","result":"pass"})

        output_path = Path(outputs[0]["output"]["path"])
        decoded[output_path][0,0,0] ^= np.uint8(1)
        rejected("changed_projected_pixel",run)
        decoded[output_path][0,0,0] ^= np.uint8(1)
        rejected("wrong_projection_crop",lambda:run(projection_change=lambda r:r.__setitem__("clusterCropBox",[1,0,9,8])))
        rejected("wrong_projection_predecessor",lambda:run(projection_change=lambda r:r.__setitem__("base",{"image":sources[1]["image"],"record":sources[1]["record"]})))
        rejected("wrong_projection_tile_id",lambda:run(projection_change=lambda r:r.__setitem__("tileId","r02_c02")))
        rejected("cyclic_projection",lambda:run(seen={projection_path}))
        rejected("cyclic_cluster",lambda:run(seen={cluster_path}))
        for name, edit in [
            ("out_of_range_seam",lambda c:c["joins"][0]["overlapPath"].__setitem__(0,4)),
            ("discontinuous_seam",lambda c:c["joins"][0]["overlapPath"].__setitem__(slice(0,2),[0,3])),
            ("wrong_seam_axis",lambda c:c["joins"][0].__setitem__("axis",0)),
            ("wrong_source_position",lambda c:c["sources"][1].__setitem__("tileOrigin",[0,0])),
            ("changed_root_hash",lambda c:c["sources"][0]["rootAssembly"].__setitem__("sha256","0"*64)),
            ("manifest_snapshot_drift",lambda c:c["manifestSnapshot"].__setitem__("extra",True)),
            ("source_outside_manifest",lambda c:c["sources"][0].__setitem__("image",deepcopy(sources[1]["image"]))),
        ]:
            value = deepcopy(cluster);edit(value)
            rejected(name,lambda value=value:run(cluster_value=value))
        changed_labels=labels.copy();changed_labels[0,0]=3
        np.savez_compressed(plane_path,source_tile_id=changed_labels)
        value=deepcopy(cluster);value["sourceIndexPlane"]=repair.file_info(plane_path)
        rejected("ownership_disagrees_with_seam_paths",lambda:run(cluster_value=value))
        changed_labels[0,0]=255
        np.savez_compressed(plane_path,source_tile_id=changed_labels)
        value["sourceIndexPlane"]=repair.file_info(plane_path)
        rejected("unassigned_ownership_value",lambda:run(cluster_value=value))
        bad=labels[:8,:8].copy();bad[0,0]=3
        rejected("source_footprint_violation",lambda:connected.verify_projection_pixels(pixels[:8,:8],bad,arrays,0))
    result={"status":"pass","checks":checks,"production2x2Assembled":False,"artFilesWritten":False,
            "fixtureLimit":"8x8 array projections; raw/halo validation boundary is mocked, public record/hash/path validation is real.",
            "tools":[repair.file_info(ZONE/'assemble_connected_tiles.py'),repair.file_info(ZONE/'apply_native_tile_repair.py')]}
    path=ZONE/'qa/connected_projection_validation.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({"status":"pass","checkCount":len(checks),"record":repair.file_info(path)}))


if __name__ == '__main__':
    main()
