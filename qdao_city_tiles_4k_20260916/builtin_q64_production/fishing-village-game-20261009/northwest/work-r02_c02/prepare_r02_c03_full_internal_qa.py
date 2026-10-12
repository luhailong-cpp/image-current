from production import *
O=E;Q=O/'qa-full-internal';Q.mkdir(exist_ok=True);p=O/'r02_c03.candidate.png';im=Image.open(p);manifest={'candidate':{'file':str(p),'sha256':sha(p)},'scale':1,'contactSheetIsExactNativeCropPasteOnly':True,'verticalSeams':[],'horizontalSeams':[],'junctions':[],'coreInheritance':[],'status':'awaiting-new-seam-junction-visual-review'}
for r in range(4):
 sheet=Image.new('RGB',(600,1024))
 for c in range(1,4):
  b=[c*1024-100,r*1024,c*1024+100,(r+1)*1024];piece=im.crop(b);z=Q/f'v-{r+1}-{c}.png';piece.save(z);sheet.paste(piece,((c-1)*200,0));manifest['verticalSeams'].append({'file':str(z),'sha256':sha(z),'cropBox':b,'contactSheetCell':[(c-1)*200,0,c*200,1024]})
 sheet.save(Q/f'vertical-row-{r+1}.png')
for r in range(1,4):
 sheet=Image.new('RGB',(1024,800))
 for c in range(4):
  b=[c*1024,r*1024-100,(c+1)*1024,r*1024+100];piece=im.crop(b);z=Q/f'h-{r}-{c+1}.png';piece.save(z);sheet.paste(piece,(0,c*200));manifest['horizontalSeams'].append({'file':str(z),'sha256':sha(z),'cropBox':b,'contactSheetCell':[0,c*200,1024,(c+1)*200]})
 sheet.save(Q/f'horizontal-row-{r}.png')
sheet=Image.new('RGB',(768,768))
for r in range(1,4):
 for c in range(1,4):
  b=[c*1024-128,r*1024-128,c*1024+128,r*1024+128];piece=im.crop(b);z=Q/f'junction-{r}-{c}.png';piece.save(z);sheet.paste(piece,((c-1)*256,(r-1)*256));manifest['junctions'].append({'file':str(z),'sha256':sha(z),'cropBox':b,'contactSheetCell':[(c-1)*256,(r-1)*256,c*256,r*256]})
sheet.save(Q/'junctions-3x3.png');before=np.asarray(Image.open(E.parent/'qa-before/core-1-1.png'))
changes=read(O/'qa.json')['changedCores']
for r in range(1,5):
 for c in range(1,5):
  final=O/'qa'/f'core-{r}-{c}.png';prior=E.parent/'qa-before'/f'core-{r}-{c}.png';same=np.array_equal(np.asarray(Image.open(final)),np.asarray(Image.open(prior)))
  assert same==([r,c] not in changes);manifest['coreInheritance'].append({'core':[r,c],'file':str(final),'sha256':sha(final),'reviewBasis':'reviewed final changed-core crop' if not same else 'previously viewed qa-before crop, exact unchanged native pixels','priorFile':str(prior),'priorSha256':sha(prior),'inheritedPixelMismatches':0 if same else None})
write(Q/'coverage-prepared.json',manifest);print(json.dumps({'output':str(Q),'cores':16,'verticalSeams':12,'horizontalSeams':12,'junctions':9,'newContactSheets':8}))
