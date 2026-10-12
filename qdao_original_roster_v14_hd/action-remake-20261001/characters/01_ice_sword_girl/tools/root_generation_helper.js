async function(spec){
 const R='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/01_ice_sword_girl';
 const promptFile='sources/'+spec.stem+'.prompt.txt',receiptFile='sources/'+spec.stem+'.receipt.json';
 const started=(await tools.clock__curr_time({})).current_time;
 await tools.apply_patch('*** Begin Patch\n*** Add File: '+R+'/'+promptFile+'\n+'+spec.prompt.replace(/\n/g,'\n+')+'\n*** End Patch');
 const args={prompt:spec.prompt,referenced_image_paths:spec.refs,transparent_background:true};
 const result=await tools.image_gen__imagegen(args);generatedImage(result);
 const completed=(await tools.clock__curr_time({})).current_time;
 const receipt={startedAt:started,completedAt:completed,tool:'image_gen__imagegen',route:'builtin',submittedParameters:{...args,model:null,quality:null},actualModel:null,actualQuality:null,toolResult:{output_hint:result.output_hint},referenceRoles:spec.roles,unverifiedReason:'宿主管理，无model/quality选择器，工具未披露实际型号/质量。'};
 await tools.apply_patch('*** Begin Patch\n*** Add File: '+R+'/'+receiptFile+'\n+'+JSON.stringify(receipt,null,2).replace(/\n/g,'\n+')+'\n*** End Patch');
 const host=result.output_hint.match(/as (C:\\[^\r\n]+?\.png) by default/)[1];
 const quote=s=>"'"+s.replace(/'/g,"''")+"'",dest=R+'/'+spec.file;
 text(await tools.exec_command({cmd:'if(Test-Path -LiteralPath '+quote(dest)+'){throw "Target exists"}\nNew-Item -ItemType Directory -Force -Path '+quote(dest.slice(0,dest.lastIndexOf('/')))+' | Out-Null\nCopy-Item -LiteralPath '+quote(host)+' -Destination '+quote(dest)+'\n& '+quote('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')+' '+quote(R+'/tools/record_frame.py')+' '+quote(spec.file)+' '+quote(receiptFile)+' '+quote(promptFile),max_output_tokens:1200}));
 return {file:spec.file,host,completed};
}
