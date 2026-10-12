from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
import local_repairs
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[('r09_c08','r09_c08/repairs-resume-20261012/lower-rim-elbow-v01/integrated/assembly.json','r09_c08/pipeline/qa/c60755460eef51ba/visual-review-20261012.json'),('r13_c05','r13_c05/pipeline/output/58c1da5acdb9a915/assembly.json','r13_c05/pipeline/qa/full-native-review-20261012.json')]
cat=read(B/'current-candidates.json');out=[]
for tile,rel,review in items:
 ap=B/rel;a=read(ap);ctx=a['contextOutput'];core=a['output']
 for e in [ctx,core]:assert sha(e['file'])==e['sha256']
 old=np.array(Image.open(ctx['file']).convert('RGB'));im=np.array(Image.open(core['file']).convert('RGB'))
 assert old.shape==(4326,4326,3) and im.shape==(4096,4096,3) and np.array_equal(im,old[115:4211,115:4211])
 for n in a['nativeSources']:
  assert sha(n['nativeFile'])==n['nativeSha256'] and Image.open(n['nativeFile']).size==(1254,1254)
  assert sha(n['recordFile'])==n['recordSha256'] and sha(n['receiptFile'])==n['receiptSha256']
 for step in a.get('localNativeRepairs',[]):
  assert sha(step['generationRecord'])==step['generationRecordSha256'] and sha(step['native'])==step['nativeSha256']
  g=read(step['generationRecord']);assert sha(g['sourceOutputPath'])==g['sha256']
  assert sha(g['evidence']['toolReceipt'])==g['evidence']['toolReceiptSha256']
  assert sha(g['inputContext'])==g['inputContextSha256']
  base=np.array(Image.open(g['inputContext']).convert('RGB'));native=np.array(Image.open(g['file']).convert('RGB'))
  l,t,r,b=step['contextBox'];mixed,details=local_repairs.quilt(base[t:b,l:r],native,2);base[t:b,l:r]=mixed
  assert np.array_equal(base,old) and details['alphaSha256Uint8RowMajor']==step['quilting']['alphaSha256Uint8RowMajor']
 report={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','assembly':str(ap),'assemblySha256':sha(ap),'coreAndContextHashesVerified':True,'nativeSourceAndReceiptHashesVerified':True,'coreEqualsContextCrop':True,'repairCompositionReproduced':bool(a.get('localNativeRepairs')),'workerReview':str(B/review),'formalAccepted':False,'internalPassed':False}
 if tile=='r09_c08':report.update(rootViewed=['lower-rim-elbow-v01/integrated/native-review-crop.png'],findings=['Local lower ring borders visibly smooth; quiet stone texture still dense/clouded. Upper ring breaks and external boundary review remain open.'])
 else:report.update(rootViewed=['external-top-native/TOP-4.png','58c1da5acdb9a915/native-qa/V3-3.png'],findings=['TOP4 abrupt cream wall to projecting gray stone ledge confirms geometry failure. V3 row3 red plinth and leaf edges have triangular cuts; dense surface pattern remains. Other worker QA findings retained.'])
 rp=ap.parent/'root-provenance-and-targeted-review.json';assert not rp.exists();atomic_json(rp,report)
 cat['tiles'][tile]={'tile':tile,'source':'current-native-provisional-with-open-QA','assembly':str(ap),'candidate':core,'context':ctx,'formalAccepted':False,'internalPassed':False,'review':str(rp)};out.append({'tile':tile,'review':str(rp)})
cat.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),complete4kCandidateCount=len(cat['tiles']),formalAcceptedCount=0)
atomic_json(B/'current-candidates.json',cat)
print(json.dumps(out))
