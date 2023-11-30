$source_root ="F:\LicenseKeys"
$destination = "F:\LicenseKeysPrivate"
$copy_success = $true
try
{
    Copy-Item -Path $source_root\* -Destination $destination -recurse -Force
}
catch
{
    write-host "Copy falied, message: "$_.exception.message
    $copy_success = $false
}
if($copy_success)
{
    write-host "Copy succeeded, Removing source file."
    Get-ChildItem $source_root -Recurse | Where-Object {$_.Name -eq  "soapui.dat" -or $_.Name -eq  "soapui.key" -or  $_.Name -eq  "info.txt"} | Remove-Item -Path {$_.FullName} -Force
}

gci $source_root -Recurse -Directory | foreach {
   if((gci $_.FullName) -eq $null){$_.FullName; Remove-Item $_.FullName -Recurse }
}