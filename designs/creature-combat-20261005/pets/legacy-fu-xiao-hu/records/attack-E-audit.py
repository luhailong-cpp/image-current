from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent; R=B/'records'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]; hashes=set()
for i in range(1,13):
 n=f'{i:02}'; p=B/'runtime/attack/E'/f'{n}.png'; native=R/'attack-E-native'/f'{n}.png'; gen=R/f'attack-E-{n}.generation.json'
 im=Image.open(p); a=im.getchannel('A'); r=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf8')); g=json.loads(gen.read_text(encoding='utf8'))
 assert im.size==(1024,1024) and im.mode=='RGBA' and a.getextrema()==(0,255)
 assert sha(p)==r['sha256'] and sha(native)==r['derivedFrom']['sha256']==g['sha256']
 assert sha(p) not in hashes; hashes.add(sha(p))
 for ext in ['prompt.txt','receipt.json']: assert (R/f'attack-E-{n}.{ext}').is_file()
 assert g['actualModel'] is None and g['actualQuality'] is None
 rows.append({'frame':i,'file':str(p.relative_to(B)).replace('\\','/'),'sha256':sha(p),'nativeSha256':sha(native),'alphaBoundingBox':a.getbbox(),'opaqueBoundingBox':a.point(lambda v:255 if v>=128 else 0).getbbox(),'nativeSize':[g['width'],g['height']]})
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'count':12,'durationMs':30,'sequenceMs':360,'dimensionsAndAlpha':'passed','uniqueSha256':'passed','perFrameSources':'passed','frames':rows,'visualReview':{'allNativeFramesViewed':True,'contactSheetViewed':'preview/attack-E-frames.jpg shows01-11;12 independently viewed','playback':'pending root combined preview review','identity':'same tiger, front three-quarter E','anatomy':'two forepaws two hind feet one tail; same right forepaw throughout','scope':'art assets only, not client verification'}}
(R/'attack-E-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
clean=[]
for row in rows:
 n=f"{row['frame']:02}"; p=(R/'attack-E-native'/f'{n}.png').resolve()
 assert p.parent==(R/'attack-E-native').resolve() and B.resolve() in p.parents
 gpath=R/f'attack-E-{n}.generation.json';g=json.loads(gpath.read_text(encoding='utf8'))
 g['sourceRetention']={'status':'native intermediate deleted after complete export and source audit','deletedAt':datetime.now(timezone.utc).isoformat(),'finalFile':row['file'],'finalSha256':row['sha256'],'historicalReferences':'native predecessor paths retained as historical provenance; not active runtime dependencies'}
 gpath.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf8')
 p.unlink(); clean.append({'path':str(p),'sha256':row['nativeSha256'],'reason':'final1024RGBA verified and no longer active generation reference'})
(R/'attack-E-cleanup.json').write_text(json.dumps({'deleted':clean,'preserved':['12 runtime PNG and export records','all prompts receipts generation records','shared identity/style/design references'],'hostCache':'outside authorized write directory; unchanged'},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))

