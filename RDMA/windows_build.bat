@echo off
REM Windows Build Script for Software-Defined RDMA
REM Automated compilation and installation for Windows systems

setlocal enabledelayedexpansion

REM Configuration
set DRIVER_NAME=WindowsDMA
set DRIVER_VERSION=2.0
set VISUAL_STUDIO_VERSION=2022
set WDK_VERSION=22H2
set PYTHON_VERSION=3.9

REM Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%Windows DMA Build Script%NC%
echo ==============================
echo.
echo Visual Studio: %VISUAL_STUDIO_VERSION%
echo Windows Driver Kit: %WDK_VERSION%
echo Python: %PYTHON_VERSION%
echo.

REM Check prerequisites
echo %YELLOW%Checking prerequisites...%NC%

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Python not found. Please install Python %PYTHON_VERSION% or later%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Python available%NC%
)

REM Check Visual Studio
where devenv >nul 2>&1
if errorlevel 1 (
    echo %RED%Visual Studio not found. Please install Visual Studio %VISUAL_STUDIO_VERSION% with C++ workload%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Visual Studio available%NC%
)

REM Check Windows Driver Kit
if not exist "%ProgramFiles(x86)%\Windows Kits\10\%WDK_VERSION%" (
    echo %RED%Windows Driver Kit not found. Please install WDK %WDK_VERSION%%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Windows Driver Kit available%NC%
)

REM Check pywin32
python -c "import win32api" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%Installing pywin32...%NC%
    pip install pywin32
    if errorlevel 1 (
        echo %RED%Failed to install pywin32%NC%
        pause
        exit /b 1
    )
    echo %GREEN%✓ pywin32 installed%NC%
) else (
    echo %GREEN%✓ pywin32 available%NC%
)

REM Check other Python dependencies
echo %YELLOW%Checking Python dependencies...%NC%
pip show numpy >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%Installing required Python packages...%NC%
    pip install -r requirements.txt
    if errorlevel 1 (
        echo %RED%Failed to install Python dependencies%NC%
        pause
        exit /b 1
    )
) else (
    echo %GREEN%✓ Python dependencies available%NC%
)

echo.
echo %GREEN%All prerequisites satisfied%NC%
echo.

REM Build Windows kernel driver
echo %YELLOW%Building Windows kernel driver...%NC%

REM Setup build environment
call "C:\Program Files\Microsoft Visual Studio\%VISUAL_STUDIO_VERSION%\Enterprise\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1

REM Set WDK environment variables
set "WDK_DIR=%ProgramFiles(x86)%\Windows Kits\10\%WDK_VERSION%"
set "INCLUDE=%WDK_DIR%\Include\10.0.22621.0\km;%WDK_DIR%\Include\10.0.22621.0\shared;%INCLUDE%"
set "LIB=%WDK_DIR%\Lib\10.0.22621.0\km\x64;%LIB%"
set "PATH=%WDK_DIR%\bin\10.0.22621.0\x64;%PATH%"

REM Compile driver
echo %BLUE%Compiling Windows DMA driver...%NC%
cl /I"%INCLUDE%" ^
   /DWIN32_LEAN_AND_MEAN ^
   /DNTDDI_VERSION=0x06000000 ^
   /DKERNEL_MODE ^
   /DRIVER_NAME=%DRIVER_NAME% ^
   /DRIVER_VERSION=%DRIVER_VERSION% ^
   /O2 /Ob2 /Oi /Ot /Oy /GL ^
   /Gy /GF ^
   /W3 /WX ^
   /Zi /Zp8 ^
   /Gd /GR- ^
   /favor:INTEL64 ^
   /arch:AVX2 ^
   windows_dma_driver.cpp ^
   /Fe:windows_dma_driver.sys ^
   /link ^
   /DRIVER ^
   /SUBSYSTEM:NATIVE ^
   /NODEFAULTLIB ^
   /ENTRY:DriverEntry ^
   /BASE:0x10000 ^
   /ALIGN:4096 ^
   /SECTION:.text,ERW ^
   /SECTION:.data,RW ^
   /MERGE:.rdata=.text ^
   /OPT:REF ^
   /OPT:ICF ^
   /LTCG ^
   kernel32.lib ntoskrnl.lib hal.lib

if errorlevel 1 (
    echo %RED%Driver compilation failed%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Driver compiled successfully%NC%
)

REM Create INF file for driver installation
echo %YELLOW%Creating driver INF file...%NC%

