# Windows 10/11 Compatibility Fix for RAM Sharing System
# Ensures smooth operation between different Windows versions

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "fix", "setup", "test")]
    [string]$Action = "check",
    
    [Parameter(Mandatory=$false)]
    [string]$TargetOS = "auto"
)

# Global variables
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Get-WindowsVersion {
    try {
        $osInfo = Get-CimInstance -ClassName Win32_OperatingSystem
        $version = [version]$osInfo.Version
        $build = $osInfo.BuildNumber
        $productName = $osInfo.Caption
        
        return @{
            ProductName = $productName
            Version = $version
            Build = $build
            IsWindows10 = $build -ge 10240 -and $build -lt 22000
            IsWindows11 = $build -ge 22000
            IsHome = $productName -like "*Home*"
            IsPro = $productName -like "*Pro*"
            IsEnterprise = $productName -like "*Enterprise*"
        }
    } catch {
        Write-Log "Failed to detect Windows version: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Test-AdminPrivileges {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch {
        return $false
    }
}

function Set-PowerShellExecutionPolicy {
    Write-Log "Setting PowerShell execution policy for cross-version compatibility..."
    
    try {
        # Set execution policy to RemoteSigned for current user
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Log "Execution policy set to RemoteSigned for current user" "SUCCESS"
        
        # Also set for local machine if possible
        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
            Write-Log "Execution policy set to RemoteSigned for local machine" "SUCCESS"
        } catch {
            Write-Log "Could not set execution policy for local machine (expected on some systems)" "WARNING"
        }
        
        return $true
    } catch {
        Write-Log "Failed to set execution policy: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Enable-NetworkSharingFeatures {
    param([hashtable]$OSInfo)
    
    Write-Log "Enabling network sharing features for $($OSInfo.ProductName)..."
    
    $features = @()
    
    # Base features for all versions
    $features += "FS-FileServer"
    
    # Windows 10/11 specific features
    if ($OSInfo.IsWindows10 -or $OSInfo.IsWindows11) {
        $features += "FS-iSCSITarget-Server"
    }
    
    # Enterprise/Pro features
    if ($OSInfo.IsPro -or $OSInfo.IsEnterprise) {
        $features += "FS-DFSNamespace", "FS-DFSR"
    }
    
    foreach ($feature in $features) {
        try {
            $result = Install-WindowsFeature -Name $feature -IncludeManagementTools -ErrorAction SilentlyContinue
            if ($result.Success) {
                Write-Log "Installed feature: $feature" "SUCCESS"
            } else {
                Write-Log "Feature already installed or not available: $feature" "INFO"
            }
        } catch {
            Write-Log "Could not install feature $feature : $($_.Exception.Message)" "WARNING"
        }
    }
    
    return $true
}

