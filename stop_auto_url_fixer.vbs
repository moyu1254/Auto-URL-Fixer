Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
exePath = fso.BuildPath(scriptDir, "Auto URL Fixer.exe")

shell.CurrentDirectory = scriptDir

If fso.FileExists(exePath) Then
    shell.Run """" & exePath & """ --stop", 0, False
Else
    shell.Run "powershell -ExecutionPolicy Bypass -File """ & fso.BuildPath(scriptDir, "stop_auto_url_fixer.ps1") & """", 0, False
End If
