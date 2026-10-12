from pathlib import Path
import json, hashlib, shutil, argparse
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('source');p.add_argument('--review',default='pending_visual_review');a=p.parse_args()
    key=a.key
    if '/' in key or '\\' in key or '..' in key: raise ValueError('unsafe key')
    request=ROOT/'provenance/requests'/f'{key}.json'
    q=json.loads(request.read_text(encoding='utf-8-sig'))
    dst=ROOT/'sources/new'/f'{key}.png';dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists(): raise ValueError('output exists')
    shutil.copyfile(a.source,dst)
    with Image.open(dst) as im:
        im.load(); geometry={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None}
    sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    config=json.loads((ROOT.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
    references=[{'file':path,'sha256':sha(path),'purpose':'Roles specified in saved actual prompt'} for path in q['submittedParameters'].get('referenced_image_paths',[])]
    record={'file':dst.relative_to(ROOT).as_posix(),'sha256':sha(dst),'generatedAt':q.get('startedAt'),'recordedAt':datetime.now(timezone.utc).isoformat(),**geometry,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':q.get('configSnapshot',config),'submittedParameters':q['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具无型号或质量选择器，回执未披露实际型号/质量。','prompt':f'prompts/{key}.txt','references':references,'evidence':{'hostOutput':a.source,'toolResult':f'provenance/receipts/{key}.tool.json'},'acceptance':a.review}
    out=ROOT/'provenance/generation'/f'{key}.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(dst),'record':str(out),'sha256':record['sha256'],**geometry},ensure_ascii=False))
if __name__=='__main__':main()
