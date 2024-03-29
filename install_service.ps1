#
# TODO
#

param (
    # Env should be either 'prod' or 'dev'
    [Parameter(Mandatory=$true)][ValidateSet("prod", "dev")][string]$env
)

# Check if the script is running as Administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Output "Not running as administrator!"
    exit(1)
}

# Make sure the script stop at the first error
$ErrorActionPreference = "Stop"

$root_folder = (Get-Location).ToString()
$nssm_exe = $root_folder + "\nssm.exe"

# Recover settings from the settings.json file
$s = Get-Content -Raw settings.json | ConvertFrom-Json
$service_name = $s.service_name
$nssm_version = $s.nssm_version

# Recover optional credentials for the windows service
try {
	$service_user = $s.service_user
	$service_password = $s.service_password
} catch {
	$service_user = $null
	$service_password = $null
}

# Check if nssm is installed; if not, download and put it in the root folder
If (-Not (Test-Path($nssm_exe)))
{
    Write-Output "nssm not found, installing"
    
    $nssm_temp_folder = $root_folder + "\temp"
    $nssm_url = "https://nssm.cc/release/nssm-" + $nssm_version + ".zip"
    $nssm_zip = $nssm_temp_folder + "\nssm.zip"
    $nssm_inner_exe = $nssm_temp_folder + "\nssm-" + $nssm_version + "\win64\nssm.exe"

    mkdir $nssm_temp_folder
    Invoke-WebRequest $nssm_url -OutFile $nssm_zip
    Expand-Archive $nssm_zip -DestinationPath $nssm_temp_folder
    mv $nssm_inner_exe $nssm_exe
    Remove-Item -Force -Recurse -Path $nssm_temp_folder
}

# Check if the service is already installed
$out = cmd /c "$nssm_exe status ODKBot" '2>&1'
if ($?) {
    $err_msg = "[ERR] Service '" + $service_name + "' already installed!"
    Write-Output $err_msg
    exit(1)
}
else {

    $msg = "Installing ODKBot in the '" + $env + "' environment..."
    Write-Output $msg

    # Find out the correct python paths with poetry
    $poetry_env_info = poetry env info | Select-String "Path"
    $python_path = ($poetry_env_info[0].ToString() -replace "Path:\ *","")
    $scripts_folder = $python_path + "\Scripts"

    # Install the service using nssm
    $service_cmd = $scripts_folder + "\python.exe"
    $service_args = $scripts_folder + "\odkbot_" + $env
    & $nssm_exe install $service_name $service_cmd $service_args
    & $nssm_exe set $service_name AppDirectory $root_folder
    & $nssm_exe set $service_name AppStdout $root_folder\log.txt
    & $nssm_exe set $service_name AppStderr $root_folder\log.txt
    & $nssm_exe set $service_name AppEnvironmentExtra PYTHONPATH=$python_path

    if ($service_user -and $service_password) {
        & $nssm_exe set $service_name ObjectName $service_user $service_password
    }

    Write-Output ""
    Write-Output "[OK] Installed!"
    Write-Output ""
    Write-Output "Starting the service..."
    Write-Output ""

    & $nssm_exe start $service_name

    Write-Output "[OK] ALL DONE!"
}
