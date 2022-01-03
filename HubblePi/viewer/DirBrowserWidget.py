from PyQt5 import QtCore, QtWidgets
import sys, os
import pandas as pd
import logging

import HubblePi.Toolbox

from HubblePi.viewer import DirBrowser_ui


class DirBrowserWidget(QtWidgets.QWidget, DirBrowser_ui.Ui_Form):
    sigFileName = QtCore.pyqtSignal(str)


    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        #
        self.label_Dir.setText(".")


    @QtCore.pyqtSlot()
    def on_pushButton_Dir_clicked(self):
        Dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select folder to browse", self.label_Dir.text())
        self.label_Dir.setText(Dir)
        self.on_pushButton_ReloadDir_clicked()


    @QtCore.pyqtSlot()
    def on_pushButton_ReloadDir_clicked(self):
        logging.debug("entering on_pushButton_ReloadDir_clicked")
        Data = pd.DataFrame(columns=["FileName", "comment", "ExposureSpeed", "AnalogGain"])
        Dir = self.label_Dir.text()
        DirList = os.listdir(Dir)
        RawExtensions = []
        if self.checkBox_JPG.isChecked():
            RawExtensions += [".jpg"]
        if self.checkBox_DNG.isChecked():
            RawExtensions += [".dng"]
        if self.checkBox_NPY.isChecked():
            RawExtensions += [".npy", ".npz"]
        InfoExtensions = [".info"]
        # remove non-file entries
        FileList = [Entry for Entry in DirList if os.path.isfile(os.path.join(Dir, Entry))]
        # raw files
        RawList = [Entry for Entry in FileList if Entry[-4:].lower() in RawExtensions]
        Data = Data.append(pd.DataFrame({"FileName": RawList}), ignore_index=True, sort=False)
        # info files
        logging.debug("loading info files")
        InfoList = [Entry for Entry in FileList if Entry[-5:].lower() in InfoExtensions]
        for Entry in InfoList:
            # does Data contain any matching RAW entry?
            RawMatches = Data["FileName"].str[:-4] == Entry[:-5]
            if RawMatches.any():
                # load info file
                Info = HubblePi.Toolbox.LoadInfo(os.path.join(Dir, Entry))
                Data.loc[RawMatches, "comment"] = Info.get("comment", -1)
                Data.loc[RawMatches, "ExposureSpeed"] = Info.get("ExposureSpeed", -1)
                Data.loc[RawMatches, "AnalogGain"] = Info.get("AnalogGain", -1)
        #
        self.tableView_Files.setData(Data, RootDir=Dir)
        logging.debug("leaving on_pushButton_ReloadDir_clicked")


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tableView_Files_doubleClicked(self, idx):
        FileName = self.tableView_Files.getFileName(idx)
        self.tableView_Files.markLine(idx)
        logging.debug("DirBrowserWidget clicked: %s" % FileName)
        self.sigFileName.emit(FileName)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s- %(message)s', level=logging.DEBUG)
    # build application
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("GeierSoft")
    app.setOrganizationDomain("Astro")
    app.setApplicationName("HubblePi_Viewer")
    app.setStyle("Plastique")
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setCentralWidget(DirBrowserWidget())
    MainWindow.show()
    RetCode = app.exec_()
    sys.exit(RetCode)

