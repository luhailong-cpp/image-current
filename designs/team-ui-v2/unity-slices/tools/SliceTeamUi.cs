using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;

internal class CommandScript : IRunCommand
{
    const string Source = "E:/work/image/designs/team-ui-v2/team-ui-v2.png";
    const string Package = "E:/work/image/designs/team-ui-v2/unity-slices/";
    const string AssetRoot = "Assets/Resources/UI/Ugui/TeamV2/";
    Texture2D source;
    float scale;
    ExecutionResult result;
    readonly List<Entry> entries = new List<Entry>();

    public void Execute(ExecutionResult execution)
    {
        result = execution;
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            throw new InvalidOperationException("Team slicing needs a stable editor in edit mode.");
        if (Path.GetFullPath(Application.dataPath).Replace('\\','/') != "E:/work/mmorpg-client/Assets")
            throw new InvalidOperationException("Unexpected project.");
        Directory.CreateDirectory(Package + "png");
        Directory.CreateDirectory(AssetRoot);
        source = new Texture2D(2, 2, TextureFormat.RGBA32, false);
        ImageConversion.LoadImage(source, File.ReadAllBytes(Source));
        scale = source.width / 1200f;
        try
        {
            MainFrame();
            Title();
            Section();
            Card("member_row", new Rect(121, 386, 529, 60), new Vector4(15,12,15,12));
            Card("application_card", new Rect(687, 148, 392, 123), new Vector4(17,15,17,15));
            Button("button_primary", new Rect(914,222,140,41), true);
            Button("button_secondary", new Rect(771,222,137,41), false);
            Disc("close", new Rect(1084,22,51,51), .98f, 0);
            Disc("portrait_frame", new Rect(149,326,57,57), .985f, .86f);
            Disc("empty_slot", new Rect(149,326,57,57), .98f, 0);
            Badge("badge_leader", new Rect(377,143,77,28), false);
            Badge("badge_self", new Rect(459,143,57,27), true);
            Disc("status_online", new Rect(559,145,19,20), .9f, 0);
            Disc("status_offline", new Rect(559,280,19,19), .9f, 0);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (var e in entries)
            {
                var importer = (TextureImporter)AssetImporter.GetAtPath(AssetRoot + e.name + ".png");
                result.RegisterObjectModification(importer);
                importer.textureType = TextureImporterType.Sprite;
                importer.spriteImportMode = SpriteImportMode.Single;
                importer.spritePixelsPerUnit = 100;
                importer.spriteBorder = new Vector4(e.border[0],e.border[1],e.border[2],e.border[3]);
                var settings = new TextureImporterSettings();
                importer.ReadTextureSettings(settings);
                settings.spriteMeshType = SpriteMeshType.FullRect;
                importer.SetTextureSettings(settings);
                importer.alphaIsTransparency = true;
                importer.mipmapEnabled = false;
                importer.isReadable = false;
                importer.npotScale = TextureImporterNPOTScale.None;
                importer.filterMode = FilterMode.Bilinear;
                importer.wrapMode = TextureWrapMode.Clamp;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.maxTextureSize = 4096;
                importer.SaveAndReimport();
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(AssetRoot + e.name + ".png");
                if (sprite == null || sprite.rect.width != e.width || sprite.rect.height != e.height)
                    throw new InvalidOperationException("Failed native-sized Sprite import: " + e.name);
            }
            var manifest = new Manifest {
                generatedAtUtc = DateTime.UtcNow.ToString("o"), unityVersion = Application.unityVersion,
                sourceWidth = source.width, sourceHeight = source.height,
                sourceSha256 = Hash(File.ReadAllBytes(Source)), sprites = entries.ToArray()
            };
            File.WriteAllText(Package + "manifest.json", Newtonsoft.Json.JsonConvert.SerializeObject(manifest, Newtonsoft.Json.Formatting.Indented));
            AssetDatabase.SaveAssets();
            result.Log("TEAM_SLICES_IMPORTED|count=" + entries.Count + "|source=" + source.width + "x" + source.height + "|root=" + AssetRoot);
        }
        finally { result.DestroyObject(source); }
    }

