from PIL import Image,ImageDraw
from production import W
im=Image.new('RGB',(1254,1254),'black');ImageDraw.Draw(im).polygon([(540,350),(1180,400),(1180,860),(510,870)],fill='white');im.save(W/'guides/paving-west-local-repair.mask-guide.png')

