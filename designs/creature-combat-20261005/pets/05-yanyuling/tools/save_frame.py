import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('source'); p.add_argument('action'); p.add_argument('direction'); p.add_argument('frame',type=int)
    a=p.parse_args(); src=Path(a.source).resolve()
    dst=ROOT/'runtime'/a.action/a.direction/f'{a.frame:02d}.png'
    dst.parent.mkdir(parents=True,exist_ok=True)
    record_dir=ROOT/'provenance'/a.action/a.direction
    receipt=json.loads((record_dir/f'{a.frame:02d}.receipt.json').read_text(encoding='utf-8-sig'))
    im=Image.open(src); native={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'sha256':digest(src)}
    out=im.convert('RGBA')
    if out.size!=(1024,1024): out=out.resize((1024,1024),Image.Resampling.LANCZOS)
    out.save(dst)
    refs=[]
    for i,ref in enumerate(receipt['submittedParameters']['referenced_image_paths']):
        refs.append({'file':ref,'sha256':digest(ref),'role': ['E identity','W identity','primary painting and material style'][i] if i<3 else 'accepted same-direction continuity reference'})
    data={'file':dst.relative_to(ROOT).as_posix(),'sha256':digest(dst),'generatedAt':receipt['finishedAt'], 'native':native,'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具不开放model/quality选择器，结果未披露实际版本/质量。','evidence':{'receipt':(record_dir/f'{a.frame:02d}.receipt.json').relative_to(ROOT).as_posix(),'toolOutputHint':receipt['output_hint']},'prompt':(record_dir/f'{a.frame:02d}.prompt.txt').relative_to(ROOT).as_posix(),'references':refs,'derivedFrom':{'file':str(src),'sha256':native['sha256'],'sourceRetained':True},'operation':{'name':'whole-canvas uniform resize','from':[native['width'],native['height']],'to':[1024,1024],'perFrameAlignment':False},'visualReview':{'status':'reviewed_generation_output','notes':receipt.get('visualNotes','')}}
    data['visualReview']['status']=receipt.get('visualStatus','reviewed_generation_output')
    dst.with_suffix('.png.generation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(dst),'native':native,'sha256':data['sha256'],'alphaExtrema':out.getchannel('A').getextrema()},ensure_ascii=False))
if __name__=='__main__': main()
