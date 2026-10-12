from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image

B=Path(__file__).resolve().parent.parent
D=B/'r10_c08/pipeline/qa/right-lane-review-20261013-v01'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(name,im,provenance):
    f=D/(name+'.png');assert not f.exists();f.parent.mkdir(parents=True,exist_ok=True);im.save(f,format='PNG')
    return {'file':str(f),'sha256':sha(f),'pixels':list(im.size),'sourceResampling':False,**provenance}
def main():
    assert not D.exists();c=read(B/'current-candidates.json')['tiles'];snap={}
    for tile in ['r09_c06','r10_c06','r09_c07','r09_c08','r10_c07']:
        q=c[tile];core=q['candidate'];ctx=q['context']
        assert sha(core['file'])==core['sha256'] and sha(ctx['file'])==ctx['sha256']
        snap[tile]={'core':core,'context':ctx,'assembly':q.get('assembly'),'priorReview':q.get('review')}
    assemblies=list((B/'r10_c08/pipeline/output').glob('*/assembly.json'))
    assert len(assemblies)==1
    p=assemblies[0];q=read(p)
    assert q['verifiedNativeCount']==2 and q['output']['width']==2048 and q['output']['height']==1024
    snap['r10_c08']={'core':q['output'],'context':q['contextOutput'],'assembly':str(p),'partial':True}
    for q in snap.values():
        for key in ['core','context']:
            assert sha(q[key]['file'])==q[key]['sha256']
    images={t:Image.open(q['core']['file']).convert('RGB') for t,q in snap.items()}
    panels=[];edges=[]
    pairs=[('r09_c06','r09_c07','x',4096),('r09_c07','r09_c08','x',4096),('r10_c06','r10_c07','x',4096),('r09_c07','r10_c07','y',4096),('r09_c08','r10_c08','y',2048),('r10_c07','r10_c08','x',1024)]
    for a,b,axis,length in pairs:
        edge=f'{a}--{b}';names=[]
        for start in range(0,length,1024):
            end=min(start+1024,length);im1,im2=images[a],images[b]
            if axis=='x':
                box1=[im1.width-192,start,im1.width,end];box2=[0,start,192,end]
                out=Image.new('RGB',(384,end-start));out.paste(im1.crop(box1),(0,0));out.paste(im2.crop(box2),(192,0))
            else:
                box1=[start,im1.height-192,end,im1.height];box2=[start,0,end,192]
                out=Image.new('RGB',(end-start,384));out.paste(im1.crop(box1),(0,0));out.paste(im2.crop(box2),(0,192))
            name=f'external-{edge}-{start:04d}-{end:04d}'
            r=save(name,out,{'kind':'external-core-shared-edge','axis':axis,'edge':edge,'range':[start,end],'sourceA':{'file':snap[a]['core']['file'],'sha256':snap[a]['core']['sha256'],'box':box1},'sourceB':{'file':snap[b]['core']['file'],'sha256':snap[b]['core']['sha256'],'box':box2},'joinPosition':192,'operation':'exact native adjacent core crops pasted without blending'})
            panels.append(r);names.append(name)
        # Quantify 230px common context only; never treat numeric equality as visual acceptance.
        ca=Image.open(snap[a]['context']['file']).convert('RGB');cb=Image.open(snap[b]['context']['file']).convert('RGB')
        if axis=='x': boxa=[4096,115,4326,length+115];boxb=[0,115,230,length+115]
        else: boxa=[115,4096,length+115,4326];boxb=[115,0,length+115,230]
        aa=np.asarray(ca.crop(boxa)).astype(np.int16);bb=np.asarray(cb.crop(boxb)).astype(np.int16);delta=np.abs(aa-bb)
        edges.append({'edge':edge,'axis':axis,'availableNativeLength':length,'panels':names,'overlapMeanAbsDifference':float(delta.mean()),'overlapMaxAbsDifference':int(delta.max()),'overlapDifferentPixelFraction':float(np.any(delta,axis=2).mean()),'overlapSourceBoxes':[boxa,boxb],'numericMetricsDoNotProveAcceptance':True})
    selected={
        'r09_c07':[('x',1024,0),('x',2048,0),('x',3072,0),('y',1024,2048),('y',2048,2048),('y',3072,2048)],
        'r09_c08':[('x',1024,0),('x',2048,0),('x',3072,0),('y',1024,0),('y',2048,0),('y',3072,0)],
        'r10_c07':[('x',1024,2048),('x',2048,2048),('x',3072,2048),('y',1024,0),('y',2048,2048),('y',3072,2048)],
        'r10_c08':[('x',1024,0)]}
    for tile,regions in selected.items():
        im=images[tile]
        for axis,seam,start in regions:
            box=[seam-192,start,seam+192,start+1024] if axis=='x' else [start,seam-192,start+1024,seam+192]
            name=f'internal-{tile}-{axis}{seam}-{start:04d}'
            panels.append(save(name,im.crop(box),{'kind':'selected-internal-seam','tile':tile,'axis':axis,'seamPositionInCore':seam,'segmentStart':start,'boxInCore':box,'source':snap[tile]['core'],'operation':'exact native crop without resampling'}))
    write(D/'sources-and-panels.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':snap,'edges':edges,'panels':panels,'formalAccepted':False,'internalPassed':False,'newGenerationPerformed':False,'sourceResampling':False,'modelRequirement':{'file':'D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md','sha256':sha('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')}})
    print(json.dumps({'directory':str(D),'panelCount':len(panels),'externalEdges':len(edges),'partialAssembly':str(p)}))
if __name__=='__main__':main()
