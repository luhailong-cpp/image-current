from native_work import *
a=ZONE/'tiles/r03_c13.png';b=ZONE/'qa/r03_c14-existing-coverage-native.png';ad=read(a.with_suffix('.png.derivation.json'));bd=read(b.with_suffix('.png.derivation.json'));assert sha(a)==ad['sha256'] and sha(b)==bd['sha256']
ai=Image.open(a).convert('RGB');bi=Image.open(b).convert('RGBA');assert bi.getchannel('A').crop((0,0,256,4096)).getextrema()==(255,255)
border=Image.new('RGB',(512,4096));border.paste(ai.crop((3840,0,4096,4096)),(0,0));border.paste(bi.crop((0,0,256,4096)).convert('RGB'),(256,0))
prefix='r03_c13__r03_c14.existing-border';border.save(ZONE/'qa'/f'{prefix}.png');parts=[]
for i in range(4):
 p=ZONE/'qa'/f'{prefix}.segment-{i+1}.png';border.crop((0,i*1024,512,(i+1)*1024)).save(p);parts.append(p.as_posix())
write(ZONE/'qa'/f'{prefix}.json',{'a':a.as_posix(),'b':b.as_posix(),'aSha256':sha(a),'bSha256':sha(b),'operation':'exact256px existing-art shared edge crops, no resampling or blending','rightTileIncomplete':True,'edgeCoveragePixels':4096,'uncoveredEdgePixels':0,'segments':parts,'status':'pending_visual_review','formalAccepted':False})
print(json.dumps({'prefix':prefix,'edgePixels':4096}))

