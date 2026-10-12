from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R/'full-limb-review-20261004'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected={}
for p in W.glob('*/selection.json'):
    for slot,value in load(p).get('slots',{}).items():
        assert slot not in selected,slot
        selected[slot]=value if isinstance(value,str) else value.get('file') or value.get('path')
data=load(R/'delivery-current.json');data.update(orders={},runFrameMs=60,runCycleMs=960,phaseWeightsApplied=False)
try:font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
except OSError:font=ImageFont.load_default()
for group,frames in data['groups'].items():
    for f in frames:
        slot=group+'/'+str(f['frame']).zfill(2)
        file=selected.get(slot,f['file']);f['candidateUrl']='../'+file+'?v='+sha(R/file)[:12]
        f['sha256']=sha(R/file)
for group in ['run/E','run/W','run/NW','run/SW']:
    frames=data['groups'][group]
    for start in [0,8]:
        canvas=Image.new('RGB',(4*384,2*420),'#e9e8e1');draw=ImageDraw.Draw(canvas);inputs=[]
        for j,f in enumerate(frames[start:start+8]):
            slot=group+'/'+str(f['frame']).zfill(2);file=selected.get(slot,f['file']);p=R/file
            im=Image.open(p).convert('RGBA').resize((384,384),Image.Resampling.LANCZOS)
            x=j%4*384;y=j//4*420;canvas.paste(im,(x,y),im)
            draw.text((x+8,y+389),slot+(' NEW' if slot in selected else ' current'),font=font,fill='#263b34')
            inputs.append({'slot':slot,'file':file,'sha256':sha(p),'generationRecord':file+'.generation.json'})
        p=W/(group.replace('/','-')+f'-selected-{start+1:02}-{start+8:02}.jpg')
        canvas.save(p,quality=95)
        write(Path(str(p)+'.generation.json'),{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'operation':'whole-canvas fixed-grid proposed sequence visual inspection; no sprite editing','derivedFrom':inputs})
template=(R/'tools/uniform-player.html').read_text(encoding='utf-8')
template=template.replace('正在参照已确认的弓足少女逐向修正，图片仍在复查。','在制修稿联审：仅已选新稿临时覆盖，正式成品尚未统一发布。')
(W/'selection-preview.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__RUN_ONLY__','true'),encoding='utf-8')
print(json.dumps({'selected':len(selected),'reviewSheets':8,'preview':'full-limb-review-20261004/selection-preview.html'}))
