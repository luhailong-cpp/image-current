from PIL import Image,ImageDraw
from production import W
p=W/'guides/paving-mid-local-repair.mask-guide.png';im=Image.new('RGB',(1254,1254),'black');ImageDraw.Draw(im).polygon([(90,460),(800,460),(1020,330),(1170,370),(1170,860),(90,870)],fill='white');im.save(p)
a=Image.open(W/'joint-stage/joint.context.png')
for n,b in [('foliage-left-v01',[12750,4700,14004,5954]),('foliage-right-upper-v01',[14650,4700,15904,5954]),('foliage-right-lower-v01',[14650,5750,15904,7004])]:a.crop((b[0]-12173,b[1]-3981,b[2]-12173,b[3]-3981)).save(W/'guides'/(n+'.target.png'))

