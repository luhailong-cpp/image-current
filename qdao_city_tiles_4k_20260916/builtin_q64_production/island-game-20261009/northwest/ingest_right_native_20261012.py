"""Local receipt-backed exact native ingest without global config dependency."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil,argparse
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
a=argparse.ArgumentParser();a.add_argument("--stem",required=True);a.add_argument("--source",required=True);a.add_argument("--prompt",required=True);a.add_argument("--refs",required=True);o=a.parse_args()
src=Path(o.source);dst=Z/"native"/(o.stem+".png");gp=dst.with_suffix(".png.generation.json")
assert not gp.exists(),"Refuse overwrite generation record"
rp=Z/"receipts"/(o.stem+".receipt.json");receipt=read(rp)
assert Path(receipt["generatedFile"]).resolve()==src.resolve()
assert receipt["tool"]=="image_gen.imagegen" and receipt["route"]=="builtin"
with Image.open(src) as im:
    im.load();assert im.size==(1254,1254) and im.mode in ("RGB","RGBA")
    if im.mode=="RGBA":assert im.getextrema()[3]==(255,255)
    size=list(im.size);fmt=im.format
if dst.exists():assert sha(dst)==sha(src),"Existing partial copy differs"
else:shutil.copy2(src,dst)
refs=read(o.refs)
if isinstance(refs,dict):refs=refs["inputs"]
for r in refs:
    assert sha(r["path"])==r["sha256"],"Reference changed since guide"
    r["nativeSize"]=list(Image.open(r["path"]).size)
cfg=Path("D:/work/image/config/image-generation.json")
rec=dict(file=dst.as_posix(),sha256=sha(dst),generatedAt=datetime.now(timezone.utc).isoformat(),nativeWidth=size[0],nativeHeight=size[1],format=fmt,sourceOutputPath=src.as_posix(),sourceOutputSha256=sha(src),tool="image_gen.imagegen",route="builtin",configSnapshot=read(cfg) if cfg.exists() else None,configSnapshotUnavailableReason=None if cfg.exists() else "Global image config absent at ingestion; actual host model and quality undisclosed. No config restored or invented.",submittedParameters=dict(model=None,quality=None,transparent_background=False),actualModel=None,actualQuality=None,unverifiedReason="Host managed; builtin tool does not disclose model or quality.",prompt=o.prompt,promptSha256=sha(o.prompt),references=refs,evidence=dict(receipt=rp.as_posix(),ingestionScript=Path(__file__).as_posix()),resizedAfterGeneration=False,finalArtUpscaled=False,status="candidate_pending_native_visual_and_seam_QA")
ip=Z/"guides"/(o.stem+".input.json")
if ip.exists():
    i=read(ip)
    if "globalBox" in i:rec["globalBox"]=i["globalBox"];rec["coreBox"]=i["coreBox"]
gp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"file":dst.as_posix(),"size":size,"sha256":sha(dst),"configPresent":cfg.exists(),"progressModified":False}))

