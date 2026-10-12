from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
base=T/'qa/local-caps-trial-01/index.json';m=p.read(base);pix=np.array(Image.open(m['candidate']['file']).convert('RGB'));own=np.array(Image.open(m['sourceIndex']['file']));sources=m['sources']
neighbor=Z/'r07_c06';sf=neighbor/'repair-native/west-seam-r3-fix04.png';sg=sf.with_suffix('.png.generation.json');g=p.read(sg);assert p.sha(sf)=='40a58d45a8f6b0e2be7a2dd293dde08381876ea78dbc9fbcd4d78eb9ce6a5435'
n=np.array(Image.open(sf).convert('RGB'));pix[2204:2364,4009:4096]=n[230:390,540:627];own[2204:2364,4009:4096]=len(sources)
sources.append({'id':'shared-east-r3-fix04','file':str(sf),'sha256':p.sha(sf),'tileOriginXY':[3469,1974],'worldBox':g['worldBox'],'generationRecord':ref(sg),'sharedSource':True,'adoptedSourceROI':[540,230,627,390],'adoptedTileROI':[4009,2204,4096,2364],'proposal':ref(neighbor/'qa/west-seam-r3-fix04-shared-proposal01/proposal-proof.json')})
proof=[];evidence=[]
for i,s in enumerate(sources):
 f=Path(s['file']);assert p.sha(f)==s['sha256'];ys,xs=np.where(own==i);a=np.array(Image.open(f).convert('RGB'));ox,oy=s['tileOriginXY'];assert a.shape==(1254,1254,3);assert np.array_equal(pix[ys,xs],a[ys-oy,xs-ox]);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactNativePixels':True})
 if i<17:
  v=p.validate_native(f,T,f.stem[:6]);s['kind']='fixed_grid' if i<16 else 'supplemental_same_grid_roi';s['generationRecord']=ref(Path(v['generationRecord']));gr=p.read(v['generationRecord'])
  ev={k:ref(Path(v[k])) for k in ['prompt','request','receipt']};host=gr.get('sourceHostFile',gr.get('evidence',{}).get('hostOutputPath'))
  if i<16:assert p.sha(p.selected_path(T,s['id']))==s['sha256']
 else:
  gr=p.read(s['generationRecord']['file']);ev={}
  if 'evidence' in gr:
   for k in ['prompt','request','receipt']:ev[k]=ref(Path(gr['evidence'][k]));assert ev[k]['sha256']==gr['evidence'][k+'Sha256']
  else:
   for k,r in [('request',gr['request']),('receipt',gr['toolReceipt'])]:assert p.sha(r['file'])==r['sha256'];ev[k]=r
  host=gr.get('sourceHostFile',gr.get('hostOutputPath'))
 assert host and p.sha(host)==s['sha256'],(s['id'],host)
 s['evidence']=ev;s['sourceHostFile']=str(host);s['sourceHostSha256']=s['sha256'];s['sourceResampled']=False
 evidence.append({'sourceIndex':i,'sourceHashValidated':True,'hostOutputByteIdentical':True,'evidence':ev})
signature=__import__('hashlib').sha256(pix.tobytes()).hexdigest()[:16];D=T/'candidate'/('r07_c05-candidate-native-rois-'+signature);D.mkdir(exist_ok=True);assert not (D/'assembly.json').exists()
im=Image.fromarray(pix);out=A.save_png(im,D/'candidate.png');owner=A.save_png(Image.fromarray(own),D/'source-index.png');qa=A.write_qa(im,out,T/'qa'/D.name)
manifest={'schemaVersion':2,'createdAtUtc':p.now(),'tile':'r07_c05','status':'candidate_pending_full_visual_review','output':out,'baseManifest':ref(base),'fixedGridSourceCount':16,'additionalNativeSourceCount':len(sources)-16,'totalNativeSourceCount':len(sources),'nativeSources':sources,'sourceIndex':owner,'sourceIndexEncoding':'uint8 zero-based nativeSources index; exact native coordinate = tile coordinate minus tileOriginXY','pixelProof':{'status':'passed','checkedPixels':sum(r['pixelCount'] for r in proof),'allPixelsUnmodifiedNativeSamplesAtExactWorldCoordinates':True,'counts':proof},'sourceAudit':evidence,'sourceResampled':False,'blending':False,'feathering':False,'qa':qa,'formalAccepted':False}
assert manifest['pixelProof']['checkedPixels']==4096*4096;p.write_json(D/'assembly.json',manifest,replace=False)
print(json.dumps({'directory':str(D),'output':out,'sources':len(sources)}))
