from workflow import *
import numpy as np
q=ROOT/'qa/r14_c12-sol-20261013-v01';im=Image.open(ROOT/'tiles/r14_c12.candidate-sol-20261013-v01.png').convert('RGB');p=read(ROOT/'qa/r14_c12-partial-local-20261013/partial-proof-and-review-queue.json');s=read(q/'seams.json');prior={e['id']:e for e in p['knownInternalSeams']};new=[]
for e in s['entries']:
 assert np.array_equal(np.array(im.crop(e['sourceCrop'])),np.array(Image.open(e['file']).convert('RGB')))
 if e['id'] in prior:
  assert sha(Path(e['file']))==prior[e['id']]['sha256'];e['status']='passed_unchanged_root_partial_actual_review'
 else:new.append(e)
newj=[];oldj={e['id']:e for e in p['knownJunctions']}
for r in range(1,4):
 for c in range(1,4):
  f=q/f'junction_{r}{c}.png'
  if f'j{r}{c}' in oldj:assert sha(f)==oldj[f'j{r}{c}']['sha256']
  else:newj.append({'file':str(f),'id':f'j{r}{c}'})
for prefix,items in [('new-h',[e for e in new if e['id'][0]=='h']),('new-v',[e for e in new if e['id'][0]=='v']),('new-j',newj)]:
 w,h=Image.open(items[0]['file']).size;contact=Image.new('RGB',(w*2,h*((len(items)+1)//2)))
 for i,e in enumerate(items):contact.paste(Image.open(e['file']).convert('RGB'),((i%2)*w,(i//2)*h))
 contact.save(q/f'contact-{prefix}.png')
write(q/'seams.json',s);write(q/'review-inheritance.json',{'priorReview':str(ROOT/'qa/r14_c12-partial-local-20261013/partial-proof-and-review-queue.json'),'unchangedPreviouslyReviewedSeams':18,'unchangedPreviouslyReviewedJunctions':5,'newSeams':[e['id'] for e in new],'newJunctions':[e['id'] for e in newj],'sourceProof':str(q/'source-proof.json'),'formalAccepted':False})
q=ROOT/'qa/r12_c13-floor-ownership-20261013';a=read(q/'candidate-v03-actual-qa.json');im=Image.open(a['candidate']).convert('RGB')
for name in ['internalSeams','junctions','ownershipBoundaryQA']:
 for e in a[name]:assert np.array_equal(np.array(im.crop(e['box'])),np.array(Image.open(e['file']).convert('RGB')))
for prefix,items in [('vertical',[e for e in a['internalSeams'] if e['id'][0]=='v']),('horizontal',[e for e in a['internalSeams'] if e['id'][0]=='h'])]:
 for start in range(0,len(items),4):
  chunk=items[start:start+4];w,h=Image.open(chunk[0]['file']).size;contact=Image.new('RGB',(w*2,h*2))
  for i,e in enumerate(chunk):contact.paste(Image.open(e['file']).convert('RGB'),((i%2)*w,(i//2)*h))
  contact.save(q/f'contact-v03-{prefix}-{start//4+1}.png')
contact=Image.new('RGB',(1536,1536))
for i,e in enumerate(a['junctions']):contact.paste(Image.open(e['file']).convert('RGB'),((i%3)*512,(i//3)*512))
contact.save(q/'contact-v03-junctions.png')
im.crop((2816,3400,3328,4096)).save(q/'actual-lowest-sail-batten.png')
print('Actual QA pixel identities verified; 14c12 new6 seams/new4 junctions, right24/9 contacts prepared')
