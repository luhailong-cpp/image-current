from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Q=T/'review/material-band-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ev(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mp=T/'candidate/r16_c14-material-repair-v2-20261013-manifest.json';m=read(mp);now=datetime.now(timezone.utc).isoformat()
base=np.asarray(Image.open(m['baseCandidate']['path']).convert('RGB'));source=np.asarray(Image.open(m['repairNative']['path']).convert('RGB'))
mask=np.asarray(Image.open(m['alpha']['path']));w=mask.astype(np.uint32)[...,None];expected=base.copy()
expected[850:2104,2842:4096]=((base[850:2104,2842:4096].astype(np.uint32)*(255-w)+source.astype(np.uint32)*w+127)//255).astype(np.uint8)
actual=np.asarray(Image.open(m['candidate']['path']).convert('RGB'));context=np.asarray(Image.open(m['context']['path']).convert('RGB'));oldctx=np.asarray(Image.open(m['baseContext']['path']).convert('RGB'))
assert np.array_equal(expected,actual);assert np.array_equal(context[115:4211,115:4211],actual)
assert np.array_equal(actual[:256],base[:256]) and np.array_equal(actual[-256:],base[-256:]) and np.array_equal(actual[:,:256],base[:,:256])
expectedctx=oldctx.copy();expectedctx[115:4211,115:4211]=actual;assert np.array_equal(expectedctx,context)
oldqa=read(T/'review/native49-56e834ccdf9f6e52a143/visual-qa-v1.json')
replay={'baseSixteenNativesAndSavedAlphaPixelIdentical':True,'baseVerificationRecord':ev(T/'review/native49-56e834ccdf9f6e52a143/index.json'),'repairSavedCandidatePixelIdentical':True,'savedContextPixelIdentical':True,'northWestSouth256PixelEdgesUnchanged':True,'outsideMaskPixelsUnchanged':True,'resize':False,'rgbCorrection':False}
qa={'schemaVersion':2,'tile':'r16_c14','reviewedAt':now,'candidate':m['candidate'],'context':m['context'],'baseFullQA':ev(T/'review/native49-56e834ccdf9f6e52a143/visual-qa-v1.json'),'inspectionBasis':'49 native regions + 14 north/west join images already individually viewed. Their unchanged pixels are reused; after repair full native1254x650 segment and 3 local original-size crops inspected. No added geometry break, double edge or artificial straight value/texture step found.','currentRepairViews':[x for x in m['reviewImages'] if '-after-' in x['path']],'internalGeometryQA':'pass','internalArtQA':'pass_with_texture_watch','resolved':[{'id':'R16C14-M01','coreBox':[3110,1100,4096,1180],'status':'resolved_native_repair','note':'Straight transition removed; natural mineral patches continue through old line. True horizontal and vertical mortar preserved.'}],'externalNeighborSeamQA':oldqa['externalNeighborSeamQA'],'textureWatch':'Local natural limestone grain varies across sources; no clear geometric discontinuity remains in reviewed current coverage. Neighbor-independent review and east join still required.','replay':replay,'actualNativeOutputCount':18,'activeNativeCount':16,'activeRepairNativeCount':1,'formalAccepted':False,'actualModel':None,'actualQuality':None,'gameRun':False}
qap=Q/'visual-qa-v2.json';save(qap,qa)
status='internal_pass_north_west_local_pass_with_texture_watch_east_pending'
ptr={'schemaVersion':2,'tile':'r16_c14','publishedAt':now,'status':status,'candidate':m['candidate'],'context':m['context'],'manifest':ev(mp),'visualQA':ev(qap),'baseAssemblyManifest':m['baseManifest'],'activeNativeCount':16,'actualNativeOutputCount':18,'activeRepairNativeCount':1,'internalArtQA':qa['internalArtQA'],'externalNeighborSeamQA':qa['externalNeighborSeamQA'],'replay':replay,'formalAccepted':False}
save(T/'candidate/latest-selection.json',ptr);save(T/'candidate/latest-assembly.json',ptr)
p=read(T/'progress.json');p.update(updatedAt=now,status=status,candidate=m['candidate']['path'],candidateSha256=m['candidate']['sha256'],context=m['context']['path'],contextSha256=m['context']['sha256'],assemblyManifest=str(mp),repairManifest=str(mp),visualQA=ev(qap),actualNativeOutputCount=18,activeRepairNativeCount=1,internalArtQA=qa['internalArtQA'],externalNeighborSeamQA=qa['externalNeighborSeamQA'],remainingFindings=[],formalAccepted=False,nextStep='Independent neighbor QA; begin assigned r16_c15 when north r15_c15 south core edge is stable, using this unchanged structural east edge.')
save(T/'progress.json',p)
for name in ['production-resume-20261013.json','local-continuation-20261013.json']:
 c=read(T/name);c.update(updatedAt=now,status=status,actualNativeOutputCount=18,activeRepairNativeCount=1,candidate=m['candidate'],context=m['context'],manifest=ev(mp),visualQA=ev(qap),replay=replay,internalQA=qa['internalArtQA'],externalQA=qa['externalNeighborSeamQA'],remainingFindings=[],firstRepairOutputThisRound=m['repairNative'],nextCoordinateAssigned='r16_c15',nextStep=p['nextStep'],formalAccepted=False);save(T/name,c)
save(T/'handoff-20261013.json',{'tile':'r16_c14','createdAt':now,'selected':ptr,'originalSourceCount':18,'allSuccessfulOutputsIngested':True,'remaining':qa['externalNeighborSeamQA'],'nextAssignedCoordinate':'r16_c15','gitActions':False,'globalProgressWritten':False,'actualModel':None,'actualQuality':None})
print(json.dumps({'candidate':m['candidate'],'context':m['context'],'manifest':ev(mp),'visualQA':ev(qap),'sourceCount':18,'status':status},indent=2))
