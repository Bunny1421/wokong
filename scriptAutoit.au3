#RequireAdmin
HotKeySet("{ESC}", "Terminate")

Func Terminate()
    ToolTip("โปรแกรมถูกหยุดการทำงานด้วยปุ่ม ESC")
    Exit 0
EndFunc

Global $hPipe = _NamedPipe_Connect("\\.\pipe\ColorDetectionPipe")

Func _NamedPipe_Connect($sPipeName)
    Local $hPipe = DllCall("kernel32.dll", "handle", "CreateFile", "str", $sPipeName, "dword", 0x80000000, "dword", 3, "ptr", 0, "dword", 3, "dword", 0, "ptr", 0)
    If @error Or $hPipe[0] = -1 Then
        MsgBox(16, "Error", "ไม่สามารถเชื่อมต่อ Named Pipe ได้")
        Exit
    EndIf
    Return $hPipe[0]
EndFunc

While True
    Local $sData = _NamedPipe_Read($hPipe)
    If $sData = "7" Then
        Send("{HOME}")
	ElseIf $sData =  "9" Then
		Send("{PGUP}")
	ElseIf $sData = "4" Then
		Send("{LEFT}")
	ElseIf $sData = "6" Then
		Send("{RIGHT}")
	ElseIf $sData = "1" Then
		Send("{END}")
	ElseIf $sData = "3" Then
		Send("{PGDN}")
	ElseIf $sData = "SPACE" Then
		Send("{SPACE}")
    EndIf
WEnd

Func _NamedPipe_Read($hPipe)
    Local $buffer = DllStructCreate("char[16]")
    Local $aResult = DllCall("kernel32.dll", "bool", "ReadFile", "handle", $hPipe, "ptr", DllStructGetPtr($buffer), "dword", 16, "dword*", 0, "ptr", 0)

    If @error Or $aResult[0] = 0 Then MsgBox(16, "Error", "ไม่สามารถเชื่อมต่อ Named Pipe ได้") Return ""
    Return StringStripWS(DllStructGetData($buffer, 1), 3)
EndFunc
