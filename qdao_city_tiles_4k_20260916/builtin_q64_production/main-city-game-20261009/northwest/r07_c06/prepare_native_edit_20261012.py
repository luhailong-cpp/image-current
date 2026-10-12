"""Build only an edit guide: original native center and exact neighbor bands."""
from pathlib import Path
from PIL import Image
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v2',HERE.parent/'production_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
p = argparse.ArgumentParser()
p.add_argument('--id',required=True)
p.add_argument('--source',required=True)
p.add_argument('--anchor-guide',required=True)
p.add_argument('--bands',default='north,west')
args=p.parse_args()
source = Path(args.source)
anchor = Path(args.anchor_guide)
target = Image.open(source).convert('RGB')
guide = Image.open(anchor).convert('RGB')
assert target.size == guide.size == (1254,1254)
bands=[]
for side in args.bands.split(','):
    box = {'north':(0,0,1254,230),'west':(0,0,230,1254)}[side]
    target.paste(guide.crop(box),box[:2])
    bands.append(dict(source=str(anchor),sha256=v2.sha(anchor),sourceBox=list(box),targetBox=list(box),side=side))
out = HERE / 'layout-only' / (args.id + '.native-edit-guide.png')
v2.save_png(out,target)
v2.write_json(out.with_suffix('.png.derivation.json'),
              dict(id=args.id,guide=str(out),sha256=v2.sha(out),purpose='Edit target guide only; not a generated final source',
                   baseNative=dict(file=str(source),sha256=v2.sha(source),sourceBox=[0,0,1254,1254],targetBox=[0,0,1254,1254]),
                   exactNativeAnchorBands=bands,anchorDerivation=str(anchor.with_suffix('.png.derivation.json')),
                   sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False))
print(json.dumps(dict(guide=str(out),sha256=v2.sha(out),bands=bands)))