(
echo [Version]
echo Signature="$WINDOWS NT$"
echo Class=System
echo ClassGuid={4d36e97d-e325-11ce-bfc1-08002be10318}
echo Provider=%DRIVER_NAME%
echo DriverVer=01/01/2024,%DRIVER_VERSION%.0.0
echo CatalogFile=windows_dma.cat
echo.
echo [DestinationDirs]
echo DefaultDestDir = 12
echo.
echo [DefaultInstall]
echo CopyFiles = DefaultDestDir
echo.
echo [DefaultInstall.Services]
echo AddService = %DRIVER_NAME%, 0x00000002, WindowsDMA_Service_Inst
echo.
echo [DefaultInstall.HW]
echo AddReg = WindowsDMA_HW_AddReg
echo.
echo [WindowsDMA_Service_Inst]
echo DisplayName    = "%DRIVER_NAME% Driver"
echo ServiceType    = 1               ; SERVICE_KERNEL_DRIVER
echo StartType       = 3               ; SERVICE_DEMAND_START
echo ErrorControl    = 1               ; SERVICE_ERROR_NORMAL
echo ServiceBinaryName = %12%\windows_dma_driver.sys
echo.
echo [WindowsDMA_HW_AddReg]
echo HKR,, "Parameters"
echo.
echo [SourceDisksNames]
echo 1 = %DISK%,,,
echo.
echo [SourceDisksFiles]
echo windows_dma_driver.sys = 1,,
echo.
echo [DefaultDestDir]
echo 11
echo.
echo [DefaultUninstall]
echo DelFiles = DefaultDestDir
echo.
echo [DefaultUninstall.Services]
echo DelService = %DRIVER_NAME%,0x204
) > windows_dma.inf

echo %GREEN%✓ Driver INF file created%NC%

REM Create Windows service installation script
echo %YELLOW%Creating Windows service installer...%NC%

(
echo @echo off
echo REM Windows DMA Driver Installation Script
echo.
echo if "%1"=="install" goto install
echo if "%1"=="uninstall" goto uninstall
echo if "%1"=="start" goto start
echo if "%1"=="stop" goto stop
echo.
echo echo Usage: %%0 [install^|uninstall^|start^|stop]
echo goto end
echo.
echo :install
echo echo Installing Windows DMA driver...
echo pnputil /add-driver /install windows_dma.inf /subdirs
echo if errorlevel 1 (
echo     echo Driver installation failed
echo     pause
echo     exit /b 1
echo ^)
echo echo Driver installed successfully
echo goto end
echo.
echo :uninstall
echo echo Uninstalling Windows DMA driver...
echo pnputil /delete-driver windows_dma.inf /uninstall
echo if errorlevel 1 (
echo     echo Driver uninstallation failed
echo     pause
echo     exit /b 1
echo ^)
echo echo Driver uninstalled successfully
echo goto end
echo.
echo :start
echo echo Starting Windows DMA service...
echo sc start WindowsDMA
echo if errorlevel 1 (
echo     echo Service start failed
echo     pause
echo     exit /b 1
echo ^)
echo echo Service started successfully
echo goto end
echo.
echo :stop
echo echo Stopping Windows DMA service...
echo sc stop WindowsDMA
echo if errorlevel 1 (
echo     echo Service stop failed
echo     pause
echo     exit /b 1
echo ^)
echo echo Service stopped successfully
echo goto end
echo.
echo :end
) > install_windows_driver.bat

echo %GREEN%✓ Windows service installer created%NC%

REM Create Python package for Windows
echo %YELLOW%Creating Windows Python package...%NC%

if not exist "windows_package" mkdir windows_package

(
echo from setuptools import setup, find_packages
echo.
echo setup(
echo     name="software-defined-rdma-windows",
echo     version="%DRIVER_VERSION%.0.0",
echo     description="Software-Defined RDMA for Windows",
echo     long_description=open("README.md").read(),
echo     long_description_content_type="text/markdown",
echo     author="Software-Defined RDMA Project",
echo     author_email="info@rdma-project.com",
echo     url="https://github.com/rdma-project/software-defined-rdma",
echo     packages=find_packages(),
echo     classifiers=[
echo         "Development Status :: 4 - Beta",
echo         "Intended Audience :: Developers",
echo         "License :: OSI Approved :: MIT License",
echo         "Programming Language :: Python :: 3",
echo         "Programming Language :: Python :: 3.8",
echo         "Programming Language :: Python :: 3.9",
echo         "Programming Language :: Python :: 3.10",
echo         "Operating System :: Microsoft :: Windows",
echo         "Topic :: System :: Hardware",
echo         "Topic :: System :: Networking",
echo     ],
echo     python_requires="^=3.8",
echo     install_requires=[
echo         "numpy>=1.24.0",
echo         "psutil>=5.9.0",
echo         "pywin32>=306",
echo         "pywintypes>=306",
echo         "win32security>=306",
echo         "win32profile>=306",
echo         "win32process>=306",
echo         "win32job>=306",
echo         "netifaces>=0.11.0",
echo     ],
echo     extras_require={
echo         "dev": [
echo             "pytest>=7.0.0",
echo             "pytest-cov>=4.0.0",
echo             "black>=22.0.0",
echo             "flake8>=5.0.0",
echo             "mypy>=1.0.0",
echo         ],
echo         "monitoring": [
echo             "matplotlib>=3.5.0",
echo             "scipy>=1.9.0",
echo         ],
echo     },
echo     entry_points={
echo         "console_scripts": [
echo             "windows-dma=windows_dma_interface:main",
echo         ],
echo     },
echo     include_package_data=True,
echo     package_data={
echo         "": ["*.md", "*.txt", "*.bat", "*.inf", "*.sys"],
echo     },
echo )
) > windows_package\setup.py

