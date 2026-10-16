from native_work import *
ident='r03_c09_cross_p0102_right_repair'
a='r03_c09_p01_02_v2';b='r03_c09_p01_03'
native=[34189,8077,35443,9331];core=[34304,8192,35328,9216]
im=Image.new('RGB',(1254,1254));sources=[]
for name,world in [(a,[34189,8077,34816,9331]),(b,[34816,8077,35443,9331])]:
 f=ZONE/'native'/f'{name}.png';box=patch(name)['nativeWorldBox'];crop=[world[0]-box[0],world[1]-box[1],world[2]-box[0],world[3]-box[1]];at=[world[0]-native[0],world[1]-native[1]]
 im.paste(Image.open(f).crop(crop),tuple(at));sources.append({'file':f.as_posix(),'sha256':sha(f),'crop':crop,'paste':at})
guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists();im.save(guide)
write(guide.with_suffix('.png.derivation.json'),{'operation':'exact native piece assembly spanning failed grout join; no resize or blend','sources':sources,'nativeWorldBox':native,'coreWorldBox':core,'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1536,0],'finalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'edit target: exact native composite, failed join through vertical center; preserve external contour anchors'},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
p=ZONE/'qa/r03_c09_p01_02_v2__r03_c09_p01_03.json';d=read(p);d.update(status='failed_geometry_continuity',reviewer='root',reviewedAtUtc=now(),finding='First repair did not resolve slab contour step. Centered native joint repair is second attempt.');write(p,d)
print(json.dumps({'id':ident,'references':[e['file'] for e in refs]}))

