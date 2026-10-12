from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;P=O.parent
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def dump(f,v):Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(f):
 f=Path(f);v={'file':str(f),'sha256':sha(f)}
 if f.suffix=='.png':
  with Image.open(f) as im:v.update(width=im.width,height=im.height,mode=im.mode,format=im.format)
 return v
def rgb(f):return np.array(Image.open(f).convert('RGB'))
prep=read(O/'preparation.json');entries=[]
for i in [1,2,3]:
 r=read(O/f'roi{i}-receipt.json');raw=O/f'roi{i}-raw.png';host=Path(r['hostSourceFile']);params=Path(r['parametersFile']);args=read(params)
 assert raw.read_bytes()==host.read_bytes()
 r.update(raw=ref(raw),hostRaw=ref(host),parameters=ref(params),references=[ref(x) for x in args['referenced_image_paths']],
  rawHostBytesUnmodified=True,actualModel=None,actualQuality=None,contextTileBox=prep['contextTileBox'],contextWorldBox=prep['contextWorldBox'])
 dump(O/f'roi{i}-receipt.json',r)
 A=np.array(Image.open(O/f'roi{i}-alpha.png'));D=rgb(O/f'roi{i}-derived-context.png');B=rgb(O/f'stage{i-1}-native.png')
 assert np.array_equal(D[A==0],B[A==0])
 ys,xs=np.where(A>0);support=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 info={'schemaVersion':1,'kind':'native_multi_source_alpha_derivation','id':i,'tile':'r03_c04',
  'status':'LOCAL_PASS_ROOT_MAY_IMPORT' if i==3 else 'FAIL_DO_NOT_APPLY','formalAccepted':False,
  'contextTileBox':prep['contextTileBox'],'contextWorldBox':prep['contextWorldBox'],
  'generationEditWindow':prep['rois'][i-1]['roiBox'],'positiveSupportContextBox':support,
  'positiveSupportTileBox':[support[0]+453,support[1]+493,support[2]+453,support[3]+493],
  'baseTile':ref(prep['baseFile']),'baseContext':ref(O/f'stage{i-1}-native.png'),'raw':ref(raw),'receipt':ref(O/f'roi{i}-receipt.json'),
  'derivedFile':str(O/f'roi{i}-derived-context.png'),'derivedHash':sha(O/f'roi{i}-derived-context.png'),
  'alphaFile':str(O/f'roi{i}-alpha.png'),'alphaHash':sha(O/f'roi{i}-alpha.png'),
  'supportPositiveMaskFile':str(O/f'roi{i}-support-positive-mask.png'),'supportPositiveMaskHash':sha(O/f'roi{i}-support-positive-mask.png'),
  'nativePixels':[1254,1254],'width':1254,'height':1254,'alphaScale':255,
  'alphaQuantization':'floor(255*w+0.5)','smoothstep':'s(v,a,b)=t*t*(3-2*t), t=clip((v-a)/(b-a),0,1); pixel-center coordinates',
  'blendFormula':'(base*(255-alpha)+raw*alpha+127)//255 per RGB channel',
  'alphaFormula':('s(x,775,791)*(1-s(x,1079,1095))*s(y,510,526)*(1-s(y,664,680))' if i==3 else 'see compose_roi.py; ROI1 final rejected trial additionally uses roi1-adaptive-path.json and adapt_seam.py'),
  'verifiedOutsideSupportUnchanged':True,'resizedAfterGeneration':False,'finalArtUpscaled':False,'spatialBlur':False,
  'operation':'At identical world coordinates, copy already-composited derived pixels where support-positive-mask>0. Do not alpha-composite twice.',
  'visualVerdict':r['visualVerdict'],'qa':ref(O/f'roi{i}-qa-detail-native.png')}
 if i==3:info['applicationOrder']='Apply accepted roof-row-repair/right first, then this ROI3; omit ROI1 and ROI2 entirely.'
 dump(O/f'roi{i}-manifest.json',info);entries.append(info)

tile=rgb(prep['baseFile']);rd=rgb(P/'right/derived-context.png');rm=np.array(Image.open(P/'right/support-positive-mask.png'))>0
tile[493:1747,1433:2687]=np.where(rm[:,:,None],rd,tile[493:1747,1433:2687])
nd=rgb(O/'roi3-derived-context.png');nm=np.array(Image.open(O/'roi3-support-positive-mask.png'))>0
tile[493:1747,453:1707]=np.where(nm[:,:,None],nd,tile[493:1747,453:1707])
Image.fromarray(tile).save(O/'candidate-accepted-only-native.png')
Image.fromarray(tile[1000:1220,580:1290]).save(O/'qa-left-remaining-native.png')
Image.fromarray(tile[970:1220,1200:1580]).save(O/'qa-roi3-joined-native.png')
remaining=[
 {'id':'left-roof-junction1','tileBox':[583,1008,943,1218],'worldBox':[12871,9200,13231,9410],
  'status':'FAIL_REMAINS_ORIGINAL','type':'original triangular/jagged ceramic overlap and gutter discontinuity; ROI1 rejected because compositing introduced lower geometry mismatch'},
 {'id':'left-roof-junction2','tileBox':[903,1008,1278,1218],'worldBox':[13191,9200,13566,9410],
  'status':'FAIL_REMAINS_ORIGINAL_EXCEPT_ROI3_OVERLAP','type':'original wide triangular roof shoulders and gutter phase jump; ROI2 rejected because its lower boundary shifted. Accepted ROI3 improves the rightmost overlap beginning tile x1228.'}
]
handoff={'status':'ONE_NARROW_ROI_PASS_TWO_FAIL_CLOSED','generationRequests':3,'generationLimit':3,'noFurtherGeneration':True,
 'contextTileBox':prep['contextTileBox'],'contextWorldBox':prep['contextWorldBox'],
 'accepted':[{'id':3,'manifest':str(O/'roi3-manifest.json'),'derived':entries[2]['derivedFile'],
  'alpha':entries[2]['alphaFile'],'support':entries[2]['supportPositiveMaskFile']}],
 'applyOrder':[str(P/'right/manifest.json'),str(O/'roi3-manifest.json')],
 'rejected':[str(O/'roi1-manifest.json'),str(O/'roi2-manifest.json')],
 'remainingFailures':remaining,'wholeLeftBandPass':False,
 'candidateForQA':ref(O/'candidate-accepted-only-native.png'),'qaRemaining':ref(O/'qa-left-remaining-native.png'),
 'qaAcceptedJoin':ref(O/'qa-roi3-joined-native.png'),'selectionOrProgressModified':False,
 'sourceTileUnchanged':sha(prep['baseFile'])==prep['baseSha256'],'writesConfinedTo':str(O)}
dump(O/'handoff.json',handoff)
print(json.dumps({'handoff':str(O/'handoff.json'),'roi3Manifest':str(O/'roi3-manifest.json'),
 'roi3DerivedHash':entries[2]['derivedHash'],'roi3AlphaHash':entries[2]['alphaHash'],'roi3SupportHash':entries[2]['supportPositiveMaskHash'],
 'remainingFailures':remaining},ensure_ascii=False))
