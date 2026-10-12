from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(root/'manifest.json')
errors=[]; index=[]
for frame in manifest['frames']:
    rel=frame['file']; output=root/rel
    if not output.exists(): errors.append(f'Missing {rel}'); continue
    derived_path=output.with_suffix('.png.generation.json')
    if not derived_path.exists(): errors.append(f'Missing derivative record {rel}'); continue
    derived=read(derived_path)
    if derived['sha256']!=sha(output): errors.append(f'Output SHA mismatch {rel}')
    native_record_path=root/derived['derivedFrom']['generationRecord']
    native=read(native_record_path)
    source_hash=native.get('sourceSha256',native.get('nativeSHA256',native.get('sha256')))
    if source_hash!=derived['derivedFrom']['sha256']: errors.append(f'Source SHA chain mismatch {rel}')
    source=root/derived['derivedFrom']['file']
    if source.exists() and sha(source)!=source_hash: errors.append(f'Native source SHA mismatch {rel}')
    if not source.exists() and derived['derivedFrom'].get('retained') is not False: errors.append(f'Unexplained missing native {rel}')
    prompt_path=root/native['prompt']
    if not prompt_path.exists(): errors.append(f'Missing prompt {rel}: {prompt_path}')
    evidence=native.get('evidence',{})
    receipt_value=evidence.get('receipt')
    if receipt_value and not (root/receipt_value).exists(): errors.append(f'Missing receipt {rel}: {receipt_value}')
    if not receipt_value: errors.append(f'No receipt pointer {rel}')
    for required in ['configSnapshot','submittedParameters','actualModel','actualQuality','generatedAt','references']:
        if required not in native: errors.append(f'{rel} lacks {required}')
    params=native.get('submittedParameters',{})
    for k in ['model','quality']:
        if k not in params: errors.append(f'{rel} missing null submitted {k}')
    index.append({'file':rel,'sha256':sha(output),'nativeGenerationRecord':native_record_path.relative_to(root).as_posix(),'exportRecord':derived_path.relative_to(root).as_posix(),'prompt':native['prompt'],'receipt':receipt_value,'generatedAt':native.get('generatedAt'),'nativeSHA256':source_hash,'targetModel':native.get('configSnapshot',{}).get('model'),'targetQuality':native.get('configSnapshot',{}).get('quality'),'actualModel':native.get('actualModel'),'actualQuality':native.get('actualQuality')})
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed' if len(index)==68 and not errors else 'incomplete_or_failed','auditedFrameCount':len(index),'expected':68,'errors':errors,'clientStatus':'not_integrated'}
(root/'provenance-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'generation-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
