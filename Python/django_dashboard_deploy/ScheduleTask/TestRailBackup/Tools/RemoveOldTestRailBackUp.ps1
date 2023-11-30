
Set-Variable -Name count -Value ((Get-ChildItem F:\TestRailBackUp\SuitesBackup).Count -30)

if($count -gt 0) {
	foreach($folder in (Get-ChildItem F:\TestRailBackUp\SuitesBackup | Sort-Object LastWriteTime)) {
		if($count -gt 0){
			write-host "removing $folder"
			Remove-Item -Path $folder.FullName -Force -Recurse
			$count = $count -1
		} else {
			break
		}
	}
} 

exit
 