from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
from PIL import Image
import numpy as np
OUT=Path(__file__).parent; REVIEW=OUT.parent.parent; BASE=REVIEW.parent.parent; PROD=BASE/'island-game-20261009/southeast'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
snap=read(OUT/'metadata-snapshot.json'); docs=snap['documents']; supplemental={}; checks=[]
def capture(p):
 p=Path(p);a=p.stat();b=p.read_bytes();z=p.stat();h=hashlib.sha256(b).hexdigest();c={'file':str(p),'sha256':h,'bytes':len(b),'stableDuringRead':a.st_mtime_ns==z.st_mtime_ns and a.st_size==z.st_size}; checks.append(c);return b,c
for n in ['production-resume-wall-20261013.json','resume-right-current-batch-20261013.json','qa/returned-batch-resume-20261013/root-visual-review.json','qa/r13_c11-resume-20261013-v01/source-pixel-proof.json','qa/r13_c11-resume-20261013-v01/root-independent-review-resume-20261013.json']:
 b,c=capture(PROD/n);supplemental[n]=json.loads(b.decode('utf-8-sig'))
write('supplemental-metadata-snapshot.json',{'capturedAtUtc':now(),'documents':supplemental,'checks':checks.copy()})
oldtiles={t['tileId']:t for t in read(REVIEW/'resume-v02/coverage-inventory.json')['tiles'] if t['zone']=='southeast'}
tiles={tid:{'tileId':tid,'coreCount':0,'fullCoverage':False,'adopted':False,'file':None,'sha256':None,'formalAccepted':False,'evidence':str(OUT/'metadata-snapshot.json'),'worldBox':t['worldBox']} for tid,t in oldtiles.items()}
candidate_checks=[]
for adopted, records in [(True,docs['progress.json']['currentAdoptedCandidates']),(False,docs['current-zone-counts-20261013.json']['pendingCandidates'])]:
 for x in records:
  tid=x['tile']; b,c=capture(x['candidate']); expected=x['sha256'];assert c['sha256']==expected
  old=oldtiles[tid];candidate_checks.append({**c,'tileId':tid,'matchesDeclaredHash':True,'baselineFile':old['file'],'baselineSha256':old['sha256'],'baselineHashUnchanged':old['sha256']==c['sha256']})
  tiles[tid].update(coreCount=16,fullCoverage=True,adopted=adopted,file=x['candidate'],sha256=c['sha256'],internalPassedAsRecorded=x['internalPassed'],evidence={'frozenMetadata':str(OUT/'metadata-snapshot.json'),'productionReview':x.get('review')})
partial={
 'r14_c11':(docs['progress-r14_c11.json']['selectedVersions'],'progress-r14_c11.json'),
 'r13_c13':(supplemental['resume-right-current-batch-20261013.json']['selected'],'resume-right-current-batch-20261013.json'),
 'r14_c14':(docs['r14_c14-quick-review-20261013.json']['selected'],'r14_c14-quick-review-20261013.json'),
 'r08_c10':({re.search(r'_p(\d{2})$',k)[1]:v['version'] for k,v in supplemental['production-resume-wall-20261013.json']['generated'].items() if v['status'].startswith('quick_')},'production-resume-wall-20261013.json')}
for tid,(versions,authority) in partial.items():
 selected=[]
 for coord,v in versions.items():
  p=PROD/'native'/f'{tid}_p{coord}_{v}.png';b,c=capture(p);im=Image.open(p);assert im.size==(1254,1254);selected.append({**c,'coordinate':coord,'version':v,'dimensions':list(im.size)})
 tiles[tid].update(coreCount=len(selected),selectedNativeCores=selected,evidence={'authority':str(PROD/authority),'frozenSnapshot':str(OUT/('supplemental-metadata-snapshot.json' if authority in supplemental else 'metadata-snapshot.json'))})
# Explicit pending sources remain excluded from selected-core counts.
unselected=[]
for tid,coords in [('r14_c11',['14_v01','34_v01']),('r14_c14',['14_v01']),('r08_c10',['24_v01','44_v01']),('r13_c13',['11_v01','13_v01','13_v02','24_v01'])]:
 for cv in coords:
  p=PROD/'native'/f'{tid}_p{cv}.png'
  if p.exists():b,c=capture(p);unselected.append({**c,'tileId':tid,'patchVersion':cv,'countedAsSelected':False,'status':'saved_not_passed_or_superseded','evidence':str(OUT/'supplemental-metadata-snapshot.json')})
