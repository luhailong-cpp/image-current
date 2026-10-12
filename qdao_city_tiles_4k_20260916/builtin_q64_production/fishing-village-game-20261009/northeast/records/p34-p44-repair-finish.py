from pathlib import Path
from PIL import Image, ImageChops, ImageStat
import json,hashlib,datetime,shutil
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):return {'path':str(p),'sha256':sha(p),'role':role}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
source=Path('C:/Users/luyua/.codex/generated_images/01a12173-24a9-7203-9696-bbaf72d918c4/exec-da8db31a-4493-408c-ad86-39749359b8b9.png')
native=B/'native/p34-p44-repair-native-v1.png'
assert not native.exists()
shutil.copyfile(source,native)
im=Image.open(native)
subpath=B/'records/p34-p44-repair-v1.submission.json'
receipt=B/'records/p34-p44-repair-v1.receipt.json'
sub=read(subpath);plan=read(B/'records/p34-p44-repair-plan.json')
for item in sub['references']:assert sha(item['path'])==item['sha256'],item['path']
gen={'createdAtUtc':now,'file':str(native),'sha256':sha(native),'size':list(im.size),'nativeMetadataKeys':list(im.info),'operation':'copy host-generated native output byte for byte; no resize or repaint','route':'builtin','tool':'image_gen.imagegen','configSnapshot':sub['configSnapshot'],'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'actualVersionQualityNote':'No model or quality selectors or returned version/quality are exposed by this built-in tool. Config target is not actual evidence.','source':ref(source,'host native generated output'),'references':sub['references'],'prompt':ref(sub['promptFile'],'exact submitted full prompt'),'receipt':ref(receipt,'tool receipt'),'submission':ref(subpath,'pre-call submitted parameters record'),'actualAiCallsThisRepair':1,'formalAccepted':False,'usable':False,'status':'candidate pending visual checks'}
write(str(native)+'.generation.json',gen)
assert im.size==(1254,1254),'Native size mismatch; no rescale permitted'
im=im.convert('RGB')
def compose(a,b):
    c=Image.new('RGB',(1254,2278));c.paste(a.crop((0,0,1254,1139)),(0,0));c.paste(b.crop((0,115,1254,1254)),(0,1139));return c
paths={}
images={}
for part in plan['candidateBackPastePlan']:
    patch=part['patch'];old=B/('native/r06_c12_'+patch+'-v1.png')
    assert sha(old)==plan['topPatch' if patch=='p34' else 'bottomPatch']['sha256']
    dst=B/('native/p34-p44-repair-'+patch+'-candidate-v1.png')
    out=Image.open(old).convert('RGB');out.paste(im.crop(tuple(part['repairSourceBox'])),tuple(part['destinationBox'][:2]));out.save(dst)
    images[patch]=out;paths[patch]=dst
    write(str(dst)+'.derived.json',{'file':str(dst),'sha256':sha(dst),'size':list(out.size),'sources':[ref(old,'original patch'),ref(native,'one joint repair native output')],'operation':'opaque 1:1 native rectangular paste; no scaling, blending, feathering, repaint or synthesized pixels','repairSourceBox':part['repairSourceBox'],'destinationBox':part['destinationBox'],'status':'candidate pending visual checks','formalAccepted':False,'usable':False,'modelQualityInheritedFrom':ref(str(native)+'.generation.json','native generated provenance')})
oldcombo=compose(Image.open(plan['topPatch']['path']).convert('RGB'),Image.open(plan['bottomPatch']['path']).convert('RGB'))
combo=compose(images['p34'],images['p44'])
expected=oldcombo.copy();expected.paste(im,(0,512));assert ImageChops.difference(combo,expected).getbbox() is None
qafiles=[]
def saveqa(name,view,sources,operation,extra=None):
    p=B/('qa/p34-p44-repair-'+name+'.png');view.save(p)
    data={'file':str(p),'sha256':sha(p),'size':list(view.size),'sources':sources,'operation':operation,'native1to1':True,'formalAccepted':False}
    if extra:data.update(extra)
    write(str(p)+'.derived.json',data);qafiles.append(data)
sr=[ref(paths['p34'],'repaired p34 candidate'),ref(paths['p44'],'repaired p44 candidate')]
saveqa('joint-candidate-v1',combo,sr,'native vertical assembly; p34 source [0,0,1254,1139], p44 source [0,115,1254,1254]')
for name,y in [('upper-insertion-boundary',512),('core-boundary',1139),('lower-insertion-boundary',1766)]:
    saveqa(name,combo.crop((0,y-128,1254,y+128)),sr,'native crop from joint candidate',[ ][0] if False else {'jointCropBox':[0,y-128,1254,y+128],'seamLocalY':128})
for left,right in [('p33','p34'),('p43','p44')]:
    lp=B/('native/r06_c12_'+left+'-v1.png')
    li=Image.open(lp).convert('RGB');v=Image.new('RGB',(256,1254));v.paste(li.crop((1011,0,1139,1254)),(0,0));v.paste(images[right].crop((115,0,243,1254)),(128,0))
    saveqa(left+'-'+right+'-left-neighbor',v,[ref(lp,'left native neighbor'),ref(paths[right],'new right native candidate')],'native core-cut stripe; left [1011,0,1139,1254], right [115,0,243,1254]',{'seamLocalX':128})
saveqa('left-guard-interior',im.crop((52,0,308,1254)),[ref(native,'native repair')],'native crop [52,0,308,1254] around requested x180 guard boundary',{'guardBoundaryLocalX':128})
oldtarget=Image.open(plan['target']['path']).convert('RGB')
metrics={}
for key,box in plan['guardBands'].items():
    diff=ImageChops.difference(oldtarget.crop(tuple(box)),im.crop(tuple(box)))
    hist=diff.convert('RGB').histogram()
    total=(box[2]-box[0])*(box[3]-box[1])*3
    unchanged=sum(hist[i*256] for i in range(3))
    metrics[key]={'box':box,'meanAbsoluteChannelDifference':sum(ImageStat.Stat(diff).mean)/3,'unchangedChannelRatio':unchanged/total,'exactlyIdentical':diff.getbbox() is None}
check={'createdAtUtc':now,'actualAiCallsThisRepair':1,'nativeGenerated':ref(native,'one new AI output'),'nativeSize':[1254,1254],'candidateFiles':[ref(paths[x],x+' candidate only') for x in ['p34','p44']],'jointWorldBox':[48013,22413,49267,24691],'repairWorldBox':plan['worldBox'],'repairInJointBox':[0,512,1254,1766],'coreBoundaryInJointY':1139,'coreBoundaryInRepairY':627,'sourceOverlapExactlySameRepairPixels':True,'backPasteExactNoScaling':True,'guardDifferenceMetricsNotVisualAcceptance':metrics,'qaFiles':qafiles,'rightTileExternalEdge':'unreviewed/unaccepted exterior; no pass claim','formalAccepted':False,'usable':False,'allChecksPassed':False,'visualReviewPending':True}
write(B/'qa/p34-p44-repair-check.json',check)
print(json.dumps({'native':str(native),'sha256':sha(native),'size':list(im.size),'candidates':[str(p) for p in paths.values()],'qaCount':len(qafiles),'guardMetrics':metrics}))

