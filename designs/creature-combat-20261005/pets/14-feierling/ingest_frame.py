"""Archive textual evidence and export one real AI frame; never creates a pose."""
import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
action,direction,index,source=sys.argv[1:5]
index=f'{int(index):02}'
src=Path(source)
gen=ROOT/'generation'/action/direction
out=ROOT/'runtime'/action/direction
gen.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
native=gen/f'{index}.native.png'; target=out/f'{index}.png'
shutil.copyfile(src,native)
with Image.open(native) as im:
    dims=list(im.size); mode=im.mode
    assert mode=='RGBA', 'Native output missing RGBA; do not silently remove background'
    im.resize((1024,1024),Image.Resampling.LANCZOS).save(target)
    native_meta={k:str(v)[:2000] for k,v in im.info.items() if k not in ['icc_profile','exif']}
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
references=[{'path':'D:/work/image/designs/pets-xianling-20260924/source/14-feierling-E.png','role':'E native identity and anatomy'}, {'path':'D:/work/image/designs/pets-xianling-20260924/source/14-feierling-W.png','role':'W native identity and anatomy'}, {'path':'D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','role':'MAIN approved painting and material style'}]
receipt_path=gen/f'{index}.receipt.json'
if receipt_path.exists():
    receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    submitted_refs=receipt.get('submittedReferences',receipt.get('referenced_image_paths',[]))
    for path in submitted_refs:
        if path not in [r['path'] for r in references]: references.append({'path':path,'role':'accepted same-direction frame for scale and pose continuity'})
for ref in references: ref['sha256']=sha(Path(ref['path']))
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.now(timezone.utc).isoformat(),'native':{'file':native.relative_to(ROOT).as_posix(),'sha256':sha(native),'width':dims[0],'height':dims[1],'format':'PNG','mode':mode},'width':1024,'height':1024,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'userOverride':'GPT Image 2.5 / max target; built-in only','submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[x['path'] for x in references]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未提供 model/quality 选择器，返回未披露实际版本和质量。','prompt':(gen/f'{index}.prompt.txt').relative_to(ROOT).as_posix(),'references':references,'evidence':{'returnedSourcePath':str(src),'receipt':(gen/f'{index}.receipt.json').relative_to(ROOT).as_posix(),'nativeMetadataSummary':native_meta},'derivedFrom':{'sha256':sha(native),'nativeFile':native.relative_to(ROOT).as_posix()},'operation':{'type':'whole-canvas-resize','from':dims,'to':[1024,1024],'resampling':'LANCZOS','perFrameAlignment':False},'visualStatus':'pending full sequence review'}
(gen/f'{index}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(target),'nativeSize':dims,'sha256':record['sha256']}))