ims={tid:Image.open(t['file']).convert('RGB') for tid,t in tiles.items() if t['file']}
# New r13 full candidate: exact contributions, no synthesized or blended pixels.
proof=supplemental['qa/r13_c11-resume-20261013-v01/source-pixel-proof.json'];arr=np.array(ims['r13_c11']);coverage=np.zeros((4096,4096),np.uint8); replay=[]
for s in proof['sources']:
 b,c=capture(s['file']);assert c['sha256']==s['sha256'];im=Image.open(s['file']).convert('RGB');a=s['sourceCrop'];d=s['destinationBox'];pixels=np.array(im.crop(a));dst=arr[d[1]:d[3],d[0]:d[2]];m=int(np.any(pixels!=dst,axis=2).sum());coverage[d[1]:d[3],d[0]:d[2]]+=1;replay.append({**c,'sourceCrop':a,'destinationBox':d,'mismatchedPixels':m})
assert int(coverage.min())==int(coverage.max())==1 and sum(x['mismatchedPixels'] for x in replay)==0
write('r13_c11-source-proof.json',{'candidate':tiles['r13_c11']['file'],'sha256':tiles['r13_c11']['sha256'],'sourceCount':len(replay),'sources':replay,'coverageMin':int(coverage.min()),'coverageMax':int(coverage.max()),'mismatchedPixels':0})
# Existing reviewed edges are replayed only at the narrow current crops. No full assembly or history scan.
oldremaining=read(REVIEW/'resume-v02/southeast-remaining/summary.json');reuse=[]
def worldcrop(box,tids):
 out=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));covered=0
 for tid in tids:
  tb=tiles[tid]['worldBox'];x1=max(tb[0],box[0]);y1=max(tb[1],box[1]);x2=min(tb[2],box[2]);y2=min(tb[3],box[3])
  if x1<x2 and y1<y2:out.paste(ims[tid].crop((x1-tb[0],y1-tb[1],x2-tb[0],y2-tb[1])),(x1-box[0],y1-box[1]));covered+=(x2-x1)*(y2-y1)
 assert covered==out.width*out.height
 return out
for edge in oldremaining['newEdgeReviews']:
 parts=[]
 for s in edge['segments']:
  previous=Image.open(s['file']).convert('RGB');current=worldcrop(s['worldBox'],edge['tiles']);b,c=capture(s['file']);assert c['sha256']==s['sha256'];same=previous.size==current.size and previous.tobytes()==current.tobytes();parts.append({'file':s['file'],'sha256':c['sha256'],'pixelsMatchCurrent':same,'priorStatus':s['status']})
 reuse.append({'tiles':edge['tiles'],'allPixelsMatchCurrent':all(x['pixelsMatchCurrent'] for x in parts),'priorStatus':edge['status'],'segments':parts,'reused':all(x['pixelsMatchCurrent'] for x in parts)})
write('shared-edge-reuse.json',{'edgePairs':reuse,'allThirteenReusable':all(x['reused'] for x in reuse),'previousReview':str(REVIEW/'resume-v02/southeast-remaining/summary.json')})
# New exact-pixel crops only.
cuts=[]
def save(im,name,source,box=None,world=None,kind=None):
 q=OUT/(name+'.png');q.parent.mkdir(parents=True,exist_ok=True);im.save(q);assert Image.open(q).convert('RGB').tobytes()==im.tobytes();rec={'file':str(q),'sha256':sha(q),'source':source,'sourceBox':box,'worldBox':world,'dimensions':list(im.size),'pixelExact':True,'kind':kind,'visualReview':'pending'};cuts.append(rec);return im
im=ims['r13_c11'];local=[('new-bottom-v-c2',(1792,3072,2304,4096)),('new-bottom-v-c3',(2816,3072,3328,4096)),('new-bottom-h-c3',(2048,2816,3072,3328)),('new-bottom-h-c4',(3072,2816,4096,3328)),('new-bottom-j-c2',(1792,2816,2304,3328)),('new-bottom-j-c3',(2816,2816,3328,3328)),('column-left',(3328,0,3840,1024)),('column-bottom',(3584,768,4096,1280))]
for name,box in local:save(im.crop(box),'r13_c11/'+name,tiles['r13_c11']['file'],list(box),kind='internal_delta')
for side,tids,edge in [('north',['r12_c11','r13_c11'],49152),('east',['r13_c11','r13_c12'],45056)]:
 for i in range(4):
  box=[40960+i*1024,edge-256,40960+(i+1)*1024,edge+256] if side=='north' else [edge-256,49152+i*1024,edge+256,49152+(i+1)*1024]
  save(worldcrop(box,tids),f'r13_c11/{side}-{i+1}',[tiles[t]['file'] for t in tids],world=box,kind='external_new_full_candidate')
