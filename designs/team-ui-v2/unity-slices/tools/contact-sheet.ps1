Add-Type -AssemblyName System.Drawing
$teamRoot=Split-Path -Parent $PSScriptRoot
$teamSheet=[Drawing.Bitmap]::new(1100,860)
$teamG=[Drawing.Graphics]::FromImage($teamSheet)
$teamG.Clear([Drawing.Color]::FromArgb(255,65,73,69))
$teamFont=[Drawing.Font]::new('Segoe UI',12)
$teamIndex=0
foreach($teamFile in Get-ChildItem -LiteralPath (Join-Path $teamRoot 'png') -Filter '*.png') {
 $teamPic=[Drawing.Image]::FromFile($teamFile.FullName)
 $teamX=($teamIndex%3)*365+10
 $teamY=[math]::Floor($teamIndex/3)*171+8
 $teamG.DrawString($teamFile.BaseName,$teamFont,[Drawing.Brushes]::White,$teamX,$teamY)
 $teamFactor=[math]::Min(345/$teamPic.Width,125/$teamPic.Height)
 $teamG.DrawImage($teamPic,[int]$teamX,[int]($teamY+31),[int]($teamPic.Width*$teamFactor),[int]($teamPic.Height*$teamFactor))
 $teamPic.Dispose()
 $teamIndex++
}
$teamSheet.Save((Join-Path $teamRoot 'contact-sheet.png'))
$teamFont.Dispose()
$teamG.Dispose()
$teamSheet.Dispose()