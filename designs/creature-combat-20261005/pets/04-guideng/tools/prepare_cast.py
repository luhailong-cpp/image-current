from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
existing=list((B/'runtime/cast/E').glob('*.png'))
i=next((n for n in range(1,17) if not (B/f'runtime/cast/E/{n:02}.png').exists()),17)
poses={
7:'Left branch is raised beside the outer edge of leaf hat (screen right), not behind head; bent elbow legible. Right lamp remains near lower chest. A restrained faint gold glimmer clusters at white flowers. Body same scale, no lean away.',
8:'Charge peak. Left branch high outside hat, left elbow opens slightly; right hand steadies lantern in front of right waist/low chest. Both arms form open curved gesture. Body gently upright, knees still bent. Small luminous osmanthus specks join lamp and branch, never cover face.',
9:'Start release. Left shoulder rotates and left arm extends branch diagonally toward LOWER RIGHT in front of torso; elbow remains soft. Right lantern stays raised and stable. Head turns very slightly toward target while retaining E front. Golden light gathers on branch tip.',
10:'Release begins. Left elbow unfolds further toward lower-right target, branch projects forward at shoulder/chest height, NOT up-left. Lantern stays in right hand screen left. A short sparse stream of warm golden osmanthus petals follows branch toward lower right; no large beam.',
11:'Release peak. Left arm reaches its strongest forward extension along lower-right attack axis, soft elbow. Right lantern upright and steady at lower chest. A compact warm gold burst and few white-gold petals beyond branch tip toward right/lower-right; all particles contained, torso and hands unobscured.',
12:'Release eases. Left elbow begins bending back 5 degrees from peak while branch still points lower-right. Right hand begins lowering lamp a little. Golden petals thin and dim; head and torso ease back from the small forward focus.',
13:'Both arms start recovery. Left branch retracts to in front of left shoulder, right lantern descends toward hip; elbow joint arcs continuous. Torso settles, knees slightly relax. Only three faint petals near branch, no outward beam.',
14:'Left branch returns to shoulder-front with elbow more bent; right lantern handle settles near hip height. Head returns to original calm angle. Ribbons settle a little later than body, no outward particles.',
15:'Near neutral hovering stance. Left branch angled upright at shoulder beside face; right arm relaxes lower and opens. Face calm, hips and floating knees almost original position. Only normal lantern inner light, no spell glow outside.',
16:'Complete recovery to calm floating combat ready stance, same E direction and proportions. Left hand holds branch upright at shoulder with natural small elbow bend, right hand lantern at hip side. Head slightly lifted from frame15, ribbons softly settle differently. Fresh independent pose, not duplicate frame01. No outgoing particles.'}
if i>16: print(json.dumps({'done':True}));raise SystemExit
base=(B/'prompts/E-cast/01.txt').read_text(encoding='utf-8')
import re
prompt=base.replace('frame 01 of 16',f'frame {i:02} of 16')
prompt=re.sub(r'Pose frame 01:.*?\n1024',f'Pose frame {i:02}: '+poses[i]+' Image 4 is the preceding frame: preserve exact identity, camera, zoom and pelvis location; advance the described shoulder/elbow/hand joints. BOTH feet visible, no crossed knees or changed near leg. Keep continuous lantern/branch size and hand ownership.\n1024',prompt,flags=re.S)
refs=['D:/work/image/designs/pets-xianling-20260924/source/04-guideng-E.png','D:/work/image/designs/pets-xianling-20260924/source/04-guideng-W.png','D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png',str(B/f'runtime/cast/E/{i-1:02}.png')]
(B/f'prompts/E-cast/{i:02}.txt').write_text(prompt,encoding='utf-8')
cfg=json.loads((B/'records/E-cast/01.json').read_text(encoding='utf-8'))['configSnapshot']
print(json.dumps({'frame':i,'base':str(B).replace('\\','/'),'prompt':prompt,'refs':refs,'cfg':cfg},ensure_ascii=True))
