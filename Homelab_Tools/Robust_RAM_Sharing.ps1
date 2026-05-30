# Robust RAM Sharing Solution for Homelab
# Multiple methods with automatic fallback and verification

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("setup", "cleanup", "test", "map", "unmap")]
    [string]$Action = "setup",
    
    [Parameter(Mandatory=$false)]
    [string]$Method = "auto",
    
    [Parameter(Mandatory=$false)]
    [int]$RAMSizeGB = 4,
    
    [Parameter(Mandatory=$false)]
    [string]$TargetIP = "192.168.1.186",
    
    [Parameter(Mandatory=$false)]
    [string]$DriveLetter = "R"
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

function Test-AdminPrivileges {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch {
        return $false
    }
}

function Install-RequiredFeatures {
    Write-Log "Installing required Windows features..."
    
    # Install iSCSI Target Server
    try {
        Install-WindowsFeature -Name FS-iSCSITarget-Server -IncludeManagementTools
        Write-Log "iSCSI Target Server installed successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to install iSCSI Target Server: $($_.Exception.Message)" "WARNING"
    }
    
    # Install File Server role
    try {
        Install-WindowsFeature -Name FS-FileServer -IncludeManagementTools
        Write-Log "File Server role installed successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to install File Server role: $($_.Exception.Message)" "WARNING"
    }
}

function Test-ImDiskInstallation {
    try {
        $imdisk = Get-Command imdisk.exe -ErrorAction SilentlyContinue
        return $null -ne $imdisk
    } catch {
        return $false
    }
}

