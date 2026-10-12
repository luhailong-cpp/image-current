"""Explicit current ownership; obsolete duplicate NE/NW rows remain historical."""
from pathlib import Path
import json

ORDER = ['inventory-root.json', 'inventory-hit.json', 'inventory-cast.json',
         'inventory-run-north.json', 'inventory-run-ne-cast.json', 'inventory-run-nw-finish.json']

def current_slots(root):
    chosen = {}
    for name in ORDER:
        p = Path(root) / name
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding='utf-8-sig'))
        for frame in doc.get('frames', []):
            key = (frame['action'], frame['direction'], frame['frame'])
            chosen[key] = (name, frame)
    return [chosen[k] for k in sorted(chosen)]
