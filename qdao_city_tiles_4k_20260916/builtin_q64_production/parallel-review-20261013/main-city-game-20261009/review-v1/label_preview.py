from review_existing import *
from PIL import ImageDraw, ImageFont

d=read(GROUP/'manifest.json')
with Image.open(d['preview']['file']) as im:
    out=Image.new('RGB',(im.width,im.height+64),(22,38,42))
    out.paste(im,(0,64))
draw=ImageDraw.Draw(out)
font=ImageFont.load_default(size=20)
draw.text((16,9),'PREVIEW ONLY - 18.75% scale; native assembly: 8192 x 12288 pixels',font=font,fill=(241,232,205))
draw.text((16,35),'6 existing 4K composites | r03-r05 / c04-c05 | Local seam pass; full map acceptance pending',font=font,fill=(190,215,208))
p=GROUP/'PREVIEW-ONLY-LABELED-1536x2368.png'
assert not p.exists()
out.save(p)
d['labeledPreview']={'file':str(p),'sha256':sha(p),'pixels':list(out.size),'artScale':0.1875,'previewOnly':True,'headerOutsideArt':True,'productionArt':False}
d['currentRuleAcknowledgement']={'rootInstruction':'D:/work/image/AGENTS.md','sha256':sha('D:/work/image/AGENTS.md'),'readAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'modelPolicy':'2026-10-13 clarification allows existing builtin 2.0 fallback; 2.5 preferred if free/existing route available. No new image generation in this review task.','oldControlSnapshot':'Old AGENTS hash retained only as capture history; policy change does not change stored image pixels.'}
save(GROUP/'manifest.json',d)
print(json.dumps(d['labeledPreview']))
