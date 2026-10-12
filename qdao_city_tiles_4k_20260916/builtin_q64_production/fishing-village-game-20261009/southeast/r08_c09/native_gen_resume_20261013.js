(async function(pid,version) {
 const Z="D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast",T=Z+"/r08_c09",py="C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
 const q=s=>"'"+s.replace(/'/g,"''")+"'";
 const rr=await tools.exec_command({cmd:"Get-Content -LiteralPath 'D:/work/image/AGENTS.md' -Raw; Get-Content -LiteralPath 'D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json' -Raw",max_output_tokens:12000});
 if(rr.exit_code!==0||!rr.output.includes("允许继续使用现有内置绘图工具"))throw Error("Read updated rules before generation");
 const rq=await tools.exec_command({cmd:"Get-Content -LiteralPath "+q(T+"/"+pid+"-"+version+".request.json")+" -Raw",max_output_tokens:9000});if(rq.exit_code!==0)throw Error(rq.output);
 const req=JSON.parse(rq.output),responsePath=T+"/"+pid+"-"+version+".tool-response.json";
 const r=await tools.image_gen__imagegen({prompt:req.prompt,referenced_image_paths:req.referenced_image_paths,transparent_background:false});
 store(pid+version+"_result",r);
 const o=typeof r==="string"?{output_hint:r}:{output_hint:r.output_hint||r.outputHint||JSON.stringify(r,(k,v)=>["image_url","data"].includes(k)?"[binary omitted]":v)};
 const save=await tools.exec_command({cmd:"if(Test-Path -LiteralPath "+q(responsePath)+"){throw 'Response exists'};[System.IO.File]::WriteAllText("+q(responsePath)+", "+q(JSON.stringify(o))+", [System.Text.UTF8Encoding]::new($false))",max_output_tokens:200});if(save.exit_code!==0)throw Error(save.output);
 const m=o.output_hint.match(/as (C:[^\r\n]+\.png) by default/);if(!m)throw Error("Inspect saved response for source path");
 text(await tools.exec_command({cmd:"& "+q(py)+" "+q(T+"/resume_native_20261012.py")+" receipt "+pid+" "+version+" "+q(m[1])+" "+q(responsePath),max_output_tokens:800}));
 generatedImage(r);
})
