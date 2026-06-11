Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
exePath = fso.BuildPath(scriptDir, "Auto URL Fixer.exe")

shell.CurrentDirectory = scriptDir

If fso.FileExists(exePath) Then
    shell.Run """" & exePath & """", 0, False
Else
    launchCommand = "cmd /c ""where pyw >nul 2>nul && pyw -3 -m auto_url_fixer || where pythonw >nul 2>nul && pythonw -m auto_url_fixer || where py >nul 2>nul && py -3 -m auto_url_fixer || python -m auto_url_fixer"""
    shell.Run launchCommand, 0, False
End If
