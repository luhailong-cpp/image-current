"""Replace explicitly reviewed action frames; preserve every other runtime PNG byte-for-byte."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,io
from PIL import Image
from export_review_runtime import inspect_png,json_bytes,evidence_bundle
B=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
selection_path=B/'review/full-body-selected-20261005.json'
selection=read(selection_path);m=read(B/'manifest.json')
before_raw=(B/'manifest.json').read_bytes()
assert sha(before_raw)==selection['beforeManifestSha256'],'Runtime selection changed during revision'
rows={f['slot']:f for s in m['sequences'] for f in s['frames']}
now=datetime.now(timezone.utc).isoformat();pending=[];revised=[];newly_exported=[]
for choice in selection['replacements']:
    slot=choice['slot'];f=rows[slot]
    assert slot.split('-')[0] in ('run','hit','attack','cast') and sha((B/f['file']).read_bytes())==f['sha256']==choice['beforeRuntimeSha256']
    native=B/'staging'/f"{choice['key']}.png";raw=native.read_bytes()
    assert sha(raw)==choice['sourceSha256']
    if slot in m.get('fullBodyRevision',{}).get('changedSlots',[]) and f['sourceSha256']==choice['sourceSha256']:
        assert f['sourceFile']==native.relative_to(B).as_posix()
        assert sha(native.with_suffix('.png.generation.json').read_bytes())==choice['sourceGenerationRecordSha256']
        revised.append(slot)
        continue
    source,info=inspect_png(raw,slot)
    out=source.resize((1024,1024),Image.Resampling.LANCZOS) if source.size!=(1024,1024) else source.copy()
    stream=io.BytesIO();out.save(stream,format='PNG');out_raw=stream.getvalue()
    checked,output_info=inspect_png(out_raw,slot+' revised output',native=False);checked.close()
    record_path=native.with_suffix('.png.generation.json');record_raw=record_path.read_bytes();record=read(record_path)
    assert sha(record_raw)==choice['sourceGenerationRecordSha256'],'Source record changed after explicit selection'
    assert record['sha256']==sha(raw) and record['actualModel'] is None and record['actualQuality'] is None
    old_receipt=read(B/f['generationRecord']['file'])
    original={'file':record_path.relative_to(B).as_posix(),'sha256':sha(record_raw),'record':record,
              'availableEvidenceFiles':evidence_bundle(record,native,record_path,B),
              'editInputEvidence':{'file':f['file'],'sha256':f['sha256'],
                  'generationRecord':old_receipt,'historyManifest':'provenance/full-body-revision-20261005/manifest-before.json'}}
    receipt={'file':f['file'],'sha256':sha(out_raw),'exportedAt':now,'width':1024,'height':1024,'mode':'RGBA',
             'derivedFrom':{'file':native.relative_to(B).as_posix(),'sha256':sha(raw),'nativeSize':info['size']},
             'transform':{'type':'uniform_full_canvas_resize','filter':'LANCZOS','crop':None,'translation':[0,0],'alphaCleanup':False},
             **{k:record[k] for k in ['configSnapshot','submittedParameters','actualModel','actualQuality']},
             'sourceGenerationRecord':original}
    receipt_raw=json_bytes(receipt)
    f.update(sha256=sha(out_raw),sourceFile=native.relative_to(B).as_posix(),sourceSha256=sha(raw),
             sourceNativeSize=info['size'],status='needs_review',technicalChecksPassed=True,
             sourceEdgeHighAlphaPixels=info['edgeHighAlphaPixels'],outputEdgeHighAlphaPixels=output_info['edgeHighAlphaPixels'],
             generationRecord={'file':f['file']+'.generation.json','sha256':sha(receipt_raw),'record':receipt})
    pending.extend([(B/f['file'],out_raw),(B/f['generationRecord']['file'],receipt_raw)])
    revised.append(slot);newly_exported.append(slot);source.close();out.close()
assert len(revised)==len(set(revised)) and revised
m['status']='needs_review';m['automaticApproval']=False
m['counts']['visualPassedSlots']=196-len(revised)
affected={s.rsplit('-',1)[0] for s in revised}
if m.get('timingRevision'):affected.update('run-'+d for d in m['timingRevision']['directions'])
m['counts']['dynamicPassedSequences']=14-len(affected)
m['selectionSource']={'file':selection_path.relative_to(B).as_posix(),'sha256':sha(selection_path.read_bytes()),'builtAt':now}
m['acceptance']={'file':None,'sha256':None,'record':{'status':'needs_review','reason':'New full-body revision pending actual playback'}}
prior_revision=m.get('fullBodyRevision')
m['fullBodyRevision']={'exportedAt':now,'changedSlots':revised,'previousManifestSha256':selection['baselineManifestSha256'],'beforeImageExportManifestSha256':sha(before_raw),
                   'priorPartialExport':prior_revision,'newlyExportedSlots':newly_exported,
                   'previousManifest':'provenance/full-body-revision-20261005/manifest-before.json'}
pending.append((B/'manifest.json',json_bytes(m)))
# Validation precedes mutation. Keep old bytes only in memory for I/O rollback.
old={p:p.read_bytes() for p,_ in pending}
try:
    for p,raw in pending:p.write_bytes(raw)
except BaseException:
    for p,raw in old.items():p.write_bytes(raw)
    raise
changed=set(revised)
before=json.loads(before_raw)
for s in before['sequences']:
    for f in s['frames']:
        if f['slot'] not in changed:assert sha((B/f['file']).read_bytes())==f['sha256'],'Untargeted frame changed'
print(json.dumps({'replaced':revised,'newlyExported':newly_exported,'unchanged':196-len(revised),'status':'needs_review'}))
