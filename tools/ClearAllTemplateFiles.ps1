# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

$ErrorActionPreference = 'Stop'
$exitCode = 0
$currentTarget = 'repository root'
$wslUncPattern = '^\\\\wsl(\.localhost|\$)\\(?<distro>[^\\]+)\\(?<rest>.*)$'

function ConvertTo-WslPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $match = [regex]::Match(
        $Path,
        $script:wslUncPattern,
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if (-not $match.Success) {
        throw "Cannot convert non-WSL UNC path to a Linux path: '$Path'"
    }

    return '/' + ($match.Groups['rest'].Value -replace '\\', '/')
}

function Invoke-WslDelete {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Directory', 'File')]
        [string]$TargetType
    )

    $script:currentTarget = $Path
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    if (-not [System.IO.Path]::IsPathRooted($Path)) {
        throw "Refusing to delete a non-absolute path: '$Path'"
    }

    Write-Host "Removing: $Path"
    $linuxPath = ConvertTo-WslPath -Path $Path
    if ($TargetType -eq 'Directory') {
        $wslArguments = @('-d', $script:wslDistro, '--', 'rm', '-rf', '--', $linuxPath)
    }
    else {
        $wslArguments = @('-d', $script:wslDistro, '--', 'rm', '-f', '--', $linuxPath)
    }

    & wsl.exe @wslArguments
    $wslExitCode = $LASTEXITCODE
    $targetStillExists = Test-Path -LiteralPath $Path
    if ($wslExitCode -eq 0 -or -not $targetStillExists) {
        return
    }

    throw "wsl.exe failed to remove '$Path' (exit code $wslExitCode)."
}

function Invoke-WslPatternDelete {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Description,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Directory', 'File')]
        [string]$TargetType,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $script:currentTarget = $Description
    Write-Host "Removing: $Description"

    if ($TargetType -eq 'Directory') {
        $wslArguments = @(
            '-d', $script:wslDistro, '--', 'find', $script:wslRepositoryRoot,
            '-type', 'd', '-name', $Name, '-prune',
            '-exec', 'rm', '-rf', '--', '{}', '+'
        )
    }
    else {
        $wslArguments = @(
            '-d', $script:wslDistro, '--', 'find', $script:wslRepositoryRoot,
            '-type', 'f', '-name', $Name,
            '-exec', 'rm', '-f', '--', '{}', '+'
        )
    }

    & wsl.exe @wslArguments
    $wslExitCode = $LASTEXITCODE

    # A pattern has no single path for Test-Path, so verify it with a second
    # Linux find. Fixed targets below are verified with Test-Path.
    if ($TargetType -eq 'Directory') {
        $findType = 'd'
    }
    else {
        $findType = 'f'
    }
    $verificationArguments = @(
        '-d', $script:wslDistro, '--', 'find', $script:wslRepositoryRoot,
        '-type', $findType,
        '-name', $Name, '-print', '-quit'
    )
    $remainingTarget = @(& wsl.exe @verificationArguments)
    $verificationExitCode = $LASTEXITCODE
    $verifiedAbsent = $verificationExitCode -eq 0 -and $remainingTarget.Count -eq 0

    if ($wslExitCode -eq 0 -or $verifiedAbsent) {
        return
    }

    throw "wsl.exe failed to remove '$Description' (exit code $wslExitCode)."
}

