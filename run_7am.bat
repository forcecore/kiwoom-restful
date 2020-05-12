@echo off
echo Server script start

REM cd to where this batch file is.
REM Running a batch file as Administrator will get you into system32 so...
REM we need to change directory first.
REM The variable %~dp0 holds this information.
cd %~dp0

REM You need to copy, modify activate.bat
REM if you installed anaconda somewhere else.
call activate.bat

REM Tradable items get updated at certain hour of the day.
REM We need to wait a little while.
REM I intend to run this at 6:00 before leaving home.
python wait7am.py

REM Run the server
python kiwoom_restful_server.py

REM Let's see the output
pause
