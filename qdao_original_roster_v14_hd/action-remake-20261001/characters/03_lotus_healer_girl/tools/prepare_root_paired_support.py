from pathlib import Path
import json
B=Path(__file__).resolve().parent.parent
REF=B.parent/'09_bamboo_archer_girl/runtime/run'
jobs=[]
for direction,numbers in [('NE',[3,5,6,7,8,11,12,13,14,15,16]),('S',[5,6,7,8,13,14,15,16])]:
    data=json.loads((B/f'review/run-{direction}-sequence-input.json').read_text(encoding='utf-8-sig'))
    frames={int(f.get('frame',f.get('slot'))):f for f in data['frames']}
    for n in numbers:
        src=Path(frames[n]['source'])
        if not src.is_absolute():src=(B/src).resolve()
        right=n<=8
        side='RIGHT' if right else 'LEFT'
        free='LEFT' if right else 'RIGHT'
        phase=(n-1)%8+1
        master=Path(frames[1 if right else 9]['source'])
        if not master.is_absolute():master=(B/master).resolve()
        if phase in (3,4):
            place='directly BELOW the pelvis in middle stance, heel AND forefoot down, knee softly bent accepting body weight'
            motion='The free leg is bent and passing forward. Keep its pose unless needed to preserve correct hip ownership.'
        elif phase in (5,6):
            place='a LITTLE BEHIND the pelvis in continuing late support, heel still down and full foot bearing weight; NOT yet toe-off'
            motion='The other knee swings forward while its foot stays clearly lifted. The support leg must extend toward the ground, never fold up behind.'
        else:
            place='BEHIND the pelvis in final late stance, with the FOREFOOT and toe still visibly pressing the ground; heel may rise modestly while calf pushes, but it is NOT airborne'
            motion='The other free leg extends forward preparing its next contact, but this frame still bears weight on the original support foot. Do not switch support feet early.'
        if direction=='NE':
            axis='NE rear three-quarter, away toward upper-right. Supporting shoe toe follows the shin toward upper-right in perspective, consistent with image3. Backward stance progression is toward lower-left in the ground plane, NOT a sideways fan. Keep contact shoe bottom around1165-1190 on the1254 canvas, allowing sensible near/far depth, not an ankle floating high near the skirt.'
            reference=REF/'NE'/'03.png'
        else:
            axis='S direct front, toward viewer. Supporting shoe and knee point straight toward viewer/down-frame, no outward yaw. Rearward progression is deeper/up-frame under the hip, not spreading sideways. Right support is screen-left, left support screen-right; keep both legs on narrow parallel tracks. Support shoe must reach a credible ground depth near1140-1180 on1254 canvas with real ankle/forefoot contact, not fold high near skirt.'
            reference=REF/'S'/'03.png'
        prompt=f"""Use case precise-object-edit. One independent animation frame for user-requested continuous grounded stride. Image1 is edit target for EXACT upperbody registration and props; image2 identifies which anatomical support leg remains planted in this half-cycle; image3 is approved bamboo archer foot-axis/grounding/style reference ONLY.
This is {direction} frame{n:02d} of16. Change only legs/ankles/shoes below hips as needed. Keep image1 head/bun/face/hair, torso, hands, gold hooked lotus lantern in anatomical RIGHT hand, round jade bottle LEFT, costume and all accessories unchanged at the SAME canvas position/scale. Full WHITE baggy trousers, pink lotus shoes, same chibi anatomy; no bare knees or bow.
Anatomical {side} foot is STILL THE SUPPORT FOOT, the same leg that is planted in image2. It is {place}. {motion} Anatomical {free} leg is the free swing leg. Trace each leg from its correct hip, no swapping crossed legs or duplicate limbs.
{axis}
Redraw real support anatomy: soft loaded knee, ankle over a planted shoe, thin gold sole edge at contact, heel lowering when full-foot support is required. Do NOT show the support foot's broad brown outsole facing camera as though it were flying. The airborne free foot may expose its sole normally. No whole-character translation, crop, rotate, mirroring, or motion blur to fake ground. No duplicate pose from image2: retain image1 distinct leg phase while making this support foot bear weight at the stated position.
This is position-step {((phase-1)//2)+1}, image{1 if phase%2 else 2} of a TWO-DISTINCT-POSE pair. Both pair members support the same foot but show modest knee/ankle/weight progression; do not make a new contact or take off between them.
Keep1254x1254 square RGBA genuine transparent background. Preserve the original silhouette above hips and intact edges. No ground drawing, shadow, text, or extra props."""
        stem=f'generation/{direction}/{n:02d}-paired-v1'
        for suffix in ['.png','.prompt.txt','.args.json','.job.json']:
            if (B/(stem+suffix)).exists():raise FileExistsError(stem+suffix)
        refs=[{'path':str(src).replace('\\','/'),'purpose':'edit target; preserve current upperbody registration'},
              {'path':str(master).replace('\\','/'),'purpose':f'identity of anatomical {side} supporting leg in this half-cycle'},
              {'path':str(reference).replace('\\','/'),'purpose':'user approved grounded foot axis/style only'}]
        (B/(stem+'.prompt.txt')).write_text(prompt,encoding='utf-8')
        args={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs],'transparent_background':True}
        (B/(stem+'.args.json')).write_text(json.dumps(args,ensure_ascii=False,indent=2),encoding='utf-8')
        job={'output':stem+'.png','prompt':stem+'.prompt.txt','references':refs,'receipt':stem+'.receipt.json'}
        (B/(stem+'.job.json')).write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
        jobs.append({'direction':direction,'slot':n,'stem':stem,'source':refs[0]['path'],'args':args})
(B/'review/root-paired-generation-jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'jobs':len(jobs),'byDirection':{d:sum(j['direction']==d for j in jobs) for d in ['NE','S']}}))

