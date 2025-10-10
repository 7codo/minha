@echo off
:loop
echo [%date% %time%] Running ANEM Automation...
call "C:\Users\Admin\Desktop\code\python\scripts\minha\run_project.bat"
echo Waiting 5 minutes...
timeout /t 15 /nobreak >nul
goto loop
