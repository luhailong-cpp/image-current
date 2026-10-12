"""Build exact native-pixel QA crops inside this tile only; no verdict implied."""
from pathlib import Path
import argparse
import importlib.util
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v2', HERE.parent / 'production_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
parser = argparse.ArgumentParser()
parser.add_argument('--rows', type=int, required=True)
parser.add_argument('--label', required=True)
args = parser.parse_args()
if args.rows not in range(1, 5):
    raise ValueError('Rows outside tile')
qa = HERE / 'qa' / args.label
qa.mkdir(exist_ok=False)
selection = v2.read(HERE / 'selection.json')
height = args.rows * 1024
art = Image.new('RGB', (4096, height))
sources = []
for row in range(1, args.rows + 1):
    for col in range(1, 5):
        pid = f's{row:02}_{col:02}'
        path = v2.selected_path(HERE, pid, selection)
        proof = v2.validate_native(path, HERE, pid)
        proof.update(id=pid, coreCrop=[115, 115, 1139, 1139], destinationBox=[(col-1)*1024, (row-1)*1024, col*1024, row*1024])
        sources.append(proof)
        with Image.open(path) as im:
            art.paste(im.convert('RGB').crop((115,115,1139,1139)), ((col-1)*1024, (row-1)*1024))
art_path = qa / ('hard-cores-' + str(args.rows) + '-rows.png')
art.save(art_path)
entries = []
def save(name, image, category, coordinate):
    path = qa / (name + '.png')
    image.save(path)
    entries.append(dict(name=name, file=str(path), sha256=v2.sha(path), category=category, coordinate=coordinate, actuallyViewed=False, verdict='pending'))
for row in range(args.rows):
    for col in range(1, 4):
        x = col*1024
        save(f'v-r{row+1}-c{col}', art.crop((x-128, row*1024, x+128, (row+1)*1024)), 'internal-vertical', [x, row*1024])
for row in range(1, args.rows):
    y = row*1024
    for col in range(4):
        save(f'h-r{row}-c{col+1}', art.crop((col*1024, y-128, (col+1)*1024, y+128)), 'internal-horizontal', [col*1024, y])
    for col in range(1, 4):
        x = col*1024
        save(f'j-r{row}-c{col}', art.crop((x-192, y-192, x+192, y+192)), 'internal-junction', [x,y])
neighbors = {}
for side, tile in [('north', 'r06_c06'), ('west', 'r07_c05')]:
    directory = HERE.parent / tile
    neighbor_selection = v2.read(directory / 'selection.json') if (directory / 'selection.json').is_file() else {}
    usable = {}
    for row in range(1,5):
        for col in range(1,5):
            pid = f's{row:02}_{col:02}'
            path = v2.selected_path(directory, pid, neighbor_selection)
            if path.is_file():
                usable[pid] = v2.validate_native(path, directory, pid)
    candidates = []
    for manifest in (directory / 'candidate').glob('*-candidate-*.assembly.json'):
        info = v2.candidate_info(manifest, directory, usable)
        if info and info['usesCurrentSelection']:
            candidates.append(info)
    if not candidates:
        neighbors[side] = dict(status='no-current-complete-candidate', tile=tile)
        continue
    info = sorted(candidates, key=lambda item: item['createdAt'])[-1]
    neighbors[side] = info
    with Image.open(info['file']) as im:
        neighbor = im.convert('RGB')
    if side == 'north':
        for col in range(4):
            crop = Image.new('RGB', (1024,256))
            crop.paste(neighbor.crop((col*1024,3968,(col+1)*1024,4096)), (0,0))
            crop.paste(art.crop((col*1024,0,(col+1)*1024,128)), (0,128))
            save(f'north-c{col+1}', crop, 'external-north', [col*1024,0])
    else:
        for row in range(args.rows):
            crop = Image.new('RGB', (256,1024))
            crop.paste(neighbor.crop((3968,row*1024,4096,(row+1)*1024)), (0,0))
            crop.paste(art.crop((0,row*1024,128,(row+1)*1024)), (128,0))
            save(f'west-r{row+1}', crop, 'external-west', [0,row*1024])
record = dict(tile=HERE.name, createdAt=v2.now(), rows=args.rows, art=dict(file=str(art_path), sha256=v2.sha(art_path), size=list(art.size)), sources=sources, neighbors=neighbors, entries=entries, sourceResampled=False, sourceUpscaled=False, colorChanged=False, blended=False, geometry='Exact source core [115,115,1139,1139] translated at world coordinates', formalAccepted=False)
v2.write_json(qa / 'crops.json', record)
print(json.dumps(dict(directory=str(qa), art=record['art'], cropCount=len(entries), categories={k:sum(e['category']==k for e in entries) for k in sorted({e['category'] for e in entries})}, neighbors=neighbors), indent=2))
