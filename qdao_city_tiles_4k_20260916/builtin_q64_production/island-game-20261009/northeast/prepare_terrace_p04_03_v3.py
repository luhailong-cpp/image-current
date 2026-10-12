from native_work import *
ident='r03_c13_p04_03_v3'
old=ZONE/'native/r03_c13_p04_03_v2.png'
fix=ZONE/'native/r03_c13_cross_terrace_repair.png'
a=read(old.with_suffix('.png.generation.json'))['nativeWorldBox']
b=read(fix.with_suffix('.png.generation.json'))['nativeWorldBox']
box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
im=Image.open(old).convert('RGB')
crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]]
at=[box[0]-a[0],box[1]-a[1]]
im.paste(Image.open(fix).crop(crop),tuple(at))
# This is a guide only: cropped correct terrace reaches the frame edge at y1139.
p=ZONE/'guides'/f'{ident}.anchored-layout-only.png'; assert not p.exists(); im.save(p)
der={'operation':'exact registered native composite for edit guide only, no scaling','base':{'file':old.as_posix(),'sha256':sha(old)},'correctedTerraceSource':{'file':fix.as_posix(),'sha256':sha(fix),'sourceCrop':crop,'targetPaste':at},'patch':patch(ident),'finalArt':False}
write(p.with_suffix('.png.derivation.json'),der)
refs=[{'file':p.as_posix(),'sha256':sha(p),'role':'native edit target: corrected terrace on left; continue it across remaining lower region','derivationRecord':p.with_suffix('.png.derivation.json').as_posix()},{'file':fix.as_posix(),'sha256':sha(fix),'role':'correct continuous single terrace source at registered adjacent world coordinates'},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
q=read(ZONE/'qa/r03_c13_cross_terrace_repair.overlay.json');q.update(review='failed_right_and_bottom_attachment',notes='Interior is correct but perimeter source geometry jumps. Not selected. Correct interior used as guide for replacement whole p04_03.');write(ZONE/'qa/r03_c13_cross_terrace_repair.overlay.json',q)
r=read(fix.with_suffix('.png.generation.json'));r.update(status='guide_only_not_selected',internalSeams='failed_perimeters',notes='Native correct terrace guide for whole adjoining core regeneration');write(fix.with_suffix('.png.generation.json'),r)
print(json.dumps(refs))

