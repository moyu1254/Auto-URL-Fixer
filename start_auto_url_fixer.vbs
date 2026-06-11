Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.Run "cmd /c ""where pyw >nul 2>nul && pyw -3 -m auto_url_fixer || where pythonw >nul 2>nul && pythonw -m auto_url_fixer || where py >nul 2>nul && py -3 -m auto_url_fixer || python -m auto_url_fixer""", 0, False
