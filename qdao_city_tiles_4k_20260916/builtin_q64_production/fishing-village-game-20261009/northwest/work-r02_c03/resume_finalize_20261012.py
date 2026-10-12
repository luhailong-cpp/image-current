from production import *
from datetime import datetime,timezone

D=W/'resume-20261012-v1';F=D/sys.argv[1];O=D/(sys.argv[2] if len(sys.argv)>2 else 'final-v2');O.mkdir(exist_ok=True);Q=O/'qa';Q.mkdir(exist_ok=True)
pm=read(F/'assembly.json');pa=np.asarray(Image.open(F/'full-pair.png'));pi=np.asarray(Image.open(F/'source-id.png'));ps=pm['sources']
wa=np.asarray(Image.open(F/'west-joint.png'));wi=np.asarray(Image.open(F/'west-joint.source-id.png'));wb=read(F/'west-joint.assembly.json')['globalBox']
def proof(a,ids,sources,origin,selected=None):
 checks=[]
 for k in np.unique(ids if selected is None else ids[selected]):
  s=sources[str(k)];assert sha(s['file'])==s['sha256'];src=np.asarray(Image.open(s['file']));mask=ids==k
  if selected is not None:mask&=selected
  yy,xx=np.nonzero(mask);sx=xx+origin[0]-s['globalNativeBox'][0];sy=yy+origin[1]-s['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(a[yy,xx],src[sy,sx]);checks.append({'sourceId':int(k),'pixels':int(len(yy)),'mismatches':0})
 return {'pixels':int(ids.size if selected is None else selected.sum()),'mismatches':0,'contributions':checks}
candidate=pa[115:4211,115:4211];ci=pi[115:4211,115:4211];cp=O/'r02_c03.candidate.png';ip=O/'r02_c03.source-id.png';shutil.copy2(F/'r02_c03.candidate.png',cp);shutil.copy2(F/'r02_c03.source-id.png',ip)
pr=proof(candidate,ci,ps,[8192,4096]);write(O/'source-pixel-proof.json',pr)
cm={'schemaVersion':1,'tile':'r02_c03','globalCoreBox':[8192,4096,12288,8192],'outputSize':[4096,4096],'candidate':{'file':str(cp),'sha256':sha(cp)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':{str(k):ps[str(k)] for k in np.unique(ci)},'sourcePixelProof':pr,'nativeScaleResampled':False,'sourceSelectionOnly':True,'baseCandidate':{'file':str(W/'converge-v1/r02_c03.candidate.png'),'sha256':sha(W/'converge-v1/r02_c03.candidate.png')},'parentAssembly':{'file':str(F/'assembly.json'),'sha256':sha(F/'assembly.json')},'status':'candidate-pending-final-changed-region-review','formalAccepted':False}
write(O/'r02_c03.assembly.json',cm)
for r in range(4):
 for c in range(4):Image.fromarray(candidate[r*1024:(r+1)*1024,c*1024:(c+1)*1024]).save(Q/f'core-{r+1}-{c+1}.png')
for edge,boxes in [('north',[(i*1024,0,(i+1)*1024,256) for i in range(4)]),('south',[(i*1024,3840,(i+1)*1024,4096) for i in range(4)]),('west',[(0,i*1024,256,(i+1)*1024) for i in range(4)]),('east',[(3840,i*1024,4096,(i+1)*1024) for i in range(4)])]:
 for j,b in enumerate(boxes):Image.fromarray(candidate).crop(b).save(Q/f'{edge}-{j+1}.png')
def neighbor(tile,ampath,render,renderIds,renderBox,applyBox):
 bm=read(ampath);bp=Path(bm['candidate']['file']);bip=Path(bm['sourceIdMap']['file']);assert sha(bp)==bm['candidate']['sha256'];assert sha(bip)==bm['sourceIdMap']['sha256']
 base=np.asarray(Image.open(bp));a=base.copy();ids=np.asarray(Image.open(bip)).copy();bs={str(s['sourceId']):s for s in bm['sources']} if isinstance(bm['sources'],list) else bm['sources'].copy();origin=bm['globalCoreBox'][:2]
 l,t,r,bot=applyBox;ry,rx=t-renderBox[1],l-renderBox[0];sy,sx=t-origin[1],l-origin[0];h,w=bot-t,r-l;incoming=render[ry:ry+h,rx:rx+w];incomingIds=renderIds[ry:ry+h,rx:rx+w];changed=np.any(a[sy:sy+h,sx:sx+w]!=incoming,axis=2);a[sy:sy+h,sx:sx+w][changed]=incoming[changed]
 def common(s):
  for key,v in bs.items():
   if v['sha256']==s['sha256'] and v['globalNativeBox']==s['globalNativeBox']:return int(key)
  key=max(int(k) for k in bs)+1;s=s.copy();s['sourceId']=key;bs[str(key)]=s;return key
 for k in np.unique(incomingIds[changed]):ids[sy:sy+h,sx:sx+w][changed&(incomingIds==k)]=common(ps[str(k)])
 diff=np.any(a!=base,axis=2);yy,xx=np.nonzero(diff);bb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];g=[bb[0]+origin[0],bb[1]+origin[1],bb[2]+origin[0],bb[3]+origin[1]];z=a[bb[1]:bb[3],bb[0]:bb[2]];mi=diff[bb[1]:bb[3],bb[0]:bb[2]];zi=ids[bb[1]:bb[3],bb[0]:bb[2]]
 dp=O/(tile+'.delta.png');mp=O/(tile+'.delta.mask.png');sip=O/(tile+'.delta.source-id.png');Image.fromarray(z).save(dp);Image.fromarray(mi.astype(np.uint8)*255).save(mp);Image.fromarray(zi).save(sip)
 dpr=proof(a,ids,bs,origin,diff);outside=int(np.count_nonzero(np.any(a[~diff]!=base[~diff],axis=1)));assert outside==0
 record={'schemaVersion':1,'tile':tile,'baseCandidate':{'file':str(bp),'sha256':sha(bp)},'baseAssembly':{'file':str(ampath),'sha256':sha(ampath)},'baseSourceIdMap':{'file':str(bip),'sha256':sha(bip)},'globalCoreBox':bm['globalCoreBox'],'globalDeltaBox':g,'tileDeltaBox':bb,'payload':{'file':str(dp),'sha256':sha(dp)},'mask':{'file':str(mp),'sha256':sha(mp),'values':[0,255]},'sourceIdMap':{'file':str(sip),'sha256':sha(sip)},'sources':{str(k):bs[str(k)] for k in np.unique(zi[mi])},'proof':dpr,'unchangedOutsideMaskMismatches':outside,'sourceSelectionOnly':True,'nativeScaleResampled':False,'operation':'assert base SHA256; overwrite native RGB only where mask==255, with no blending','status':'independent-delta-pending-final-changed-region-review','formalAccepted':False}
 write(O/(tile+'.delta.json'),record)
 proposedPath=O/(tile+'.proposed.png');Image.fromarray(a).save(proposedPath);nid=O/(tile+'.proposed.source-id.png');Image.fromarray(ids).save(nid);npr=proof(a,ids,bs,origin)
 write(O/(tile+'.proposed.assembly.json'),{'schemaVersion':1,'tile':tile,'globalCoreBox':bm['globalCoreBox'],'candidate':{'file':str(proposedPath),'sha256':sha(proposedPath)},'sourceIdMap':{'file':str(nid),'sha256':sha(nid)},'sources':bs,'proof':npr,'baseCandidate':record['baseCandidate'],'independentDelta':{'file':str(O/(tile+'.delta.json')),'sha256':sha(O/(tile+'.delta.json'))},'nativeScaleResampled':False,'formalAccepted':False})
 return a,record
a02,d02=neighbor('r03_c02',B/'work-r03_c02/west-final/r03_c02.west-final.assembly.json',wa,wi,wb,[7565,8192,8192,9331])
a03,d03=neighbor('r03_c03',B/'delivery-2x2/stage-v4/r03_c03.assembly.json',pa,pi,pm['globalBox'],[8192,8192,12288,9331])
for j in range(4):
 joint=Image.new('RGB',(1024,600));joint.paste(Image.fromarray(candidate).crop((j*1024,3796,(j+1)*1024,4096)),(0,0));joint.paste(Image.fromarray(a03).crop((j*1024,0,(j+1)*1024,300)),(0,300));joint.save(Q/f'south-with-delta-{j+1}.png')
joint=Image.new('RGB',(600,1024));joint.paste(Image.fromarray(a02).crop((3796,0,4096,1024)),(0,0));joint.paste(Image.fromarray(a03).crop((0,0,300,1024)),(300,0));joint.save(Q/'r03-west-east-with-deltas.png')
for tile,a,d in [('r03_c02',a02,d02),('r03_c03',a03,d03)]:
 b=d['tileDeltaBox'];x=max(0,b[0]-150);y=max(0,b[1]-150);r=min(4096,b[2]+150);bot=min(4096,b[3]+150)
 for tag,z in [('west',[x,y,min(r,x+600),bot]),('east',[max(x,r-600),y,r,bot]),('south',[x,max(y,bot-450),r,bot])]:Image.fromarray(a).crop(z).save(Q/(tile+'.delta-'+tag+'.png'))
before=np.asarray(Image.open(W/'converge-v1/r02_c03.candidate.png'));changedCores=[]
for r in range(4):
 for c in range(4):
  if not np.array_equal(candidate[r*1024:(r+1)*1024,c*1024:(c+1)*1024],before[r*1024:(r+1)*1024,c*1024:(c+1)*1024]):changedCores.append([r+1,c+1])
write(O/'handoff-prepared.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':cm['candidate'],'assembly':{'file':str(O/'r02_c03.assembly.json'),'sha256':sha(O/'r02_c03.assembly.json')},'sourceProof':{'file':str(O/'source-pixel-proof.json'),'sha256':sha(O/'source-pixel-proof.json')},'changedCores':changedCores,'deltas':[d02,d03],'status':'awaiting-changed-region-visual-review','formalAccepted':False})
print(json.dumps({'candidate':str(cp),'candidateSha256':sha(cp),'changedCores':changedCores,'deltas':[{k:d[k] for k in ['tile','globalDeltaBox','baseCandidate','proof']} for d in [d02,d03]]},ensure_ascii=False))
