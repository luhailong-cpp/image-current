"""Export independently AI-generated frames with one fixed whole-canvas transform."""
from pathlib import Path
from PIL import Image
import sys, json, hashlib, datetime

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[3]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
source, action, direction, number = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
stem = f'{action}-{direction}-{number:02}'
out = ROOT / 'runtime' / action / direction / f'{number:02}.png'
out.parent.mkdir(parents=True, exist_ok=True)
im = Image.open(source)
assert im.mode == 'RGBA', f'Expected real RGBA, got {im.mode}'
assert im.width == im.height, 'Uniform square export requires a square source'
assert im.getchannel('A').getextrema()[0] == 0, 'No transparent pixels'
final = Image.new('RGBA', (1024,1024))
final.alpha_composite(im.resize((960,960), Image.Resampling.LANCZOS),(32,6))
final.save(out)
refs = [
 ('designs/pets-xianling-20260924/source/07-cangzhanglin-E.png','original E identity and anatomy'),
 ('designs/pets-xianling-20260924/source/07-cangzhanglin-W.png','original W identity and anatomy'),
 ('designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','main approved painting and material style')]
record = {
 'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),
 'generatedAt':datetime.datetime.fromtimestamp(source.stat().st_mtime,datetime.timezone.utc).isoformat(),
 'native':{'file':str(source),'sha256':sha(source),'width':im.width,'height':im.height,'format':'PNG','mode':im.mode},
 'width':1024,'height':1024,'format':'PNG','tool':'image_gen.imagegen','route':'builtin',
 'configSnapshot':json.loads((PROJECT/'config/image-generation.json').read_text(encoding='utf-8-sig')),
 'submittedParameters':{'model':None,'quality':None,'transparent_background':True},
 'actualModel':None,'actualQuality':None,
 'unverifiedReason':'宿主管理，工具没有 model/quality 选择器，返回未披露，原生PNG无可核实版本元数据。',
 'prompt':f'prompts/{stem}.txt','evidence':f'records/{stem}.receipt.txt',
 'references':[{'file':str(PROJECT/p),'purpose':role,'sha256':sha(PROJECT/p)} for p,role in refs],
 'derivedFrom':{'file':str(source),'sha256':sha(source)},
 'operation':{'type':'whole-canvas-uniform-export','sourceCanvas':list(im.size),'resizedCanvas':[960,960],'destinationCanvas':[1024,1024],'offset':[32,6],'resampling':'Lanczos','perFrameAlignment':False},
 'visualStatus':'pending-group-review','clientIntegration':'not-tested'}
rec = ROOT/'records'/f'{stem}.generation.json'
for extra in sys.argv[5:]:
    continuity = Path(extra)
    record['references'].append({'file':str(continuity),'purpose':'independent AI frame for framing, identity or targeted pose correction; see prompt for exact role','sha256':sha(continuity)})
rec.parent.mkdir(parents=True,exist_ok=True)
rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':record['file'],'sha256':record['sha256'],'native':list(im.size),'alpha':final.getchannel('A').getextrema()}))
