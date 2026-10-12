from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib
from datetime import datetime, timezone
B=Path(__file__).resolve().parent.parent
Q=B/'qa/r08_c11-v01-sol'
def rd(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def wr(f,d):
    assert not Path(f).exists()
    Path(f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit=rd(Q/'source-audit.json')
im=Image.open(audit['file']).convert('RGB')
assert sha(audit['file'])==audit['sha256']
a=np.asarray(im);ids=np.asarray(Image.open(audit['sourceID']))
chains=[]
for s in audit['sources']:
    native=Path(s['file']);recfile=Path(str(native)+'.generation.json');rec=rd(recfile)
    assert sha(native)==s['sha256']==rec['sha256']
    assert rec['route']=='builtin' and rec['tool']=='image_gen.imagegen'
    assert rec['actualModel'] is None and rec['actualQuality'] is None and rec['submittedParameters']=={'model':None,'quality':None}
    assert rec['resizedAfterGeneration'] is False
    checks=[]
    for key in ['prompt','request','receipt','sourceOutputPath']:
        f=Path(rec[key]);expected=rec[key+'Sha256' if key!='sourceOutputPath' else 'sourceOutputSha256']
        assert sha(f)==expected
        checks.append({'kind':key,'file':str(f),'sha256':expected})
    for z in rec['references']:
        assert sha(z['file'])==z['sha256']
        checks.append({'kind':'reference','file':z['file'],'sha256':z['sha256']})
    assert Image.open(native).size==(1254,1254)
    yy,xx=np.where(ids==s['id']);ox,oy=s['originInTile']
    assert np.array_equal(a[yy,xx],np.asarray(Image.open(native).convert('RGB'))[yy-oy,xx-ox])
    chains.append({'sourceID':s['id'],'native':str(native),'nativeSha256':sha(native),'generationRecord':str(recfile),'generationRecordSha256':sha(recfile),'visiblePixels':len(xx),'allRecordedHashesVerified':True,'pixelIdentityVerified':True,'evidence':checks})
    if s['role']=='selected_complete_object_overlay':
        x0,y0,x1,y1=s['destinationBox']
        for label,x,y in [('top-left',x0,y0),('top-right',x1,y0),('bottom-left',x0,y1),('bottom-right',x1,y1)]:
            box=[x-256,y-256,x+256,y+256]
            if min(box)>=0 and box[2]<=4096 and box[3]<=4096:
                o=Q/f'overlay{s["id"]}-corner-{label}.png';assert not o.exists();im.crop(box).save(o)
for direction in ['east','south']:
    full=Image.open(Q/f'external-{direction}.png')
    for k in range(4):
        box=[0,k*1024,512,(k+1)*1024] if direction=='east' else [k*1024,0,(k+1)*1024,512]
        f=Q/f'external-{direction}-part{k+1}.png';assert not f.exists();full.crop(box).save(f)
freeze=B/'migration-freeze-coordinate-audit-20261011.json'
baseline=rd(B/'production-resume-wall-sol-20261012.json')['historicalFreezeEvidence']['sha256']
assert sha(freeze)==baseline
wr(Q/'generation-chain-proof.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'candidate':audit['file'],'candidateSha256':audit['sha256'],'sourceCount':len(chains),'nativeSize':[1254,1254],'coreSize':[1024,1024],'finalSize':[4096,4096],'allVisiblePixelIdentityVerified':True,'allRecordedHashesVerified':True,'chains':chains,'historicalFreezeSha256':baseline,'historicalFreezeUnmodified':True,'actualModel':None,'actualQuality':None,'builtinOnly':True,'paidApiUsed':False,'finalArtResizedOrRGBModified':False,'formalAccepted':False})
print(json.dumps({'chainProof':str(Q/'generation-chain-proof.json'),'sources':len(chains),'allVerified':True}))

