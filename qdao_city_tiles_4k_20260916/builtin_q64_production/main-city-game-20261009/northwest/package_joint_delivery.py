"""Package a jointly reviewed 2x2 milestone; never marks the entire zone complete."""
from pathlib import Path
import argparse, datetime, hashlib, json, zipfile
from PIL import Image
import numpy as np

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def ref(p): return {"file":str(p),"sha256":sha(p)}
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("joint_directory")
    a=ap.parse_args()
    d=Path(a.joint_directory).resolve()
    z=Path(__file__).resolve().parent
    if not d.is_relative_to(z/"joint-2x2-r05_c04-r06_c05"):
        raise ValueError("Delivery must stay within the owned joint directory")
    manifest=d/"joint-assembly.json"; m=read(manifest)
    assert m["pixelProvenanceVerification"]["status"]=="passed"
    assert m["pixelProvenanceVerification"]["pixelsVerified"]==8192*8192
    expected={q["name"]:q for q in m["qa"]}
    assert len(expected)==161
    reports=[d/("review-"+part+".json") for part in ("vertical","horizontal","junctions")]
    entries={}
    for p in reports:
        data=read(p)
        for entry in data["entries"]:
            name=entry["name"]
            assert name in expected and name not in entries, name
            assert entry["sha256"]==expected[name]["sha256"]==sha(Path(expected[name]["file"])),name
            assert entry["verdict"] in ("passed","nonblocking"),(name,entry["verdict"])
            assert entry.get("actuallyViewed") or entry.get("inheritedFrom"),name
            if not entry.get("actuallyViewed"):
                origin=entry["inheritedFrom"]
                assert origin["sha256"]==entry["sha256"],name
            entries[name]=entry
    assert set(entries)==set(expected)
    joint=Path(m["output"]["file"])
    assert sha(joint)==m["output"]["sha256"]
    img=Image.open(joint).convert("RGB")
    for tile in m["splitTiles"]:
        p=Path(tile["file"])
        assert sha(p)==tile["sha256"]
        assert np.array_equal(np.asarray(Image.open(p).convert("RGB")),np.asarray(img.crop(tile["cropLTRB"])))
    preview=d/"preview-only-1600.png"
    img.resize((1600,1600),Image.Resampling.LANCZOS).save(preview)
    summary={
        "schemaVersion":1,
        "createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status":"joint_milestone_internal_visual_qa_passed",
        "scope":"r05_c04/r05_c05/r06_c04/r06_c05 only; northwest zone remains in progress",
        "wholeZoneComplete":False,
        "ownedZoneTileCount":60,
        "currentJointTileCount":4,
        "assemblyManifest":ref(manifest),
        "jointImage":m["output"],
        "tiles":m["splitTiles"],
        "nativePixelProvenance":m["pixelProvenanceVerification"],
        "tileCropsVerified":4,
        "reviewReports":[ref(p) for p in reports],
        "qaCount":len(entries),
        "directlyViewedCount":sum(bool(e.get("actuallyViewed")) for e in entries.values()),
        "identicalHashInheritedCount":sum(not bool(e.get("actuallyViewed")) for e in entries.values()),
        "blockingCount":0,
        "crossTileQA": {"status":"passed_within_current_2x2", "seamSegments":m["visualQA"]["betweenTileSeamSegments"], "junctions":m["visualQA"]["tileBoundaryJunctions"], "outerSidesPending":True},
        "nonblockingCount":sum(e["verdict"]=="nonblocking" for e in entries.values()),
        "preview":{**ref(preview),"pixels":[1600,1600],"previewOnly":True,"resampled":True,"productionSource":False},
        "formalAccepted":False,
        "outerBoundaryStatus":"pending adjacent native tiles outside the current 2x2",
        "runtimeIntegration":False,
        "capacity5000Validated":False,
        "actualModel":None,"actualQuality":None,
        "entries":list(entries.values()),
    }
    write(d/"delivery-summary.json",summary)
    readme=d/"DELIVERY.txt"
    readme.write_text(
        "西北官府区：连续 2×2 原生美术样段\n\n"
        "本包含 r05_c04、r05_c05、r06_c04、r06_c05 四张 4096×4096 PNG。\n"
        "排列：上排 r05_c04 / r05_c05；下排 r06_c04 / r06_c05。\n"
        "四张图精确切自同一张 8192×8192 联合图，共用边已完成联合检查。\n"
        "161 处接缝和交点审查无阻断问题。细微纹理差异详见审查记录。\n"
        "正式像素逐点追溯至 64 张原生生成图；未放大、羽化、模糊、变形或调色。\n"
        "preview-only-1600.png 是浏览缩略图，不是正式 4K 原图。\n\n"
        "此包仅为当前 4 块样段，不代表整个西北 60 块区域完成。\n"
        "外圈未生成邻块的美术接缝仍待后续闭合；本次不包含游戏接入工作。\n"
        "完整像素来源和原始工具凭据保存在制作目录；本包内有审查摘要。\n",
        encoding="utf-8")
    package=d/"northwest-2x2-4k-tiles.zip"
    with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_STORED) as zipf:
        for tile in m["splitTiles"]:
            p=Path(tile["file"]); zipf.write(p,"tiles/"+p.name)
        for p in [readme,preview,d/"delivery-summary.json",manifest,*reports]:
            zipf.write(p,p.name)
    write(d/"package.json",{"package":ref(package),"bytes":package.stat().st_size,"joint":m["output"],"summary":ref(d/"delivery-summary.json"),"wholeZoneComplete":False})
    print(json.dumps({"package":str(package),"qaCount":161,"blockingCount":0,"tiles":4,"wholeZoneComplete":False}))

if __name__=="__main__": main()
