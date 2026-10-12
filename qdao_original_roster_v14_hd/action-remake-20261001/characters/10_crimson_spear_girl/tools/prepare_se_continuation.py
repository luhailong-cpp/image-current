from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
queue=json.loads((ROOT/'generation/run-south-queue.json').read_text(encoding='utf-8-sig'))
out=[]
for x in queue:
    if not x['slot'].startswith('run-SE-'):continue
    d=ROOT/'generation'/x['slot']
    if (d/'native.png').exists():continue
    i=int(x['slot'].split('-')[-1])
    key='run-SE-04' if i<=8 else 'run-SE-12'
    refs=[str(ROOT/'generation'/key/'native.png')]+x['refs']
    phase=x['prompt'].split('POSE for this exact frame: ')[1].split(' Whole body leans')[0]
    arms=("RIGHT shoulder and lower RIGHT hand swing a little FORWARD against the near RIGHT leg trailing; far LEFT elbow draws back while its hand stays high on shaft." if i<=5 or i>=15 else ("Both shoulders pass neutral with visibly changing bent elbow angles; do not freeze the gun/arms." if i in [6,7,8,14] else "RIGHT shoulder and lower RIGHT hand draw a little BACK against the near RIGHT thigh leading; far LEFT shoulder advances."))
    prompt=("Edit reference1 into ONE new independent animation frame "+x['slot']+". Preserve its exact character identity, face, detailed gold/red/white costume, original boot diamond/flower ornaments, spear design, face/body scale and clean rounded handpainted finish. Reference2 is exact approved SE idle camera/identity, reference3 portrait details, reference4 approved style. Native square at least1024 and genuine alpha.\n"
    +"CAMERA: SOUTHEAST, front three-quarter45-degree view diagonally toward lower screen-right, same as reference2. Anatomical RIGHT leg is NEAR and emerges from screen-left hip. Anatomical LEFT leg is FAR and emerges from screen-right hip. Trace each thigh to its own hip; preserve near/far overlap. Short chibi legs, torso inclines forward, real moving run.\n"
    +"MANDATORY NEW POSE: "+phase+". Rebuild leg positions for this phase, not just hair. Show knee flexion, ankle and boot angle appropriate to support vs flight. Near/far legs visibly alternate which one leads. "+arms+"\n"
    +"Both hands keep original LEFT high/front grip near red spearhead and RIGHT lower/rear grip near gold butt. Wrists close around same single straight long shaft with correct fingers, both elbows remain anatomically connected. Maintain grip order while shoulders counter-rotate opposite pelvis; move gun with both arms. Red crystal spearhead/gold mount/red tassel upper right; gold butt/red tassel lower left.\n"
    +"Canvas registration: maintain reference1 full-canvas character scale, no subject bbox fit or zoom. Shared virtual root normalized(0.5,0.91992), small natural hip bob. Preserve camera-ground perspective, brief flight20–45px, no floor/shadow. Keep all spear tips/ribbons/boots fully inside5% safe margins. Same brown twin buns, twin ponytails, amber eyes, red ribbons and gold bead waist chain. No effects, motion blur, text, particles, duplicated limbs or mirrored pose. Exactly one finished transparent sprite.")
    (d/'prompt-continuation.txt').write_text(prompt,encoding='utf-8')
    (d/'request.json').write_text(json.dumps({'referenced_image_paths':refs,'transparent_background':True,'model':None,'quality':None,'prompt_file':'prompt-continuation.txt'},ensure_ascii=False,indent=2),encoding='utf-8')
    out.append({'slot':x['slot'],'prompt':prompt,'refs':refs})
(ROOT/'generation/run-se-continuation-queue.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([x['slot'] for x in out]))

