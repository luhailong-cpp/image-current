from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,copy
R=Path(__file__).resolve().parents[1];W=R/'run-contact-revision-20261004';P=R/'preview/contact-candidate';P.mkdir(exist_ok=True)
d=json.loads((R/'delivery-current.json').read_text(encoding='utf-8'));d=copy.deepcopy(d);d['orders']={}
selected={}
for path in W.glob('*/selection.json'):
    s=json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(s.get('slots'),dict):selected.update(s['slots'])
for group,frames in d['groups'].items():
    for f in frames:
        slot=group+'/'+str(f['frame']).zfill(2)
        if slot not in selected:
            f['candidateUrl']=f['url']+'?v='+f['sha256'][:12];continue
        val=selected[slot];path=val if isinstance(val,str) else val.get('file') or val.get('path')
        src=Path(path);src=src if src.is_absolute() else R/src
        if not src.exists():raise ValueError(str(src))
        im=Image.open(src).convert('RGBA');im=im.resize((1024,1024),Image.Resampling.LANCZOS)
        dest=P/(slot.replace('/','-')+'.png');im.save(dest)
        f['candidateUrl']='contact-candidate/'+dest.name+'?v='+hashlib.sha256(dest.read_bytes()).hexdigest()[:12]
        f['sourceFrame']=f['frame'];f['revisionCandidate']=True
template=(R/'tools/uniform-player.html').read_text(encoding='utf-8')
template=template.replace('正在参照已确认的弓足少女逐向修正，图片仍在复查。','接地复修候选：每个空间位置两帧，同脚连续支撑后交替；仍在逐向复查。')
(R/'preview/contact-revision.html').write_text(template.replace('__DATA__',json.dumps(d,ensure_ascii=False)).replace('__RUN_ONLY__','true'),encoding='utf-8')
for direction in ['N','S']:
    sheet=Image.new('RGB',(1320,1280),'#e9e8e1');draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(d['groups']['run/'+direction]):
        p=(R/'preview'/f['candidateUrl'].split('?',1)[0]).resolve();im=Image.open(p)
        crop=im.crop((335,675,665,975));x=(i%4)*330;y=(i//4)*320;sheet.paste(crop,(x,y),crop)
        draw.line((x,y+267,x+330,y+267),fill='#5e7e68');draw.text((x+10,y+303),f"{direction}/{i+1:02}"+(' revised' if f.get('revisionCandidate') else ''),fill='#21362c')
    sheet.save(W/f'{direction}-feet-candidate.jpg',quality=95)
print(json.dumps({'candidateSlots':list(selected),'runtimeUnchanged':True}))
