import uuid
from pathlib import Path
Z=Path(__file__).resolve().parent;p=Z/'update_current_production_20261012.py';s=p.read_text(encoding='utf-8');lines=s.splitlines();out=[]
for line in lines:
 if line.startswith('model_gate='):
  out.append("assert 'allows GPT Image 2.0' in model_requirement.read_text(encoding='utf-8-sig')")
  out.append("model_gate={'preferredImageModel':'GPT Image 2.5 on free/included route','permittedFallback':'GPT Image 2.0 or existing builtin image tool; no metadata confirmation gate','verifiedActualRoute':'builtin image_gen.imagegen','actualImageModel':None,'newGenerationAllowed':True,'reason':'User clarification revokes mandatory2.5 pause and authorizes current builtin production when free2.5 unavailable. Paid API remains unauthorized.','projectRules':{'path':str(model_rules),'sha256':sha(model_rules)},'modelRequirement':{'path':str(model_requirement),'sha256':sha(model_requirement)},'existingArtworkModelRelabelAllowed':False}")
 elif line.startswith('resume.update('):
  out.append(line.replace("status='existing_art_QA_active_new_generation_paused_required_image_model'","status='active_native_art_production'").replace('newArtworkGenerationAllowed=False','newArtworkGenerationAllowed=True'))
 elif line.startswith("progress.update(status=resume['status']"):
  out.append("progress.update(status=resume['status'],generationStopped=False,newGenerationAllowed=True,newArtworkGenerationAllowed=True,generationGate=model_gate,currentPatch='Root r04_c12 missing cores and r05_c12 west roof repair; central_sol c14 independent QA then c13 northward; east_sol r07_c14 independent QA then c14 northward; roof_sol c11/c10 extension',nextStep='Continue original exclusive owned native coordinates and necessary seam repairs; finish existing independent QA and continue next tile',inFlightState='Fresh builtin generation authorized under corrected free2.5 preference/2.0 fallback; actual image model remains unreturned',allRequiredNativeQAPassed=False,taskComplete=False)")
 elif line.startswith('ack.update('):out.append(line.replace('newArtworkGenerationAllowed=False','newArtworkGenerationAllowed=True'))
 else:out.append(line)
t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');t.write_text('\n'.join(out)+'\n',encoding='utf-8');t.replace(p);print('Corrected user model preference applied atomically to current local checkpoint helper')
