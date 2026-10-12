from pathlib import Path
import sys,os,json
os.environ['ISLAND_PROGRESS_FILE']='progress-r12_c11.json'
from workflow import ROOT,read,write,sha,progress
pid,version,target,desc=sys.argv[1:5]
assert not (ROOT/'native'/f'{pid}_{version}.png').exists()
f=ROOT/'native'/target
refs=[{'file':str(f),'sha256':sha(f),'role':'Actual native edit target, preserve its coordinates and all unaffected content'}]+read(ROOT/'references.json')
prompt='Edit the first attached image at its exact native 1254 x1254 size. It is an existing continuous daylight Q-painted game-art crop. Last three images are the full layout, material and approved style references. '+desc+' Return one opaque native square. Keep all unmentioned content exactly the same. Do not resize, zoom or change framing; no new object, label or watermark.'
pf=ROOT/'prompts'/f'{pid}_{version}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{pid}_{version}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
progress(status='generating',currentPatch=pid,nextStep='Precise native material repair recorded')
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
