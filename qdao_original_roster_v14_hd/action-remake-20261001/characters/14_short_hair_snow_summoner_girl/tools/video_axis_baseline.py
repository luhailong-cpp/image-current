import av, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
V=Path('C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
out=R/'run/staging'; out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'at':datetime.now(timezone.utc).isoformat(),'status':'reopened_for_video_axis_review','scope':'14 only; reference screenshot mountain guard is not an edit target','video':str(V),'videoSha256':sha(V),'frames':{p.relative_to(R).as_posix():sha(p) for p in sorted((R/'run').glob('*/*.png')) if p.parent.name!='staging'},'preservedPriorAudit':json.loads((R/'audit/final-visual-review.json').read_text(encoding='utf-8-sig')),'segments':[]}
for start in [6.2,8.7,13.7]:
    c=av.open(str(V)); ims=[]; ts=[]
    for fr in c.decode(video=0):
        t=float(fr.time)
        if t<start:continue
        if t>=start+.8:break
        if len(ims)>=16:continue
        im=fr.to_image(); w,h=im.size
        # Same fixed centre crop throughout each contiguous interval; no pose edits.
        im=im.crop((int(w*.42),int(h*.26),int(w*.58),int(h*.65))).resize((240,260))
        ims.append(im); ts.append(t)
    c.close()
    sheet=Image.new('RGB',(960,4*285),(238,238,230)); d=ImageDraw.Draw(sheet)
    for i,(im,t) in enumerate(zip(ims,ts)):
        x=i%4*240;y=i//4*285;sheet.paste(im,(x,y+25));d.text((x+5,y+5),f'{t:.3f}s',fill='black')
    path=out/f'video-axis-reference-{start}.jpg';sheet.save(path,quality=94)
    record['segments'].append({'start':start,'frameTimes':ts,'sheet':path.relative_to(R).as_posix(),'note':'Consecutive decoded source frames, fixed camera crop, reference visibility limited by nameplate.'})
(R/'audit/video-axis-baseline.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'baselineFrames':len(record['frames']),'segments':record['segments']}))
