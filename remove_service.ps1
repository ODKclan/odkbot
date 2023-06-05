#
# TODO
#


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
    $out = (& $nssm_exe status ODKBot)
    
    # If the service is not stopped...
    if ( -Not ( $out -eq "SERVICE_STOPPED"))
    {
        # ... stop the service
        & $nssm_exe stop $service_name
    }

    & $nssm_exe remove $service_name confirm

    Write-Output ""
    Write-Output "[OK] UNINSTALLED!"

}
else {
    $err_msg = "[ERR] Service '" + $service_name + "' is not installed!"
    Write-Output $err_msg
    exit(1)
}
