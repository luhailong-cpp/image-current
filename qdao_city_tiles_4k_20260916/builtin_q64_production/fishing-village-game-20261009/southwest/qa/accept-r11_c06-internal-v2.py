import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
trp=z/'qa/repair-r11_c06-internal-v2-trace.json';tr=read(trp);q=read(z/'qa/repair-r11_c06-internal-v1-qa-index.json')
v1=np.array(Image.open(q['context']['path']));v2=np.array(Image.open(tr['context']['path']));mask=np.load(z/'qa/repair-r11_c06-internal-v2-context-source-ids.npy');oldmask=np.load(z/'qa/repair-r11_c06-internal-v1-context-source-ids.npy');affected=(mask==4)|(oldmask==4);assert np.array_equal(v1[~affected],v2[~affected])
ap=z/'qa/r11_c06-internal-visual-audit-v2.json';assert not ap.exists()
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c06','status':'passed','scope':'internal seams only; north and other external joins pending','base39Viewed':ref(z/'qa/r11_c06-internal-visual-audit-v1.json'),'repairTrace':ref(trp),'nativeCompositeRepairRegionsViewed':q['repairQa'],'postBoundaryRevisionViewed':ref(z/'qa/repair-r11_c06-internal-v2-D-result-native.png'),'qaMethod':'Original 39 native seam crops inspected; each of five complete 1254 repair regions and all four boundaries directly re-inspected. Revised D full region inspected. All changed pixels lie inside these inspected native regions; all other pixels inherit initial QA. The 23 auxiliary affected seam crops are saved, not claimed separately viewed.','issuesResolved':['A table rim and ground shadow zipper','B bowl and tabletop brightness join','C clipped pebble at stair foot','D tall wooden post horizontal band and local mask endpoints','E rear table leg brown band'],'mechanicalValidation':tr['validation'],'v1ToV2OnlyDRegionChanged':True,'candidate':tr['candidate'],'context':tr['context']}
prod.write(ap,audit)
l=read(z/'current-tile-ledger.json')
for e in l['tiles']:
 if e['tile']=='r11_c06':e.update({'current4096':tr['candidate'],'nativeContext':tr['context'],'sourceTrace':ref(trp),'internalQa':'passed','internalAudit':ref(ap),'knownSharedEdgesQa':'pending','artExport':False})
prod.write(z/'current-tile-ledger.json',l)
print(json.dumps({'audit':ref(ap),'context':tr['context']}))
