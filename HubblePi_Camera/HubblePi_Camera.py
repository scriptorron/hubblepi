"""
this is the camera control script of HubblePi
"""

import sys
import io
import socketserver
import struct
import picamera
import threading
import copy
import time

import logging

import Statistics

MaxFrameRate = 15
MaxDynFrameRate = MaxFrameRate


class ReportingTimer(Statistics.StatisticsTimer):
    def __init__(self, name, batchsize=10, min_Intervall = 10.0):
        Statistics.StatisticsTimer.__init__(self, batchsize=batchsize)
        self.name = name
        self.min_Intervall = min_Intervall
        self.lastReport = time.time()

    def stop(self):
        Statistics.StatisticsTimer.stop(self)
        if time.time() - self.lastReport > self.min_Intervall:
            Report = self.name + ": act=%.3f, min=%.3f, mean=%.3f, max=%.3f" % (self.last(), self.min(), self.mean(), self.max())
            logging.info(Report)
            self.lastReport = time.time()



class Camera(object):

    def __init__(self):
        self.CaptureThread = None
        # camera
        self.PiCam = picamera.PiCamera(resolution='VGA', framerate=MaxFrameRate)
        #self.PiCam = picamera.PiCamera(resolution='VGA')
        #self.PiCam = picamera.PiCamera(resolution='VGA', framerate_range = (1.0, MaxFrameRate))
        #self.PiCam.framerate_range = (1.0/12, MaxFrameRate)
        # switch off the red LED
        self.PiCam.led = False
        #
        self.IsCapturing = False
        # storing state for temporary stop
        self.temp_DoRaw = False

    def __del__(self):
        logging.debug("entering Camera.__del__")
        self.StopCapture()

    def StartCapture(self):
        if not self.IsCapturing:
            self.CaptureThread = CaptureThread(self.PiCam)
            self.CaptureThread.start()
            self.IsCapturing = True

    def StopCapture(self):
        if self.IsCapturing:
            self.CaptureThread.DoRun.clear()
            self.CaptureThread.join()
            self.IsCapturing = False

    def TemporaryStopRecording(self):
        if self.IsCapturing:
            self.temp_DoRaw = self.CaptureThread.DoRaw.is_set()
            self.CaptureThread.DoRun.clear()
            self.CaptureThread.join()

    def TemporaryRestartRecording(self):
        if self.IsCapturing:
            self.CaptureThread = CaptureThread(self.PiCam)
            if self.temp_DoRaw:
                self.CaptureThread.DoRaw.set()
            else:
                self.CaptureThread.DoRaw.clear()
            self.CaptureThread.start()

    def RawOn(self):
        if self.IsCapturing:
            self.CaptureThread.DoRaw.set()

    def RawOff(self):
        if self.IsCapturing:
            self.CaptureThread.DoRaw.clear()

    def get_Frame(self):
        if not self.IsCapturing:
            return None
        else:
            ret = None
            got_Access = self.CaptureThread.FrameAccess.acquire(False)
            if got_Access:
                if self.CaptureThread.hasNewFrame:
                    ret = copy.deepcopy(self.CaptureThread.Frame)
                    self.CaptureThread.hasNewFrame = False
                self.CaptureThread.FrameAccess.release()
            return ret


