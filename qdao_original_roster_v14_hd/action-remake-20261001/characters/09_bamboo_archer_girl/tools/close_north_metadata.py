from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
sp=ROOT/'selection/run-north.json';selection=read(sp);changes=[]
for row in selection['frames']:
 rp=ROOT/row['generationRecord'];rec=read(rp)
 assert rp.resolve().is_relative_to(ROOT.resolve())
 assert sha(ROOT/row['file'])==row['sha256']
 assert sha(rp)==row['generationRecordSha256']
 if rec.get('route')!='postprocess':continue
 source=rec['derivedFrom'];original=ROOT/source['generationRecord']
 assert sha(original)==source['generationRecordSha256']
 originalRec=read(original);before=sha(rp)
 rec['prompt']=originalRec['prompt'];rec['references']=originalRec['references']
 rec['inheritedPromptAndReferenceScope']='These top-level compatibility fields describe the original AI source only. This record is deterministic alpha cleanup, with no new AI submission.'
 rec['sourceGenerationEvidence']={'file':source['generationRecord'],'sha256':source['generationRecordSha256'],'actualModel':originalRec.get('actualModel'),'actualQuality':originalRec.get('actualQuality'),'originalGeneratedAt':originalRec.get('generatedAt')}
 rec['recordUpdatedAtUtc']=stamp
 write(rp,rec);row['generationRecordSha256']=sha(rp)
 changes.append({'file':row['generationRecord'],'oldRecordSha256':before,'newRecordSha256':sha(rp),'sourceGenerationRecord':source['generationRecord'],'imageUnchanged':True})
assert len(changes)==7,len(changes)
write(sp,selection)
tp=ROOT/'provenance/run-north/technical-current.json';technical=read(tp)
bySlot={f"{r['action']}/{r['direction']}/{r['frame']:02d}":r for r in selection['frames']}
for row in technical['frames']:
 selected=bySlot[row['slot']]
 row['generationRecord']=selected['generationRecord'];row['generationRecordSha256']=selected['generationRecordSha256']
technical['updatedAt']=stamp;technical['metadataCompatibilityRepair']='Top-level original prompt and references inherited with verified original generation record SHA; no new image or AI invocation.'
write(tp,technical)
rp=ROOT/'review-parts/run-north.json';review=read(rp)
notes={'E':'前掌沿屏右行进，屈膝回收脚的脚尖俯仰不构成横向外撇；E02已以原尺寸核验。','NE':'前掌向右、后跟花纹杯在左；露底摆动脚须按跟—前掌结构判断，未见膝踝横向脱轴；NE01/10已以原尺寸核验。','NW':'支撑靴右侧绿色圆面是后跟杯/厚跟，前掌在左侧延伸；未把后跟误认成反向鞋尖；NW01/10已以原尺寸核验。'}
for row in review['frames']:
 direction=row['slot'].split('/')[1]
 assert sha(ROOT/'runtime'/(row['slot']+'.png'))==row['sha256']
 row['footOrientation']=notes[direction]
 row['footAxisReview']='48帧逐格鞋部检查及指定原尺寸帧核验。无可确定的新外八字问题，保留正确帧；不采用07或任何垂直方向为已通过模板。审查人north_closeout，主审按其已返回事实落盘。'
review['footAxisReviewedAtUtc']=stamp;review['updatedAt']=stamp
write(rp,review)
cp=ROOT/'provenance/run-north/cleanup-closeout.json';cleanup=read(cp)
for row in cleanup['files']:
 if row['disposition']=='pending_parent_manifest_reference_removal' and not (ROOT/row['file']).exists():
  row['disposition']='deleted_by_root_after_current_references_verified';row['deletionEvidence']='audit/cleanup-rejected-20261003.json'
cleanup['updatedAt']=stamp;write(cp,cleanup)
write(ROOT/'audit/north-metadata-closeout.json',{'atUtc':stamp,'changes':changes,'newAiCalls':0,'imageChanges':0,'selectionSha256':sha(sp),'reviewSha256':sha(rp),'basis':'Source prompt/references inherited only after verifying original generation-record hash.'})
print(json.dumps({'correctedMetadata':len(changes),'footAxisFramesRecorded':len(review['frames']),'imageChanges':0}))
