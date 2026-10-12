"""Local-index wrapper around the unchanged native tile assembler."""
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import native_tile_candidate as n

original_inspect = n.inspect_sources
local_index = Path(__file__).parent/'r10_c03-worker-map.json'
n.inspect_sources = lambda tile: original_inspect(tile, local_index)
result = n.build_candidate('r10_c03', 'c04-hardseam-r10c03-v01')
print(json.dumps(result, ensure_ascii=False))
