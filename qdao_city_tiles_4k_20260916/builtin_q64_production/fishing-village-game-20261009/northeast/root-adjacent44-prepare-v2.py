from r06_c13_extension import *
from PIL import Image
p='root-adjacent44-v2'
old=json.loads((Z/'records/root-adjacent44-v1.plan.json').read_text(encoding='utf-8'))
a=Image.open(Z/'native/root-adjacent44-v1.png').convert('RGB')
for e in old['nativeEdgeSources']:
 a.paste(Image.open(e['path']).convert('RGB').crop(e['cropBox']),e['pasteAt'])
gp=Z/'guides'/f'{p}.four-edge-guide.png';a.save(gp)
write(str(gp)+'.derived.json',{'purpose':'guide only; v1 body plus exact four native anchors','base':ref(Z/'native/root-adjacent44-v1.png','edit target'),'sources':old['nativeEdgeSources'],'operation':'opaque1:1 crop and paste; top and bottom own corners'})
old['createdAtUtc']=now();old['references']=old['references'][:3]+[ref(gp,'v2 exact native four-edge guide'),ref(Z/'native/r07_c12_northrepair43-v1.png','left neighbor thin curb geometry and material only; not whole-object layout')]
old['base']=ref(Z/'native/root-adjacent44-v1.png','v1 candidate body')
old.pop('guideCorrection',None);old.pop('topAnchorException',None)
old['configSnapshot']=json.loads(CONFIG.read_text(encoding='utf-8-sig'))
write(Z/'records'/f'{p}.plan.json',old)
