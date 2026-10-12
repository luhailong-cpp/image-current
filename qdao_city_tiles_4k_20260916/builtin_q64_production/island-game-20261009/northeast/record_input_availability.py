from native_work import *
p=ZONE/'progress.json';s=read(p)
for stage,err in [('shared input availability','D:/work/image/config/image-generation.json missing; batch metadata preserved from existing snapshot; no shared-file reconstruction attempted'),('approved style reference availability','D:/work/image/designs/mail-ui-v1/01-mail-event.png missing; child r04_c12_p01_01 and r03_c14_p04_02 requests failed before image output')]:
 if not any(x.get('stage')==stage for x in s['errors']):s['errors'].append({'stage':stage,'error':err,'resolved':False,'recordedAtUtc':now(),'action':'Recorded for delegating root; no substitute reference or alternate generation route used.'})
s['knownSharedEdgesReviewed']=[{'pair':['r03_c12','r03_c13'],'reviewedPixels':4096,'geometry':'pass','scope':'shared edge only'},{'pair':['r03_c13','r03_c14'],'reviewedPixels':4096,'geometry':'pass','scope':'shared existing edge only; c14 partial'}]
write(p,s)
print('Unresolved reference/config availability and actual shared-edge review scopes recorded.')

