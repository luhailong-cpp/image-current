"""Diagnostic hard seam across the native 230px shared tile overlap.

Rows 1-2 only; exports QA strips and exact paths, never game tiles.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
PREFIX = "preflight-shared-r09c04-c05-rows12-v1"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def save(name, array):
    path = QA / name
    assert path.name.startswith(PREFIX) and not path.exists()
    with path.open("xb") as handle:
        Image.fromarray(array).save(handle, format="PNG")
    assert np.array_equal(np.asarray(Image.open(path)), array)
    return {"path": path.as_posix(), "sha256": sha(path), "size": [array.shape[1], array.shape[0]]}


def write(name, data):
    path = QA / name
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def main():
    lp = QA / "repair-r09_c04-v1-trace.json"
    rp = QA / "preflight-r09_c05-rows12-v1-trace.json"
    left_record, right_record = read(lp), read(rp)
    refs = [left_record["context"], right_record["context"]]
    for ref in refs:
        assert sha(ref["path"]) == ref["sha256"]
    left = np.asarray(Image.open(refs[0]["path"]).convert("RGB"))[:2278]
    right = np.asarray(Image.open(refs[1]["path"]).convert("RGB"))
    assert left.shape == right.shape == (2278,4326,3)
    helper_ref = left_record["seamHelper"]
    assert sha(helper_ref["path"]) == helper_ref["sha256"]
    spec = importlib.util.spec_from_file_location("shared_edge_seam", helper_ref["path"])
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    a, b = left[:,4096:4326], right[:,:230]
    seam = helper._minimum_vertical_seam(a,b)
    mask = np.arange(230)[None,:] >= seam[:,None]
    overlap = np.where(mask[:,:,None],b,a)
    strip = np.concatenate([left[:,3866:4096], overlap, right[:,230:460]],axis=1)
    assert strip.shape == (2278,690,3)
    assert np.array_equal(overlap[mask],b[mask]) and np.array_equal(overlap[~mask],a[~mask])
    core_strip = strip[115:2163].copy()
    output = save(PREFIX+"-diagnostic-native.png",core_strip)
    mask_ref = save(PREFIX+"-overlap-source-mask-bw.png",mask.astype(np.uint8)*255)
    qa=[]
    for i,start in enumerate((0,700,1148),1):
        name=PREFIX+f"-part{i:02d}-100pct.png"
        ref=save(name,core_strip[start:start+900])
        record={**ref,"source":output,"sourceBox":[0,start,690,start+900],"operation":"integer crop only",
                "nominalCoreBoundaryX":345,"seamXByImageRow":(seam[115+start:115+start+900]+230).tolist(),
                "globalBox":[16039,32768+start,16729,32768+start+900]}
        write(name+".derivation.json",record)
        qa.append(record)
    trace={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),
        "status":"diagnostic_partial_shared_edge_pending_visual_review","notFullTile":True,
        "doesNotModifyEitherExport":True,"formalAcceptedCount":0,
        "sourceTraces":[{"path":lp.as_posix(),"sha256":sha(lp)},{"path":rp.as_posix(),"sha256":sha(rp)}],
        "sources":refs,"helper":helper_ref,"script":{"path":Path(__file__).as_posix(),"sha256":sha(__file__)},
        "globalOverlapBox":[16269,32653,16499,34931],"nominalWorldBoundaryX":16384,
        "seamXByContextRowInOverlap":seam.tolist(),"seamXByContextRowInWorld":(seam+16269).tolist(),
        "rightChosenAtOrRight":True,"sourceMask":{**mask_ref,"legend":{"0":"r09_c04 repaired context","255":"r09_c05 partial context"}},
        "output":output,"outputGlobalBox":[16039,32768,16729,34816],"qa":qa,
        "noResize":True,"noFeather":True,"noColourCorrection":True,"noDrawing":True,"allPixelsMatchOriginalSources":True}
    path=write(PREFIX+"-trace.json",trace)
    print(json.dumps({"trace":path.as_posix(),"qaCount":len(qa),"seamWorldXRange":[int(seam.min()+16269),int(seam.max()+16269)]}))


if __name__=="__main__":
    main()
