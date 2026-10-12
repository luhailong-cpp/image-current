from workflow import *
q=ROOT/'qa/returned-batch-resume-20261013';q.mkdir(exist_ok=True)
specs=[('r14_c11_p14_v01','N','r13_c11_p44_v01'),('r14_c11_p14_v01','E','r14_c12_p11_v01'),('r14_c11_p34_v01','E','r14_c12_p31_v01'),('r14_c11_p34_v01','S','r14_c11_p44_v01'),('r14_c11_p42_v01','W','r14_c11_p41_v01'),('r08_c10_p13_v01','E','r08_c10_p14_v01'),('r08_c10_p24_v01','N','r08_c10_p14_v01'),('r08_c10_p24_v01','E','r08_c11_p21_v06'),('r13_c13_p24_v02','N','r13_c13_p14_v01')]
entries=[];hs=[];vs=[]
for pid,d,nid in specs:
    pf=ROOT/'native'/f'{pid}.png';nf=ROOT/'native'/f'{nid}.png';a=Image.open(pf).convert('RGB').crop((115,115,1139,1139));b=Image.open(nf).convert('RGB').crop((115,115,1139,1139))
    if d in ['N','S']:
        im=Image.new('RGB',(1024,512));upper,lower=(b,a) if d=='N' else (a,b);im.paste(upper.crop((0,768,1024,1024)),(0,0));im.paste(lower.crop((0,0,1024,256)),(0,256))
    else:
        im=Image.new('RGB',(512,1024));left,right=(b,a) if d=='W' else (a,b);im.paste(left.crop((768,0,1024,1024)),(0,0));im.paste(right.crop((0,0,256,1024)),(256,0))
    dest=q/f'{pid}-{d}.png';assert not dest.exists();im.save(dest)
    entry={'patch':pid,'neighbor':nid,'side':d,'file':str(dest),'sha256':sha(dest),'patchSha256':sha(pf),'neighborSha256':sha(nf),'status':'pending_visual_review'};entries.append(entry)
    (hs if d in ['N','S'] else vs).append(im)
for typ,items,w,h,cols in [('h',hs,1024,512,2),('v',vs,512,1024,3)]:
    for start in range(0,len(items),cols*2 if typ=='h' else cols):
        batch=items[start:start+(cols*2 if typ=='h' else cols)];sheet=Image.new('RGB',(w*min(cols,len(batch)),h*((len(batch)+cols-1)//cols)))
        for i,im in enumerate(batch):sheet.paste(im,((i%cols)*w,(i//cols)*h))
        sheet.save(q/f'contact-{typ}-{start+1}.png')
ids=list(dict.fromkeys(s[0] for s in specs));preview=Image.new('RGB',(1536,1024))
for i,pid in enumerate(ids):preview.paste(Image.open(ROOT/'native'/f'{pid}.png').convert('RGB').resize((512,512)),((i%3)*512,(i//3)*512))
preview.save(q/'native-layout-preview-only.png')
write(q/'manifest.json',{'createdAt':now(),'entries':entries,'nativePreviewOrder':ids,'previewNotFinalArt':True,'actualSeamsUseUnchangedCorePixels':True})
print(q)
