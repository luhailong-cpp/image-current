
"""Read-only artwork replay: emits only a JSON audit, never image files."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
import assemble as assembly
import local_repairs as repairs
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(s):
 p=Path(s);return p if p.is_absolute() else ROOT/p
def replay(tile):
 m=read(ROOT/tile/'output'/'assembly.json');arrays={};checks=[]
 for rec in m['nativeSources']:
  p=resolve(rec['nativeFile']);assert sha(p)==rec['nativeSha256']
  with Image.open(p) as im:
   assert im.size==(1254,1254);arrays[(rec['row'],rec['column'])]=np.array(im.convert('RGB'))
  checks.append({'file':str(p),'sha256':sha(p)})
 pixels,metrics=assembly.assemble_pixels(arrays,tuple(m['selectedRectangleInclusive']),m['composition']['maximumFeatherRadiusPixels'])
 core=pixels[115:-115,115:-115].copy();encoded=repairs.encode_png(core);actual=hashlib.sha256(encoded).hexdigest()
 assert actual==m['output']['sha256'],f'{tile} replay assembly hash mismatch'
 result={'tile':tile,'sourceCount':len(checks),'sources':checks,'baseAssemblyPngHashMatches':True,'baseAssemblySha256':actual,'repairStages':[]}
 if tile=='r10_c05':
  for name in ['wood','stone']:
   rp=ROOT/tile/'repairs'/'native'/f'{name}.png.generation.json';r=read(rp)
   assert r['inputCandidateSha256']==actual
   assert sha(r['file'])==r['sha256'];l,t,rr,bb=r['candidateBox']
   with Image.open(r['file']) as im:native=np.array(im.convert('RGB'))
   repaired,detail=repairs.quilt(core[t:bb,l:rr].copy(),native,2)
   core[t:bb,l:rr]=repaired;actual=hashlib.sha256(repairs.encode_png(core)).hexdigest()
   result['repairStages'].append({'id':name,'nativeHashVerified':True,'inputCandidateHashVerified':True,'outputSha256':actual,'nativeCorePreserved':detail.get('nativeCorePreservedExactly'),'sourceResampling':False})
  target=ROOT/tile/'repairs'/'output'/'r10_c05.repaired.candidate.png'
 else:target=resolve(m['output']['file'])
 with Image.open(target) as im:current=np.array(im.convert('RGB'))
 diff=np.any(core!=current,axis=2)
 result.update({'currentOutput':str(target),'currentSha256':sha(target),'replayedSha256':actual,'totalPixels':int(diff.size),'differentPixelCount':int(diff.sum()),'byteHashMatches':actual==sha(target),'pixelReplayPassed':not diff.any(),'noArtWritten':True})
 assert result['pixelReplayPassed'] and result['byteHashMatches']
 return result
results=[replay('r10_c05'),replay('r11_c05')]
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'gateActive':True,'operation':'Replay existing native images and existing seam algorithms entirely in memory; exact PNG hashes and every output pixel compared. No generation requests and no image writes.','results':results,'totalComparedPixels':sum(r['totalPixels'] for r in results),'differentPixelCount':sum(r['differentPixelCount'] for r in results),'passed':True,'limitation':'Pixel reproduction does not revalidate a missing historic style reference, visual quality, walkability or capacity.','missingReference':'D:/work/image/designs/mail-ui-v1/01-mail-event.png','actualModel':None,'actualQuality':None,'formalAccepted':False}
out=ROOT/'capacity-source-replay.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(out),'totalComparedPixels':report['totalComparedPixels'],'differentPixelCount':report['differentPixelCount'],'passed':True}))

