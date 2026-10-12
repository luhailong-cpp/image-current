"""Fixed whole-canvas export. Does not create animation poses."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__':
    action, direction, frame, source = sys.argv[1:5]
    assert action in ('hit','attack','cast') and direction in ('E','W')
    frame=f'{int(frame):02d}'
    source=Path(source)
    provenance=ROOT/'provenance'/action/direction
    provenance.mkdir(parents=True,exist_ok=True)
    native=provenance/'_inprogress'/f'{frame}.png'
    native.parent.mkdir(exist_ok=True)
    if not native.exists(): shutil.copy2(source,native)
    im=Image.open(native)
    assert im.width==im.height, 'Non-square native needs review'
    assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0, 'Real alpha required'
    out=Image.new('RGBA',(1024,1024))
    out.alpha_composite(im.resize((920,920),Image.Resampling.LANCZOS),(52,37))
    final=ROOT/'runtime'/action/direction/f'{frame}.png'
    final.parent.mkdir(parents=True,exist_ok=True)
    out.save(final)
    request_path=provenance/f'{frame}.request.json'
    request=json.loads(request_path.read_text(encoding='utf-8-sig')) if request_path.exists() else {}
    record={'file':str(final.relative_to(ROOT)).replace('\\','/'),'sha256':sha(final),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((ROOT.parents[3]/'config'/'image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未开放型号/质量选择器，返回值未披露型号和质量。','prompt':str((provenance/f'{frame}.prompt.txt').relative_to(ROOT)).replace('\\','/'),'references':[{'path':p,'role':('E identity' if i==0 else 'W identity' if i==1 else 'main style' if i==2 else 'continuity')} for i,p in enumerate(request.get('referenced_image_paths',[]))],'evidence':str((provenance/f'{frame}.receipt.json').relative_to(ROOT)).replace('\\','/'),'derivedFrom':{'file':str(native.relative_to(ROOT)).replace('\\','/'),'sha256':sha(native),'width':im.width,'height':im.height,'format':'PNG','hostOutputPath':str(source)},'operation':{'type':'fixed_whole_canvas_resize_and_composite','resizedSize':[920,920],'offset':[52,37],'canvasSize':[1024,1024],'perFrameAlignment':False},'visualReview':'pending'}
    dump(final.with_suffix('.png.generation.json'),record)
    print(json.dumps({'file':str(final),'nativeSize':im.size,'nativeSHA':sha(native),'sha256':sha(final),'alphaBBox':out.getbbox()}))
