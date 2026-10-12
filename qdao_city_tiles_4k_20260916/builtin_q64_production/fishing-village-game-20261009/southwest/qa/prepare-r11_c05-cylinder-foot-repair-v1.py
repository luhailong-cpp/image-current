import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
a=read(z/'qa/full-tile-r11_c05-assembly.json')
preview=z/'qa/r11_c05-composition-preview-v1.png'
assert not preview.exists();im=Image.open(a['output']['path']);im.thumbnail((1400,1400));im.save(preview)
source=z/'qa/r11_c05-cylinder-foot-repair-v1-source-native.png'
assert not source.exists();box=[1390,1580,2644,2834]
Image.open(a['output']['path']).crop(box).save(source)
prod.write(z/'qa/r11_c05-internal-visual-audit-v1.json',{'createdAtUtc':prod.now(),'tile':'r11_c05','status':'repair_required','reviewer':'root','candidate':a['output'],'context':a['context'],'assembly':ref(z/'qa/full-tile-r11_c05-assembly.json'),'nativeQaWindowsViewed':39,'viewed':[{'file':q['file'],'sha256':q['sha256'],'viewedAtNativeScale':True,'result':'repair_required' if any(s in q['file'] for s in ['v2048-part03','h2048-part03','intersection-x2048-y2048']) else 'pass'} for q in a['qa']],'issues':[{'id':'red-cylinder-foot','coreBox':[1800,1980,2160,2270],'finding':'One short stepped notch breaks red cylinder lower gold band and bottom silhouette at shared native edge; three QA windows show same defect.','repairStatus':'prepared_not_submitted'}],'completionClaim':False})
refs=read(z/'references.json')
req={'stem':'r11_c05_cylinder_foot_repair_v1','tile':'r11_c05','patch':'localized-repair-red-cylinder-foot','coordinates':{'role':'localized native seam repair','globalContextBox':[17774,42540,19028,43794],'expectedNativeDimensions':[1254,1254]},'references':[{'path':source.as_posix(),'role':'edit target exact native crop; preserve framing'},refs[1],refs[2]],'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'baseAssembly':ref(z/'qa/full-tile-r11_c05-assembly.json'),'repairCoreBox':box,'requestedModelPreference':'Free/included GPT Image2.5 preferred; existing builtin fallback authorized. Actual model undisclosed.'}
prod.write(z/'native/r11_c05_cylinder_foot_repair_v1.request.json',req)
print(json.dumps({'source':ref(source),'preview':ref(preview),'audit':ref(z/'qa/r11_c05-internal-visual-audit-v1.json'),'refs':req['references']}))

