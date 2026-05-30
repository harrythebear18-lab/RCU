# Homelab Tools - PowerShell Auto Setup Script
# Run with: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then: .\setup.ps1

param(
    [switch]$SkipGPU,
    [switch]$Admin,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Homelab Tools - PowerShell Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
if ($Admin -or ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "[✓] Running with administrator privileges" -ForegroundColor Green
    $IsAdmin = $true
} else {
    Write-Host "[!] Running without administrator privileges" -ForegroundColor Yellow
    $IsAdmin = $false
}

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to install package via winget
function Install-WingetPackage {
    param($PackageName, $DisplayName)
    Write-Host "Installing $DisplayName..." -ForegroundColor Yellow
    try {
        winget install $PackageName --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] $DisplayName installed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[!] $DisplayName installation failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "[!] $DisplayName installation failed: $_" -ForegroundColor Red
        return $false
    }
}

# Check Python installation
if (Test-Command "python") {
    $PythonVersion = python --version 2>&1
    Write-Host "[✓] Python found: $PythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found. Installing Python..." -ForegroundColor Red
    if (Install-WingetPackage "Python.Python.3" "Python 3") {
        Write-Host "[✓] Python installed. Please restart PowerShell and run this script again." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[ERROR] Failed to install Python. Please install manually from https://python.org" -ForegroundColor Red
        exit 1
    }
}

# Check Git installation
if (Test-Command "git") {
    $GitVersion = git --version
    Write-Host "[✓] Git found: $GitVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Git not found. Installing Git..." -ForegroundColor Red
    if (Install-WingetPackage "Git.Git" "Git") {
        Write-Host "[✓] Git installed. Please restart PowerShell and run this script again." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[ERROR] Failed to install Git. Please install manually from https://git-scm.com" -ForegroundColor Red
        exit 1
    }
}

# Install Git LFS
if (Test-Command "git-lfs") {
    $LFSVersion = git-lfs version
    Write-Host "[✓] Git LFS found: $LFSVersion" -ForegroundColor Green
} else {
    Write-Host "[!] Git LFS not found. Installing..." -ForegroundColor Yellow
    if (Test-Path ".\git-lfs.exe") {
        Write-Host "Using bundled Git LFS..." -ForegroundColor Yellow
        .\git-lfs.exe install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] Git LFS installed from bundle" -ForegroundColor Green
        } else {
            Write-Host "[!] Bundled Git LFS installation failed" -ForegroundColor Red
        }
    } else {
        if (Install-WingetPackage "GitHub.GitLFS" "Git LFS") {
            git lfs install
            Write-Host "[✓] Git LFS installed" -ForegroundColor Green
        } else {
            Write-Host "[!] Git LFS installation failed" -ForegroundColor Red
        }
    }
}

# Upgrade pip and install dependencies
Write-Host "Upgrading pip and installing dependencies..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "[✓] Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "[!] Some dependencies failed to install. Installing core packages..." -ForegroundColor Yellow
    try {
        python -m pip install psutil matplotlib numpy tkinter
        Write-Host "[✓] Core dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Core dependencies installation failed" -ForegroundColor Red
    }
}

# Install GPU packages if requested
if (-not $SkipGPU) {
    Write-Host "Installing GPU packages..." -ForegroundColor Yellow
    try {
        python -m pip install cupy-cuda11x GPUtil pyopencl
        Write-Host "[✓] GPU packages installed" -ForegroundColor Green
    } catch {
        Write-Host "[!] GPU packages installation failed (optional)" -ForegroundColor Yellow
    }
}

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
$Directories = @("logs", "cache", "temp", "performance_data", "monitoring_data")
foreach ($Dir in $Directories) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
        Write-Host "[✓] Created $Dir directory" -ForegroundColor Green
    }
}

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
[Environment]::SetEnvironmentVariable("HOMELAB_ROOT", $PWD, "User")
[Environment]::SetEnvironmentVariable("PYTHONPATH", $PWD, "User")
Write-Host "[✓] Environment variables set" -ForegroundColor Green

# Download LFS objects
Write-Host "Downloading LFS objects..." -ForegroundColor Yellow
git lfs pull
if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] LFS objects downloaded" -ForegroundColor Green
} else {
    Write-Host "[!] Some LFS objects may not be available" -ForegroundColor Yellow
}

# Test functionality
Write-Host "Testing functionality..." -ForegroundColor Yellow
try {
    $TestResult = python -c "import psutil, matplotlib, numpy; print('Core dependencies OK')"
    if ($TestResult -eq "Core dependencies OK") {
        Write-Host "[✓] Core dependencies working" -ForegroundColor Green
    } else {
        Write-Host "[!] Core dependencies test failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Core dependencies test failed: $_" -ForegroundColor Yellow
}

# Create desktop shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Homelab Tools.lnk")
    $Shortcut.TargetPath = "$PWD\homelab_launcher.py"
    $Shortcut.WorkingDirectory = $PWD
    $Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,13"
    $Shortcut.Save()
    Write-Host "[✓] Desktop shortcut created" -ForegroundColor Green
} catch {
    Write-Host "[!] Failed to create desktop shortcut" -ForegroundColor Yellow
}

# Administrator-specific setup
if ($IsAdmin) {
    Write-Host "Performing administrator setup..." -ForegroundColor Yellow
    
    # Create firewall rules
    try {
        New-NetFirewallRule -DisplayName "Homelab Tools" -Direction Inbound -Program "python.exe" -Action Allow -ErrorAction SilentlyContinue
        Write-Host "[✓] Firewall rules created" -ForegroundColor Green
    } catch {
        Write-Host "[!] Failed to create firewall rules" -ForegroundColor Yellow
    }
    
    # Set up performance monitoring
    try {
        reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PerfLib" /v "Application" /t REG_SZ /d "Homelab Tools" /f | Out-Null
        Write-Host "[✓] Performance monitoring configured" -ForegroundColor Green
    } catch {
        Write-Host "[!] Failed to configure performance monitoring" -ForegroundColor Yellow
    }
}

# Create launch script
Write-Host "Creating launch script..." -ForegroundColor Yellow
$LaunchScript = @"
@echo off
cd /d "%CD%"
python homelab_launcher.py
pause
"@
$LaunchScript | Out-File -FilePath "launch.bat" -Encoding ASCII
Write-Host "[✓] Launch script created" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Double-click the Homelab Tools desktop shortcut" -ForegroundColor White
Write-Host "2. Or run: .\launch.bat" -ForegroundColor White
Write-Host "3. Or run: python homelab_launcher.py" -ForegroundColor White
Write-Host ""
Write-Host "If you encounter issues:" -ForegroundColor White
Write-Host "- Run: .\setup.ps1 -Admin" -ForegroundColor White
Write-Host "- Check Python and Git installations" -ForegroundColor White
Write-Host "- Verify internet connection for LFS downloads" -ForegroundColor White
Write-Host ""
Write-Host "For GPU support, run: .\setup.ps1 -SkipGPU:`$false" -ForegroundColor White
Write-Host ""

# Ask if user wants to launch immediately
$Launch = Read-Host "Launch Homelab Tools now? (y/n)"
if ($Launch -eq 'y' -or $Launch -eq 'Y') {
    Write-Host "Launching Homelab Tools..." -ForegroundColor Green
    try {
        python homelab_launcher.py
    } catch {
        Write-Host "[!] Failed to launch Homelab Tools" -ForegroundColor Red
    }
}
