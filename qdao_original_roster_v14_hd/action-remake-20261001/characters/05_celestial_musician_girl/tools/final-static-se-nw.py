from pathlib import Path
from PIL import Image
import json, hashlib, datetime
r=Path(__file__).resolve().parents[1]
def read(p): return json.loads((r/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((r/p).read_bytes()).hexdigest()
def save(p,d): (r/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sel=read('provenance/run/selection-SE-NW.json')
se=read('provenance/run/grounding-SE-20261003.json')
nw=read('provenance/run/grounding-NW-20261003.json')
seFoot=[
'近RIGHT低靴为较正面透视缩短，鞋头沿脚背前向，远LEFT高折；未见明确横向外旋，保留。',
'近RIGHT屈膝压重，鞋面与踝链连续，低鞋前端透视略偏左但没有独立扭踝外八；保留。',
'近RIGHT低支撑鞋为前向缩短，远LEFT回收靴鞋头随胫骨；保留。',
'近RIGHT承重靴接近正前，远LEFT高前鞋露底来自翘尖，膝踝同向；保留。',
'近RIGHT后靴抬跟，趾端向下前，远LEFT前鞋朝SE；无明确横向分叉，保留。',
'近RIGHT后蹬靴趾下跟高，远LEFT前鞋朝SE，鞋底显露来自前摆背屈；保留。',
'双空，近RIGHT后折靴随胫骨回收，远LEFT前鞋朝右前，未见独立扭踝外旋；保留。',
'远LEFT前低鞋鞋头右前，近RIGHT后靴回收，两鞋方向随对应胫骨，保留。',
'远LEFT低支撑靴朝右前，近RIGHT后折靴朝下前，无明显外八；保留。',
'远LEFT低靴鞋头右前、屈膝承重，近RIGHT高折；保留。',
'远LEFT低支撑靴朝右前，近RIGHT回收靴略伸出，膝踝链连续；保留。',
'近RIGHT高前鞋为短靴正面缩短，远LEFT低支撑靴右前，不把翘尖露底判外八；保留。',
'近RIGHT高前鞋为较正面缩短，鞋跟到鞋头没有14旧版那样大幅横拧，远LEFT开始抬跟；保留。',
'v4近RIGHT高前靴已从左外撇改为下偏右，靴面与膝踝前摆同向；远LEFT脚尖低蹬离，未换腿。',
'v3近RIGHT高前靴转为下偏右，保留双膝高屈/远LEFT后折短暂腾空；两鞋方向随前后腿，无旧版向左横拧。',
'v3近RIGHT下降靴转下偏右，靴底薄边与下降腿同向；远LEFT仍高折，腿序未换。']
seSupport=['near_RIGHT','near_RIGHT','near_RIGHT','near_RIGHT','near_RIGHT_forefoot','near_RIGHT_toeoff','none','far_LEFT_pending','far_LEFT','far_LEFT','far_LEFT','far_LEFT','far_LEFT_forefoot','far_LEFT_toeoff','none','near_RIGHT_pending']
for row in se['frames']:
 f=row['frame']; current=next(s for s in sel if s['direction']=='SE' and s['frame']==f)
 if row['file']!=current['file']: row['preFootCorrectionFile']=row['file']
 row.update(current)
 row['observedSupport']=seSupport[f-1]
 row['footDirectionReview']={'decision':'corrected' if f>=14 else 'keep','toeOutObserved':False,'evidence':seFoot[f-1]}
 if f==14: row['footKneeAnkleCOM']='近RIGHT前膝高，靴尖下偏右，远LEFT后靴趾端低、跟高，蹬离相位保持。'
 if f==15: row['footKneeAnkleCOM']='两膝高屈、近RIGHT鞋头转正，远LEFT后折，短暂双空；新靴子脚尖较旧版低，腾空间隙缩短。'
 if f==16:
  row['observedPhase']='descent_contact_boundary'
  row['footKneeAnkleCOM']='近RIGHT前低靴下降、鞋尖下偏右，远LEFT后鞋高折；前足接近接触高度。'
se['reviewedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
se['staticFootDirectionConclusion']='明确外撇的14/15/16分别选v4/v3/v3，静态鞋向修复完成；01–13无明确需修横向外旋保留。'
se['redrawRequiredNow']=[]
se['unresolved']=['整圈固定尺度/根配准和时长由根代理检验，不得逐帧贴脚。','07与15为短暂腾空；15鞋尖转正后间隙缩短，需整段动态对照。','08/16在下降与接触边界，接触时点/停留权重不可仅凭编号认定。','客户端真实地面移动速度与滑步未验收，正式通过仍0。']
save('provenance/run/grounding-SE-20261003.json',se)
for row in nw['frames']:
 row['footDirectionReview']['decision']='keep'
nw['independentReadabilityReview']['status']='completed_retain_current_v2'
nw['independentReadabilityReview']['evidence']='provenance/run/NW04-06-independent-review-20261003.json'
nw['unresolved']=['01/02的静态压低差较小，需连播评价承重感。','固定尺度根配准、全周期速度、逐帧时长与客户端滑步仍未验收；正式通过仍0。']
save('provenance/run/grounding-NW-20261003.json',nw)
rows=[]
for s in sel:
 im=Image.open(r/s['file']); h=sha(s['file']); rec=read(s['generationRecord'])
 assert im.mode=='RGBA' and min(im.size)>=1024
 assert rec.get('sha256',h)==h,(s['file'],'hash mismatch')
 g=se if s['direction']=='SE' else nw
 phase=next(f for f in g['frames'] if f['frame']==s['frame'])
 row={**s,'sha256':h,'generationRecordSha256':sha(s['generationRecord']),'nativeSize':list(im.size),'mode':im.mode,'staticReview':'reviewed_no_required_static_redraw','observedPhase':phase['observedPhase'],'observedSupport':phase['observedSupport'],'footDirection':phase['footDirectionReview'],'anatomicalEvidence':phase.get('anatomicalTrace',phase.get('footKneeAnkleCOM','')),'handTopology':'LEFT hand upper qin; RIGHT hand lower strings; NW far right hand naturally occluded','actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'formalVisualPassed':False}
 rows.append(row)
assert len(rows)==32 and len({x['sha256'] for x in rows})==32
report={'schemaVersion':1,'reviewer':'finish_se_nw','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'run SE/NW 32 current selected native frames','selectionManifest':'provenance/run/selection-SE-NW.json','selectionManifestSha256':sha('provenance/run/selection-SE-NW.json'),'staticConclusion':'当前32槽逐张实看，手持、可见髋膝踝与靴尖方向静态检查完成；没有剩余明确需重画的静态外八/换腿项。','toeDirectionCorrection':{'SE14':'v2 -> v4; v3 rejected for swapped phase','SE15':'v2 -> v3','SE16':'v2 -> v3','NW':'retain current16, shoe yaw follows knee/ankle; not inferred from screen position'},'independentEvidence':['provenance/run/NW04-06-independent-review-20261003.json'],'requiredStaticRedraw':[],'formalVisualPassed':0,'dynamicReview':'parent_review_required','clientReview':'not_available','transformPolicy':'native images unchanged; no bbox fit, no foot-bottom alignment, no global move used to fake grounding','rows':rows}
save('provenance/run/static-SE-NW-final-20261003.json',report)
cast=[]
for s in read('provenance/cast/selection-W.json'):
 im=Image.open(r/s['file'])
 cast.append({**s,'sha256':sha(s['file']),'generationRecordSha256':sha(s['generationRecord']),'nativeSize':list(im.size),'mode':im.mode,'footDirection':{'decision':'keep','toeOutObserved':False,'evidence':'双靴鞋尖朝W/画面左，膝踝与鞋轴同向；各蓄力站姿未见明确横向外八。'},'handTopology':'近LEFT臂跨琴上握，远RIGHT腕从低弦抬升到高位后回落','staticReview':'candidate','formalVisualPassed':False})
save('provenance/cast/foot-direction-W01-07-20261003.json',{'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'cast W01–07 only; W08–16 parent-owned','requiredStaticFootRedraw':[],'formalVisualPassed':0,'rows':cast})
print(json.dumps({'runFrames':len(rows),'uniqueRunHashes':len({x['sha256'] for x in rows}),'castFootReviewed':len(cast),'nativeDimensions':sorted(set(tuple(x['nativeSize']) for x in rows)),'staticRedrawRemaining':0},ensure_ascii=False))

