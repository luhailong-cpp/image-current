from native_work import *
tid='r05_c14'; ident='r05_c14_cross_floor_tone_repair'; x,y=0,2700
target=ZONE/'tiles/r05_c14.png'; left=ZONE/'tiles/r05_c13.png'
im=Image.new('RGB',(1254,1254))
im.paste(Image.open(left).crop((3981,y-115,4096,y+1139)),(0,0))
im.paste(Image.open(target).crop((0,y-115,1139,y+1139)),(115,0))
dest=ZONE/'guides'/f'{ident}.png'; assert not dest.exists(); im.save(dest)
sources=[{'file':target.as_posix(),'sha256':sha(target),'crop':[0,y-115,1139,y+1139],'paste':[115,0]},{'file':left.as_posix(),'sha256':sha(left),'crop':[3981,y-115,4096,y+1139],'paste':[0,0]}]
write(dest.with_suffix('.png.derivation.json'),{'operation':'exact unscaled assembled native tile crop, left context only from neighbor, no image drawing','sources':sources,'nativeWorldBox':[53248-115,16384+y-115,53248+1139,16384+y+1139],'coreWorldBox':[53248,16384+y,53248+1024,16384+y+1024],'coreCrop':[115,115,1139,1139],'tileLocalPaste':[x,y],'finalArt':False})
write(ZONE/'prompts'/f'{ident}.inputs.json',[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target, actual assembled1254 native crop across cupboard foot and floor; farleft115px external neighbor context preserve','sources':sources},*current_references()])
print(dest.as_posix())

