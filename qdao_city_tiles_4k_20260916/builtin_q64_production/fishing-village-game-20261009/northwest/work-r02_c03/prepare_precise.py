from production import *
from PIL import ImageDraw
specs=[
('r02_c03_paving_precise_a_v02','r02_c03_paving_join_a_v01',[[160,470,445,735],[525,450,795,720],[895,450,1190,760]]),
('r02_c03_paving_precise_b_v02','r02_c03_paving_join_b_v01',[[320,420,785,770]]),
('r02_c03_paving_precise_c_v02','r02_c03_paving_join_c_v01',[[115,440,435,735]]),
('r02_c03_paving_precise_d_v02','r02_c03_paving_join_d_v01',[[570,430,810,690],[990,530,1190,800]])]
for n,old,boxes in specs:
 im=Image.open(W/'guides'/(old+'.target.png'));p=W/'guides'/(n+'.target.png');im.save(p);info=read(W/'guides'/(old+'.target.png.derivation.json'));write(str(p)+'.derivation.json',{**info,'file':str(p),'sha256':sha(p)})
 mask=Image.new('RGB',(1254,1254),'black');dr=ImageDraw.Draw(mask)
 for b in boxes:dr.rectangle(b,fill='white')
 mp=W/'guides'/(n+'.allowed-mask.png');mask.save(mp);write(str(mp)+'.json',{'role':'edit-location instruction only, never final art pixels','rectangles':boxes,'globalNativeBox':info['globalNativeBox']})

