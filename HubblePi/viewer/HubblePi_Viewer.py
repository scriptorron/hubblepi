
import sys
import PIL
import PIL.Image
import rawpy
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
import colour_demosaicing
import imageio


import logging

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

import HubblePi.Toolbox
from HubblePi.viewer import HubblePi_Viewer_ui

theme_selection = "Dark" # "Dark", "Light"

class Image(object):
    def __init__(self):
        self.Raw = None
        self.CameraType = None
        self.FileName = None
        self.PixelCorrected = None
        self.Debayered = None
        self.Processed = None


class MainWin(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWin, self).__init__()
        pg.setConfigOption('background', pg.mkColor(100, 0, 0))
        self.ui = HubblePi_Viewer_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        #
        self.ui.ImageView_Preview.setLevels(0.0, 1.0)
        self.ui.ImageView_Preview.ui.roiBtn.hide()
        self.ui.ImageView_Preview.ui.menuBtn.hide()
        # states
        self.Image = Image()
        self.BlackLevelImage = np.r_[[[]]]
        self.GainImage = np.r_[[[]]]
        # connect signals
        for cb in [self.ui.checkBox_doBlackLevelCorrection, self.ui.checkBox_doGainCorrection,
                   self.ui.checkBox_doSaltAndPepperCorrection, self.ui.checkBox_takeSaltAndPepperFromImages]:
            cb.toggled.connect(self.processFromPixelCorrection)
        self.ui.doubleSpinBox_SaltAndPepperSigma.valueChanged.connect(lambda f: self.processFromPixelCorrection())
        self.ui.comboBox_BayerPattern.currentIndexChanged.connect(lambda i: self.processFromDebayer())
        self.ui.comboBox_DebayerAlgo.currentIndexChanged.connect(lambda i: self.processFromDebayer())
        self.ui.doubleSpinBox_GainR.valueChanged.connect(self.processFromDebayer)
        self.ui.doubleSpinBox_GainG.valueChanged.connect(self.processFromDebayer)
        self.ui.doubleSpinBox_GainB.valueChanged.connect(self.processFromDebayer)
        self.ui.checkBox_AutoScale.toggled.connect(self.processFromPostprocess)
        self.ui.doubleSpinBox_minPercentile.valueChanged.connect(self.processFromPostprocess)
        self.ui.doubleSpinBox_maxPercentile.valueChanged.connect(self.processFromPostprocess)
        self.ui.doubleSpinBox_OutOffset.valueChanged.connect(self.processFromPostprocess)
        self.ui.doubleSpinBox_OutGain.valueChanged.connect(self.processFromPostprocess)
        self.ui.doubleSpinBox_Gamma.valueChanged.connect(self.processFromPostprocess)
        self.ui.comboBox_Rotation.currentIndexChanged.connect(self.processFromPostprocess)
        self.ui.checkBox_flipH.toggled.connect(self.processFromPostprocess)
        self.ui.checkBox_flipV.toggled.connect(self.processFromPostprocess)
        #


    @QtCore.pyqtSlot(str)
    def on_widget_DirBrowser_sigFileName(self, str):
        self.ui.pushButton_SaveImg.setEnabled(False)
        self.Image.FileName = str
        Raw, CameraType = self.LoadImageFile(str)
        if Raw is not None:
            self.Image.Raw = Raw
            self.Image.CameraType = CameraType
            self.processFromPixelCorrection()


    def clearImageView(self):
        self.ui.ImageView_Preview.clear()


    def processFromPixelCorrection(self):
        logging.debug("Entering processFromPixelCorrection...")
        self.clearImageView()
        self.Image.PixelCorrected = None
        self.Image.Debayered = None
        self.Image.Processed = None
        if (self.Image.Raw is not None) and (self.Image.CameraType is not None):
            Img = self.Image.Raw
            # Black correction
            #print "DBG1: %f, %f" % (Img.min(), Img.max())
            if self.ui.checkBox_doBlackLevelCorrection.isChecked():
                if Img.shape == self.BlackLevelImage.shape:
                    Img = Img - self.BlackLevelImage
                else:
                    self.loadBlackLevelImage()
                    if Img.shape != self.BlackLevelImage.shape:
                        QtWidgets.QMessageBox.warning(self,
                                                      "Wrong Black Level image", "Can not use black level image!\n"
                                                      "Black Level correction gets disabled.")
                        self.ui.checkBox_doBlackLevelCorrection.setChecked(False)
                        return
                    else:
                        Img = Img - self.BlackLevelImage
                #print "DBG2: %f, %f, %s, %f, %f, %s" % (Img.min(), Img.max(), Img.dtype, self.BlackLevelImage.min(), self.BlackLevelImage.max(), self.BlackLevelImage.dtype)
            # Flat correction
            if self.ui.checkBox_doGainCorrection.isChecked():
                if Img.shape == self.GainImage.shape:
                    Img = Img * self.GainImage
                else:
                    self.loadGainImage()
                    if Img.shape != self.GainImage.shape:
                        QtWidgets.QMessageBox.warning(self,
                                                      "Wrong Flat image", "Can not use gain image!\n"
                                                      "Gain correction gets disabled.")
                        self.ui.checkBox_doGainCorrection.setChecked(False)
                        return
                    else:
                        Img = Img * self.GainImage
            #print "DBG3: %f, %f" % (Img.min(), Img.max())
            # normalize scaling
            MaxVal = {1: 1024, 2: 1024, 3: 4096}[self.Image.CameraType]
            Img = Img / float(MaxVal)
            # TODO: implement Salt&Pepper correction
            #
            #print "DBG4: %f, %f" % (Img.min(), Img.max())
            self.Image.PixelCorrected = Img
            self.processFromDebayer()


    def processFromDebayer(self):
        logging.debug("Entering processFromDebayer...")
        self.clearImageView()
        self.Image.Debayered = None
        self.Image.Processed = None
        if (self.Image.PixelCorrected is not None) and (self.Image.CameraType is not None):
            Img = self.Image.PixelCorrected
            Pattern = self.ui.comboBox_BayerPattern.currentText()
            if Pattern == "auto":
                Pattern = {
                    1: u"GBRG",
                    2: u"GBRG",
                    3: u"BGGR",
                }[self.Image.CameraType]
            Debayer = self.ui.comboBox_DebayerAlgo.currentText()
            # debayer
            if Debayer == "bilinear":
                Img = colour_demosaicing.demosaicing_CFA_Bayer_bilinear(Img, pattern=Pattern)
            elif Debayer == "Malvar2004":
                Img = colour_demosaicing.demosaicing_CFA_Bayer_Malvar2004(Img, pattern=Pattern)
            elif Debayer == "Menon2007":
                Img = colour_demosaicing.demosaicing_CFA_Bayer_Menon2007(Img, pattern=Pattern)
            elif Debayer == "DDFAPD":
                Img = colour_demosaicing.demosaicing_CFA_Bayer_DDFAPD(Img, pattern=Pattern)
            # white balance
            Img[:, :, 0] *= self.ui.doubleSpinBox_GainR.value()
            Img[:, :, 1] *= self.ui.doubleSpinBox_GainG.value()
            Img[:, :, 2] *= self.ui.doubleSpinBox_GainB.value()
            #
            self.Image.Debayered = Img
            self.processFromPostprocess()


    def processFromPostprocess(self):
        logging.debug("Entering processFromPostprocess...")
        self.clearImageView()
        self.Image.Processed = None
        if (self.Image.Debayered is not None) and (self.Image.CameraType is not None):
            Img = self.Image.Debayered
            #print ("Img min: %f, max: %f" % (Img.min(), Img.max()))
            #
            Offset = np.percentile(Img, self.ui.doubleSpinBox_minPercentile.value())
            Gain = 1.0 / np.percentile(Img - Offset, 100.0 - self.ui.doubleSpinBox_maxPercentile.value())
            self.ui.label_AutoscaleParams.setText("offset: %.3f, gain: %.3f" % (Offset, Gain))
            if not self.ui.checkBox_AutoScale.isChecked():
                Offset = self.ui.doubleSpinBox_OutOffset.value()
                Gain = self.ui.doubleSpinBox_OutGain.value()
            Img = (Img - Offset) * Gain
            # gamma correction
            Img = np.where(np.sign(Img) > 0, np.abs(Img) ** self.ui.doubleSpinBox_Gamma.value(), Img)
            # rotation and mirror
            Rot = self.ui.comboBox_Rotation.currentText()
            if Rot != "0deg":
                k = {"90deg": 3, "180deg": 2, "270deg": 1}[Rot]
                Img = np.rot90(Img, k=k)
            if self.ui.checkBox_flipH.isChecked():
                Img = np.flipud(Img)
            if self.ui.checkBox_flipV.isChecked():
                Img = np.fliplr(Img)
            #
            self.Image.Processed = Img
            self.plotProcessedImage()
            self.ui.pushButton_SaveImg.setEnabled(True)


    def plotProcessedImage(self):
        logging.debug("Entering plotProcessedImage...")
        if self.Image.Processed is not None:
            self.ui.ImageView_Preview.setImage(self.Image.Processed, autoLevels=False,
                                               autoHistogramRange=False,
                                               #levelMode="rgb",
                                               )
            logging.debug("Finished image view.")


    def LoadImageFile(self, FileName):
        logging.debug("Loading image file %s" % FileName)
        if FileName.endswith(".jpg"):
            # RPi RAW Jpg
            img = PIL.Image.open(FileName)
            EXIF = img._getexif()
            if EXIF is not None:
                if EXIF.get(272, "") == 'RP_ov5647':
                    CameraType = 1
                elif EXIF.get(272, "") == 'RP_imx219':
                    CameraType = 2
                elif EXIF.get(272, "") == 'RP_imx477':
                    CameraType = 3
                else:
                    QtWidgets.QMessageBox.critical(self, "Unknown Data", "Can not identify camera type!")
                    return None, None
            else:
                QtWidgets.QMessageBox.critical(self, "Unknown Data", "Can not identify camera type! (EXIF missing)")
                return None, None
            with open(FileName, "rb") as fh:
                FileData = fh.read()
            Raw = HubblePi.Toolbox.ExtractRawFromJpgData(JpgData=FileData, CameraType=CameraType)
        elif FileName.endswith(".dng"):
            # DNG
            RawPyImg = rawpy.imread(FileName)
            Raw = RawPyImg.raw_image
            if Raw.shape == (1944, 2592):
                CameraType = 1
            elif Raw.shape == (2464, 3280):
                CameraType = 2
            elif Raw.shape == (3040, 4056):
                CameraType = 3
            else:
                QtWidgets.QMessageBox.critical(self, "Unknown Data", "Can not identify camera type!")
                return None, None
        elif FileName.endswith(".npy") or FileName.endswith(".npz"):
            Raw = np.load(FileName)
            if Raw.shape == (1944, 2592):
                CameraType = 1
            elif Raw.shape == (1944, 3240):
                # packed V.1
                CameraType = 1
                Raw = Raw.astype(np.uint16) << 2
                for byte in range(4):
                    Raw[:, byte::5] |= ((Raw[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
                Raw = np.delete(Raw, np.s_[4::5], 1)
            elif Raw.shape == (2464, 3280):
                CameraType = 2
            elif Raw.shape == (2464, 4100):
                # packed V.2
                CameraType = 2
                Raw = Raw.astype(np.uint16) << 2
                for byte in range(4):
                    Raw[:, byte::5] |= ((Raw[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
                Raw = np.delete(Raw, np.s_[4::5], 1)
            elif Raw.shape == (3040, 4056):
                CameraType = 3
            elif Raw.shape == (3040, 6084):
                # packed V.3
                CameraType = 3
                Raw = Raw.astype(np.uint16)
                UD = np.zeros((Raw.shape[0], Raw.shape[1] / 3 * 2), dtype=np.uint16)
                UD[:, ::2] = (Raw[:, ::3] << 4) + (Raw[:, 2::3] & 0x0F)
                UD[:, 1::2] = (Raw[:, 1::3] << 4) + ((Raw[:, 2::3] >> 4) & 0x0F)
                Raw = UD
            else:
                QtWidgets.QMessageBox.critical(self, "Unknown Data", "Can not identify camera type!")
                return None, None
        else:
            QtWidgets.QMessageBox.critical(self, "Unknown Data", "Unknown file type!")
            return None, None
        Raw = Raw.astype(float)
        return Raw, CameraType


    def loadBlackLevelImage(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(self, "Select Black Level image", ".",
                                                   "all supported files (*.npy *.npz *.jpg *.dng);;" +
                                                   "NPY/NPZ files (*.npy *.npz);;JPG files (*.jpg);; DNG files (*.dng)")[0]
        if fn != "":
            self.BlackLevelImage, CameraType = self.LoadImageFile(fn)
        else:
            self.BlackLevelImage = np.r_[[[]]]


    @QtCore.pyqtSlot()
    def on_pushButton_loadBlackLevelImage_clicked(self):
        self.loadBlackLevelImage()
        self.processFromPixelCorrection()


    def loadGainImage(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(self, "Select Flat image", ".",
                                                   "all supported files (*.npy *.npz *.jpg *.dng);;" +
                                                   "NPY/NPZ files (*.npy *.npz);;JPG files (*.jpg);; DNG files (*.dng)")[0]
        if fn != "":
            try:
                GainImage, CameraType = self.LoadImageFile(fn)
                self.GainImage = GainImage.mean()/GainImage
            except:
                self.GainImage = np.r_[[[]]]
        else:
            self.GainImage = np.r_[[[]]]


    @QtCore.pyqtSlot()
    def on_pushButton_loadGainImage_clicked(self):
        self.pushButton_loadGainImage()
        self.processFromPixelCorrection()

    @QtCore.pyqtSlot()
    def on_pushButton_SaveImg_clicked(self):
        logging.debug("Save Image clicked")
        if self.Image.Processed is not None:
            ProposedFileName = self.Image.FileName.rsplit(".", 1)[0] + ".png"
            fn = QtWidgets.QFileDialog.getSaveFileName(self, "Save image", ProposedFileName,
                                                       "all supported files (*.png *.tif);;" +
                                                       "16bit PNG (*.png);;16bit TIF (*.tif)")[
                0]
            if fn == "":
                return
            # saturate at [0.0, 1.0]
            Img = self.Image.Processed.copy()
            Img[Img < 0] = 0.0
            Img[Img > 1] = 1.0
            if fn.lower().endswith(".tif"):
                imageio.imsave(fn, imageio.core.image_as_uint(Img, bitdepth=16))
            elif fn.lower().endswith(".png"):
                imageio.imsave(fn, imageio.core.image_as_uint(Img, bitdepth=16), 'PNG-FI')
            else:
                QtWidgets.QMessageBox.critical(self, "Unknown File Format", "Don't know how to save %s" % fn)



## Start Qt event loop unless running in interactive mode.
def main():
    logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.DEBUG)
    # build application
    App = QtWidgets.QApplication(sys.argv)
    App.setOrganizationName("GeierSoft")
    App.setOrganizationDomain("Astro")
    App.setApplicationName("HubblePi_Viewer")
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