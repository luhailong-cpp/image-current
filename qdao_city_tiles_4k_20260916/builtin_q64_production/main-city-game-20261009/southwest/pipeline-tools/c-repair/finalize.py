from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,sys
D=Path(__file__).resolve().parent
req=json.loads((D/'c-horizontal-joint.request.json').read_text(encoding='utf-8'))
src=Path(sys.argv[1]);native=D/'c-horizontal-joint.native.png'
with Image.open(src) as im:
 assert im.size==(1254,1254) and im.format=='PNG'
shutil.copy2(src,native)
old=np.array(Image.open(D/'c-horizontal-joint.target.png').convert('RGB'))
new=np.array(Image.open(native).convert('RGB'))
roi=(560,500,635,553);x0,y0,x1,y1=roi
a=old[y0:y1,x0:x1].astype(np.float32);b=new[y0:y1,x0:x1].astype(np.float32)
yy,xx=np.indices(a.shape[:2]);weight=np.minimum.reduce([xx,yy,x1-x0-1-xx,y1-y0-1-yy]).clip(0,2).astype(np.float32)/2
patch=np.rint(a*(1-weight[:,:,None])+b*weight[:,:,None]).astype(np.uint8)
result=old.copy();result[y0:y1,x0:x1]=patch
Image.fromarray(patch).save(D/'c-horizontal-joint.overlay.patch.png')
Image.fromarray(result).save(D/'c-horizontal-joint.repaired-target.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
box=[1650+x0,1750+y0,1650+x1,1750+y1]
record={'tool':'image_gen.imagegen','file':str(native),'sha256':sha(native),'width':1254,'height':1254,'nativePixelsPreserved':True,'resizedAfterGeneration':False,'actualModel':None,'actualQuality':None,'request':str(D/'c-horizontal-joint.request.json'),'references':req['references'],'evidence':{'toolReceipt':str(D/'c-horizontal-joint.receipt.json'),'toolReceiptSha256':sha(D/'c-horizontal-joint.receipt.json')}}
(D/'c-horizontal-joint.native.png.generation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
proposal={'source':req['source'],'sourceSha256':req['sourceSha256'],'outputNative':record,'patch':{'file':str(D/'c-horizontal-joint.overlay.patch.png'),'sha256':sha(D/'c-horizontal-joint.overlay.patch.png'),'contextBox':box},'operation':'Paste premixed native crop at exact context coordinates, no resizing or extra blending','maximumFeatherRadiusPixels':2,'outsideRoiUnchanged':True,'visualQa':'pending','formalAccepted':False}
(D/'overlay-proposal.json').write_text(json.dumps(proposal,indent=2),encoding='utf-8')
print(json.dumps({'patch':proposal['patch'],'qaPreview':str(D/'c-horizontal-joint.repaired-target.png')}))

