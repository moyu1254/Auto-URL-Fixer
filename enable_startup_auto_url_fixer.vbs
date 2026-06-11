Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
exePath = fso.BuildPath(scriptDir, "Auto URL Fixer.exe")

shell.CurrentDirectory = scriptDir

If fso.FileExists(exePath) Then
    shell.Run """" & exePath & """ --enable-startup", 0, False
End If
