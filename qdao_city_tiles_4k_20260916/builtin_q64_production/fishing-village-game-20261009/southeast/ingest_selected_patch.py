"""Ingest a visually inspected builtin candidate and select its native patch.
This is a candidate selection only; all tile/seam acceptance remains pending.
"""
from pathlib import Path
import sys,json
import tile_native_workflow as wf
tile,pid,version=sys.argv[1:4];T=wf.writable_tile(tile)
receipt=wf.read(T/f'{pid}-{version}.receipt.json')
result=wf.ingest(tile,pid,version,receipt['sourcePath'])
assert result['nativeDimensions']==[1254,1254], 'Native dimensions changed; do not rescale'
p=T/'selected-patches.json'
sel=wf.read(p) if p.exists() else {'tile':tile,'patches':{}}
sel['patches'][pid]=f'native/{pid}-{version}.png'
sel.update(status='native_production_and_internal_QA',internalReady=False,formalAccepted=False)
wf.write(p,sel)
print(json.dumps({**result,'selectedPositions':len(sel['patches'])}))
