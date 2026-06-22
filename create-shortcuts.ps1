$WshShell = New-Object -ComObject WScript.Shell
$BatchFile = Join-Path $PSScriptRoot "start-dashboard.bat"

# Desktop shortcut
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "FIFO Portfolio Analyzer.lnk"))
$Shortcut.TargetPath = $BatchFile
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "FIFO Portfolio Analyzer"
$Shortcut.IconLocation = "shell32.dll,170"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

# Startup shortcut
$StartupPath = [System.Environment]::GetFolderPath("Startup")
$StartupLink = $WshShell.CreateShortcut((Join-Path $StartupPath "FIFO Portfolio Analyzer.lnk"))
$StartupLink.TargetPath = $BatchFile
$StartupLink.WorkingDirectory = $PSScriptRoot
$StartupLink.Description = "FIFO Portfolio Analyzer"
$StartupLink.IconLocation = "shell32.dll,170"
$StartupLink.WindowStyle = 7
$StartupLink.Save()

Write-Host "Desktop + Startup shortcuts created for FIFO Portfolio Analyzer"
