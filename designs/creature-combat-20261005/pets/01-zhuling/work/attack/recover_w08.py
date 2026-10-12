from pathlib import Path
import json,re,hashlib
from PIL import Image
B=Path(r'D:/work/image/designs/creature-combat-20261005/pets/01-zhuling')
log=Path(r'C:/Users/luyua/.codex/sessions/2026/10/05/rollout-2026-10-05T06-53-14-01a10bb2-400d-70f2-98e4-54d0e81e68a2.jsonl')
prompt=None;event=None
for line in log.open(encoding='utf-8'):
 r=json.loads(line);p=r.get('payload',{})
 if r.get('ordinal')==636:
  prompt=p['input'].split('store("w8fixPrompt",`',1)[1].rsplit('`);',1)[0]
 if r.get('ordinal')==658:
  event={k:v for k,v in p['item'].items() if k!='result'};returned=r['timestamp']
assert prompt and event and event['revisedPrompt']==prompt
src=Path(event['savedPath']);assert src.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads(Path(r'D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
old=json.loads((B/'records/attack/W/08.attempt-01.rejected.json').read_text(encoding='utf-8-sig'))
refs=[old['derivedFrom']['originalPath'],r'C:/Users/luyua/.codex/generated_images/01a10bb2-400d-70f2-98e4-54d0e81e68a2/exec-dabd14a1-051e-42b4-b184-234a9da7e962.png',r'D:/work/image/designs/pets-xianling-20260924/source/01-zhuling-W.png',r'D:/work/image/designs/pets-xianling-20260924/source/01-zhuling-E.png',r'D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png']
roles=['edit target rejected W08 three-wing attempt','preceding correct W07 native pose and anatomy','original W identity and camera','original E supplemental anatomy','main confirmed painterly style']
receipt={'startedAt':'2026-10-05T20:21:31.612Z','returnedAt':returned,'tool':'image_gen.imagegen','route':'builtin','event':event,'recoveryEvidence':{'sourceSession':str(log),'promptOrdinal':636,'callOrdinal':646,'completionOrdinal':658},'submittedParameters':{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True,'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未提供 model/quality 选择器，完成事件未披露真实版本或质量。'}
(B/'prompts/attack/W/08.txt').write_text(prompt,encoding='utf-8')
(B/'records/attack/W/08.receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
with Image.open(src) as im:
 native={'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'sha256':sha(src)}
 canvas=Image.new('RGBA',(1024,1024));canvas.alpha_composite(im.convert('RGBA').resize((820,820),Image.Resampling.LANCZOS),(102,102))
 out=B/'runtime/attack/W/08.png';canvas.save(out)
rec={'action':'attack','direction':'W','frame':8,'file':'runtime/attack/W/08.png','sourcePath':str(src),'sha256':sha(out),'width':1024,'height':1024,'durationMs':30,'pivot':[0.5,0.08],'event':None,'generatedAt':returned,'startedAt':receipt['startedAt'],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':receipt['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':receipt['unverifiedReason'],'prompt':'prompts/attack/W/08.txt','references':[{'path':p,'role':role} for p,role in zip(refs,roles)],'evidence':{'receipt':'records/attack/W/08.receipt.json','generationId':event['id']},'native':native,'derivedFrom':{'path':str(src),'sha256':sha(src)},'operation':'Full native square canvas resized to 820x820, alpha-composited at (102,102) on transparent 1024x1024 canvas; no bbox fitting or per-frame alignment.','alphaExtrema':canvas.getchannel('A').getextrema(),'alphaBBox':canvas.getchannel('A').getbbox(),'visualStatus':'individually inspected; two wings repaired; full sequence pending','editingSource':{'record':'records/attack/W/08.attempt-01.rejected.json'},'recoveryNote':'Recovered completed native output after interrupted persistence, using original session prompt/call/completion events; no new model call.'}
target=B/'records/attack/W/08.generation.json';target.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
side=B/'runtime/attack/W/08.png.generation.json'
if side.exists():side.unlink()
print(json.dumps({'output':str(out),'sha':sha(out),'native':native,'recovered':True}))
