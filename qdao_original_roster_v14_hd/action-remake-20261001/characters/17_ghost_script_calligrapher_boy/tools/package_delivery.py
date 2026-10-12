"""Bundle validated final runtime assets and portable preview, without source images."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json
B=Path(__file__).resolve().parents[1]
M=json.loads((B/'manifest.json').read_text(encoding='utf-8'))
assert M['status'] in ('passed','ready_with_review_limit') and M['counts']['exportedRuntimeSlots']==196
if M['status']=='ready_with_review_limit':
    assert M['acceptance']['record']['dynamicApproval']=='incomplete' and M['acceptance']['record']['browserAccessLimit']
verification=json.loads((B/'review/final-package-verification.json').read_text(encoding='utf-8'))
cleanup=json.loads((B/'cleanup-report.json').read_text(encoding='utf-8-sig'))
manifest_sha=hashlib.sha256((B/'manifest.json').read_bytes()).hexdigest()
assert verification['status']=='passed' and verification['manifestSha256']==manifest_sha
assert verification['acceptanceSha256']==hashlib.sha256((B/'acceptance.json').read_bytes()).hexdigest()
assert cleanup['status']=='completed' and cleanup['manifestSha256']==manifest_sha
files=list((B/'runtime').rglob('*'))
files=[p for p in files if p.is_file()]
files += [B/p for p in ['manifest.json','acceptance.json','DELIVERY.md','STATUS.md',
    'cleanup-report.json','animation-timing.json','preview/delivery.html','preview/delivery-data.json',
    'preview/run-current-960ms.webp','preview/run-current-960ms.json',
    'review/final-package-verification.json','review/final-sequence-review.json',
    'review/contact-pairs-current-20261004.json','preview/manifest-preview.json']]
selection=B/M['selectionSource']['file']
if selection not in files:files.append(selection)
if (B/'review/axis-revision-state.json').exists():
    files += [B/'review/axis-revision-state.json',B/'review/axis-video/observations.json',B/'review/axis-playback-review.json']
    files += list((B/'provenance/axis-revision-20261004').glob('*.json'))
    files += [p for d in (B/'review').glob('axis-*') if d.is_dir()
              for p in d.glob('*.json') if p.name not in ('observations.json',)]
    # Keep the new revision's native-edit lineage as text, including rejected
    # N16v6 when it was the actual input to its corrected successor.
    seen_records=set()
    def add_native_evidence(source):
        native=Path(source)
        native=(native if native.is_absolute() else B/native).resolve()
        if not native.is_relative_to((B/'staging').resolve()):return
        record_path=native.with_suffix('.png.generation.json')
        if record_path in seen_records:return
        seen_records.add(record_path)
        record=json.loads(record_path.read_text(encoding='utf-8-sig'))
        files.append(record_path)
        for raw in [record.get('prompt'),*record.get('evidence',{}).values()]:
            if not isinstance(raw,str):continue
            candidate=(B/raw).resolve()
            if candidate.is_relative_to(B.resolve()) and candidate.suffix in ('.json','.txt') and candidate.is_file():
                files.append(candidate)
        for ref in record.get('references',[]):
            if ref.get('path'):add_native_evidence(ref['path'])
    current_revision=M.get('fullBodyRevision') or M.get('axisRevision',{})
    for sequence in M['sequences']:
        for frame in sequence['frames']:
            if frame['slot'] in current_revision.get('changedSlots',[]):
                add_native_evidence(frame['sourceFile'])
    if M.get('fullBodyRevision'):
        files += list((B/'review').glob('full-body-*.json'))
        files += [p for folder in (B/'review').glob('full-body-audit-*') for p in folder.glob('*.json')]
        files += list((B/'provenance/full-body-revision-20261005').glob('*.json'))
        files += list((B/'review').glob('axis-*.json'))
        for dirname in ['run-W-facing-20261005','torso-continuity-E-20261005','cast-E03-path-20261005','run-E11-depth-20261005','run-E08-E10-depth-20261005']:
            files += list((B/'review'/dirname).glob('*.json'))
        files += list((B/'review').glob('*60ms*.json'))
    files=list(dict.fromkeys(files))
assert all(p.is_file() and p.resolve().is_relative_to(B.resolve()) for p in files)
for s in M['sequences']:
    for f in s['frames']:
        assert hashlib.sha256((B/f['file']).read_bytes()).hexdigest()==f['sha256']
out=B/'17-spirit-scribe-actions.zip'
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files): z.write(p,p.relative_to(B).as_posix())
with ZipFile(out) as z:
    assert z.testzip() is None
    assert sum(p.endswith('.png') for p in z.namelist())==196
result={'file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'bytes':out.stat().st_size,'entries':len(files),'runtimePngs':196,
        'clientIntegrated':False,'zipIntegrity':'passed','assetDeliveryStatus':M['status'],'dynamicApproval':M['acceptance']['record']['dynamicApproval']}
(B/'package.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
