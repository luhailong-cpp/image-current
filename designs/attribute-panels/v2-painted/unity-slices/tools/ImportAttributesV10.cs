using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;

internal class CommandScript : IRunCommand
{
    const string Staged="E:/work/image/qdao_ui_style_recut_v10/staged/designs/attribute-panels/v2-painted/unity-slices/";
    const string Art="E:/work/image/designs/attribute-panels/v2-painted/unity-slices/";
    const string Dest="Assets/Resources/UI/Ugui/AttributesPaintedV2/";
    const string QA="E:/work/mmorpg-client/.codex-artifacts/attribute-ui-v10-20260911/";
    class Spec { public string name,sha; public int width,height; public UnityEngine.Vector4 border; }
    string Hash(string file) { using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(file))).Replace("-","").ToLowerInvariant(); }
    void Backup(string file,string area)
    {
        if(!File.Exists(file))return;string dir=QA+"backup-before-v10/"+area+"/";Directory.CreateDirectory(dir);
        string target=dir+Path.GetFileName(file);if(!File.Exists(target))File.Copy(file,target);
    }
    public void Execute(ExecutionResult result)
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode||EditorApplication.isCompiling)throw new Exception("Expected ready editor in edit mode.");
        if(Path.GetFullPath(Application.dataPath).Replace('\\','/').TrimEnd('/')!="E:/work/mmorpg-client/Assets")throw new Exception("Wrong project.");
        var specs=new Spec[]{new Spec { name="window_frame", sha="7aba0f0d6834a5f70eeb29c4308d57f171594e3e9894921569fdd6a602720663", width=1546, height=743, border=new UnityEngine.Vector4(97f,74f,97f,99f) },
new Spec { name="paper_tile", sha="1e49b07c8c1fd508ab4798d3b68c28dd827b2421afa6438a15f6c81175d26992", width=375, height=57, border=new UnityEngine.Vector4(11f,11f,11f,11f) },
new Spec { name="title_plate", sha="b9a01536ef28813328ea538341925106c0b7fe84fe910af49e9b93abef8c96a8", width=655, height=110, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="title_character", sha="fbadd8f375baced08becff9e6f100854f331dc1bb36029a7251e7ebd23407f2b", width=221, height=48, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="title_pet", sha="9da8791da335ece5dcbc2665b316944c2dd7fb4910e1eec2ddd1d93101099bc8", width=212, height=47, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="button_primary", sha="e9e5ada2210d1f57741a3955b7166002c0a41142a92a40f089125678c1c5a24e", width=376, height=97, border=new UnityEngine.Vector4(66f,30f,66f,30f) },
new Spec { name="button_secondary", sha="96fe5fe53fb30def6e5ee8931179911cfd6a21be1d092359f69d5941cb2999f5", width=271, height=82, border=new UnityEngine.Vector4(30f,27f,30f,27f) },
new Spec { name="button_scheme", sha="451990db93a0bba54cf0dc7856196c215ba8cc348672b00bf107a464505f5a32", width=389, height=79, border=new UnityEngine.Vector4(30f,24f,30f,24f) },
new Spec { name="dropdown_arrow", sha="3e7782d11939e08db08a68ac58e750394ba59f5dc97b74779b8cfc82b239172e", width=36, height=27, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="tab_horizontal", sha="c5dda5483942a74e0a831f853b9ee5c10ffe46c778960b188fb909617a6aaa65", width=279, height=71, border=new UnityEngine.Vector4(27f,24f,27f,24f) },
new Spec { name="section_header", sha="98dc6c9898d54286999b7be1010e94019582b7232a24df8cfc714ecebbc0fbda", width=422, height=57, border=new UnityEngine.Vector4(42f,20f,42f,20f) },
new Spec { name="tab_vertical_normal", sha="1e2f8ff206c9e208c206ea94aab3befe965aefae05546a9b5eedfa1275b1f7bc", width=92, height=127, border=new UnityEngine.Vector4(13f,21f,24f,21f) },
new Spec { name="tab_vertical_selected", sha="67ac18f09129d07a0b52aabdf90e34ae62f3c16e7fb7b8730f10713d2f5f5fb9", width=97, height=127, border=new UnityEngine.Vector4(13f,21f,24f,21f) },
new Spec { name="close_button", sha="7194b5d71bf37d999e16f28b5ed7da55ecd9d674b438254ea134a9283b498339", width=81, height=80, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="close_tassel", sha="20abbf34762758034e2c87749111a3c06dedf74d013cadc7aa997502517776a5", width=30, height=81, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="step_minus", sha="e788695456c8d65c590bf0b35fbfc027b7baaccb4e42ae39983fb72e529feaa6", width=66, height=65, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="step_plus", sha="cc5a01c6224ab1d2c5b29e448ccd8a18d4fd30d431dd068c279d598f2237e71f", width=66, height=65, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="step_plate", sha="e90a79a03cfc48f8716c57c39bfeb922e3d3f4c052642c8d1c1b90c5b5358033", width=66, height=65, border=new UnityEngine.Vector4(15f,15f,15f,15f) },
new Spec { name="slider_track", sha="f35d337bd76d4481db6636aba64172c0d86621fbddc043f3af1c6f7e1ae9697f", width=324, height=23, border=new UnityEngine.Vector4(7f,7f,7f,7f) },
new Spec { name="slider_fill", sha="6613b6f5a4ac1d03e1e92082efc92fd61c339b98d04523ac2a289bdac75acf0f", width=60, height=23, border=new UnityEngine.Vector4(7f,7f,7f,7f) },
new Spec { name="slider_thumb", sha="9cab35f55f601663f5f0020600e5815b81de09e303262ddda4be2571207d2aef", width=51, height=51, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="notice_icon", sha="cbf6754ffe44bbbbf2c6fc31e27153e22b07debcd9072ac55188ed388aff510b", width=47, height=47, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="stat_field", sha="c175e6e627776393cb7371df797ebe88bdfa0916769829269089ee22ac9b8c46", width=273, height=62, border=new UnityEngine.Vector4(12f,12f,12f,12f) },
new Spec { name="divider", sha="628ddbfc48a51b5c7e0375ad4fd25d734e559c051c5b69b41963fc9c3a40bbe3", width=34, height=661, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="pet_card_normal", sha="ad58f542cacdea60ef0e9bbae2d40819c7fa39a8a4ebedc1fc46d8d675ee27fa", width=419, height=135, border=new UnityEngine.Vector4(21f,21f,21f,21f) },
new Spec { name="pet_card_selected", sha="f8ad6f7d944af4f7c5b5c8daeb2d62ec45f977e579656fee7759d99f7b793260", width=419, height=135, border=new UnityEngine.Vector4(21f,21f,21f,21f) },
new Spec { name="portrait_lingyue", sha="f0506e1ea727f492ab9b316ada94794d96fa7a78031861a7c2639868778172ae", width=160, height=160, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="portrait_hutuantuan", sha="dd62e68f9ebce2bf9c53c2008a1322dfcb016f7fd82e41bff7be323646323c81", width=160, height=160, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="portrait_fuxiaohu", sha="e20c92128ec0ab1156c61ed0344fa386f1ab0a9f714eb2612585d03caeb6b9df", width=160, height=160, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="portrait_yunjiujiu", sha="5fa824d73f866a24475dd28cc849261fcdcdf0cc966784e1fbd9824fc2028d86", width=160, height=160, border=new UnityEngine.Vector4(0f,0f,0f,0f) },
new Spec { name="portrait_frame", sha="fab13d1b2dd5bef7260209fc22fcbd15c9e5a835b83d359ed0d3b5b9d5a0e4a0", width=134, height=115, border=new UnityEngine.Vector4(11f,11f,11f,11f) }};
        var guids=new Dictionary<string,string>();
        // Validate the entire frozen input set before publishing any file.
        foreach(var s in specs)
        {
            if(Hash(Staged+"png/"+s.name+".png")!=s.sha)throw new Exception("Staged input changed: "+s.name);
            var probe=new Texture2D(2,2);try
            {
                if(!probe.LoadImage(File.ReadAllBytes(Staged+"png/"+s.name+".png"))||probe.width!=s.width||probe.height!=s.height)throw new Exception("Bad dimensions: "+s.name);
                if(s.border.x+s.border.z>=s.width||s.border.y+s.border.w>=s.height)throw new Exception("Bad border: "+s.name);
            }finally{UnityEngine.Object.DestroyImmediate(probe);}
            guids[s.name]=AssetDatabase.AssetPathToGUID(Dest+s.name+".png");
        }
        Directory.CreateDirectory(QA);Directory.CreateDirectory(Art+"png");Directory.CreateDirectory(Dest);
        int updated=0;
        foreach(var s in specs)
        {
            string file=s.name+".png";
            Backup(Art+"png/"+file,"art");Backup(Dest+file,"client");Backup(Dest+file+".meta","meta");
            if(!File.Exists(Dest+file)||Hash(Dest+file)!=s.sha)updated++;
            File.Copy(Staged+"png/"+file,Art+"png/"+file,true);
            File.Copy(Staged+"png/"+file,Dest+file,true);
        }
        foreach(string name in new[]{"manifest.json","file-validation.json","sprite-overview.png","nine-slice-review.png","frame-fields-review.png","fixed-glyph-title-review.png","character-layout-review.png","pet-layout-review.png"})
        {Backup(Art+name,"art-documents");File.Copy(Staged+name,Art+name,true);}
        Backup(Dest+"manifest.json","client-documents");File.Copy(Staged+"manifest.json",Dest+"manifest.json",true);
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var records=new List<string>();
        foreach(var s in specs)
        {
            var path=Dest+s.name+".png";var importer=(TextureImporter)AssetImporter.GetAtPath(path);
            importer.textureType=TextureImporterType.Sprite;importer.spriteImportMode=SpriteImportMode.Single;
            importer.alphaIsTransparency=true;importer.mipmapEnabled=false;importer.isReadable=false;importer.sRGBTexture=true;
            importer.textureCompression=TextureImporterCompression.Uncompressed;importer.filterMode=FilterMode.Bilinear;importer.wrapMode=TextureWrapMode.Clamp;
            importer.spritePixelsPerUnit=100;importer.maxTextureSize=4096;importer.spriteBorder=s.border;
            var settings=new TextureImporterSettings();importer.ReadTextureSettings(settings);settings.spriteMeshType=SpriteMeshType.FullRect;importer.SetTextureSettings(settings);
            importer.SaveAndReimport();
            var sprite=AssetDatabase.LoadAssetAtPath<Sprite>(path);
            if(sprite==null||sprite.rect.width!=s.width||sprite.rect.height!=s.height||sprite.border!=s.border)throw new Exception("Sprite import failed: "+s.name);
            string guid=AssetDatabase.AssetPathToGUID(path);
            if(!string.IsNullOrEmpty(guids[s.name])&&guid!=guids[s.name])throw new Exception("GUID changed: "+s.name);
            if(Hash(path)!=s.sha||Hash(Art+"png/"+s.name+".png")!=s.sha)throw new Exception("Published bytes differ: "+s.name);
            if(Resources.Load<Sprite>("UI/Ugui/AttributesPaintedV2/"+s.name)==null)throw new Exception("Resource failed: "+s.name);
            records.Add("{\"name\":\""+s.name+"\",\"sha256\":\""+s.sha+"\",\"guid\":\""+guid+"\",\"width\":"+s.width+",\"height\":"+s.height+"}");
        }
        AssetDatabase.SaveAssets();
        string json="{\"status\":\"passed\",\"version\":\"v10\",\"tool\":\"Unity official relay MCP / Unity_RunCommand\",\"unityVersion\":\""+Application.unityVersion+"\",\"utc\":\""+DateTime.UtcNow.ToString("o")+"\",\"sprites\":31,\"updatedClientImages\":"+updated+",\"guidsPreserved\":true,\"resourceLoadPassed\":true,\"dimensionsAndBordersPassed\":true,\"artAndClientHashesMatch\":true,\"manifestSha256\":\""+Hash(Dest+"manifest.json")+"\",\"files\":["+string.Join(",",records)+"]}";
        File.WriteAllText(QA+"import-validation.json",json);File.WriteAllText(Art+"unity-import-v10.json",json);
        result.Log("V10_IMPORT_PASS|31 sprites|updated="+updated+"|GUIDs preserved|art+client hashes verified|"+QA);
    }
}