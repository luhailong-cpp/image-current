from worker import *
tile=sys.argv[1];t=B/tile;m=read(t/'selected.json');assert len(m)==16
out=t/'qa'/'core-assembly-v01.png';assert not out.exists()
im=Image.new('RGB',(4096,4096))
for p,rec in m.items():
 assert sha(rec['path'])==rec['sha256'];source=Image.open(rec['path']);assert source.size==(1254,1254)
 a,b=int(p[1:3]),int(p[4:6]);im.paste(source.crop((115,115,1139,1139)),((b-1)*1024,(a-1)*1024))
im.save(out)
for a in range(1,4):
 for b in range(4):
  im.crop((a*1024-128,b*1024,a*1024+128,(b+1)*1024)).save(t/'qa'/f'vertical-{a}-{b}.png')
  im.crop((b*1024,a*1024-128,(b+1)*1024,a*1024+128)).save(t/'qa'/f'horizontal-{a}-{b}.png')
write(t/'qa'/'assembly-v01.json',{'tile':tile,'path':str(out),'sha256':sha(out),'dimensions':[4096,4096],'sources':[{'patch':p,'path':r['path'],'sha256':r['sha256']} for p,r in m.items()],'assembly':'16 integer1024core crops placed at exact coordinates; no resize/blend','allPixelsNative':True,'internalQA':'pending','externalQA':'pending','formalAccepted':False})
print(out)
