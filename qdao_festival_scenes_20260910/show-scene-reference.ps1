param([Parameter(Mandatory=$true)][string]$Path)
Add-Type -AssemblyName System.Drawing
$sceneSource = [Drawing.Image]::FromFile($Path)
$sceneFactor = [Math]::Min(1024.0/$sceneSource.Width,768.0/$sceneSource.Height)
$sceneBitmap = [Drawing.Bitmap]::new($sceneSource,[int]($sceneSource.Width*$sceneFactor),[int]($sceneSource.Height*$sceneFactor))
$sceneStream = [IO.MemoryStream]::new()
$sceneCodec = [Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
$sceneParams = [Drawing.Imaging.EncoderParameters]::new(1)
$sceneParams.Param[0] = [Drawing.Imaging.EncoderParameter]::new([Drawing.Imaging.Encoder]::Quality,[long]60)
$sceneBitmap.Save($sceneStream,$sceneCodec,$sceneParams)
[Convert]::ToBase64String($sceneStream.ToArray())
$sceneBitmap.Dispose()
$sceneSource.Dispose()
$sceneStream.Dispose()
