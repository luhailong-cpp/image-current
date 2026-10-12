from native_work import *
tid='r03_c09';pp=ZONE/f'patch-plan-{tid}.json'
assert not pp.exists() and not list((ZONE/'native').glob(tid+'*.png'))
split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert tid not in {t for b in split['batches'] if b['status']=='allocated_root_reserved' for t in b['tiles']}
refs=current_references();layout=Image.open(refs[0]['file']).convert('RGB');assert sha(refs[0]['file'])==refs[0]['sha256']
patches=[]
for r in range(4):
 for c in range(4):
  ident=f'{tid}_p{r+1:02d}_{c+1:02d}';x,y=32768+c*1024,8192+r*1024;box=[x-115,y-115,x+1139,y+1139];source_box=[v*1254/57344 for v in box]
  p=ZONE/'guides'/f'{ident}.layout-only.png';assert not p.exists()
  layout.transform((1254,1254),Image.Transform.EXTENT,source_box,Image.Resampling.BICUBIC).save(p)
  rec={'id':ident,'coreWorldBox':[x,y,x+1024,y+1024],'nativeWorldBox':box,'expectedNativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'layoutBox':source_box,'guide':p.as_posix(),'guideSha256':sha(p),'guideRole':'layout-only enlarged coordinate crop, forbidden as final artwork pixels','operation':'Pillow EXTENT BICUBIC of exact floating box, layout-only','derivedFrom':refs[0],'status':'not_started'}
  write(p.with_suffix('.png.derivation.json'),rec);patches.append(rec)
write(pp,{'patches':patches,'adjacentNativeOverlapPixels':230,'noFinalArtScaling':True})
print(json.dumps({'tile':tid,'preparedLayoutOnlyGuides':16,'firstCore':'r03_c09_p01_04','rightAnchor':'r03_c10_p01_01'}))
