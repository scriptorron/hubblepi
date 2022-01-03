
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
import sys, os
import io
import socket
import struct
import PIL
import PIL.Image
import numpy as np
import pyqtgraph as pg
import time, datetime
import json
import copy
import re
import itertools

import logging

from HubblePi.capture import Statistics
import HubblePi.Toolbox
from HubblePi.capture import ConnectDlg_ui
from HubblePi.capture import SettingNameDlg_ui
from HubblePi.capture import Capture_ui


# suppress DEBUG log messages from PIL
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

ShowMenuBar = False # hide menu bar with item for automated dark noise measurement
theme_selection = "Dark" # "Dark", "Light"

# TODO: move presets in an AppData folder (or user home)
if hasattr(sys, "frozen"):
    # compiled code
    PresetFolder = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "presets")
else:
    PresetFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets")

#@staticmethod
def My_qWait(t):
    end = time.time() + t
    while time.time() < end:
        QtWidgets.QApplication.processEvents()



class ReportingTimer(Statistics.StatisticsTimer, QtCore.QObject):
    sigReport = QtCore.pyqtSignal(str)

    def __init__(self, name, batchsize=10, min_Intervall = 10.0):
        Statistics.StatisticsTimer.__init__(self, batchsize=batchsize)
        QtCore.QObject.__init__(self)
        self.name = name
        self.min_Intervall = min_Intervall
        self.lastReport = time.time()

    def stop(self):
        Statistics.StatisticsTimer.stop(self)
        if time.time() - self.lastReport > self.min_Intervall:
            Report = self.name + ": act=%.3f, min=%.3f, mean=%.3f, max=%.3f" % (self.last(), self.min(), self.mean(), self.max())
            logging.info(Report)
            self.sigReport.emit(Report)
            self.lastReport = time.time()


