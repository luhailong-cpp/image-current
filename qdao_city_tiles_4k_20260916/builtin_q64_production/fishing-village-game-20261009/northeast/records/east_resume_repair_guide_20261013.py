import importlib.util,json,sys,hashlib
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('e',Z/'records/east_resume_r04_20261013.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
p,version,base=sys.argv[1:]
plan=json.loads((Z/'records'/f'{p}.plan.json').read_text(encoding='utf-8-sig'))
src=Z/'native'/f'{p}-{base}.png';im=Image.open(src).convert('RGB')
for edge in plan['nativeEdgeSources']:
 n=Image.open(edge['path']).convert('RGB');im.paste(n.crop(edge['cropBox']),tuple(edge['pasteAt']))
guide=Z/'guides'/f'{p}-{version}.native-anchor-repair.png';assert not guide.exists();im.save(guide)
plan['version']=version;plan['repairOf']=e.b.ref(src,'repair target');plan['references']=plan['references'][:3]+[e.b.ref(src,'repair target'),e.b.ref(guide,'exact native anchors replaced for guidance only')]
e.write(Z/'records'/f'{p}-{version}.plan.json',plan);e.write(Path(str(guide)+'.derived.json'),{'purpose':'guidance only, never final pixels','operation':'integer crops of native anchors pasted over failed candidate','source':e.b.ref(src,'target'),'nativeEdgeSources':plan['nativeEdgeSources']});print(guide)
