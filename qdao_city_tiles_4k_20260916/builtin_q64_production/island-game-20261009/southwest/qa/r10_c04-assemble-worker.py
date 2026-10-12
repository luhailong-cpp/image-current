from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import native_tile_candidate as m
original_inspect=m.inspect_sources
m.inspect_sources=lambda tile: original_inspect(tile,ROOT/'qa/r10_c04-worker-map.json')
print(json.dumps(m.build_candidate('r10_c04','c04-hardseam-r10c04-v01')))