class ConnectDlg(QtWidgets.QDialog, ConnectDlg_ui.Ui_Dialog):
    def __init__(self, IP, CommandPort, StreamingPort, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lineEdit_IP.setText(IP)
        self.spinBox_CommandPort.setValue(CommandPort)
        self.spinBox_StreamingPort.setValue(StreamingPort)


class SettingNameDlg(QtWidgets.QDialog, SettingNameDlg_ui.Ui_Dialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)


class MainWin(QtWidgets.QMainWindow):
    sigBildInfo = QtCore.pyqtSignal(dict)


    def __init__(self):
        super(MainWin, self).__init__()
        pg.setConfigOption('background', pg.mkColor(100, 0, 0))
        self.ui = Capture_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.menubar.setVisible(ShowMenuBar)
        self.ui.plainTextEdit_Log.setMaximumBlockCount(100)
        self.ui.ImageView_Preview.setLevels(0, 255)
        self.ui.ImageView_Preview.ui.roiBtn.hide()
        self.ui.ImageView_Preview.ui.menuBtn.hide()
        PlainTextEdit_ImageInfosFont = QtGui.QFont("Monospace");
        PlainTextEdit_ImageInfosFont.setStyleHint(QtGui.QFont.TypeWriter);
        self.ui.plainTextEdit_ImageInfos.setFont(PlainTextEdit_ImageInfosFont)
        # settings
        self.PersistentSettings = QtCore.QSettings()
        self.PresetFolder = PresetFolder
        # states
        self.PreviewImageStream = None
        self.PreviewImageInfo = None
        # timer for statistics
        self.StatTimers = {
            "onNewImage": ReportingTimer("time for showing and saving image"),
            "onBildInfo": ReportingTimer("time for showing image info"),
        }
        self.StatTimers["onNewImage"].sigReport.connect(self.AddLogMessage)
        # Signal Proxy fuer Bildinfos
        self.BildInfoProxy = pg.SignalProxy(self.sigBildInfo, rateLimit=4, slot=self.onBildInfo)
        # connect with camera server
        self.IsConnected = False
        while not self.IsConnected:
            CDlg = ConnectDlg(
                IP = self.PersistentSettings.value("CameraServer", "raspicam.local"),
                CommandPort = self.PersistentSettings.value("CommandPort", 60000),
                StreamingPort = self.PersistentSettings.value("StreamingPort", 60001),
            )
            if CDlg.exec_():
                self.ServerIP = CDlg.lineEdit_IP.text()
                self.PersistentSettings.setValue("CameraServer", self.ServerIP)
                self.ServerCommandPort = CDlg.spinBox_CommandPort.value()
                self.PersistentSettings.setValue("CommandPort", self.ServerCommandPort)
                self.ServerStreamingPort = CDlg.spinBox_StreamingPort.value()
                self.PersistentSettings.setValue("StreamingPort", self.ServerStreamingPort)
                try:
                    Resp = self.CameraCommand("hello")
                except (socket.gaierror, socket.error):
                    QtWidgets.QMessageBox.critical(self, "Connection Error",
                                                   "Could not connect to server.",
                                                   QtWidgets.QMessageBox.NoButton, QtWidgets.QMessageBox.Ok)
                else:
                    if Resp.startswith("HubblePi_Camera"):
                        self.AddLogMessage("Connected with %s." % Resp)
                        self.IsConnected = True
                    else:
                        QtWidgets.QMessageBox.critical(self, "Connection Error",
                                                       "Could not find the HubblePi Camera on this server.",
                                                       QtWidgets.QMessageBox.NoButton, QtWidgets.QMessageBox.Ok)
            else:
                # TODO: is this the right way to close the window?
                sys.exit(0)
        #
        self.RxLastFrame = None # time stamp of last received frame
        self.RxFramePeriod = None # smoothed frame rate
        self.LastSavedImageAt = 0.0
        #
        self.isRecording = False
        self.SaveImagesFolder = self.PersistentSettings.value("ImageFolder", "./Images")
        # camera controls
        self.CameraParamTree = pg.parametertree.ParameterTree()
        #self.AlgorithmParamTree.header().setStretchLastSection(False)
        #self.AlgorithmParamTree.resizeColumnToContents(0)
        #self.AlgorithmParamTree.resizeColumnToContents(1)
        # for any reason the last column has a larger width (columnWidth(1)) than needed
        #self.AlgorithmParamTree.setFixedWidth(self.AlgorithmParamTree.columnWidth(0) + self.AlgorithmParamTree.columnWidth(1) * 30.0/43 + 5)
        self.CameraParamTreeLayout = QtWidgets.QVBoxLayout(self.ui.widget_Params)
        self.CameraParamTreeLayout.addWidget(self.CameraParamTree)
        self.CameraParams = None
        #self.SetCameraControls(self.AllCameraControls)
        # settings
        self.ui.comboBox_LoadSettings.currentIndexChanged.connect(self.LoadSetting)
        self.fillLoadSettings()
        self.LoadSettingsFile(os.path.join(self.PresetFolder, "default.set"))
        # start stream receiver
        self.StreamRx = StreamReceiver(ServerIP=self.ServerIP, Port=self.ServerStreamingPort)
        self.StreamRx.sigImage.connect(self.onNewImage)
        self.StreamRx.StatFrameTimer.sigReport.connect(self.AddLogMessage)
        self.StreamRx.start()
        # start streaming
        self.CameraCommand("raw_off")
        self.CameraCommand("start_capture")
        # connect
        self.ui.comboBox_PreviewRot.currentIndexChanged.connect(self.ShowPreview)
        self.ui.checkBox_PreviewFlipH.toggled.connect(self.ShowPreview)
        self.ui.checkBox_PreviewFlipV.toggled.connect(self.ShowPreview)
        self.ui.comboBox_RawPreviewMode.currentIndexChanged.connect(self.ShowPreview)



    @QtCore.pyqtSlot()
    def closeEvent(self, event):
        logging.debug("entering closeEvent")
        # The window is about to close. Here is a better place to clean up than in the __del__ method!
        if self.IsConnected:
            # stop stream receiver
            self.StreamRx.stop()
            logging.debug("waiting for StreamRx to stop")
            self.StreamRx.wait()
            # stop camera
            self.CameraCommand("stop_capture")
        # proceed with close
        event.accept()

    def AddLogMessage(self, Msg, Severity="INFO"):
        if Severity=="ERROR":
            Html = '<font color="red">ERROR: %s</font>' % Msg
        elif Severity=="WARN":
            Html = '<font color="orange">WARN: %s</font>' % Msg
        else:
            #Html = '<font color="black">%s</font>' % Msg
            Html = Msg
        self.ui.plainTextEdit_Log.appendHtml(Html)
        self.ui.statusbar.showMessage(Msg)

    def fillLoadSettings(self):
        self.ui.comboBox_LoadSettings.currentIndexChanged.disconnect()
        Files = [f for f in os.listdir(self.PresetFolder) if re.match(".*\.set", f)]
        for File in Files:
            FN = os.path.join(self.PresetFolder, File)
            logging.debug("probing settings file %s" % FN)
            try:
                with open(FN, "rb") as fh:
                    Setting = json.load(fh)
                self.ui.comboBox_LoadSettings.addItem("%s (%s)" % (Setting["name"], File), userData=File)
            except ValueError:
                logging.error("setting file %s is not a valid JSON" % FN)
                pass
        self.ui.comboBox_LoadSettings.currentIndexChanged.connect(self.LoadSetting)


    def LoadSetting(self):
        Idx = self.ui.comboBox_LoadSettings.currentIndex()
        File = self.ui.comboBox_LoadSettings.itemData(Idx)
        FN = os.path.join(self.PresetFolder, File)
        self.LoadSettingsFile(FN)


    def LoadSettingsFile(self, FileName):
        self.AddLogMessage("Loading setting file %s" % FileName)
        with open(FileName, "rb") as fh:
            Setting = json.load(fh)
        self.SetCameraControls(Setting["controls"])


    def CameraCommand(self, Command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ServerIP, self.ServerCommandPort))
        s.sendall(bytes(Command, encoding="ascii"))
        Resp = s.recv(1024).decode("ascii")
        s.shutdown(2)
        s.close()
        self.AddLogMessage(f'Camera command "{Command}", response "{Resp}"')
        return Resp

    def GetTimeStamp(self):
        return datetime.datetime.now().strftime("%y%m%dT%H%M%S%f")[:-3]

    def ShowPreview(self):
        if self.PreviewImageStream is not None:
            self.PreviewImageStream.seek(0)
            if self.ui.checkBox_RawPreview.isChecked() and (self.PreviewImageInfo["CaptureType"] == 'C'):
                # show RAW preview
                img = self.PreviewImageStream.getvalue()
                #logging.debug(f'RAW img: {len(img)} of {type(img)}')
                img = HubblePi.Toolbox.ExtractRawFromJpgData(img, CameraType=self.PreviewImageInfo["CameraType"])
                BayerChannels = {
                    1: {"G1": (0, 0), "B": (0, 1), "R": (1, 0), "G2": (1, 1)},  # GBRG
                    2: {"G1": (0, 0), "B": (0, 1), "R": (1, 0), "G2": (1, 1)},  # GBRG
                    3: {"B": (0, 0), "G1": (0, 1), "G2": (1, 0), "R": (1, 1)},  # BGGR
                }[self.PreviewImageInfo["CameraType"]]
                RawPreviewMode = self.ui.comboBox_RawPreviewMode.currentText()
                # logging.debug(f'RawPreviewMode: {RawPreviewMode} ({type(RawPreviewMode)})')
                #logging.debug(f'JPG img: {img.shape} of {img.dtype}')
                if RawPreviewMode == "gray":
                    img = img[0::2, :] + img[1::2, :]
                    img = img[:, 0::2] + img[:, 1::2]
                    img = img // 4
                elif RawPreviewMode == "red":
                    img = img[BayerChannels["R"][0]::2, BayerChannels["R"][1]::2]
                elif RawPreviewMode == "green 1":
                    img = img[BayerChannels["G1"][0]::2, BayerChannels["G1"][1]::2]
                elif RawPreviewMode == "green 2":
                    img = img[BayerChannels["G2"][0]::2, BayerChannels["G2"][1]::2]
                elif RawPreviewMode == "blue":
                    img = img[BayerChannels["B"][0]::2, BayerChannels["B"][1]::2]
                else:
                    raise NotImplementedError
            else:
                # show JPG preview
                img = PIL.Image.open(self.PreviewImageStream)
                img = np.asarray(img)
            #logging.debug(f'PreviewImage: {img.shape} of {img.dtype}')
            Rot = self.ui.comboBox_PreviewRot.currentText()
            if Rot != "0deg":
                k = {"90deg": 3, "180deg": 2, "270deg": 1}[Rot]
                img = np.rot90(img, k=k)
            if self.ui.checkBox_PreviewFlipH.isChecked():
                img = np.flipud(img)
            if self.ui.checkBox_PreviewFlipV.isChecked():
                img = np.fliplr(img)
            # show preview image
            self.ui.ImageView_Preview.setImage(img, autoLevels=False,
                                               autoHistogramRange=False,
                                               #levelMode="rgb",
                                               autoRange=False,
                                               )


    @QtCore.pyqtSlot(dict)
    def onNewImage(self, D):
        self.StatTimers["onNewImage"].start()
        self.StreamRx.DiscardFrames = True
        image_stream  = D["stream"]
        image_stream.seek(0)
        info = D["info"]
        # save image?
        if self.isRecording:
            if (time.time() - self.LastSavedImageAt) > self.ui.doubleSpinBox_TimeLapse.value():
                if (
                        (self.ui.checkBox_RecordRaw.isChecked() and (info["CaptureType"] == 'C')) or
                        ((not self.ui.checkBox_RecordRaw.isChecked()) and (info["CaptureType"] == 'P'))
                ):
                    self.LastSavedImageAt = time.time()
                    FileName = os.path.join(self.SaveImagesFolder,
                                            self.ui.lineEdit_FileName.text() + "_" + self.GetTimeStamp())
                    with open(FileName+".jpg", "wb") as FH:
                        FH.write(image_stream.getvalue())
                    #
                    info["comment"] = self.ui.lineEdit_ImageComment.text()
                    with open(FileName+".info", "w") as FH:
                        json.dump(info, FH, indent=2)
                    #
                    self.RecordedImageCounter += 1
                    self.ui.label_RecordedImageCounter.setText("%d" % self.RecordedImageCounter)
                    #self.ui.statusbar.showMessage("Recording JPG, %d of %d" % (self.RecordedImageCounter, self.ui.spinBox_nImagesToRecord.value()))
                if self.RecordedImageCounter >= self.ui.spinBox_nImagesToRecord.value():
                    self.on_pushButton_StopRec_clicked()
        # preview image
        self.PreviewImageStream = image_stream
        self.PreviewImageInfo = info
        self.ShowPreview()
        # calculate received frame rate
        if self.RxLastFrame is None:
            self.RxFramePeriod = None
        elif self.RxFramePeriod is None:
            self.RxFramePeriod = info["TimeStamp"] - self.RxLastFrame
        else:
            self.RxFramePeriod = 0.75 * self.RxFramePeriod + 0.25 * (info["TimeStamp"] - self.RxLastFrame)
        self.RxLastFrame = info["TimeStamp"]
        if self.RxFramePeriod is None:
            info["RxFrameRate"] = 0.0
        else:
            if self.RxFramePeriod > 0:
                info["RxFrameRate"] = 1.0 / self.RxFramePeriod
            else:
                info["RxFrameRate"] = 999.0
        #
        #info["Resolution"] = "%dx%d" % (img.shape[1], img.shape[0])
        # store frame info for automation
        self.FrameInfo = info
        #
        self.sigBildInfo.emit(info)
        #
        self.StreamRx.DiscardFrames = False
        self.StatTimers["onNewImage"].stop()


    def onBildInfo(self, evt):
        self.StatTimers["onBildInfo"].start()
        D = evt[0]
        self.ui.plainTextEdit_ImageInfos.setPlainText(
            "frame number:   %d\n" % (D["FrameCnt"]) +
            "capture number: %d (%d)\n" % (D["CaptureCnt"], D["CaptureCnt"]-D["FrameCnt"]) +
            "type:           %s\n" % (D["CaptureType"]) +
            "sensor mode:    %d\n" % (D["SensorMode"]) +
            "exp. mode:      %s\n" % (D["ExpMode"].strip()) +
            "shutter speed:  %.3f ms\n" % (D["ShutterSpeed"] / 1000) +
            "exposure speed: %.3f ms\n" % (D["ExposureSpeed"] / 1000) +
            "ISO:            %d\n" % (D["ISO"]) +
            "analog gain:    %.3f\n" % (D["AnalogGain"]) +
            "frame rate:     %.3f (%.3f)\n" % (D["FrameRate"], D["RxFrameRate"]) +
            #"resolution:     %s\n" % (D["Resolution"]) +
            "exp. comp.:     %d\n" % (D["ExposureCompensation"]) +
            "AWB mode:       %s\n" % (D["AwbMode"].strip()) +
            "AWG gains:      %.3f, %.3f\n" % (D["AWB_Gain[0]"], D["AWB_Gain[1]"]) +
            "digital gain:   %.3f\n" % (D["DigitalGain"]) +
            "discard. frames:%d" % (D["DiscardedFrames"])
        )
        # status bar
        StsMsg = "Frame %d, Exposure speed %d us, Analog gain %.3f" % (D["FrameCnt"], D["ExposureSpeed"], D["AnalogGain"])
        if self.isRecording:
            self.ui.statusbar.showMessage(StsMsg + ", Recording %s %d of %d" % (
                "RAW" if self.ui.checkBox_RecordRaw.isChecked() else "JPG",
                self.RecordedImageCounter, self.ui.spinBox_nImagesToRecord.value()))
        else:
            self.ui.statusbar.showMessage(StsMsg)
        self.StatTimers["onBildInfo"].stop()


    @QtCore.pyqtSlot()
    def on_pushButton_Folder_clicked(self):
        ImageFolder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                 "Folder to store images..",
                                                                 self.SaveImagesFolder)
        if ImageFolder != '':
            self.SaveImagesFolder = ImageFolder
            self.PersistentSettings.setValue("ImageFolder", ImageFolder)

    @QtCore.pyqtSlot()
    def on_pushButton_StartRec_clicked(self):
        self.AddLogMessage("Starting recording.", "INFO")
        self.ui.pushButton_StartRec.setEnabled(False)
        self.ui.pushButton_StartRec.setStyleSheet('background-color: red;')
        self.ui.pushButton_StopRec.setEnabled(True)
        self.ui.checkBox_RecordRaw.setEnabled(False)
        self.RecordedImageCounter = 0
        self.ui.label_RecordedImageCounter.setText("%d" % self.RecordedImageCounter)
        self.LastSavedImageAt = 0.0
        if self.ui.checkBox_RecordRaw.isChecked():
            self.CameraCommand("raw_on")
        self.isRecording = True


    @QtCore.pyqtSlot()
    def on_pushButton_StopRec_clicked(self):
        self.isRecording = False
        if not self.ui.checkBox_RawPreview.isChecked():
            self.CameraCommand("raw_off")
        self.ui.pushButton_StopRec.setEnabled(False)
        self.ui.pushButton_StartRec.setEnabled(True)
        self.ui.pushButton_StartRec.setStyleSheet(None)
        self.ui.checkBox_RecordRaw.setEnabled(True)
        QtWidgets.QApplication.beep()
        self.AddLogMessage("Finished recording.", "INFO")

    @QtCore.pyqtSlot(bool)
    def on_checkBox_RawPreview_toggled(self, checked):
        if not self.isRecording:
            if checked:
                self.CameraCommand("raw_on")
            else:
                self.CameraCommand("raw_off")
        self.ShowPreview()

    def SetCameraControls(self, CameraControls):
        """
        remove the present camera controls by the new ones

        :param CameraControls: new list of camera controls
        """
        if self.CameraParams is not None:
            # disconnect old signals before removing the params
            for p in self.CameraParams:
                p.sigValueChanged.disconnect()
        #
        self.CameraControls = []
        #
        for CameraControl in CameraControls:
            Info = self.CameraCommand("info_"+CameraControl["name"])
            Vals = eval(Info, {}, {})
            if "type" not in CameraControl:
                if type(Vals) == list:
                    CameraControl["type"] = "list"
                    CameraControl["values"] = Vals
                elif type(Vals) == tuple:
                    CameraControl["type"] = {
                        float: "float",
                        int: "int",
                    }[type(Vals[0])]
                    CameraControl["limits"] = Vals
                else:
                    raise ValueError("Unknown control parameter type: %s" % str(Vals))
            if "value" not in CameraControl:
                # read actual value from camera
                Get = self.CameraCommand("get_" + CameraControl["name"])
                try:
                    Val = eval(Get, {}, {})
                except:
                    Val = str(Get)
                CameraControl["value"] = Val
            else:
                # set value to camera
                logging.debug("preset camera parameter %s: %s" % (CameraControl["name"], CameraControl["value"]))
                self.AddLogMessage("Preset camera parameter %s: %s" % (CameraControl["name"], CameraControl["value"]))
                Resp = self.CameraCommand("set_%s %s" % (CameraControl["name"], CameraControl["value"]))
                logging.debug("  Response: %s" % Resp)
            self.CameraControls.append(CameraControl)
        #
        self.CameraParams = pg.parametertree.Parameter.create(name='params', type='group', children=self.CameraControls)
        self.CameraParamTree.setParameters(self.CameraParams, showTop=False)
        for p in self.CameraParams:
            p.sigValueChanged.connect(self.CameraParamChanged)


    #@QtCore.pyqtSlot()
    #def on_pushButton_CameraReceiveSettings_clicked(self):
    #    logging.debug("receiving camera settings")
    #    for i in range(len(self.CameraControls)):
    #        self.CameraControls[i].pop("value")
    #    self.SetCameraControls(self.CameraControls)


    def CameraParamChanged(self, Param):
        logging.debug("camera parameter %s changed: %s" % (Param.name(), Param.value()))
        self.AddLogMessage("Camera parameter %s changed: %s" % (Param.name(), Param.value()))
        Resp = self.CameraCommand("set_%s %s" % (Param.name(), Param.value()))
        logging.debug("  Response: %s" % Resp)


    @QtCore.pyqtSlot()
    def on_pushButton_CameraSaveSettings_clicked(self):
        logging.debug("on_pushButton_CameraSaveSettings_clicked")
        LastFileName = self.PersistentSettings.value("settings_file", ".")
        fn = QtWidgets.QFileDialog.getSaveFileName(self, "Save settings..", LastFileName, "Settings Files (*.set)")[0]
        if fn == '':
            return
        self.PersistentSettings.setValue("settings_file", fn)
        #
        Controls = copy.deepcopy(self.CameraControls)
        for i in range(len(Controls)):
            Controls[i]["value"] = self.CameraParams.child(Controls[i]["name"]).value()
        #
        SettingDlg = SettingNameDlg()
        if SettingDlg.exec_() == QtWidgets.QDialog.Accepted:
            Setting = {
                "name": SettingDlg.lineEdit_SettingName.text(),
                "controls" : Controls,
            }
            with open(fn, "wb") as fh:
                json.dump(Setting, fh, indent=2)


    @QtCore.pyqtSlot()
    def on_action_DarkNoiseMeasurement_triggered(self):
        logging.debug("menu action Dark Noise Measurement triggered")
        self.AddLogMessage("Started automation task.")
        #
        CapturesPerCombination = 20
        self.on_pushButton_Folder_clicked()
        self.ui.lineEdit_FileName.setText("DarkNoise")
        self.ui.lineEdit_ImageComment.setText("automated dark noise measurement")
        self.ui.spinBox_nImagesToRecord.setValue(CapturesPerCombination)
        #
        if self.FrameInfo["CameraType"] == 1:
            # V1 camera
            self.LoadSettingsFile(os.path.join(self.PresetFolder, "V1_low_light.set"))
            My_qWait(2.0)
            analog_gain = [1.0, 2.0, 4.0, 8.0]
            shutter_speed_s =[0.0001, 0.0002, 0.0005,
                              0.001, 0.002, 0.005,
                              0.01, 0.02, 0.05,
                              0.1, 0.2, 0.5,
                              1.0, 2.0, 6.0,
                              ]
        elif self.FrameInfo["CameraType"] == 2:
            # V2 camera
            self.LoadSettingsFile(os.path.join(self.PresetFolder, "V1_low_light.set"))
            My_qWait(2.0)
            analog_gain = [1.0, 2.0, 4.0, 8.0, 12.0]
            shutter_speed_s =[0.0001, 0.0002, 0.0005,
                              0.001, 0.002, 0.005,
                              0.01, 0.02, 0.05,
                              0.1, 0.2, 0.5,
                              1.0, 2.0, 5.0,
                              10.0
                              ]
        elif self.FrameInfo["CameraType"] == 3:
            # HQ camera
            self.LoadSettingsFile(os.path.join(self.PresetFolder, "mode3.set"))
            My_qWait(2.0)
            analog_gain = [1.0, 2.0, 4.0, 8.0, 12.0, 16.0]
            shutter_speed_s =[0.0001, 0.0002, 0.0005,
                              0.001, 0.002, 0.005,
                              0.01, 0.02, 0.05,
                              0.1, 0.2, 0.5,
                              1.0, 2.0, 5.0,
                              10.0, 20.0, 50.0,
                              100.0, 200.0,
                              ]
        else:
            raise NotImplementedError("unknown camera type: %s" % str(self.FrameInfo["CameraType"]))
        #
        n_Combinations = len(list(itertools.product(analog_gain, shutter_speed_s)))
        self.AddLogMessage("Measuring %d parameter combinations." % n_Combinations)
        Combination = 0
        for ag in analog_gain:
            for ss in shutter_speed_s:
                Combination += 1
                self.AddLogMessage("Parameter combination %d of %d: analog_gain=%.2f, shutter_speed_s=%.4f" % (Combination, n_Combinations, ag, ss))
                self.CameraParams.child("analog_gain").setValue(ag)
                self.CameraParams.child("shutter_speed_s").setValue(ss)
                # setting exposure mode to "auto" makes the first
                #self.CameraParams.child("exposuremode").setValue("auto")
                My_qWait(5*ss + 2.0)
                #self.CameraParams.child("exposuremode").setValue("off")
                #My_qWait(1.0)
                # start recording
                self.on_pushButton_StartRec_clicked()
                # wait for end of recording
                while self.isRecording:
                    My_qWait(1.0)
        #
        My_qWait(5.0)
        self.AddLogMessage("Automation task ended.")