box=[44800,48896,45312,49408];tids=['r12_c11','r12_c12','r13_c11','r13_c12'];save(worldcrop(box,tids),'r13_c11/northeast-junction',[tiles[t]['file'] for t in tids],world=box,kind='external_junction')
# Boards retain exact scale; rows ordered as named in manifests, without resizing.
boards=[]
groups=[('bottom-vertical',['new-bottom-v-c2','new-bottom-v-c3']),('bottom-horizontal',['new-bottom-h-c3','new-bottom-h-c4']),('bottom-junctions',['new-bottom-j-c2','new-bottom-j-c3']),('column',['column-left','column-bottom']),('north',[f'north-{i}' for i in range(1,5)]),('east',[f'east-{i}' for i in range(1,5)])]
for name,names in groups:
 xs=[next(x for x in cuts if Path(x['file']).stem==n) for n in names];width=max(x['dimensions'][0] for x in xs);height=sum(x['dimensions'][1] for x in xs);board=Image.new('RGB',(width,height));y=0;placements=[]
 for x in xs:piece=Image.open(x['file']);board.paste(piece,(0,y));placements.append({'file':x['file'],'position':[0,y],'size':list(piece.size)});y+=piece.height
 q=OUT/('board-'+name+'-100pct.png');board.save(q);boards.append({'file':str(q),'dimensions':list(board.size),'pieces':placements,'scale':1})
write('crop-manifest.json',{'cuts':cuts,'boards':boards,'operation':'exact integer crop and paste only; no scaling, filtering, blending or generation'})
write('candidate-reuse.json',{'checks':candidate_checks,'unchangedPriorFullCandidateCount':sum(x['baselineHashUnchanged'] for x in candidate_checks)})
write('unselected-saved-sources.json',{'sources':unselected,'notCounted':True})
counts={'targetTiles':49,'fullCoverage':sum(t['fullCoverage'] for t in tiles.values()),'adoptedFullCoverage':sum(t['fullCoverage'] and t['adopted'] for t in tiles.values()),'partialTiles':sum(0<t['coreCount']<16 for t in tiles.values()),'emptyTiles':sum(t['coreCount']==0 for t in tiles.values()),'selectedNativeCores':sum(t['coreCount'] for t in tiles.values()),'formalAccepted':0};counts['unadoptedFullCandidates']=counts['fullCoverage']-counts['adoptedFullCoverage'];counts['missingNativeCores']=784-counts['selectedNativeCores'];counts['missingFullTiles']=49-counts['fullCoverage']
delta=[{'tileId':tid,'baselineCoreCount':oldtiles[tid]['coreCount'],'currentCoreCount':t['coreCount'],'coreCountDelta':t['coreCount']-oldtiles[tid]['coreCount'],'fileChanged':oldtiles[tid]['file']!=t['file'],'adoptedNow':t['adopted']} for tid,t in tiles.items() if oldtiles[tid]['coreCount']!=t['coreCount'] or oldtiles[tid]['file']!=t['file'] or oldtiles[tid].get('productionAdoptedFull')!=t['adopted']]
write('summary.json',{'schemaVersion':3,'zone':'southeast','status':'visual_review_pending','snapshotStartedAtUtc':snap['startedAtUtc'],'snapshotCompletedAtUtc':now(),'counts':counts,'tiles':list(tiles.values()),'delta':delta,'generationPerformed':False,'aiEditPerformed':False,'productionModified':False,'sharedGitTouched':False,'historicalArchiveRescanned':False,'formalAccepted':0,'sourceScope':'Frozen current effective selections and pending full candidates. Working/in-flight and explicitly rejected sources excluded. Later metadata changes reported separately.'})
write('source-checks.json',{'checks':checks,'allStableDuringRead':all(x['stableDuringRead'] for x in checks),'allSourcePixelsReplayedForNewCandidate':True})
print(json.dumps({'counts':counts,'delta':delta,'unchangedCandidates':sum(x['baselineHashUnchanged'] for x in candidate_checks),'oldRemainingEdgesReusable':sum(x['reused'] for x in reuse),'newCrops':len(cuts),'boards':boards},ensure_ascii=False))
