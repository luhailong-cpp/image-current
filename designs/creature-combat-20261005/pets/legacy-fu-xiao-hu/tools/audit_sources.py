from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def resolve(x):
 p=Path(x);return p if p.is_absolute() else ROOT/p
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
m=read(ROOT/'manifest.json');errors=[];rows=[]
for f in m['frames']:
 record=resolve(f['sourceRecord']);g=read(record);chain=[str(record.relative_to(ROOT))];model=g
 if f.get('sha256')!=sha(ROOT/f['file']):errors.append({'file':f['file'],'error':'manifest SHA mismatch; rebuild delivery before audit'})
 if g.get('sha256')!=sha(ROOT/f['file']):errors.append({'file':f['file'],'error':'export source record SHA mismatch'})
 while 'configSnapshot' not in model:
  nextrec=model.get('derivedFrom',{}).get('generationRecord')
  if not nextrec:errors.append({'file':f['file'],'error':'missing model evidence chain'});break
  np=resolve(nextrec);chain.append(str(np.relative_to(ROOT)));parent=model;model=read(np)
  if parent.get('derivedFrom',{}).get('sha256')!=model.get('sha256'):errors.append({'file':f['file'],'error':'native generation chain SHA mismatch','record':str(np.relative_to(ROOT))})
 for key in ['configSnapshot','submittedParameters','actualModel','actualQuality','unverifiedReason','prompt','references']:
  if key not in model:errors.append({'file':f['file'],'error':'missing '+key})
 prompt=model.get('prompt'); prompt_exists=bool(prompt and resolve(prompt).exists())
 if not prompt_exists:errors.append({'file':f['file'],'error':'prompt file missing'})
 refs=[]
 for ref in model.get('references',[]):
  value=ref.get('path') or ref.get('file')
  if not value:continue
  p=resolve(value);refs.append({'file':value,'role':ref.get('role'),'present':p.exists(),'recordedInputSHA256':ref.get('sha256'),'currentFileSHA256':sha(p) if p.exists() else None,'use':'historical generation input; recorded input SHA may differ from current file after approved editing/calibration; only runtime and design are current dependencies'})
 evidence=model.get('evidence',{}); receipt=evidence.get('toolReceipt') or evidence.get('receipt') or model.get('receipt')
 receipt_exists=isinstance(receipt,dict) or bool(isinstance(receipt,str) and resolve(receipt).exists())
 if not receipt_exists:errors.append({'file':f['file'],'error':'receipt evidence missing'})
 rows.append({'file':f['file'],'sha256':sha(ROOT/f['file']),'generationChain':chain,'target':model.get('configSnapshot'),'submittedModel':model.get('submittedParameters',{}).get('model'),'submittedQuality':model.get('submittedParameters',{}).get('quality'),'actualModel':model.get('actualModel'),'actualQuality':model.get('actualQuality'),'unverifiedReason':model.get('unverifiedReason'),'prompt':prompt,'receiptEvidence':receipt,'references':refs})
report={'auditedAt':datetime.now(timezone.utc).isoformat(),'expected':68,'actual':len(rows),'passed':not errors and len(rows)==68,'errors':errors,'modelEvidenceInterpretation':'All actualModel/actualQuality values remain unconfirmed; no API/CLI used','frames':rows}
(ROOT/'records/source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(rows),'errors':errors},ensure_ascii=False))
