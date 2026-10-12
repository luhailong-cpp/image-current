from r06_c13_extension import Z,C,CONFIG,N,sha,ref,write,now
from PIL import Image
import json
p='root-adjacent44-v1'
co={'id':'r06_c12_p44','coreGlobalBox':[48128,23552,49152,24576],'nativeGlobalBox':[48013,23437,49267,24691],'nativeCoreBox':[115,115,1139,1139],'expectedSize':[1254,1254]}
base=Z/'native/r07_c12_northrepair44-bridge-candidate.png'
a=Image.open(base).convert('RGB');sources=[]
for f,side,box,xy in [
('r07_c12_northrepair43-v1.png','left',[1024,0,1254,1254],[0,0]),
('r06_c13_p41-v2.png','right',[0,0,230,1254],[1024,0]),
('resume-20261010-stall-upper-v1.png','top',[0,1024,1254,1254],[0,0]),
('r07_c12_p14-v1.png','bottom',[0,0,1254,230],[0,1024])]:
 path=Z/'native'/f;a.paste(Image.open(path).convert('RGB').crop(box),xy)
 e=ref(path,'exact_native_'+side+'_230px');e.update(cropBox=box,pasteAt=xy);sources.append(e)
gp=Z/'guides'/f'{p}.four-edge-guide.png';a.save(gp)
write(str(gp)+'.derived.json',{'purpose':'mechanical edit guide only; not final artwork','base':ref(base,'unchanged fish stall body; interior curb needs correction'),'sources':sources,'coordinates':co,'operation':'opaque1:1 native strips; bottom/top own corners'})
plan={'patchId':'r06_c12_p44','createdAtUtc':now(),'coordinates':co,'references':[ref(C['layoutReference'],'whole-map layout only'),ref(C['detailStyleReference'],'material style only'),ref(C['primaryStyleReference'],'primary Q Daoist style only'),ref(gp,'exact repair guide with all four native anchors')],'nativeEdgeSources':sources,'base':ref(base,'repair body source'),'expectedNativeSize':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'configSnapshot':json.loads(CONFIG.read_text(encoding='utf-8-sig')),'configSource':ref(CONFIG,'configured target only, not actual selector'),'configSnapshotCaptureStage':'prepare_before_generation'}
write(Z/'records'/f'{p}.plan.json',plan)
print(str(gp))
