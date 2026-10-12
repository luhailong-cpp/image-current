from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,datetime
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
src=Z/'native/r05_c12_p11-p21-loweredge-v3.png';im=Image.open(src).convert('RGB')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
qa=Z/'qa/r05_c12-loweredge-v3-plane-trial'
base_context=Z/'qa/r05_c12-roofbridge-v1/context.native-1to1.png'
context=qa/'context.native-1to1.png'
new_context=Image.open(context).convert('RGB')
qa_defs=[('context',[0,0,1254,1254]),('top',[0,547,1024,707]),('bottom',[0,1020,1024,1180]),('right',[820,547,980,1180]),('left-halo',[0,547,160,1180]),('interior-blue-tiles',[0,620,900,970])]
qa_records=[]
for label,crop in qa_defs:
 p=qa/f'{label}.native-1to1.png';qi=Image.open(p).convert('RGB')
 qa_records.append(dict(path=str(p),sha256=sha(p),rawRGBPixelSha256=hashlib.sha256(qi.tobytes()).hexdigest(),nativeSize=list(qi.size),contextCrop=crop,operation='exact integer crop from assembled native context; no resize'))
contrib=[]
proof=[]
delta={}
for patch,ngb,sourcecrop,pasteat in [('r05_c12_p11',[44941,16269,46195,17523],[0,627,900,742],[0,1139]),('r05_c12_p21',[44941,17293,46195,18547],[0,627,900,1100],[0,115])]:
 base=Z/f'native/{patch}-roofbridge-v1.png';out=Z/f'native/{patch}-roofbridge-v3-plane.png';assert not out.exists()
 old=Image.open(base).convert('RGB');new=old.copy();new.paste(im.crop(sourcecrop),tuple(pasteat));new.save(out)
 width=sourcecrop[2]-sourcecrop[0];height=sourcecrop[3]-sourcecrop[1]
 rect=[pasteat[0],pasteat[1],pasteat[0]+width,pasteat[1]+height]
 restored=new.copy();restored.paste(old.crop(rect),tuple(pasteat))
 outside_equal=ImageChops.difference(restored,old).getbbox() is None
 cropped_equal=ImageChops.difference(new.crop(rect),im.crop(sourcecrop)).getbbox() is None
 assert outside_equal and cropped_equal
 world=[44941+sourcecrop[0],16781+sourcecrop[1],44941+sourcecrop[2],16781+sourcecrop[3]]
 inherited=read(str(base)+'.derived.json')
 contribution=dict(source=str(src),sourceSha256=sha(src),sourceCropBox=sourcecrop,pasteAt=pasteat,targetLocalBox=rect,worldBox=world)
 record=dict(schemaVersion=1,file=str(out),sha256=sha(out),coordinates=inherited['coordinates'],pixels=list(new.size),nativeGlobalBox=ngb,
 operation='Exact integer crop and opaque paste from one generated native image; no resize, paint, blend, color adjustment or feather',
 derivedFrom=[dict(path=str(base),sha256=sha(base),derivedRecord=dict(path=str(base)+'.derived.json',sha256=sha(str(base)+'.derived.json'))),dict(path=str(src),sha256=sha(src),generationRecord=dict(path=str(src)+'.generation.json',sha256=sha(str(src)+'.generation.json')))],
 contributions=[contribution],inheritedNativeSourcesPreserved=True,
 mechanicalProof=dict(outsideContributionEqualToBase=outside_equal,contributionEqualToExactNativeSourceCrop=cropped_equal),
 status='proposed_local_roof_seam_repair_pending_root_independent_review',formalAccepted=False)
 save(Path(str(out)+'.derived.json'),record)
 contrib.append(dict(path=str(out),sha256=sha(out),record=dict(path=str(out)+'.derived.json',sha256=sha(str(out)+'.derived.json')),contribution=contribution))
 delta[patch]=out.name
 proof.append(dict(patch=patch,outsideContributionEqualToBase=outside_equal,contributionEqualToExactNativeSourceCrop=cropped_equal))
save(qa/'native-contribution-proof.json',dict(schemaVersion=1,source=dict(path=str(src),sha256=sha(src),nativeSize=list(im.size)),derived=contrib,mechanicalProof=proof,qa=qa_records,formalAccepted=False))
save(Z/'records/r05_c12.roof_sol.proposed-selection-v3-plane-20261012.json',dict(schemaVersion=1,agent='roof_sol',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 purpose='Replace only p11/p21 derived roofbridge using consistent lower roof plane; working selection unchanged by child',
 selectionDelta=delta,expectedCurrentSelection={'r05_c12_p11':'r05_c12_p11-roofbridge-v1.png','r05_c12_p21':'r05_c12_p21-roofbridge-v1.png'},
 generatedSource=dict(path=str(src),sha256=sha(src),nativeSize=list(im.size),generationRecord=dict(path=str(src)+'.generation.json',sha256=sha(str(src)+'.generation.json'))),
 exactContribution=dict(sourceLocalBox=[0,627,900,1100],worldBox=[44941,17408,45841,17881]),derived=contrib,qa=qa_records,
 inheritedV1Contribution=dict(sourceLocalBox=[0,490,1254,740],worldBox=[44941,17271,46195,17521]),
 rootIndependentReview='pending',formalAccepted=False,externalLeftJoin='unreviewed: no native c11 neighbor exists; contribution begins at existing frame edge; x0..115 is native halo',
 priorAttemptsPreserved=[dict(version='loweredge-v2',reason='Rejected wide narrow strip changed pitch at bottom/side cuts'),dict(version='loweredge-v3 two small windows',reason='Rejected window cuts truncate redrawn curves')]))
print(json.dumps(dict(selectionDelta=delta,derived=contrib,mechanicalProof=proof),ensure_ascii=False))
