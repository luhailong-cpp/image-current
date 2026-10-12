using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

// Executed inside the editor by Unity's official Unity_RunCommand MCP tool.
internal class CommandScript : IRunCommand
{
    const string Source = "E:/work/image/designs/attribute-panels/v2-painted/";
    const string Output = "E:/work/image/designs/attribute-panels/v2-painted/unity-slices/";
    const string Assets = "Assets/Resources/UI/Ugui/AttributesPaintedV2/";
    Texture2D character, pet;
    readonly List<Entry> entries = new List<Entry>();
    ExecutionResult report;
    [Serializable] class Entry
    {
        public string name, source, processing;
        public int width, height;
        public float[] sourceRectTopLeft;
        public float[] borderLeftBottomRightTop;
        public string resourcePath;
    }
    [Serializable] class Manifest
    {
        public string tool = "Unity official MCP / Unity_RunCommand";
        public string unityVersion;
        public string referenceCoordinates = "1440-wide reference preview, top-left origin; crop edges mapped to source native pixels";
        public string artwork = "Exact source crops; text-free controls reconstructed only from clean pixels of the approved artwork. No AI regeneration.";
        public Entry[] sprites;
    }
    // Historical crop recipe would overwrite both this repository and the client with pre-v10 skins.
    static void RejectHistoricalRebuild()
    {
        throw new InvalidOperationException("Historical UI slicing is disabled. Rebuild and publish with qdao_ui_style_recut_v10/README.md, then import the current manifest into Unity.");
    }
    public void Execute(ExecutionResult result)
    {
        RejectHistoricalRebuild();
        report = result;
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new Exception("Run in edit mode.");
        Directory.CreateDirectory(Output + "png");
        Directory.CreateDirectory(Output + "sources");
        Directory.CreateDirectory(Assets);
        character = Load(Source + "01-character-ui-no-affinity.png");
        pet = Load(Source + "02-pet-ui.png");
        File.Copy(Source + "01-character-ui-no-affinity.png", Output + "sources/character.png", true);
        File.Copy(Source + "02-pet-ui.png", Output + "sources/pet.png", true);
        try
        {
            Frame();
            Export("paper_tile", character, 862, 95, 280, 42, new Vector4(8,8,8,8));
            var title = Crop(character,477,0,488,82);
            ClearText(title, character,477,0, 636,38,175,34,620,831);
            Exterior(title, false); Exterior(title, true); LargestComponent(title);
            Save("title_plate",title,"character",new float[]{477,0,488,82},Vector4.zero,"Original title ornament and taiji; lettering replaced from clean jade pixels.");
            TitleInk("title_character",character,638,37,165,36);
            TitleInk("title_pet",pet,640,38,158,35);

            var primary=Crop(character,815,483,280,72);
            ClearText(primary,character,815,483,866,497,183,40,854,1059);
            Exterior(primary,true);
            Save("button_primary",primary,"character",new float[]{815,483,280,72},new Vector4(49,22,49,22),"Original gold scroll ends and jade plate; text removed from clean neighboring rows.");
            var secondary=Crop(character,575,488,202,61);
            ClearText(secondary,character,575,488,634,500,96,35,624,738);
            Exterior(secondary,true);
            Save("button_secondary",secondary,"character",new float[]{575,488,202,61},new Vector4(22,20,22,20),"Original ivory button frame; text removed.");
            var scheme=Crop(character,189,76,290,59);
            ClearText(scheme,character,189,76,277,89,110,33,259,404);
            ClearText(scheme,character,189,76,430,94,31,24,415,463);
            Exterior(scheme,true);
            Save("button_scheme",scheme,"character",new float[]{189,76,290,59},new Vector4(22,18,22,18),"Empty scheme dropdown plate; arrow supplied separately.");
            Export("dropdown_arrow",character,431,96,27,20,Vector4.zero,"Original fixed dropdown symbol.",true);
            var pool=Crop(character,527,91,208,53);
            ClearText(pool,character,527,91,584,102,97,34,573,695);
            Exterior(pool,true);
            Save("tab_horizontal",pool,"character",new float[]{527,91,208,53},new Vector4(20,18,20,18),"Empty jade attribute-points tab.");
            var section=Crop(pet,714,237,314,43);
            ClearText(section,pet,714,237,814,244,100,29,795,942);
            Exterior(section,true);
            Save("section_header",section,"pet",new float[]{714,237,314,43},new Vector4(31,15,31,15),"Ivory section heading with two gold studs; text-free.");

            VerticalTab("tab_vertical_normal",character,1260,108,68,95,false);
            VerticalTab("tab_vertical_selected",character,1260,207,72,95,true);
            Circle("close_button",character,1259,23,60,60);
            Export("close_tassel",character,1310,50,23,60,Vector4.zero,"Separate jade beads and red tassel.",false,false);
            Export("step_minus",character,685,221,49,49,Vector4.zero,"Fixed minus symbol.",true);
            Export("step_plus",character,1135,221,49,49,Vector4.zero,"Fixed plus symbol.",true);
            var step=Crop(character,685,221,49,49);
            ClearText(step,character,685,221,695,237,28,16,692,725);
            Exterior(step,true);
            Save("step_plate",step,"character",new float[]{685,221,49,49},new Vector4(11,11,11,11),"Empty square step button; use a native plus/minus label when desired.");
            Export("slider_track",character,876,235,241,17,new Vector4(5,5,5,5));
            Export("slider_fill",character,749,235,45,17,new Vector4(5,5,5,5));
            Circle("slider_thumb",character,800,225,38,38);
            Circle("notice_icon",character,531,164,35,35);
            var field=Crop(character,277,147,204,46);
            ClearText(field,character,277,147,289,155,102,30,286,430);
            Save("stat_field",field,"character",new float[]{277,147,204,46},new Vector4(9,9,9,9),"Empty value field, no reference numeric value.");
            Export("divider",character,496,67,25,493,Vector4.zero,"Original gold divider and ornaments; paper background removed.",true);

            Card("pet_card_normal",false);
            Card("pet_card_selected",true);
            // Use the existing approved transparent pet artwork for dynamic portraits: the
            // screenshot avatars contain baked levels and are unsuitable for runtime values.
            Portrait("portrait_lingyue", "E:/work/image/designs/attribute-panels/assets/lingyue.png");
            Portrait("portrait_hutuantuan", "E:/work/image/designs/attribute-panels/assets/hutuantuan.png");
            Portrait("portrait_fuxiaohu", "E:/work/image/designs/attribute-panels/assets/fuxiaohu.png");
            Portrait("portrait_yunjiujiu", "E:/work/image/designs/attribute-panels/assets/yunjiujiu.png");
            var portraitFrame=Crop(pet,184,114,100,86);
            for(int y=5;y<portraitFrame.height-5;y++) for(int x=5;x<portraitFrame.width-5;x++) portraitFrame.SetPixel(x,y,Color.clear);
            Exterior(portraitFrame,false); Exterior(portraitFrame,true);
            Save("portrait_frame",portraitFrame,"pet",new float[]{184,114,100,86},new Vector4(8,8,8,8),"Frame only. Portrait and level are separate runtime elements.");

            var manifest = MakeManifest();
            File.WriteAllText(Output+"manifest.json",manifest);
            File.WriteAllText(Assets+"manifest.json",manifest);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach(var e in entries)
            {
                var importer = (TextureImporter)AssetImporter.GetAtPath(Assets+e.name+".png");
                importer.textureType=TextureImporterType.Sprite;
                importer.spriteImportMode=SpriteImportMode.Single;
                importer.alphaIsTransparency=true;
                importer.mipmapEnabled=false;
                importer.isReadable=false;
                importer.sRGBTexture=true;
                importer.textureCompression=TextureImporterCompression.Uncompressed;
                importer.filterMode=FilterMode.Bilinear;
                importer.wrapMode=TextureWrapMode.Clamp;
                importer.spritePixelsPerUnit=100;
                var settings = new TextureImporterSettings(); importer.ReadTextureSettings(settings); settings.spriteMeshType=SpriteMeshType.FullRect; importer.SetTextureSettings(settings);
                importer.maxTextureSize=4096;
                importer.spriteBorder=new Vector4(e.borderLeftBottomRightTop[0],e.borderLeftBottomRightTop[1],e.borderLeftBottomRightTop[2],e.borderLeftBottomRightTop[3]);
                importer.SaveAndReimport();
                var sprite=AssetDatabase.LoadAssetAtPath<Sprite>(Assets+e.name+".png");
                if(sprite==null) throw new Exception("Sprite import failed: "+e.name);
                report.Log("SPRITE_OK|"+e.name+"|"+e.width+"x"+e.height+"|border="+sprite.border);
            }
            AssetDatabase.SaveAssets();
            report.Log("SLICE_COMPLETE|count="+entries.Count+"|"+Output);
        }
        finally { UnityEngine.Object.DestroyImmediate(character); UnityEngine.Object.DestroyImmediate(pet); }
    }
    Texture2D Load(string file) { var t=new Texture2D(2,2,TextureFormat.RGBA32,false); if(!t.LoadImage(File.ReadAllBytes(file))) throw new Exception(file); return t; }
    Texture2D Crop(Texture2D src,float x,float y,float w,float h)
    {
        float s=src.width/1440f; int xx=Mathf.RoundToInt(x*s), yy=Mathf.RoundToInt(y*s);
        int ww=Mathf.RoundToInt((x+w)*s)-xx, hh=Mathf.RoundToInt((y+h)*s)-yy;
        var t=new Texture2D(ww,hh,TextureFormat.RGBA32,false); t.SetPixels(src.GetPixels(xx,src.height-yy-hh,ww,hh)); return t;
    }
    void ClearText(Texture2D target,Texture2D src,float originX,float originY,float x,float y,float w,float h,float cleanLeft,float cleanRight)
    {
        float s=src.width/1440f;
        int sx=Mathf.RoundToInt(x*s), sy=Mathf.RoundToInt(y*s), ox=Mathf.RoundToInt(originX*s), oy=Mathf.RoundToInt(originY*s);
        int ww=Mathf.RoundToInt(w*s),hh=Mathf.RoundToInt(h*s);
        for(int j=0;j<hh;j++)
        {
            int sourceY=src.height-sy-j-1;
            Color a=src.GetPixel(Mathf.RoundToInt(cleanLeft*s),sourceY),b=src.GetPixel(Mathf.RoundToInt(cleanRight*s),sourceY);
            for(int i=0;i<ww;i++)
            {
                int tx=sx-ox+i,ty=target.height-(sy-oy+j)-1;
                if(tx>=0&&ty>=0&&tx<target.width&&ty<target.height) target.SetPixel(tx,ty,Color.Lerp(a,b,i/(float)Math.Max(1,ww-1)));
            }
        }
    }
    void Exterior(Texture2D t,bool paper)
    {
        var px=t.GetPixels(); int w=t.width,h=t.height; var seen=new bool[px.Length]; var q=new Queue<int>();
        for(int x=0;x<w;x++){q.Enqueue(x);q.Enqueue((h-1)*w+x);} for(int y=0;y<h;y++){q.Enqueue(y*w);q.Enqueue(y*w+w-1);}
        while(q.Count>0)
        {
            int k=q.Dequeue();if(seen[k])continue;seen[k]=true;var c=px[k];
            bool bg=c.a<.01f || (paper ? c.r>.53f && c.g>c.r*.91f && c.b>c.r*.77f : c.g>c.r*1.055f && c.b>c.r*.98f && c.r<.62f && c.g<.68f);
            if(!bg)continue;px[k]=Color.clear;int x=k%w,y=k/w;
            if(x>0)q.Enqueue(k-1);if(x<w-1)q.Enqueue(k+1);if(y>0)q.Enqueue(k-w);if(y<h-1)q.Enqueue(k+w);
        }
        t.SetPixels(px);
    }
    void Export(string name,Texture2D src,float x,float y,float w,float h,Vector4 border,string processing="Exact native-pixel crop.",bool paper=false,bool noMatte=true)
    {
        var t=Crop(src,x,y,w,h); if(paper||!noMatte)Exterior(t,paper);
        Save(name,t,src==character?"character":"pet",new float[]{x,y,w,h},border,processing);
    }
    void Save(string name,Texture2D t,string source,float[] rect,Vector4 border,string processing)
    {
        t.Apply();var bytes=t.EncodeToPNG(); File.WriteAllBytes(Output+"png/"+name+".png",bytes);File.WriteAllBytes(Assets+name+".png",bytes);
        float s=source=="pet"?pet.width/1440f:character.width/1440f;
        entries.Add(new Entry{name=name,source=source,width=t.width,height=t.height,sourceRectTopLeft=rect,processing=processing,
            borderLeftBottomRightTop=new float[]{Mathf.Round(border.x*s),Mathf.Round(border.y*s),Mathf.Round(border.z*s),Mathf.Round(border.w*s)},resourcePath="UI/Ugui/AttributesPaintedV2/"+name});
        UnityEngine.Object.DestroyImmediate(t);
    }
    void Blit(Texture2D dest,Texture2D src,int x,int y,int w,int h,bool mirror=false)
    {
        for(int j=0;j<h;j++) for(int i=0;i<w;i++)
        {
            float u=(i+.5f)/w;if(mirror)u=1-u;
            dest.SetPixel(x+i,dest.height-y-j-1,src.GetPixelBilinear(u,1-(j+.5f)/h));
        }
    }
    void Frame()
    {
        // Nine-slice reconstruction avoids any screenshot numbers or sliders in the paper.
        float s=character.width/1440f; var f=new Texture2D(Mathf.RoundToInt(1152*s),Mathf.RoundToInt(554*s),TextureFormat.RGBA32,false);
        f.SetPixels(new Color[f.width*f.height]);
        void Part(float sx,float sy,float sw,float sh,float dx,float dy,float dw,float dh,bool mirror=false)
        {var c=Crop(character,sx,sy,sw,sh);Blit(f,c,Mathf.RoundToInt(dx*s),Mathf.RoundToInt(dy*s),Mathf.RoundToInt(dw*s),Mathf.RoundToInt(dh*s),mirror);UnityEngine.Object.DestroyImmediate(c);}
        Part(862,95,280,42,25,26,1100,506);
        Part(193,42,280,24,45,10,1062,24);
        Part(195,555,995,29,48,525,1056,29);
        Part(137,100,33,423,9,67,33,437);
        Part(137,100,33,423,1110,67,33,437,true);
        Part(128,31,60,70,0,0,60,70);
        Part(128,31,60,70,1092,0,60,70,true);
        Part(128,533,64,51,0,503,64,51);
        Part(1210,533,70,51,1082,503,70,51);
        Exterior(f,false);
        Save("window_frame",f,"character",new float[]{128,31,1152,554},new Vector4(72,55,72,74),"Nine-part assembly from original gold corners/edges and blank paper; excludes all controls and data.");
    }
    void VerticalTab(string name,Texture2D src,float x,float y,float w,float h,bool selected)
    {
        var t=Crop(src,x,y,w,h);
        ClearText(t,src,x,y,x+17,y+16,32,h-32,x+11,x+w-16);
        Exterior(t,false);
        Save(name,t,"character",new float[]{x,y,w,h},new Vector4(10,16,18,16),"Original vertical tab; text removed; attach to the window's right edge.");
    }
    void Card(string name,bool selected)
    {
        float x=175,y=selected?105:208;var t=Crop(pet,x,y,313,101);float s=pet.width/1440f;
        var clean=selected?Crop(pet,292,117,177,7):Crop(character,862,95,280,42);
        Blit(t,clean,Mathf.RoundToInt(10*s),Mathf.RoundToInt(7*s),Mathf.RoundToInt(291*s),Mathf.RoundToInt(87*s));
        UnityEngine.Object.DestroyImmediate(clean);Exterior(t,true);
        Save(name,t,"pet",new float[]{x,y,313,101},new Vector4(16,16,16,16),"Original outer card border; cleared portrait, name, level and state; clean source-color interior.");
    }
    string MakeManifest()
    {
        string Q(string a) { return "\""+a.Replace("\\","\\\\").Replace("\"","\\\"")+"\""; }
        string A(float[] a) { return "["+string.Join(",",Array.ConvertAll(a,v=>v.ToString(System.Globalization.CultureInfo.InvariantCulture)))+"]"; }
        var b=new System.Text.StringBuilder();
        b.Append("{\"tool\":\"Unity official MCP / Unity_RunCommand\",\"unityVersion\":").Append(Q(Application.unityVersion));
        b.Append(",\"referenceCoordinates\":\"1440-wide top-left reference coordinates; each source is mapped independently to native pixels\",\"sprites\":[");
        for(int i=0;i<entries.Count;i++)
        {
            var e=entries[i];if(i>0)b.Append(",");
            float scale=e.source=="pet"?pet.width/1440f:character.width/1440f;
            var native=(float[])e.sourceRectTopLeft.Clone();
            if(e.source=="pet"||e.source=="character")
            {
                native[0]=Mathf.Round(e.sourceRectTopLeft[0]*scale);native[1]=Mathf.Round(e.sourceRectTopLeft[1]*scale);
                native[2]=Mathf.Round((e.sourceRectTopLeft[0]+e.sourceRectTopLeft[2])*scale)-native[0];
                native[3]=Mathf.Round((e.sourceRectTopLeft[1]+e.sourceRectTopLeft[3])*scale)-native[1];
            }
            b.Append("{\"name\":").Append(Q(e.name)).Append(",\"source\":").Append(Q(e.source));
            b.Append(",\"width\":").Append(e.width).Append(",\"height\":").Append(e.height);
            b.Append(",\"sourceRectTopLeft\":").Append(A(e.sourceRectTopLeft));
            b.Append(",\"sourceRectNativeTopLeft\":").Append(A(native));
            b.Append(",\"borderLeftBottomRightTop\":").Append(A(e.borderLeftBottomRightTop));
            b.Append(",\"processing\":").Append(Q(e.processing));
            b.Append(",\"resourcePath\":").Append(Q(e.resourcePath));
            b.Append(",\"containsDynamicText\":false,\"containsStaticTitle\":").Append(e.name=="title_character"||e.name=="title_pet"?"true":"false").Append("}");
        }
        return b.Append("]}").ToString();
    }
    void LargestComponent(Texture2D t)
    {
        var p=t.GetPixels();int w=t.width,h=t.height;var seen=new bool[p.Length];var largest=new List<int>();
        for(int start=0;start<p.Length;start++)
        {
            if(seen[start]||p[start].a<.02f)continue;
            var group=new List<int>();var q=new Queue<int>();q.Enqueue(start);seen[start]=true;
            while(q.Count>0)
            {
                int k=q.Dequeue();group.Add(k);int x=k%w,y=k/w;
                for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++)
                {
                    int xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=w||yy>=h)continue;int n=yy*w+xx;
                    if(seen[n]||p[n].a<.02f)continue;seen[n]=true;q.Enqueue(n);
                }
            }
            if(group.Count>largest.Count)largest=group;
        }
        var keep=new bool[p.Length];foreach(int k in largest)keep[k]=true;
        for(int i=0;i<p.Length;i++)if(!keep[i])p[i]=Color.clear;t.SetPixels(p);
    }
    void TitleInk(string name,Texture2D src,float x,float y,float w,float h)
    {
        var t=Crop(src,x,y,w,h);var p=t.GetPixels();
        for(int i=0;i<p.Length;i++)
        {
            var c=p[i];float alpha=Mathf.Clamp01((c.r-.40f)/.46f)*Mathf.Clamp01((c.g-.46f)/.32f);
            p[i]=new Color(1f,.97f,.85f,alpha);
        }
        t.SetPixels(p);Save(name,t,src==character?"character":"pet",new float[]{x,y,w,h},Vector4.zero,"Fixed title calligraphy extracted by luminance from jade background; transparent, no dynamic values.");
    }
    void Circle(string name,Texture2D src,float x,float y,float w,float h)
    {
        var t=Crop(src,x,y,w,h);
        for(int yy=0;yy<t.height;yy++)for(int xx=0;xx<t.width;xx++)
        {
            float d=Mathf.Sqrt(Mathf.Pow((xx+.5f-t.width*.5f)/(t.width*.5f),2)+Mathf.Pow((yy+.5f-t.height*.5f)/(t.height*.5f),2));
            var c=t.GetPixel(xx,yy);c.a=Mathf.Clamp01((.965f-d)*t.width*.5f);t.SetPixel(xx,yy,c);
        }
        Save(name,t,src==character?"character":"pet",new float[]{x,y,w,h},Vector4.zero,"Original fixed circular icon; geometric alpha excludes neighboring UI.");
    }
    void Portrait(string name,string path)
    {
        var src=Load(path);int minX=src.width,minY=src.height,maxX=0,maxY=0;
        var p=src.GetPixels(); for(int y=0;y<src.height;y++)for(int x=0;x<src.width;x++)if(p[y*src.width+x].a>.1f){minX=Math.Min(minX,x);maxX=Math.Max(maxX,x);minY=Math.Min(minY,y);maxY=Math.Max(maxY,y);}
        int span=Math.Max(1,Mathf.RoundToInt((maxY-minY+1)*.57f));int cx=(minX+maxX)/2;
        if(name=="portrait_lingyue") { span=Mathf.RoundToInt(src.width*.31f); cx=Mathf.RoundToInt(src.width*.427f); maxY=Mathf.RoundToInt(src.height*.705f); }
        var t=new Texture2D(160,160,TextureFormat.RGBA32,false);
        for(int y=0;y<160;y++)for(int x=0;x<160;x++)t.SetPixel(x,y,src.GetPixelBilinear((cx-span/2f+x*span/159f)/src.width,(maxY-span+y*span/159f)/src.height));
        Save(name,t,path,new float[]{cx-span/2f,src.height-maxY,span,span},Vector4.zero,"Head crop of existing approved transparent pet art, resampled to 160x160; no baked level.");
        UnityEngine.Object.DestroyImmediate(src);
    }
}
