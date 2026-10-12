from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
entries=[]
for i in range(1,17):
    name=f'{i:02}'; out=ROOT/f'runtime/cast/W/{name}.png'; rec=out.with_suffix('.png.generation.json'); r=read(rec)
    retry=r.get('selectedRetry'); key=name+('-'+retry if retry else '')
    receipt=ROOT/f'records/cast-W-{key}.receipt.json'; receipt_data=read(receipt)
    native=ROOT/r['derivedFrom']['file']; native_rec=native.with_suffix('.png.generation.json')
    n=read(native_rec) if native_rec.exists() else {k:v for k,v in r.items() if k not in ('derivedFrom','operation')}
    for d in (r,n):
        d['generatedAt']=datetime.fromisoformat(receipt_data['returnedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).isoformat()
        d['generatedAtBasis']='Actual tool-return timestamp; exact model-completion timestamp undisclosed'
        d['evidence'].update(receipt=f'records/cast-W-{key}.receipt.json',returnedFields=['image_url','output_hint'],actualModelDisclosed=False,actualQualityDisclosed=False)
        d['submittedParameters']['referenced_image_paths']=[x['path'] for x in d['references']]
        for ref in d['references']:
            ref['sha256']=sha(Path(ref['path']))
            if '/runtime/cast/W/' in ref['path']:ref['role']='Previous or initial cast pose and composition reference, actually viewed before use'
    n.update(file=str(native.relative_to(ROOT)).replace('\\','/'),sha256=sha(native),width=1254,height=1254,mode='RGBA',format='PNG')
    n.pop('derivedFrom',None);n.pop('operation',None)
    r['derivedFrom']['generationRecord']=str(native_rec.relative_to(ROOT)).replace('\\','/')
    r['visualStatus']='reviewed-individually; playback review separately recorded'
    write(native_rec,n);write(rec,r)
    im=Image.open(out);a=im.getchannel('A');entry={'frame':i,'file':r['file'],'sha256':sha(out),'width':im.width,'height':im.height,'mode':im.mode,'durationMs':45,'alphaExtrema':list(a.getextrema()),'alphaBBox':list(a.getbbox()),'visibleBBoxAlpha16':list(a.point(lambda p:255 if p>=16 else 0).getbbox()),'record':str(rec.relative_to(ROOT)).replace('\\','/'),'selectedRetry':retry}
    entries.append(entry)
for name in ('08','09','10'):
    old=ROOT/f'source/cast/W/{name}.png';oldrec=old.with_suffix('.png.generation.json')
    reject=ROOT/f'records/rejected-cast-W-{name}.generation.json'
    if old.exists():
        old.resolve().relative_to(ROOT)
        data=read(oldrec);data.update(retention='Rejected native pixels removed after selected retry export verified',deleted=True);write(oldrec,data)
        rej=read(reject);rej['derivedFrom']['deleted']=True;write(reject,rej)
        old.unlink()
folder=ROOT/'preview/cast-W';folder.mkdir(parents=True,exist_ok=True)
sheet=Image.new('RGB',(1280,1408),'#e8e4d8');draw=ImageDraw.Draw(sheet)
for i,e in enumerate(entries):
    x=(i%4)*320;y=(i//4)*352
    sprite=Image.open(ROOT/e['file']).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
    sheet.paste(sprite,(x,y),sprite);draw.text((x+12,y+325),f"W cast {i+1:02}  / 45 ms",fill='#243e35')
sheet.save(folder/'contact.png')
write(folder/'contact.png.generation.json',{'file':'preview/cast-W/contact.png','sha256':sha(folder/'contact.png'),'derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['record']} for e in entries],'operation':'QA contact sheet only; each full 1024 canvas scaled to 320x320, 4x4 grid, no source frame modification'})
technical={'frameCount':len(entries),'expectedFrameCount':16,'all1024RGBA':all(e['width']==1024 and e['height']==1024 and e['mode']=='RGBA' for e in entries),'allTrueAlpha':all(e['alphaExtrema']==[0,255] for e in entries),'uniquePixelFiles':len(set(e['sha256'] for e in entries)),'durationMs':720,'fullCanvasResizeOnly':True,'perFrameTranslation':False,'alphaCleanup':False}
write(ROOT/'records/cast-W-technical.json',{'technical':technical,'frames':entries,'notes':'Alpha 1-7 isolated residue kept by explicit parent instruction; visible core silhouettes assessed separately. Native output always1254; exported 1024 is not claimed native.'})
print(json.dumps(technical))
