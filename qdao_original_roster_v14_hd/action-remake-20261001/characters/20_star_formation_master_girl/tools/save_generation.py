from pathlib import Path
import argparse, json, hashlib, shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
BASE = Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('source');p.add_argument('dest');p.add_argument('prompt');p.add_argument('refs')
p.add_argument('--status',default='pending_visual_review');p.add_argument('--note',default='')
a=p.parse_args()
dest=(BASE/a.dest).resolve()
assert dest.is_relative_to(BASE),dest
dest.parent.mkdir(parents=True,exist_ok=True)
assert not dest.exists(),dest
shutil.copyfile(a.source,dest)
im=Image.open(dest);im.load()
cfg=json.loads((BASE.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
refs=json.loads(a.refs)
rec={'file':a.dest,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'generatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'generatedAtMeaning':'本地接收保存时间；服务端时刻未披露','width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':refs},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具无型号和质量选择器，回执未披露实际参数。','prompt':a.prompt,'references':[{'path':r,'role':('姿态/身份参考' if i<len(refs)-1 else '主要已确认画法风格参考')} for i,r in enumerate(refs)],'evidence':{'output_path':a.source,'result_type':'image_url + output_hint; no model/quality metadata'},'review':{'status':a.status,'note':a.note,'dynamicAcceptance':False}}
Path(str(dest)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':a.dest,'size':im.size,'mode':im.mode,'sha256':rec['sha256'],'status':a.status},ensure_ascii=False))

