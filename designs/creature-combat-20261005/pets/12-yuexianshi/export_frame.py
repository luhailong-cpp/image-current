"""Fixed whole-canvas export; never aligns individual feet or synthesizes a pose."""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('job')
    args=p.parse_args()
    job=json.loads(Path(args.job).read_text(encoding='utf-8-sig'))
    action,direction,index=job['action'],job['direction'],job['index']
    group=f'{action}-{direction}'
    source=Path(job['source'])
    img=Image.open(source)
    native={'width':img.width,'height':img.height,'mode':img.mode,'format':img.format,'sha256':sha(source)}
    if img.width!=img.height: raise ValueError('Native canvas must be square; review instead of stretching')
    if img.mode!='RGBA': raise ValueError('Native image missing RGBA; do not invent alpha')
    alpha=img.getchannel('A')
    if alpha.getextrema()[0]!=0: raise ValueError('No transparent pixels')
    out=ROOT/'runtime'/action/direction/f'{index:02}.png'
    out.parent.mkdir(parents=True,exist_ok=True)
    canvas=Image.new('RGBA',(1024,1024))
    # The same normalized full-canvas transform is used across every frame.
    resized=img.resize((960,960),Image.Resampling.LANCZOS)
    canvas.paste(resized,(32,16))
    canvas.save(out)
    refs=[]
    for entry in job['references']:
        ref=dict(entry); ref['sha256']=sha(ref['path']); refs.append(ref)
    record={
        'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),
        'generatedAt':job['generatedAt'],'recordedAt':datetime.now(timezone.utc).isoformat(),
        'action':action,'direction':direction,'frame':index,'durationMs':{'hit':40,'attack':30,'cast':45}[action],
        'width':1024,'height':1024,'format':'PNG','mode':'RGBA','native':native,
        'tool':'image_gen.imagegen','route':'builtin',
        'configSnapshot':json.loads((ROOT.parents[3]/'config'/'image-generation.json').read_text(encoding='utf-8-sig')),
        'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[x['path'] for x in refs]},
        'actualModel':None,'actualQuality':None,
        'unverifiedReason':'宿主管理，工具未开放 model/quality 选择器，返回未披露可核实的型号和质量。',
        'prompt':job['prompt'],'references':refs,'evidence':{'receipt':job['receipt']},
        'derivedFrom':{'path':str(source),'sha256':native['sha256'],'nativeSize':[img.width,img.height]},
        'operation':{'type':'uniform-full-canvas-export','resize':[960,960],'offset':[32,16],'output':[1024,1024],'perFrameAlignment':False},
        'pivot':[0.5,0.08],'anchorTopLeft':[512,942],
        'visualStatus':job.get('visualStatus','pending'),
    }
    dst=ROOT/'records'/group/f'{index:02}.generation.json'
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(out),'record':str(dst),'native':native,'alpha':canvas.getchannel('A').getextrema(),'bbox':canvas.getchannel('A').getbbox()},ensure_ascii=False))
if __name__=='__main__':main()
