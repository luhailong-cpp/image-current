from r06_c13_extension import *
p='r06_c13_p41';v='v2'
a=Image.open(Z/'native'/f'{p}-v1.png').convert('RGB')
sources=[]
for f,side,box,xy in [
('r07_c12_northrepair44-bridge-candidate.png','left',[1024,0,1254,1254],[0,0]),
('r06_c13_p42-v1.png','right',[0,0,230,1254],[1024,0]),
('r06_c13_p31-v1.png','top',[0,1024,1254,1254],[0,0])]:
 path=Z/'native'/f
 a.paste(Image.open(path).convert('RGB').crop(box),xy)
 rr=ref(path,'exact_native_'+side+'_230px');rr.update(cropBox=box,pasteAt=xy);sources.append(rr)
gp=Z/'guides'/f'{p}-{v}.native-edge-repair.png';a.save(gp)
write(str(gp)+'.derived.json',{'purpose':'guide only; target body with updated native left/right/top anchors, not final artwork','target':ref(Z/'native'/f'{p}-v1.png','edit target'),'sources':sources,'operation':'opaque1:1 strips, no final painting'})
plan=json.loads((Z/'records'/f'{p}.plan.json').read_text(encoding='utf-8'))
plan['createdAtUtc']=now();plan['nativeEdgeSources']=sources
plan['references']=plan['references'][:3]+[ref(gp,'precise edit guide; new left wood floor, old incorrect center gray floor must be replaced')]
plan['configSnapshot']=json.loads(CONFIG.read_text(encoding='utf-8-sig'));plan['configSource']=ref(CONFIG,'configured target only, not actual selector')
plan['editTarget']=ref(Z/'native'/f'{p}-v1.png','original candidate')
write(Z/'records'/f'{p}-{v}.plan.json',plan)
print(str(gp))
