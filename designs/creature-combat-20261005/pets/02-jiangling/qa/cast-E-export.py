import json,sys,hashlib
from pathlib import Path
from PIL import Image
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/02-jiangling")
n=int(sys.argv[1]); tag=f"cast-E-{n:02d}"
receipt=json.loads((root/"receipts"/f"{tag}.json").read_text(encoding="utf-8"))
src=Path(receipt["sourcePath"]); dst=root/"runtime/cast/E"/f"{n:02d}.png"
dst.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src); original={"width":im.width,"height":im.height,"mode":im.mode,"format":im.format}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
srcsha=sha(src)
out=im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS)
out.save(dst)
refs=[{"path":p,"role":r,"sha256":sha(Path(p))} for p,r in zip(receipt["references"],["E identity edit target","W rear identity anatomy reference","main painted material and finish style reference","previous reviewed E cast frame continuity reference"])]
record={"file":str(dst.relative_to(root)).replace("\\","/"),"sha256":sha(dst),"generatedAt":receipt["completedAt"],"generationStartedAt":receipt["startedAt"],"width":1024,"height":1024,"format":"PNG","mode":"RGBA","action":"cast","direction":"E","frame":n,"durationMs":45,"pivot":[0.5,0.08],"anchor":[512,942],"event":"cast" if n==10 else None,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":receipt["references"]},"actualModel":None,"actualQuality":None,"evidence":{"receipt":f"receipts/{tag}.json","returnedFields":receipt["returnedFields"]},"unverifiedReason":"宿主管理；工具未披露模型或质量，当前工具无model/quality选择器。","prompt":f"prompts/{tag}.txt","references":refs,"native":{"path":str(src),"sha256":srcsha,**original},"derivedFrom":{"path":str(src),"sha256":srcsha,"generationRecord":f"records/{tag}.json"},"operation":{"type":"uniformFullCanvasResize","sourceSize":[im.width,im.height],"destinationSize":[1024,1024],"resample":"Lanczos","noTranslation":True,"noPerFrameFootAlignment":True},"visualReview":{"status":"reviewed-single-frame","checks":["E front three-quarter facing lower-right","two hands and two feet","right fan with three jade bells, left empty","identity clothing and short black bob preserved","full subject contained"],"continuousPlayback":"pending"}}
for p in [root/"records"/f"{tag}.json",dst.with_suffix(".png.generation.json")]:p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":n,"native":original,"sha256":record["sha256"],"alphaExtrema":out.getchannel("A").getextrema(),"bbox":out.getchannel("A").getbbox()}))

