from production import *
from PIL import ImageDraw
specs=[
('r02_c03_paving_connector_a_v03','r02_c03_paving_precise_a_v02',[[[380,595],[498,576]]],[8077,4600,9331,5854]),
('r02_c03_paving_connector_b_v03','r02_c03_paving_precise_b_v02',[[[445,557],[465,577]],[[648,588],[669,608]]],[8077,5590,9331,6844])]
for n,old,lines,b in specs:
 im=Image.open(W/'native'/(old+'.png'));p=W/'guides'/(n+'.target.png');im.save(p);guide=im.copy();dr=ImageDraw.Draw(guide)
 for line in lines:dr.line([tuple(q) for q in line],fill=(255,0,255),width=7)
 gp=W/'guides'/(n+'.connector-guide.png');guide.save(gp);write(str(gp)+'.derivation.json',{'file':str(gp),'sha256':sha(gp),'source':str(W/'native'/(old+'.png')),'sourceSha256':sha(W/'native'/(old+'.png')),'globalNativeBox':b,'guideOnly':True,'magentaLines':lines})

