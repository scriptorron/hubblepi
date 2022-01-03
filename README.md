# HubblePi

This software turns a Raspeberry Pi camera in a remote controlled camera for astrophotography. 
The typical application is to have a Raspberry Pi with HQ camera mounted on a telescope while the user controls
the camera over the network. All controlls of the camera are available but the main focus is on long term
exposures with full control of low level parameters (analog gain, shutter time) and getting raw image data.
Other applications could be:
- low light photography (for instance light emission microscopy),
- time laps photography,
- ...

The software package consists of:
- A server script running on a Raspberry Pi (which has a camera). This script receives commands to control
  the camera. The Raspberry Pi can run headless.
- A client software with GUI allowing the user to control the camera over TCP/IP.
- A preview GUI for the captured raw images.
- A command line tool to convert the raw images to FITS.

Raspberry Pi cameras V1 and HQ are supported, but the HQ camera is highly recommended because of its much better
performance (higher sensitivity, lower noise, larger dynamic range, longer exposure times, higher resolution).

**ATTENTION:**

**The camera server script does not use any authentication to protect against intruders.**
**Use the server script behind a firewall or in an isolated network!**

## Installation

### On Raspberry Pi

1. install `python3` and `pip3` on your Raspberry Pi
2. copy folder `HubblePi_Camera` to your raspberry Pi
3. install required Python libraries on your Raspberry Pi: 
   ```
   cd HubblePi_Camera
   pip install -r requirements.txt
   ```

### On Client Computer

#### Development Environment
You will need this setup when you want to
- change the source code or
- compile the code by yourself or
- execute the latest Python source code.

I use the Miniconda distribution on 64bit Windows (https://docs.conda.io/en/latest/miniconda.html)
because it makes less trouble with incompatible packages.
Any other Python3 installation will likely also work but needs installation commands to be modified.

Do the following steps:
1. Install Miniconda.
2. Setup an isolated environment `HubblePi` and install required libraries:
   ```
   conda env create -f environment.yml
   ```
   (Conda will ask if you want to proceed installation. Answer with "y".)
3. Change to `HubblePi` environment (if not already done) with `conda ativate HubblePi`
   and install `HubblePi` library:
   ```
   pip install -e .
   ```

After that you have will have the `HubblePi_Capture`, `HubblePi_Viewer` and `HubblePi_RPi2Fits` commands available
in the `HubblePi` environment.

#### Precompiled Software
TODO 

## Usage

1. Remote login on your Raspberry Pi and start the camera server:
```
cd HubblePi
python3 HubblePi_Camera.py -v debug
```
2. Start `HubblePi_Capture` on your client computer, connect to your Raspberry Pi (you will need its network name
   for that), adjust camera settings and take pictures.
   
Please see Wiki (TODO) for further documentation.

