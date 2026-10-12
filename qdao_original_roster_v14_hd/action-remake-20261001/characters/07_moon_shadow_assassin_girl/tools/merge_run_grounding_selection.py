"""Freeze the final reviewed selection against the actual amended run plan."""
from pathlib import Path
from revise_feet_20261003 import ROOT,read,save,sha,now,scoped
REV=ROOT/'review/run-grounding-20261004'
files=['selection-east.json','selection-front.json','selection-north.json','selected-west.json',
       'selection-south.json','selection-southeast.json','selection-root-southeast.json']
selected={};evidence=[]
for file in files:
    d=read(REV/file);assert d['staticReviewed'],file
    values=d['selected'];assert isinstance(values,dict),file
    for key,p in values.items():
        assert key not in selected,key
        native=scoped(p);nr=read(str(native)+'.generation.json');assert sha(native)==nr['sha256']
        selected[key]=native.relative_to(ROOT).as_posix()
    evidence.append({'path':(REV/file).relative_to(ROOT).as_posix(),'sha256':sha(REV/file),'count':len(values)})
plan=read(REV/'plan.json');expected={f for d in plan['directions'] for f in d['necessaryTargetFrames']}
assert set(selected)==expected,(sorted(expected-set(selected)),sorted(set(selected)-expected))
assert len(selected)==plan['totalNecessaryTargetFrames']
save(REV/'selection.json',{'staticReviewed':True,'reviewedAt':now(),'selected':selected,'count':len(selected),
    'scope':'Each native and full candidate sequences reviewed; formal export/playback acceptance still pending',
    'selectionEvidence':evidence,'clientTested':False})
print(f'Frozen{len(selected)} reviewed run-frame choices.')