class CaptureThread(threading.Thread):
    def __init__(self, PiCam):
        threading.Thread.__init__(self)
        self.Camera = PiCam
        self.CameraType = {
            'ov5647': 1,
            'imx219': 2,
            #'RP_testc': 3,  # this is the HQ camera!
            'imx477': 3,  # this is the HQ camera!
        }[self.Camera.revision]
        self.DoRun = threading.Event()
        self.DoRun.set()
        self.DoRaw = threading.Event()
        self.DoRaw.clear()
        self.IsIdle = threading.Event()
        self.IsIdle.set()
        # FIXME: needs lock
        self.Frame = ""
        self.hasNewFrame = False
        self.FrameCnt = 0
        self.FrameAccess = threading.Lock()
        # statistics
        self.StatStoreFrame = ReportingTimer("frame storage time")
        self.StatCaptureTime = ReportingTimer("frame capture time")

    def store_Frame(self, stream):
        self.FrameAccess.acquire(True)
        self.StatStoreFrame.start()
        ###########
        self.FrameCnt += 1
        size = stream.tell()
        CaptureType = b'C' if size > 6404096 else b'P'
        self.Frame = struct.pack(
            '<LLcbLLHfbffffB12s12s',
            size,
            self.FrameCnt,
            CaptureType,
            self.CameraType,
            self.Camera.shutter_speed,
            self.Camera.exposure_speed,
            self.Camera.iso,
            self.Camera.framerate,
            self.Camera.exposure_compensation,
            self.Camera.awb_gains[0], self.Camera.awb_gains[1],
            self.Camera.analog_gain,
            self.Camera.digital_gain,
            self.Camera.sensor_mode,
            ("%12s" % str(self.Camera.exposure_mode)).encode(),
            ("%12s" % str(self.Camera.awb_mode)).encode(),
        )
        stream.seek(0)
        self.Frame += stream.read(size)
        self.hasNewFrame = True
        ###########
        self.StatStoreFrame.stop()
        self.FrameAccess.release()


    def run(self):
        # signalize that it is running
        self.IsIdle.clear()
        self.StatCaptureTime.start()
        while self.DoRun.is_set():
            # continuous capture
            stream = io.BytesIO()
            if self.DoRaw.is_set():
                # raw mode
                for foo in self.Camera.capture_continuous(stream, format='jpeg', bayer=True, burst=True):
                    self.StatCaptureTime.stop()
                    self.StatCaptureTime.start()
                    self.store_Frame(stream)
                    stream.seek(0)
                    stream.truncate()
                    # check between the frames if to continue or to change mode
                    if (not self.DoRun.is_set()) or (not self.DoRaw.is_set()):
                        break
            else:
                # preview mode
                for foo in self.Camera.capture_continuous(stream, format='jpeg', bayer=False, burst=True):
                    self.StatCaptureTime.stop()
                    self.StatCaptureTime.start()
                    self.store_Frame(stream)
                    stream.seek(0)
                    stream.truncate()
                    # check between the frames if to continue or to change mode
                    if (not self.DoRun.is_set()) or (self.DoRaw.is_set()):
                        break
        # finished
        self.IsIdle.set()

#########################################################


class CommandServerHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        logging.debug("entered server.handle")
        # self.request is the TCP socket connected to the client
        Command = self.request.recv(1024).strip()  # max. 1024 bytes per command
        Command = Command.decode()
        logging.debug("Received command from client %s: >%s<" % (self.client_address[0], Command))
        # processing command
        if Command == "exit":
            global Cam
            Cam.StopCapture()
            # taken from: https://stackoverflow.com/questions/10085996/shutdown-socketserver-serve-forever-in-one-thread-python-application
            self.server._BaseServer__shutdown_request = True
        else:
            Response = self.ProcessCommand(Command)
            logging.debug("Sending response: >%s<" % Response)
            # send answer
            self.request.sendall(Response.encode())
        logging.debug("leaving server.handle")

    def ProcessCommand(self, Command):
        global Cam
        global MaxDynFrameRate
        if Command == "hello":
            return "HubblePi_Camera 2.0.0"
        #
        elif Command == "start_capture":
            Cam.StartCapture()
            return "ok"
        elif Command == "stop_capture":
            Cam.StopCapture()
            return "ok"
        elif Command == "raw_on":
            Cam.RawOn()
            return "ok"
        elif Command == "raw_off":
            Cam.RawOff()
            return "ok"
        # shutter speed
        elif Command == "info_shutter_speed_s":
            ShutterSpeeds = {
                'ov5647': "(0.0e-6, 6.0)",
                'imx219': "(0.0e-6, 10.0)",
                'imx477': "(0.0e-6, 200.0)",
            }[Cam.PiCam.revision]
            return ShutterSpeeds
        elif Command == "get_shutter_speed_s":
            return "%e" % (Cam.PiCam.shutter_speed * 1e-6)
        elif Command.startswith("set_shutter_speed_s "):
            ShutterSpeed = int(float(Command[20:]) * 1e6)
            FrameRate = min(1e6 / (ShutterSpeed + 150), MaxDynFrameRate)
            Cam.TemporaryStopRecording()
            Cam.PiCam.framerate = FrameRate
            Cam.PiCam.shutter_speed = ShutterSpeed
            Cam.TemporaryRestartRecording()
            return "ok"
        # analog_gain
        elif Command == "info_analog_gain":
            AnalogGains = {
                'ov5647': "(1.0, 8.0)",
                'imx219': "(1.0, 12.0)",
                'imx477': "(1.0, 16.0)",
            }[Cam.PiCam.revision]
            return AnalogGains
        elif Command == "get_analog_gain":
            return "%.3f" % Cam.PiCam.analog_gain
        elif Command.startswith("set_analog_gain "):
            Cam.PiCam.analog_gain = float(Command[16:])
            return "ok"
        # sensor_mode
        elif Command == "info_sensor_mode":
            SensorModes = {
                'ov5647': list(range(8)),
                'imx219': list(range(8)),
                'imx477': list(range(4)),
            }[Cam.PiCam.revision]
            return "%s" % SensorModes
        elif Command == "get_sensor_mode":
            return "%d" % Cam.PiCam.sensor_mode
        elif Command.startswith("set_sensor_mode "):
            Cam.TemporaryStopRecording()
            Cam.PiCam.sensor_mode = int(Command[16:])
            # picamera documentation states that sometime this must be done twice in a row
            Cam.PiCam.sensor_mode = int(Command[16:])
            Cam.TemporaryRestartRecording()
            return "ok"
        # ISO setting
        elif Command == "info_iso":
            # highest supported ISO is 1600, but analog_gain can go higher
            return "[0, 100, 200, 320, 400, 500, 640, 800, 1600]"
        elif Command == "get_iso":
            return "%d" % Cam.PiCam.iso
        elif Command.startswith("set_iso "):
            Cam.PiCam.iso = int(Command[8:])
            return "ok"
        # resolution
        elif Command == "info_resolution":
            return "[" + ", ".join(['"640x480"', '"1024x768"', '"%s"' % str(Cam.PiCam.MAX_RESOLUTION)]) + "]"
        elif Command == "get_resolution":
            return str(Cam.PiCam.resolution)
        elif Command.startswith("set_resolution "):
            Cam.TemporaryStopRecording()
            Cam.PiCam.resolution = Command[14:]
            Cam.TemporaryRestartRecording()
            return "ok"
        # exposure modes
        elif Command == "info_exposuremode":
            return "[" + ", ".join(['"%s"' % k for k in Cam.PiCam.EXPOSURE_MODES.keys()]) + "]"
        elif Command == "get_exposuremode":
            return Cam.PiCam.exposure_mode
        elif Command.startswith("set_exposuremode "):
            Cam.PiCam.exposure_mode = Command[17:]
            return "ok"
        # still_stats
        elif Command == "info_still_stats":
            return '[True, False]'
        elif Command == "get_still_stats":
            return str(Cam.PiCam.still_stats)
        elif Command.startswith("set_still_stats "):
            Cam.PiCam.still_stats = Command[16:] in ["True", "true", "TRUE"]
            return "ok"
        # AWB
        elif Command == "info_AWB_mode":
            return "[" + ", ".join(['"%s"' % k for k in Cam.PiCam.AWB_MODES.keys()]) + "]"
        elif Command == "get_AWB_mode":
            return Cam.PiCam.awb_mode
        elif Command.startswith("set_AWB_mode "):
            Cam.PiCam.awb_mode = Command[13:]
            return "ok"
        # meter modes
        elif Command == "info_metermode":
            return "[" + ", ".join(['"%s"' % k for k in Cam.PiCam.METER_MODES.keys()]) + "]"
        elif Command == "get_metermode":
            return Cam.PiCam.meter_mode
        elif Command.startswith("set_metermode "):
            Cam.PiCam.meter_mode = Command[14:]
            return "ok"
        # framerate
        elif Command == "info_framerate":
            return "(%d, %d)" % (0.001, Cam.PiCam.MAX_FRAMERATE)
        elif Command == "get_framerate":
            return "%d" % Cam.PiCam.framerate
        elif Command.startswith("set_framerate "):
            FrameRate = float(Command[14:])
            FrameRate = min(FrameRate, MaxFrameRate)
            MaxDynFrameRate = FrameRate
            Cam.TemporaryStopRecording()
            Cam.PiCam.framerate = FrameRate
            Cam.TemporaryRestartRecording()
            return "ok"
        # digital_gain
        elif Command == "info_digital_gain":
            return "(0.0, 1000.0)"
        elif Command == "get_digital_gain":
            return "%d" % Cam.PiCam.digital_gain
        elif Command.startswith("set_digital_gain "):
            Cam.PiCam.digital_gain = float(Command[17:])
            return "ok"
        # exposure compensation
        elif Command == "info_exposure_compensation":
            return "(-25, 25)"
        elif Command == "get_exposure_compensation":
            return "%d" % Cam.PiCam.exposure_compensation
        elif Command.startswith("set_exposure_compensation "):
            Cam.PiCam.exposure_compensation = int(Command[26:])
            return "ok"
        # AWB gains
        elif Command == "info_AWB_gain_0":
            return "(0.0, 8.0)"
        elif Command == "get_AWB_gain_0":
            return "%f" % Cam.PiCam.awb_gains[0]
        elif Command.startswith("set_AWB_gain_0 "):
            Cam.PiCam.awb_gains = (float(Command[15:]), Cam.PiCam.awb_gains[1])
            return "ok"
        elif Command == "info_AWB_gain_1":
            return "(0.0, 8.0)"
        elif Command == "get_AWB_gain_1":
            return "%f" % Cam.PiCam.awb_gains[1]
        elif Command.startswith("set_AWB_gain_1 "):
            Cam.PiCam.awb_gains = (Cam.PiCam.awb_gains[0], float(Command[15:]))
            return "ok"
        # image effects
        elif Command == "info_imageeffects":
            return "[" + ", ".join(['"%s"' % k for k in Cam.PiCam.IMAGE_EFFECTS.keys()]) + "]"
        elif Command == "get_imageeffects":
            return Cam.PiCam.image_effect
        elif Command.startswith("set_imageeffects "):
            Cam.PiCam.image_effect = Command[17:]
            return "ok"
        # DRC strength
        elif Command == "info_drc_strength":
            return "[" + ", ".join(['"%s"' % k for k in Cam.PiCam.DRC_STRENGTHS.keys()]) + "]"
        elif Command == "get_drc_strength":
            return Cam.PiCam.drc_strength
        elif Command.startswith("set_drc_strength "):
            Cam.PiCam.drc_strength = Command[17:]
            return "ok"
        # image denoise
        elif Command == "info_image_denoise":
            return '[True, False]'
        elif Command == "get_image_denoise":
            return str(Cam.PiCam.image_denoise)
        elif Command.startswith("set_image_denoise "):
            Cam.PiCam.image_denoise = Command[18:] in ["True", "true", "TRUE"]
            return "ok"
        # error
        return "UNKNOWN COMMAND (%s)" % str(Command)


