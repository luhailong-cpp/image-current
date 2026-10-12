from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'check_G3_v1.py').read_text(encoding='utf-8')
s=s.replace("STEM='G3-bottom-conditioned-v1'","STEM='G3-bottom-conditioned-v2'")
s=s.replace("BOX=[250,597,970,725];WORLD=[36310,47189,37030,47317]",
            "BOX=[300,473,971,766];WORLD=[36360,47065,37031,47358]\nADOPTMASK=Image.open(D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png').convert('L')")
s=s.replace('exec-c3f89e46-b371-4ae2-bbae-b496e4708291.png','exec-9b142e68-6cc5-4150-a0e5-c2a8ed24091c.png')
s=s.replace("(D/(STEM+'-guide-provenance.json'))","(D/'G3-bottom-conditioned-v1-guide-provenance.json')")
s=s.replace("bounded=guide.copy();bounded.paste(im.crop(BOX),BOX[:2])",
            "bounded=guide.copy();bounded.paste(im.convert('RGB'),(0,0),ADOPTMASK)")
s=s.replace("mask=np.zeros((1254,1254),bool);mask[BOX[1]:BOX[3],BOX[0]:BOX[2]]=True",
            "mask=np.asarray(ADOPTMASK)>0")
s=s.replace("art.paste(im.crop(sourcebox),dest[:2]);array=np.asarray(art)",
            "localmask=ADOPTMASK.crop(sourcebox)\n    art.paste(im.crop(sourcebox),dest[:2],localmask);array=np.asarray(art)")
s=s.replace("pmask[dest[1]:dest[3],dest[0]:dest[2]]=True",
            "pmask[dest[1]:dest[3],dest[0]:dest[2]]=np.asarray(localmask)>0")
s=s.replace("{'left':[186,533,314,789],'top':[250,533,970,661],\n                 'right':[906,533,1034,789],'bottom':[250,661,970,789],\n                 'G3':[257,427,1119,827],'band':[186,533,1034,789]}",
            "{'left':[236,473,364,830],'top':[300,409,971,666],\n                 'right':[906,409,1035,830],'bottom':[300,702,971,830],\n                 'G3':[257,427,1119,827],'band':[236,409,1035,830]}")
s=s.replace("'outsideAdoptionChangedPixels':0,",
            "'adoptMask':str(D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png'),'adoptMaskSha256':sha(D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png'),'outsideAdoptionChangedPixels':0,")
out=D/'check_G3_v2.py';assert not out.exists();out.write_text(s,encoding='utf-8')
print(str(out))
