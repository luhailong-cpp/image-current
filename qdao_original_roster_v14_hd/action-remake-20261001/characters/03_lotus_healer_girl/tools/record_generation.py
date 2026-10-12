from pathlib import Path
import json,sys,hashlib,shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
BASE=Path(__file__).resolve().parent.parent
ROOT=Path("D:/work/image")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
job_path=Path(sys.argv[1]).resolve()
job=json.loads(job_path.read_text(encoding="utf-8-sig"))
out=(BASE/job["output"]).resolve()
if not out.is_relative_to(BASE): raise ValueError("outside role directory")
host=Path(sys.argv[2])
out.parent.mkdir(parents=True,exist_ok=True)
if out.exists(): raise FileExistsError(out)
shutil.copy2(host,out)
im=Image.open(out)
record={"schemaVersion":1,"file":str(out.relative_to(BASE)).replace(chr(92),"/"),"sha256":sha(out),
"generatedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"generatedAtMeaning":"local receipt time; server timestamp unavailable",
"native":{"width":im.width,"height":im.height,"format":im.format,"mode":im.mode},
"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads((ROOT/"config/image-generation.json").read_text(encoding="utf-8-sig")),
"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[r["path"] for r in job["references"]]},
"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露/无可核实型号质量元数据",
"evidence":{"hostOutputPath":str(host),"copiedShaMatches":sha(host)==sha(out),"receipt":job.get("receipt"),"pngTextMetadata":{k:v for k,v in im.info.items() if isinstance(v,(str,int,float))}},
"prompt":job["prompt"],"promptSha256":sha(BASE/job["prompt"]),"references":[dict(r,sha256=sha(r["path"])) for r in job["references"]],
"status":job.get("status","pending_visual_review"),"review":job.get("review",{}),
"officialVerification":job.get("officialVerification",{"verifiedOn":"2026-10-03","url":"https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst","finding":"most capable image model, max quality listed; no built-in selectors"})}
if im.mode=="RGBA":
 record["alphaExtrema"]=im.getchannel("A").getextrema()
 record["alphaGt8Bounds"]=im.getchannel("A").point(lambda a:255 if a>8 else 0).getbbox()
out.with_name(out.name+".generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:record[k] for k in ["file","sha256","native","alphaGt8Bounds"]}))
