import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
idx=read(z/'art-delivery-index.json')
for e in idx['artAccepted']:
 for k in ['file','sourceTrace','artAudit','nativeContext']:
  assert prod.sha(e[k]['path'])==e[k]['sha256'],(e['tile'],k)
resume=read(z/'production-resume-20261012.json')
assert prod.sha(resume['historicalFreeze']['path'])==resume['historicalFreeze']['sha256']
p=z/'delivery-update-20261012-v1.json';assert not p.exists()
prod.write(p,{'createdAtUtc':prod.now(),'status':'production_continues','targetTiles':49,'artExportCoordinates':len(idx['artAccepted']),'newCoordinatesSinceResume':['r10_c03','r10_c07','r11_c06'],'currentArtDeliveryIndex':ref(z/'art-delivery-index.json'),'entries':idx['artAccepted'],'all49Complete':False,'historicalFreezeUnchanged':True,'historicalFreeze':resume['historicalFreeze'],'drawingAssignments':{'root':'r11_c05','stair_rebuild':'r11_c03','finish_r10c05':'r11_c07','art_qa':'r08_c06 south joint, then r08_c05'},'imageWritePolicy':'All new final images versioned; prior images kept; no Git operations','builtinImageGenerationOnly':True})
resume['updatedAtUtc']=prod.now();resume['breakpoints']={'root':'r11_c05 6/16 unique native slots; next wave and width correction in progress','stair_rebuild':'r11_c03 lower rows','finish_r10c05':'r11_c07 lower rows then latest four-tile joint','art_qa':'r08_c06 south joint final neighbor reconciliation then r08_c05'};resume['latestDeliveryUpdate']=ref(p);prod.write(z/'production-resume-20261012.json',resume)
print(json.dumps({'verifiedEntries':len(idx['artAccepted']),'deliveryUpdate':ref(p),'historicalFreezeUnchanged':True}))

