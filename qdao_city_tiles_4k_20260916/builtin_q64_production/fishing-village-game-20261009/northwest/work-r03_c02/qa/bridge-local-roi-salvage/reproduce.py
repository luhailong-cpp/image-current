"""QA-only native-pixel local ROI salvage. No generation, warp, blend or color edit.

Run with bundled Python; outputs remain beside this file. v01 is immutable base,
v02 is the only inserted source. DP paths are restricted to the local roof region.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCES = [ROOT / "native/r03_c02_c03_roof_bridge_v01.png",
           ROOT / "native/r03_c02_c03_roof_bridge_v02.png"]
PINNED = ["4b7ce960681f7949a312932a736fc0b7ba37adda3e56a885fd6d82d7bf109532",
          "664c4d5f2b48e02b11e61ec128d1caf84f55ddbfec564aa0abcc6d66f00f8714"]
INF = np.int64(10**12)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def minimum_path(cost, low, high):
    """4-connected seam with per-row inclusive eligible x ranges; no RGB changes."""
    h, w = cost.shape
    positions = np.arange(w)
    allowed = (positions[None, :] >= low[:, None]) & (positions[None, :] <= high[:, None])
    c = np.where(allowed, cost, INF)
    prev = c[0].copy()
    back = np.zeros((h, w), dtype=np.int8)
    for y in range(1, h):
        options = np.stack((prev, np.r_[INF, prev[:-1]], np.r_[prev[1:], INF]))
        k = options.argmin(axis=0)
        prev = c[y] + options[k, positions]
        back[y] = np.array([0, -1, 1], dtype=np.int8)[k]
    path = np.empty(h, dtype=np.int32)
    path[-1] = prev.argmin()
    total = int(prev[path[-1]])
    assert total < INF, "No admissible connected path"
    for y in range(h - 1, 0, -1):
        path[y - 1] = path[y] + back[y, path[y]]
    assert np.all(path >= low) and np.all(path <= high)
    assert np.all(np.abs(np.diff(path)) <= 1)
    return path, total

def main():
    for path, pin in zip(SOURCES, PINNED):
        assert sha(path) == pin, str(path)
    a, b = [np.array(Image.open(p).convert("RGB")) for p in SOURCES]
    assert a.shape == b.shape == (1254, 1254, 3)
    cost = np.sum((a.astype(np.int64) - b.astype(np.int64))**2, axis=2)
    # Mandatory v02 selection covers the old narrow diagonal lane and replacement
    # cap. This is a QA constraint, not newly drawn art. Outer115px L/R stay v01.
    forced = np.zeros((1254, 1254), dtype=bool)
    for y in range(546):
        center = int(round(610 + 0.78*y))
        forced[y, center-55:center+56] = True
    forced[490:666, 940:1089] = True
    Image.fromarray(forced.astype(np.uint8)*255).save(HERE / "mandatory-v02-region.png")
    summary = []
    for variant in ("narrow-ribbon", "broad-neighborhood"):
        height = 831
        low_l = np.zeros(height, dtype=int)
        high_l = np.zeros(height, dtype=int)
        low_r = np.zeros(height, dtype=int)
        high_r = np.zeros(height, dtype=int)
        for y in range(height):
            center = int(round(610 + 0.78*min(y, 600)))
            xs = np.flatnonzero(forced[y])
            first = int(xs[0]) if len(xs) else 940
            last = int(xs[-1]) if len(xs) else 1088
            if variant == "narrow-ribbon":
                low_l[y] = max(300, min(first-10, center-230))
                high_l[y] = first-2
                low_r[y] = last+2
                high_r[y] = min(1138, max(last+10, center+230))
            else:
                low_l[y], high_l[y] = 300, first-2
                low_r[y], high_r[y] = last+2, 1138
        left, lc = minimum_path(cost[:height], low_l, high_l)
        right, rc = minimum_path(cost[:height], low_r, high_r)
        bottom, bc = minimum_path(cost[680:831].T,
                                  np.zeros(1254, dtype=int),
                                  np.full(1254, 150, dtype=int))
        bottom += 680
        yy, xx = np.indices((1254,1254))
        mask = np.zeros((1254,1254),dtype=bool)
        mask[:height] = (xx[:height] >= left[:,None]) & (xx[:height] < right[:,None])
        mask &= yy < bottom[None,:]
        assert mask[forced].all(), "Actual problem was not fully replaced"
        assert not mask[:,:115].any() and not mask[:,1139:].any()
        out = a.copy()
        out[mask] = b[mask]
        assert np.array_equal(out[~mask], a[~mask]) and np.array_equal(out[mask], b[mask])
        assert np.array_equal(out[:,:115], a[:,:115])
        assert np.array_equal(out[:,1139:], a[:,1139:])
        dest = HERE / variant
        dest.mkdir(exist_ok=True)
        Image.fromarray(out).save(dest / "candidate.png")
        ids = np.where(mask,2,1).astype(np.uint8)
        Image.fromarray(ids).save(dest / "source-id.png")
        Image.fromarray(mask.astype(np.uint8)*255).save(dest / "selection-mask.png")
        boxes = {
            "roof-full": [300,0,1190,750],
            "north": [430,0,1139,240],
            "middle": [540,180,1160,560],
            "caps-and-eave": [700,440,1180,840],
            "left-upper": [300,0,720,430],
            "left-lower": [490,360,960,830],
            "right-upper": [780,0,1200,430],
            "right-lower": [860,360,1220,830],
        }
        evidence=[]
        for name,box in boxes.items():
            path=dest/f"{name}.100pct.png"
            Image.fromarray(out).crop(box).save(path)
            evidence.append({"file":str(path),"sha256":sha(path),"nativeCrop":box})
        record={
            "variant":variant,"status":"pending-100percent-visual-review",
            "candidate":str(dest/"candidate.png"),"sha256":sha(dest/"candidate.png"),
            "globalNativeBox":[7565,8077,8819,9331],"imageSize":[1254,1254],
            "sources":[{"sourceId":i+1,"file":str(p),"sha256":sha(p)} for i,p in enumerate(SOURCES)],
            "sourceIdFile":str(dest/"source-id.png"),"sourceIdSha256":sha(dest/"source-id.png"),
            "mandatoryRegion":str(HERE/"mandatory-v02-region.png"),
            "allMandatoryPixelsFromV02":True,
            "sourcePixelProvenanceVerified":True,
            "leftAndRight115PixelsExactV01":True,
            "warp":False,"resample":False,"feather":False,"blend":False,"colorRewrite":False,
            "v02PixelCount":int(mask.sum()),
            "paths":{"left":left.tolist(),"right":right.tolist(),"bottom":bottom.tolist()},
            "pathCostsSquaredRGB":{"left":lc,"right":rc,"bottom":bc},
            "criterion":"Cost guides binary selection only; visual geometric continuity must decide acceptance.",
            "reproductionScript":str(Path(__file__).resolve()),"scriptSha256":sha(__file__),
            "evidence":evidence,
        }
        write_json(dest/"record.json",record)
        summary.append({"variant":variant,"candidateSha256":record['sha256'],"v02Pixels":int(mask.sum()),"record":str(dest/'record.json')})
    write_json(HERE/"attempts.json",summary)
    print(json.dumps(summary))

if __name__ == "__main__":
    main()
