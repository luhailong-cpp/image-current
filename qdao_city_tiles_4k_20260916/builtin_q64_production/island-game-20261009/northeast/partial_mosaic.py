from native_work import *
ids=[['r03_c12_p01_01','r03_c12_p01_02_v2','r03_c12_p01_03','r03_c12_p01_04'],['r03_c12_p02_01_v2','r03_c12_p02_02_v2','r03_c12_p02_03','r03_c12_p02_04_v2']]
out=Image.new('RGB',(4096,2048)); sources=[]
for row,line in enumerate(ids):
    for col,ident in enumerate(line):
        p=ZONE/'native'/f'{ident}.png'; im=Image.open(p); assert im.size==(1254,1254); out.paste(im.crop((115,115,1139,1139)),(col*1024,row*1024)); sources.append({'file':p.as_posix(),'sha256':sha(p),'coreCrop':[115,115,1139,1139],'paste':[col*1024,row*1024]})
out.save(ZONE/'qa/r03_c12-upper-half-native.png')
out.resize((1536,768),Image.Resampling.LANCZOS).save(ZONE/'qa/r03_c12-upper-half-preview.png')
write(ZONE/'qa/r03_c12-upper-half.json',{'status':'partial_work_in_progress_not_4k_tile','nativeCoverage':[4096,2048],'sources':sources,'operation':'exact native core concatenation, no feathering or resizing for native mosaic; preview downsample only','unreviewed':['external tile edges','lower half missing']})
