"""Record user allocation and prepare individual native E pose edits; no pixel editing."""
import json
from pathlib import Path
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contract=read(R/'review/grounding-fourframes/contract.json')
contract.update(status='middle4_each_side2_native_pose_repair_in_progress',latestUserRequirement='应该是要着中间地四帧，旁边地各两帧',allocationInterpretation='每脚半圈8帧：沿跑向前侧2，中间身体下方4，后侧2。16帧75ms均匀。每帧独立真实姿态。',allocationIsAssistantExecutionInterpretation=True)
contract['latestSpatialFeedback']['allocationScope']='per_foot_eight_frame_half_cycle_execution_interpretation'
contract['activeFramePlan']=[{'frames':[1,2],'supportFoot':'right','position':'front_side_landing','ms':150},{'frames':[3,4,5,6],'supportFoot':'right','position':'middle_under_body_weight_bearing','ms':300},{'frames':[7,8],'supportFoot':'right','position':'rear_side_push_off','ms':150},{'frames':[9,10],'supportFoot':'left','position':'front_side_landing','ms':150},{'frames':[11,12,13,14],'supportFoot':'left','position':'middle_under_body_weight_bearing','ms':300},{'frames':[15,16],'supportFoot':'left','position':'rear_side_push_off','ms':150}]
write(R/'review/grounding-fourframes/contract.json',contract)
for name in ('STATUS.md','MERGE_HANDOFF.md'):
    p=R/name;s=p.read_text(encoding='utf-8-sig');s=s.replace('2026-10-04最新：按每脚每次至少连续4真实承重帧重新修订中。此前数量及静态结论不代表新接地要求通过；基线与修复记录见review/grounding-fourframes/。','2026-10-04最新：按用户“中间四帧、旁边各两帧”重排真实接地姿态中；每脚前侧2→中间4→后侧2，16×75ms。此前196槽数量及静态结论不代表新要求通过；见review/grounding-fourframes/contract.json。');p.write_text(s,encoding='utf-8')
cfg=read(Path('D:/work/image/config/image-generation.json'))
style='D:/work/image/designs/jubaozhai-ui/02-characters.png'
old={x['frame']:x for x in read(R/'selected-new.json') if x['action']=='run' and x['direction']=='E'}
reuse={1:old[1]['source'],2:old[2]['source'],4:old[3]['source'],8:'generation/run/E/04-v4.png',9:old[9]['source'],10:old[10]['source'],12:old[11]['source'],16:'generation/run/E/12-v3.png'}
jobs=[]
for frame in [3,5,6,7,11,13,14,15]:
    right=frame<9;phase=frame if right else frame-8
    target='generation/run/E/03-v1.png' if right else 'generation/run/E/11-v2.png'
    end='generation/run/E/04-v4.png' if right else 'generation/run/E/12-v3.png'
    foot='anatomical RIGHT, near-camera' if right else 'anatomical LEFT, far-camera'
    swing='anatomical LEFT, far-camera' if right else 'anatomical RIGHT, near-camera'
    desc={3:'early middle stance: planted ankle is at x=650, only slightly ahead of pelvis; supporting knee softly bends to absorb weight. The free knee advances from behind toward the pelvis; free shoe is near x=640, bottom y=1080, visibly above the ground.',5:'third middle stance: planted ankle is at x=560, slightly behind pelvis; supporting knee is naturally bent while the body passes over it. Free knee swings ahead toward the right, free ankle x=770 and shoe bottom y=1060.',6:'fourth middle stance: planted ankle is at x=520, modestly behind pelvis; knee extends a little as the hip passes forward, ankle still dorsiflexed with sole grounded. Free knee farther ahead, free ankle x=790 and shoe bottom y=1080.',7:'first rear-side stance: planted ankle is at x=465 behind pelvis; rear leg extends from hip, heel only slightly lifted and ball/toes planted horizontally. Free leg reaches ahead of body, free ankle x=795 and shoe bottom y=1090.'}[phase]
    stem=f'generation/run/E/middle4-{frame:02d}-v1'
    prompt=f'''Use case: precise-object-edit. Produce ONE independent transparent 1254x1254 EAST-facing chibi running frame, slot {frame:02d}/16. Input 1 is exact identity, camera, scale and upper-body edit target; input 2 is the later rear-contact pose for trajectory only; input 3 is the approved painted style.\n+The user requests one supporting foot passes through front-side TWO real poses, middle FOUR real poses, rear-side TWO real poses; do not repeat a static drawing. This output is {desc}\n+Redraw ONLY articulated lower limbs below the pelvis; retain the full upper body/head at exactly input 1's position, scale and proportions. Maintain skull width, face, hair, smile, ears, band, knot, torso, sleeves, BOTH hands, jewelry and gourd. The supporting foot is {foot}; the swinging foot is {swing}. Its layering must remain anatomically coherent. Pelvis near x=660, y=900; preserve current hip position. Support boot size matches the original, ankle near specified x, sole bottom y=1156 in this same canvas; boot points EAST (screen-right), not toward viewer, not rolled sideways. Middle stance must have a broad flat grounded sole, not merely an isolated dangling toe. Rear stance has grounded broad forefoot, natural gentle heel rise. Free foot stays above support level. Exactly two legs, two feet, no crossed or merged shins. Keep natural knee bends and short chibi limb lengths.\n+Upper body unchanged from input1: anatomical LEFT hand grips and supports the golden taiji gourd, anatomical RIGHT hand is empty. Preserve bright clean hand-painted jade green, ivory and warm gold detail. No text, no ground/shadow/contact marker, no UI, no background, no mirroring, no image translation/rescale, no cropped limbs, no enlarged head. Highest fidelity of ongoing batch; true transparent alpha. One frame only, not a contact sheet.'''
    refs=[str(R/target),str(R/end),style]
    req={'startedAt':datetime.now(timezone.utc).isoformat(),'status':'prepared','tool':'image_gen.imagegen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'prompt':stem+'.prompt.txt','references':refs,'referenceRoles':['exact edit target / scale and identity','later rear support trajectory','approved painted style'],'editTarget':target,'userRequirement':'中间四帧、旁边各两帧','plannedSlot':frame,'supportFoot':'right' if right else 'left'}
    assert not (R/(stem+'.request.json')).exists(),stem
    (R/(stem+'.prompt.txt')).write_text(prompt,encoding='utf-8');write(R/(stem+'.request.json'),req)
    jobs.append({'frame':frame,'stem':stem,'prompt':prompt,'references':refs})
write(R/'review/grounding-fourframes/E-middle4-jobs.json',jobs)
plan=[]
for frame in range(1,17):
    phase=(frame-1)%8+1;source=reuse.get(frame,f'generation/run/E/middle4-{frame:02d}-v1.png')
    plan.append({'action':'run','direction':'E','frame':frame,'source':source,'supportFoot':'right' if frame<9 else 'left','position':'front' if phase<3 else 'middle' if phase<7 else 'rear','status':'planned_existing_source_pending_sequence_review' if frame in reuse else 'planned_new_native_pose','observation':'前侧2→中间4→后侧2；真实逐帧屈膝/踝过渡待看图核对。'})
write(R/'review/grounding-fourframes/E-middle4-plan.json',plan)
print(json.dumps({'prepared':len(jobs),'plan':len(plan)}))
