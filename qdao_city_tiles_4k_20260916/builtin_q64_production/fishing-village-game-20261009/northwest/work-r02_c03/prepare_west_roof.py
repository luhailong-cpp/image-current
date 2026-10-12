from production import *
D=W/'guides';n='r02_r03_roof_west_bridge_v01';b=[7565,8077,8819,9331]
m=read(B/'work-r03_c02/west-final/final-joint.assembly.json');s=m['sources']['19'];im=Image.open(s['file']).copy();assert s['globalNativeBox']==b
current=Image.open(W/'combined-v1/full-pair.png');x0=8192;im.paste(current.crop((x0-8077,8077-3981,8819-8077,9331-3981)),(x0-b[0],0))
p=D/(n+'.target.png');im.save(p);write(str(p)+'.derivation.json',{'file':str(p),'sha256':sha(p),'globalNativeBox':b,'actualSourceLeft':s,'actualRight':str(W/'combined-v1/full-pair.png'),'actualRightSha256':sha(W/'combined-v1/full-pair.png'),'rightBeginsX':8192,'resampled':False})

