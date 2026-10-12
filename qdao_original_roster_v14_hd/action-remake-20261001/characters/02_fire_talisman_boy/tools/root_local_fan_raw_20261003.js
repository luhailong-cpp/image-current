async (action,direction,frame,target,phase,attempt=1,replace=false)=>{
const root="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/02_fire_talisman_boy";
const refs=[{path:target,role:"EDIT TARGET: fixed framing, camera, rendering, anatomical connections and global scale"},{path:"D:/work/image/q_daoist_character_pack_4096/02_fire_talisman_boy_transparent_4096.png",role:"committed character identity, anatomical right fan and left bell",sha256:"8df2760a5a80eb54ea21558abace8bcbaeca7f7ae6f64de022b6a8b1919c854a"},{path:"D:/work/image/designs/jubaozhai-ui/02-characters.png",role:"approved painted art style",sha256:"7a95140fc3c7a0ae6562ec6dff51d5296edd15116375152a8b22502c7107e879"}];
const hashResult=await tools.exec_command({cmd:"(Get-FileHash -Algorithm SHA256 -LiteralPath '"+target.replace(/'/g,"''")+"').Hash.ToLowerInvariant()",max_output_tokens:100});
refs[0].sha256=hashResult.output.trim();
if(!/^[a-f0-9]{64}$/.test(refs[0].sha256))throw new Error("Cannot record edit target SHA before generation");
const prompt="Precise local image edit. Image 1 is the EDIT TARGET. Image 2 preserves the character identity. Image 3 preserves approved painted rendering. "+phase+" Preserve all pixels outside the red paper fan as faithfully as possible: body, hair, face, hands, arms, bell, legs, shoes, canvas scale and position. Transparent RGBA square, native at least 1024. Keep existing transparency. Do not add any effect/text/shadow. Configuration target GPT Image2.5 Sunburst/max is host-managed.";
const id=action+"-"+direction+"-"+String(frame).padStart(2,"0")+"-20261003-attempt-"+String(attempt).padStart(2,"0");
const record={call_id:id,requested_slot:action+"/"+direction+"/"+String(frame).padStart(2,"0"),submittedAt:new Date().toISOString(),userTimezone:"America/New_York",route:"builtin",tool:"image_gen.imagegen",configSnapshot:{model:"gpt-image-2.5-sunburst",quality:"max",builtin_product:"ChatGPT Images 2.5",verified_on:"2026-10-01",batchContinued:true},submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:refs.map(x=>x.path)},actualModel:null,actualQuality:null,prompt:"prompts/"+id+".txt",references:refs,status:"submitted",outputFiles:[]};
const initial=JSON.stringify(record);
await tools.apply_patch("*** Begin Patch\n*** Add File: "+root+"/prompts/"+id+".txt\n+"+prompt+"\n*** Add File: "+root+"/records/"+id+".json\n+"+initial+"\n*** End Patch");
let result;
try {result=await tools.image_gen__imagegen({prompt,referenced_image_paths:refs.map(x=>x.path),transparent_background:true});}
catch(e){record.status="failed";record.endedAt=new Date().toISOString();record.rawError=String(e);await tools.apply_patch("*** Begin Patch\n*** Update File: "+root+"/records/"+id+".json\n@@\n-"+initial+"\n+"+JSON.stringify(record)+"\n*** End Patch");text({slot:record.requested_slot,error:String(e)});return{ok:false,slot:record.requested_slot,error:String(e)};}
generatedImage(result);
const path=result.output_hint?.match(/as ([^\r\n]+\.png) by default/)?.[1];
if(!path){text({slot:record.requested_slot,error:"No parseable local output path; actual returned metadata must be inspected"});return{ok:false,slot:record.requested_slot,error:"No parseable local output path"};}
await tools.apply_patch("*** Begin Patch\n*** Add File: "+root+"/records/"+id+".receipt.json\n+"+JSON.stringify({call_id:id,returnedAt:new Date().toISOString(),nativePath:path,output_hint:result.output_hint,actualModel:null,actualQuality:null,toolResultKeys:Object.keys(result)})+"\n*** End Patch");
return{ok:true,slot:record.requested_slot,path,record:"records/"+id+".json",action,direction,frame,replace};
}
