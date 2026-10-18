from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
B=Path(__file__).resolve().parents[2];T=B/'r11_c07';patch='p02_03';at='layout-band3-anchored-20261013c-v03'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
source=T/'refinement/versions/layout-band3-20261013c-v02/p02_03.png'
preband=T/'native/p02_03.png'
left=T/'refinement/versions/layout-band3-20261013c-v01/p02_02.png'
for p in [source,preband,left]:assert Image.open(p).size==(1254,1254)
seed=Image.open(source).convert('RGB')
seed.paste(Image.open(preband).crop((0,840,1254,1044)),(0,840))
seed.paste(Image.open(source).crop((0,910,1254,1010)),(0,840))
seed.paste(Image.open(left).crop((1024,0,1254,1254)),(0,0))
sp=T/f'pipeline/guides/{patch}.{at}.native-coordinate-guide.png';assert not sp.exists();seed.save(sp)
d={'source':{'file':str(source),'sha256':sha(source)},'previousTwoBandNative':{'file':str(preband),'sha256':sha(preband)},'leftSelectedNative':{'file':str(left),'sha256':sha(left)},'operations':[{'source':str(preband),'crop':[0,840,1254,1044],'target':[0,840,1254,1044]},{'source':str(source),'crop':[0,910,1254,1010],'target':[0,840,1254,940]},{'source':str(left),'crop':[1024,0,1254,1254],'target':[0,0,230,1254]}],'purpose':'mechanical native coordinate guidance only for subsequent imagegen; never selected final art','resampling':False,'colorAdjustment':False,'finalArt':False}
sp.with_name(sp.name+'.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=T/'pipeline/prompts/p02_03.layout-band3-20261013c-v02.request.json';r=read(base)
prompt="""Precise-object-edit. Produce one opaque native1254x1254 finished PNG matching Image1 exact composition. Image1 is a coordinate guidance assembled only from existing native crops, not final art. Three flat horizontal blue-grey paving strips are now visibly located at y255-355, y620-727, and y840-940. Keep ALL three strips at these exact heights and widths across the entire image. The bottom of band3 is y940, ordinary pale paving begins immediately below; no band or extra ivory strip at y1010/1050. Smoothly redraw the small pasted material transitions with genuinely new native hand-painted detail, preserving every straight band boundary and surrounding slab line position. Preserve exact left230 native band height, scale and lighting; x230 is not a grout divider. No recenter, resize, redesign, new glyph, extra band, curve, raised curb or prop. Images2/3/4 approved whole-city geometry, daylight clean pale stone and Daoist hand-painted style. Image5 exact original coarse layout also has three grey strips, only geometry evidence. Quiet broad faces with sparse fine brush marks, no dense cells, noise or marble. Final image must be newly returned by built-in tool, not the coordinate guide pixels reused as a finished asset."""
pp=T/f'pipeline/prompts/{patch}.{at}.prompt.txt';rp=T/f'pipeline/prompts/{patch}.{at}.request.json';assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),neighborSources=[],explicitRefinementOf={'file':str(base),'sha256':sha(base)},cornerTreatment={'bothSourcesPresent':False,'reason':'whole-frame coordinate guidance after independent missing-core work; final must be fresh imagegen'})
r['references'][0]={'file':str(sp),'sha256':sha(sp),'role':'nonfinal exact native coordinate guide with third band at840-940'}
r['referenced_image_paths']=[x['file'] for x in r['references']]
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(rp),'seed':str(sp)},ensure_ascii=False))

