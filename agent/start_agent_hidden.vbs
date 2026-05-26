' 自动化工厂设备Agent后台启动脚本
' 无控制台窗口运行

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c start_agent.bat", 0, False
Set WshShell = Nothing
