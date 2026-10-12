"""Lossless source audit and uniform whole-canvas export; never creates poses."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ingest(receipt):
    rp=Path(receipt).resolve()
    r=json.loads(rp.read_text(encoding='utf-8-sig'))
    action,direction,number=r['action'],r['direction'],int(r['frame'])
    assert action in ['hit','attack','cast'] and direction in ['E','W']
    src=Path(r['sourcePath'])
    dest=ROOT/'runtime'/action/direction/f'{number:02d}.png'
    dest.parent.mkdir(parents=True,exist_ok=True)
    source_sha=sha(src)
    with Image.open(src) as im:
        native={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode}
        assert im.width==im.height,'Unexpected non-square source, review required'
        assert 'A' in im.getbands(),'Missing alpha requires actual imagegen repair'
        assert im.getchannel('A').getextrema()==(0,255),'Alpha is not genuine or incomplete'
        rgba=im.convert('RGBA')
        if im.size!=(1024,1024):rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
        rgba.save(dest)
    config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
    record={'file':str(dest.relative_to(ROOT)).replace('\\','/'),'sha256':sha(dest),'generatedAt':r.get('completedAt'),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':r['references'],'promptFile':r['promptFile']},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed. Tool exposes no model/quality selector and returns only image_url/output_hint; no reliable model/quality metadata disclosed.','evidence':{'receipt':str(rp.relative_to(ROOT)).replace('\\','/'),'output_hint':r.get('output_hint')},'prompt':r['promptFile'],'references':r['references'],'native':native,'width':1024,'height':1024,'format':'PNG','mode':'RGBA','derivedFrom':{'path':str(src),'sha256':source_sha,'generationReceipt':str(rp.relative_to(ROOT)).replace('\\','/')},'operation':{'type':'whole_canvas_uniform_resize' if native['width']!=1024 else 'RGBA_png_export','from':[native['width'],native['height']],'to':[1024,1024],'perFrameAlignment':False,'cropped':False,'mirrored':False,'generatedMissingFrames':False},'visualStatus':r.get('visualStatus','pending-review')}
    record_path=dest.with_suffix('.png.generation.json')
    if record_path.exists():
        old=json.loads(record_path.read_text(encoding='utf-8-sig'))
        if old.get('sha256')!=record['sha256']:
            history=ROOT/'records'/'superseded';history.mkdir(exist_ok=True)
            old['supersededByReceipt']=str(rp.relative_to(ROOT)).replace('\\','/')
            (history/f'{action}-{direction}-{number:02d}-{old.get("sha256","unknown")[:12]}.generation.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
    record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(dest),'sha256':record['sha256'],'native':native},ensure_ascii=False))
if __name__=='__main__':
    for x in sys.argv[1:]:ingest(x)
