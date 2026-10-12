from r06_c13_extension import *
pinned={};checks=[];notes=[]
for r in range(1,5):
 for c in range(1,5):
  p=f'r06_c13_p{r}{c}';v='v2' if p.endswith(('p11','p41')) else 'v1'
  n=Z/'native'/f'{p}-{v}.png';d=json.loads(Path(str(n)+'.generation.json').read_text(encoding='utf-8'))
  assert Image.open(n).size==(1254,1254)
  assert sha(n)==d['sha256']==d['source']['sha256']
  assert d['coordinates']==coords(p)
  assert d['actualModel'] is None and d['actualQuality'] is None
  assert d['configSnapshot']
  for key in ['source','prompt','receipt']:
   e=d[key];assert sha(e['path'])==e['sha256'],(p,key)
  for e in d['references']:assert sha(e['path'])==e['sha256'],(p,e['role'])
  assert len(d['references'])==4
  pinned[p]={'path':str(n).replace('\\','/'),'sha256':sha(n)}
  checks.append({'patchId':p,'nativeImage':ref(n,'selected native candidate'),'generationRecord':ref(str(n)+'.generation.json','complete source evidence'),'coordinates':coords(p),'actualModel':None,'actualQuality':None,'configCaptureStage':d['configSnapshotCaptureStage'],'allStoredEvidenceHashesVerified':True})
selection={'schemaVersion':1,'tile':T,'status':'proposed_selection_pending_root_assembly_and_review','patches':pinned}
sp=Z/'records'/f'{T}.selection-proposed-v1.json';write(sp,selection)
handoff={'createdAtUtc':now(),'tile':T,'nativeCountSelected':16,'nativeGenerationCount':18,'selection':ref(sp,'explicit proposed16source selection'),'coordinates':ref(Z/'records'/f'{T}.coordinates.json','authoritative native mapping'),'verifiedSources':checks,'nativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'tileCoreGlobalBox':[49152,20480,53248,24576],'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'formalAccepted':False,'usable':False,'rootAssemblyPending':True,'reviewNotes':['All per-generation full native left/top QA viewed; p41-v2 additionally right neighbor checked.','p11-v1 rejected for miniature/duplicated building; selected p11-v2.','p41-v1 obsolete wrong gray floor/eyeless fish; selected p41-v2 after new western p44 material source.','p33 and p43 join gray landing and wooden deck; root should assess full-scale material boundary against wider overview.','p34 seating under umbrella follows crop but develops a connected bench-like form; root should review against original separate table/chair layout before acceptance.','All upper/east outer tile borders still lack generated external neighbors; no formal tile acceptance.','Early10 generation record config snapshots backfilled retrospectively with honest capture-stage; no actual selector claimed.'],'pendingRootQA':['assemble16cores','24 internal full core-edge seams','9 four-way junctions','4096 west border against current r06_c12 selected sources','4096 south border against updated r07_c13 sources']}
write(Z/'records'/f'{T}.handoff-v1.json',handoff)
print(json.dumps({'selection':str(sp),'handoff':str(Z/'records'/f'{T}.handoff-v1.json'),'checks':len(checks),'allEvidenceHashesVerified':True}))
