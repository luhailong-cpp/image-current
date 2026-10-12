"""Guide-only provisional west native halo; final source requires later review."""
from pathlib import Path
import importlib.util,json
from PIL import Image
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('w',T/'workflow_actual_boundaries_20261012.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
w.prepare('s04_02','native01','north')
base=T/'layout-only/s04_02_native01.actual-final-guide.png';source=T/'native/s04_01_material03.png';target=T/'layout-only/s04_02_native01.pendingwest-guide.png';image=Image.open(base).convert('RGB')
image.paste(Image.open(source).convert('RGB').crop((1024,0,1254,1254)),(0,0));w.p.save_png(target,image)
w.p.write_json(target.with_suffix('.png.derivation.json'),dict(file=str(target),sha256=w.p.sha(target),base=dict(file=str(base),sha256=w.p.sha(base)),source=dict(file=str(source),sha256=w.p.sha(source),cropLTRB=[1024,0,1254,1254],pasteXY=[0,0],reviewPendingWestTexture=True),role='layout-only with provisional exact native west halo, not production art',gameArt=False,sourceResampled=False))
print(json.dumps(dict(guide=str(target),sourceResampled=False)))
