import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
p='c04-hardseam-central-r12c03-v01'
r=load(ROOT/'qa'/f'{p}-report.json')
assert r['validation']['mismatchedPixels']==0
a={**r['outputs'][0], 'record':str(ROOT/'qa'/f'{p}-report.json'),'sourceReport':str(ROOT/'qa'/f'{p}-report.json'),'sourceIdMask':str(ROOT/'qa'/f'{p}-source-id-mask.png'),'nativeSourceCount':16,'nativePixelsVerified':True,'internalPassed':False,'internalTileSeamsPassed':False,'formalAccepted':False,'allOuterTileEdgesPassed':False,'internalStatus':'24 native segments inspected; two localized timber discontinuities pending repair','pendingRepairs':[{'globalArea':[11230,48120,11310,48200],'issue':'small horizontal board groove discontinuity at V3 row4'},{'globalArea':[10540,48070,10690,48160],'issue':'jagged highlight near H3 column3 timber groove'}]}
assert hashfile(a['path'])==a['sha256']
d=load(ROOT/'qa/expansion-central-worker-map.json')
d['candidateArtifacts']['r12_c03']=a
d['updatedAtUtc']=now()
dump(ROOT/'qa/expansion-central-worker-map.json',d)
dump(ROOT/'qa/central-r12c03-review-20261013.json',{'recordedAtUtc':now(),'basis':'continued root visual inspection from saved conversation; all24 native segments inspected before restart','artifact':a,'splitChecked':'MAP_PARALLEL_SPLIT_20261013.json; no island southwest coordinate allocation conflict'})
print('r12_c03 complete candidate retained; internal and formal acceptance false')