    int P(float v) => Mathf.RoundToInt(v * scale);
    Texture2D New(float w, float h)
    {
        var t = new Texture2D(P(w), P(h), TextureFormat.RGBA32, false);
        t.SetPixels(new Color[t.width*t.height]);
        return t;
    }
    Texture2D Crop(Rect r)
    {
        int x=P(r.x), top=P(r.y), w=P(r.xMax)-x, h=P(r.yMax)-top;
        var t=new Texture2D(w,h,TextureFormat.RGBA32,false);
        t.SetPixels(source.GetPixels(x,source.height-top-h,w,h));
        return t;
    }
    void Patch(Texture2D t, Rect from, Rect to, bool flipX=false, bool flipY=false)
    {
        int left=P(to.x), top=P(to.y), w=P(to.xMax)-left, h=P(to.yMax)-top;
        for(int y=0;y<h;y++) for(int x=0;x<w;x++)
        {
            int xx=left+x, yy=t.height-1-top-y;
            if(xx<0||yy<0||xx>=t.width||yy>=t.height) continue;
            float u=(x+.5f)/w, v=(y+.5f)/h;
            if(flipX) u=1-u; if(flipY) v=1-v;
            var c=source.GetPixelBilinear((from.x+from.width*u)*scale/source.width,
                1-(from.y+from.height*v)*scale/source.height);
            t.SetPixel(xx,yy,c);
        }
    }
    // Replace baked text only with clean pixels from the same approved artwork.
    void Fill(Texture2D t, Rect r, Rect clean) => Patch(t,clean,r);
    void Rounded(Texture2D t,float radius)
    {
        float rr=P(radius);
        for(int y=0;y<t.height;y++) for(int x=0;x<t.width;x++)
        {
            float dx=Mathf.Max(rr-(x+.5f),Mathf.Max(x+.5f-(t.width-rr),0));
            float dy=Mathf.Max(rr-(y+.5f),Mathf.Max(y+.5f-(t.height-rr),0));
            float a=Mathf.Clamp01(rr-Mathf.Sqrt(dx*dx+dy*dy)+.5f);
            var c=t.GetPixel(x,y); c.a*=a; t.SetPixel(x,y,c);
        }
    }
    void Polygon(Texture2D t, Vector2[] polygon)
    {
        // Four samples at native resolution leave a soft alpha boundary around original ornamentation.
        for(int y=0;y<t.height;y++) for(int x=0;x<t.width;x++)
        {
            int hits=0;
            for(int sy=0;sy<2;sy++) for(int sx=0;sx<2;sx++)
            {
                float px=(x+(sx+.5f)/2)/scale, py=(t.height-y-(sy+.5f)/2)/scale;
                bool inside=false;
                for(int i=0,j=polygon.Length-1;i<polygon.Length;j=i++)
                {
                    var a=polygon[i];var b=polygon[j];
                    if((a.y>py)!=(b.y>py) && px<(b.x-a.x)*(py-a.y)/(b.y-a.y)+a.x) inside=!inside;
                }
                if(inside)hits++;
            }
            var c=t.GetPixel(x,y);c.a*=hits*.25f;t.SetPixel(x,y,c);
        }
    }
    void Save(string name,Texture2D t,Rect sourceRect,Vector4 border,string process)
    {
        t.Apply();var bytes=t.EncodeToPNG();
        File.WriteAllBytes(Package+"png/"+name+".png",bytes);
        File.WriteAllBytes(AssetRoot+name+".png",bytes);
        entries.Add(new Entry{name=name,width=t.width,height=t.height,
            sourceRectTopLeft1200=new[]{sourceRect.x,sourceRect.y,sourceRect.width,sourceRect.height},
            border=new[]{(float)P(border.x),(float)P(border.y),(float)P(border.z),(float)P(border.w)},
            processing=process,sha256=Hash(bytes),resourcePath="UI/Ugui/TeamV2/"+name});
        result.DestroyObject(t);
    }
    void MainFrame()
    {
        var t=New(1034,438);
        Fill(t,new Rect(8,8,1018,422),new Rect(950,294,90,24));
        Patch(t,new Rect(122,51,200,17),new Rect(36,0,962,17));
        Patch(t,new Rect(322,477,180,14),new Rect(36,424,962,14));
        Patch(t,new Rect(81,182,22,137),new Rect(0,38,22,362));
        Patch(t,new Rect(1096,183,19,135),new Rect(1015,38,19,362));
        Patch(t,new Rect(81,51,45,48),new Rect(0,0,45,48));
        Patch(t,new Rect(81,51,45,48),new Rect(989,0,45,48),true);
        Patch(t,new Rect(81,51,45,48),new Rect(0,390,45,48),false,true);
        Patch(t,new Rect(81,51,45,48),new Rect(989,390,45,48),true,true);
        Rounded(t,22);
        Save("main_frame",t,new Rect(81,51,1034,438),new Vector4(47,49,47,49),
            "Nine-part reconstruction from original gold frame edges/corners and blank paper; all source UI/data excluded; corner outside alpha softened.");
    }
    void Title()
    {
        var r=new Rect(378,0,445,90);var t=Crop(r);
        Fill(t,new Rect(123,19,202,45),new Rect(474,23,24,39));
        // Remove the small baked subtitle so it can remain a native text label.
        Fill(t,new Rect(183,68,76,16),new Rect(542,70,16,11));
        Polygon(t,new[]{new Vector2(0,50),new Vector2(5,34),new Vector2(23,29),new Vector2(31,16),new Vector2(45,7),new Vector2(65,5),new Vector2(75,14),new Vector2(199,14),new Vector2(214,1),new Vector2(230,7),new Vector2(239,14),new Vector2(370,14),new Vector2(385,5),new Vector2(402,8),new Vector2(415,21),new Vector2(416,33),new Vector2(438,39),new Vector2(444,51),new Vector2(433,66),new Vector2(405,66),new Vector2(395,72),new Vector2(301,72),new Vector2(296,83),new Vector2(288,88),new Vector2(151,88),new Vector2(144,82),new Vector2(139,72),new Vector2(78,72),new Vector2(65,67),new Vector2(23,65),new Vector2(12,62)});
        Save("title_plate",t,r,new Vector4(88,18,88,22),"Approved jade cloud title; original title letters cleared with adjacent jade pixels; decorative silhouette alpha; native title remains editable.");
    }
    void Section()
    {
        var r=new Rect(107,75,269,45);var t=Crop(r);
        Fill(t,new Rect(47,8,158,27),new Rect(310,86,12,19));
        Polygon(t,new[]{new Vector2(0,21),new Vector2(8,9),new Vector2(20,2),new Vector2(36,2),new Vector2(48,7),new Vector2(217,7),new Vector2(235,17),new Vector2(248,18),new Vector2(264,23),new Vector2(269,32),new Vector2(257,41),new Vector2(235,42),new Vector2(40,42),new Vector2(22,44),new Vector2(9,39),new Vector2(3,30)});
        Save("section_plate",t,r,new Vector4(47,10,45,13),"Original section header; baked Chinese cleared with source jade; ornament silhouette isolated.");
    }
    void Card(string name,Rect r,Vector4 border)
    {
        var t=Crop(r);Fill(t,new Rect(6,5,r.width-12,r.height-10),new Rect(505,334,128,33));
        if (name == "application_card") Patch(t,new Rect(950,148,85,8),new Rect(16,0,r.width-32,8));
        Rounded(t,8);
        Save(name,t,r,border,"Original fine paper border; all portraits/data replaced by original blank paper; rounded exterior alpha.");
    }
    void Button(string name,Rect r,bool jade)
    {
        var t=Crop(r);
        Fill(t,new Rect(36,8,r.width-71,24),jade?new Rect(938,232,12,20):new Rect(798,232,10,20));
        Polygon(t,new[]{new Vector2(0,20),new Vector2(7,12),new Vector2(10,5),new Vector2(21,2),new Vector2(r.width-22,2),new Vector2(r.width-11,5),new Vector2(r.width-7,13),new Vector2(r.width,20),new Vector2(r.width-7,28),new Vector2(r.width-12,36),new Vector2(r.width-22,40),new Vector2(20,40),new Vector2(10,35),new Vector2(6,28)});
        Save(name,t,r,new Vector4(28,10,28,10),"Original gold-edged button; baked action removed using adjacent clean material; transparent silhouette; native button label.");
    }
    void Badge(string name,Rect r,bool jade)
    {
        var t=Crop(r);
        Fill(t,new Rect(12,5,r.width-24,r.height-10),jade?new Rect(465,150,8,13):new Rect(388,149,9,14));
        Rounded(t,10);
        Save(name,t,r,new Vector4(17,8,17,8),"Original role badge with baked role cleared using source material; native role label.");
    }
    void Disc(string name,Rect r,float outer,float inner)
    {
        var t=Crop(r);float radius=Mathf.Min(t.width,t.height)*.5f;
        for(int y=0;y<t.height;y++) for(int x=0;x<t.width;x++)
        {
            float d=Vector2.Distance(new Vector2(x+.5f,y+.5f),new Vector2(t.width*.5f,t.height*.5f));
            float a=Mathf.Clamp01(radius*outer-d+.5f);
            if(inner>0)a*=Mathf.Clamp01(d-radius*inner+.5f);
            var c=t.GetPixel(x,y);c.a*=a;t.SetPixel(x,y,c);
        }
        Save(name,t,r,Vector4.zero,inner>0?"Original circular gold rim isolated as transparent ring; source portrait excluded.":"Exact circular source crop with antialiased alpha; fixed symbol only, no player data.");
    }
    static string Hash(byte[] bytes) { using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant(); }
    [Serializable] class Entry {public string name,resourcePath,processing,sha256;public int width,height;public float[] sourceRectTopLeft1200,border;}
    [Serializable] class Manifest
    {
        public string tool="Unity official MCP / Unity_RunCommand",generatedAtUtc,unityVersion;
        public string source="E:/work/image/designs/team-ui-v2/team-ui-v2.png",sourceSha256;
        public int sourceWidth,sourceHeight;
        public string coordinates="Top-left coordinates on a 1200-wide reference; mapped to native 1931-wide pixels. No AI regeneration or upscaling. Text-free reconstruction uses clean source patches.";
        public Entry[] sprites;
    }
}