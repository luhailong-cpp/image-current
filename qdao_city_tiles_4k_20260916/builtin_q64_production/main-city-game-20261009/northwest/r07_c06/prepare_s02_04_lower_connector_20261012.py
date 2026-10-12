from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'native/s02_04_orphanfix03.png';p=r/'layout-only/s02_04_orphanfix04.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
d.line((210,768,230,750),fill=(238,30,35),width=17)
d.line((230,809,339,929),fill=(238,30,35),width=13)
d.line((210,768,345,935),fill=(0,180,220),width=5)
im.save(p)
p.with_suffix('.png.derivation.json').write_text(json.dumps(dict(worldBox=[23437,25485,24691,26739],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),ink=dict(cyanDesiredGrout=[[210,768],[345,935]],redBranchesToErase=[[[210,768],[230,750]],[[230,809],[345,935]]])),indent=2),encoding='utf-8')
cp=r/'continuation-repair-checkpoint-20261012-v02.json'
assert not cp.exists()
cp.write_text(json.dumps(dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),formalAccepted=False,currentCandidate=dict(file=str(r/'candidate/r07_c06-candidate-native-roi-v05.png'),sha256=hashlib.sha256((r/'candidate/r07_c06-candidate-native-roi-v05.png').read_bytes()).hexdigest()),registry=str(r/'candidate/native-overlays-20261012-v05.json'),selectedRepair='s02_02_orphanfix03',independentReview=str(r/'qa/independent-repaired-core-20261012/independent-review.json'),westCurrentCandidate=str(r.parent/'r07_c05/candidate/r07_c05-candidate-native-rois-e1016a4a06b9410e/candidate.png'),westCurrentSHA256='9cfe09e3cb3c3ee756c1876189825b2f338a56f048ba6a287bea62da915b380f',sharedWestUpperAdoptedBothSides=True,currentUnselectedNative='s02_04_orphanfix03',currentNativeProgress='Upper direct connector fixed, tiny NE spur removed, SW dead-end removed. Incidental entire NE link (322,482)->(542,292) also removed but remaining graph has no orphan at those two nodes. Lower cuts and actual upper row1 corner remain.',nextPreparedGuide=str(p),remainingGroups=['r2c4 lower/native-halo and actual upper corner','r3c4 vertical band','r4c4 vertical band','west-row3 lower topology','triangle material fullQA'],oldGoldConcernDisprovedByWiderActualPixels=True,allOriginalsAndDraftsRetained=True,noProgressWrite=True),indent=2),encoding='utf-8')
