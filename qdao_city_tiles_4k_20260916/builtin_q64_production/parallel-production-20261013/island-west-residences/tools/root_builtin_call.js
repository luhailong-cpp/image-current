(async (stem, retryReason) => {
 const b='D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences';
 const py='C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
 const q=s=>"'"+s.replaceAll("'","''")+"'";
 const pre=await tools.exec_command({cmd:"$rules=Get-Content -LiteralPath 'D:/work/image/AGENTS.md' -Raw; $split=Get-Content -LiteralPath 'D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json' -Raw|ConvertFrom-Json; $g=& "+q(py)+" -B "+q(b+'/tools/batch_pipeline.py')+' precall --stem '+q(stem)+(retryReason?' --retry-reason '+q(retryReason):'')+" | ConvertFrom-Json; $i=Get-Content -LiteralPath "+q(b+'/guides/'+stem+'.input.json')+" -Raw|ConvertFrom-Json; @{ready=$g.ready;precall=$g.precallRecord.path;ruleHash=(Get-FileHash -LiteralPath 'D:/work/image/AGENTS.md' -Algorithm SHA256).Hash;args=@{prompt=(Get-Content -LiteralPath $i.prompt.path -Raw);referenced_image_paths=$i.imageGenReferencedImagePaths;transparent_background=$false}}|ConvertTo-Json -Depth 8 -Compress",max_output_tokens:4000});
 if(pre.exit_code!==0)throw Error(pre.output);
 const p=JSON.parse(pre.output);if(!p.ready)throw Error('Precall not ready');
 if(p.ruleHash.toLowerCase()!=='57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a')throw Error('Root rules changed; reread required');
 let r;
 try{r=await tools.image_gen__imagegen(p.args);}catch(e){
  const err={stem,error:String(e),precall:p.precall,recordedAtUtc:new Date().toISOString(),returnedImage:false};
  store('lastGenerationError',err);
  const path=b+'/receipts/'+stem+'.error-'+Date.now()+'.json';
  await tools.exec_command({cmd:'[IO.File]::WriteAllText('+q(path)+','+q(JSON.stringify(err))+',[Text.UTF8Encoding]::new($false))',max_output_tokens:300});
  throw e;
 }
 store('lastActualResult',r);store('lastActualStem',stem);store('lastActualPrecall',p.precall);
 const raw=r.output_hint.match(/ as (.+?) by default\./s)[1];
 const receipt=b+'/receipts/'+stem+'.tool-response.json';
 const obj=JSON.stringify({image_url:'',output_hint:r.output_hint});
 const ingest=await tools.exec_command({cmd:'$p='+q(receipt)+"; if(Test-Path -LiteralPath $p){throw 'Receipt already exists'}; $o="+q(obj)+"|ConvertFrom-Json; $o.image_url='data:image/png;base64,'+[Convert]::ToBase64String([IO.File]::ReadAllBytes("+q(raw)+")); if($o.image_url.Length -ne "+r.image_url.length+"){throw 'Length mismatch'}; [IO.File]::WriteAllText($p,($o|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false)); & "+q(py)+' -B '+q(b+'/tools/batch_pipeline.py')+' ingest --stem '+q(stem)+' --raw '+q(raw)+' --tool-result '+q(receipt)+' --precall-record '+q(p.precall),max_output_tokens:2200});
 if(ingest.exit_code!==0){text(ingest);throw Error('Ingest failed; actual result preserved in store');}
 const ii=JSON.parse(ingest.output);text({stem,status:ii.status,size:ii.measured?.nativeSize,sha256:ii.raw?.sha256,saved:ii.raw?.path});generatedImage(r);
})
