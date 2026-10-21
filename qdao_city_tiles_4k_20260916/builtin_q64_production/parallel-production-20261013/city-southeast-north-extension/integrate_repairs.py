from worker import *
for tile,name in [('r12_c13','east-upper-seam-v01'),('r12_c14','middle-wall-seam-v01')]:
    t=B/tile; d=t/'repairs'/name
    rec=json.loads((d/'coordinates.json').read_text(encoding='utf-8-sig'))
    src=t/'qa'/'core-assembly-v01.png'; rp=d/'native-v01.png'
    im=Image.open(src).convert('RGB'); repair=Image.open(rp).convert('RGB')
    x,y,x2,y2=rec['crop']; out=t/'qa'/'repair-candidate-v02.png'; assert not out.exists()
    im.paste(repair.crop((115,115,1139,1139)),(x+115,y+115)); im.save(out)
    write(t/'qa'/'repair-candidate-v02.json',{'source':str(src),'sourceSha256':sha(src),'repair':str(rp),'repairSha256':sha(rp),'sourceCrop':[115,115,1139,1139],'targetBox':[x+115,y+115,x+1139,y+1139],'path':str(out),'sha256':sha(out),'size':[4096,4096],'resized':False,'blended':False,'accepted':False,'status':'native replacement candidate; other seams and replacement perimeter pending'})
    print(out)
