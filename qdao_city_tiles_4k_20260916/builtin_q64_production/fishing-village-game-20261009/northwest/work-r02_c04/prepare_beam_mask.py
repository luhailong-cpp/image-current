from PIL import Image,ImageDraw
from production import W
a=Image.new('RGB',(1254,1254),'black');ImageDraw.Draw(a).polygon([(268,200),(1110,510),(1137,1180),(270,970)],fill='white');a.save(W/'guides/rail-span-right-v04.mask-guide.png')

