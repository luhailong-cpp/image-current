from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,io
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=read(z/'tiles/r03_c12.png.derivation.json');final=Image.open(d['file']).convert('RGB')
rebuild=Image.new('RGB',final.size);sources=[]
for item in d['sources']:
 p=Path(item['file']);sources.append({'path':str(p),'sha256':sha(p),'matches':sha(p)==item['sha256']})
 rebuild.paste(Image.open(p).convert('RGB').crop(item['coreCrop']),tuple(item['tileLocalPaste'][:2]))
for item in d['requiredOverlays']:
 p=Path(item['source']);sources.append({'path':str(p),'sha256':sha(p),'matches':sha(p)==item['sha256']})
 rebuild.paste(Image.open(p).convert('RGB').crop(item['coreCrop']),tuple(item['tileLocalPaste'][:2]))
arr=np.array(final);diff=np.any(np.array(rebuild)!=arr,axis=2)
previousPath=z/'qa/history/0405a72d05a7-r03_c12.png'
previous=Image.open(previousPath).convert('RGB')
changed=np.any(np.array(previous)!=arr,axis=2);outside=changed.copy();outside[3840:4096,1536:2560]=False
ys,xs=np.where(changed)
buf=io.BytesIO();rebuild.save(buf,format='PNG');rebuiltHash=hashlib.sha256(buf.getvalue()).hexdigest()
repair=z/'native/r04_c12_cross_01_02_jar_paint_repair_v2.png';r=read(repair.with_suffix('.png.generation.json'))
top=np.array(Image.open(z/'qa/r04_c12_cross_01_02_jar_paint_repair_v2.top-100pct.png')).astype(float)
seam=float(np.abs(top[100,400:]-top[99,400:]).mean())
near=float(np.abs(top[90:110,400:][1:]-top[90:110,400:][:-1]).mean())
a={'scope':'Independent review of paired jar paint bridge v2 and r03_c12 revised native export','reviewer':'east_finish','status':'provenance_passed_visual_top_perimeter_color_step_requires_review','tileId':'r03_c12','tileSha256':sha(Path(d['file'])),'recordedTileSha256Matches':sha(Path(d['file']))==d['sha256'],'nativeReplayDifferencePixels':int(diff.sum()),'nativeReplayPngSha256':rebuiltHash,'nativeReplayExactPngHashMatch':rebuiltHash==sha(Path(d['file'])),'changedRectangle':[1536,3840,2560,4096],'actualChangedBBox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],'changedPixelsOutsideRectangle':int(outside.sum()),'unchangedTopLeftRightBoundaries':not bool(changed[:,:115].any() or changed[:,-115:].any() or changed[:115,:].any()),'priorSnapshot':str(previousPath),'priorSnapshotSha256':sha(previousPath),'sourceChecks':sources,'repairSha256':sha(repair),'repairOriginalToolBytesMatch':sha(repair)==sha(Path(r['evidence']['originalToolPath'])),'actualModel':r['actualModel'],'actualQuality':r['actualQuality'],'nativeSize':list(Image.open(repair).size),'visualReview':{'top':'not passed: visible straight horizontal glaze tone step at image y100 across orange jar and blue jewel; this is exact outer overlay perimeter.','bottom':'passed: pale paving geometry/color continues','left':'passed: paving grid and texture continue','right':'geometry passed; faint straight vertical glaze tone line at image x100 remains suspect, needs parent review','actual-tile-boundary':'passed: jar/paving smoothly continuous across true4K seam'},'topColorDiagnostic':{'jarRegionX':[400,1024],'boundaryRowAbsoluteMeanChannelDelta':seam,'neighboring20RowMeanDelta':near,'note':'diagnostic supports visual review, not independent pass threshold'},'resized':False,'feathered':False,'formalAccepted':False,'reviewedAtUtc':datetime.now(timezone.utc).isoformat()}
assert all(s['matches'] for s in sources)
(z/'qa/r03_c12-jar-bridge-independent-east-audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:a[k] for k in ['status','tileSha256','nativeReplayDifferencePixels','nativeReplayExactPngHashMatch','changedPixelsOutsideRectangle','actualChangedBBox','topColorDiagnostic']}))

