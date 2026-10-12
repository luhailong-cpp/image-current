from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
rows=[];frames=[];seen={};issues=[]
for n in range(1,17):
    idx=f'{n:02d}'; p=ROOT/'runtime/cast/E'/f'{idx}.png'; im=Image.open(p).convert('RGBA'); a=im.getchannel('A')
    digest=hashlib.sha256(p.read_bytes()).hexdigest(); pixelhash=hashlib.sha256(im.tobytes()).hexdigest()
    recpath=p.with_suffix('.png.generation.json'); rec=json.loads(recpath.read_text(encoding='utf-8-sig'))
    for ref in rec['references']:
        rp=Path(ref['path']); ref['sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
        ref['role']='principal confirmed painting/material style' if 'attribute-panels' in str(rp) else ('original pet identity' if 'qdao_chibi_pets_v1' in str(rp) else ('E direction, proportion and camera anchor' if '/design/' in str(rp).replace('\\','/') else ('starting-frame closure reference' if rp.name=='01.png' and n in (15,16) else 'immediately preceding accepted pose edit target')))
    rec['visualStatus']='all individual frames inspected; full animation playback requires main-window review'
    rec['visualReview']={'singleFrameInspection':True,'direction':'E diagonal front toward lower right','limbs':'two front paws both holding original gourd, two hind feet; one tail','cropping':'ears, tail, paws and spell within canvas','playback':'pending main-window review'}
    recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    corners=[a.getpixel(xy) for xy in [(0,0),(1023,0),(0,1023),(1023,1023)]]
    bbox=a.point(lambda v:255 if v>=32 else 0).getbbox()
    if im.size!=(1024,1024) or min(a.getextrema())!=0 or max(a.getextrema())!=255 or any(corners):issues.append(idx+': size/alpha/corners')
    if pixelhash in seen:issues.append(idx+': duplicate '+seen[pixelhash])
    if digest!=rec['sha256']:issues.append(idx+': record SHA mismatch')
    seen[pixelhash]=idx; frames.append(im)
    rows.append({'frame':n,'file':str(p.relative_to(ROOT)).replace('\\','/'),'durationMs':45,'size':im.size,'mode':'RGBA','alphaExtrema':a.getextrema(),'transparentPixels':a.histogram()[0],'cornersAlpha':corners,'significantAlphaBBox':bbox,'sha256':digest,'pixelSha256':pixelhash,'nativeSize':[rec['derivedFrom']['width'],rec['derivedFrom']['height']]})
sheet=Image.new('RGB',(1280,1376),(46,57,60));draw=ImageDraw.Draw(sheet)
for i,im in enumerate(frames):
    x=(i%4)*320;y=(i//4)*344
    thumb=im.resize((320,320),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
    draw.text((x+12,y+324),f'cast E {i+1:02d} / 16 - 45ms',fill=(244,238,221))
sheet.save(ROOT/'qa/cast-E-contact.png')
for label,duration in [('normal',45),('slow',180)]:
    frames[0].save(ROOT/f'qa/cast-E-{label}.png',save_all=True,append_images=frames[1:],duration=duration,loop=0,disposal=0,blend=0)
report={'group':'cast/E','createdAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'frameCount':16,'normalDurationMs':720,'slowDurationMs':2880,'technicalStatus':'passed' if not issues else 'failed','issues':issues,'individualFrameInspection':'performed on all 16 accepted outputs and rejected 07/09/11 variants','playbackStatus':'pending main-window playback review','clientStatus':'not integrated','notes':['No duplicate images, translations, interpolation or mirrored frame generation used.','One built-in image_gen call per independent frame; corrected 07/09/11 with additional real calls.','Actual model and quality not exposed; both null. Config target gpt-image-2.5-sunburst/max.','Review first-to-last transition and generation-induced minor contour variation in combined playback.','All native outputs 1254x1254, exported uniformly by full-canvas Lanczos resize to 1024x1024 without individual alignment.'],'frames':rows}
(ROOT/'qa/cast-E-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'technicalStatus':report['technicalStatus'],'frames':16,'issues':issues,'bbox':[r['significantAlphaBBox'] for r in rows]},ensure_ascii=False))
