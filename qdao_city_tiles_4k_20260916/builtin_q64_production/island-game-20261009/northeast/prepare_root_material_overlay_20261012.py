from native_work import *
ident='r03_c10_cross_native_material_repair'
source=ZONE/'tiles/r03_c10-native-v1-20261012.png'
native=[39309,9101,40563,10355];core=[39424,9216,40448,10240]
box=[native[0]-36864,native[1]-8192,native[2]-36864,native[3]-8192]
guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists()
im=Image.open(source);im.crop(tuple(box)).save(guide)
write(guide.with_suffix('.png.derivation.json'),{'operation':'mechanical exact native1254 artwork crop for local builtin edit; no resampling','source':source.as_posix(),'sourceSha256':sha(source),'sourceCrop':box,'nativeWorldBox':native,'coreWorldBox':core,'coreCrop':[115,115,1139,1139],'finalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'edit target: exact native artwork crop spanning the residual vertical material scar; no resize'},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
p=ZONE/'native/r03_c10_p02_03_v3.png.generation.json';r=read(p);r.update(status='unselected_residual_material_boundary',pendingIssues=['Residual stone-face boundary near oldx1024; centered native overlay repair selected instead of repeated full-core redraw.']);write(p,r)
print(json.dumps({'id':ident,'guide':guide.as_posix(),'refs':[r['file'] for r in refs],'nativeWorldBox':native,'coreWorldBox':core,'tileLocalPaste':[2560,1024]}))
