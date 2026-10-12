from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
Z=Q.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=Z/'r09_c08/native/p44-v2.png'
south=Z/'r10_c08/processed/colorpass/p14-colorpass.png'
assert sha(original)=='65460e7999a2f127e892daaa8772217be8c78d6f72db5da66293ac9bb5ae5720'
assert sha(south)=='68e603da60a10c7ca9c0f6e7392ea85322ae59502ff3550cbed3b66e3ca691f4'
raw2=Path('C:/Users/luyua/.codex/generated_images/01a13554-e65d-71e2-a119-8c3677ffd303/exec-1c02855c-4e31-44fc-960a-ecdb752b9bef.png')
saved2=Q/'window-v2-raw.png';assert not saved2.exists();shutil.copyfile(raw2,saved2)
with Image.open(saved2) as im:dims=list(im.size)
assert dims==[1254,1254]
g=dict(savedAtUtc=datetime.now(timezone.utc).isoformat(),tool='image_gen__imagegen',route='builtin',
 file=str(saved2),sha256=sha(saved2),sourcePath=str(raw2),nativeDimensions=dims,actualModel=None,actualQuality=None,
 prompt=str(Q/'window-v2.prompt.txt'),request=str(Q/'window-v2.request.json'),receipt=str(Q/'window-v2.receipt.json'),
 imageOperation='Byte-exact copy of actual builtin output',selected=False)
(Q/'window-v2-raw.png.generation.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8')
base=Image.open(original).convert('RGB')
joint=Image.open(Q/'joint-input-v1-1254.png').convert('RGB')
frame_box=[602,530,900,799]
native_box=[frame_box[0]+115,frame_box[1]+340,frame_box[2]+115,frame_box[3]+340]
world_box=[31744+frame_box[0],36065+frame_box[1],31744+frame_box[2],36065+frame_box[3]]
records=[]
for v in (1,2):
    raw=Image.open(Q/f'window-v{v}-raw.png').convert('RGB');assert raw.size==(1254,1254)
    candidate=base.copy();candidate.paste(raw.crop(frame_box),tuple(native_box[:2]))
    native=Q/f'p44-window-v{v}-QA-only.png';assert not native.exists();candidate.save(native)
    composite=joint.copy();composite.paste(raw.crop(frame_box),tuple(frame_box[:2]))
    cp=Q/f'joint-window-v{v}-north-only-QA.png';composite.save(cp)
    wp=Q/f'window-v{v}-boundary-100pct.png';composite.crop([550,480,980,1090]).save(wp)
    seam=Q/f'window-v{v}-actual-south-join-100pct.png';composite.crop([550,735,980,863]).save(seam)
    a=np.asarray(candidate);b=np.asarray(base);mask=np.zeros(a.shape[:2],bool)
    mask[native_box[1]:native_box[3],native_box[0]:native_box[2]]=True
    assert np.array_equal(a[~mask],b[~mask])
    assert np.array_equal(np.asarray(composite)[799:],np.asarray(joint)[799:])
    record=dict(version=v,nativeQACandidate=str(native),nativeQACandidateSha256=sha(native),
      raw=str(Q/f'window-v{v}-raw.png'),rawSha256=sha(Q/f'window-v{v}-raw.png'),
      frameBox=frame_box,nativeBox=native_box,globalBox=world_box,
      sourceResampling=False,sourceMovement=False,sourceBlur=False,sourceBlending=False,
      exactRawAtSameWorldCoordinate=True,outsideBoundedNativeRegionUnchanged=True,
      southernExistingCoreUnchanged=True,canonicalChanged=False,
      evidence=[dict(file=str(p),sha256=sha(p),resized=False) for p in (cp,wp,seam)],
      usable=False,formalAccepted=False,adoptRecommended=False,
      review='Pending exact north-only seam visual inspection')
    records.append(record)
(Q/'bounded-candidates-qa-v1.json').write_text(json.dumps(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),
  originalNorth=str(original),originalNorthSha256=sha(original),originalSouth=str(south),originalSouthSha256=sha(south),
  originalRetained=True,candidates=records),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidateRecords=str(Q/'bounded-candidates-qa-v1.json'),rawV2Sha256=sha(saved2),nativeBox=native_box)))
