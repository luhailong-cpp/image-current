from pathlib import Path
from PIL import Image
import importlib.util,json,hashlib
D=Path(__file__).resolve().parent;BASE=D.parent.parent
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);sources=helper.Sources()
frame=[30550,40200,31804,41454];before,pieces,missing=sources.extract(frame);assert not missing
bp=D/'bench-G3-left-conditioned-v6-before-guide-native1254.png';assert not bp.exists();before.save(bp)
guide=Image.new('RGB',(1254,1254),'white');guide.paste(before.crop((386,256,749,924)),(386,256))
gp=D/'bench-G3-left-conditioned-v6-intact-neighborhood-guide-native1254.png';assert not gp.exists();guide.save(gp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=D/'current-native-guide-manifest-v2-bench-G3.json';assert not mp.exists();mp.write_text(json.dumps({'schemaVersion':1,'guides':[{'name':'bench-G3-left','frameWorld':frame,'file':str(bp),'sha256':sha(bp),'sourcePieces':pieces}],'canonicalSelectionsModified':False},indent=2),encoding='utf-8')
text=(D/'check_native_rect_generation_v1.py').read_text();text=text.replace("(D/'current-native-guide-manifest-v1.json')","Path(job.get('sourceGuideManifest',str(D/'current-native-guide-manifest-v1.json')))")
cp=D/'check_native_rect_generation_v3.py';assert not cp.exists();cp.write_text(text)
print(json.dumps({'guide':str(gp),'before':str(bp),'manifest':str(mp),'sourcePieces':len(pieces)}))

