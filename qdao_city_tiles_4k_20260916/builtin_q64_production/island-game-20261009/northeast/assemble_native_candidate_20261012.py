from native_work import *
import re,sys
import numpy as np
tid,name=sys.argv[1:3]
selection=read(ZONE/f'selection-{tid}.json')
assert all(all(row) for row in selection['cores']), 'Requires all16 selected cores'
row,col=map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',tid).groups())
ox,oy=(col-1)*4096,(row-1)*4096
dest=ZONE/'tiles'/f'{name}.png'
preview=ZONE/'qa'/f'{name}-preview.png'
qa=ZONE/'qa'/f'{name}-final'
assert not dest.exists() and not preview.exists() and not qa.exists(), 'Preserve all existing PNG and QA'
out=Image.new('RGB',(4096,4096));coverage=np.zeros((4096,4096),dtype='uint8');sources=[]
for r,line in enumerate(selection['cores']):
 for c,ident in enumerate(line):
  p=ZONE/'native'/f'{ident}.png';rec=read(p.with_suffix('.png.generation.json'));im=Image.open(p)
  assert im.size==(1254,1254) and sha(p)==rec['sha256']
  assert rec['coreWorldBox']==[ox+c*1024,oy+r*1024,ox+(c+1)*1024,oy+(r+1)*1024]
  assert rec['coreCrop']==[115,115,1139,1139]
  core=im.crop(tuple(rec['coreCrop']));out.paste(core,(c*1024,r*1024));coverage[r*1024:(r+1)*1024,c*1024:(c+1)*1024]+=1
  sources.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':rec['coreCrop'],'tileLocalPaste':[c*1024,r*1024],'nativeSize':list(im.size)})
overlays=[]
for ident in selection.get('overlays',[]):
 q=read(ZONE/'qa'/f'{ident}.overlay.json')
 assert q['review'].startswith('passed_') and sha(q['source'])==q['sha256']
 out.paste(Image.open(q['source']).crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste']));overlays.append(q)
assert (coverage==1).all()
qa.mkdir();out.save(dest);out.resize((1536,1536),Image.Resampling.LANCZOS).save(preview)
for r in range(4):
 for c in range(4):out.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(qa/f'core-{r+1}-{c+1}-100pct.png')
for i in range(1,4):
 for j in range(4):
  out.crop((i*1024-128,j*1024,i*1024+128,(j+1)*1024)).save(qa/f'vertical-{i}-segment-{j+1}-100pct.png')
  out.crop((j*1024,i*1024-128,(j+1)*1024,i*1024+128)).save(qa/f'horizontal-{i}-segment-{j+1}-100pct.png')
for r in range(1,4):
 for c in range(1,4):out.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(qa/f'cross-{r}-{c}-100pct.png')
record={'tileId':tid,'file':dest.as_posix(),'sha256':sha(dest),'size':[4096,4096],'worldBox':[ox,oy,ox+4096,oy+4096],'operation':'16 exact native1024 core crops plus recorded repair overlays, no resampling or feathering','sources':sources,'requiredOverlays':overlays,'baseCoverageMin':1,'baseCoverageMax':1,'uncoveredPixels':0,'finalArtUpscaled':False,'status':'complete_native_coverage_pending_whole_tile_QA','internalReview':'pending','externalSeams':'pending adjacent4k tiles','formalAccepted':False,'actualModel':None,'actualQuality':None,'generatedAtUtc':now(),'preview':preview.as_posix(),'inspectionCrops':qa.as_posix()}
write(dest.with_suffix('.png.derivation.json'),record)
selection.update(candidatePath=dest.as_posix(),derivationPath=dest.with_suffix('.png.derivation.json').as_posix(),updatedAtUtc=now());write(ZONE/f'selection-{tid}.json',selection)
print(json.dumps({'candidatePath':dest.as_posix(),'sha256':record['sha256'],'preview':preview.as_posix(),'inspectionCrops':qa.as_posix(),'uncoveredPixels':0}))