class StreamReceiver(QtCore.QThread):
    sigImage = QtCore.pyqtSignal(dict)

    def __init__(self, ServerIP, Port):
        QtCore.QThread.__init__(self)
        self.ServerIP = ServerIP
        self.Port = Port
        # run in loop
        self.RunInLoop = True
        self.DiscardFrames = False
        self.DiscardedFrames = 0
        self.StatFrameTimer = ReportingTimer("time between received frames", batchsize=5)

    def stop(self):
        self.RunInLoop = False

    def run(self):
        LenHeaderSize = struct.calcsize('<L')
        ExtHeaderSize = struct.calcsize('<LcbLLHfbffffB12s12s')
        FrameCnt = 0
        logging.debug("entering frame receive loop")
        try:
            logging.debug("connecting streaming receiver to port %d" % self.Port)
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.debug("socket created")
            server_socket.connect((self.ServerIP, self.Port))
            logging.debug(f'socket is in blocking mode: {server_socket.getblocking()}')
            SocketRxFile = server_socket.makefile('rb')
            logging.debug("connection established")
            self.StatFrameTimer.start()
            server_socket.send(b"GET\r\n")
            #logging.debug("sent command")
            while self.RunInLoop:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                LenHeaderBytes = SocketRxFile.read(LenHeaderSize)
                #logging.debug(f'read {len(LenHeaderBytes)} bytes')
                if LenHeaderBytes is None:
                    raise NotImplementedError("Unexpected None when reading LenHeater")
                elif len(LenHeaderBytes) != LenHeaderSize:
                    # FIXME: That happens often!
                    logging.warning("Unexpected len(LenHeaderBytes)=%d" % len(LenHeaderBytes))
                else:
                    frame_len = struct.unpack('<L', LenHeaderBytes)[0]
                    if frame_len > 0:
                        (
                            CaptureCnt,
                            CaptureType, CameraType, Camera_shutter_speed, Camera_exposure_speed,
                            Camera_iso, Camera_framerate, Camera_exposure_compensation,
                            Camera_awb_gains_0, Camera_awb_gains_1,
                            Camera_analog_gain,
                            Camera_digital_gain,
                            Camera_sensor_mode,
                            Camera_exposure_mode, Camera_awb_mode,
                        ) = struct.unpack('<LcbLLHfbffffB12s12s', SocketRxFile.read(ExtHeaderSize))
                        #logging.debug(f'unpacked header')
                        # read image stream
                        image_stream = io.BytesIO()
                        image_stream.write(SocketRxFile.read(frame_len))
                        #logging.debug(f'read frame')
                        #
                        FrameCnt += 1
                        #
                        if self.DiscardFrames:
                            self.DiscardedFrames += 1
                        else:
                            self.sigImage.emit({"stream": image_stream,
                                                "info": {
                                                    "FrameLen": frame_len,
                                                    "CaptureCnt": CaptureCnt,
                                                    "CaptureType": CaptureType.decode("ascii"),
                                                    "CameraType": CameraType,
                                                    "ShutterSpeed": Camera_shutter_speed,
                                                    "ExposureSpeed": Camera_exposure_speed,
                                                    "ISO": Camera_iso,
                                                    "FrameRate" : Camera_framerate,
                                                    "ExposureCompensation": Camera_exposure_compensation,
                                                    "FrameCnt": FrameCnt,
                                                    "DiscardedFrames": self.DiscardedFrames,
                                                    "TimeStamp": time.time(),
                                                    "AWB_Gain[0]": Camera_awb_gains_0,
                                                    "AWB_Gain[1]": Camera_awb_gains_1,
                                                    "AnalogGain": Camera_analog_gain,
                                                    "DigitalGain": Camera_digital_gain,
                                                    "SensorMode": Camera_sensor_mode,
                                                    "ExpMode": Camera_exposure_mode.decode("ascii"),
                                                    "AwbMode": Camera_awb_mode.decode("ascii"),
                                                },
                            })
                        self.StatFrameTimer.stop()
                        self.StatFrameTimer.start()
                # wait
                self.msleep(50)
                # for any reason multiple requests do not work (due to firewall?)
                # need to close and reopen the socket!
                SocketRxFile.close()
                server_socket.shutdown(2)
                server_socket.close()
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((self.ServerIP, self.Port))
                SocketRxFile = server_socket.makefile('rb')
                # ask for next frame
                server_socket.send(b"GET\r\n")
                #logging.debug("sent command (2)")
        except Exception as e:
            print(e)
        finally:
            SocketRxFile.close()
            server_socket.shutdown(2)
            server_socket.close()



## Start Qt event loop unless running in interactive mode.
def main():
    logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.DEBUG)
    # build application
    App = QtWidgets.QApplication(sys.argv)
    App.setOrganizationName("GeierSoft")
    App.setOrganizationDomain("Astro")
    App.setApplicationName("HubblePi_Capture")
    #
    # stolen from https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    if theme_selection == 'Dark':
        App.setStyle("Fusion")
        #
        # # Now use a palette to switch to dark colors:
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(35, 35, 35))
        dark_palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(53, 53, 53))
        App.setPalette(dark_palette)
    elif theme_selection == 'Light':
        App.setStyle("")
        pass
    else:
        pass
    #
    MainWindow = MainWin()
    #MainWindow.resize(1400, 900)
    MainWindow.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        #QtGui.QApplication.instance().exec_()
        sys.exit(App.exec_())


if __name__ == '__main__':
    main()