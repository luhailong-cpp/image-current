"""Record assigned p21/p31/p41 native results without touching zone progress."""
import sys, json, re, shutil, hashlib, datetime
from pathlib import Path
from PIL import Image
ZONE = Path(__file__).resolve().parent.parent
ROOT = next(p for p in ZONE.parents if (p/'config/image-generation.json').is_file())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
name=sys.argv[1]
if not re.fullmatch(r'r06_c12_p(?:21|31|41)-v[0-9]+',name): raise ValueError('Assigned prefixes only')
patch_id=name.split('-')[0]
rp=ZONE/'records'/f'{name}.receipt.json'
receipt=read(rp)
match=re.search(r' as (.+?) by default\.',receipt['response']['output_hint'])
if not match: raise ValueError('No output path in tool receipt')
source=Path(match.group(1))
target=ZONE/'native'/f'{name}.png'
if target.exists() and sha(target)!=sha(source): raise ValueError('Version already exists')
if not target.exists(): shutil.copy2(source,target)
with Image.open(target) as im:
    im.load()
    width,height=im.size
    fmt=im.format
    keys=list(im.info)
manifest=read(ZONE/'records/r06_c12.coordinates.json')
coordinate=next(p for p in manifest['patches'] if p['id']==patch_id)
prepared_path=ZONE/'records'/f'{patch_id}.prepared-references.json'
prepared=read(prepared_path)
roles={str(Path(r['path']).resolve()):r['role'] for r in prepared['references']}
refs=[]
for value in receipt['request']['referenced_image_paths']:
    path=Path(value).resolve()
    role=roles.get(str(path),'precise local edit target; repair only identified discontinuity, preserve frame')
    ref={'path':str(path),'sha256':sha(path),'role':role}
    for suffix in ('.generation.json','.derived.json','.references.json'):
        side=path.with_name(path.name+suffix)
        if side.exists():ref.setdefault('provenance',[]).append({'path':str(side),'sha256':sha(side)})
    refs.append(ref)
prompt=ZONE/'records'/f'{name}.prompt.txt'
record={'file':str(target),'sha256':sha(target),'width':width,'height':height,'format':fmt,
    'patchId':patch_id,'version':name.split('-')[-1],'generatedAt':None,
    'observedAtUtc':receipt['observedAtUtc'],'timeEvidence':'tool observation time; exact generation time undisclosed',
    'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin',
    'configSnapshot':prepared['configSnapshot'],'configSnapshotCaptureStage':'prepared guide before generation',
    'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,
    'unverifiedReason':'Host-managed image_gen exposes no model/quality selectors; receipt and PNG metadata disclose no actual model/quality',
    'prompt':{'path':str(prompt),'sha256':sha(prompt)},'receipt':{'path':str(rp),'sha256':sha(rp)},
    'evidence':{'receipt':str(rp),'pngMetadataKeys':keys},'references':refs,
    'coordinateRecord':{'path':str(ZONE/'records/r06_c12.coordinates.json'),'sha256':sha(ZONE/'records/r06_c12.coordinates.json')},
    'coordinates':coordinate,'preparedGuideEvidence':{'path':str(prepared_path),'sha256':sha(prepared_path)},
    'source':{'path':str(source),'sha256':sha(source),'operation':'byte-for-byte copy; no resizing'},
    'dimensionValidation':{'expected':[1254,1254],'actual':[width,height],'passed':(width,height)==(1254,1254)},
    'usableNative':False,'formalAccepted':False,'status':'candidate_awaiting_100_percent_seam_QA'}
save(str(target)+'.generation.json',record)
print(json.dumps({'path':str(target),'sha256':record['sha256'],'size':[width,height],'metadataKeys':keys},ensure_ascii=False))
if (width,height)!=(1254,1254): raise SystemExit(2)
