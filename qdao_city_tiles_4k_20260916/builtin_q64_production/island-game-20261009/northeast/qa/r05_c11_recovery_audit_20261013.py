from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sel=read(z/'selection-r05_c11.json');checked=[]
for row in sel['cores']:
 for ident in row:
  if not ident:continue
  p=z/'native'/f'{ident}.png';r=read(p.with_suffix('.png.generation.json'));q=read(z/'qa'/f'{ident}.joins.json')
  assert p.exists() and sha(p)==r['sha256']==q['nativeSha256']
  with Image.open(p) as im:assert im.size==(1254,1254)
  checked.append({'id':ident,'sha256':r['sha256'],'savedReviewStatus':q['status'],'reviewReusable':q['status'].startswith('passed_')})
rec={'tileId':'r05_c11','worker':'repair_recovery','writtenAtUtc':datetime.now(timezone.utc).isoformat(),'selectedCoreCount':len(checked),'selectedChecks':checked,'recoveredUnselected':[{'id':'r05_c11_p01_01_v2','sha256':sha(z/'native/r05_c11_p01_01_v2.png'),'issue':'Lower right planted garden is abruptly clipped where it meets right neighbor paving; top boundary coherent. Preserved as unselected candidate.'}],'nextId':'r05_c11_p01_01_v3','newNetworkCallState':'in_flight','formalAccepted':False,'globalProgressModified':False}
p=z/'qa/r05_c11-recovery-audit-20261013.json'
assert not p.exists();p.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selectedCoreCount':len(checked),'allPriorChecksReusable':all(x['reviewReusable'] for x in checked)}))
