from pathlib import Path
import json,hashlib,datetime
from PIL import Image
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=p.as_posix(),sha256=sha(p))
ip=Z/'qa/r05_c02_v5_internal_review/qa_index.json'
assert sha(ip)=='ec202aab0a2b9ef2590fe811c9621d846cf9ec5149f1521f30397d0fcc7a6830'
index=json.loads(ip.read_text(encoding='utf-8-sig'))
items=index['seamAndJunctionCrops']
notes=["Flowers and gilded cloud cap contours continuous.","Upper curved gold bands and relief continuous.","Red wall and adjacent paving continuous.","Bronze cloud curls continuous.","Taiji medallion rim and bronze contours continuous.","Medallion curvature and right body continuous.","Left cauldron foot and ground joints continuous.","Middle bronze foot and bowl contour continuous.","Bronze body and lower paving continuous.","Lower left paving and flowers continuous.","Lower central paving and shadows continuous.","Lower right paving and foliage continuous.","Flower edge, wall and golden cloud relief continuous.","Left gold body and cloud relief continuous.","Gold bowl curve and band continuous.","Red column, lantern and path continuous.","Paving slab joints meet cleanly at bronze plinth; flowers continuous.","Broad bronze body and gold relief uninterrupted.","Taiji circular rims and central dots uninterrupted.","Paving, red wooden jamb and panel meet continuously.","Cauldron foot curl and surrounding paving continuous.","Middle foot base and shadowed paving continuous.","Right foot base and diagonal slab joints continuous.","Small censer handles, feet and paving continuous.","Cloud scroll junction has continuous outline and illumination.","Broad upper bronze band continuous.","Curved body edge against paving continuous.","Lower cloud band and body continuous.","Nested medallion rings continuous.","Right medallion edge and ground continuous.","Southwest paving diagonals and foot edge continuous.","Central lower paving grout and foot edge continuous.","Cauldron underside and diagonal paving continuous."]
assert len(items)==len(notes)==33
for x,n in zip(items,notes):
 p=Path(x['path']);assert sha(p)==x['sha256']
 with Image.open(p) as im:assert list(im.size)==x['dimensions']
 x.update(status='PASS',method='independent full native crop view_image original, all 33 actually viewed in connected_continuation turn',note=n)
candidate=Z/'tiles/r05_c02_candidate-v5_4096.png'
record=Z/'tiles/r05_c02_candidate-v5_4096.native-repair.json'
assert sha(candidate)=='b528be1523f24174a0c940fcbfaa2b54ddf21adcc7ff36768ff7e3cd05142a98'
assert sha(record)=='88989850bff2ff5b316206029cbec2547a84e68351e6a22f84919c693ec8c67a'
out=Z/'qa/r05_c02_v5_independent_native33_connected_20261013.json'
assert not out.exists()
data=dict(schemaVersion=1,reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/connected_continuation',tileId='r05_c02',candidate=info(candidate),record=info(record),qaIndex=info(ip),ownerReview=info(Z/'qa/r05_c02_v5_owner_native33_review_20261013.json'),strictReplay=info(Z/'qa/r05_c02_v5_strict_native_replay_20261013.json'),status='independent_native33_PASS',passed=33,repair=0,independentInternalClosurePassed=True,formalAccepted=False,scope='Internal 24 seams and 9 junctions at native scale only; does not grant whole-map or external-edge acceptance.',items=items)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(info(out)))

