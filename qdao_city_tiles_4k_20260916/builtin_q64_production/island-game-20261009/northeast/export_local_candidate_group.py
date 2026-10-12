from native_work import *
import numpy as np,re
export=ZONE/'exports/20261011-local-v1';export.mkdir(parents=True,exist_ok=True)
tids=[f'r{r:02}_c{c:02}' for r in [3,4] for c in [12,13,14]];mosaic=Image.new('RGB',(12288,8192));entries=[]
for tid in tids:
 p=ZONE/'tiles'/f'{tid}.png';d=read(p.with_suffix('.png.derivation.json'));assert sha(p)==d['sha256'];im=Image.open(p).convert('RGB');assert im.size==(4096,4096)
 replay=Image.new('RGB',(4096,4096))
 for s in d['sources']:
  assert sha(s['file'])==s['sha256'];replay.paste(Image.open(s['file']).crop(s['coreCrop']),s['tileLocalPaste'])
 for s in d['requiredOverlays']:
  assert sha(s['source'])==s['sha256'];replay.paste(Image.open(s['source']).crop(s['coreCrop']),s['tileLocalPaste'])
 assert np.array_equal(np.array(replay),np.array(im)),tid
 r,c=map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',tid).groups());mosaic.paste(im,((c-12)*4096,(r-3)*4096))
 entries.append({'tileId':tid,'file':p.as_posix(),'sha256':sha(p),'size':[4096,4096],'worldBox':d['worldBox'],'internalReview':d['internalReview'],'coreCount':len(d['sources']),'overlayCount':len(d['requiredOverlays']),'nativeRebuildDifferencePixels':0,'formalAccepted':False,'derivation':p.with_suffix('.png.derivation.json').as_posix()})
dest=export/'r03-r04_c12-c14-native-candidate.png';assert not dest.exists();mosaic.save(dest)
preview=export/'r03-r04_c12-c14-preview.png';mosaic.resize((3072,2048),Image.Resampling.LANCZOS).save(preview)
for c in [1,2]:mosaic.crop((c*4096-512,4096-512,c*4096+512,4096+512)).save(export/f'cross-{c}-100pct.png')
index={'status':'continuous_native_candidate_with_two_internal_color_repairs_pending','exportedAtUtc':now(),'originalZoneTargetTiles':49,'excludedElsewhere':['r01_c13','r01_c14','r02_c13','r02_c14'],'ownedTargetTiles':45,'completeNativeCoverageTiles':6,'currentlyInternalPassedTiles':4,'internalColorRepairTiles':['r03_c12','r03_c13'],'formalAcceptedTiles':0,'tiles':entries,'mosaic':{'file':dest.as_posix(),'sha256':sha(dest),'size':[12288,8192],'worldBox':[45056,8192,57344,16384],'operation':'exact paste of6 current4096native tiles; no scale/feather','preview':preview.as_posix(),'previewDownsampledOnly':True},'knownDefects':[{'tileIds':['r03_c12','r03_c13'],'issue':'gold gourd horizontal color band around tile-localy2048'},{'tileIds':['r03_c12'],'issue':'slender clay bottle horizontal color band around tile-localy3072'}],'sharedEdgeGeometryReviewedPairs':[['r03_c12','r03_c13'],['r03_c13','r03_c14'],['r03_c12','r04_c12'],['r03_c13','r04_c13'],['r03_c14','r04_c14'],['r04_c12','r04_c13'],['r04_c13','r04_c14']],'outerAdjacentTileEdgesNotFullyAcceptedCount':8,'mapBoundaryEdges':2,'allSourcesRetained':True,'actualModel':None,'actualQuality':None}
write(export/'delivery-index.json',index)
print(json.dumps({'candidateTiles':6,'internalPassedTiles':4,'mosaic':index['mosaic'],'index':(export/'delivery-index.json').as_posix()}))

