from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[2];T=B/'r11_c07';patch='p02_04';at='frame-aligned-20261013c-v03'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
source=Path(r'C:\Users\luyua\.codex\generated_images\01a1360d-254b-78b0-ba57-d65ad046ef63\exec-da6067c9-b3d9-4aea-97fb-0f55fc5c63f6.png');guide=T/'guides/p02_04.layout-only.png';base=T/'pipeline/prompts/p02_04.continue-20261013c-v02.request.json'
native=Image.open(source).convert('RGB');seed=native.copy()
seed.paste(Image.open(guide).crop((1000,728,1254,1254)),(1000,728))
seed.paste(native.crop((1103,840,1156,1254)),(1000,840))
seed.paste(native.crop((1187,840,1191,1254)),(1053,840))
sp=T/f'pipeline/guides/{patch}.{at}.coordinate-guidance.png';assert not sp.exists();seed.save(sp)
d={'source':{'file':str(source),'sha256':sha(source)},'approvedGuide':{'file':str(guide),'sha256':sha(guide)},'operations':[{'source':str(guide),'crop':[1000,728,1254,1254],'target':[1000,728,1254,1254]},{'source':str(source),'crop':[1103,840,1156,1254],'target':[1000,840,1053,1254]},{'source':str(source),'crop':[1187,840,1191,1254],'target':[1053,840,1057,1254]}],'purpose':'coordinate guidance only, exact crop/paste without resampling; never final art','resampling':False,'gameArt':False}
sp.with_name(sp.name+'.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=read(base);prompt="""Precise-object-edit. Output one opaque native1254-square finished PNG, same crop/camera. Image1 coordinate guide now places existing rectangular road frame at its correct original position. Keep upper grey strips y255-355 and620-727 unchanged across full width. Third grey horizontal strip y840-940 turns DOWN at x1000-1057: inner edge x1000, outer edge x1057, straight vertical to bottom border. Keep this exact turn coordinate and narrower projected vertical width. The horizontal third band ends at outer edge x1057, pale floor fills all area to its right, no remaining band/column at x1100-1190. Regenerate the coarse lower-right ground in Image1 into genuinely new native hand-painted stone, retaining original sparse floor seams. Preserve exact left native band heights and top lines. Image5 is exact original layout, confirms the right turn near x1000-1055, geometry only. No extra strip, cap, curve, vertical divider at x230, raised curb, step, column, prop, motif or text. Broad quiet grey/ivory stone with sparse fine brushwork and restrained variation, no cell grid or cracks. Images2/3/4 approved city geometry, daylight clean stone and Daoist art. The composed guide is never final art; output must be new model-rendered1254."""
pp=T/f'pipeline/prompts/{patch}.{at}.prompt.txt';rp=T/f'pipeline/prompts/{patch}.{at}.request.json';assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),neighborSources=[],explicitRefinementOf={'file':str(base),'sha256':sha(base)},cornerTreatment={'bothSourcesPresent':False,'reason':'Explicit right frame coordinate correction, final must be new imagegen'})
r['references'][0]={'file':str(sp),'sha256':sha(sp),'role':'nonfinal coordinate guidance: right frame1000-1057'};r['references'].append({'file':str(guide),'sha256':sha(guide),'role':'exact original projected frame corner geometry only'});r['referenced_image_paths']=[q['file'] for q in r['references']]
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(rp),'seed':str(sp)},ensure_ascii=False))

