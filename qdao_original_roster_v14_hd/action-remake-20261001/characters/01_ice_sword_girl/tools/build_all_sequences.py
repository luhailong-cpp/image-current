"""Inventory and preview real exported frames; never manufacture missing poses."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image
R=Path(__file__).resolve().parents[1]
SPEC={'run':(['S','SE','E','NE','N','NW','W','SW'],16,60),'hit':(['E','W'],6,40),'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
retirement_path=R/'review/retired-image-sources.json'
retirement=read(retirement_path) if retirement_path.exists() else {}
retired={x['file']:x['sha256'] for x in retirement.get('removedFiles',[])} if retirement.get('status')=='applied' else {}
proof_path=R/'review/delivery-provenance.json'
proof=read(proof_path) if proof_path.exists() else {}
attested={x['file']:x for x in proof.get('frames',[])} if proof.get('passed') else {}
sequences=[]; errors=[]; seen={}
for action,(dirs,count,ms) in SPEC.items():
 for direction in dirs:
  selection_path=R/'review'/f'{action}-{direction}-selection.json'
  if action!='run':selection_path=R/'review'/f'combat-{action}-{direction}-selection.json'
  selection=read(selection_path) if selection_path.exists() else {}
  frames=[]
  for i in range(1,count+1):
   p=R/f'candidate/{action}/{direction}/{i:02}.png'
   if not p.exists():continue
   record=p.with_name(p.name+'.generation.json'); problems=[]
   if not record.exists():problems.append('missing_generation_record');rec={}
   else:rec=read(record)
   im=Image.open(p)
   if im.size!=(1024,1024) or im.mode!='RGBA':problems.append('not_1024_RGBA')
   if im.mode=='RGBA' and im.getchannel('A').getextrema()!=(0,255):problems.append('alpha_range')
   file_sha=sha(p)
   if rec.get('sha256')!=file_sha:problems.append('record_sha_mismatch')
   native=rec.get('nativeFrameSize',[])
   if len(native)!=2 or min(native)<1024:problems.append('native_size_unverified')
   derived=rec.get('derivedFrom',{})
   source=derived.get('file') or derived.get('path') or rec.get('sourcePath')
   source_path=R/source if source else None
   if not source_path or not source_path.exists():
    prior=attested.get(p.relative_to(R).as_posix(),{})
    if not (source and retired.get(source)==derived.get('sha256') and prior.get('sha256')==file_sha and prior.get('native')==source):problems.append('missing_native_source_without_retirement_proof')
   elif derived.get('sha256')!=sha(source_path):problems.append('native_source_sha_mismatch')
   pixels=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
   if pixels in seen:problems.append('duplicate_pixels:'+seen[pixels])
   seen[pixels]=p.relative_to(R).as_posix()
   f={'frame':i,'path':p.relative_to(R).as_posix(),'sha256':file_sha,'durationMs':ms,'nativeSource':source,'generationRecord':record.relative_to(R).as_posix(),'technicalPass':not problems,'technicalErrors':problems}
   frames.append(f)
   if problems:errors.append({'file':f['path'],'errors':problems})
  sequences.append({'action':action,'direction':direction,'expectedFrames':count,'presentFrames':len(frames),'complete':len(frames)==count,'frameMs':ms,'cycleMs':ms*count,'selection':selection_path.relative_to(R).as_posix() if selection else None,'artStatus':selection.get('artStatus','not_yet_reviewed'),'offlineArtworkReviewComplete':selection.get('offlineArtworkReviewComplete',False),'eightConsecutiveSupportVerified':selection.get('eightConsecutiveSupportVerified',False) if action=='run' else None,'positionPairsVerified':selection.get('positionPairsVerified',False) if action=='run' else None,'dynamicArtAccepted':selection.get('dynamicArtAccepted',False),'remainingIssues':selection.get('remainingIssues',[]),'clientRuntimeVerified':False,'frames':frames})
data={'schemaVersion':1,'characterId':R.name,'createdAt':datetime.now(timezone.utc).isoformat(),'targetFrameCount':196,'presentFrameCount':sum(s['presentFrames'] for s in sequences),'technicalPassCount':sum(f['technicalPass'] for s in sequences for f in s['frames']),'completeSequences':sum(s['complete'] for s in sequences),'sequenceCount':14,'clientIntegrated':False,'clientRuntimeVerified':False,'actualModel':None,'actualQuality':None,'modelQualityNote':'宿主管理路径未披露实际版本与质量；逐图记录保存配置目标、提交与返回证据。','sequences':sequences,'errors':errors}
write(R/'manifest.json',data)
write(R/'review/all-sequences.json',data)
(R/'preview/all-sequences.js').write_text('window.ALL_SEQUENCES='+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf-8')
print(json.dumps({k:data[k] for k in ['presentFrameCount','technicalPassCount','completeSequences','errors']},ensure_ascii=False))
