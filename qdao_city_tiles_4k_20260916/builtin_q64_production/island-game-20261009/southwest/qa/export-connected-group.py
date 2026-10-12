"""Export the reviewed four-tile group without resampling any delivered pixels."""
from pathlib import Path
import sys,argparse,shutil,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import ROOT,load,dump,metadata,hashfile,now
from native_multi_tile_repair import read_base
from PIL import Image
import numpy as np

ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--review',required=True);ap.add_argument('--version',default='v01');a=ap.parse_args()
spec=load(a.spec); review=load(a.review)
assert review['connectedSharedEdgesPassed'] and review['fourWayJunctionPassed']
out=ROOT/'output'/f'contiguous-r09-r10-c03-c04-{a.version}'
assert not out.exists();out.mkdir()
tile_names=['r09_c03','r09_c04','r10_c03','r10_c04'];tiles=[];canvas=Image.new('RGB',(8192,8192))
for i,tile in enumerate(tile_names):
 pre=spec[tile];paths=[ROOT/'qa'/(pre+s) for s in ['-candidate-4096.png','-source-id-mask.png','-report.json']]
 base=read_base(paths);report=load(paths[2]);assert base['tile']==tile
 art=out/f'{tile}-native-4096.png';mask=out/f'{tile}-source-id-mask.png';rp=out/f'{tile}-source-report.json'
 for src,dst in zip(paths,[art,mask,rp]):shutil.copy2(src,dst);assert hashfile(src)==hashfile(dst)
 used=set(map(int,np.unique(base['ids'])));sources=[s for s in report['inputs'] if s['sourceId'] in used]
 unique_sources={(s['path'],s['sha256']) for s in sources}
 entry={**metadata(art,'4096 native traced candidate; internal and connected-group QA passed'),'tile':tile,'candidateGlobalBox':base['box'],'qaPrefix':pre,'sourceIdMask':metadata(mask,'source-ID map'),'sourceReport':{'path':str(rp),'sha256':hashfile(rp)},'contributingSourceIdCount':len(used),'uniqueNativeSourceCount':len(unique_sources),'validation':base['baseValidation'],'internalPassed':True,'connectedGroupEdgesPassed':True,'allOuterTileEdgesPassed':False,'formalAccepted':False}
 deriv=out/f'{tile}-native-4096.png.derivation.json';dump(deriv,{**entry,'createdAtUtc':now(),'operation':'lossless byte-for-byte copy of source-verified native candidate','derivedFrom':[metadata(paths[0],'reviewed QA candidate')],'groupReview':str(Path(a.review).resolve())});entry['derivation']=str(deriv)
 tiles.append(entry);canvas.paste(Image.fromarray(base['base']),((i%2)*4096,(i//2)*4096))
del base
combined=out/'r09-r10-c03-c04-native-8192.png';canvas.save(combined)
with Image.open(combined) as im:
 assert im.size==(8192,8192)
 for i,tile in enumerate(tiles):
  with Image.open(tile['path']) as part:assert np.array_equal(np.array(im.crop(((i%2)*4096,(i//2)*4096,(i%2+1)*4096,(i//2+1)*4096))),np.array(part))
preview=out/'preview-2048.png';canvas.resize((2048,2048),Image.Resampling.LANCZOS).save(preview)
manifest={'createdAtUtc':now(),'status':'four native candidates with internal and connected-group shared-edge QA passed; group outer joins remain pending','groupGlobalBox':[8192,32768,16384,40960],'tiles':tiles,'combined':metadata(combined,'native same-coordinate 2x2 hard paste; no resampling'),'preview':metadata(preview,'4:1 downsampled display preview only'),'combinedPixelCount':8192*8192,'combinedExactlyMatchesFourTiles':True,'candidate4kCount':4,'internalPassed4kCount':4,'connectedGroupPassed4kCount':4,'fullyExternalPassed4kCount':0,'formalAcceptedCount':0,'groupReview':{'path':str(Path(a.review).resolve()),'sha256':hashfile(a.review)},'remainingZoneTiles':45,'zoneTileCount':49,'actualModel':None,'actualQuality':None,'limitations':['Group outer perimeter neighbors have not been generated and checked.','A few slight native brushwork/material changes are recorded in local QA.','This is one contiguous group, not the whole southwest zone or whole map.']}
dump(out/'manifest.json',manifest)
dump(str(combined)+'.derivation.json',{'operation':'native-size same-coordinate hard paste of four 4096 exports','globalBox':manifest['groupGlobalBox'],'sourceTiles':[{'path':e['path'],'sha256':e['sha256'],'globalBox':e['candidateGlobalBox']} for e in tiles],'sha256':hashfile(combined),'pixelCount':8192*8192,'allTileCropsExact':True,'resampling':False})
print(json.dumps({'outputDirectory':str(out),'manifest':str(out/'manifest.json'),'combined':str(combined),'preview':str(preview),'counts':[4,4,4,0]},ensure_ascii=False))
