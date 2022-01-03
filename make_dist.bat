del /S /Q dist\HubblePi > NUL:
rd /S /Q dist\HubblePi

pyinstaller HubblePi.spec
if %errorlevel% neq 0 exit /b %errorlevel%

rem del /S /Q build > NUL:
rem rd /S /Q build
