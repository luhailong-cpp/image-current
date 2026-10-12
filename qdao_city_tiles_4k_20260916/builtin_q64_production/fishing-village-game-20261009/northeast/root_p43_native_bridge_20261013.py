import json
from PIL import Image
import root_workflow as w
import r06_c14_extension as b
Z=w.Z;left=Z/'native'/'r04_c12_p42-v1.png';right=Z/'native'/'r04_c12_p43-v2.png';p='r04_c12_p42-p43-crestbridge';v='v1'
assert b.sha(left)=='77df366d0e02bd7adceb61fb442ab28fe42f7e01e2c9773d9a3ec2b622c0e75d';assert b.sha(right)=='a2816dbf1d3b06816724a060d8a208925e12e686d60507263c796b1bca1c66ea'
a=Image.new('RGB',(1254,1254));a.paste(Image.open(left).convert('RGB').crop((512,0,1139,1254)),(0,0));a.paste(Image.open(right).convert('RGB').crop((115,0,742,1254)),(627,0));f=Z/'guides'/f'{p}-{v}.native-target.png';assert not f.exists();a.save(f)
co={'id':p,'nativeGlobalBox':[46477,15245,47731,16499],'expectedSize':[1254,1254],'purpose':'repair centered native seam; no independent formal core'}
src=[dict(b.ref(left,'left selected core/halo native source'),cropBox=[512,0,1139,1254],pasteAt=[0,0]),dict(b.ref(right,'right pending candidate native source'),cropBox=[115,0,742,1254],pasteAt=[627,0])];w.atomic(str(f)+'.derived.json',{'purpose':'exact native repair target; not final art','coordinates':co,'sources':src,'operation':'integer crop+opaque paste only','resized':False,'centerSeamX':627})
refs=[b.ref(b.C['layoutReference'],'layout only'),b.ref(b.C['detailStyleReference'],'material only'),b.ref(b.C['primaryStyleReference'],'primary Q style only'),b.ref(f,'native centered seam target')]
plan={'patchId':p,'createdAtUtc':b.now(),'coordinates':co,'references':refs,'nativeEdgeSources':[],'expectedNativeSize':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'repairPurpose':'centered crest seam near x627 upper portion; final contributions must be limited and separately validated'};plan.update(b.config_evidence());w.atomic(Z/'records'/f'{p}-{v}.plan.json',plan);print(str(f))