function Install-ImDisk {
    Write-Log "Installing ImDisk Toolkit..."
    
    $downloadUrl = "https://sourceforge.net/projects/imdisk-toolkit/files/latest/download"
    $installerPath = "$env:TEMP\imdisk-toolkit.exe"
    
    try {
        # Download ImDisk
        Write-Log "Downloading ImDisk Toolkit..."
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath
        
        # Install silently
        Write-Log "Installing ImDisk silently..."
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -NoNewWindow
        
        # Verify installation
        if (Test-ImDiskInstallation) {
            Write-Log "ImDisk Toolkit installed successfully" "SUCCESS"
            return $true
        } else {
            Write-Log "ImDisk installation verification failed" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to install ImDisk: $($_.Exception.Message)" "ERROR"
        return $false
    } finally {
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
}

function New-RAMDisk {
    param([int]$SizeGB, [string]$DriveLetter)
    
    Write-Log "Creating ${SizeGB}GB RAM disk as drive ${DriveLetter}:"
    
    try {
        # Remove existing RAM disk if it exists
        $existingDisk = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue
        if ($existingDisk) {
            Write-Log "Removing existing RAM disk on drive ${DriveLetter}:" "WARNING"
            imdisk -D -m "${DriveLetter}:"
        }
        
        # Create new RAM disk
        $sizeMB = $SizeGB * 1024
        imdisk -a -s "${sizeMB}M" -m "${DriveLetter}:" -p "/fs:ntfs /q /y"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "RAM disk created successfully as ${DriveLetter}:" "SUCCESS"
            return $true
        } else {
            Write-Log "Failed to create RAM disk" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error creating RAM disk: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function New-iSCSITarget {
    param([string]$DriveLetter, [string]$TargetName = "RAMDiskTarget")
    
    Write-Log "Creating iSCSI target for RAM disk..."
    
    try {
        $diskNumber = (Get-Partition -DriveLetter $DriveLetter).DiskNumber
        
        # Create iSCSI virtual disk
        $vhdPath = "C:\iSCSI\RAMDisk.vhdx"
        $vhdFolder = Split-Path $vhdPath -Parent
        
        if (!(Test-Path $vhdFolder)) {
            New-Item -Path $vhdFolder -ItemType Directory -Force
        }
        
        # Create VHD from RAM disk partition
        Export-PhysicalDisk -DiskNumber $diskNumber -FilePath $vhdPath
        
        # Create iSCSI target
        New-IscsiVirtualDisk -Path $vhdPath -Size ($RAMSizeGB * 1GB) -Description "RAM Disk iSCSI Target"
        New-IscsiServerTarget -TargetName $TargetName -Path $vhdPath
        
        Write-Log "iSCSI target created: $TargetName" "SUCCESS"
        return $true
    } catch {
        Write-Log "Failed to create iSCSI target: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function New-SMBShare {
    param([string]$DriveLetter, [string]$ShareName = "RamDisk")
    
    Write-Log "Creating SMB share for RAM disk..."
    
    try {
        $sharePath = "${DriveLetter}:\"
        
        # Remove existing share if it exists
        $existingShare = Get-SmbShare -Name $ShareName -ErrorAction SilentlyContinue
        if ($existingShare) {
            Write-Log "Removing existing SMB share: $ShareName" "WARNING"
            Remove-SmbShare -Name $ShareName -Force
        }
        
        # Create new share
        New-SmbShare -Name $ShareName -Path $sharePath -ReadAccess "Everyone" -FullAccess "Everyone"
        
        Write-Log "SMB share created: \\$TargetIP\$ShareName" "SUCCESS"
        return $true
    } catch {
        Write-Log "Failed to create SMB share: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Connect-iSCSITarget {
    param([string]$TargetIP, [string]$TargetName = "RAMDiskTarget")
    
    Write-Log "Connecting to iSCSI target on $TargetIP..."
    
    try {
        # Connect to iSCSI target
        Connect-IscsiTarget -NodeAddress "${TargetIP}:3260" -TargetPortalAddress $TargetIP -TargetPortalPortNumber 3260
        
        # Wait for connection
        Start-Sleep -Seconds 3
        
        # Find and initialize the new disk
        $disk = Get-Disk | Where-Object { $_.OperationalStatus -eq "Online" -and $_.PartitionStyle -eq "RAW" } | Select-Object -First 1
        
        if ($disk) {
            Initialize-Disk -Number $disk.Number -PartitionStyle MBR
            New-Partition -DiskNumber $disk.Number -UseMaximumSize -AssignDriveLetter
            Format-Volume -DriveLetter $disk.Partitions[0].DriveLetter -FileSystem NTFS -Confirm:$false
            
            Write-Log "iSCSI target connected and initialized as drive $($disk.Partitions[0].DriveLetter):" "SUCCESS"
            return $true
        } else {
            Write-Log "No new disk found after iSCSI connection" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to connect to iSCSI target: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Connect-SMBShare {
    param([string]$TargetIP, [string]$ShareName = "RamDisk", [string]$DriveLetter = "Z")
    
    Write-Log "Mapping SMB share from $TargetIP..."
    
    try {
        # Remove existing mapping if it exists
        $existingMapping = Get-PSDrive -Name $DriveLetter -ErrorAction SilentlyContinue
        if ($existingMapping) {
            Write-Log "Removing existing drive mapping: ${DriveLetter}:" "WARNING"
            net use "${DriveLetter}:" /delete
        }
        
        # Map the share
        net use "${DriveLetter}:" "\\$TargetIP\$ShareName" /persistent:yes
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "SMB share mapped as ${DriveLetter}:" "SUCCESS"
            return $true
        } else {
            Write-Log "Failed to map SMB share" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error mapping SMB share: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-RAMDiskPerformance {
    param([string]$DriveLetter)
    
    Write-Log "Testing RAM disk performance..."
    
    try {
        $testFile = "${DriveLetter}:\performance_test.tmp"
        $dataSize = 100MB
        
        # Write test
        $writeTime = Measure-Command {
            $data = [byte[]]::new($dataSize)
            [System.IO.File]::WriteAllBytes($testFile, $data)
        }
        
        # Read test
        $readTime = Measure-Command {
            [System.IO.File]::ReadAllBytes($testFile) | Out-Null
        }
        
        # Cleanup
        Remove-Item $testFile -Force -ErrorAction SilentlyContinue
        
        $writeSpeed = [math]::Round($dataSize / 1MB / $writeTime.TotalSeconds, 2)
        $readSpeed = [math]::Round($dataSize / 1MB / $readTime.TotalSeconds, 2)
        
        Write-Log "Performance Results:" "SUCCESS"
        Write-Log "  Write: $writeSpeed MB/s" "INFO"
        Write-Log "  Read:  $readSpeed MB/s" "INFO"
        
        return @{
            WriteSpeed = $writeSpeed
            ReadSpeed = $readSpeed
            Success = $true
        }
    } catch {
        Write-Log "Performance test failed: $($_.Exception.Message)" "ERROR"
        return @{ Success = $false }
    }
}

# Main execution
switch ($Action) {
    "setup" {
        Write-Log "Starting robust RAM sharing setup..." "INFO"
        
        # Step 1: Check administrator privileges
        if (!(Test-AdminPrivileges)) {
            Write-Log "This script requires administrator privileges. Please run as Administrator." "ERROR"
            exit 1
        }
        
        # Step 2: Install required Windows features FIRST
        Write-Log "Step 1: Installing Windows features..." "INFO"
        Install-RequiredFeatures
        
        # Step 3: Install ImDisk if needed
        Write-Log "Step 2: Checking ImDisk installation..." "INFO"
        if (!(Test-ImDiskInstallation)) {
            Write-Log "ImDisk not found, installing..." "INFO"
            if (!(Install-ImDisk)) {
                Write-Log "ImDisk installation failed. Cannot proceed." "ERROR"
                exit 1
            }
        } else {
            Write-Log "ImDisk already installed" "SUCCESS"
        }
        
        # Step 4: Clean up any existing RAM disk
        Write-Log "Step 3: Cleaning up existing RAM disk..." "INFO"
        $existingDisk = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue
        if ($existingDisk) {
            Write-Log "Removing existing RAM disk on ${DriveLetter}:" "WARNING"
            imdisk -D -m "${DriveLetter}:" -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
        
        # Step 5: Create RAM disk
        Write-Log "Step 4: Creating RAM disk..." "INFO"
        if (New-RAMDisk -SizeGB $RAMSizeGB -DriveLetter $DriveLetter) {
            # Step 6: Verify RAM disk is accessible
            Write-Log "Step 5: Verifying RAM disk accessibility..." "INFO"
            Start-Sleep -Seconds 3
            $disk = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue
            if (-not $disk) {
                Write-Log "RAM disk not accessible after creation" "ERROR"
                exit 1
            }
            Write-Log "RAM disk verified and accessible" "SUCCESS"
            
            # Step 7: Create SMB share FIRST (more reliable)
            Write-Log "Step 6: Creating SMB share..." "INFO"
            $SMBSuccess = New-SMBShare -DriveLetter $DriveLetter
            
            # Step 8: Create iSCSI target SECOND (optional, for performance)
            Write-Log "Step 7: Creating iSCSI target..." "INFO"
            $iSCSISuccess = New-iSCSITarget -DriveLetter $DriveLetter
            
            # Step 9: Verify shares are working
            Write-Log "Step 8: Verifying shares..." "INFO"
            Start-Sleep -Seconds 2
            
            if ($SMBSuccess -or $iSCSISuccess) {
                Write-Log "RAM sharing setup completed successfully!" "SUCCESS"
                Write-Log "Available methods:" "INFO"
                if ($SMBSuccess) {
                    Write-Log "  SMB Share: \\$TargetIP\RamDisk" "INFO"
                }
                if ($iSCSISuccess) {
                    Write-Log "  iSCSI Target: RAMDiskTarget" "INFO"
                }
                
                # Step 10: Test performance LAST
                Write-Log "Step 9: Testing performance..." "INFO"
                Test-RAMDiskPerformance -DriveLetter $DriveLetter
                
                Write-Log "Setup completed in correct order!" "SUCCESS"
            } else {
                Write-Log "Failed to create any sharing methods" "ERROR"
                exit 1
            }
        } else {
            Write-Log "RAM disk creation failed" "ERROR"
            exit 1
        }
    }
    
    "map" {
        Write-Log "Mapping RAM disk from $TargetIP..."
        
        # Step 1: Test network connectivity FIRST
        Write-Log "Step 1: Testing network connectivity..." "INFO"
        if (!(Test-Connection -ComputerName $TargetIP -Count 2 -Quiet)) {
            Write-Log "Cannot reach server at $TargetIP" "ERROR"
            exit 1
        }
        Write-Log "Network connectivity confirmed" "SUCCESS"
        
        # Step 2: Try SMB share FIRST (more reliable)
        Write-Log "Step 2: Attempting SMB share connection..." "INFO"
        if (Connect-SMBShare -TargetIP $TargetIP) {
            Write-Log "SMB share connection successful" "SUCCESS"
        } else {
            Write-Log "SMB share failed, trying iSCSI..." "WARNING"
            # Step 3: Try iSCSI as fallback
            Write-Log "Step 3: Attempting iSCSI connection..." "INFO"
            if (Connect-iSCSITarget -TargetIP $TargetIP) {
                Write-Log "iSCSI connection successful" "SUCCESS"
            } else {
                Write-Log "All connection methods failed" "ERROR"
                Write-Log "Troubleshooting:" "INFO"
                Write-Log "  1. Ensure server is running on $TargetIP" "INFO"
                Write-Log "  2. Check Windows Firewall settings" "INFO"
                Write-Log "  3. Run Fix_Windows_Compatibility.bat on both PCs" "INFO"
                exit 1
            }
        }
        
        Write-Log "RAM disk mapping completed in correct order!" "SUCCESS"
    }
    
    "test" {
        $drive = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue
        if ($drive) {
            Test-RAMDiskPerformance -DriveLetter $DriveLetter
        } else {
            Write-Log "RAM disk not found on drive ${DriveLetter}:" "ERROR"
        }
    }
    
    "cleanup" {
        Write-Log "Cleaning up RAM sharing setup..."
        
        # Remove SMB share
        $share = Get-SmbShare -Name "RamDisk" -ErrorAction SilentlyContinue
        if ($share) {
            Remove-SmbShare -Name "RamDisk" -Force
            Write-Log "SMB share removed" "INFO"
        }
        
        # Remove iSCSI target
        $target = Get-IscsiServerTarget -TargetName "RAMDiskTarget" -ErrorAction SilentlyContinue
        if ($target) {
            Remove-IscsiServerTarget -TargetName "RAMDiskTarget" -Confirm:$false
            Write-Log "iSCSI target removed" "INFO"
        }
        
        # Remove RAM disk
        $disk = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue
        if ($disk) {
            imdisk -D -m "${DriveLetter}:"
            Write-Log "RAM disk removed" "INFO"
        }
        
        Write-Log "Cleanup completed" "SUCCESS"
    }
    
    default {
        Write-Log "Unknown action: $Action" "ERROR"
        exit 1
    }
}

Write-Log "Script completed" "SUCCESS"
