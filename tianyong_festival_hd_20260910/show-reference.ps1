param([Parameter(Mandatory=$true)][string]$Path)
Add-Type -AssemblyName System.Drawing
$citySourceImage = [Drawing.Image]::FromFile($Path)
$cityViewImage = [Drawing.Bitmap]::new($citySourceImage,896,896)
$cityViewStream = [IO.MemoryStream]::new()
$cityViewEncoder = [Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
$cityViewParams = [Drawing.Imaging.EncoderParameters]::new(1)
$cityViewParams.Param[0] = [Drawing.Imaging.EncoderParameter]::new([Drawing.Imaging.Encoder]::Quality,[long]55)
$cityViewImage.Save($cityViewStream,$cityViewEncoder,$cityViewParams)
[Convert]::ToBase64String($cityViewStream.ToArray())
$cityViewImage.Dispose()
$citySourceImage.Dispose()
$cityViewStream.Dispose()
