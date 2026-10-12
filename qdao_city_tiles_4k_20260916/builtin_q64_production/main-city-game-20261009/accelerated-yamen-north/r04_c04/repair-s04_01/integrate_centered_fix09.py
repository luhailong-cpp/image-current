from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,runpy,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix09_centered'
P=runpy.run_path(str(ROOT/'pipeline.py'))
nf=B/'fix08/generated.png';bf=D/'generated-centered.png';sf=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
N=np.array(Image.open(nf).convert('RGB'));G=np.array(Image.open(bf).convert('RGB'));S=np.array(Image.open(sf).convert('RGB'))
assert N.shape==G.shape==S.shape==(1254,1254,3)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Upper repair source join in true-world overlap, before the original failed seam.
upper=P['minimum_seam'](N[512:896].transpose(1,0,2),G[:384].transpose(1,0,2))+512
result=N.copy();mask=np.zeros((1254,1254),dtype=np.uint8)
ym=np.arange(1254)[:,None]
useg=ym>=upper[None,:]
mapped=np.zeros_like(N);mapped[512:1254]=G[:742]
result=np.where(useg[...,None],mapped,result);mask[useg]=1
# Keep all source choices within northern ownership, then retain exact old halo.
lower=P['minimum_seam'](result[1024:1139].transpose(1,0,2),S[:115].transpose(1,0,2))+1024
uses=ym>=lower[None,:]
oldmapped=np.zeros_like(N);oldmapped[1024:]=S[:230]
result=np.where(uses[...,None],oldmapped,result);mask[uses]=2
replay=N.copy();replay[mask==1]=mapped[mask==1];replay[mask==2]=oldmapped[mask==2]
assert np.array_equal(replay,result)
assert np.array_equal(result[1138:1254],S[114:230])
out=D/'s04_01_fix09_centered_derived.png'
if out.exists():raise FileExistsError(out)
Image.fromarray(result).save(out);Image.fromarray(mask).save(D/'source-index-mask.png')
hard=Image.new('RGB',(1254,1254));hard.paste(Image.fromarray(result).crop((0,512,1254,1139)),(0,0));hard.paste(Image.fromarray(S).crop((0,115,1254,742)),(0,627));hard.save(D/'derived-centered-boundary-native.png')
Image.fromarray(result).crop((0,448,1254,960)).save(D/'upper-repair-join-native.png')
hard.crop((600,370,1040,800)).save(D/'south-rail-repair-detail-native.png')
refs=[{'file':str(p),'sha256':sha(p),'worldBox':w} for p,w in [(nf,[12173,15245,13427,16499]),(bf,[12173,15757,13427,17011]),(sf,[12173,16269,13427,17523])]]
record={'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','mode':'RGB','opaque':True,'worldBoxWithHalo':[12173,15245,13427,16499],
        'kind':'native_pixel_source_selection_derivative','route':'native_pixel_source_selection','tool':None,'actualModel':None,'actualQuality':None,
        'sources':refs,'sourceOffsetsY':[0,512,1024],'sourceIndexMask':str(D/'source-index-mask.png'),'sourceIndexMaskSha256':sha(D/'source-index-mask.png'),
        'sourceIndexMeaning':{'0':'fix08 native','1':'centered fix09 native at target y512','2':'existing south native at target y1024'},
        'upperSeamNativeYRange':[int(upper.min()),int(upper.max())],'upperSeamYByNativeX':upper.tolist(),
        'lowerSeamNativeYRange':[int(lower.min()),int(lower.max())],'lowerSeamYByNativeX':lower.tolist(),
        'method':'Minimum-error binary source choice in true-world overlaps; no artwork resampling, blending, feathering or color correction',
        'pixelReplayMismatchCount':0,'formalNorthBoundaryUsesExactSouthSource':True,'southSourceNotModified':True,
        'resizedAfterGeneration':False,'finalArtUpscaled':False,'formalAccepted':False,'visualQA':'pending'}
for suffix in ['.png.derivation.json','.png.generation.json']:(out.with_suffix(suffix)).write_text(json.dumps(record,indent=2),encoding='utf-8')
receipt=json.loads((D/'tool-result.json').read_text(encoding='utf-8'))
host=Path(receipt['output_hint'].split(' as ')[1].split(' by default')[0])
evidence={'file':str(bf),'sha256':sha(bf),'width':1254,'height':1254,'format':'PNG','worldBox':[12173,15757,13427,17011],
          'route':'builtin_image_gen','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'hostOutputPath':str(host),
          'hostByteCopyVerified':sha(host)==sha(bf),'resizedAfterGeneration':False,'formalAccepted':False,
          'parameters':str(D/'parameters.json'),'parametersSha256':sha(D/'parameters.json'),'receipt':str(D/'tool-result.json'),'receiptSha256':sha(D/'tool-result.json'),
          'preparation':str(D/'preparation.json'),'preparationSha256':sha(D/'preparation.json'),'submittedReference':str(D/'centered-native-context.png'),
          'submittedReferenceSha256':sha(D/'centered-native-context.png')}
(D/'generation-evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'upperRange':record['upperSeamNativeYRange'],'lowerRange':record['lowerSeamNativeYRange'],'replayMismatch':0,'hostBytesVerified':evidence['hostByteCopyVerified']},indent=2))
