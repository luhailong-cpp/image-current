from worker import *
t=B/'r12_c13'; source=t/'qa'/'repair-candidate-v02.png'; im=Image.open(source).convert('RGB'); evidence=[]
for name in ['lower-parasol-seam-v01','lower-pillar-seam-v01']:
    d=t/'repairs'/name; rec=json.loads((d/'coordinates.json').read_text(encoding='utf-8-sig')); x,y,_,_=rec['crop']; p=d/'native-v01.png'; ri=Image.open(p).convert('RGB')
    im.paste(ri.crop((115,115,1139,1139)),(x+115,y+115)); evidence.append({'repair':str(p),'sha256':sha(p),'sourceCrop':[115,115,1139,1139],'target':[x+115,y+115,x+1139,y+1139]})
out=t/'qa'/'repair-candidate-v03.png'; assert not out.exists(); im.save(out)
write(t/'qa'/'repair-candidate-v03.json',{'path':str(out),'sha256':sha(out),'size':[4096,4096],'source':str(source),'sourceSha256':sha(source),'repairs':evidence,'resized':False,'accepted':False,'status':'candidate_needs_perimeter_review'})
print(out)
