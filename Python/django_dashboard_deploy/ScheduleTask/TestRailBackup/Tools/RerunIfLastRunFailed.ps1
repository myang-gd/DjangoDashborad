
$done = Get-ChildItem F:\TestRailBackUp\SuitesBackup | Sort-Object LastWriteTime | select -last 1 | Get-ChildItem | where-object {$_.Name -eq 'Done.txt'}
$task_name = 'BackupTestRailSuite'

if($done -eq $null -and (Get-ScheduledTask -TaskName $task_name).State -ne "Running") {
	write-host "Rerun $task_name"
	Start-ScheduledTask -TaskName $task_name
} 

exit
