"""Tile-only request/receipt helpers; image generation stays in built-in tool."""
from pathlib import Path
import json,sys,importlib.util
T=Path(__file__).resolve().parent;Z=T.parent
spec=importlib.util.spec_from_file_location('p',Z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
if sys.argv[1]=='request':
 identifier=sys.argv[2];params=p.read(T/'planned'/(identifier+'.parameters.json'))
 print(json.dumps(p.record_request('r06_c07',identifier,T/'planned'/(identifier+'.parameters.json'))))
elif sys.argv[1]=='ingest':
 identifier=sys.argv[2];host=sys.argv[3]
 hint=sys.argv[4] if len(sys.argv)>4 else ''
 receipt=T/'receipts'/(identifier+'.tool.json')
 p.write_json(receipt,dict(tool='image_gen.imagegen',output_hint=hint,sourceHostFile=host,mediaStoredAsNativeHostFile=True,actualModel=None,actualQuality=None))
 print(json.dumps(p.ingest('r06_c07',identifier,host,receipt)))
