"""Independent QA only. Exact coordinate pixel selection; writes only beside this file."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(name):
    p = ROOT / 'native' / (name + '.png')
    return np.array(Image.open(p).convert('RGB')), p

def provenance(p):
    rp=p.with_suffix('.png.generation.json')
    rec=json.loads(rp.read_text(encoding='utf-8-sig'))
    with Image.open(p) as im:
        assert im.size==(1254,1254) and im.format=='PNG'
        assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
    assert sha(p)==rec['sha256']
    assert rec['route'] in ('builtin','builtin_image_gen')
    assert not rec['resizedAfterGeneration'] and not rec['finalArtUpscaled']
    evidence=rec['evidence']
    refs={}
    for label,key in [('generationRecord',None),('prompt','prompt'),('request','request'),('receipt','receipt')]:
        ep=rp if key is None else Path(rec[key] if key=='prompt' else evidence[key])
        refs[label]={'file':str(ep),'sha256':sha(ep)}
    return {'file':str(p),'sha256':sha(p),'nativeDimensions':[1254,1254],'opaque':True,'worldBoxWithHalo':rec['worldBoxWithHalo'],'coreWorldBox':rec['coreWorldBox'],'coreCrop':rec['coreCrop'],'route':rec['route'],'sourceResampled':False,**refs}

def save(image, name):
    p = OUT / (name+'.png')
    Image.fromarray(image).save(p)
    return p

def sheet(names, box, label):
    ims=[]
    for name in names:
        arr,p=load(name)
        ims.append((name,Image.fromarray(arr).crop(box)))
    w,h=ims[0][1].size
    out=Image.new('RGB',(w*len(ims),h+30),(255,255,255))
    draw=ImageDraw.Draw(out)
    for i,(name,im) in enumerate(ims):
        draw.text((i*w+4,8),name,fill=(0,0,0))
        out.paste(im,(i*w,30))
    p=OUT/(label+'.png');out.save(p)
    return {'file':str(p),'crop':list(box),'scale':1,'labelPixelsOutsideArt':True}

def minimum_seam(left,right):
    difference=left.astype(np.float32)-right.astype(np.float32)
    cost=np.mean(difference*difference,axis=2)
    h,w=cost.shape
    center=(w-1)/2
    typical=float(np.median(cost))+1
    cost+=(np.abs(np.arange(w)-center)/max(center,1))**4*typical*.16
    prev=cost[0].copy(); back=np.zeros((h,w),np.int8)
    for y in range(1,h):
        options=np.stack((np.r_[np.inf,prev[:-1]],prev,np.r_[prev[1:],np.inf]))
        choice=np.argmin(options,axis=0)
        back[y]=choice.astype(np.int8)-1
        prev=cost[y]+np.take_along_axis(options,choice[None,:],axis=0)[0]
    seam=np.empty(h,np.int32);seam[-1]=np.argmin(prev)
    for y in range(h-1,0,-1):seam[y-1]=seam[y]+int(back[y,seam[y]])
    return seam

def quilt_patch(base, donor, outer, inner):
    l,t,r,b=outer;il,it,ir,ib=inner
    yy,xx=np.mgrid[t:b,l:r]
    left=minimum_seam(base[t:b,l:il],donor[t:b,l:il])+l
    right=minimum_seam(base[t:b,ir:r],donor[t:b,ir:r])+ir
    top=minimum_seam(base[t:it,l:r].transpose(1,0,2),donor[t:it,l:r].transpose(1,0,2))+t
    bottom=minimum_seam(base[ib:b,l:r].transpose(1,0,2),donor[ib:b,l:r].transpose(1,0,2))+ib
    inside=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
    mask=np.zeros(base.shape[:2],bool);mask[t:b,l:r]=inside
    out=np.where(mask[...,None],donor,base)
    return out,mask,{'outer':list(outer),'forcedInner':list(inner),'leftPath':left.tolist(),'rightPath':right.tolist(),'topPath':top.tolist(),'bottomPath':bottom.tolist()}

def proposal(name,base_name,donor_name,outer,inner):
    base,bp=load(base_name);donor,dp=load(donor_name)
    out,mask,paths=quilt_patch(base,donor,outer,inner)
    op=save(out,name);mp=save(mask.astype(np.uint8)*255,name+'-source-mask')
    assert np.array_equal(out[~mask],base[~mask]) and np.array_equal(out[mask],donor[mask])
    saved=np.array(Image.open(op).convert('RGB'))
    saved_mask=np.array(Image.open(mp))==255
    assert np.array_equal(saved,out) and np.array_equal(saved_mask,mask)
    assert np.array_equal(saved[~saved_mask],base[~saved_mask]) and np.array_equal(saved[saved_mask],donor[saved_mask])
    base_ref=provenance(bp);donor_ref=provenance(dp)
    assert base_ref['worldBoxWithHalo']==donor_ref['worldBoxWithHalo']
    for rect,label in [((100,230,450,1139),'transition'),((115,115,1139,260),'north'),((100,115,260,1139),'west'),((1000,115,1139,1139),'east'),((115,990,1139,1139),'south')]:
        Image.fromarray(out).crop(rect).save(OUT/(name+'-'+label+'.png'))
    boundaries={
        'northCoreRow115ChangedPixels':int(np.any(out[115,115:1139]!=base[115,115:1139],axis=1).sum()),
        'westCoreColumn115ChangedPixels':int(np.any(out[115:1139,115]!=base[115:1139,115],axis=1).sum()),
        'eastCoreColumn1138ChangedPixels':int(np.any(out[115:1139,1138]!=base[115:1139,1138],axis=1).sum()),
        'southCoreRow1138ChangedPixels':int(np.any(out[1138,115:1139]!=base[1138,115:1139],axis=1).sum()),
    }
    return {'name':name,'file':str(op),'sha256':sha(op),'mask':str(mp),'maskSha256':sha(mp),'maskEncoding':'0=base source; 255=donor source','base':base_ref,'donor':donor_ref,'paths':paths,'donorPixelCount':int(mask.sum()),'originalPixelCount':int((~mask).sum()),'exactCoordinatePixelProof':True,'reconstructedEveryPixel':True,'savedPNGReopenedAndReconstructed':True,'baseAndDonorWorldCoordinatesMatch':True,'resized':False,'warped':False,'blended':False,'recolored':False,'geometry':'binary selection of original native RGB pixels at the identical x,y; no pixel arithmetic in output','coreBoundaryComparison':boundaries,'status':'QA_probe_pending_visual_review','formalAccepted':False}

records=[]
records.append(sheet(['s02_02_resume02']+['s02_02_transitionfix%02d'%i for i in range(1,5)],(160,700,320,880),'s02_02-mid-branch-native-crops'))
records.append(sheet(['s02_04_resume02','s02_04_transitionfix01','s02_04_transitionfix02'],(160,450,400,650),'s02_04-mid-branch-native-crops'))
records.append(sheet(['s02_04_resume02','s02_04_transitionfix01','s02_04_transitionfix02'],(160,950,420,1170),'s02_04-low-branch-native-crops'))
(OUT/'crop-records.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
proposals=[]
proposals.append(proposal('s02_02-original-plus-fix02-minseam','s02_02_resume02','s02_02_transitionfix02',(145,230,640,1250),(270,290,490,1090)))
proposals.append(proposal('s02_02-original-plus-fix03-minseam','s02_02_resume02','s02_02_transitionfix03',(145,230,620,1245),(250,300,450,1110)))
proposals.append(proposal('s02_04-original-plus-fix01-minseam','s02_04_resume02','s02_04_transitionfix01',(145,230,630,1245),(300,320,480,1110)))
findings={
    's02_02-original-plus-fix02-minseam':['Disconnected original tips remain near x230 at approximately y357, y671 and y1024. Donor arm also stops near x243,y456. A small grout break appears near x230,y730 where the binary seam crosses the diagonal.'],
    's02_02-original-plus-fix03-minseam':['Middle southwest branch still ends near x194,y842; original upper/lower tips survive where the minimum-error path keeps original pixels.'],
    's02_04-original-plus-fix01-minseam':['Middle tail still ends near x225,y576 and lower tail near x215,y1060. The local minimum-error overlay preserves these native donor orphans.'],
}
for p in proposals:
    p.update(status='rejected_QA_probe',actuallyViewed=True,verdict='needs_repair',findings=findings[p['name']],completePerimeterAcceptance=False)
(OUT/'proposal-records.json').write_text(json.dumps(proposals,indent=2)+'\n',encoding='utf-8')
review={
    'scope':'Independent QA only; no native/selection/progress/prior QA changes',
    'status':'no_defensible_complete_repair_found',
    'formalAccepted':False,
    'nativeSourcesActuallyViewed':['s02_02_resume02','s02_02_transitionfix01','s02_02_transitionfix02','s02_02_transitionfix03','s02_02_transitionfix04','s02_04_resume02','s02_04_transitionfix01','s02_04_transitionfix02'],
    'nativeScaleCropRecords':str(OUT/'crop-records.json'),
    'proposalRecords':str(OUT/'proposal-records.json'),
    'mechanicalProof':'Every tested proposal pixel reconstructed exactly from its base or donor at the identical source coordinate, with PNG hashes, native provenance, and binary mask. No resize, warping, blending, recoloring or generated texture.',
    'findings':[
        's02_02_transitionfix02 supplies a continuous grid but moves the west anchor; simply using it as the source fails the real west join.',
        's02_02_transitionfix03 and transitionfix04 are closer to the desired T-junction layout, but retain a southwest branch from the native junction near (267,770); its endpoint is disconnected inside a slab.',
        'Both s02_04 donors retain a southwest middle tail; transitionfix01 extends it farther left but it still terminates inside a slab. The lower donor tail also remains.',
        'The three explicit minimum-error overlays tested here fail transition QA. They are evidence probes only and are not suitable for source selection.',
        'The selected sources remain unchanged; their two previously recorded blockers are not resolved by this review.',
    ],
    'limits':'This is a visual rejection of the supplied native sources and the saved minimum-error probes, not a proof that every possible binary pixel mask is impossible. No proposal earned complete perimeter acceptance.',
    'recommendedNextNativeEdit':'Use anchor-preserving native edit to close or remove the remaining donor branches while preserving the full x115/y115 core seam anchors; inspect complete native-scale transition and all perimeter joins before any selection.'
}
(OUT/'review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cropCount':len(records),'proposals':[{'name':p['name'],'donorPixelCount':p['donorPixelCount'],'exactCoordinatePixelProof':p['exactCoordinatePixelProof']} for p in proposals]},indent=2))
