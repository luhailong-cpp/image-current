from pathlib import Path
from PIL import Image
import numpy as np, json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[2]
Q=Path(__file__).resolve().parent
def rd(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sh(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def wr(f,d):
    assert not f.exists()
    f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names={'C':'r09_c12.candidate-v09','N':'r08_c12.candidate-v15','W':'r09_c11.candidate-v05','E':'r09_c13.candidate-v02','S':'r10_c12.candidate-v02','NW':'r08_c11.candidate-v01','SW':'r10_c11.candidate-v04','SE':'r10_c13.candidate-v02'}
imgs={};proof=[]
for label,name in names.items():
    f=B/'tiles'/(name+'.png');im=Image.open(f).convert('RGB');assert im.size==(4096,4096)
    r=Path(str(f)+'.generation.json')
    if not r.exists():r=B/'qa/r08_c11-v01-sol/source-audit.json'
    d=rd(r);assert sh(f)==d['sha256']
    recsources=[]
    if 'sourceID' in d:
        sid=Path(d['sourceID']);assert sh(sid)==d['sourceIDSha256']
        ids=np.asarray(Image.open(sid));out=np.zeros((4096,4096,3),np.uint8)
        for s in d['sources']:
            src=Path(s['file']);assert sh(src)==s['sha256'];a=np.asarray(Image.open(src).convert('RGB'));yy,xx=np.where(ids==s['id']);ox,oy=s['originInTile'];out[yy,xx]=a[yy-oy,xx-ox]
            recsources.append({'file':str(src),'sha256':sh(src),'sourceID':s['id'],'originInTile':s['originInTile'],'visiblePixels':len(xx)})
        assert np.all(ids>0)
    else:
        seq=d.get('contributions',d.get('derivedFrom',d.get('entries')))
        assert seq is not None
        seq=seq+d.get('repairOverlays',[])+d.get('overlays',[])
        replay=Image.new('RGB',(4096,4096));ids=np.zeros((4096,4096),np.uint16)
        for k,s in enumerate(seq,1):
            src=Path(s['file']);assert sh(src)==s['sha256'];crop=s['sourceCrop'];dst=s.get('destination',s.get('destinationBox',[])[:2]);part=Image.open(src).convert('RGB').crop(crop);replay.paste(part,dst)
            ids[dst[1]:dst[1]+part.height,dst[0]:dst[0]+part.width]=k
            recsources.append({'file':str(src),'sha256':sh(src),'sourceCrop':crop,'destination':dst})
        out=np.asarray(replay);assert np.all(ids>0)
    mismatch=int(np.count_nonzero(np.any(out!=np.asarray(im),axis=2)));assert mismatch==0,(label,mismatch)
    imgs[label]=im
    proof.append({'label':label,'file':str(f),'sha256':sh(f),'pixels':[4096,4096],'record':str(r),'recordSha256':sh(r),'sourceIdentityReplayedPixels':16777216,'mismatchedPixels':mismatch,'sources':recsources})
entries=[]
def save(name,size,parts,**extra):
    out=Image.new('RGBA' if extra.get('missingDiagonal') else 'RGB',size)
    for label,box,dst in parts:out.paste(imgs[label].crop(box),dst)
    f=Q/(name+'.png');assert not f.exists();out.save(f)
    for label,box,dst in parts:
        assert np.array_equal(np.asarray(out.convert('RGB').crop([dst[0],dst[1],dst[0]+box[2]-box[0],dst[1]+box[3]-box[1]])),np.asarray(imgs[label].crop(box)))
    entries.append({'name':name,'file':str(f),'sha256':sh(f),'pixels':list(size),'nativeScale':True,'noBlendOrResize':True,'parts':[{'label':label,'sourceBox':box,'destination':dst,'sourceFile':str(B/'tiles'/(names[label]+'.png')),'sourceSha256':sh(B/'tiles'/(names[label]+'.png'))} for label,box,dst in parts],**extra})
for k in range(4):
    a=k*1024;b=(k+1)*1024
    save(f'north-{k+1}',(1024,512),[('N',[a,3840,b,4096],[0,0]),('C',[a,0,b,256],[0,256])],seam='y256')
    save(f'south-{k+1}',(1024,512),[('C',[a,3840,b,4096],[0,0]),('S',[a,0,b,256],[0,256])],seam='y256')
    save(f'west-{k+1}',(512,1024),[('W',[3840,a,4096,b],[0,0]),('C',[0,a,256,b],[256,0])],seam='x256')
    save(f'east-{k+1}',(512,1024),[('C',[3840,a,4096,b],[0,0]),('E',[0,a,256,b],[256,0])],seam='x256')
save('corner-NW',(512,512),[('NW',[3840,3840,4096,4096],[0,0]),('N',[0,3840,256,4096],[256,0]),('W',[3840,0,4096,256],[0,256]),('C',[0,0,256,256],[256,256])])
save('corner-NE',(512,512),[('N',[3840,3840,4096,4096],[0,0]),('C',[3840,0,4096,256],[0,256]),('E',[0,0,256,256],[256,256])],missingDiagonal='r08_c13 full candidate not available; top-right transparent quadrant is unknown, not artwork')
save('corner-SW',(512,512),[('W',[3840,3840,4096,4096],[0,0]),('C',[0,3840,256,4096],[256,0]),('SW',[3840,0,4096,256],[0,256]),('S',[0,0,256,256],[256,256])])
save('corner-SE',(512,512),[('C',[3840,3840,4096,4096],[0,0]),('E',[0,3840,256,4096],[256,0]),('S',[3840,0,4096,256],[0,256]),('SE',[0,0,256,256],[256,256])])
wr(Q/'source-identity-and-evidence.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'target':names['C'],'localOnly':True,'allEightCandidatesReplayedExact':True,'mismatchedPixelCount':0,'imageGenerationCalls':0,'sourceCandidates':proof,'entries':entries,'NEFourTileCornerIncomplete':True})
print(json.dumps({'evidenceCount':len(entries),'candidateReplayCount':len(proof),'mismatchedPixels':0,'qa':str(Q)}))

