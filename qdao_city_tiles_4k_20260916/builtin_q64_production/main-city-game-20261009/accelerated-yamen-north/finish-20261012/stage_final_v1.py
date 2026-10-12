import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'staged-final-v2';O.mkdir(exist_ok=True)
bases={'r03_c04':'424e41dd0ce0','r03_c05':'945fa7bcbb42','r04_c04':'71cabb17b21f','r04_c05':'0e9a0c64dd52'}
basefiles={t:ROOT/t/'candidate'/f'{t}-pipeline-fixed-native-contexts-{sha}.png' for t,sha in bases.items()}
original={t:np.array(Image.open(f).convert('RGB')) for t,f in basefiles.items()}
arr={t:a.copy() for t,a in original.items()};mask={t:np.zeros((4096,4096),bool) for t in bases};records=[]
def apply(tile,box,derived,support,manifest):
 l,t,r,b=box;d=np.array(Image.open(derived).convert('RGB'));m=np.array(Image.open(support).convert('L'))>0
 assert d.shape[:2]==m.shape==(b-t,r-l)
 arr[tile][t:b,l:r][m]=d[m];mask[tile][t:b,l:r]|=m
 records.append({'tile':tile,'tileBox':box,'derived':p.reference(derived,'already composited native pixels'),'support':p.reference(support,'native support'),'manifest':{'file':str(manifest),'sha256':p.sha(manifest)},'operation':'Copy only support-positive pixels at identical coordinates. No additional alpha.'})
for tile in ('r03_c04','r03_c05'):
 apply(tile,[0,0,4096,4096],H/'d1-merged-v2'/f'{tile}-trial.png',H/'d1-merged-v2'/f'{tile}-support.png',H/'derive_d1_v2.py')
hf=p.read(ROOT/'r03_c04/finish-20261012-left-roof/handoff.json')
apply('r03_c04',hf['contextTileBox'],Path(hf['derived']),Path(hf['support']),Path(hf['manifest']))
L=H/'lower-merged-v3';M=H/'micro-derived-v2'
apply('r03_c05',[1695,2380,4096,3634],L/'d4-derived.png',L/'d4-support.png',L/'d4-derivation.json')
apply('r03_c05',[2280,2380,3534,3634],M/'d4-color-splice-v1-derived.png',M/'d4-color-splice-v1-alpha.png',M/'d4-color-splice-v1-derivation.json')
apply('r03_c05',[400,2550,1654,3804],L/'d5-derived.png',L/'d5-alpha.png',L/'d5-derivation.json')
for tag,y in [('e1-west-v1',1740),('e2-west-v1',2842)]:
 src=H/tag;alpha=np.array(Image.open(H/'lower-merged-v1'/(tag+'-alpha.png')).convert('L'))
 gen=np.array(Image.open(src/'raw-native.png').convert('RGB'))
 before=np.concatenate([arr['r03_c04'][y:y+1254,3469:],arr['r03_c05'][y:y+1254,:627]],axis=1)
 derived=((before.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
 d=O/tag;d.mkdir(exist_ok=True)
 p.save_png(d/'current-base-native.png',Image.fromarray(before));p.save_png(d/'derived-native.png',Image.fromarray(derived));p.save_png(d/'alpha.png',Image.fromarray(alpha))
 rec={'base':p.reference(d/'current-base-native.png','actual prior-stage native neighboring material'),'generated':p.reference(src/'raw-native.png','builtin original'),'alpha':p.reference(d/'alpha.png','recorded material alpha'),'worldBox':[15757,8192+y,17011,8192+y+1254],'formula':'(actual-current-base*(255-alpha)+generated*alpha+127)//255','resampled':False,'spatialBlur':False};p.put_json(d/'derivation.json',rec)
 for tile,crop,box in [('r03_c04',[0,0,627,1254],[3469,y,4096,y+1254]),('r03_c05',[627,0,1254,1254],[0,y,627,y+1254])]:
  df=d/(tile+'-derived.png');sf=d/(tile+'-support.png');p.save_png(df,Image.fromarray(derived).crop(tuple(crop)));p.save_png(sf,Image.fromarray(alpha).crop(tuple(crop)))
  apply(tile,box,df,sf,d/'derivation.json')
 p.save_png(d/'qa-top-native.png',Image.fromarray(derived).crop((430,0,850,250)))
 p.save_png(d/'qa-middle-native.png',Image.fromarray(derived).crop((430,350,850,820)))
 p.save_png(d/'qa-bottom-native.png',Image.fromarray(derived).crop((430,950,850,1254)))
rf=p.read(ROOT/'r04_c04/finish-20261012-rail-facet/handoff.json')
# Named output is the explicit final v2 handoff.
apply('r04_c04',[300,2400,1554,3654],ROOT/'r04_c04/finish-20261012-rail-facet/derived-context-native-v2.png',ROOT/'r04_c04/finish-20261012-rail-facet/source-support-v2.png',ROOT/'r04_c04/finish-20261012-rail-facet/derivation-v2.json')
for tag in ['c05-wood-v1','c05-floor-v1','c05-plinth-v1','c05-green-band-v1']:
 prep=p.read(H/tag/'preparation.json');apply('r04_c05',prep['tileBox'],M/(tag+'-derived.png'),M/(tag+'-alpha.png'),M/(tag+'-derivation.json'))
summary={'schemaVersion':1,'createdAt':p.now(),'operationsInOrder':records,'baseCandidates':{t:p.reference(f,'previous adopted candidate') for t,f in basefiles.items()},'method':'Recorded material alpha of builtin generated pixels, and coordinate-identical native copies only','resampled':False,'spatialBlur':False,'formalAccepted':False,'sourceOverlapRecipe':{'file':str(H/'derive_lower_v2.py'),'sha256':p.sha(H/'derive_lower_v2.py'),'notes':'D4 source overlap is 12px smoothstep around minimum-error path. Actual source2 weights in lower-merged-v3/d4-source2-overlap-weight.png. Return alpha top540..570,bottom748..780.'}}
p.put_json(O/'staging-manifest.json',summary)
for tile in bases:
 assert np.array_equal(arr[tile][~mask[tile]],original[tile][~mask[tile]])
 p.save_png(O/(tile+'-staged.png'),Image.fromarray(arr[tile]));p.save_png(O/(tile+'-support.png'),Image.fromarray(mask[tile].astype('uint8')*255))
 folder=O/tile;folder.mkdir(exist_ok=True);contexts=[]
 for row,top in enumerate([0,1024,2048,2842],1):
  for col,left in enumerate([0,1024,2048,2842],1):
   box=[left,top,left+1254,top+1254];sub=mask[tile][top:top+1254,left:left+1254]
   if not sub.any():continue
   df=folder/f'context-{row}-{col}.png';sf=folder/f'support-{row}-{col}.png'
   p.save_png(df,Image.fromarray(arr[tile]).crop(tuple(box)));p.save_png(sf,Image.fromarray(sub.astype('uint8')*255))
   contexts.append({'tileBox':box,'derivedFile':str(df),'supportFile':str(sf),'manifest':str(O/'staging-manifest.json')})
 spec={'tile':tile,'outputDirectory':'finish-20261012-integrated','baseCandidate':str(basefiles[tile]),'contexts':contexts}
 p.put_json(O/(tile+'-integration-spec.json'),spec)
 print(tile,'contexts',len(contexts),'changed',int(np.any(arr[tile]!=original[tile],axis=2).sum()))

