from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;d=D/'W01-alpha-v2';old=D/'W01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
p=json.loads((old/'preparation.json').read_text(encoding='utf-8-sig'))
p['priorPreparation']=info(old/'preparation.json');p['alpha']=info(d/'alpha-crop.png');p['fullAlpha']=info(d/'alpha-native-1254.png')
p['version']='W01-alpha-v2-same-native-no-generation';p['status']='mechanical_alpha_reselection_not_new_generation';p['alphaSelection']=info(d/'alpha-selection.json')
p['alphaRule']='Saved original alpha reduced by a minimum-error bottom path and 24px taper; strictly subset of the same native crop. See alpha-selection.json.'
p['preparedAtUtc']=datetime.now(timezone.utc).isoformat()
p['sourceReceipt']=info(next(old.glob('receipt-*.json')))
assert not (d/'preparation.json').exists()
(d/'preparation.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
receipt=next(old.glob('receipt-*.json'));shutil.copyfile(receipt,d/receipt.name)
print(json.dumps(info(d/'preparation.json')))

