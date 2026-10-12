async function(task){
 const root="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy",q=s=>"'"+s.replace(/'/g,"''")+"'", py="C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
 if(!task.stem.startsWith(root+"/provenance/"))throw Error("out of scope");
 const cmd=async c=>await tools.exec_command({cmd:c,max_output_tokens:1200});
 const write=async(path,value)=>{const content=typeof value==="string"?value:JSON.stringify(value,null,2)+"\n";return await tools.apply_patch("*** Begin Patch\n*** Add File: "+path+"\n"+content.split("\n").map(l=>"+"+l).join("\n")+"\n*** End Patch");};
 const check=await cmd(`Test-Path -LiteralPath ${q(task.stem+".submission.json")}`);if(check.output.trim()==="True")return {status:"attempt_exists",stem:task.stem};
 const cr=await cmd("Get-Content -LiteralPath 'D:/work/image/config/image-generation.json' -Raw"),config=JSON.parse(cr.output),startedAt=new Date().toISOString();
 await write(task.stem+".prompt.txt",task.args.prompt);
 await write(task.stem+".submission.json",{startedAt,tool:"image_gen__imagegen",route:"builtin",timezone:"America/New_York",configTarget:{model:config.model,quality:config.quality},configSnapshot:config,submittedParameters:{...task.args,model:null,quality:null},actualModel:null,actualQuality:null});
 let result;try{result=await tools.image_gen__imagegen(task.args);generatedImage(result);}
 catch(e){await write(task.stem+".error.json",{startedAt,completedAt:new Date().toISOString(),error:String(e),step:"image_generation"});return{status:"failed",frame:task.frame,direction:task.direction,error:String(e)};}
 await write(task.stem+".receipt.json",{completedAt:new Date().toISOString(),result:{...result,image_url:result.image_url?"[omitted; source PNG retained until accepted export]":undefined}});
 const source=result.output_hint?.match(/ as (.+?\.png) by default/)?.[1];if(!source)return{status:"source_path_missing"};
 const copied=await cmd(`Copy-Item -LiteralPath ${q(source)} -Destination ${q(task.stem+".png")}`);if(copied.exit_code!==0)throw Error(copied.output);
 const n=await cmd(`& ${q(py)} -X utf8 ${q(root+"/tools/record_native.py")} ${q(task.stem)} --status candidate_pending_visual`);return{status:n.exit_code===0?"native_candidate":"record_failed",frame:task.frame,direction:task.direction,stem:task.stem,output:n.output};
}