REM Copy necessary files
copy windows_dma_interface.py windows_package\ >nul 2>&1
copy windows_dma_driver.cpp windows_package\ >nul 2>&1
copy windows_dma.inf windows_package\ >nul 2>&1
copy README.md windows_package\ >nul 2>&1

echo %GREEN%✓ Windows Python package created%NC%

REM Create Windows installer
echo %YELLOW%Creating Windows installer...%NC%

REM Use NSIS or Inno Setup if available
where makensis >nul 2>&1
if not errorlevel 1 (
    echo %BLUE%Creating NSIS installer...%NC%
    
    (
        echo !define APP_NAME "Software-Defined RDMA"
        echo !define APP_VERSION "%DRIVER_VERSION%.0.0"
        echo !define PUBLISHER "RDMA Project"
        echo !define APP_URL "https://github.com/rdma-project/software-defined-rdma"
        echo.
        echo Name "${APP_NAME}"
        echo OutFile "Software-Defined-RDMA-${APP_VERSION}-Setup.exe"
        echo InstallDir "$PROGRAMFILES\${APP_NAME}"
        echo RequestExecutionLevel admin
        echo.
        echo Page directory
        echo Page instfiles
        echo.
        echo Section "MainSection" SEC01
        echo     SetOutPath "$INSTDIR"
        echo     File /r "windows_package\*"
        echo     File "windows_dma_driver.sys"
        echo     File "windows_dma.inf"
        echo     File "install_windows_driver.bat"
        echo.
        echo     ; Install driver
        echo     ExecWait '"$INSTDIR\install_windows_driver.bat" install'
        echo.
        echo     ; Create uninstaller
        echo     WriteUninstaller "$INSTDIR\Uninstall.exe"
        echo SectionEnd
        echo.
        echo Section "Uninstall"
        echo     Delete "$INSTDIR\Uninstall.exe"
        echo     RMDir /r "$INSTDIR"
        echo SectionEnd
    ) > setup.nsi
    
    makensis setup.nsi >nul 2>&1
    if not errorlevel 1 (
        echo %GREEN%✓ Windows installer created%NC%
    ) else (
        echo %YELLOW%NSIS installer creation failed%NC%
    )
else
    echo %YELLOW%NSIS not found, skipping installer creation%NC%
fi

REM Test the build
echo %YELLOW%Testing build...%NC%

REM Test Python import
python -c "import windows_dma_interface; print('✓ Python interface import successful')" >nul 2>&1
if errorlevel 1 (
    echo %RED%Python interface test failed%NC%
) else (
    echo %GREEN%✓ Python interface test passed%NC%
)

REM Test driver file
if exist windows_dma_driver.sys (
    echo %GREEN%✓ Driver file exists%NC%
) else (
    echo %RED%Driver file missing%NC%
)

REM Test INF file
if exist windows_dma.inf (
    echo %GREEN%✓ INF file exists%NC%
) else (
    echo %RED%INF file missing%NC%
)

echo.
echo %GREEN%Windows DMA build completed successfully!%NC%
echo.
echo %BLUE%Next steps:%NC%
echo 1. Install the driver: install_windows_driver.bat install
echo 2. Start the service: install_windows_driver.bat start
echo 3. Test the interface: python windows_dma_interface.py
echo 4. Install the Python package: pip install -e windows_package/
echo.
echo %BLUE%Files created:%NC%
echo - windows_dma_driver.sys (Windows kernel driver)
echo - windows_dma.inf (Driver installation file)
echo - windows_dma_interface.py (Python interface)
echo - install_windows_driver.bat (Driver installer)
echo - windows_package/ (Python package)
echo - Software-Defined-RDMA-%DRIVER_VERSION%.0.0-Setup.exe (Windows installer)
echo.
echo %YELLOW%Note: Administrator privileges required for driver installation%NC%

pause
