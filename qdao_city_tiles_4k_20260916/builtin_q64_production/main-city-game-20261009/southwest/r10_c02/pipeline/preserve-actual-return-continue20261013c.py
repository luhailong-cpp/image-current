import sys,json,hashlib,shutil,re
from pathlib import Path
from PIL import Image
rp,source,started,returned,hint=sys.argv[1:]
p=Path(rp)
q=json.loads(p.read_text(encoding='utf-8-sig'))
tile=q['tile']
patch=q['coordinates']['id']
assert tile=='r10_c02'
attempt=p.name.removeprefix(patch+'.').removesuffix('.request.json')
t=p.parents[2]
s=Path(source)
assert str(s) in hint
d=t/'refinement'/'versions'/attempt/(patch+'.returned-native.png')
assert not d.exists()
d.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(s,d)
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
h=sha(d)
assert h==sha(s)
with Image.open(d) as im:pixels=list(im.size)
pres=dict(file=str(d),sha256=h,source=str(s),pixels=pixels,nativePixelsPreserved=True,resampling=False)
r=dict(tool='image_gen.imagegen',status='returned_image',route='builtin',sourceOutputPath=str(s),startedAtUtc=started,returnedAtUtc=returned,actualModel=None,actualQuality=None,paidApiUsed=False,formalAccepted=False,internalAccepted=False,request=str(p),actualReferences=q['references'],outputHint=hint,workspacePreservation=pres,visualStatus='saved_before_visual_inspection',visualDisposition='Actual returned image byte-copied immediately in the same tool execution. Selection and visual QA remain pending.')
out=t/'pipeline'/'receipts'/(patch+'.'+attempt+'.receipt.json')
assert not out.exists()
out.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(receipt=str(out),saved=pres),ensure_ascii=False))

