from worker import *
tile,name,src=sys.argv[1:];d=B/tile/'repairs'/name;p=d/'native-v01.png';assert not p.exists();shutil.copyfile(src,p)
im=Image.open(p);assert im.size==(1254,1254)
rec=read(d/'coordinates.json');rec.update(path=str(p),originalOutput=src,sha256=sha(p),actualDimensions=list(im.size),tool='image_gen.imagegen',actualModel=None,modelEvidence='not returned',resized=False,savedAt=now(),verdict='local seam improved; integration perimeter pending')
write(d/'native-v01.json',rec);print(json.dumps(rec))
