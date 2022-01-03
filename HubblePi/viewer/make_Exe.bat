del /S /Q dist\HubblePi_Viewer > NUL:
rd /S /Q dist\HubblePi_Viewer

pyinstaller HubblePi_Viewer.spec
if %errorlevel% neq 0 exit /b %errorlevel%

del /S /Q build > NUL:
rd /S /Q build
