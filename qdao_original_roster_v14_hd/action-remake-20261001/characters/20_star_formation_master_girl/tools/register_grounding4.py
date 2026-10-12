"""Register a built-in grounding correction and whole-canvas export."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,json,hashlib,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=argparse.ArgumentParser();p.add_argument("job");a=p.parse_args();j=rd(Path(a.job))
out=(ROOT/j["dest"]).resolve();assert out.is_relative_to(ROOT)
out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists(),out
shutil.copyfile(j["outputPath"],out)
im=Image.open(out);im.load();assert im.mode=="RGBA" and min(im.size)>=1024
refs=[]
for i,path in enumerate(j["refs"]):
 q=Path(path);r={"path":path,"role":j.get("roles",["edit_target","previous_phase","identity_reference","bamboo_direction_reference","approved_style_reference"])[i],"sha256":sha(q),"size":Image.open(q).size}
 side=Path(str(q)+".generation.json")
 if side.exists():r.update(generationRecord=str(side),generationRecordSha256=sha(side))
 refs.append(r)
prompt=out.with_suffix(".prompt.txt");prompt.write_text(j["prompt"],encoding="utf-8")
rec={"file":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"generatedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"generatedAtMeaning":"本地接收保存时间","width":im.width,"height":im.height,"mode":im.mode,"format":"PNG","tool":"image_gen__imagegen","route":"builtin","configSnapshot":rd(ROOT.parents[3]/"config/image-generation.json"),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":j["refs"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具无型号和质量选择器，回执未披露实际参数。","prompt":prompt.relative_to(ROOT).as_posix(),"references":refs,"evidence":{"output_path":j["outputPath"],"output_hint":j["outputHint"],"resultKeys":["image_url","output_hint"]},"review":{"status":"pending_visual_review","dynamicAcceptance":False}}
wr(Path(str(out)+".generation.json"),rec)
dest=out.with_name(out.stem+"-1024.png")
im.resize((1024,1024),Image.Resampling.LANCZOS).save(dest)
wr(Path(str(dest)+".generation.json"),{"file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"width":1024,"height":1024,"mode":"RGBA","format":"PNG","derivedFrom":{"file":rec["file"],"sha256":rec["sha256"],"generationRecord":rec["file"]+".generation.json","generationRecordSha256":sha(Path(str(out)+".generation.json"))},"operation":{"type":"whole_canvas_resize","sourceCanvas":list(im.size),"imageSize":[1024,1024],"offset":[0,0],"canvasSize":[1024,1024],"pivot":[512,922],"resizeCount":1,"usesBoundingBox":False,"alignsLowestPixel":False,"resample":"LANCZOS"},"actualModel":None,"actualQuality":None,"isNewAIGeneration":False})
print(json.dumps({"native":str(out),"export":str(dest),"size":im.size,"sha256":sha(dest)},ensure_ascii=False))

