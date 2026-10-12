"""Northward adjacent generation guides and verbatim builtin-output ingestion."""
import argparse,json
from pathlib import Path
from PIL import Image
import r06_c14_extension as base

Z=Path(__file__).resolve().parent
def configure(tile):
    base.T=tile;base.ORIGIN=((int(tile[5:])-1)*4096,(int(tile[1:3])-1)*4096)
def init(tile):
    configure(tile)
    refs=[base.ref(base.C['layoutReference'],'authoritative layout'),base.ref(base.C['detailStyleReference'],'independent materials'),base.ref(base.C['primaryStyleReference'],'Q Daoist style')]
    x,y=base.ORIGIN;p=Z/'records'/f'{tile}.coordinates.json';assert not p.exists()
    base.write(p,{'tile':tile,'tileOrigin':[x,y],'tileCoreBox':[x,y,x+4096,y+4096],'references':refs,'patches':[base.coords(f'{tile}_p{r}{c}') for r in range(1,5) for c in range(1,5)]})
def prep(p):
    tile=p[:7];configure(tile);co=base.coords(p);n=1254
    im=Image.open(base.C['layoutReference']).convert('RGB').transform((n,n),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
    pure=Z/'guides'/f'{p}.layout-only.png';assert not pure.exists();im.save(pure)
    choices=Z/'records'/f'{tile}.working-selection.json';choices=json.loads(choices.read_text()) if choices.exists() else {}
    r,c=int(p[-2]),int(p[-1]);sources=[]
    if r==4:
        south=f'r{int(tile[1:3])+1:02d}_c{int(tile[5:]):02d}'
        selections={'r06_c12':'r06_c12.selection-closure-v5.json','r06_c13':'r06_c13.selection-proposed-v1.json'}
        sel=json.loads((Z/'records'/selections[south]).read_text(encoding='utf-8-sig'))
        item=sel['patches'][f'{south}_p1{c}'];bottom=Path(item if isinstance(item,str) else item['path'])
        if not bottom.is_absolute():bottom=Z/bottom
        if isinstance(item,dict):assert base.sha(bottom)==item['sha256']
    else:bottom=Z/'native'/choices.get(f'{tile}_p{r+1}{c}',f'{tile}_p{r+1}{c}-v1.png')
    left=Z/'native'/choices.get(f'{tile}_p{r}{c-1}',f'{tile}_p{r}{c-1}-v1.png') if c>1 else None
    for path,side in [(left,'left'),(bottom,'bottom')]:
        if not path:continue
        a=Image.open(path).convert('RGB');assert a.size==(n,n)
        crop=[1024,0,n,n] if side=='left' else [0,0,n,230];xy=[0,0] if side=='left' else [0,1024]
        im.paste(a.crop(crop),xy);rr=base.ref(path,'exact_native_'+side+'_230px');rr.update({'cropBox':crop,'pasteAt':xy});sources.append(rr)
    gp=Z/'guides'/f'{p}.native-edge-layout.png';assert not gp.exists();im.save(gp)
    base.write(str(gp)+'.derived.json',{'purpose':'layout-only with native pixel anchors; not final art','coordinates':co,'sources':[base.ref(base.C['layoutReference'],'layout')]+sources,'operation':'EXTENT bicubic layout guide only; native opaque1:1 strips, bottom owns corner'})
    refs=[base.ref(base.C['layoutReference'],'full-map layout only'),base.ref(base.C['detailStyleReference'],'independent materials only'),base.ref(base.C['primaryStyleReference'],'primary style only'),base.ref(gp,'exact local guide with native edge constraints')]
    plan={'patchId':p,'createdAtUtc':base.now(),'coordinates':co,'references':refs,'nativeEdgeSources':sources,'expectedNativeSize':[n,n],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
    plan.update(base.config_evidence())
    base.write(Z/'records'/f'{p}.plan.json',plan);print(json.dumps(plan,ensure_ascii=False))
if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('op');q.add_argument('patch');q.add_argument('--source');q.add_argument('--version',default='v1');a=q.parse_args()
    if a.op=='init':init(a.patch)
    elif a.op=='prepare':prep(a.patch)
    elif a.op=='ingest':base.ingest(a.patch,a.source,a.version)
