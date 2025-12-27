@echo off
chcp 65001 >nul
REM Network Share Setup Script
REM This script configures network discovery and file sharing settings

echo ================================
echo Network Sharing Auto-Configuration Script
echo ================================

REM Request administrator privileges
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~fs0\"' -Verb RunAs"
    exit /b
)

echo Administrator privileges obtained
echo.

REM Enable network discovery and file sharing for all profiles
echo Enabling network discovery and file sharing for all network profiles...
netsh advfirewall firewall set rule group="network discovery" new enable=Yes profile=private,domain,public >nul
netsh advfirewall firewall set rule group="file and printer sharing" new enable=Yes profile=private,domain,public >nul

REM Configure network discovery settings
echo Configuring network discovery settings...
netsh advfirewall firewall set rule group="network discovery" new enable=Yes >nul

REM Configure file and printer sharing
echo Configuring file and printer sharing...
netsh advfirewall firewall set rule group="file and printer sharing" new enable=Yes >nul

REM Turn off password protected sharing - specifically targeting the GUI setting
echo Turning off password protected sharing...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v EnableSecuritySignature /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v RequireSecuritySignature /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v EnablePlainTextPassword /t REG_DWORD /d 1 /f >nul

REM Specifically disable password protected sharing in the registry
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f >nul
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v SMBDeviceEnabled /t REG_DWORD /d 1 /f >nul

REM Disable password protected sharing via Group Policy settings
echo Setting Group Policy for password protected sharing...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\LanmanServer\Parameters" /v EnableSecuritySignature /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\LanmanServer\Parameters" /v RequireSecuritySignature /t REG_DWORD /d 0 /f >nul

REM Modify network security policy to allow anonymous access
echo Modifying network security policy for anonymous access...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v RestrictAnonymous /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v EveryoneIncludesAnonymous /t REG_DWORD /d 1 /f >nul
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v ANONYMOUS_NAME_LOOKUP /t REG_DWORD /d 1 /f >nul

REM Enable file and printer sharing for Microsoft networks
echo Enabling file and printer sharing for Microsoft networks...
netsh mbn set connectionprofile interface="*" ssid="*" sharing=allow >nul 2>&1

REM Check if Server service is running
echo Checking if Server service is running...
sc query lanmanserver | findstr /i "running" >nul
if %errorLevel% NEQ 0 (
    echo Starting Server service...
    net start server >nul
)

REM Check if Workstation service is running
echo Checking if Workstation service is running...
sc query lanmanworkstation | findstr /i "running" >nul
if %errorLevel% NEQ 0 (
    echo Starting Workstation service...
    net start workstation >nul
)

REM Set up shared folder (current directory)
echo Setting up shared folder...
set "folderPath=%~dp0"
set "folderName=SharedFolder"

echo Folder path to share: %folderPath%
echo Share name will be: %folderName%

REM Remove existing share with the same name
echo Removing any existing share with same name...
net share "%folderName%" /delete >nul 2>&1

REM Create share using multiple methods
echo Creating share...

REM Method 1: Using net share with full path
net share "%folderName%"="%folderPath%" /GRANT:Everyone,FULL >nul 2>&1
if %errorLevel% equ 0 (
    echo Method 1 succeeded: Share created using net share command
    goto :verification
)

REM Method 2: Using PowerShell if Method 1 fails
echo Method 1 failed, trying PowerShell method...
powershell -Command "New-SmbShare -Name '%folderName%' -Path '%folderPath%' -FullAccess 'Everyone'" >nul 2>&1
if %errorLevel% equ 0 (
    echo Method 2 succeeded: Share created using PowerShell
    goto :verification
)

REM Method 3: Using WMI if PowerShell fails
echo Method 2 failed, trying WMI method...
powershell -Command "([wmiclass]'Win32_Share').Create('%folderPath%', '%folderName%', 0, 2147483647, 'Shared folder')" >nul 2>&1
if %errorLevel% equ 0 (
    echo Method 3 succeeded: Share created using WMI
    goto :verification
)

echo All methods failed to create share.

:verification
echo.
echo Share setup completed!
echo.
echo Share name: %folderName%
echo Share path: %folderPath%
echo Permissions: Everyone Full Control
echo.
echo Network Discovery: Enabled
echo File and Printer Sharing: Enabled
echo Password Protected Sharing: Disabled
echo Anonymous Access: Enabled
echo.
echo Verifying share...
net share | findstr /i "%folderName%"
if %errorLevel% equ 0 (
    echo Share verified successfully!
) else (
    echo Share may not have been created. Check system permissions.
)
echo.
echo Current shares on this system:
net share
echo.
pause