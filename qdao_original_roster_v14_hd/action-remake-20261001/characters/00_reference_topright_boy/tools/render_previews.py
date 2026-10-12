"""Derived contact sheets and exact-timing animated WebP previews; never fills missing frames."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review/animations'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8-sig'))
    groups={}
    for f in manifest['frames']:
        _,action,direction,name=f['file'].split('/')
        groups.setdefault((action,direction),{})[int(name[:2])]=f
    products=[]
    for (action,direction),frames in groups.items():
        count={'run':16,'hit':6,'attack':12,'cast':16}[action]
        durations=[frames[n]['frameDurationMs'] for n in sorted(frames)]
        columns=4 if count>6 else 3;rows=(count+columns-1)//columns
        contact=Image.new('RGB',(columns*256,rows*280),(238,236,230))
        draw=ImageDraw.Draw(contact)
        animation=[];sources=[]
        for n in range(1,count+1):
            x=((n-1)%columns)*256;y=((n-1)//columns)*280
            draw.text((x+8,y+256),f'{action} {direction} {n:02d} - CANDIDATE' if n in frames else f'{n:02d} MISSING',(37,67,56))
            if n not in frames: continue
            f=frames[n];p=ROOT/f['file'];im=Image.open(p).convert('RGBA')
            contact.paste(im.resize((256,256),Image.Resampling.LANCZOS),(x,y),im.getchannel('A').resize((256,256),Image.Resampling.LANCZOS))
            display=Image.new('RGBA',(512,512),(238,236,230,255));display.alpha_composite(im.resize((512,512),Image.Resampling.LANCZOS))
            animation.append(display.convert('RGB'));sources.append({'file':f['file'],'sha256':sha(p),'generationRecord':f['file']+'.generation.json'})
        cp=OUT/f'{action}-{direction}-contact.png';contact.save(cp)
        created=[{'file':cp.relative_to(ROOT).as_posix(),'sha256':sha(cp),'kind':'contact_sheet','missingSlots':[i for i in range(1,count+1) if i not in frames]}]
        if len(frames)==count:
            for label,multiplier in [('normal',1),('slow',4)]:
                p=OUT/f'{action}-{direction}-{label}.webp'
                animation[0].save(p,save_all=True,append_images=animation[1:],duration=[ms*multiplier for ms in durations],loop=0,lossless=True,method=4)
                with Image.open(p) as check:
                    if check.n_frames!=count:raise ValueError(f'Frame count changed: {p}')
                created.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'kind':'animated_preview','frameCount':count,'frameDurationsMs':[ms*multiplier for ms in durations],'cycleDurationMs':sum(durations)*multiplier})
        for item in created:
            item.update({'route':'derived','operation':'complete-canvas uniform display resize, ivory background; no pose synthesis or framewise fitting','derivedFrom':sources,'artApproved':False,'clientIntegrated':False})
            (ROOT/(item['file']+'.derivation.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        products.extend(created)
    (OUT/'index.json').write_text(json.dumps({'status':'candidate_visual_previews_not_acceptance','products':products},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'previewProducts':len(products),'completeSequences':sum(1 for p in products if p['kind']=='animated_preview')//2}))
if __name__=='__main__':main()
