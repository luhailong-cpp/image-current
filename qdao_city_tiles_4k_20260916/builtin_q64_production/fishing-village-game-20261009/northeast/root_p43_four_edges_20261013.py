import json
from pathlib import Path
from PIL import Image
import root_north_20261012 as n
b=n.b;Z=n.Z;p='r04_c12_p43';n.configure(p[:7]);co=b.coords(p)
target=Z/'native'/f'{p}-v3.png';a=Image.open(target).convert('RGB');d=json.loads((Z/'records/r04_c12.working-selection.json').read_text());edges=[]
source=[(Z/'native'/d['r04_c12_p42'],'left',[1024,0,1254,1254],[0,0]),(Z/'native'/d['r04_c12_p44'],'right',[0,0,230,1254],[1024,0]),(Z/'native'/d['r04_c12_p33'],'top',[0,1024,1254,1254],[0,0]),(n.selected(Z/'records/r05_c12.selection-root-v2.json','r05_c12_p13'),'bottom',[0,0,1254,230],[0,1024])]
for f,side,box,xy in source:
 im=Image.open(f).convert('RGB');assert im.size==(1254,1254);a.paste(im.crop(box),tuple(xy));rr=b.ref(f,'exact_native_'+side+'_230px');rr.update(cropBox=box,pasteAt=xy);edges.append(rr)
gp=Z/'guides'/f'{p}-v5.four-edge-native-guide.png';assert not gp.exists();a.save(gp);n.atomic(str(gp)+'.derived.json',{'purpose':'AI generation guide only, not final art','sources':[b.ref(target,'retained best existing native target')]+edges,'operation':'exact native crop/opaque paste; left right then top/bottom own corners','finalArt':False,'coordinates':co})
plan=json.loads((Z/'records'/f'{p}.plan.json').read_text());plan['coordinates']=co;plan['nativeEdgeSources']=edges;plan['references']=plan['references'][:3]+[b.ref(target,'native edit target'),b.ref(gp,'four native neighbor geometry guide')];plan['createdAtUtc']=b.now();plan['repairTarget']=b.ref(target,'native edit target');plan['repairGuide']=b.ref(gp,'fresh four-edge guide');plan['method']='Four stable real neighbor anchors now available; prior retries had only left/bottom constraints';pp=Z/'records'/f'{p}-v5.plan.json';assert not pp.exists();n.atomic(pp,plan);print(str(gp))

