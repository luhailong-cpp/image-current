import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageStat

D=Path(__file__).resolve().parent
original=D/'inputs/p23-flower-corner-v1.png'
source=D/'source/p23-flower-corner-v1.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=Image.open(original).convert('RGB'); b=Image.open(source).convert('RGB')
assert a.size==b.size==(1254,1254)
assert sha(source)=='9998b8991cd6abbc29850d3bab13e512f425b029e19f045dbee110ec8f7ed98a'
assert sha(original)=='683e408d85c45ebb4f95d00176d3d7451d9f416f7f04909f543816d772544f73'
box=[370,430,910,1000]
mask=Image.new('L',a.size,0)
ImageDraw.Draw(mask).rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=255)
maskpath=D/'p23-flower-mask.png';mask.save(maskpath)
proposal=a.copy();proposal.paste(b,(0,0),mask)
proposalpath=D/'p23-flower-proposal.png';proposal.save(proposalpath)
changed=ImageChops.difference(proposal,a)
outside=ImageChops.multiply(changed,ImageChops.invert(mask).convert('RGB'))
assert outside.getbbox() is None
assert mask.histogram()[0]+mask.histogram()[255]==1254*1254
assert proposal.crop(box).tobytes()==b.crop(box).tobytes()
artifacts=[]
for label,crop in [('top',[340,390,940,470]),('bottom',[340,960,940,1040]),('left',[330,400,410,1030]),('right',[870,400,950,1030])]:
    p=D/f'p23-flower-edge-{label}-100pct.png';proposal.crop(crop).save(p)
    artifacts.append({'edge':label,'file':str(p),'sha256':sha(p),'contextBox':crop,'resized':False})
previewbox=[340,400,940,1030]
for label,pixels in [('before',a),('after',proposal)]:
    p=D/f'p23-flower-{label}-100pct.png';pixels.crop(previewbox).save(p)
    artifacts.append({'view':label,'file':str(p),'sha256':sha(p),'contextBox':previewbox,'resized':False})
record={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'integer-integration-proposal-edge-reviewed-with-minor-source-note',
 'source':{'file':str(source),'sha256':sha(source),'pixels':[1254,1254]},
 'original':{'file':str(original),'sha256':sha(original)},
 'inputWorldBox':[50572,20930,51826,22184],
 'mask':{'file':str(maskpath),'sha256':sha(maskpath),'pixels':[1254,1254],'values':[0,255],'contextBox':box,'nonzeroPixels':540*570},
 'proposal':{'file':str(proposalpath),'sha256':sha(proposalpath),'pixels':[1254,1254],'coordinateSpace':'repair-context, not full tile'},
 'integerTileOperations':[{'source':str(source),'sourceSha256':sha(source),'crop':box,'dest':[1790,880],
     'mask':str(maskpath),'maskSha256':sha(maskpath),'maskCrop':box,'destinationTile':'r06_c13',
     'destinationTileBox':[1790,880,2330,1450],'worldBox':[50942,21360,51482,21930]}],
 'reasonForExpansion':'The repaired branch extends below original editContextBox y=880; expanded to y=1000 to retain complete lower leaves and twig. Border crossing only permitted where original and repair continue the same unchanged object.',
 'pixelProof':{'maskOutsideUnchanged':True,'maskOutsideDifferenceBoundingBox':None,'insideMatchesGeneratedSourceExactly':True,'maskBinary':True,'integerCoordinates':True,'resized':False,'blurred':False,'feathered':False},
 'edgeQa':artifacts,
 'visualQa':{'viewedAtOriginalPixels':True,'originalAndGeneratedFullContextsViewed':True,
    'reviewedEdges':['top','bottom','left','right'],
    'edgeConclusion':'No visibly severed petal, leaf, or twig at the four integration edges. Right edge stays on continuous red timber; bottom extends below the regenerated branch into matching surrounding foliage. Minor paint-tone variation is not geometrical clipping.',
    'mainDefect':'Original 115x115 rectangular flower/leaf block is replaced by a continuous flowering branch.',
    'sourceInternalNote':{'priority':'P3','contextBox':[713,684,754,696],
      'worldBox':[51285,21614,51326,21626],
      'description':'Small pink bud behind a green leaf retains a very straight short lower occlusion edge in the generated source. This lies inside the mask, is not introduced by integration, and is recorded rather than concealed.',
      'evidence':str(D/'p23-flower-inner-bud-review-100pct.png')},
    'decision':'Proposal ready for parent integration review; no additional generation or color blending performed.'},
 'candidateModified':False,'imageGenerationCalls':0}
(D/'p23-flower-proposal.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'maskSha256':sha(maskpath),'proposalSha256':sha(proposalpath),'report':str(D/'p23-flower-proposal.json')}))
