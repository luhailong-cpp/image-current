import json,sys,hashlib
import pipeline as native_pipeline
from pathlib import Path
ROOT=Path(__file__).resolve().parent
tile=ROOT/sys.argv[1]
sel=tile/'pipeline-selection.json'
d=json.loads(sel.read_text(encoding='utf-8-sig')) if sel.exists() else {}
old=dict(d)
for pair in sys.argv[2:]:
    patch,relative=pair.split('=',1)
    p=(tile/relative).resolve()
    p.relative_to(tile)
    assert p.is_file() and Path(str(p)+'.generation.json').is_file()
    d[patch]=str(p)
receipt={'oldSelection':old,'newSelection':d,'reason':'Select recorded native pixel derivations after local seam QA; full tile acceptance pending'}
sha=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()[:12]
(tile/'receipts'/('derivation-selection-'+sha+'.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8')
native_pipeline.replace_json(sel,d)
print(sha)
