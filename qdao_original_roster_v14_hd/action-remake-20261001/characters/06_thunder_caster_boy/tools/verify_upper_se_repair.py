from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json
R=Path(__file__).resolve().parents[1]
checks=[]
for n,v in [(2,2),(3,1)]:
 stem=f'run_SE_{n:02}_uppercontinuity_v{v}';p=R/'runtime/run/SE'/f'{n:02}.png';s=R/'work'/f'{stem}.png';a=Image.open(s);b=Image.open(p)
 assert a.size==(1254,1254) and b.size==(1024,1024) and b.mode=='RGBA'
 assert ImageChops.difference(a.resize((1024,1024),Image.Resampling.LANCZOS),b).getbbox() is None
 rec=json.loads(s.with_name(s.name+'.generation.json').read_text(encoding='utf-8'));rec['evidence']['toolReceipt']=f'records/{stem}_toolreceipt.json';s.with_name(s.name+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 checks.append({'frame':n,'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(a.size),'runtimeSize':list(b.size),'rgba':b.mode,'alphaExtrema':b.getchannel('A').getextrema(),'exactFullCanvasDownsample':True})
p=R/'work/run_SE_02_uppercontinuity_v1.png.generation.json';j=json.loads(p.read_text(encoding='utf-8'));j['visualReview']='拒稿：左符牌位置改善，但头部较原帧明显放大、上移，未采用。';j['rejected']=True;j['evidence']['toolReceipt']='records/run_SE_02_uppercontinuity_v1_toolreceipt.json';p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
out=R/'review/SE02_03_upper_repair_verification_20261005.json';out.write_text(json.dumps({'checks':checks,'runtimeEdits':['SE02','SE03'],'actualModel':None,'actualQuality':None,'phaseAndTimingChanged':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