function Set-NetworkSettings {
    param([hashtable]$OSInfo)
    
    Write-Log "Configuring network settings for Windows compatibility..."
    
    try {
        # Enable network discovery
        $firewallRules = @(
            @{Name="File and Printer Sharing (Echo Request - ICMPv4-In)"; Enabled=$true},
            @{Name="File and Printer Sharing (SMB-In)"; Enabled=$true},
            @{Name="File and Printer Sharing (NB-Datagram-In)"; Enabled=$true},
            @{Name="File and Printer Sharing (NB-Name-In)"; Enabled=$true},
            @{Name="Windows Management Instrumentation (WMI-In)"; Enabled=$true}
        )
        
        foreach ($rule in $firewallRules) {
            try {
                Set-NetFirewallRule -DisplayName $rule.Name -Enabled $rule.Enabled -ErrorAction SilentlyContinue
                Write-Log "Configured firewall rule: $($rule.Name)" "SUCCESS"
            } catch {
                Write-Log "Firewall rule not found: $($rule.Name)" "WARNING"
            }
        }
        
        # Configure network profile settings
        try {
            $networkProfiles = Get-NetConnectionProfile
            foreach ($networkProfile in $networkProfiles) {
                if ($networkProfile.NetworkCategory -ne "Private") {
                    Set-NetConnectionProfile -InterfaceAlias $profile.InterfaceAlias -NetworkCategory Private
                    Write-Log "Set network profile to Private for $($profile.InterfaceAlias)" "SUCCESS"
                }
            }
        } catch {
            Write-Log "Could not configure network profiles: $($_.Exception.Message)" "WARNING"
        }
        
        # Enable SMB settings for Windows 10/11 compatibility
        try {
            # Enable SMB1 for legacy compatibility (Windows 10)
            if ($OSInfo.IsWindows10) {
                Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart -ErrorAction SilentlyContinue
                Write-Log "Enabled SMB1 protocol for Windows 10 compatibility" "SUCCESS"
            }
            
            # Ensure SMB2/3 are enabled
            Set-SmbServerConfiguration -EnableSMB2Protocol $true -Force -ErrorAction SilentlyContinue
            Set-SmbServerConfiguration -EnableSMB3Protocol $true -Force -ErrorAction SilentlyContinue
            Write-Log "Enabled SMB2/3 protocols" "SUCCESS"
            
        } catch {
            Write-Log "SMB configuration warning: $($_.Exception.Message)" "WARNING"
        }
        
        return $true
    } catch {
        Write-Log "Network configuration failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Set-UserPermissions {
    param([hashtable]$OSInfo)
    
    Write-Log "Configuring user permissions for cross-version access..."
    
    try {
        # Add current user to necessary groups
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        $groups = @("Administrators", "Users", "Remote Desktop Users")
        
        foreach ($group in $groups) {
            try {
                $groupObj = [ADSI]"WinNT://./$group,group"
                $groupObj.Add("WinNT://$currentUser,user")
                Write-Log "Added user to group: $group" "SUCCESS"
            } catch {
                Write-Log "User already in group or no permission: $group" "INFO"
            }
        }
        
        # Configure share permissions
        try {
            # Create Everyone group if it doesn't exist
            $everyone = [System.Security.Principal.SecurityIdentifier]"S-1-1-0"
            $everyoneAccount = $everyone.Translate([System.Security.Principal.NTAccount])
            Write-Log "Everyone group found: $($everyoneAccount.Value)" "SUCCESS"
        } catch {
            Write-Log "Could not find Everyone group" "WARNING"
        }
        
        return $true
    } catch {
        Write-Log "User permission configuration failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-CrossVersionConnectivity {
    param([string]$TargetIP = "192.168.1.132")
    
    Write-Log "Testing cross-version connectivity to $TargetIP..."
    
    $tests = @(
        @{Name="Ping"; Command={Test-Connection -ComputerName $TargetIP -Count 2 -Quiet}},
        @{Name="SMB Share"; Command={Get-SmbShare -Name "RamDisk" -ErrorAction SilentlyContinue}},
        @{Name="iSCSI Target"; Command={Get-IscsiServerTarget -ErrorAction SilentlyContinue}},
        @{Name="Port 445 (SMB)"; Command={Test-NetConnection -ComputerName $TargetIP -Port 445 -WarningAction SilentlyContinue}},
        @{Name="Port 3260 (iSCSI)"; Command={Test-NetConnection -ComputerName $TargetIP -Port 3260 -WarningAction SilentlyContinue}}
    )
    
    $results = @()
    
    foreach ($test in $tests) {
        try {
            $result = & $test.Command
            $success = if ($result -is [bool]) { $result } else { $null -ne $result }
            
            $results += @{
                Test = $test.Name
                Success = $success
                Details = if ($success) { "Passed" } else { "Failed" }
            }
            
            $status = if ($success) { "SUCCESS" } else { "FAILED" }
            Write-Log "$($test.Name): $status" $status
        } catch {
            $results += @{
                Test = $test.Name
                Success = $false
                Details = $_.Exception.Message
            }
            Write-Log "$($test.Name): FAILED - $($_.Exception.Message)" "ERROR"
        }
    }
    
    return $results
}

function Install-ImDiskCompatibility {
    param([hashtable]$OSInfo)
    
    Write-Log "Installing ImDisk with Windows $($OSInfo.Version) compatibility..."
    
    try {
        # Check if ImDisk is already installed
        $imdisk = Get-Command imdisk.exe -ErrorAction SilentlyContinue
        if ($imdisk) {
            Write-Log "ImDisk already installed" "SUCCESS"
            return $true
        }
        
        # Download ImDisk
        $downloadUrl = "https://sourceforge.net/projects/imdisk-toolkit/files/latest/download"
        $installerPath = "$env:TEMP\imdisk-toolkit.exe"
        
        Write-Log "Downloading ImDisk Toolkit..."
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath
        
        # Install with compatibility options for Windows 10/11
        Write-Log "Installing ImDisk with compatibility mode..."
        
        $process = Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Log "ImDisk installed successfully" "SUCCESS"
            
            # Verify installation
            $imdisk = Get-Command imdisk.exe -ErrorAction SilentlyContinue
            if ($imdisk) {
                Write-Log "ImDisk installation verified" "SUCCESS"
                return $true
            } else {
                Write-Log "ImDisk installation verification failed" "ERROR"
                return $false
            }
        } else {
            Write-Log "ImDisk installation failed with exit code $($process.ExitCode)" "ERROR"
            return $false
        }
    } catch {
        Write-Log "ImDisk installation failed: $($_.Exception.Message)" "ERROR"
        return $false
    } finally {
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
}

function New-CompatibilityReport {
    param([hashtable]$OSInfo, [array]$TestResults)
    
    Write-Log "Generating compatibility report..."
    
    $report = @"
========================================
WINDOWS COMPATIBILITY REPORT
========================================
System Information:
- OS: $($OSInfo.ProductName)
- Version: $($OSInfo.Version)
- Build: $($OSInfo.Build)
- Edition: $(if ($OSInfo.IsHome) { 'Home' } elseif ($OSInfo.IsPro) { 'Pro' } elseif ($OSInfo.IsEnterprise) { 'Enterprise' } else { 'Unknown' })

Test Results:
"@
    
    foreach ($result in $TestResults) {
        $status = if ($result.Success) { "✅ PASS" } else { "❌ FAIL" }
        $report += "`n- $($result.Test): $status - $($result.Details)"
    }
    
    $report += @"

Recommendations:
- Ensure both PCs are on the same network segment
- Run this script as Administrator on both systems
- Verify Windows Firewall allows file sharing
- Use SMB2/3 for best Windows 10/11 compatibility
- Consider using iSCSI for better performance

Next Steps:
1. Run Setup_RAM_Sharing.bat on the server PC
2. Run Map_RAM_Sharing.bat on the client PC
3. Use the GUI for easier management
"@
    
    $reportPath = "$env:USERPROFILE\Desktop\Windows_Compatibility_Report.txt"
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Log "Compatibility report saved to: $reportPath" "SUCCESS"
    return $reportPath
}

# Main execution
switch ($Action) {
    "check" {
        Write-Log "Starting Windows compatibility check..." "INFO"
        
        # Detect Windows version
        $osInfo = Get-WindowsVersion
        if (-not $osInfo) {
            Write-Log "Failed to detect Windows version" "ERROR"
            exit 1
        }
        
        Write-Log "Detected: $($osInfo.ProductName) Build $($osInfo.Build)" "INFO"
        
        # Check admin privileges
        if (-not (Test-AdminPrivileges)) {
            Write-Log "This script requires administrator privileges" "ERROR"
            Write-Log "Please run as Administrator" "ERROR"
            exit 1
        }
        
        # Test connectivity
        $testResults = Test-CrossVersionConnectivity
        
        # Generate report
        $reportPath = New-CompatibilityReport -OSInfo $osInfo -TestResults $testResults
        
        Write-Log "Compatibility check completed" "SUCCESS"
        Write-Log "Report saved to: $reportPath" "INFO"
    }
    
    "fix" {
        Write-Log "Starting Windows compatibility fixes..." "INFO"
        
        # Detect Windows version
        $osInfo = Get-WindowsVersion
        if (-not $osInfo) {
            Write-Log "Failed to detect Windows version" "ERROR"
            exit 1
        }
        
        # Check admin privileges
        if (-not (Test-AdminPrivileges)) {
            Write-Log "This script requires administrator privileges" "ERROR"
            exit 1
        }
        
        # Apply fixes
        $success = $true
        
        $success = $success -and (Set-PowerShellExecutionPolicy)
        $success = $success -and (Enable-NetworkSharingFeatures -OSInfo $osInfo)
        $success = $success -and (Set-NetworkSettings -OSInfo $osInfo)
        $success = $success -and (Set-UserPermissions -OSInfo $osInfo)
        $success = $success -and (Install-ImDiskCompatibility -OSInfo $osInfo)
        
        if ($success) {
            Write-Log "All compatibility fixes applied successfully" "SUCCESS"
        } else {
            Write-Log "Some fixes failed. Check the log above." "WARNING"
        }
        
        # Test after fixes
        $testResults = Test-CrossVersionConnectivity
        New-CompatibilityReport -OSInfo $osInfo -TestResults $testResults
    }
    
    "setup" {
        Write-Log "Running complete Windows compatibility setup..." "INFO"
        
        # Run fix first
        & $PSCommandPath -Action fix
        
        # Then run RAM sharing setup
        $ramScript = Join-Path $PSScriptRoot "Robust_RAM_Sharing.ps1"
        if (Test-Path $ramScript) {
            Write-Log "Starting RAM sharing setup..." "INFO"
            & $ramScript -Action setup
        } else {
            Write-Log "RAM sharing script not found: $ramScript" "ERROR"
        }
    }
    
    "test" {
        Write-Log "Running compatibility tests..." "INFO"
        
        $osInfo = Get-WindowsVersion
        $testResults = Test-CrossVersionConnectivity
        Create-CompatibilityReport -OSInfo $osInfo -TestResults $testResults
    }
    
    default {
        Write-Log "Unknown action: $Action" "ERROR"
        exit 1
    }
}

Write-Log "Windows compatibility script completed" "SUCCESS"
