(async function(a){
 const T='D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c08';
 const q=s=>"'"+s.replace(/'/g,"''")+"'";
 const pre=await Promise.allSettled([tools.exec_command({cmd:"Get-Content -LiteralPath 'D:/work/image/AGENTS.md' -Raw",max_output_tokens:5000}),tools.exec_command({cmd:"Get-Content -LiteralPath 'D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json' -Raw",max_output_tokens:9000})]);
 for(const r of pre)if(r.status!=='fulfilled'||r.value.exit_code!==0)throw Error('Failed required instruction reads');
 if(JSON.parse(pre[1].value.output).batches.some(b=>b.map==='fishing-village-game-20261009'&&b.status==='allocated_root_reserved'&&b.tiles.includes('r08_c08')))throw Error('Reserved coordinate');
 const stem=T+'/'+a.pid+'-'+a.v;
 async function write(path,value){let r=await tools.exec_command({cmd:'if(Test-Path -LiteralPath '+q(path)+"){throw 'Version already exists'};[System.IO.File]::WriteAllText("+q(path)+', '+q(value)+', [System.Text.UTF8Encoding]::new($false))',max_output_tokens:300});if(r.exit_code!==0)throw Error(r.output);}
 await write(stem+'.prompt.txt',a.prompt);
 await write(stem+'.request.json',JSON.stringify({tool:'image_gen__imagegen',route:'builtin',prompt:a.prompt,referenced_image_paths:a.refs,transparent_background:false,preparedAt:new Date().toISOString(),model:null,quality:null,actualModel:null,actualQuality:null},null,2));
 const r=await tools.image_gen__imagegen({prompt:a.prompt,referenced_image_paths:a.refs,transparent_background:false});
 const hint=typeof r==='string'?r:(r.output_hint||r.outputHint||JSON.stringify(r,(k,v)=>['image_url','data'].includes(k)?'[binary omitted]':v));
 const sourcePath=hint.match(/as (C:[^\r\n]+\.png) by default/)?.[1];if(!sourcePath)throw Error('Inspect actual result path');
 await write(stem+'.receipt.json',JSON.stringify({receivedAt:new Date().toISOString(),sourcePath,outputHint:hint,tool:'image_gen__imagegen',route:'builtin',actualModel:null,actualQuality:null},null,2));
 generatedImage(r);
})
