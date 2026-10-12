from production import *
im=Image.open(W/'base-v1/full-pair.png')
specs=[
('r02_c03_rail_continuity_v01',[10800,5190,12054,6444]),
('r02_c03_paving_join_a_v01',[8077,4600,9331,5854]),
('r02_c03_paving_join_b_v01',[8077,5590,9331,6844]),
('r02_c03_paving_join_c_v01',[9101,5590,10355,6844]),
('r02_c03_paving_join_d_v01',[10125,5590,11379,6844]),
('r02_c03_blue_ridge_v01',[8077,6650,9331,7904])]
for n,b in specs:
 p=W/'guides'/(n+'.target.png');im.crop((b[0]-8077,b[1]-3981,b[2]-8077,b[3]-3981)).save(p);write(str(p)+'.derivation.json',{'file':str(p),'sha256':sha(p),'source':str(W/'base-v1/full-pair.png'),'sourceSha256':sha(W/'base-v1/full-pair.png'),'globalNativeBox':b,'resampled':False})