class CommandServerThread(threading.Thread):
    def __init__(self, Host, Port):
        threading.Thread.__init__(self, name="CommandServerThread")
        self.Host = Host
        self.Port = Port

    def run(self):
        self.Server = socketserver.TCPServer((self.Host, self.Port), CommandServerHandler)
        try:
            self.Server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Received KeyboardInterrupt (handler 2)")
        finally:
            # Clean-up server (close socket, etc.)
            self.Server.server_close()

###################################################

class StreamingServerHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    StatFrameSendTime = ReportingTimer("frame transmission time")

    def handle(self):
        # self.request is the TCP socket connected to the client
        Command = self.request.recv(1024).strip()  # max. 1024 bytes per command
        Command = Command.decode()
        #logging.debug("Received streaming command from client %s: >%s<" % (self.client_address[0], Command))
        # processing command
        if Command == "GET":
            global Cam
            Frame = Cam.get_Frame()
            if Frame is None:
                # no new frame available or camera not capturing
                answ = struct.pack("<L", 0)
                self.request.sendall(answ)
                #logging.debug("Streaming answered with %d bytes: >%s<" % (len(answ), str(answ)))
            else:
                self.StatFrameSendTime.start()
                self.request.sendall(Frame)
                #logging.debug("Streaming answered with %d bytes" % (len(Frame)))
                self.StatFrameSendTime.stop()
        else:
            logging.error("Streaming server received unknown command: >%s<" % Command)

class StreamingServerThread(threading.Thread):
    def __init__(self, Host, Port):
        threading.Thread.__init__(self, name="StreamingServerThread")
        self.Host = Host
        self.Port = Port

    def run(self):
        self.Server = socketserver.TCPServer((self.Host, self.Port), StreamingServerHandler)
        self.Server.serve_forever()


####################################################

def main():
    # command line parameter
    import argparse
    parser = argparse.ArgumentParser(description="HubblePi camera server, v2")
    parser.add_argument('-v', '--verbose', choices=['warn', 'error', 'info', 'debug'], default='error',
                        help='message verbosity level (default: error)')
    parser.add_argument('-c', '--commandPort', type=int, default=60000,
                        help='port number for commands (default: %d)' % 60000)
    parser.add_argument('-s', '--streamingPort', type=int, default=60001,
                        help='port number for commands (default: %d)' % 60001)
    args = parser.parse_args()
    # logging
    if (args.verbose == "debug"):
        logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.DEBUG)
    elif (args.verbose == "info"):
        logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.INFO)
    elif (args.verbose == "error"):
        logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.ERROR)
    else:
        logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.WARN)
    #
    Host = ""
    CommandPort = args.commandPort
    StreamingPort = args.streamingPort
    logging.debug("binding command port to %s:%d" % (Host, CommandPort))
    logging.debug("binding streaming port to %s:%d" % (Host, StreamingPort))

    # run application
    global Cam
    logging.debug("creating camera instance")
    Cam = Camera()
    #
    logging.debug("creating streaming server")
    StreamingServer = StreamingServerThread(Host, StreamingPort)
    StreamingServer.start()
    logging.debug("creating command server")
    CommandServer = CommandServerThread(Host, CommandPort)
    CommandServer.start()
    try:
        while CommandServer.is_alive():
            time.sleep(0.2)
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt")
        # terminate command server
        CommandServer.Server._BaseServer__shutdown_request = True
        logging.debug("command server stopped")
    finally:
        logging.debug("stopping capture")
        Cam.StopCapture()
        # terminate streaming server
        logging.debug("stopping streaming server")
        StreamingServer.Server._BaseServer__shutdown_request = True
    # finish
    logging.debug("exit")
    sys.exit(0)

if __name__ == '__main__':
    main()