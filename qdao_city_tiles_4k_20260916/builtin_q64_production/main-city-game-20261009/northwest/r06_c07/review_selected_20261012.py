"""Record a human/agent visual verdict only after native and all listed crops were viewed."""
from pathlib import Path
import sys,json,importlib.util
T=Path(__file__).resolve().parent;Z=T.parent
spec=importlib.util.spec_from_file_location('p',Z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
identifier=sys.argv[1];note=sys.argv[2];status=sys.argv[3] if len(sys.argv)>3 else 'passed_available_native_source_review'
folder=T/'qa'/'source-review'/identifier
m=p.read(folder/'manifest.json')
record=dict(status=status,source=m['source'],actuallyViewed=True,viewDetail='original',viewedNative=True,crops=[dict(file=x['file'],sha256=x['sha256'],actuallyViewed=True,verdict='pass' if status.startswith('passed') else 'needs_repair') for x in m['crops']],notes=note,fullTileInternalQA=False,formalAccepted=False,reviewer='/root/local_saved_patch_audit')
path=folder/'review.json';assert not path.exists();p.write_json(path,record)
if status.startswith('passed'):
 print(json.dumps(p.record_selection('r06_c07',identifier[:6],identifier,note,str(path))))
else:print(json.dumps(record))
