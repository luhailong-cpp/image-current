(async function(args) {
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
 const sourcePath="C:/Users/luyua/.codex/generated_images/01a1216d-4a55-7063-ba13-5ddf6d9106f7/"+match[0];
 const receipt={receivedAt:new Date().toISOString(),sourcePath,outputHint:hint,tool:"image_gen__imagegen",route:"builtin",actualModel:null,actualQuality:null,model:null,quality:null};
 x=await write(stem+".receipt.json",JSON.stringify(receipt,null,2));if(x.exit_code!==0)throw Error(x.output);
 generatedImage(r);
})
