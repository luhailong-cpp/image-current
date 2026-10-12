using System;
using System.IO;
using UnityEngine;
using UnityEngine.UI;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

internal class CommandScript : IRunCommand
{
    const string Root="Assets/Resources/UI/Ugui/AttributesPaintedV2/";
    const string Output="E:/work/image/designs/attribute-panels/v2-painted/unity-slices/";
    public void Execute(ExecutionResult result)
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Edit mode required.");
        var guids=AssetDatabase.FindAssets("t:Sprite",new[]{Root.TrimEnd('/')});
        if(guids.Length!=31)throw new Exception("Expected 31 Sprite assets, found "+guids.Length);
        foreach(var guid in guids)
        {
            var path=AssetDatabase.GUIDToAssetPath(guid);var sprite=AssetDatabase.LoadAssetAtPath<Sprite>(path);
            var imp=(TextureImporter)AssetImporter.GetAtPath(path); var b=sprite.border;
            if(imp.textureType!=TextureImporterType.Sprite||imp.mipmapEnabled||imp.textureCompression!=TextureImporterCompression.Uncompressed)throw new Exception("Import settings: "+path);
            if(b.x+b.z>=sprite.rect.width||b.y+b.w>=sprite.rect.height)throw new Exception("Invalid border: "+path);
            if(Resources.Load<Sprite>("UI/Ugui/AttributesPaintedV2/"+sprite.name)==null)throw new Exception("Resource load failed: "+path);
        }
        var previousScene=SceneManager.GetActiveScene();
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
        SceneManager.SetActiveScene(scene);var previousTarget=RenderTexture.active;
        RenderTexture target=null;Texture2D pixels=null;Camera camera=null;
        try
        {
            camera=new GameObject("Slice QA Camera",typeof(Camera)).GetComponent<Camera>();
            result.RegisterObjectCreation(camera.gameObject);
            camera.enabled=false;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.16f,.23f,.20f);
            camera.transform.position=new UnityEngine.Vector3(0,0,-10);camera.orthographic=true;camera.nearClipPlane=.1f;camera.farClipPlane=100;
            camera.cullingMask=1<<29;
            target=new RenderTexture(1440,1000,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);camera.targetTexture=target;
            var go=new GameObject("Attribute Slice QA",typeof(RectTransform),typeof(Canvas),typeof(CanvasScaler));result.RegisterObjectCreation(go);
            var canvas=go.GetComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=camera;canvas.planeDistance=1;
            var scaler=go.GetComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1440,1000);scaler.matchWidthOrHeight=.5f;
            var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            RectTransform Rect(string name,UnityEngine.Transform parent,float x,float y,float w,float h)
            {
                var r=new GameObject(name,typeof(RectTransform)).GetComponent<RectTransform>();r.SetParent(parent,false);r.gameObject.layer=29;
                r.anchorMin=r.anchorMax=new Vector2(0,1);r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(x,-y);r.sizeDelta=new Vector2(w,h);return r;
            }
            void Label(string name,string text,float x,float y,float w,float h,int size=18)
            {var t=Rect(name,go.transform,x,y,w,h).gameObject.AddComponent<Text>();t.font=font;t.fontSize=size;t.text=text;t.color=new Color(.96f,.94f,.84f);t.raycastTarget=false;}
            void Art(string name,float x,float y,float w,float h)
            {
                var im=Rect(name,go.transform,x,y,w,h).gameObject.AddComponent<UnityEngine.UI.Image>();im.sprite=AssetDatabase.LoadAssetAtPath<Sprite>(Root+name+".png");
                im.color=Color.white;im.raycastTarget=false;im.type=im.sprite.border.sqrMagnitude>0?UnityEngine.UI.Image.Type.Sliced:UnityEngine.UI.Image.Type.Simple;
                im.preserveAspect=im.type==UnityEngine.UI.Image.Type.Simple;im.pixelsPerUnitMultiplier=Mathf.Max(1,im.sprite.rect.height/h);
            }
            Label("Heading","PAINTED ATTRIBUTE UI / UNITY SPRITE VERIFICATION",32,18,1350,40,26);
            Art("window_frame",30,104,656,345);Art("title_plate",179,70,380,64);Art("title_character",303,97,140,32);
            Art("window_frame",742,104,656,345);Art("title_plate",887,70,380,64);Art("title_pet",1011,97,140,32);
            Art("button_scheme",64,164,240,52);Art("dropdown_arrow",266,180,26,20);
            Art("stat_field",64,238,240,50);Art("stat_field",64,312,240,50);
            Art("tab_horizontal",342,164,260,52);Art("slider_track",342,267,248,14);Art("slider_fill",342,267,136,14);Art("slider_thumb",460,255,36,36);
            Art("step_minus",310,255,30,30);Art("step_plus",600,255,30,30);
            Art("button_primary",360,348,248,66);Art("button_secondary",76,364,220,52);
            Art("close_button",650,98,50,50);Art("close_button",1362,98,50,50);
            Art("tab_vertical_normal",680,173,50,76);Art("tab_vertical_selected",680,250,50,76);
            string[] pets={"lingyue","hutuantuan","fuxiaohu","yunjiujiu"};
            for(int i=0;i<4;i++){Art(i==0?"pet_card_selected":"pet_card_normal",778,155+i*66,275,60);Art("portrait_"+pets[i],794,158+i*66,52,52);Art("portrait_frame",790,156+i*66,60,55);}
            Art("section_header",1080,157,264,44);Art("stat_field",1080,225,245,42);Art("step_minus",1080,290,42,42);Art("stat_field",1125,290,148,42);Art("step_plus",1277,290,42,42);
            Art("button_primary",1080,346,246,64);
            Label("ResizeHeading","NINE-SLICE WIDTH CHECK / 180px / 300px / 500px",32,485,1350,32,22);
            string[] buttons={"button_primary","button_secondary","button_scheme","pet_card_selected","tab_horizontal"};
            for(int i=0;i<buttons.Length;i++){float y=535+i*86;Label("N"+i,buttons[i],32,y+12,240,32);Art(buttons[i],280,y,180,62);Art(buttons[i],490,y,300,62);Art(buttons[i],825,y,500,62);}
            foreach(var t in go.GetComponentsInChildren<UnityEngine.Transform>(true))t.gameObject.layer=29;
            Canvas.ForceUpdateCanvases();camera.Render();RenderTexture.active=target;
            pixels=new Texture2D(1440,1000,TextureFormat.RGB24,false);pixels.ReadPixels(new Rect(0,0,1440,1000),0,0);pixels.Apply();
            File.WriteAllBytes(Output+"unity-sprite-preview.png",pixels.EncodeToPNG());
            File.WriteAllText(Output+"unity-validation.json","{\"tool\":\"Unity official MCP / Unity_RunCommand\",\"unityVersion\":\""+Application.unityVersion+"\",\"sprites\":31,\"resourceLoadPassed\":true,\"importSettingsPassed\":true,\"bordersPassed\":true,\"rendered\":\"unity-sprite-preview.png\",\"scope\":\"Isolated native UGUI sprite preview; runtime panel integration belongs to the parallel UI task\"}");
            result.Log("QA_PASS|31 sprites|Resources.Load=31|9-slice borders valid|Native UGUI screenshot="+Output+"unity-sprite-preview.png");
        }
        finally
        {
            RenderTexture.active=previousTarget;if(camera!=null)camera.targetTexture=null;
            if(pixels!=null)UnityEngine.Object.DestroyImmediate(pixels);if(target!=null){target.Release();UnityEngine.Object.DestroyImmediate(target);}
            if(previousScene.IsValid()&&previousScene.isLoaded)SceneManager.SetActiveScene(previousScene);
            if(scene.IsValid()&&scene.isLoaded)EditorSceneManager.CloseScene(scene,true);
        }
    }
}
