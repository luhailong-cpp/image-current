using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
internal class CommandScript : IRunCommand
{
 public void Execute(ExecutionResult result)
 {
  if(EditorApplication.isPlayingOrWillChangePlaymode||EditorApplication.isCompiling)throw new System.InvalidOperationException("Stable edit mode required");
  const string png="E:/work/image/designs/team-ui-v2/unity-slices/png/title_plate.png";
  const string asset="Assets/Resources/UI/Ugui/TeamV2/title_plate.png";
  var t=new Texture2D(2,2,TextureFormat.RGBA32,false);
  ImageConversion.LoadImage(t,File.ReadAllBytes(png));
  var pixels=t.GetPixels32(); var seen=new bool[pixels.Length]; var q=new Queue<int>();
  for(int i=0;i<pixels.Length;i++)if(pixels[i].a==0){q.Enqueue(i);seen[i]=true;}
  int cleared=0;
  while(q.Count>0)
  {
   int k=q.Dequeue(),x=k%t.width,y=k/t.width;
   for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++)
   {
    int xx=x+dx,yy=y+dy;
    if(xx<0||yy<0||xx>=t.width||yy>=t.height)continue;
    int n=yy*t.width+xx;if(seen[n])continue;
    var c=pixels[n];
    bool sky=c.b>165&&c.b>c.r-14&&c.b>c.g-17;
    if(!sky)continue;
    seen[n]=true;q.Enqueue(n);c.a=0;pixels[n]=c;cleared++;
   }
  }
  t.SetPixels32(pixels);t.Apply();var bytes=t.EncodeToPNG();
  File.WriteAllBytes(png,bytes);File.WriteAllBytes(asset,bytes);
  result.DestroyObject(t);
  AssetDatabase.ImportAsset(asset,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
  result.Log("TEAM_TITLE_ALPHA_CLEANED|pixels="+cleared);
 }
}