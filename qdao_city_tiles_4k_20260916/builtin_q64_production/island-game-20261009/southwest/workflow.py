"""Workflow bookkeeping and same-coordinate neighbor crop constraints; no drawing."""
import production as p
import re
from PIL import Image
from pathlib import Path

def select(stem,evidence,observations,known=None):
    src=p.ROOT/'native'/f'{stem}.png'
    rec=p.load(str(src)+'.generation.json')
    for name in evidence:
        assert (p.ROOT/'qa'/name).exists(), name
    qa=p.ROOT/'qa'/f'{stem}.visual-qa.json'
    p.dump(qa,{'source':p.metadata(src,'selected native candidate'),'checkedAtUtc':p.now(),'evidence':evidence,'observations':observations,'knownLimitations':known or ['Final whole-tile and adjacent final-tile review pending'],'status':'candidate_for_extension','formalAccepted':False})
    rec['status']='candidate_for_extension';rec['visualQA']=qa.as_posix();p.dump(str(src)+'.generation.json',rec)
    index=p.load(p.ROOT/'current-native-map.json'); co=rec['coordinates']; tile=co['tile']
    rows=index.setdefault(tile,[])
    while len(rows)<4: rows.append([None]*4)
    rows[co['subrow']-1][co['subcolumn']-1]=stem
    p.dump(p.ROOT/'current-native-map.json',index)
    total=sum(sum(x is not None for row in v for x in row) for k,v in index.items() if k.startswith('r') and isinstance(v,list))
    generated=len({tuple(x.name.split('_')[:4]) for x in (p.ROOT/'native').glob('*.png.generation.json') if re.fullmatch(r'r\d{2}_c\d{2}_s\d{2}_\d{2}_v\d{2}\.png\.generation\.json',x.name)})
    p.update(selectedCandidateCoreCount=total,corePositionsCovered=total,corePositionsGenerated=generated)

def reject(stem,reason):
    src=p.ROOT/'native'/f'{stem}.png'; rec=p.load(str(src)+'.generation.json')
    rec['status']='rejected_pending_replacement';rec['rejectionReason']=reason;p.dump(str(src)+'.generation.json',rec)
    idx=p.load(p.ROOT/'current-native-map.json');co=rec['coordinates'];rows=idx.get(co['tile'],[])
    if len(rows)>=co['subrow'] and rows[co['subrow']-1][co['subcolumn']-1]==stem:
        rows[co['subrow']-1][co['subcolumn']-1]=None
    p.dump(p.ROOT/'current-native-map.json',idx)
    p.dump(p.ROOT/'qa'/f'{stem}.rejection.json',{'source':p.metadata(src,'rejected old interpretation'),'reason':reason,'checkedAtUtc':p.now(),'formalAccepted':False,'replacementPending':True})

def anchor_left_to_final(stem,finaltile):
    guide=p.ROOT/'guides'/f'{stem}.native-overlap-guide.png'
    deriv=p.load(str(guide)+'.derivation.json'); co=deriv['coordinates']; box=co['nativeGlobalBox']
    r,c=map(int,(finaltile[1:3],finaltile[5:7]))
    fb=[(c-1)*4096,(r-1)*4096,c*4096,r*4096]
    index=p.load(p.ROOT/'current-native-map.json')
    final=Path(index['candidateArtifacts'][finaltile]['path'])
    x0,y0,x1,y1=max(box[0],fb[0]),max(box[1],fb[1]),min(box[2],fb[2]),min(box[3],fb[3])
    assert x1>x0 and y1>y0
    crop=[x0-fb[0],y0-fb[1],x1-fb[0],y1-fb[1]]; dest=[x0-box[0],y0-box[1]]
    with Image.open(guide) as g,Image.open(final) as f:
        result=g.convert('RGB');result.paste(f.crop(crop),tuple(dest));result.save(guide)
    deriv['derivedFrom'].append({**p.metadata(final,'actual current neighboring final candidate; overrides all prior source pixels in this intersection'),'sourceCrop':crop,'destinationTopLeft':dest,'generationRecord':index['candidateArtifacts'][finaltile]['record']})
    deriv['sha256']=p.hashfile(guide);p.dump(str(guide)+'.derivation.json',deriv)
    print({'actualFinalNeighborConstraint':final.as_posix(),'crop':crop,'destination':dest})

def external_left_check(stem,lefttile,name):
    src=p.ROOT/'native'/f'{stem}.png'
    co=p.load(str(src)+'.generation.json')['coordinates']
    idx=p.load(p.ROOT/'current-native-map.json')
    final=Path(idx['candidateArtifacts'][lefttile]['path'])
    r,c=map(int,(lefttile[1:3],lefttile[5:7]))
    assert co['coreGlobalBox'][0]==c*4096
    yy=co['coreGlobalBox'][1]-(r-1)*4096
    assert 0<=yy<=3072
    crops=[[3796,yy,4096,yy+1024],[115,115,415,1139]]
    with Image.open(final) as f,Image.open(src) as im:
        out=Image.new('RGB',(600,1024));out.paste(f.crop(crops[0]),(0,0));out.paste(im.crop(crops[1]),(300,0))
    dest=p.ROOT/'qa'/f'{name}.png';out.save(dest)
    p.dump(str(dest)+'.derivation.json',{'sha256':p.hashfile(dest),'operation':'same-coordinate hard crop/paste native100; no resampling','sources':[p.metadata(final,'actual current neighbor4K candidate'),p.metadata(src,'new candidate core')],'sourceCrops':crops,'seamAt':300,'globalY':[co['coreGlobalBox'][1],co['coreGlobalBox'][3]],'notFinalPairAcceptance':True})


