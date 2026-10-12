"""Finalize 04 delivery metadata after explicit visual review; optional scoped image cleanup."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
from io import BytesIO
import argparse, hashlib, json
from timing_profile import RUN_NORMAL_DURATIONS
ROOT=Path(__file__).resolve().parents[1]
SPECS={"run":(16,["N","NE","E","SE","S","SW","W","NW"],75),"hit":(6,["E","W"],40),"attack":(12,["E","W"],30),"cast":(16,["E","W"],45)}
AUDIT='provenance/audit/final_inventory_audit_20261003.json'
APPROVAL='provenance/audit/root_visual_approval_20261003.json'
SNAPSHOT='provenance/audit/export_precleanup_snapshot.json'
LEDGER='provenance/audit/final_image_retention_20261003.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def require(condition,message):
 if not condition:raise ValueError(message)
def local(value,within=None):
 require(isinstance(value,str) and bool(value),'Missing relative path')
 p=Path(value)
 require(not p.is_absolute() and '..' not in p.parts,f'Expected confined relative path: {value}')
 p=(ROOT/p).resolve();boundary=(ROOT/within).resolve() if within else ROOT
 require(p.is_relative_to(boundary),f'Path outside allowed directory: {value}')
 return p
def save(p,obj):
 p=local(rel(p))
 p.parent.mkdir(parents=True,exist_ok=True)
 temp=p.with_name(p.name+'.tmp')
 require(not temp.exists(),f'Refuse existing temporary file: {temp}')
 temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 temp.replace(p)
def measure(p):
 content=p.read_bytes()
 with Image.open(BytesIO(content)) as im:
  im.load();pixels=im.convert('RGBA')
  info={'sha256':hashlib.sha256(content).hexdigest(),'width':im.width,'height':im.height,
        'mode':im.mode,'format':im.format,'rgbaPixelSha256':hashlib.sha256(pixels.tobytes()).hexdigest()}
 return info,pixels
def entries_by_file(entries,expected,label):
 require(isinstance(entries,list),f'{label}: missing entries list');result={}
 for entry in entries:
  require(isinstance(entry,dict),f'{label}: invalid entry');name=entry.get('file')
  require(isinstance(name,str) and name in expected and name not in result,f'{label}: invalid/duplicate/extra file: {name}')
  result[name]=entry
 require(set(result)==expected,f'{label}: missing files: {sorted(expected-set(result))}')
 return result
def preflight(cleanup):
 """Read-only. Approval schema: character/reviewer/reviewedAt/scope/entries.

 entries must bind every current file/sha256/status=visual_passed. Optional
 methods, observations, offlineSequenceReview and per-entry observation or
 independentPoseObserved are copied only when explicitly supplied by root.
 """
 require(ROOT.name=='04_mountain_guardian_boy','Finalizer restricted to character 04')
 expected={f'frames/{a}/{d}/frame_{n:02d}.png' for a,(count,dirs,_) in SPECS.items() for d in dirs for n in range(1,count+1)}
 require({rel(p) for p in (ROOT/'frames').rglob('*.png')}==expected and len(expected)==196,'Expected exactly 196 formal PNG slots')
 audit_path=local(AUDIT,'provenance/audit');approval_path=local(APPROVAL,'provenance/audit')
 audit=read(audit_path);approval=read(approval_path)
 require(Path(audit.get('root','')).resolve()==ROOT,'Audit belongs to another root')
 require(audit.get('expectedCount')==196 and audit.get('actualPngCount')==196 and audit.get('missingPngs')==[] and audit.get('extraPngs')==[] and audit.get('summary',{}).get('errorCount')==0,'Audit inventory/errors not clean')
 for key in ('duplicateFormalShaGroups','duplicateRgbaPixelGroups','duplicateNativeShaGroups'):
  require(audit.get(key)==[],f'Audit reports/omits {key}')
 audits=entries_by_file(audit.get('frames'),expected,'audit')
 require(approval.get('character')==ROOT.name,'Approval belongs to another character')
 for key in ('reviewer','reviewedAt','scope'):
  require(isinstance(approval.get(key),str) and approval[key].strip(),f'Approval missing {key}')
 require(datetime.fromisoformat(approval['reviewedAt'].replace('Z','+00:00')).utcoffset() is not None,'Approval time requires timezone')
 approvals=entries_by_file(approval.get('entries'),expected,'approval')
 guards={AUDIT:sha(audit_path),APPROVAL:sha(approval_path)};frames=[]
 for a,(count,dirs,ms) in SPECS.items():
  for d in dirs:
   for n in range(1,count+1):
    name=f'frames/{a}/{d}/frame_{n:02d}.png';p=local(name,'frames');j=local(rel(p.with_suffix('.generation.json')),'frames')
    data=read(j);record_sha=sha(j);export,export_pixels=measure(p)
    require((export['width'],export['height'],export['mode'],export['format'])==(1024,1024,'RGBA','PNG'),f'Formal format: {name}')
    require(data.get('file')==name and data.get('sha256')==export['sha256'],f'Unbound sidecar: {name}')
    require(data.get('actualModel') is None and data.get('actualQuality') is None,f'Unexpected actual model/quality: {name}')
    native=data.get('nativeSource',{});native_path=local(native.get('path'),'provenance');native_actual,native_pixels=measure(native_path)
    require(native['path']==rel(native_path),f'Native path must be canonical relative path: {name}')
    require(native_actual['width']>=1024 and native_actual['height']>=1024 and native_actual['mode']=='RGBA' and native_actual['format']=='PNG',f'Native size/format: {name}')
    for key in ('sha256','width','height','mode','format'):
     require(native.get(key)==native_actual[key],f'Native {key} mismatch: {name}')
    resized=native_pixels.resize((1024,1024),Image.Resampling.LANCZOS)
    pixel_match=resized.tobytes()==export_pixels.tobytes();resized.close();native_pixels.close();export_pixels.close()
    require(pixel_match,f'Whole-canvas export mismatch: {name}')
    row=audits[name];approved=approvals[name]
    require(row.get('errors')==[] and row.get('wholeCanvasResizePixelMatch') is True and row.get('nativeAvailability')=='available',f'Audit lacks clean native/pixel evidence: {name}')
    require(row.get('sidecarSha256')==record_sha,f'Stale audit sidecar: {name}; rerun inventory audit')
    for label,measured in (('actual',export),('nativeActual',native_actual)):
     recorded=row.get(label,{})
     require(recorded.get('stableDuringRead') is True and all(recorded.get(k)==measured[k] for k in ('sha256','width','height','mode','format','rgbaPixelSha256')),f'Stale audit {label}: {name}; rerun inventory audit')
    require(row.get('nativeRecord',{}).get('path')==native['path'] and row['nativeRecord'].get('sha256')==native_actual['sha256'],f'Audit native binding: {name}')
    require(approved.get('sha256')==export['sha256'] and approved.get('status')=='visual_passed',f'No root approval for current SHA: {name}')
    if 'independentPoseObserved' in approved:require(isinstance(approved['independentPoseObserved'],bool),f'Invalid pose declaration: {name}')
    guards.update({name:export['sha256'],rel(j):record_sha,native['path']:native_actual['sha256']})
    frames.append({'action':a,'direction':d,'frame':n,'path':name,'sha256':export['sha256'],'record':rel(j),'recordSha256BeforeFinalization':record_sha,'nativeSource':native,'data':data,'approval':approved,'export':export,'native':{'path':native['path'],**native_actual},'duration':ms})
 require(len({f['export']['sha256'] for f in frames})==196 and len({f['export']['rgbaPixelSha256'] for f in frames})==196 and len({f['native']['sha256'] for f in frames})==196,'Duplicate export/native content')
 candidates=[]
 if cleanup:
  require(not local(SNAPSHOT,'provenance/audit').exists() and not local(LEDGER,'provenance/audit').exists(),'Existing final snapshot/ledger: preserve and inspect before retrying cleanup')
  old={ROOT/'preview'/n for n in ('run_E_normal.gif','run_N_normal.gif','run_S_normal.gif')}
  paths=list((ROOT/'provenance').rglob('*.png'))+list((ROOT/'provenance').rglob('*.gif'))+[p for p in old if p.exists()]
  seen=set()
  for p in sorted(paths):
   resolved=p.resolve()
   require(not p.is_symlink() and resolved==p.absolute(),f'Cleanup refuses redirected path: {p}')
   require(resolved.is_relative_to(ROOT) and (resolved.is_relative_to(ROOT/'provenance') or resolved in old) and resolved.suffix.lower() in ('.png','.gif'),f'Cleanup outside image scope: {p}')
   require(resolved.is_file() and resolved not in seen,f'Invalid cleanup file: {p}');seen.add(resolved)
   item={'path':rel(resolved),'sha256':sha(resolved),'bytes':resolved.stat().st_size};candidates.append(item);guards[item['path']]=item['sha256']
  require({f['native']['path'] for f in frames}.issubset({item['path'] for item in candidates}),'Cleanup plan must include every measured selected native')
 outputs=[f['record'] for f in frames]+['review.json','runtime_timing.json','manifest.delivery.json','frames.sha256']
 if cleanup:outputs += [SNAPSHOT,LEDGER]
 for name in outputs:
  output=local(name)
  require(not output.with_name(output.name+'.tmp').exists(),f'Existing temporary output: {name}')
 for name,digest in guards.items():require(sha(local(name))==digest,f'Input changed during preflight: {name}')
 return {'frames':frames,'approval':approval,'auditSha256':guards[AUDIT],'approvalSha256':guards[APPROVAL],'candidates':candidates}
def main(cleanup):
 plan=preflight(cleanup) # No writes above this gate, including on a late-frame failure.
 NOW=datetime.now(timezone.utc).isoformat()
 frames=plan['frames'];approval=plan['approval'];snapshot_sha=None
 if cleanup:
  snapshot={'schema':'qdao-export-precleanup-snapshot-v1','character':ROOT.name,'measuredAt':datetime.now(timezone.utc).isoformat(),
   'audit':{'path':AUDIT,'sha256':plan['auditSha256']},'visualApproval':{'path':APPROVAL,'sha256':plan['approvalSha256']},
   'entries':[{'file':f['path'],'sha256':f['sha256'],'record':f['record'],'recordSha256BeforeFinalization':f['recordSha256BeforeFinalization'],
               'export':f['export'],'native':f['native'],'wholeCanvasResizePixelMatch':True} for f in frames]}
  save(ROOT/SNAPSHOT,snapshot);snapshot_sha=sha(ROOT/SNAPSHOT)
 for f in frames:
  data=f['data'];approved=f['approval'];previous=data.get('review',{})
  data['review']={'status':approved['status'],'automaticallyApproved':False,'reviewedAt':approval['reviewedAt'],
   'scope':approval['scope'],'reviewer':approval['reviewer'],'priorReview':previous,'sourceBoundSha256':f['sha256'],
   'clientDynamicStatus':'not_integrated','approvalRecord':APPROVAL,'approvalSha256':plan['approvalSha256']}
  for key in ('independentPoseObserved','observation'):
   if key in approved:data['review'][key]=approved[key]
  data['frameDurationMs']=f['duration']
  if f['action']=='run':
   data['runTiming']={'offlinePreviewDefaultLoopMs':1200,'offlinePreviewFrameMs':75,'offlinePreviewFrameDurationsMs':RUN_NORMAL_DURATIONS,
    'clientApprovedLoopMs':None,'status':'user_selected_offline_1200_client_unconfirmed'}
  data.setdefault('rootAnchor',{})['status']='declared_layout_target_not_pixel_verified';data['clientIntegration']='not_integrated'
  if snapshot_sha:
   data['nativeSource']['precleanupSnapshot']={'path':SNAPSHOT,'sha256':snapshot_sha}
   for source in [data['nativeSource'],*data.get('derivedFrom',[])]:
    if isinstance(source,dict) and source.get('path')==f['native']['path'] and source.get('sha256')==f['native']['sha256']:
     source['fileRetained']=True # Preflight actually measured this source; failures must stay retained.
  save(ROOT/f['record'],data)
 review={"character":ROOT.name,"reviewedAt":approval['reviewedAt'],"finalizedAt":NOW,"generated":len(frames),"exported":len(frames),"staticVisualPassed":len(frames),
  "offlineSequenceReview":approval.get('offlineSequenceReview','not_declared'),"clientIntegration":"not_integrated","clientDynamicAcceptance":"not_run",
  "methods":approval.get('methods',[]),"observations":approval.get('observations',{}),
  "limits":["1200ms/75ms为用户选定的离线节奏；客户端速度未接入验证。","512,928仅历史布局声明；不把辅助线或最低脚像素当作物理地面。","独立绘制的杖首细纹/衣褶有少量逐帧变化；不据SHA不同证明动态质量。","客户端世界位移/停步/转向/碰撞锚点和脚滑测试未运行。"],
  "frameBindings":[{k:f[k] for k in ("action","direction","frame","path","sha256","record")} for f in frames],
  "audit":AUDIT,"auditSha256":plan['auditSha256'],"rootVisualApproval":{'path':APPROVAL,'sha256':plan['approvalSha256']}}
 save(ROOT/"review.json",review)
 timing={"character":ROOT.name,"frameIndexBase":1,"canvas":[1024,1024],"mode":"RGBA",
  "layoutAnchor":{"x":512,"y":928,"status":"historical_layout_target_not_measured_ground"},
  "clientRootAnchor":None,"clientIntegration":"not_integrated",
  "run":{"directions":SPECS["run"][1],"framesPerDirection":16,"frameMs":75,
  "offlineDefaultLoopMs":1200,"offlineFrameDurationsMs":RUN_NORMAL_DURATIONS,"clientApprovedLoopMs":None,
  "timingRationale":"用户指定1200ms完整循环，16帧均匀75ms；移除旧快档，不加首尾停顿。",
  "previewEncoding":"APNG","previewFrameDurationsMs":[75]*16,"phaseMarkers":{"1":"第一侧接触","2":"承重缓冲","3":"中支撑","4":"后蹬/交换","5":"蹬地收尾","6":"短腾空","7":"下降","8":"异侧预接触","9":"异侧接触","10":"异侧承重缓冲","11":"异侧中支撑","12":"反向后蹬/交换","13":"反向蹬地收尾","14":"短腾空","15":"下降","16":"回接第一侧"}},
  "hit":{"directions":["E","W"],"framesPerDirection":6,"frameMs":40,"durationMs":240,"loopInGame":False},
  "attack":{"directions":["E","W"],"framesPerDirection":12,"frameMs":30,"durationMs":360,"contactFrame":6,"contactTimeMsFromStart":150,"loopInGame":False},
  "cast":{"directions":["E","W"],"framesPerDirection":16,"frameMs":45,"durationMs":720,"releaseFrame":10,"releaseTimeMsFromStart":405,"loopInGame":False},
  "eventTimingNote":"一基帧号，事件在指定帧开始触发；仅素材建议标记，实际命中/弹道由客户端处理。",
  "transformPolicy":"整画布统一缩放；无单帧平移、脚底贴线、bbox缩放、镜像、复制或补帧。"}
 save(ROOT/"runtime_timing.json",timing)
 cleanup_record=None
 if cleanup:
  cleanup_record={'schema':'qdao-image-retention-v2','character':ROOT.name,'startedAt':datetime.now(timezone.utc).isoformat(),
   'policy':'仅删除本角色已导出原生/拒稿/中间图片及列明重复预览；保留所有文字。','nativeAuditBeforeDeletion':AUDIT,'nativeAuditSha256':plan['auditSha256'],
   'precleanupSnapshot':{'path':SNAPSHOT,'sha256':snapshot_sha},'files':[{**item,'status':'pending'} for item in plan['candidates']],'outsideCharacterDirectoryTouched':False}
  save(ROOT/LEDGER,cleanup_record)
  for item in cleanup_record['files']:
   try:
    original=ROOT/item['path'];p=local(item['path'])
    require(not original.is_symlink() and p==original.absolute() and (p.is_relative_to(ROOT/'provenance') or item['path'] in ('preview/run_E_normal.gif','preview/run_N_normal.gif','preview/run_S_normal.gif')),f"Cleanup path changed: {item['path']}")
    require(sha(p)==item['sha256'],f"Cleanup file changed after preflight: {item['path']}")
    p.unlink();item.update(status='deleted',deletedAt=datetime.now(timezone.utc).isoformat())
   except (OSError,ValueError) as error:item.update(status='failed',attemptedAt=datetime.now(timezone.utc).isoformat(),error=str(error))
   save(ROOT/LEDGER,cleanup_record)
  cleanup_record['completedAt']=datetime.now(timezone.utc).isoformat()
  cleanup_record['deletedCount']=sum(item['status']=='deleted' for item in cleanup_record['files'])
  cleanup_record['failedCount']=sum(item['status']=='failed' for item in cleanup_record['files'])
  save(ROOT/LEDGER,cleanup_record)
  removed={item['path']:item for item in cleanup_record['files'] if item['status']=='deleted'}
  for f in frames:
   data=f['data']
   for source in [data['nativeSource'],*data.get('derivedFrom',[])]:
    if not isinstance(source,dict):continue
    item=removed.get(source.get('path'))
    if item and source.get('sha256')==item['sha256']:
     source.update(fileRetained=False,deletedAt=item['deletedAt'],retentionRecord=LEDGER,
       retentionNote='成功删除后登记；原生实测与导出绑定见SHA锁定的清理前快照。')
   save(ROOT/f['record'],data)
 file_records=[{"path":f["path"],"sha256":f["sha256"],"record":f["record"],"recordSha256":sha(ROOT/f["record"])} for f in frames]
 save(ROOT/"manifest.delivery.json",{"character":ROOT.name,"createdAt":NOW,"targetFrames":196,"exportedFrames":len(frames),"files":file_records,"review":"review.json","timing":"runtime_timing.json",
  'cleanup':None if cleanup_record is None else {'record':LEDGER,'deleted':cleanup_record['deletedCount'],'failed':cleanup_record['failedCount']}})
 local('frames.sha256').write_text("\n".join(f["sha256"]+"  "+f["path"] for f in frames)+"\n",encoding="utf-8")
 print(json.dumps({"frames":len(frames),"distinct":len({f["sha256"] for f in frames}),"cleanup":cleanup,"staticVisualPassed":len(frames),'cleanupFailed':0 if cleanup_record is None else cleanup_record['failedCount']},ensure_ascii=False))
 if cleanup_record and cleanup_record['failedCount']:raise SystemExit('Partial cleanup: inspect ledger failures; do not rerun blindly.')
if __name__=="__main__":
 if RUN_NORMAL_DURATIONS != [75]*16: raise SystemExit("历史交付工具已停用；本轮使用finalize_video_axis_followup.py。")
 p=argparse.ArgumentParser();p.add_argument("--cleanup",action="store_true");a=p.parse_args()
 try:main(a.cleanup)
 except (OSError,ValueError,KeyError,TypeError) as error:raise SystemExit(str(error)) from error

