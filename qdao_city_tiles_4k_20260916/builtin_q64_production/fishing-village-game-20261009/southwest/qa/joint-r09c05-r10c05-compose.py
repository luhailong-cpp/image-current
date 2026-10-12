"""Native vertical join / optional four-path local repair for c05 pair."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
Z=Q.parent
WORLD=[16269,32653,20595,41075]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def mod(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rgb(p,size):
    im=Image.open(p); assert im.size==size
    if im.mode=='RGBA': assert im.getextrema()[3]==(255,255)
    return np.array(im.convert('RGB'))
def png(p,a):
    assert not p.exists(),str(p)
    Image.fromarray(a).save(p);assert np.array_equal(np.array(Image.open(p)),a)
    return {**ref(p),'size':[a.shape[1],a.shape[0]]}
def js(p,d):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return ref(p)
def npy(p,a):
    assert not p.exists(),str(p)
    np.save(p,a,allow_pickle=False);assert np.array_equal(np.load(p),a);return ref(p)
def finish(prefix,pix,ids,trace):
    assert pix.shape==(8422,4326,3)
    trace.update({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'script':ref(__file__),'seamHelper':ref(Z/'tools/seam_helpers.py'),'repairFunctions':ref(Q/'repair-compose.py'),'noResize':True,'noFeather':True,'noColourCorrection':True,'noDrawing':True,'formalAcceptance':False})
    trace['context']={**png(Q/(prefix+'-context-native.png'),pix),'globalBox':WORLD}
    trace['sourceIds']=npy(Q/(prefix+'-source-ids.npy'),ids)
    trace['tiles']=[]
    for tile,y,wy in [('r09_c05',0,32768),('r10_c05',4096,36864)]:
        ctx=png(Q/(prefix+'-'+tile+'-context-native.png'),pix[y:y+4326])
        core=png(Q/(prefix+'-'+tile+'-candidate-4096.png'),pix[y+115:y+4211,115:4211])
        trace['tiles'].append({'tile':tile,'context':ctx,'contextBoxInJoint':[0,y,4326,y+4326],'candidate':core,'coreBoxInJoint':[115,y+115,4211,y+4211],'globalCoreBox':[16384,wy,20480,wy+4096]})
    trace['qa']=[]
    for i,x in enumerate([0,800,1600,2400,3196],1):
        box=[115+x,3866,1015+x,4556]
        trace['qa'].append({**png(Q/(prefix+f'-shared-part{i:02d}-100pct.png'),pix[3866:4556,115+x:1015+x]),'contextBox':box,'globalBox':[WORLD[j%2]+v for j,v in enumerate(box)]})
    print(json.dumps({'trace':js(Q/(prefix+'-trace.json'),trace),'tiles':trace['tiles']},ensure_ascii=False),flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['join','repair']);p.add_argument('--manifest');args=p.parse_args()
    h=mod(Z/'tools/seam_helpers.py','c05_ns_helper')
    if args.mode=='join':
        prefix='joint-r09c05-r10c05-v1'
        upstream=Q/'joint-r09c04-c05-finalrail-v1-context-native.png'
        bottom=Q/'full-tile-r10_c05-context-native.png'
        a=rgb(upstream,(8422,4326))[:,4096:8422];b=rgb(bottom,(4326,4326))
        top=png(Q/(prefix+'-top-input-native.png'),a)
        s=h._minimum_vertical_seam(a[-230:].transpose(1,0,2),b[:230].transpose(1,0,2))
        assert len(s)==4326 and np.all(np.abs(np.diff(s))<=1)
        mask=np.arange(230)[:,None]>=s[None,:]
        pix=np.concatenate([a[:4096],np.where(mask[:,:,None],b[:230],a[-230:]),b[230:]],axis=0)
        ids=np.zeros((8422,4326),dtype=np.uint8);ids[4096:4326]=mask;ids[4326:]=1
        assert np.array_equal(pix[:4326][ids[:4326]==0],a[ids[:4326]==0])
        assert np.array_equal(pix[4096:][ids[4096:]==1],b[ids[4096:]==1])
        cropbox=[0,3584,1254,4838]
        sr=png(Q/(prefix+'-post-source-native.png'),pix[3584:4838,:1254])
        trace={'mode':'join','sources':[{'upstream':ref(upstream),'cropBox':[4096,0,8422,4326],'extracted':top,'provenance':ref(Q/'joint-r09c04-c05-finalrail-v1-trace.json')},{**ref(bottom),'provenance':ref(Q/'full-tile-r10_c05-assembly.json')}],'sourceIdLegend':{'0':'right-side 4326 crop from finalrail top joint','1':'r10_c05 full native base'},'seam':{'overlapContextBox':[0,4096,4326,4326],'yByColumnInOverlap':s.tolist(),'lowerChosenAtOrBelow':True},'repairSource':{**sr,'jointContextBox':cropbox,'globalBox':[16269,36237,17523,37491]},'validation':{'sourcePixelIdentity':True}}
        finish(prefix,pix,ids,trace)
    else:
        m=read(args.manifest);prefix=m['outputPrefix'];base=read(m['baseTrace'])
        assert sha(base['context']['path'])==base['context']['sha256']
        pix=rgb(base['context']['path'],(4326,8422));orig=pix.copy();ids=np.load(base['sourceIds']['path'],allow_pickle=False)
        item=m['repair'];cb=item['jointContextBox'];l,t,r,b=cb
        old=rgb(item['source']['path'],(1254,1254));new=rgb(item['repair']['path'],(1254,1254))
        assert sha(item['source']['path'])==item['source']['sha256'] and sha(item['repair']['path'])==item['repair']['sha256']
        assert np.array_equal(old,orig[t:b,l:r])
        gen=read(item['generationRecord']['path']);assert gen['sha256']==item['repair']['sha256']
        rt=mod(Q/'repair-compose.py','c05_ns_repair')
        mask,paths=rt.closed_mask(old,new,item['repairBounds'],item['margin'],cb,h._minimum_vertical_seam)
        sel=mask.astype(bool);after=np.where(sel[:,:,None],new,old);pix[t:b,l:r]=after;ids[t:b,l:r][sel]=2
        assert np.array_equal(pix[ids<2],orig[ids<2]) and np.array_equal(after[sel],new[sel])
        trace={'mode':'repair','baseTrace':ref(m['baseTrace']),'manifest':ref(args.manifest),'repair':item,'sourceIdLegend':{**base['sourceIdLegend'],'2':'native AI localized post repair'},'repairPaths':paths,'repairMask':npy(Q/(prefix+'-post-source-mask.npy'),mask),'repairMaskPng':png(Q/(prefix+'-post-source-mask-bw.png'),mask*255),'postAfter':png(Q/(prefix+'-post-after-100pct.png'),after),'validation':{'sourcePixelIdentity':True,'unselectedBasePixelsUnchanged':True,'selectedPixelCount':int(sel.sum())}}
        finish(prefix,pix,ids,trace)
if __name__=='__main__':main()
