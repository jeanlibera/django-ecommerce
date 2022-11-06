$BaseDir = $PSScriptRoot
Write-Host "Running from $BaseDir"

$currentFolder = Split-Path $BaseDir -Leaf
if ($currentFolder -eq "scripts") {
    $requirementsTxtRelativePath = "..\requirements.txt"
    Write-Host "This is the scripts folder. The relative path is $requirementsTxtRelativePath"
}

if (-not $requirementsTxtRelativePath) {
    throw "You must run this script from the scripts folder, or from the repo root."
}

pip --version

$installed = pip list

$foundDjango = $installed | Where-Object { $_ -like 'Django*' }

if (-not $foundDjango) {
    $joinedPath = Join-Path $BaseDir $requirementsTxtRelativePath
    Write-Host "The joined path is $joinedPath"
    $requirementsTxtFilePath = Resolve-Path $joinedPath
    Write-Host "The absolute path is $requirementsTxtFilePath"
    pip3 install -r $requirementsTxtFilePath
}

pip3 list