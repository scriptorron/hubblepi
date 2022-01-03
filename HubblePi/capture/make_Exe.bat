del /S /Q dist\HubblePi_Capture > NUL:
rd /S /Q dist\HubblePi_Capture

del /S /Q build > NUL:
rd /S /Q build

call conda env export > environment.yml

pyinstaller HubblePi_Capture.spec
if %errorlevel% neq 0 exit /b %errorlevel%

