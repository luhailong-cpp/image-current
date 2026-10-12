"""Export one real generated sprite; never synthesize animation frames."""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT.parents[3] / 'config/image-generation.json').read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def finalize(action, direction, frame, source, receipt, review, replace=False):
    source, receipt = Path(source), Path(receipt)
    native = Image.open(source)
    if native.size != (1254,1254):
        raise ValueError(f'Unexpected native size {native.size}; fixed batch export expects 1254 square')
    if 'A' not in native.getbands():
        raise ValueError('Generated image is not RGBA/alpha; repair through imagegen')
    alpha=native.getchannel('A')
    if alpha.getextrema() != (0,255):
        raise ValueError('Expected genuine transparent and opaque regions')
    outdir=ROOT/'runtime'/action/direction
    outdir.mkdir(parents=True,exist_ok=True)
    out=outdir/f'{frame:02}.png'
    if out.exists() and not replace:
        raise FileExistsError(out)
    # Same whole-canvas transform for all actions in each direction.
    # E/W offsets are fixed once from the existing identity images, never per frame.
    offset=(0,28 if direction=='E' else -13)
    canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
    scaled=native.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
    canvas.alpha_composite(scaled,offset)
    canvas.save(out)
    records=ROOT/'records'/action/direction
    records.mkdir(parents=True,exist_ok=True)
    rec=json.loads(receipt.read_text(encoding='utf-8-sig'))
    record={
      'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'generatedAt':rec.get('completedAt'),
      'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin',
      'configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None,'transparent_background':True},
      'actualModel':None,'actualQuality':None,
      'unverifiedReason':'宿主管理；内置工具未开放 model/quality 选择器，也未披露实际返回版本/质量。',
      'prompt':rec.get('promptPath',f'prompts/{action}/{direction}/{frame:02}.txt'),
      'references':rec.get('arguments',{}).get('referenced_image_paths',[]),
      'evidence':{'receipt':receipt.relative_to(ROOT).as_posix(),'toolResultFields':['image_url','output_hint']},
      'native':{'path':str(source),'width':native.width,'height':native.height,'mode':native.mode,'sha256':sha(source),'retained':True},
      'derivedFrom':{'path':str(source),'sha256':sha(source)},
      'operation':{'type':'uniform_whole_canvas_export','scale':1024/1254,'offset':list(offset),'interpolation':'LANCZOS','directionRuleFixed':True,'perFrameAlignment':False},
      'action':action,'direction':direction,'frame':frame,'durationMs':{'hit':40,'attack':30,'cast':45}[action],
      'pivot':[0.5,0.08],'anchorTopLeft':[512,942],
      'visualReview':{'status':'reviewed_single_frame','notes':review,'reviewedAt':datetime.now(timezone.utc).isoformat()},
      'dynamicReview':'pending','clientIntegration':'not_tested'
    }
    (records/f'{frame:02}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(out),'nativeSize':native.size,'bbox':canvas.getchannel('A').getbbox(),'sha256':sha(out)},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('action');p.add_argument('direction');p.add_argument('frame',type=int);p.add_argument('source');p.add_argument('receipt');p.add_argument('--review',required=True)
    p.add_argument('--replace',action='store_true')
    a=p.parse_args();finalize(a.action,a.direction,a.frame,a.source,a.receipt,a.review,a.replace)
