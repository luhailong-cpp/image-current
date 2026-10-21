(async function(args) {
 const Z="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast";
 if(!["r14_c11","r13_c11"].includes(args.tile)) throw Error("Outside assignment");
 const T=Z+"/"+args.tile,A="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009";
 const refs=[args.inputRef,A+"/donghai-natural-stone-clear-routes-v10.png",A+"/donghai-natural-stone-detail-v1.png",A+"/user-references-20261009/mail-daoist-style.jpg",args.actualRef];
 const stem=T+"/"+args.pid+"-"+args.v;
 const quote=s=>"'"+s.replace(/'/g,"''")+"'";
 const write=async(path,data)=>{const x=await tools.exec_command({cmd:"if (Test-Path -LiteralPath "+quote(path)+") { throw 'Versioned output exists' }; [System.IO.File]::WriteAllText("+quote(path)+", "+quote(data)+", [System.Text.UTF8Encoding]::new($false))",max_output_tokens:300}); if(x.exit_code!==0)throw Error(x.output);};
 const request={tool:"image_gen__imagegen",route:"builtin",prompt:args.prompt,referenced_image_paths:refs,transparent_background:false,preparedAt:new Date().toISOString(),model:null,quality:null,actualModel:null,actualQuality:null};
 await write(stem+".prompt.txt",args.prompt);await write(stem+".request.json",JSON.stringify(request,null,2));
 const rules=await tools.exec_command({cmd:load("rereadRulesCmd"),max_output_tokens:500});if(rules.exit_code!==0)throw Error(rules.output);text(rules.output);
 const r=await tools.image_gen__imagegen({prompt:args.prompt,referenced_image_paths:refs,transparent_background:false});
 store(args.tile+"_"+args.pid+"_"+args.v,r);
 const hint=typeof r==="string"?r:(r.output_hint||r.outputHint||JSON.stringify(r,(key,value)=>key==="image_url"||key==="data"?"[binary omitted]":value));
 store("lastHint",hint);store("lastArgs",args);
 const sourcePath=hint.match(/[A-Z]:\\[^:\n]+?\\exec-[a-f0-9-]+\.png/i)?.[0];if(!sourcePath)throw Error("Path missing from actual tool hint");
 const receipt={receivedAt:new Date().toISOString(),sourcePath,outputHint:hint,tool:"image_gen__imagegen",route:"builtin",actualModel:null,actualQuality:null,model:null,quality:null};
 await write(stem+".receipt.json",JSON.stringify(receipt,null,2));
 const ingest=await tools.exec_command({cmd:"& "+quote(load("PY"))+" "+quote(Z+"/tile_native_workflow.py")+" --tile "+args.tile+" ingest "+args.pid+" "+args.v+" "+quote(sourcePath),max_output_tokens:1000});text(ingest);
 text({outputHint:hint});
 generatedImage(r);
})
