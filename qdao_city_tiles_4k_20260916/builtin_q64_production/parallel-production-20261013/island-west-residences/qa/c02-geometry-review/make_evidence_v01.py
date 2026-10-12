import sys
sys.dont_write_bytecode = True
from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone

B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences')
O=B/'qa/c02-geometry-review/v01'
O.mkdir(parents=True, exist_ok=False)
sources={
 'native02':B/'native/r02_c02_s04_02_a02.png',
 'native03':B/'native/r02_c02_s04_03_a02.png',
 'guide02':B/'guides/r02_c02_s04_02_a02.layout-with-native.png',
 'guide03':B/'guides/r02_c02_s04_03_a02.layout-with-native.png',
 'anchor02':B/'anchors/v01/r03_c02_s01_02_current-derived-v01.png',
 'anchor03':B/'anchors/v01/r03_c02_s01_03_current-derived-v01.png',
 'layout':B.parents[1]/'parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-wall-trees-v6.png'
}
ims={k:Image.open(p).convert('RGB') for k,p in sources.items()}
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'QA only, not generated or final art','sources':{},'outputs':[]}
for k,p in sources.items():
 manifest['sources'][k]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(ims[k].size)}
def save(im,name,description,**details):
 p=O/name
 im.save(p)
 manifest['outputs'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'description':description,**details})

# Honest hard core-boundary ownership at global x=6144; no seam optimization or blending.
pair=Image.new('RGB',(2278,1254))
pair.paste(ims['native02'].crop((0,0,1139,1254)),(0,0))
pair.paste(ims['native03'].crop((115,0,1254,1254)),(1139,0))
save(pair.crop((895,0,2095,1254)),'02-03-core-boundary-100pct.png','100 percent source pixels, core boundary x=6144 at local x=244',globalBox=[5900,7053,7100,8307],resampled=False)
overlap=Image.new('RGB',(460,1254))
overlap.paste(ims['native02'].crop((1024,0,1254,1254)),(0,0))
overlap.paste(ims['native03'].crop((0,0,230,1254)),(230,0))
save(overlap,'02-03-overlap-pair-100pct.png','Left:02 east overlap; right:03 west overlap, same global box twice',globalBoxEach=[6029,7053,6259,8307],resampled=False)
save(ims['native03'].crop((350,880,680,1180)),'03-south-step-100pct.png','Candidate03 right edge step near local y=1024; pixel crop only',sourceCrop=[350,880,680,1180],globalBox=[6379,7933,6709,8233],resampled=False)
south=Image.new('RGB',(800,230))
south.paste(ims['native03'].crop((300,1024,700,1254)),(0,0))
south.paste(ims['anchor03'].crop((300,0,700,230)),(400,0))
save(south,'03-south-overlap-pair-100pct.png','Left:03 south overlap; right:adopted south anchor, same global box twice',globalBoxEach=[6329,8077,6729,8307],resampled=False)
crop=ims['layout'].crop((124,148,159,186))
save(crop,'approved-pommel-layout-native35x38.png','Approved layout geometry crop at its original pixel size; not native production art',sourceCrop=[124,148,159,186],resampled=False)
save(crop.resize((700,760),Image.Resampling.NEAREST),'approved-pommel-layout-nearest20x-QA-ONLY.png','20x nearest-neighbor display for geometry inspection only, never final art',sourceCrop=[124,148,159,186],resampled=True)
(O/'evidence-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'outputDirectory':str(O),'outputs':manifest['outputs']},ensure_ascii=False))
