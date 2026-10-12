from workflow import *
from PIL import Image
f=ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png';a=ROOT/'native/r13_c12_p12_v01.png'
im=Image.new('RGB',(1024,512));im.paste(Image.open(f).convert('RGB').crop((1024,3840,2048,4096)),(0,0));im.paste(Image.open(a).convert('RGB').crop((115,115,1139,371)),(0,256))
out=ROOT/'qa/r12c12-real-south-p12-v01.png';im.save(out)
write(ROOT/'qa/r12c12-real-south-p12-v01.json',{'sources':[{'file':str(x),'sha256':sha(x)} for x in [f,a]],'operation':'Actual final candidate north core edge joined to unchanged new native south core; no rescale/blend','qaImage':str(out),'status':'pending_visual_review'})
q=ROOT/'qa/r12_c12-sol-20261012-v02'
write(q/'root-rejected-proposal.json',{'reviewedAtUtc':now(),'candidate':str(ROOT/'tiles/r12_c12.candidate-sol-20261012-v02.png'),'sha256':sha(ROOT/'tiles/r12_c12.candidate-sol-20261012-v02.png'),'status':'not_adopted','reason':'The shared column body is wholly west of the final c12 core. This unnecessary broad rectangular overlay changes floor groove edge endpoints at x512. Preserve original internally passed candidate v01; adopt full-column continuation only where column source pixels are actually needed in c11.','retainedCandidate':str(f),'retainedSha256':sha(f),'formalAccepted':False})
p=read(ROOT/'progress-r13_c12.json');p.update(workingVersions={'11':'v02','12':'v01','13':'v01'},pendingRepairs=['r13_c12_p11 west native halo column geometry differs from layout; cross-column lower joint generation handled by left worker. Final core-only relevance will be checked.'],inFlight=True,inFlightRequests=['r13_c12_p14_v01'],nextStep='Finish row1 native and actual top/left continuity; continue row2.')
write(ROOT/'progress-r13_c12.json',p)
r=read(ROOT/'production-resume-20261012.json');r.update(updatedAtUtc=now(),inFlightRequests=['r13_c12_p14_v01']);r['pendingRepairs'][0].update(status='upper_whole_native_saved_lower_joint_in_preparation',upperNativeSha256='477f8e40d0e85dfd03294e99175a42274d77221681d70076df875d97961bf19c',coordinateFinding='Shared column body lies in c11; c12 errors are mainly native halo. Adopt lower shaft object rectangle in c11, retain c12 passed floor pixels.');write(ROOT/'production-resume-20261012.json',r)
print(json.dumps({'qa':str(out),'newBroadOverlayRejected':True,'retainedRootCandidateSha256':sha(f)}))

