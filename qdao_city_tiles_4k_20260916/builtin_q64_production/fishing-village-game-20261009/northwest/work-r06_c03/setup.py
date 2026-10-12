from pathlib import Path
import json,sys
from PIL import Image
sys.dont_write_bytecode=True
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r06_c03';W.mkdir(exist_ok=True)
source=(B/'work-r06_c04/workflow.py').read_text()
source=source.replace("T='r06_c04';OX,OY=12288,20480","T='r06_c03';OX,OY=8192,20480")
source=source.replace("NEIGHBORS=[B/'work-r05_c04/final-v2-20261012/assembly.json']","NEIGHBORS=[B/'work-r05_c03/final-v1/assembly.json',B/'work-r06_c04/final-v2/assembly.json']")
source=source.replace("'guides/r06_c04.layout-only.png'","'guides/r06_c03.layout-only.png'")
(W/'workflow.py').write_text(source,encoding='utf-8')
sys.path.insert(0,str(W));import workflow as f
f.prepare(1,4,0)
con=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
Image.open(con['layoutReference']).transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in [8192,20480,12288,24576]),resample=Image.Resampling.BICUBIC).save(W/'guides/r06_c03.layout-only.png')
for r in range(1,5):
 for c in range(1,5):f.prepare(r,c,0)
out=Image.new('RGB',(1254,1254))
for r in range(1,5):
 for c in range(1,5):out.paste(Image.open(W/'guides'/f'r06_c03_s{r:02d}_s{c:02d}_v00.positional.png').resize((310,310)),((c-1)*314,(r-1)*314))
out.save(W/'guides/planning-16blocks.review-only.png')

