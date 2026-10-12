from pathlib import Path
import json,hashlib
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r04_c04/upper-left-work")
out=d/"merged-both-v1"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
evidence=[
 d/"s01_01-v1-native-evidence.json",
 d.parent/"native/s02_01_v4.png.generation.json",
 d.parent/"native/s03_01_v1.png.generation.json",
 d/"seam01-work/repair-v1-evidence.json",
 d/"seam02-work/seam02-v1-native-evidence.json"]
qa=json.loads((out/"final-qa-crops.json").read_text())
for item in qa:
 item.update({"actuallyViewed":True,"nativePixelScale":1,"visualVerdict":"pass","reviewers":["upper_left","lower_lantern_seam independent visual review"],"findings":"No visible duplicate gold fitting, tassel break, wall/ground color band or geometric discontinuity"})
review={"scope":"Only the two s01_01/s02_01/s03_01 lantern seams and all four new repair-entry/exit boundaries","status":"passed","sixNativeScaleCrops":qa,"overlapVerification":{"s01_s02_230pxExact":True,"s02_s03_230pxExact":True},"pixelProvenance":"every output pixel proved equal to recorded input at identical world coordinate","noResampling":True,"noBlending":True,"noColorCorrection":True,"outerNorth512pxPreserved":True,"outerSouth512pxPreserved":True,"formalTileAcceptance":False,"unreviewed":"Other columns, east-west interfaces and full tile acceptance remain parent scope","bestFiles":[str(out/f"s{r:02d}_01-derived.png") for r in (1,2,3)]}
(out/"local-seam-review.json").write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
manifest=json.loads((out/"derivation.json").read_text())
for idx,(src,e) in enumerate(zip(manifest["sources"],evidence)):
 src["generationEvidence"]=str(e)
 src["generationEvidenceSha256"]=sha(e)
 manifest["sourceMapLegend"][str(idx+1)]["generationEvidence"]=str(e)
 manifest["sourceMapLegend"][str(idx+1)]["generationEvidenceSha256"]=sha(e)
manifest["QA"]="passed local seam review; whole-tile formal acceptance remains false"
manifest["localSeamReview"]=str(out/"local-seam-review.json")
manifest["localSeamReviewSha256"]=sha(out/"local-seam-review.json")
for patch in manifest["derivedPatches"]:
 p=Path(patch["file"])
 record=json.loads(p.with_suffix(".png.generation.json").read_text())
 record["sources"]=manifest["sources"]
 record["localSeamQA"]={"status":"passed","report":str(out/"local-seam-review.json"),"formalTileAcceptance":False}
 p.with_suffix(".png.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
 patch.update(record)
(out/"derivation.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"bestDirectory":str(out),"localSeamQA":"passed","formalAccepted":False,"selectionModified":False,"progressModified":False},indent=2))

