from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[2];T=B/'r11_c07';at='layout-band3-20261013c-v02';patch='p02_03'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'pipeline/prompts/p02_03.layout-band3-20261013c-v01.request.json';r=read(base)
source=Path(r'C:\Users\luyua\.codex\generated_images\01a1360d-254b-78b0-ba57-d65ad046ef63\exec-5f2be85a-464a-46e2-a4df-b1b2552d77d8.png');left=T/'refinement/versions/layout-band3-20261013c-v01/p02_02.png'
assert Image.open(source).size==Image.open(left).size==(1254,1254)
seed=Image.open(source).convert('RGB');seed.paste(Image.open(left).crop((1024,0,1254,1254)),(0,0))
sp=T/f'pipeline/guides/{patch}.{at}.native-guidance.png';assert not sp.exists();seed.save(sp)
d={'source':str(source),'sourceSha256':sha(source),'leftNative':str(left),'leftSha256':sha(left),'sourceCrop':[1024,0,1254,1254],'targetBox':[0,0,230,1254],'operation':'exact native left strip guidance pasted on rejected native; guide only, never final art','resampling':False,'formalAccepted':False}
sp.with_name(sp.name+'.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prompt="""Precise object edit. Opaque native1254x1254 PNG same crop and camera. Correct ONLY third grey inlay band height. Image1 left230px is exact selected native LEFT neighbor: its third grey band is at y840 to937. The wrong band in the rest of Image1 sits too low at y910-1010. Remove that misplaced band and its extra ivory strip under it. Redraw ONE third band straight across the full width at the exact native left incoming y840-937, with thin ivory edge. No step, slope, taper or discontinuity at x230; x230 is only pasted reference boundary. Match native-left band material and broad block scale. Restore ordinary pale floor below y937, with only original clipped joins; no extra ivory crossbar at y1050. Keep first grey band y255-355 and second y620-727 unchanged. Remove old diamond grout only within corrected third band. Image5 exact original layout also places third stripe near y829-934; match the native neighbour precisely. No new band, ring, ornament, prop or text. Images2/3/4 approved wholecity geometry, clean daylight stone, Daoist style. Genuine new native brushwork, quiet broad faces with sparse variation, no cell noise; never use pasted guide as final art."""
pp=T/f'pipeline/prompts/{patch}.{at}.prompt.txt';rp=T/f'pipeline/prompts/{patch}.{at}.request.json';assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),neighborSources=[],explicitRefinementOf={'file':str(base),'sha256':sha(base)},cornerTreatment={'bothSourcesPresent':False,'reason':'Exact left strip guidance on rejected native edit target'})
r['references'][0]={'file':str(sp),'sha256':sha(sp),'role':'native target with exact corrected left230 guidance, never final art'}
guide=T/'guides/p02_03.layout-only.png';r['references'][4]={'file':str(guide),'sha256':sha(guide),'role':'exact original three-band geometry, guide only'}
r['referenced_image_paths']=[x['file'] for x in r['references']]
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(rp),'seed':str(sp)},ensure_ascii=False))

