from pathlib import Path
from PIL import Image
from io import BytesIO
import hashlib,json
T=Path(__file__).resolve().parent;C=T/'candidates'/f'{T.name}.candidate.png';Q=T/'qa'/'native-repairs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pixsha(im):
 b=BytesIO();im.save(b,format='PNG');return hashlib.sha256(b.getvalue()).hexdigest()
d=json.loads(Path(str(C)+'.generation.json').read_text());base=Path(d['coreBaseline']['file']);assert sha(base)==d['coreBaseline']['sha256'];im=Image.open(base).convert('RGB');rows=[]
for r in d['repairs']:
 assert pixsha(im)==r['beforeCandidateSha256'];inp=r['input'];src=Image.open(inp['file']).convert('RGB');assert sha(inp['file'])==inp['sha256'];ox,oy=r['origin']
 if ox<0:assert im.crop((0,oy,ox+1254,oy+1254)).tobytes()==src.crop((-ox,0,1254,1254)).tobytes()
 else:assert im.crop((ox,oy,ox+1254,oy+1254)).tobytes()==src.tobytes()
 assert sha(r['native'])==r['nativeSha256'] and sha(r['mask'])==r['maskSha256'];new=Image.open(r['native']).convert('RGB');mask=Image.open(r['mask']).convert('L');im.paste(new,(ox,oy),mask);assert pixsha(im)==r['outputSha256']
 after=src.copy()
 if ox<0:after.paste(im.crop((0,oy,ox+1254,oy+1254)),(-ox,0))
 else:after=im.crop((ox,oy,ox+1254,oy+1254))
 assert after.tobytes()==Image.open(Q/(r['repair']+'-after.png')).convert('RGB').tobytes()
 rows.append({'repair':r['repair'],'inputOwnPixelsMatchPriorPhase':True,'nativeAndMaskHashMatch':True,'outputPngShaMatches':True,'afterPixelsMatch':True,'outputSha256':r['outputSha256']})
assert im.tobytes()==Image.open(C).convert('RGB').tobytes() and pixsha(im)==sha(C)==d['sha256']
report={'tile':T.name,'coreBaseline':d['coreBaseline'],'repairs':rows,'finalCandidate':str(C),'sha256':sha(C),'finalPixelsMatchReplay':True,'resampling':False,'status':'pass','note':'Historical western source phases are preserved in immutable joined repair input PNGs; current western final may include its own separately logged shared overlay.'}
(T/'qa'/'final-review'/'source-replay.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
