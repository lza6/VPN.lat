@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
set ICU_ROOT=C:\Users\Administrator.DESKTOP-EGNE9ND\Desktop\vpnlat_ws\blutter\external\icu-windows
python "C:\Users\Administrator.DESKTOP-EGNE9ND\Desktop\vpnlat_ws\blutter\blutter.py" "C:\Users\Administrator.DESKTOP-EGNE9ND\Desktop\vpnlat_ws\ext\lib\arm64-v8a" "C:\Users\Administrator.DESKTOP-EGNE9ND\Desktop\vpnlat_ws\blutter_out"
