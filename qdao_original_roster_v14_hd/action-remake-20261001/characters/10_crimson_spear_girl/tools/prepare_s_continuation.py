from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
queue=json.loads((ROOT/'generation/run-south-queue.json').read_text(encoding='utf-8-sig'))
screen={
7:"SCREEN-SPACE POSE OVERRIDE: screen-right leg supports her weight, foot firmly at y=0.92; screen-left knee lifted HIGH FORWARD at y=0.69 and its boot tucked near y=0.80. Pelvis slightly over screen-right stance. This is passing/midstance, not a wide split.",
8:"SCREEN-SPACE POSE OVERRIDE: screen-right foot trails with heel high and only toe at ground y=0.92; screen-left knee forward and shin unfolds down toward viewer. Push-off; pelvis rises slightly.",
9:"SCREEN-SPACE POSE OVERRIDE: screen-right toe completes push at y=0.92, screen-left thigh leads forward visibly with knee high. Lean into camera. No two-foot standing.",
10:"SCREEN-SPACE POSE OVERRIDE: screen-right toe leaves ground, screen-left boot extends forward toward viewer; both feet just lift with a very short 20px clearance.",
11:"SCREEN-SPACE POSE OVERRIDE: screen-left thigh leads, knee flexed then extending, screen-right thigh trails with knee bent and heel folded. BOTH boots are airborne 25px above virtual ground.",
13:"SCREEN-SPACE POSE OVERRIDE: screen-left boot lands with heel first at y=0.92; screen-right leg clearly trails bent at knee, boot lifted. The foreground stance leg is screen-left.",
14:"SCREEN-SPACE POSE OVERRIDE: screen-left leg is weightbearing, knee visibly flexed, boot planted at y=0.92. Screen-right knee swings forward underneath body. Pelvis compresses down 15px.",
15:"SCREEN-SPACE POSE OVERRIDE: screen-left leg supports weight, foot planted at y=0.92; screen-right knee lifted HIGH FORWARD at y=0.69, boot tucked near y=0.80. This is the opposite passing/midstance from frame07.",
16:"SCREEN-SPACE POSE OVERRIDE: screen-left heel lifts and pushes through its toe at ground y=0.92; screen-right knee leads forward, its shin unfolds toward camera. Pelvis rises, leading into the next left-leg flight."
}
out=[]
for x in queue:
    if not x['slot'].startswith('run-S-'):continue
    d=ROOT/'generation'/x['slot']
    if (d/'native.png').exists():continue
    i=int(x['slot'].split('-')[-1])
    ref=ROOT/'generation'/('run-S-04' if i<=8 else 'run-S-12')/'native.png'
    refs=[str(ref)]+x['refs']
    prompt=("Edit reference1 to one NEW independent running pose. Preserve EXACT chibi face/body scale, perspective, clothing, golden boot ornaments, spear design and painted finish. Change limb pose and shoulder/elbow angles as requested. References2/3/4 are idle identity, portrait, approved style. "+x['prompt']+"\n"+screen[i]+"\nBoth hands remain gripping the same positions on the shaft, but CHANGE the whole spear and both elbow angles with natural chest counter-rotation. Do not freeze arms in idle: at passing pose tilt the shaft about 8 degrees flatter and draw the lower hand inward 20px while rotating shoulders to counter the lead thigh. Retain anatomical LEFT high grip / RIGHT lower grip. Whole body fits fully inside canvas, no new props or effects.")
    (d/'prompt-continuation.txt').write_text(prompt,encoding='utf-8')
    (d/'request.json').write_text(json.dumps({'referenced_image_paths':refs,'transparent_background':True,'model':None,'quality':None,'prompt_file':'prompt-continuation.txt'},ensure_ascii=False,indent=2),encoding='utf-8')
    out.append({'slot':x['slot'],'prompt':prompt,'refs':refs})
(ROOT/'generation/run-s-continuation-queue.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([x['slot'] for x in out]))

