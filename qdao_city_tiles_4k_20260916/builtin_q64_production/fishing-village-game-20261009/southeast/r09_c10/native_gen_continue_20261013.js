(async function(args) {
 const Z="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast";
 const T=Z+"/"+args.tile,A="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009";
 const refs=[args.inputRef,A+"/donghai-natural-stone-clear-routes-v10.png",A+"/donghai-natural-stone-detail-v1.png",A+"/user-references-20261009/mail-daoist-style.jpg",args.actualRef];
 const stem=T+"/"+args.pid+"-"+args.v;
 const quote=s=>"'"+s.replace(/'/g,"''")+"'";
 const write=async(path,data)=>{const v=await tools.exec_command({cmd:"if (Test-Path -LiteralPath "+quote(path)+") { throw 'Versioned output exists' }; [System.IO.File]::WriteAllText("+quote(path)+", "+quote(data)+", [System.Text.UTF8Encoding]::new($false))",max_output_tokens:300});if(v.exit_code!==0)throw Error(v.output)};
 const request={tool:"image_gen__imagegen",route:"builtin",prompt:args.prompt,referenced_image_paths:refs,transparent_background:false,preparedAt:new Date().toISOString(),model:null,quality:null,actualModel:null,actualQuality:null};
 await write(stem+".prompt.txt",args.prompt);await write(stem+".request.json",JSON.stringify(request,null,2));
 const r=await tools.image_gen__imagegen({prompt:args.prompt,referenced_image_paths:refs,transparent_background:false});
 const hint=typeof r==='string'?r:(r.output_hint||r.outputHint||JSON.stringify(r,(k,v)=>k==='image_url'||k==='data'?'[binary omitted]':v));
 const match=hint.match(/exec-[0-9a-f-]+\.png/i);if(!match)throw Error('No output filename: '+hint.slice(0,2000));
 const find=await tools.exec_command({cmd:"Get-ChildItem -LiteralPath 'C:/Users/luyua/.codex/generated_images' -Filter "+quote(match[0])+" -Recurse -File | Select-Object -ExpandProperty FullName",max_output_tokens:800});
 if(find.exit_code!==0)throw Error(find.output);const paths=find.output.trim().split(/\r?\n/).filter(Boolean);if(paths.length!==1)throw Error('Raw path ambiguity '+find.output);
 await write(stem+".receipt.json",JSON.stringify({receivedAt:new Date().toISOString(),sourcePath:paths[0],outputHint:hint,tool:"image_gen__imagegen",route:"builtin",actualModel:null,actualQuality:null,model:null,quality:null},null,2));
 text({tile:args.tile,patch:args.pid,version:args.v,sourcePath:paths[0]});generatedImage(r);
})
