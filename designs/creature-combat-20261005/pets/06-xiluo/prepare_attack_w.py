import json, sys
from pathlib import Path
R=Path(__file__).resolve().parent
f=int(sys.argv[1])
base=(R/'prompts/attack/W/06.txt').read_text(encoding='utf-8-sig').split('Attack W frame')[0]
poses={
7:"STRIKE/CONTACT peak. The SAME near-side upper-left attacking pincer from reference4 frame06 fully CLOSES its two jaws and reaches a little higher along the same upper-left attack axis. Its elbow extends only a tiny amount; keep the leftmost claw tip safely INSIDE the same canvas margin, do not stretch farther left. No pincer swapping. Fixed shell/feet/camera; a small shoulder joint thrust only. Far pincer guards hidden behind the shell. No new weapon or effect.",
8:"Immediate follow-through/retraction onset. SAME raised near-side upper-left pincer is still close to frame07 extension, closed jaws with a tiny relaxed gap. Bend its elbow inward slightly, lower the claw about 20 native pixels, beginning the return along the SAME arc. Do not snap directly to neutral; keep shell size/feet exactly stable and rear camera unchanged.",
9:"Half retraction. Same near-side claw lowers along its connected elbow arc and folds inward halfway toward the original upper-left neutral guard. Elbow visibly bent, pincer sits adjacent to left shell edge at mid shell height, two jaws slightly relaxed. Preserve pincer size and attachment, no limb switching. Far pincer stays tucked. Rear shell and support feet fixed.",
10:"Late retraction. Same near-side pincer lowers back close to original W neutral guard beside the shell, elbow folded, tips now angle gently downward as in original W identity. It is about 85 percent returned from the strike. Retain continuous limb geometry, no new claw, no chest reveal. Shell and eye settle gently, feet support in place.",
11:"Settling. Same near pincer nearly in original W neutral position and original downward pointing jaw angle, slightly inward bent with tiny residual tension. Original visible eyestalk returns. Six crab walking feet stay planted. Same shell scale/ornaments/camera, no forward locomotion.",
12:"Final recovery. Return to original W identity neutral guard and shell angle with a small newly drawn final settling difference: same near pincer relaxed beside upper-left shell edge, tips down, elbow naturally folded, far pincer mostly concealed. Original rear view hides face/chest. Six feet on original ground footprint, silk and bell almost still. Distinct AI-drawn last frame, not copied or mirrored."
}
prev=json.loads((R/f'records/attack/W/{f-1:02}.json').read_text(encoding='utf-8-sig'))
src=prev['native']['path']
prompt=base+f'Attack W frame {f}/12, 30 ms. Current pose: '+poses[f]+'\nReference4 is previous frame, preserve exact geometry, size, fixed rear camera and limb root connections. Change only the specified crab joints and small settling details. No global translation, scale change, limb-count changes or duplicate claw outlines.'
args={'prompt':prompt,'referenced_image_paths':['D:/work/image/designs/pets-xianling-20260924/source/06-xiluo-E.png','D:/work/image/designs/pets-xianling-20260924/source/06-xiluo-W.png','D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png',src],'transparent_background':True}
(R/f'prompts/attack/W/{f:02}.txt').write_text(prompt,encoding='utf-8')
p=R/f'requests/attack/W/{f:02}.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(args,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared attack W '+str(f))
