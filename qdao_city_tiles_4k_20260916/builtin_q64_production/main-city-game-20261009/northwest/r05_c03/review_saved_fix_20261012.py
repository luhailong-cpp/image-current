"""Review the saved final repair and inspect actual neighboring candidate pixels."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent
Z=T.parent
M=T/'candidate/r05_c03-candidate-hard-80982c249bee.assembly.json'
A=p.read(M)
Q=T/'qa/r05_c03-candidate-hard-80982c249bee'
oldpath=T/'qa/r05_c03-candidate-hard-65f341e34b58/review-internal.json'
old=p.read(oldpath); byname={e['name']:e for e in old['entries']}
changed={
'internal-x1024-segment04':'Blue roof tile grooves and gold border are continuous through the join; prior cut gold geometry is resolved.',
'internal-y3072-segment01':'Gold eave and blue roof tubes continue through the horizontal join with no abrupt phase cutoff.',
'junction-x1024-y3072':'Gold scroll decoration and adjacent blue roof grooves connect continuously at the repaired junction.'}
entries=[]
for q in A['qa']:
 name=Path(q['file']).stem; prev=byname[name]
 assert p.sha(q['file'])==q['sha256']
 if q['sha256']==prev['sha256']:
  assert prev['actuallyViewed'] and prev['verdict'].startswith('passed')
  e={**prev,'file':q['file'],'inheritedFrom':{'report':str(oldpath),'reportSHA256':p.sha(oldpath),'cropSHA256':prev['sha256']},'viewedThisRevision':False}
 else:
  assert name in changed
  e={'name':name,'file':q['file'],'sha256':q['sha256'],'verdict':'passed','actuallyViewed':True,'viewedThisRevision':True,'inheritedFrom':None,'findings':changed[name]}
 entries.append(e)
assert len(entries)==33 and sum(e['viewedThisRevision'] for e in entries)==3
p.write_json(Q/'review-internal-20261012.json',{'createdAtUtc':p.now(),'tile':'r05_c03','candidate':A['output'],'assemblyManifest':{'file':str(M),'sha256':p.sha(M)},'status':'passed','verdict':'passed','blockingCount':0,'counts':{'viewed':33,'viewedThisRevision':3,'inheritedIdenticalPassed':30,'blocking':0},'entries':entries,'formalAccepted':False},replace=False)
out=np.array(Image.open(A['output']['file']).convert('RGB'))
assert p.sha(A['output']['file'])==A['output']['sha256']
audit=[]
for s in A['nativeSources']:
 assert p.sha(s['file'])==s['sha256']==p.sha(p.selected_path(T,s['id']))
 rec=p.read(s['generationRecord']['file'])
 assert p.sha(s['generationRecord']['file'])==s['generationRecord']['sha256']
 assert p.sha(rec['evidence']['hostOutputPath'])==s['sha256']
 im=Image.open(s['file']).convert('RGB'); assert im.size==(1254,1254)
 crop=np.array(im.crop(tuple(s['coreCropLTRB'])))
 x,y=s['tileCorePasteXY']; assert np.array_equal(out[y:y+1024,x:x+1024],crop)
 audit.append({'id':s['id'],'file':s['file'],'sha256':s['sha256'],'hostMatchesExactly':True})
p.write_json(Q/'native-pixel-proof-20261012.json',{'createdAtUtc':p.now(),'candidate':A['output'],'sourceCount':16,'verifiedExactNativePixels':16777216,'allOutputPixelsVerified':True,'resampled':False,'blended':False,'recolored':False,'method':'Every exact 1024 square source core equals its exact world placement in the output.','sources':audit},replace=False)
neighbor=Z/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r05_c04-joint-4096.png'
left=Image.open(A['output']['file']).convert('RGB'); right=Image.open(neighbor).convert('RGB')
full=Image.new('RGB',(640,4096)); full.paste(left.crop((3776,0,4096,4096)),(0,0)); full.paste(right.crop((0,0,320,4096)),(320,0))
E=Q/'external-east-20261012'; E.mkdir(exist_ok=True)
crops=[]
for i in range(4):
 f=E/f'east-segment{i+1:02}.png'; full.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90).save(f)
 crops.append({'name':f.stem,'file':str(f),'sha256':p.sha(f),'nativePixelScale':1,'rotationCCW90':True,'actuallyViewed':False})
for i in range(1,4):
 f=E/f'east-junction-y{i*1024}.png'; full.crop((160,i*1024-160,480,i*1024+160)).save(f)
 crops.append({'name':f.stem,'file':str(f),'sha256':p.sha(f),'nativePixelScale':1,'actuallyViewed':False})
p.write_json(E/'index.json',{'candidate':A['output'],'neighbor':{'file':str(neighbor),'sha256':p.sha(neighbor)},'entries':crops,'formalAccepted':False},replace=False)
print(json.dumps({'internalPassed':33,'deltaViewed':3,'unchangedInherited':30,'exactPixels':16777216,'externalQA':str(E),'cropCount':len(crops)}))

