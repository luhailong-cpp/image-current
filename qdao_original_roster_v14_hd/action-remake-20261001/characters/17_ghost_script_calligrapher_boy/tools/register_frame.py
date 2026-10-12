"""Record host-generated frame; only uniform full-canvas downscale for review export."""
from pathlib import Path
import argparse,hashlib,json,shutil,datetime
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
REPO=BASE.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def register(source,key,request):
    source=Path(source).resolve(); request=Path(request).resolve()
    args=json.loads(request.read_text(encoding='utf-8-sig'))
    dest=BASE/'staging'/f'{key}.png'; dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and sha(dest)!=sha(source): raise RuntimeError('Do not overwrite existing frame')
    if not dest.exists(): shutil.copy2(source,dest)
    im=Image.open(dest); im.load()
    if im.width<1024 or im.height<1024: raise RuntimeError('Native frame below 1024')
    prompt=BASE/'prompts'/f'{key}.txt';prompt.parent.mkdir(exist_ok=True)
    prompt.write_text(args['prompt'],encoding='utf-8')
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
    rec={'file':str(dest.relative_to(BASE)).replace('\\','/'),'sha256':sha(dest),'generatedAt':now,'generatedAtEvidence':'Local registration time; generation completion occurred immediately before registration; exact tool timestamp not disclosed.','width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**{k:v for k,v in args.items() if k!='prompt'}},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具仅返回image_url/output_hint，未披露实际模型或质量。','evidence':{'toolReturnedPath':str(source),'workspaceCopyShaMatchesSource':sha(source)==sha(dest),'returnedFields':['image_url','output_hint'],'request':str(request.relative_to(BASE)).replace('\\','/')},'prompt':str(prompt.relative_to(BASE)).replace('\\','/'),'references':[{'path':p,'role':'See exact ordered roles in saved prompt'} for p in args.get('referenced_image_paths',[])],'review':{'status':'pending'}}
    dump(dest.with_suffix('.png.generation.json'),rec)
    print(json.dumps({'file':str(dest),'nativeSize':im.size,'sha256':rec['sha256']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('key');p.add_argument('request');a=p.parse_args();register(a.source,a.key,a.request)
