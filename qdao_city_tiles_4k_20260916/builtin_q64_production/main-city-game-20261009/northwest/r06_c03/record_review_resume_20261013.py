from pathlib import Path
import sys, importlib.util
T=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('p',T.parent/'production_v2.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
identifier,status,note=sys.argv[1:4]
out=T/'qa/source-review'/identifier
m=p.read(out/'manifest.json')
r=dict(status=status,source=m['source'],actuallyViewed=True,viewDetail='original',viewedNative=True,crops=[dict(file=x['file'],sha256=x['sha256'],actuallyViewed=True) for x in m['crops']],notes=note,fullTileInternalQA=False,formalAccepted=False,reviewer='/root/continue_r06_c03')
p.write_json(out/'review.json',r)
print(p.record_selection('r06_c03',identifier[:6],identifier,note,str(out/'review.json')))
