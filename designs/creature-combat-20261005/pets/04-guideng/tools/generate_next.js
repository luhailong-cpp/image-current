const prep=await tools.exec_command({cmd:"& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'D:/work/image/designs/creature-combat-20261005/pets/04-guideng/tools/prepare_cast.py'",max_output_tokens:4000});
const p=JSON.parse(prep.output);if(p.done){text('E cast complete');}else{
const started=new Date().toISOString();
const r=await tools.image_gen__imagegen({prompt:p.prompt,referenced_image_paths:p.refs,transparent_background:true});
generatedImage(r);
const nn=String(p.frame).padStart(2,'0');
const native=r.output_hint.match(/as (C:\\.*?\.png) by default/)[1];
const rec={file:'runtime/cast/E/'+nn+'.png',nativeFile:native,generatedAt:new Date().toISOString(),generationStartedAt:started,tool:'image_gen.imagegen',route:'builtin',configSnapshot:p.cfg,submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:p.refs},actualModel:null,actualQuality:null,unverifiedReason:'宿主管理，工具未披露model/quality，未开放选择器。',evidence:{resultKeys:Object.keys(r),output_hint:r.output_hint},prompt:'prompts/E-cast/'+nn+'.txt',references:p.refs.map((path,i)=>({path,role:['E identity','W identity/anatomy','primary painting/material style','previous frame continuity'][i]})),visualStatus:'pending sequence review'};
await tools.apply_patch('*** Begin Patch\n*** Add File: '+p.base+'/records/E-cast/'+nn+'.json\n+'+JSON.stringify(rec,null,2).replace(/\n/g,'\n+')+'\n*** End Patch');
text(await tools.exec_command({cmd:"& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+p.base+"/tools/save_frame.py' '"+p.base+"/records/E-cast/"+nn+".json'",max_output_tokens:250}));
text({completed:p.frame});
}
