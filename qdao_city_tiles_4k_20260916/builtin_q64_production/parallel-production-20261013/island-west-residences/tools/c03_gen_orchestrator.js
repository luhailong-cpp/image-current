async function c03Generate(stem) {
  const b='D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences';
  const py='C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
  const attempt=Number(stem.slice(-2));
  const pc=await tools.exec_command({cmd:"Get-Content -Raw -LiteralPath 'D:/work/image/AGENTS.md' | Out-Null; Get-Content -Raw -LiteralPath 'D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json' | Out-Null; & '"+py+"' -B '"+b+"/tools/batch_pipeline.py' precall --stem "+stem+(attempt>1?" --retry-reason 'New version with focused geometry or material instructions; all existing raw preserved and prior HOLD not passed'":""),max_output_tokens:3000});
  const gate=JSON.parse(pc.output.trim());
  if(!gate.ready)throw new Error('Precall hold: '+JSON.stringify(gate));
  const pr=await tools.exec_command({cmd:"Get-Content -Raw -LiteralPath '"+b+"/prompts/"+stem+".txt' | ConvertTo-Json -Compress",max_output_tokens:2500});
  await tools.mcp__node_repl__js({code:"var c03fs=await import('node:fs/promises');await c03fs.mkdir('"+b+"/tool-results/c03',{recursive:true});",title:'准备 c03 原始返回归档'});
  const result=await tools.image_gen__imagegen({prompt:JSON.parse(pr.output.trim()),referenced_image_paths:gate.referenced_image_paths,transparent_background:false});
  store(stem+'.toolResult',result);
  const s=JSON.stringify(result),p=b+'/tool-results/c03/'+stem+'.actual.json';
  let archive=await tools.mcp__node_repl__js({code:'var c03dest='+JSON.stringify(p)+";await c03fs.writeFile(c03dest,'',{flag:'wx'});",title:'保存 c03 实际工具返回'});
  if(archive.isError)throw new Error(JSON.stringify(archive));
  for(let i=0;i<s.length;i+=50000){
    archive=await tools.mcp__node_repl__js({code:'await c03fs.appendFile(c03dest,'+JSON.stringify(s.slice(i,i+50000))+",'utf8');",title:'保存 c03 返回数据'});
    if(archive.isError)throw new Error(JSON.stringify(archive));
  }
  archive=await tools.mcp__node_repl__js({code:"var c03actual=JSON.parse(await c03fs.readFile(c03dest,'utf8'));await c03fs.writeFile('"+b+'/tool-results/c03/'+stem+".raw.png',Buffer.from(c03actual.image_url.split(',')[1],'base64'),{flag:'wx'});console.log('Saved raw and complete result: "+stem+"');",title:'立即保存 c03 原图'});
  if(archive.isError)throw new Error(JSON.stringify(archive));
  const ing=await tools.exec_command({cmd:"& '"+py+"' -B '"+b+"/tools/batch_pipeline.py' ingest --stem "+stem+" --raw '"+b+'/tool-results/c03/'+stem+".raw.png' --tool-result '"+p+"' --precall-record '"+gate.precallRecord.path+"'",max_output_tokens:900});
  text(ing.output);
  generatedImage(result);
  return {stem,saved:true};
}
