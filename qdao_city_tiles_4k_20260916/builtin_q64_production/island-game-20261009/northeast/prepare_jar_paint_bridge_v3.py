from native_work import *
ident='r04_c12_cross_01_02_jar_paint_repair_v3'
old=read(ZONE/'guides/r04_c12_cross_01_02_jar_paint_repair_v2.png.derivation.json')
can=Image.new('RGB',(4096,8192));sources=[]
for s in old['sources']:
 s=dict(s)
 if s['sha256']=='0405a72d05a7e7cb6982dde405eb6aa1188079af02c77848bba5940f283292e1':s['file']=(ZONE/'qa/history/0405a72d05a7-r03_c12.png').as_posix()
 assert sha(s['file'])==s['sha256']
 can.paste(Image.open(s['file']).crop(s['sourceCrop']),s['canvasPaste']);sources.append(s)
other=read(ZONE/'qa/r04_c12_cross_01_03_jar_repair.overlay.json');can.paste(Image.open(other['source']).crop(other['coreCrop']),(other['tileLocalPaste'][0],4096+other['tileLocalPaste'][1]))
base=can.crop((1421,3725,2675,4979));prior=ZONE/'native/r04_c12_cross_01_02_jar_paint_repair_v2.png';base.paste(Image.open(prior).crop((256,256,998,998)),(256,256))
gp=ZONE/'guides'/f'{ident}.png';assert not gp.exists();base.save(gp)
d={**old,'sources':sources,'operation':'exact source canvas including neighboring foot repair; prior v2 inner742 square inserted into original1254 target; outer256 preserved as native color anchors; guide only','additionalOverlay':other,'priorInner':{'file':prior.as_posix(),'sha256':sha(prior),'sourceCrop':[256,256,998,998],'targetPaste':[256,256]},'finalArt':False};write(gp.with_suffix('.png.derivation.json'),d)
cp=ZONE/'guides'/f'{ident}.context.png';can.crop((1024,3328,3072,5376)).save(cp);write(cp.with_suffix('.png.derivation.json'),{'operation':'exact2048context no scale','sources':sources,'additionalOverlay':other,'finalArt':False})
refs=[{'file':gp.as_posix(),'sha256':sha(gp),'role':'edit target with exact original outer256 native color and interior corrected jar paint','derivationRecord':gp.with_suffix('.png.derivation.json').as_posix()},{'file':cp.as_posix(),'sha256':sha(cp),'role':'surrounding original native context geometry only','derivationRecord':cp.with_suffix('.png.derivation.json').as_posix()},*current_references()];write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
for oid in ['r04_c12_cross_01_02_jar_paint_repair_v2','r03_c12_cross_04_02_jar_paint_bridge']:
 q=read(ZONE/'qa'/f'{oid}.overlay.json');q.update(review='pending_color_perimeter_revision',notes='Independent review sees small top/right paint value steps; geometry and actual4K crossing pass. v3 underway.');write(ZONE/'qa'/f'{oid}.overlay.json',q)
p=ZONE/'tiles/r03_c12.png.derivation.json';q=read(p);q.update(internalReview='pending small perimeter color revision on jar bridge',status='native_coverage_pending_color_revision');write(p,q)
print(json.dumps({'id':ident,'refs':len(refs)}))

