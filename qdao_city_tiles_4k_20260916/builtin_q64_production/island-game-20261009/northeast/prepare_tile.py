from native_work import *
import sys,re
ident=sys.argv[1]; match=re.fullmatch(r'r(\d{2})_c(\d{2})',ident); assert match
row,col=map(int,match.groups()); assert 1<=row<=7 and 8<=col<=14
plan=ZONE/f'patch-plan-{ident}.json'; assert not plan.exists(), 'Refusing overwrite existing plan'
reference=read(ZONE/'reference-audit.json')['references'][0]; layout=Image.open(reference['file']).convert('RGB'); patches=[]
for r in range(4):
    for c in range(4):
        patchid=f'{ident}_p{r+1:02}_{c+1:02}'; x=(col-1)*4096+c*1024; y=(row-1)*4096+r*1024; core=[x,y,x+1024,y+1024]; box=[x-115,y-115,x+1139,y+1139]; source=[v*1254/57344 for v in box]
        guide=ZONE/'guides'/f'{patchid}.layout-only.png'; layout.transform((1254,1254),Image.Transform.EXTENT,source,Image.Resampling.BICUBIC).save(guide)
        rec={'id':patchid,'coreWorldBox':core,'nativeWorldBox':box,'expectedNativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'layoutBox':source,'guide':guide.as_posix(),'guideSha256':sha(guide),'guideRole':'layout-only enlarged coordinate crop, forbidden as final artwork pixels','operation':'Pillow EXTENT BICUBIC of exact floating box, layout-only','derivedFrom':reference,'status':'not_started'}
        write(guide.with_suffix('.png.derivation.json'),rec); patches.append(rec)
write(plan,{'patches':patches,'adjacentNativeOverlapPixels':230,'noFinalArtScaling':True})
print(plan.as_posix())
