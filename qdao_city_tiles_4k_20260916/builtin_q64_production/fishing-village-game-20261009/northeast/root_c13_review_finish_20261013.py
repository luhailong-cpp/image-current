import json,re
from pathlib import Path
from PIL import Image
import root_workflow as w
import r06_c14_extension as b
Z=w.Z;Q=Z/'qa'/'r05_c13-sol-v3';C=Z/'tiles'/'r05_c13.candidate-sol-v3.png';PIN='1a7ddce4f85656179a54b3a7b9d542560fd6efa22e7fb6286ae5feedd9cf9aa0';assert b.sha(C)==PIN
a=Image.open(C).convert('RGB');assert a.size==(4096,4096)
j=Q/'root-independent-review-journal-20261012.json';d=json.loads(j.read_text());assert len(d['viewed'])==49
sel=Z/'records'/'r05_c13.selection-sol-v3.json';s=json.loads(sel.read_text(encoding='utf-8-sig'))['patches'];assert len(s)==16
for k,item in s.items():
 f=Path(item if isinstance(item,str) else item['path']);f=f if f.is_absolute() else Z/f
 if isinstance(item,dict):assert b.sha(f)==item['sha256']
 im=Image.open(f).convert('RGB');assert im.size==(1254,1254);r,c=int(k[-2]),int(k[-1]);assert im.crop((115,115,1139,1139)).tobytes()==a.crop(((c-1)*1024,(r-1)*1024,c*1024,r*1024)).tobytes()
for name,item in d['viewed'].items():
 f=Path(item['path']);assert b.sha(f)==item['sha256'];im=Image.open(f).convert('RGB')
 if name.startswith('core_'):
  r,c=int(name[-2]),int(name[-1]);box=((c-1)*1024,(r-1)*1024,c*1024,r*1024)
 elif name.startswith('v_'):
  nums=re.findall(r'p(\d)(\d)',name);r,c=map(int,nums[0]);x=c*1024;y=(r-1)*1024;box=(x-im.width//2,y,x+im.width//2,y+im.height)
 elif name.startswith('h_'):
  nums=re.findall(r'p(\d)(\d)',name);r,c=map(int,nums[0]);x=(c-1)*1024;y=r*1024;box=(x,y-im.height//2,x+im.width,y+im.height//2)
 else:
  r,c=map(int,re.findall(r'\d',name));x=c*1024;y=r*1024;box=(x-im.width//2,y-im.height//2,x+im.width//2,y+im.height//2)
 assert a.crop(box).tobytes()==im.tobytes(),name
 item['exactPixelsVerifiedToCurrentCandidate']=True;item['candidateCrop']=box
d.update(internalNativeQAPassed=True,exact16CoreAssemblyVerified=True,all49CropPixelsVerified=True,formalAccepted=False,completedAtUtc=b.now());w.atomic(j,d)
f=Q/'internal-review-summary.json';assert not f.exists();w.atomic(f,{'reviewer':'root','candidate':b.ref(C,'stable sol-v3 candidate'),'selection':b.ref(sel,'pinned16 selection'),'internalNativeQAPassed':True,'all49NativeCropsDirectlyViewed':True,'all49CurrentPixelsVerified':True,'counts':{'cores':16,'boundaryStrips':24,'junctions':9},'journal':b.ref(j,'independent review proof'),'formalAccepted':False,'remaining':'north r04_c13 incomplete; final available external junction closure pending'})
p=Z/'records'/'active-candidates.json';index=json.loads(p.read_text());index['tiles']['r05_c13']=dict(b.ref(C,'stable independently reviewed candidate'),selection=str(sel),reviewStatus='root_internal49_exact_native_QA_passed_external_closure_pending');index['updatedAtUtc']=b.now();index['reviewPaths'].append(str(f.relative_to(Z)).replace('\\','/'));w.atomic(p,index)
print(json.dumps({'r05_c13InternalIndependentPassed':True,'candidateSha256':PIN,'exactNativeCores':16,'verifiedNativeQa':49}))
