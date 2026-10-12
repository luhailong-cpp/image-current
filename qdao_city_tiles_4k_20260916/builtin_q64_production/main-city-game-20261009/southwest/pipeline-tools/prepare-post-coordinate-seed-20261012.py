from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Path(sys.argv[1]);D=B/'r09_c06/refinement/versions/resume-20261012-v02';D.mkdir(parents=True,exist_ok=True);dst=D/'p01_03.rejected-native.png';assert not dst.exists();shutil.copy2(src,dst)
guide=B/'r09_c06/pipeline/guides/p01_03.resume-20261012-v01.continuity-seed.png';a=Image.open(dst).convert('RGB');g=Image.open(guide).convert('RGB');assert a.size==g.size==(1254,1254)
a.paste(g.crop((0,0,380,1254)),(0,0))
out=B/'r09_c06/pipeline/guides/p01_03.resume-20261012-v03.coordination-seed.png';assert not out.exists();a.save(out)
record={'savedAtUtc':datetime.now(timezone.utc).isoformat(),'guideOnly':True,'gameArt':False,'file':str(out),'sha256':sha(out),'dimensions':[1254,1254],'operation':'Exact crop/paste native known-left plus approved coarse left-post band from original continuity seed onto prior actual builtin output; no scaling, painting or pixel adjustment','nativeSource':{'file':str(dst),'sha256':sha(dst),'actualToolPath':str(src)},'guideSource':{'file':str(guide),'sha256':sha(guide),'copiedBox':[0,0,380,1254]},'finalArtCreated':False}
atomic_json(Path(str(out)+'.derivation.json'),record)
atomic_json(D/'preservation.json',{'file':str(dst),'sha256':sha(dst),'sourceOutputPath':str(src),'receipt':str(B/'r09_c06/pipeline/receipts/p01_03.resume-20261012-v02.tool-result.json'),'selected':False,'formalAccepted':False})
print(json.dumps(record,ensure_ascii=False))

