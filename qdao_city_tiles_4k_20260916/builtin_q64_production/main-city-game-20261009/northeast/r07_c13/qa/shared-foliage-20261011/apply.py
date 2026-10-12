from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,importlib.util,shutil,argparse
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;T=D.parents[1];Z=T.parent;C=T/'candidates/r07_c13.candidate.png'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
H=Z/'r07_c14/qa/native-repairs/m03-shared-handoff.json'
def replay():
 spec=importlib.util.spec_from_file_location('prior_native_replay',T/'qa/finish-20261011/apply-v3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 before,prior=m.replay(False)
 record=read(H);src=Path(record['native']);maskp=Path(record['mask'])
 assert sha(src)==record['nativeSha256'];assert sha(maskp)==record['maskSha256']
 core=read(Path(str(src)+'.generation.json'));assert core['sha256']==sha(src)
 for ref in core['references']:assert sha(ref['file'])==ref['sha256']
 assert Image.open(src).size==(1254,1254)
 crop=record['westCropLocalBox'];target=record['westPasteTileBox'];mask=Image.open(maskp).convert('L').crop(crop)
 canvas=before.copy();canvas.paste(Image.open(src).convert('RGB').crop(crop),tuple(target[:2]),mask)
 diff=ImageChops.difference(before,canvas)
 support=Image.new('L',canvas.size);support.paste(mask.point(lambda v:255 if v else 0),tuple(target[:2]));outside=diff.copy();outside.paste((0,0,0),(0,0),support);assert outside.getbbox() is None
 return canvas,before,{'priorReplay':str(T/'qa/finish-20261011/replay-v3.json'),'priorReplaySha256':sha(T/'qa/finish-20261011/replay-v3.json'),'nativeCoreCount':16,'priorRepairLayerCount':4,'handoff':str(H),'handoffSha256':sha(H),'source':str(src),'sourceSha256':sha(src),'mask':str(maskp),'maskSha256':sha(maskp),'sourceCrop':crop,'destinationTileBox':target,'edgeTaperPixels':16,'sharedBoundaryTaper':False,'resized':False,'changedPixelBox':diff.getbbox(),'outsideMaskPixelIdentical':True}
def main(check):
 canvas,before,r=replay()
 if check:
  assert sha(C)==read(D/'replay.json')['outputSha256'];assert ImageChops.difference(canvas,Image.open(C).convert('RGB')).getbbox() is None
  save(D/'verification.json',{'pixelReplayIdentical':True,'sourceBytesVerified':True,'outsideMaskPixelIdentical':True,'candidateSha256':sha(C),'nativeCoreCount':16,'repairLayerCount':5});print(json.dumps({'verified':True,'candidateSha256':sha(C)}));return
 assert sha(C)=='f6152184557308b5db907905cc9648e43fe06e9831d8c2a823a4b7fa2ad89a2c'
 assert ImageChops.difference(before,Image.open(C).convert('RGB')).getbbox() is None
 shutil.copy2(C,D/'before.candidate.png');shutil.copy2(str(C)+'.generation.json',D/'before.generation.json')
 canvas.save(C);r.update({'output':str(C),'outputSha256':sha(C),'createdAt':datetime.now(timezone.utc).isoformat()});save(D/'replay.json',r)
 side=read(D/'before.generation.json');side.update({'sha256':sha(C),'recipe':str(D/'replay.json'),'sourceReplay':str(Path(__file__)),'repairLayerCount':5,'visualReview':'shared foliage pending local review','operation':{'method':'16 native cores + 4 prior native masked repairs + shared native foliage west strip','resized':False,'sharedStripOuterEdgeTaperPixels':16}});save(Path(str(C)+'.generation.json'),side)
 p=read(T/'tile-progress.json');p.update({'candidateSha256':sha(C),'internalPassed4kCount':0,'status':'complete_4k_candidate_shared_foliage_pending_final_review','selectedRepairCount':5});save(T/'tile-progress.json',p)
 canvas.crop((3712,2842,4096,4096)).save(D/'west-strip-context-100pct.png')
 print(json.dumps({'candidateSha256':sha(C),'changedPixelBox':r['changedPixelBox']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)

