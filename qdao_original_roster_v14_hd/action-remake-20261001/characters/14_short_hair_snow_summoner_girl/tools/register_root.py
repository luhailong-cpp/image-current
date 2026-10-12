import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('slot'); p.add_argument('--request', required=True); p.add_argument('--review', default='pending_visual_review'); a=p.parse_args()
    destination=ROOT/a.slot.split('-')[0]/'staging'/f'{a.slot}.png'
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(a.source,destination)
    im=Image.open(destination)
    req=json.loads((ROOT/a.request).read_text(encoding='utf-8-sig'))
    references=[]
    for path in req['submittedParameters']['referenced_image_paths']:
        references.append({'path':path,'sha256':sha(path),'role':'identity/direction/style or previous pose; see exact prompt'})
    rec={'file':str(destination.relative_to(ROOT)).replace('\\','/'),'sha256':sha(destination),'generatedAt':datetime.fromtimestamp(Path(a.source).stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host file mtime; tool did not expose timestamp','recordedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号、质量；配置和提示词不作为实测依据。','evidence':{'toolReturnedPath':a.source,'returnedFields':['image_url','output_hint'],'workspaceCopyShaMatchesSource':sha(destination)==sha(a.source)},'references':references,'request':a.request,'review':{'status':a.review}}
    Path(str(destination)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(destination),'size':im.size,'sha256':rec['sha256'],'alpha':rec['alphaExtrema']}))
if __name__=='__main__': main()
