from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
GROUPS={
'main':('main-city-game-20261009',['northwest','northeast','southwest','southeast','accelerated-yamen-north']),
'village':('fishing-village-game-20261009',['northwest','northeast','southwest','southeast','accelerated-jewelry-approach']),
'island':('island-game-20261009',['northwest','northeast','southwest','southeast','accelerated-northeast-coast'])
}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
zones=[]
audits=[]
for label,(folder,names) in GROUPS.items():
    audit_path=ROOT/'docs'/('map-freeze-audit-'+label+'-20261011.json')
    audit=read(audit_path) if audit_path.is_file() else {}
    entries=audit.get('zones',[])
    if isinstance(entries,dict):entries=[dict(v,zone=k) for k,v in entries.items()]
    audits.append({'map':folder,'path':str(audit_path),'exists':audit_path.is_file(),'sha256':sha(audit_path) if audit_path.is_file() else None})
    for name in names:
        checkpoint=BASE/folder/name/'migration-freeze-20261011.json'
        row={'map':folder,'zone':name,'checkpointPath':str(checkpoint),'checkpointExists':checkpoint.is_file(),'ready':False,'blockers':[]}
        if not checkpoint.is_file():row['blockers'].append('checkpoint_not_yet_saved')
        else:
            row['checkpointSha256']=sha(checkpoint)
            row['checkpointLastWriteUtc']=datetime.fromtimestamp(checkpoint.stat().st_mtime,timezone.utc).isoformat()
        entry=next((x for x in entries if x.get('zone')==name),None)
        if entry is None:row['blockers'].append('independent_audit_pending')
        else:
            row['independentAudit']=str(audit_path)
            row['auditReportedReady']=entry.get('ready') is True
            row['auditEvidence']={'auditPath':str(audit_path),'auditSha256':sha(audit_path),'zoneKey':name,'detailLocation':'zones entry evidence in the independent audit; retained there without duplicating full file inventories'}
            row['auditBlockers']=entry.get('blockers',[])
            expected=entry.get('checkpointSha256')
            row['auditMatchesCurrentCheckpoint']=bool(expected and row.get('checkpointSha256')==expected)
            if not row['auditReportedReady']:row['blockers'].append('audit_has_unresolved_items')
            if not row['auditMatchesCurrentCheckpoint']:row['blockers'].append('current_checkpoint_needs_fresh_audit')
        row['ready']=not row['blockers']
        zones.append(row)
archive_path=ROOT/'designs/user-references/map-style-20261011/archive-index.json'
archive=read(archive_path) if archive_path.is_file() else {}
refs_ok=archive.get('archivedCount')==12 and archive.get('missingOriginalCount')==0
for item in archive.get('files',[]):
    p=ROOT/item.get('workspaceRelativePath','__missing__')
    refs_ok=refs_ok and p.is_file() and sha(p)==item.get('sha256')
result={
'schemaVersion':1,'checkedAtUtc':datetime.now(timezone.utc).isoformat(),
'purpose':'Portable map production freeze readiness for the upload owner to capture final incremental changes. This is NOT a Git push success receipt.',
'expectedZoneCount':15,'checkpointCount':sum(x['checkpointExists'] for x in zones),
'readyZoneCount':sum(x['ready'] for x in zones),
'readyToCaptureFinalIncrement':len(zones)==15 and all(x['ready'] for x in zones) and refs_ok,
'mapArtworkComplete':False,'remoteUploadCompleteClaimed':False,
'uploadOwnerThreadId':'01a11b5e-158a-77d0-8c02-e8e503b7abe4',
'coordinatorGitMutationsPerformed':False,'userAttachmentArchive':{'path':str(archive_path),'all12ArchivedAndHashVerified':refs_ok},
'audits':audits,'zones':zones,
'nextStep':'Keep generation frozen; resolve all missing child-save/external-archive receipts, refresh independent audits, then collect this file again. Upload owner alone handles Git and final remote verification.'
}
out=ROOT/'docs/MAP_MIGRATION_READY_20261011.json'
if result['readyToCaptureFinalIncrement']:
    result['nextStep']='All map freeze checks passed. Keep producers and audit files stable. Upload owner may now capture the final increment and alone verifies Git/LFS publication. This record does not claim upload completion.'
if out.is_file():
    previous=read(out)
    meaningful=lambda value:{k:v for k,v in value.items() if k!='checkedAtUtc'}
    if meaningful(previous)==meaningful(result):
        print(json.dumps({'unchanged':True,'checkedAtUtc':previous['checkedAtUtc'],'checkpointCount':previous['checkpointCount'],'readyZoneCount':previous['readyZoneCount'],'readyToCaptureFinalIncrement':previous['readyToCaptureFinalIncrement']},ensure_ascii=False))
        raise SystemExit(0)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['checkedAtUtc','checkpointCount','readyZoneCount','readyToCaptureFinalIncrement']},ensure_ascii=False))

