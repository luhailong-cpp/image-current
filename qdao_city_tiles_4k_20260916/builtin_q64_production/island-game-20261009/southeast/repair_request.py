from pathlib import Path
import sys,json
from workflow import ROOT,read,write,sha,progress
pid,version,target,guide,description=sys.argv[1:6]
refs=[]
for file,role in [(ROOT/'native'/target,'EDIT TARGET'),(ROOT/'guides'/guide,'coordinate and immutable overlap guide')]:
 refs.append({'file':file.as_posix(),'sha256':sha(file),'role':role})
refs+=read(ROOT/'references.json')
prompt='Use case: precise-object-edit. Edit attached image 1 only, preserving its exact native 1254 x 1254 crop, painting style, daylight and geometry. Image 2 is its exact coordinate and native overlap guide. Last three images are full-map layout, material detail and primary approved Q Daoist painting style respectively. '+description+' Keep everything else identical. Do not shift, zoom, recompose, add ornaments, text, characters, interface or watermark. Single opaque square image.'
pf=ROOT/'prompts'/f'{pid}_{version}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{pid}_{version}.request.json',{'promptPath':pf.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
progress(status='generating',currentPatch=pid,nextStep='Precise builtin repair recorded; inspect native adjacency',lastError=None)
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False},ensure_ascii=True))

