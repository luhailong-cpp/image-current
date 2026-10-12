"""Promote visually inspected E poses; keep review pending until actual playback."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selection=read(R/'audit/root-E-spatial-selection.json');inputs=read(R/'audit/root-E-spatial-inputs.json');rows=[]
for ns,v in selection.items():
 n=int(ns);src=R/'run/staging'/f'run-E-{n:02d}-spatial-v{v}.png';dest=R/'run/E'/f'{n:02d}.png'
 run(src,dest);rows.append({'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'srcRoot':inputs[ns]['sourceRoot'],'basis':'Existing anatomical root unchanged; only local leg/boot redraw; no sole alignment or whole-character shift.'})
reg=R/'run/E/spatial-registration.json';save(reg,{'globalScale':.8,'targetRoot':[512,942],'frames':rows});apply(reg)
notes=[
 '远左脚在骨盆前下方落地，01较伸展，02膝自然屈曲缓冲；近右腿在后回收，右托晶臂从后向中间摆。',
 '远左支撑脚经过髋下，03近右脚仍回收，04近右膝抬到身前；左小腿连续承重，右手从中间向前托晶。',
 '远左支撑脚位于髋后，05近右膝高抬，06近右小腿前送；后支撑膝踝连续，前掌保持接触。',
 '远左脚在后侧抬跟，07/08前脚掌与趾持续蹬地；近右脚从前摆到准备落脚仍离地，08比07更前送。',
 '近右脚前侧落脚，09大腿较前伸，10膝屈曲开始承重；远左腿后侧回收，右掌仍前托。',
 '近右脚髋下承重，11左膝抬起、12左小腿回收更明显；右手自然由中间摆到后方，左臂持续抱狐。',
 '近右脚向身后推进，13较屈膝平掌支撑，14后腿进一步伸展、脚跟轻抬；远左小腿向前送但仍离地。',
 '近右后脚前掌持续接地蹬离，15到16脚跟保持抬起且后腿伸展；远左前鞋明确高于支撑脚，衔接01换左脚。'
]
now=datetime.now(timezone.utc).isoformat();pairs=[]
for i,obs in enumerate(notes):pairs.append({'frames':[2*i+1,2*i+2],'position':f'P{i%4+1}','supportLeg':'anatomical_left_far' if i<4 else 'anatomical_right_near','observations':obs})
frames=[{'file':f'run/E/{n:02d}.png','sha256':sha(R/'run/E'/f'{n:02d}.png')} for n in range(1,17)]
contact={'direction':'E','status':'static_pending_root_preview','reviewedAt':now,'criterion':'four_successive_positions_two_distinct_poses_each','cycleMs':1200,'durationMs':75,'frames':frames,'contacts':[{'supportLeg':'anatomical_left_far','frames':list(range(1,9)),'observations':'01–08由远左脚前落、髋下、髋后到后前掌蹬地，近右腿摆动。'},{'supportLeg':'anatomical_right_near','frames':list(range(9,17)),'observations':'09–16由近右脚持续接地完成同一空间顺序，远左腿摆动。'}],'positionPairs':pairs,'visualEvidence':['run/staging/root-E-spatial-full.jpg','run/staging/root-E-spatial-legs.jpg'],'independentStaticReview':'finish_cast_w actually inspected all16 full/leg sheets before final support-height corrections; no wrong support identity, hand identity or material scale jump found. Root inspected final local corrections and rebuilt full sheet.','limitations':['Actual normal-speed and quarter-speed browser review still pending.','Alpha lower bounds used only to locate suspected height inconsistency; contact and support anatomy judged visually.'],'clientValidated':False}
save(R/'audit/contact-E-review.json',contact)
reviews=read(R/'review.json');phase=read(R/'run/E/grounding-review.json')
for n,f in enumerate(frames,1):
 pair=pairs[(n-1)//2];slot=f['file'][:-4]
 reviews[slot]={**reviews.get(slot,{}),'sha256':f['sha256'],'visualStatus':'static_pending_root_preview','latestRequirement':'audit/spatial-contact-requirement.json','contactReview':'audit/contact-E-review.json'}
 row=phase['frames'][n-1];meta=read(R/(f['file']+'.generation.json'))
 row.update({'file':f['file'],'frame':n,'sha256':f['sha256'],'selectedNative':meta['derivedFrom']['file'],'durationMs':75,'phase':pair['position'],'supportLeg':pair['supportLeg'],'observation':pair['observations'],'reviewStatus':'static_pending_root_preview'})
phase.update({'status':'static_pending_root_preview','spatialContactReview':'audit/contact-E-review.json','positionPairs':pairs,'contactSpans':contact['contacts'],'selectedCycleMs':1200,'durationsMs':[75]*16,'clientValidated':False})
save(R/'run/E/grounding-review.json',phase);save(R/'review.json',reviews)
print(json.dumps({'promoted':len(selection),'direction':'E','status':'static_pending_root_preview'}))
