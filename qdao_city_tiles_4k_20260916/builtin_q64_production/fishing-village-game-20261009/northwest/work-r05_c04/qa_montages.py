from workflow import *
Q=W/'final-v1/qa';J=Q/'montages';J.mkdir(exist_ok=True)
for r in range(1,5):
 ims=[Image.open(Q/f'v{k}-{r}.100pct.png') for k in (1,2,3)];out=Image.new('RGB',(1200,1024))
 for k,im in enumerate(ims):out.paste(im,(k*400,0))
 out.save(J/f'vertical-row-{r}.native.png')
for c in range(1,5):
 out=Image.new('RGB',(1024,1200))
 for k in (1,2,3):out.paste(Image.open(Q/f'h{k}-{c}.100pct.png'),(0,(k-1)*400))
 out.save(J/f'horizontal-col-{c}.native.png')
for y in (1024,2048,3072):
 out=Image.new('RGB',(1560,520))
 for k,x in enumerate((1024,2048,3072)):out.paste(Image.open(Q/f'junction-{x}-{y}.100pct.png'),(k*520,0))
 out.save(J/f'junction-row-{y}.native.png')
for s in (1,3):
 out=Image.new('RGB',(1024,800));out.paste(Image.open(Q/f'north-{s}.100pct.png'),(0,0));out.paste(Image.open(Q/f'north-{s+1}.100pct.png'),(0,400));out.save(J/f'north-{s}-{s+1}.native.png')
 out=Image.new('RGB',(800,1024));out.paste(Image.open(Q/f'west-{s}.100pct.png'),(0,0));out.paste(Image.open(Q/f'west-{s+1}.100pct.png'),(400,0));out.save(J/f'west-{s}-{s+1}.native.png')
