from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=B/'migration-preserved-external-20261011/manifest.json';d=json.loads(p.read_text(encoding='utf-8'))
q=json.loads((B/'r11_c06/repairs-restored-20261011/G01.qa.json').read_text(encoding='utf-8'))['nativeOrigin']
native=Path(q['file']);assert sha(native)==q['sha256']
matched=0
for e in d['sourceFiles']:
    if Path(e['originalExternalPath']).name=='exec-3253350f-1689-4135-af85-421029d4f149.png':
        dest=p.parent/(q['sha256']+'.png')
        if not dest.exists():shutil.copy2(native,dest)
        assert sha(dest)==q['sha256']
        e.update(workspaceCopy=str(dest),sha256=q['sha256'],bytes=dest.stat().st_size,copyVerified=True,recoveredFromRecordedWorkspaceNative=str(native),recoveryEvidence=str(B/'r11_c06/repairs-restored-20261011/G01.qa.json'),historicalExternalPathMissing=True)
        matched+=1
assert matched==1
d['unpreservedExternalImages']=[e['originalExternalPath'] for e in d['sourceFiles'] if not e.get('copyVerified')]
d['savedAtUtc']=datetime.now(timezone.utc).isoformat();d['missingExternalPathsRecoveredFromWorkspace']=1
atomic_json(p,d);print(json.dumps({'historicalMissingRecovered':matched,'unpreserved':d['unpreservedExternalImages'],'sourceBytes':sum(e.get('bytes',0) for e in d['sourceFiles'])}))

