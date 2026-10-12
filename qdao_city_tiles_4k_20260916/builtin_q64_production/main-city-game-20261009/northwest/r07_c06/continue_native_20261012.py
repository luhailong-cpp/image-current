"""Scoped native production helper. Never calls a paid API or updates zone progress."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('northwest_production_v2', HERE.parent / 'production_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['request', 'ingest', 'select'])
parser.add_argument('--patch', required=True)
parser.add_argument('--version', default='resume01')
parser.add_argument('--description', default='Continue large diagonal pale ivory and gray stone slabs across the unfinished center and bottom, joining the visible grout ends without jumps, forks, or extra small slabs. The whole target is flat paving, no walkway or building.')
parser.add_argument('--source')
parser.add_argument('--receipt')
args = parser.parse_args()
pid = v2.patch_id(args.patch)
identifier = pid + '_' + args.version
if args.command == 'request':
    existing_guide = HERE / 'layout-only' / (identifier + '.continuation-guide.png')
    if existing_guide.is_file():
        derivation = v2.read(existing_guide.with_suffix('.png.derivation.json'))
        if v2.sha(existing_guide) != derivation['sha256']:
            raise RuntimeError('Existing guide hash differs')
        guide = {'guide': str(existing_guide), 'missingNeighborSlots': derivation['missingNeighborSlots'], 'references': derivation['nativeNeighbors']}
    else:
        guide = v2.prepare(HERE.name, pid, args.version, 'north,west')
    if guide['missingNeighborSlots']:
        raise RuntimeError('Missing native anchors: ' + str(guide['missingNeighborSlots']))
    contract = v2.load_contract()
    prompt = ('Use case: stylized-concept. Complete IMAGE1 exact-coordinate target as opaque native1254x1254 game pavement artwork. '
              'The SHARP top230px and left230px are actual finished native neighbors: preserve their geometry, colors, narrow brown grout, cream bevel, diagonal angle and scale exactly. '
              + args.description + ' '
              'Match the sharp anchor material as gently mottled painted stone with its fine subdued diamond surface pattern. '
              'The blurry center only locates pavement, never copy blur as final. IMAGE2 city daylight context; IMAGE3 material quality; IMAGE4 Q Daoist painted style only, exclude text/UI/people/night. '
              'Keep fixed scale and crop, bright daylight, no recentering, no new objects, raised edges, grass, cracks, clutter, border, watermark or grain.')
    parameters = {'prompt': prompt, 'referenced_image_paths': [guide['guide'].replace('\\', '/'), contract['layoutReference'], contract['detailStyleReference'], contract['primaryStyleReference']], 'transparent_background': False}
    request_args = HERE / 'requests' / (identifier + '.args.json')
    v2.write_json(request_args, parameters)
    evidence = v2.record_request(HERE.name, identifier, str(request_args))
    print(json.dumps({'parameters': parameters, 'evidence': evidence, 'guide': guide['guide'], 'anchors': len(guide['references'])}, ensure_ascii=False))
elif args.command == 'ingest':
    print(json.dumps(v2.ingest(HERE.name, identifier, args.source, args.receipt), ensure_ascii=False))
else:
    print(json.dumps(v2.record_selection(HERE.name, pid, identifier, 'Native output visually reviewed for continuation geometry and daylight material; full hard-core seam QA pending'), ensure_ascii=False))
