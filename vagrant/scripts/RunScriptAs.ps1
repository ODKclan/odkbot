#
# TODO
# https://www.tiraniddo.dev/2019/09/the-art-of-becoming-trustedinstaller.html
#

param (
    # User should be in the format of 'domain\user'
    # For example, for TrustedInstaller: NT SERVICE\TrustedInstaller
    [Parameter(Mandatory=$true)][string]$user,
    [Parameter(Mandatory=$true)][string]$script
 )

$scriptPath = Get-ChildItem $script | ForEach-Object { $_.FullName }
$task_name = "RunAsTITask"

$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-executionpolicy bypass -noprofile -file $scriptPath"
Register-ScheduledTask -TaskName $task_name -Action $action

$svc = New-Object -ComObject 'Schedule.Service'
$svc.Connect()
$folder = $svc.GetFolder('\')
$task = $folder.GetTask($task_name)
$task.RunEx($null, 0, 0, $user)

Unregister-ScheduledTask -TaskName $task_name -Confirm:$false
