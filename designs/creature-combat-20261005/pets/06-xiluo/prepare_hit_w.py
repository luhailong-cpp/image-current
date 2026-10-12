import json, re, sys
from pathlib import Path
R=Path(__file__).resolve().parent
f=int(sys.argv[1])
base=(R/'prompts/hit/W/01.txt').read_text(encoding='utf-8').strip()
poses={
3:"Maximum impact compression, W frame03 of06 at80ms. From reference4 frame02, bend the same six crab support legs a little more at their original natural joints; shell tips back another 3 degrees but keeps EXACTLY THE SAME size and cloud pattern geometry. Lower body only another 10 native pixels. Visible near pincer folds higher against the hidden upper-left face as a tight guard, far pincer remains appropriately hidden. Eyestalk retracts almost entirely behind shell edge. Small recoil of bell and silk. Back view stays unchanged: no frontal face/chest. Keep feet in the same ground spots; no stepping or global shifting.",
4:"Mid recovery, W frame04 of06 at120ms. The same planted six walking legs partly straighten, body rises halfway from compressed guard toward original W neutral height. Shell begins returning to original upright angle WITHOUT scale change. Near pincer unfolds halfway downward/outward toward its original upper-left guard, far pincer stays at its anatomical side. Original eyestalk emerges halfway. Rear shell still dominates. Do not reveal face/chest, no walking.",
5:"Late recovery, W frame05 of06 at160ms. The six legs straighten nearly to their original neutral stance, body and rear shell nearly upright. Near pincer lowers most of the way toward original W neutral. Eyestalk extends almost fully at the upper-left shell edge, never show frontal face. Silk and bell have tiny residual sway. Keep shell size and six support-foot positions unchanged.",
6:"Final settling, W frame06 of06 at200ms. Return almost exactly to original W neutral shell angle, size, support footprint and camera. Near pincer relaxed on original upper-left anatomical attachment, tiny residual inward bend; far pincer largely occluded. Eyestalk extends like original W reference, face/chest remain hidden. Six walking legs support in place. This is a newly AI-drawn distinct final recovery pose, not copied from frame01. No movement cycle."
}
prev=json.loads((R/f'receipts/hit/W/{f-1:02}.json').read_text(encoding='utf-8-sig'))
src=re.search(r' as (.+\.png) by default',prev['result']['output_hint']).group(1)
prompt=base.replace('frame01/06',f'frame{f:02}/06',1)
prompt=re.sub(r'POSE frame01/06:[\s\S]*?\nKeep identical', 'POSE: '+poses[f]+'\nReference4 is previous approved W hit frame, retain camera and geometry for continuity. All opaque parts including silk must stay comfortably inside edges.\nKeep identical',prompt)
args={'prompt':prompt,'referenced_image_paths':prev['arguments']['referenced_image_paths'][:3]+[src],'transparent_background':True}
(R/f'prompts/hit/W/{f:02}.txt').write_text(prompt,encoding='utf-8')
p=R/f'requests/hit/W/{f:02}.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(args,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(args,ensure_ascii=True))
