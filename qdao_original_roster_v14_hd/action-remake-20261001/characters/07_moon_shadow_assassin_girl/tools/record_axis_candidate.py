"""Record native built-in edits without altering formal frames."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shutil, sys
from PIL import Image
R=Path(__file__).resolve().parents[1]
S=R/'staging'/(sys.argv[2] if len(sys.argv)>2 else 'axis-continuity-20261004')
assert S.resolve().is_relative_to((R/'staging').resolve())
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=S/sys.argv[1]
assert base.resolve().is_relative_to(S.resolve())
req=load(base.with_suffix('.request.json'))
receipt=load(base.with_suffix('.receipt.json'))
src=Path(re.search(r' as (.+?\.png) by default',receipt['output_hint'])[1])
dst=base.with_suffix('.png')
assert not dst.exists()
shutil.copyfile(src,dst)
with Image.open(dst) as im:
    assert im.mode=='RGBA' and im.size==(1254,1254)
    alpha=im.getchannel('A')
    edge=max(alpha.crop(box).getextrema()[1] for box in ((0,0,1254,1),(0,1253,1254,1254),(0,0,1,1254),(1253,0,1254,1254)))
    assert edge<=8 and im.getextrema()[3]==(0,255)
params=req['submittedParameters']
refs=req['references']
assert [r['path'] for r in refs]==params['referenced_image_paths']
assert all(sha(Path(r['path']))==r['sha256'] for r in refs), 'Reference changed since request preparation'
save(Path(str(dst)+'.generation.json'),{'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.now(timezone.utc).isoformat(),'userTimezone':'America/New_York','generatedAtMeaning':'received/copied time','width':1254,'height':1254,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configurationTarget'],'submittedParameters':{**params,'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool does not expose model or quality selectors or actual values.','prompt':str(base.with_suffix('.request.json')),'evidence':{'toolResult':str(base.with_suffix('.receipt.json')),'hostPath':str(src),'hostSHA256':sha(src)},'references':refs,'editSource':{'path':refs[0]['path'],'sha256':refs[0]['sha256'],'generationRecord':refs[0]['path']+'.generation.json'},'reviewStatus':'pending_root_visual_review','nativeHD':True,'operation':'verbatim native tool output copy','edgeMaxAlpha':edge})
print(json.dumps({'path':str(dst),'sha256':sha(dst),'edgeMax':edge}))
