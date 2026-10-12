from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SPECS={'run':(['N','NE','E','SE','S','SW','W','NW'],16,None),'hit':(['E','W'],6,40),'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
P=ROOT/'preview'; P.mkdir(exist_ok=True)
records=[]
timing_path=ROOT/'run-timing.json'
run_timing=json.loads(timing_path.read_text(encoding='utf-8'))
for action,(dirs,count,ms) in SPECS.items():
    for direction in dirs:
        paths=[ROOT/action/direction/f'{i:02d}.png' for i in range(1,count+1)]
        if not any(p.exists() for p in paths): continue
        cols=4;size=256; sheet=Image.new('RGB',(cols*size,((count+cols-1)//cols)*(size+24)),(231,234,233));d=ImageDraw.Draw(sheet)
        sources=[];anim=[]
        for i,p in enumerate(paths):
            x=(i%cols)*size;y=(i//cols)*(size+24)
            d.text((x+8,y+size+4),f'{action}/{direction}/{i+1:02d}'+('' if p.exists() else ' MISSING'),fill=(35,53,51))
            if p.exists():
                im=Image.open(p).convert('RGBA'); thumb=im.resize((size,size),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
                bg=Image.new('RGB',(512,512),(235,237,233));s=im.resize((512,512),Image.Resampling.LANCZOS);bg.paste(s,(0,0),s);anim.append(bg)
                sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        name=f'{action}-{direction}-sheet.jpg';sheet.save(P/name,quality=94)
        rec={'file':f'preview/{name}','operation':'labelled contact sheet; preview only; missing slots remain empty','sources':sources}
        if len(anim)==count:
            for suffix,speed in [('normal',1),('slow',4)]:
                durations=run_timing['directions'][direction]['durationsMs'] if action=='run' else [ms]*count
                durations=[x*speed for x in durations]
                target=P/f'{action}-{direction}-{suffix}.webp';anim[0].save(target,save_all=True,append_images=anim[1:],duration=durations,loop=0,lossless=True)
                records.append({'file':target.relative_to(ROOT).as_posix(),'operation':'preview compositing and 512px whole-canvas downsample','durationsMs':durations,'cycleMs':sum(durations),'sources':sources,'visualPassNotImplied':True})
        records.append(rec)
(P/'provenance.json').write_text(json.dumps({'recordedAt':datetime.now(timezone.utc).isoformat(),'files':records},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'previewFiles':len(records)}))

