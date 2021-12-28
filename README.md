# HubblePi

This software turns a Raspeberry Pi camera in a remote controlled camera for astrophotography. The typical application is to have a Raspberry Pi with HQ camera mounted on a telescope while the user controls the camera over the network. While all controlls of the camera are available the main focus is on long term exposures with full control of low level parameters (analog gain and shutter time) and getting raw image data. 

The software package consists of:
- A server script running on a Raspberry Pi (which has a camera) which alls repote control of the camera. The Raspberry Pi can run headless.
- A client software with GUI allowing the user to control the camera over TCP/IP.
- A preview GUI for the captured raw images.
- A command line tool to convert the raw images to FITS.
