
const b=load("base"),p=load("patch"),v=p.v||1,name="p"+p.r+p.c+"-v"+v,d=b+"/"+p.tile;
const common="Use case: stylized-concept. Generate ONE 1254x1254 native raster patch of a continuous Chinese Daoist rounded Q RPG environment. IMAGE 1 is the exact positional target. Preserve existing sharp native overlap strips exactly and continue all crossing edges, materials, perspective and shadows seamlessly into the new interior. Do not leave straight strip boundaries. Its blurred interior is a coordinate sketch ONLY, redraw as crisp original artwork. IMAGE 2 is wider approved geometry context only, never copy the entire scene into this patch. IMAGE 3 is approved daylight art style/materials only. IMAGE 4 is an adjacent native scale and style anchor, never duplicate its objects. Extreme close crop of a huge map. Do not zoom out or fit complete objects into frame. Fine painted rounded forms, clean beveled edges, warm upper-left sunlight, readable natural stone texture and warm wood. Sharp throughout: no blur, depth of field, photoreal noise, UI, letters, watermark, characters, animals, frame or margins. Preserve accurate camera and scale. Output fills 1254x1254, with central1024 core [115,115,1139,1139]; no rescaling. ";
const prompt=common+"\nPATCH "+p.tile+" "+name+": "+p.description;
const refs=[d+"/guides/"+name+"-positional.png",b+"/extension-20261011/south-two-layout-only.png","D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-detail-v1.png",b+"/"+p.anchor];
const request={prompt,referenced_image_paths:refs,transparent_background:false,referenceRoles:["exact positional target and existing unscaled neighbor strips","wider approved coordinate geometry only","approved daylight style and materials only","adjacent native scale/material only"]};
const startedAt=new Date().toISOString();
await tools.apply_patch("*** Begin Patch\n*** Add File: "+d+"/records/"+name+".prompt.txt\n+"+prompt.replaceAll("\n","\n+")+"\n*** Add File: "+d+"/records/"+name+".request.json\n+"+JSON.stringify(request,null,2).replaceAll("\n","\n+")+"\n*** Add File: "+d+"/records/"+name+".attempt.json\n+"+JSON.stringify({startedAt,tool:"image_gen__imagegen",actualModel:null,actualQuality:null,builtinOnly:true},null,2).replaceAll("\n","\n+")+"\n*** End Patch");
let result;
try { result=await tools.image_gen__imagegen({prompt,referenced_image_paths:refs,transparent_background:false}); }
catch(e){ const failure={startedAt,endedAt:new Date().toISOString(),error:String(e),actualModel:null,actualQuality:null};await tools.apply_patch("*** Begin Patch\n*** Add File: "+d+"/records/"+name+".failure.json\n+"+JSON.stringify(failure,null,2).replaceAll("\n","\n+")+"\n*** End Patch");text(failure);exit();}
store("lastImageResult",result);generatedImage(result);
const hint=result.output_hint||"",match=hint.match(/as (C:\\[^\n]+?\.png) by default/);
if(!match){text({error:"Generated path unavailable",output_hint:hint,receivedAt:new Date().toISOString()});exit();}
const path=match[1].replaceAll("\\","/");
const receipt={startedAt,receivedAt:new Date().toISOString(),tool:"image_gen__imagegen",output_hint:hint,originalFile:path,actualModel:null,actualQuality:null};
await tools.apply_patch("*** Begin Patch\n*** Add File: "+d+"/records/"+name+".receipt.json\n+"+JSON.stringify(receipt,null,2).replaceAll("\n","\n+")+"\n*** End Patch");
text(await tools.exec_command({cmd:"& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+b+"/extension-workflow.py' record "+p.tile+" "+p.r+" "+p.c+" "+v+" '"+path+"'",max_output_tokens:1200}));

