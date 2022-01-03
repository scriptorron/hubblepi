@echo off

echo This was used for initially setting up the HubblePi environment.
echo DO NOT USE THIS TO SETUP YOUR ENVIRONMENT!
echo It is better you run:
echo     conda env create -f environment.yml

pause

call conda create -n HubblePi python=3.8

call conda activate HubblePi
call conda install numpy scipy pillow astropy send2trash imageio pandas pyqt pyqtgraph pyinstaller

call conda env export > environment.yml
rem pip install PyQt5==5.15.4 pyqt5-tools==5.15.4.3.2
rem pip install -r requirements.txt

