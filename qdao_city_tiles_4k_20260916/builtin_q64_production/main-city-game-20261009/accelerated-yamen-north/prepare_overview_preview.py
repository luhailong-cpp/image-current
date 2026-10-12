from PIL import Image
import pipeline as p
d=p.read(p.ROOT/'qa-final-fourway-v1/manifest.json');im=Image.new('RGB',(2048,2048))
for s in d['sources']:
 f=s['file'];assert p.sha(f)==s['sha256'];tile=s['tile'];r=int(tile[1:3]);c=int(tile[5:7]);a=Image.open(f).convert('RGB');im.paste(a.resize((1024,1024),Image.Resampling.LANCZOS),((c-4)*1024,(r-3)*1024))
info=p.save_png(p.ROOT/'qa-final-fourway-v1/overview-preview-2048.png',im)
p.put_json(p.ROOT/'qa-final-fourway-v1/overview-preview.json',{'preview':info,'sources':d['sources'],'isDownscaledPreviewOnly':True,'formalAccepted':False})
