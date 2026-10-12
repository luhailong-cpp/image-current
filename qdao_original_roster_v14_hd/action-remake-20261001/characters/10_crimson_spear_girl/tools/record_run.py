from pathlib import Path
import json, hashlib, argparse, shutil
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = Path('D:/work/image')
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
parser=argparse.ArgumentParser()
parser.add_argument('slot')
parser.add_argument('source')
args=parser.parse_args()
folder=ROOT/'generation'/args.slot
folder.mkdir(parents=True, exist_ok=True)
source=Path(args.source)
dest=folder/'native.png'
if source.resolve()!=dest.resolve(): shutil.copy2(source,dest)
im=Image.open(dest)
direction=args.slot.split('-')[1]
refs=[
 (PROJECT/f'qdao_original_roster_v14_hd/recovery-20260921/10-delivery-preview/current/idle/{direction}.png','direction, identity and camera'),
 (PROJECT/'q_daoist_character_pack_4096/10_crimson_spear_girl_transparent_4096.png','identity details'),
 (PROJECT/'designs/jubaozhai-ui/02-characters.png','approved painting style')]
request_path=folder/'request.json'
if request_path.exists():
    request=json.loads(request_path.read_text(encoding='utf-8-sig'))
    refs=[(Path(p),'submitted image reference '+str(i+1)) for i,p in enumerate(request['referenced_image_paths'])]
receipt=folder/'receipt.json'
write(receipt, {'tool':'image_gen.imagegen','returnedFile':str(source),'resultFields':['image_url','output_hint'],'actualModel':None,'actualQuality':None,'recordedAt':datetime.now(timezone.utc).isoformat()})
write(folder/'native.png.generation.json',{
 'file':str(dest.relative_to(ROOT)), 'sha256':digest(dest),
 'generatedAt':datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
 'generatedAtEvidence':'host returned file modification time, recorded after tool completion',
 'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,
 'tool':'image_gen.imagegen','route':'builtin',
 'configSnapshot':json.loads((PROJECT/'config/image-generation.json').read_text(encoding='utf-8-sig')),
 'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[str(p) for p,_ in refs]},
 'actualModel':None,'actualQuality':None,
 'evidence':{'receipt':str(receipt.relative_to(ROOT))},
 'unverifiedReason':'宿主管理，工具没有 model/quality 选择器，结果未披露可核实型号与质量。',
 'prompt':str((folder/(request.get('prompt_file','prompt.txt') if request_path.exists() else 'prompt.txt')).relative_to(ROOT)),
 'references':[{'file':str(p),'sha256':digest(p),'purpose':role} for p,role in refs],
 'review':{'status':'candidate','dynamicAcceptance':False,'nativeAlpha':im.mode=='RGBA','nativeSizePass':min(im.size)>=1024}
})
print(json.dumps({'file':str(dest),'size':im.size,'mode':im.mode,'sha256':digest(dest)},ensure_ascii=False))
