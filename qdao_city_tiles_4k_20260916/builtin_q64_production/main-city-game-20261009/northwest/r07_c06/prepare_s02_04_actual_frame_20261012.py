from pathlib import Path
from PIL import Image
import hashlib,json
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');native=r/'native/s02_04_resume02.png';cand=r/'candidate/r07_c06-candidate-native-roi-v05.png';out=r/'layout-only/s02_04_orphanfix01.actual-1254.png'
a=Image.open(native).convert('RGB');c=Image.open(cand).convert('RGB');a.paste(c.crop((2957,909,4096,2163)),(0,0));assert not out.exists();a.save(out)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.with_suffix('.png.derivation.json').write_text(json.dumps(dict(worldBox=[23437,25485,24691,26739],guideOnly=True,notFinalArt=True,sources=[dict(file=str(native),sha256=sha(native),sourceROI=[1139,0,1254,1254],paste=[1139,0]),dict(file=str(cand),sha256=sha(cand),sourceROI=[2957,909,4096,2163],paste=[0,0])],sourceResampled=False,warped=False,blended=False,recolored=False,pixelOperation='Exact same-world crop/paste: current own candidate covers all1254 rows and first1139 columns; unselected future-east halo retains original native pixels.'),indent=2),encoding='utf-8')
