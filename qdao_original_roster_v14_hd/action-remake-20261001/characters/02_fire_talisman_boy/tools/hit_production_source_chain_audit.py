import json,hashlib,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
r=Path(__file__).resolve().parents[1]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((r/'inventory-hit.json').read_text(encoding='utf-8-sig'))
out={'createdAt':datetime.datetime.now(ZoneInfo('America/New_York')).isoformat(),'method':'实际读取宿主返回的PNG文件、角色内native、当前导出PNG并分别计算SHA256；不只比较记录内部字段','frames':[],'errors':[]}
for f in inv['frames']:
    rec=json.loads((r/f['source_record']).read_text(encoding='utf-8-sig'))
    native=r/rec['file']; host=Path(rec['evidence']['sourcePath']); exp=r/f['path']
    row={'action':f['action'],'direction':f['direction'],'frame':f['frame'],'source_record':f['source_record'],'actual_host_file':str(host),'native_file':str(native),'export_file':str(exp)}
    try:
        row.update(actual_host_sha256=h(host),actual_native_sha256=h(native),actual_export_sha256=h(exp))
        row['host_matches_native']=row['actual_host_sha256']==row['actual_native_sha256']
        row['native_matches_record']=row['actual_native_sha256']==rec['sha256']
        row['export_matches_record_inventory']=row['actual_export_sha256']==rec['export']['sha256']==f['sha256']
        if not all(row[k] for k in ['host_matches_native','native_matches_record','export_matches_record_inventory']):out['errors'].append({'slot':[f['action'],f['direction'],f['frame']],'reason':'SHA mismatch','details':row})
    except Exception as e:out['errors'].append({'slot':[f['action'],f['direction'],f['frame']],'reason':str(e)})
    out['frames'].append(row)
out['count']=len(out['frames']);out['passed']=not out['errors']
(r/'records/hit-source-chain-audit-20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':out['count'],'passed':out['passed'],'errors':out['errors']},ensure_ascii=False))

