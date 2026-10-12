from worker import *
tile,name,x,y=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]);t=B/tile;d=t/'repairs'/name;d.mkdir(parents=True,exist_ok=True)
source=t/'qa'/'core-assembly-v01.png';im=Image.open(source);p=d/'input.png';assert not p.exists();im.crop((x,y,x+1254,y+1254)).save(p)
write(d/'coordinates.json',{'source':str(source),'sourceSha256':sha(source),'crop':[x,y,x+1254,y+1254],'input':str(p),'size':[1254,1254],'nativeRepairPending':True})
print(p)