function Invoke-CmdDelete {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Directory', 'File')]
        [string]$TargetType
    )

    $script:currentTarget = $Path
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    if (-not [System.IO.Path]::IsPathRooted($Path)) {
        throw "Refusing to delete a non-absolute path: '$Path'"
    }

    Write-Host "Removing: $Path"

    # Keep the path out of cmd.exe's command text. Expansion is not recursive,
    # so characters such as %, &, and spaces in the absolute path stay quoted.
    $environmentVariableName = 'ICONTROLLER_CLEAN_TARGET'
    $previousTarget = [System.Environment]::GetEnvironmentVariable(
        $environmentVariableName,
        [System.EnvironmentVariableTarget]::Process
    )

    try {
        [System.Environment]::SetEnvironmentVariable(
            $environmentVariableName,
            $Path,
            [System.EnvironmentVariableTarget]::Process
        )

        if ($TargetType -eq 'Directory') {
            $command = 'rd /s /q "%ICONTROLLER_CLEAN_TARGET%"'
        }
        else {
            $command = 'del /f /q "%ICONTROLLER_CLEAN_TARGET%"'
        }

        & $env:ComSpec /d /v:off /s /c $command
        $cmdExitCode = $LASTEXITCODE
    }
    finally {
        [System.Environment]::SetEnvironmentVariable(
            $environmentVariableName,
            $previousTarget,
            [System.EnvironmentVariableTarget]::Process
        )
    }

    $targetStillExists = Test-Path -LiteralPath $Path
    if ($cmdExitCode -eq 0 -or -not $targetStillExists) {
        return
    }

    throw "cmd.exe failed to remove '$Path' (exit code $cmdExitCode)."
}

function Remove-DirectoryIfExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ($script:isWslUncPath) {
        Invoke-WslDelete -Path $Path -TargetType 'Directory'
    }
    else {
        Invoke-CmdDelete -Path $Path -TargetType 'Directory'
    }
}

function Remove-FileIfExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ($script:isWslUncPath) {
        Invoke-WslDelete -Path $Path -TargetType 'File'
    }
    else {
        Invoke-CmdDelete -Path $Path -TargetType 'File'
    }
}

try {
    $repositoryRoot = (Get-Item -LiteralPath $PSScriptRoot).Parent.FullName
    $repositoryMatch = [regex]::Match(
        $repositoryRoot,
        $wslUncPattern,
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    $script:isWslUncPath = $repositoryMatch.Success

    if ($isWslUncPath) {
        $script:wslDistro = $repositoryMatch.Groups['distro'].Value
        $script:wslRepositoryRoot = ConvertTo-WslPath -Path $repositoryRoot

        # ClearAllTemplateFiles.bat lines 3-4.
        Invoke-WslPatternDelete `
            -Description "__pycache__ directories under '$repositoryRoot'" `
            -TargetType 'Directory' `
            -Name '__pycache__'
        Invoke-WslPatternDelete `
            -Description "*.toc files under '$repositoryRoot'" `
            -TargetType 'File' `
            -Name '*.toc'
    }
    else {
        # ClearAllTemplateFiles.bat line 3: all __pycache__ directories.
        $currentTarget = "__pycache__ directories under '$repositoryRoot'"
        $pycacheDirectories = @(
            Get-ChildItem -LiteralPath $repositoryRoot -Directory -Filter '__pycache__' -Force -Recurse
        )
        foreach ($directory in $pycacheDirectories) {
            Remove-DirectoryIfExists $directory.FullName
        }

        # ClearAllTemplateFiles.bat line 4: all *.toc files.
        $currentTarget = "*.toc files under '$repositoryRoot'"
        $tocFiles = @(
            Get-ChildItem -LiteralPath $repositoryRoot -File -Filter '*.toc' -Force -Recurse
        )
        foreach ($file in $tocFiles) {
            Remove-FileIfExists $file.FullName
        }
    }

    # ClearAllTemplateFiles.bat lines 5-17, in the same order.
    Remove-FileIfExists (Join-Path -Path $repositoryRoot -ChildPath 'config.yaml')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'dist')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'build')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'app/backend/build')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'app/backend/dist')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'venv')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'app/backend/venv')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'logs')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'node_modules')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath '.pnpm-store')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'app/frontend/build')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'app/frontend/node_modules')
    Remove-DirectoryIfExists (Join-Path -Path $repositoryRoot -ChildPath 'app/frontend/.pnpm-store')

    Write-Host 'Cleanup complete.'
}
catch {
    Write-Host "Cleanup failed while removing '$currentTarget': $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}
finally {
    $null = Read-Host 'Press Enter to continue'
}

if ($exitCode -ne 0) {
    exit 1
}
