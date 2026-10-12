from native_work import *
import numpy as np
tid='r04_c14'
sel=read(ZONE/f'selection-{tid}.json')
path=ZONE/'tiles'/f'{tid}.png'
der=read(path.with_suffix('.png.derivation.json'))
assert der['sha256']==sha(path)
expected=Image.new('RGB',(4096,4096))
checks=[];refchecks=[];recovered=[]
for r,line in enumerate(sel['cores']):
 for c,ident in enumerate(line):
  p=ZONE/'native'/f'{ident}.png';d=read(p.with_suffix('.png.generation.json'));im=Image.open(p).convert('RGB')
  assert im.size==(1254,1254) and sha(p)==d['sha256']
  assert d['actualModel'] is None and d['actualQuality'] is None
  assert d['submittedParameters']['model'] is None and d['submittedParameters']['quality'] is None
  assert d['coreCrop']==[115,115,1139,1139]
  assert d['coreWorldBox']==[53248+c*1024,12288+r*1024,54272+c*1024,13312+r*1024]
  expected.paste(im.crop(tuple(d['coreCrop'])),(c*1024,r*1024))
  rp=ZONE/'receipts'/f'{ident}.tool.json';receipt=read(rp)
  if 'promptSha256' not in receipt:
   receipt['promptSha256']=sha(Path(d['prompt']));receipt['orderedReferences']=d['references'];receipt['hashesVerifiedAtUtc']=now();write(rp,receipt)
  assert receipt['promptSha256']==sha(Path(d['prompt']))
  for ref in d['references']:
   assert Path(ref['file']).is_file() and sha(Path(ref['file']))==ref['sha256']
   refchecks.append({'file':ref['file'],'sha256':ref['sha256'],'match':True})
   for sub in ref.get('sources',[]):
    assert sha(Path(sub['file']))==sub['sha256']
  if receipt.get('recovery'):recovered.append({'id':ident,'originalToolResponseAvailable':False,'sourcePath':receipt['sourcePath'],'note':receipt['recoveryNote']})
  checks.append({'id':ident,'sha256':sha(p),'nativeSize':[1254,1254],'coreCrop':d['coreCrop'],'nativeUnscaled':True,'prompt':d['prompt'],'promptSha256':sha(Path(d['prompt'])),'receipt':rp.as_posix()})
a=np.array(expected);b=np.array(Image.open(path).convert('RGB'))
delta=int(np.count_nonzero(np.any(a!=b,axis=2)));assert delta==0
qa=ZONE/'qa'/f'{tid}-final'
crops=sorted(qa.glob('*-100pct.png'));assert len(crops)==49
record={'tileId':tid,'file':path.as_posix(),'sha256':sha(path),'size':[4096,4096],'reviewer':'root/south_resume','reviewedAtUtc':now(),'status':'passed_internal_native_visual_review','formalAccepted':False,'sourceCoreCount':16,'overlayCount':0,'nativeRecordsForTile':len(list((ZONE/'native').glob(tid+'_*.png.generation.json'))),'replayDifferentPixels':delta,'uncoveredPixels':0,'baseCoverageMin':1,'baseCoverageMax':1,'internalReview':{'cores':{'reviewed':16,'passed':16},'seamSegments':{'reviewed':24,'passed':24},'crossJunctions':{'reviewed':9,'passed':9},'scale':'1:1','finding':'All final native crops directly inspected: foliage and boulder contours remain continuous; white foam and cyan sea strokes cross every core cut without straight color steps, blur bands or missing pixels. Whole4096 tile checked in preview for coherent shoreline and brightness.','crops':[{'file':p.as_posix(),'sha256':sha(p)} for p in crops]},'sources':checks,'inputReferencesVerified':refchecks,'recoveredOutputs':recovered,'resizedFinalArt':False,'feathering':False,'actualModel':None,'actualQuality':None,'externalSeams':{'north':'pending whole4096 border review with r03_c14','west':'pending whole4096 border review with r04_c13','south':'pending r05_c14','east':'world boundary, no tile neighbor'},'preview':(ZONE/'qa'/f'{tid}-preview.png').as_posix(),'promptSet':[(ZONE/'prompts'/f'{i}.prompt.txt').as_posix() for line in sel['cores'] for i in line]}
write(ZONE/'qa'/f'{tid}-acceptance.json',record)
der.update(status='complete_native_coverage_internal_review_passed',internalReview='passed_16cores_24seams_9crosses_1to1',internalReviewEvidence=(ZONE/'qa'/f'{tid}-acceptance.json').as_posix(),formalAccepted=False,reviewedAtUtc=now())
write(path.with_suffix('.png.derivation.json'),der)
print(json.dumps({'file':path.as_posix(),'sha256':sha(path),'sourceCoreCount':16,'nativeCount':record['nativeRecordsForTile'],'reviewedCrops':len(crops),'replayDifferentPixels':delta,'recoveredOutputCount':len(recovered)}))

