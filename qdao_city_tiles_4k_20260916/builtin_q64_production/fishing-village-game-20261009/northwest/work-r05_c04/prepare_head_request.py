from workflow import *
import shutil
id='r05_c04_slim_post_head_bridge_v01'
con=read(B.parent/'production-contract.json');guide=W/'guides/slim-post-head-positional.png'
prompt='Use case: precise-object-edit for native seamless game map. IMAGE1 is the ONLY target crop. Produce exactly opaque 1254x1254 at its exact framing and scale. IMAGE2 approved whole map only identifies layout. IMAGE3 material detail only. IMAGE4 primary rounded refined Q Daoist game painting style. Render the fuzzy lower-right area into native crisp original detail, preserving every sharp pixel region and matching its warm sand grain scale. The approved slender vertical warm wood net support has its rounded cap around target (650,740), cream rope collar around (660,810), shaft width about 125 pixels centered x650 continuing vertically out of bottom. Its hanging blue-gray fishing net runs from the collar down and right out of frame, with continuous braided warm cream upper edge and thin gray open mesh showing warm sand behind. Continue the existing diagonal rope from (540,520) smoothly down-right to loop around this same cap/collar as a tension rope; no detached ends. This corrects the previous short ground peg at that location into the tall net support from the approved layout. Do not invent any additional post. Preserve the separate existing short wooden ground peg at (165,960), blue-green post collar fragment at far left and all sharp sand context. Maintain the exact cap/collar positions from the fuzzy guide and the actual sharp top rope route. Native rounded sculpted warm wood with restrained smooth grain, no deep gritty cracks or fractures. Preserve view angle and lighting. No zoom, reframe, ground-foot beneath the tall shaft inside this crop, buildings, rocks larger than existing small pebbles, text, UI, characters or borders. Full object head and whole adjacent rope connection must be coherent, while the shaft and net intentionally continue beyond bottom/right frame.'
pf=W/'prompts'/(id+'.prompt.txt');pf.write_text(prompt,encoding='utf-8')
refs=[str(guide),con['layoutReference'],con['detailStyleReference'],con['primaryStyleReference']]
write(W/'receipts'/(id+'.request.json'),{'id':id,'createdAt':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptFile':str(pf),'referenced_image_paths':refs,'referenceRoles':['native positional edit target','layout only','material only','primary approved style'],'referenceHashes':[sha(p) for p in refs],'globalNativeBox':[15130,15500,16384,16754],'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
shutil.copy2(B/'work-r05_c03/record_bridge.py',W/'record_bridge.py')
# Verify all successful outputs known locally before submitting another call.
audit=[]
for p in sorted((W/'receipts').glob('*.receipt.json')):
 r=read(p);n=B/'native'/(r['id']+'.png');g=Path(str(n)+'.generation.json')
 audit.append({'id':r['id'],'nativeExists':n.exists(),'generationExists':g.exists(),'sha256':sha(n) if n.exists() else None,'size':list(Image.open(n).size) if n.exists() else None})
assert all(a['nativeExists'] and a['generationExists'] and a['size']==[1254,1254] for a in audit)
write(W/'qa/successful-output-audit.json',{'at':datetime.now(timezone.utc).isoformat(),'outputs':audit,'passed':True})
print(id)
