async function runN(frame) {
 const root="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl";
 const py="C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
 const q=s=>"'"+String(s).replace(/'/g,"''")+"'";
 const p=await tools.exec_command({cmd:"& "+q(py)+" -X utf8 "+q(root+"/tools/prepare_n_frame.py")+" "+frame,workdir:root,max_output_tokens:4000});
 if(p.exit_code!==0) throw new Error(p.output);
 const prep=JSON.parse(p.output.trim());
 const recPath=prep.request.replace(/\.request\.json$/, ".receipt.json");
 let rec;
 try {
 const r=await tools.image_gen__imagegen(prep.args);generatedImage(r);
 rec={returnedAt:new Date().toISOString(),output_hint:r.output_hint||null,actualModel:null,actualQuality:null};
 const native=(r.output_hint||"").match(/ as (.+?\.png) by default/);
 if(!native) throw new Error("Native output path unavailable: "+JSON.stringify(Object.keys(r)));
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+recPath+"\n+"+JSON.stringify(rec,null,2).split("\n").join("\n+")+"\n*** End Patch");
 text(await tools.exec_command({cmd:"& "+q(py)+" -X utf8 "+q(root+"/tools/register_e_frame.py")+" register --action run --direction N --frame "+frame+" --native "+q(native[1])+" --request "+q(prep.request)+" --receipt "+q(recPath),workdir:root,max_output_tokens:1000}));
 } catch(e) {
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+prep.request.replace(/\.request\.json$/,".error.json")+"\n+"+JSON.stringify({failedAt:new Date().toISOString(),error:String(e),request:prep.request},null,2).split("\n").join("\n+")+"\n*** End Patch");
 throw e;
 }
}
