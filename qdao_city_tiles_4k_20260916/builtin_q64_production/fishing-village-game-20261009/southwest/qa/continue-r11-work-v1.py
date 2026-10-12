import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
j=read(z/'qa/r10r11c06-joint-repair-job-v1.json');stem=j['stem']
m={'outputPrefix':'pair-r10r11c06-final-v2','basePairTrace':ref(z/'qa/pair-r10r11c06-v1-trace.json'),'repairs':[{'id':'lantern-post','source':j['source'],'repair':ref(z/'native'/f'{stem}.png'),'generationRecord':ref(z/'native'/f'{stem}.png.generation.json'),'contextBox':j['contextBox'],'repairBounds':[140,15,1180,1240],'margin':40}]}
p=z/'qa/pair-r10r11c06-final-v2.manifest.json';assert not p.exists();prod.write(p,m)
old='r11_c05_p01_04_v1';new='r11_c05_p01_04_v2';gp=z/'native'/f'{old}.png.generation.json';g=read(gp);g['status']='rejected';g['rejectionReason']='Two blue/red decorative cylinders were copied from larger layout into wrong patch coordinates. Preserve rejected image; remove only misplaced additions in v2.';prod.write(gp,g)
r=read(z/'native'/f'{old}.request.json');r['stem']=new;r['references']=[{'path':(z/'native'/f'{old}.png').as_posix(),'role':'edit target: remove misplaced two cylinders only'},{'path':(z/'layout-only'/f'{old}_continuity.png').as_posix(),'role':'exact coordinate guide: no cylinders in this patch'},read(z/'references.json')[1],read(z/'references.json')[2]]
prompt='Use case: precise-object-edit. Image1 is the1254x1254 target. Remove ONLY the two incorrectly added standing cylinders at lower left: the tall blue cylinder and shorter red cylinder with red tassel. Those belong elsewhere on the map and must not exist in this cropped area. Replace only their former silhouettes with the dark green/golden foliage and wooden display structure seen in exact coordinate guide image2. Keep the entire giant white rabbit face, eye, coral cheek, ears, round chest/body, pose and scale pixel-aligned and unchanged. Keep the diagonal golden wooden rail across the bottom, left edge wooden post, background flowers and leaves, top native overlap and right native overlap exactly where they are. Do not add any new containers or objects. Image3-4 are style only. Preserve warm daylight and painterly Q texture, no zoom/reframe, output same native1254 square, no text/UI/border.'
prod.write(z/'native'/f'{new}.request.json',r);(z/'native'/f'{new}.prompt.txt').write_text(prompt,encoding='utf-8')
prod.write(z/'qa/r11_c05-p01_04-v2-job.json',{'stem':new,'prompt':prompt,'references':[x['path'] for x in r['references']]})
subprocess.run([sys.executable,'-B',str(z/'qa/native-pair-multi-repair-compose.py'),'--manifest',str(p)],check=True)
