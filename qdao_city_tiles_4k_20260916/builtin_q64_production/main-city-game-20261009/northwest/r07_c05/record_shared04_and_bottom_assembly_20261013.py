from pathlib import Path
from datetime import datetime,timezone
import sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
ref=lambda f:{'file':str(f),'sha256':p.sha(f)}
D4=T/'bridges/shared-east-lower-04';sf4=D4/'native.png';host4=Path('C:/Users/luyua/.codex/generated_images/01a12075-f5cf-7c30-9edc-ceb79ed8cfbd/exec-646e0115-1888-44a1-970a-25ba1d25d005.png');assert p.sha(sf4)==p.sha(host4)
p.write_json(D4/'generation.json',{'id':'shared-east-lower-04','file':str(sf4),'sha256':p.sha(sf4),'sourceHostFile':str(host4),'sourceHostSha256':p.sha(host4),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'request':ref(D4/'request.json'),'toolReceipt':ref(D4/'tool-receipt.json'),'worldBox':[19853,26776,21107,28030],'tileOrigins':{'r07_c05':[3469,2200],'r07_c06':[-627,2200]},'nativePixels':[1254,1254],'sourceResampled':False,'status':'not_adopted_target_junction_still_open','targetRemainsUnpassed':True,'attemptsWithoutImprovement':2,'nextAction':'Defer this local junction and proceed with other independent missing tiles, per AGENTS.'},replace=False)
Image.open(sf4).crop((557,677,717,817)).save(D4/'failed-junction-native.png')
D3=T/'bridges/shared-east-lower-03';base=T/'bridges/shared-east-lower-02/r07_c05-assembly.json';m=p.read(base);pix=np.array(Image.open(m['output']['file']).convert('RGB'));owner=np.array(Image.open(m['sourceIndex']['file']));sources=m['nativeSources'];sf=D3/'native.png';g=p.read(D3/'generation.json');n=np.array(Image.open(sf).convert('RGB'))
pix[2995:3110,4075:4096]=n[795:910,606:627];owner[2995:3110,4075:4096]=len(sources)
sources.append({'id':'shared-east-lower-03-bottom-only','file':str(sf),'sha256':p.sha(sf),'tileOriginXY':[3469,2200],'worldBox':g['worldBox'],'adoptedSourceROI':[606,795,627,910],'adoptedTileROI':[4075,2995,4096,3110],'generationRecord':ref(D3/'generation.json'),'sourceHostFile':g['sourceHostFile'],'sourceHostSha256':g['sourceHostSha256'],'evidence':{'request':g['request'],'receipt':g['toolReceipt'],'prompt':ref(D3/'prompt.txt')},'sourceResampled':False})
proof=[]
for i,s in enumerate(sources):
 assert p.sha(s['file'])==s['sha256'];a=np.array(Image.open(s['file']).convert('RGB'));ys,xs=np.where(owner==i);ox,oy=s['tileOriginXY'];assert np.array_equal(pix[ys,xs],a[ys-oy,xs-ox]);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactSameWorldNativePixels':True})
candidate=D3/'r07_c05-combined-shared-proposal-4096.png';index=D3/'r07_c05-source-index.png';assert not candidate.exists();Image.fromarray(pix).save(candidate);Image.fromarray(owner).save(index)
prior=T/'qa/trial-bottom-floor-cap-02-trimmed/final-current-review.json';report=p.read(prior);im=Image.fromarray(pix);entries=[]
for q in report['internalQA']['entries']:
 crop=im.crop(q['cropLTRB'])
 if q['rotationCCW90']:crop=crop.transpose(Image.Transpose.ROTATE_90)
 same=crop.tobytes()==Image.open(q['file']).convert('RGB').tobytes();item={'name':q['name'],'cropLTRB':q['cropLTRB'],'rotationCCW90':q['rotationCCW90'],'priorCrop':{'file':q['file'],'sha256':q['sha256']},'unchangedPixels':same,'status':'passed_by_exact_pixel_identity' if same else 'pending_changed_crop_review'}
 if not same:
  f=D3/(q['name']+'.png');crop.save(f);item['currentCrop']=ref(f)
 entries.append(item)
assert sum(x['pixelCount'] for x in proof)==16777216
p.write_json(D3/'r07_c05-assembly.json',{'schemaVersion':2,'createdAtUtc':p.now(),'tile':'r07_c05','status':'native_candidate_pending_changed_internal_crop_review','output':ref(candidate),'baseManifest':ref(base),'nativeSources':sources,'fixedGridSourceCount':16,'additionalNativeSourceCount':len(sources)-16,'totalNativeSourceCount':len(sources),'sourceIndex':ref(index),'sourceIndexEncoding':'uint8 zero-based nativeSources; nativeXY=tileXY-tileOriginXY','pixelProof':{'status':'passed','checkedPixels':16777216,'sources':proof},'internalQA':{'priorReview':ref(prior),'entries':entries},'sourceResampled':False,'blending':False,'formalAccepted':False,'eastBoundaryRemainingDefects':[215,395,737,1090],'remainingDefectCoordinatesRelativeToSharedFrame':True},replace=False)
print({'candidate':ref(candidate),'sources':len(sources),'changedQACrops':[e['name'] for e in entries if not e['unchangedPixels']]})
