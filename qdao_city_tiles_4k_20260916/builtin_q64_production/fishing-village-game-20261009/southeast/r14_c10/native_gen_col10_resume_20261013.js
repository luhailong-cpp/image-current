(async function(args) { const read = await Promise.allSettled(["D:/work/image/AGENTS.md","D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json"].map(path => tools.exec_command({cmd:"Get-Content -LiteralPath '"+path+"' -Raw",max_output_tokens:8500}))); if(read.some(x => x.status!=="fulfilled"||x.value.exit_code!==0)) throw Error("Rules unavailable"); const rules=read[0].value.output; if(!rules.includes("不可用则回退 2.0") || !rules.includes("允许继续使用现有内置绘图工具")) throw Error("Model rules changed"); const split=JSON.parse(read[1].value.output); if(split.batches.some(x=>x.status==="allocated_root_reserved"&&x.map==="fishing-village-game-20261009"&&x.tiles.includes(args.tile))) throw Error("Reserved target"); store("latestRules",read.map(x=>x.value.output)); return await ((async function(args) {
 const Z="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast";
 const T=Z+"/"+args.tile,A="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009";
 const refs=[args.inputRef||T+"/layout-only/"+args.pid+"-native-conditioned.png",A+"/donghai-natural-stone-clear-routes-v10.png",A+"/donghai-natural-stone-detail-v1.png",A+"/user-references-20261009/mail-daoist-style.jpg",args.actualRef];
 const stem=T+"/"+args.pid+"-"+args.v;
 const quote=(s)=>"'"+s.replace(/'/g,"''")+"'";
 const write=async (path,data)=>tools.exec_command({cmd:"if (Test-Path -LiteralPath "+quote(path)+") { throw 'Versioned output already exists' }; [System.IO.File]::WriteAllText("+quote(path)+", "+quote(data)+", [System.Text.UTF8Encoding]::new($false))",max_output_tokens:500});
 const request={tool:"image_gen__imagegen",route:"builtin",prompt:args.prompt,referenced_image_paths:refs,transparent_background:false,preparedAt:new Date().toISOString(),model:null,quality:null,actualModel:null,actualQuality:null};
 let x=await write(stem+".prompt.txt",args.prompt); if(x.exit_code!==0)throw Error(x.output);
 x=await write(stem+".request.json",JSON.stringify(request,null,2));if(x.exit_code!==0)throw Error(x.output);
 const r=await tools.image_gen__imagegen({prompt:args.prompt,referenced_image_paths:refs,transparent_background:false});
 store(args.tile+"_"+args.pid+"_"+args.v,r);
 const hint=typeof r==="string"?r:(r.output_hint||r.outputHint||JSON.stringify(r,(key,value)=>key==="image_url"||key==="data"?"[binary omitted]":value));
 const match=hint.match(/exec-[0-9a-f-]+\.png/i);if(!match)throw Error("No actual output filename in builtin result; inspect result before ingest");
 const sourcePath="C:/Users/luyua/.codex/generated_images/01a13465-881e-7c42-9277-421557f67ec9/"+match[0];
 const receipt={receivedAt:new Date().toISOString(),sourcePath,outputHint:hint,tool:"image_gen__imagegen",route:"builtin",actualModel:null,actualQuality:null,model:null,quality:null};
 x=await write(stem+".receipt.json",JSON.stringify(receipt,null,2));if(x.exit_code!==0)throw Error(x.output);
 generatedImage(r);
})

)(args); })