# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HubblePi_Viewer_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(862, 812)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter_2 = QtWidgets.QSplitter(self.widget_2)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.frame_DirBrowser = QtWidgets.QFrame(self.splitter_2)
        self.frame_DirBrowser.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_DirBrowser.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_DirBrowser.setObjectName("frame_DirBrowser")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_DirBrowser)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget_DirBrowser = DirBrowserWidget(self.frame_DirBrowser)
        self.widget_DirBrowser.setObjectName("widget_DirBrowser")
        self.verticalLayout_4.addWidget(self.widget_DirBrowser)
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.ImageView_Preview = ImageView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ImageView_Preview.sizePolicy().hasHeightForWidth())
        self.ImageView_Preview.setSizePolicy(sizePolicy)
        self.ImageView_Preview.setObjectName("ImageView_Preview")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget_ParamControls = QtWidgets.QTabWidget(self.widget)
        self.tabWidget_ParamControls.setObjectName("tabWidget_ParamControls")
        self.PixelCorrections = QtWidgets.QWidget()
        self.PixelCorrections.setObjectName("PixelCorrections")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.PixelCorrections)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_loadBlackLevelImage = QtWidgets.QPushButton(self.PixelCorrections)
        self.pushButton_loadBlackLevelImage.setEnabled(False)
        self.pushButton_loadBlackLevelImage.setObjectName("pushButton_loadBlackLevelImage")
        self.gridLayout_2.addWidget(self.pushButton_loadBlackLevelImage, 1, 0, 1, 1)
        self.checkBox_doBlackLevelCorrection = QtWidgets.QCheckBox(self.PixelCorrections)
        self.checkBox_doBlackLevelCorrection.setObjectName("checkBox_doBlackLevelCorrection")
        self.gridLayout_2.addWidget(self.checkBox_doBlackLevelCorrection, 0, 0, 1, 1)
        self.checkBox_doGainCorrection = QtWidgets.QCheckBox(self.PixelCorrections)
        self.checkBox_doGainCorrection.setObjectName("checkBox_doGainCorrection")
        self.gridLayout_2.addWidget(self.checkBox_doGainCorrection, 2, 0, 1, 1)
        self.checkBox_doSaltAndPepperCorrection = QtWidgets.QCheckBox(self.PixelCorrections)
        self.checkBox_doSaltAndPepperCorrection.setObjectName("checkBox_doSaltAndPepperCorrection")
        self.gridLayout_2.addWidget(self.checkBox_doSaltAndPepperCorrection, 4, 0, 1, 1)
        self.pushButton_loadGainImage = QtWidgets.QPushButton(self.PixelCorrections)
        self.pushButton_loadGainImage.setEnabled(False)
        self.pushButton_loadGainImage.setObjectName("pushButton_loadGainImage")
        self.gridLayout_2.addWidget(self.pushButton_loadGainImage, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 142, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 6, 0, 1, 1)
        self.widget_4 = QtWidgets.QWidget(self.PixelCorrections)
        self.widget_4.setEnabled(False)
        self.widget_4.setObjectName("widget_4")
        self.gridLayout = QtWidgets.QGridLayout(self.widget_4)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox_takeSaltAndPepperFromImages = QtWidgets.QCheckBox(self.widget_4)
        self.checkBox_takeSaltAndPepperFromImages.setChecked(True)
        self.checkBox_takeSaltAndPepperFromImages.setObjectName("checkBox_takeSaltAndPepperFromImages")
        self.gridLayout.addWidget(self.checkBox_takeSaltAndPepperFromImages, 0, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.widget_4)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.doubleSpinBox_SaltAndPepperSigma = QtWidgets.QDoubleSpinBox(self.widget_4)
        self.doubleSpinBox_SaltAndPepperSigma.setDecimals(1)
        self.doubleSpinBox_SaltAndPepperSigma.setSingleStep(0.1)
        self.doubleSpinBox_SaltAndPepperSigma.setProperty("value", 3.0)
        self.doubleSpinBox_SaltAndPepperSigma.setObjectName("doubleSpinBox_SaltAndPepperSigma")
        self.gridLayout.addWidget(self.doubleSpinBox_SaltAndPepperSigma, 1, 1, 1, 1)
        self.pushButton_loadSaltAndPepperImage = QtWidgets.QPushButton(self.widget_4)
        self.pushButton_loadSaltAndPepperImage.setEnabled(False)
        self.pushButton_loadSaltAndPepperImage.setObjectName("pushButton_loadSaltAndPepperImage")
        self.gridLayout.addWidget(self.pushButton_loadSaltAndPepperImage, 2, 0, 1, 2)
        self.gridLayout_2.addWidget(self.widget_4, 5, 0, 1, 1)
        self.tabWidget_ParamControls.addTab(self.PixelCorrections, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_3 = QtWidgets.QLabel(self.tab_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 3, 1, 1, 1)
        self.comboBox_BayerPattern = QtWidgets.QComboBox(self.tab_2)
        self.comboBox_BayerPattern.setObjectName("comboBox_BayerPattern")
        self.comboBox_BayerPattern.addItem("")
        self.comboBox_BayerPattern.addItem("")
        self.comboBox_BayerPattern.addItem("")
        self.comboBox_BayerPattern.addItem("")
        self.comboBox_BayerPattern.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_BayerPattern, 0, 1, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 2, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.tab_2)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 4, 1, 1, 1)
        self.doubleSpinBox_GainR = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox_GainR.setSingleStep(0.1)
        self.doubleSpinBox_GainR.setProperty("value", 1.5)
        self.doubleSpinBox_GainR.setObjectName("doubleSpinBox_GainR")
        self.gridLayout_3.addWidget(self.doubleSpinBox_GainR, 2, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.doubleSpinBox_GainB = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox_GainB.setSingleStep(0.1)
        self.doubleSpinBox_GainB.setProperty("value", 1.5)
        self.doubleSpinBox_GainB.setObjectName("doubleSpinBox_GainB")
        self.gridLayout_3.addWidget(self.doubleSpinBox_GainB, 4, 2, 1, 1)
        self.comboBox_DebayerAlgo = QtWidgets.QComboBox(self.tab_2)
        self.comboBox_DebayerAlgo.setObjectName("comboBox_DebayerAlgo")
        self.comboBox_DebayerAlgo.addItem("")
        self.comboBox_DebayerAlgo.addItem("")
        self.comboBox_DebayerAlgo.addItem("")
        self.comboBox_DebayerAlgo.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_DebayerAlgo, 1, 1, 1, 2)
        self.doubleSpinBox_GainG = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox_GainG.setSingleStep(0.1)
        self.doubleSpinBox_GainG.setProperty("value", 1.0)
        self.doubleSpinBox_GainG.setObjectName("doubleSpinBox_GainG")
        self.gridLayout_3.addWidget(self.doubleSpinBox_GainG, 3, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 5, 1, 1, 1)
        self.tabWidget_ParamControls.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_10 = QtWidgets.QLabel(self.tab)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 8, 0, 1, 1)
        self.doubleSpinBox_OutOffset = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_OutOffset.setEnabled(False)
        self.doubleSpinBox_OutOffset.setDecimals(3)
        self.doubleSpinBox_OutOffset.setMinimum(-100000.0)
        self.doubleSpinBox_OutOffset.setMaximum(100000.0)
        self.doubleSpinBox_OutOffset.setSingleStep(0.01)
        self.doubleSpinBox_OutOffset.setObjectName("doubleSpinBox_OutOffset")
        self.gridLayout_4.addWidget(self.doubleSpinBox_OutOffset, 5, 2, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 340, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem2, 11, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.tab)
        self.label_13.setObjectName("label_13")
        self.gridLayout_4.addWidget(self.label_13, 1, 0, 1, 1)
        self.doubleSpinBox_OutGain = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_OutGain.setEnabled(False)
        self.doubleSpinBox_OutGain.setDecimals(3)
        self.doubleSpinBox_OutGain.setMinimum(-100000.0)
        self.doubleSpinBox_OutGain.setMaximum(100000.0)
        self.doubleSpinBox_OutGain.setSingleStep(0.1)
        self.doubleSpinBox_OutGain.setProperty("value", 1.0)
        self.doubleSpinBox_OutGain.setObjectName("doubleSpinBox_OutGain")
        self.gridLayout_4.addWidget(self.doubleSpinBox_OutGain, 6, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.tab)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 9, 0, 1, 1)
        self.comboBox_Rotation = QtWidgets.QComboBox(self.tab)
        self.comboBox_Rotation.setObjectName("comboBox_Rotation")
        self.comboBox_Rotation.addItem("")
        self.comboBox_Rotation.addItem("")
        self.comboBox_Rotation.addItem("")
        self.comboBox_Rotation.addItem("")
        self.gridLayout_4.addWidget(self.comboBox_Rotation, 8, 1, 1, 1)
        self.checkBox_AutoScale = QtWidgets.QCheckBox(self.tab)
        self.checkBox_AutoScale.setChecked(True)
        self.checkBox_AutoScale.setObjectName("checkBox_AutoScale")
        self.gridLayout_4.addWidget(self.checkBox_AutoScale, 1, 1, 1, 2)
        self.checkBox_flipH = QtWidgets.QCheckBox(self.tab)
        self.checkBox_flipH.setObjectName("checkBox_flipH")
        self.gridLayout_4.addWidget(self.checkBox_flipH, 9, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.tab)
        self.label_9.setObjectName("label_9")
        self.gridLayout_4.addWidget(self.label_9, 6, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.tab)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 5, 1, 1, 1)
        self.checkBox_flipV = QtWidgets.QCheckBox(self.tab)
        self.checkBox_flipV.setObjectName("checkBox_flipV")
        self.gridLayout_4.addWidget(self.checkBox_flipV, 10, 1, 1, 1)
        self.doubleSpinBox_Gamma = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_Gamma.setMinimum(0.1)
        self.doubleSpinBox_Gamma.setMaximum(10.0)
        self.doubleSpinBox_Gamma.setSingleStep(0.1)
        self.doubleSpinBox_Gamma.setProperty("value", 1.0)
        self.doubleSpinBox_Gamma.setObjectName("doubleSpinBox_Gamma")
        self.gridLayout_4.addWidget(self.doubleSpinBox_Gamma, 7, 1, 1, 1)
        self.label_AutoscaleParams = QtWidgets.QLabel(self.tab)
        self.label_AutoscaleParams.setObjectName("label_AutoscaleParams")
        self.gridLayout_4.addWidget(self.label_AutoscaleParams, 4, 1, 1, 2)
        self.label_12 = QtWidgets.QLabel(self.tab)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 7, 0, 1, 1)
        self.doubleSpinBox_minPercentile = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_minPercentile.setSingleStep(0.1)
        self.doubleSpinBox_minPercentile.setProperty("value", 0.1)
        self.doubleSpinBox_minPercentile.setObjectName("doubleSpinBox_minPercentile")
        self.gridLayout_4.addWidget(self.doubleSpinBox_minPercentile, 2, 2, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.tab)
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 2, 1, 1, 1)
        self.doubleSpinBox_maxPercentile = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_maxPercentile.setSingleStep(0.1)
        self.doubleSpinBox_maxPercentile.setProperty("value", 1.0)
        self.doubleSpinBox_maxPercentile.setObjectName("doubleSpinBox_maxPercentile")
        self.gridLayout_4.addWidget(self.doubleSpinBox_maxPercentile, 3, 2, 1, 1)
        self.tabWidget_ParamControls.addTab(self.tab, "")
        self.verticalLayout.addWidget(self.tabWidget_ParamControls)
        self.widget_3 = QtWidgets.QWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_SaveImg = QtWidgets.QPushButton(self.widget_3)
        self.pushButton_SaveImg.setEnabled(False)
        self.pushButton_SaveImg.setObjectName("pushButton_SaveImg")
        self.horizontalLayout.addWidget(self.pushButton_SaveImg)
        self.verticalLayout.addWidget(self.widget_3)
        self.verticalLayout_3.addWidget(self.splitter_2)
        self.verticalLayout_2.addWidget(self.widget_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 862, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget_ParamControls.setCurrentIndex(0)
        self.checkBox_takeSaltAndPepperFromImages.toggled['bool'].connect(self.doubleSpinBox_SaltAndPepperSigma.setEnabled)
        self.checkBox_doGainCorrection.toggled['bool'].connect(self.pushButton_loadGainImage.setEnabled)
        self.checkBox_doSaltAndPepperCorrection.toggled['bool'].connect(self.widget_4.setEnabled)
        self.checkBox_takeSaltAndPepperFromImages.toggled['bool'].connect(self.pushButton_loadSaltAndPepperImage.setDisabled)
        self.checkBox_doBlackLevelCorrection.toggled['bool'].connect(self.pushButton_loadBlackLevelImage.setEnabled)
        self.checkBox_AutoScale.toggled['bool'].connect(self.doubleSpinBox_OutOffset.setDisabled)
        self.checkBox_AutoScale.toggled['bool'].connect(self.doubleSpinBox_OutGain.setDisabled)
        self.checkBox_AutoScale.toggled['bool'].connect(self.label_AutoscaleParams.setEnabled)
        self.checkBox_AutoScale.toggled['bool'].connect(self.label_14.setEnabled)
        self.checkBox_AutoScale.toggled['bool'].connect(self.doubleSpinBox_minPercentile.setEnabled)
        self.checkBox_AutoScale.toggled['bool'].connect(self.doubleSpinBox_maxPercentile.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_loadBlackLevelImage.setText(_translate("MainWindow", "Load Black Level Image"))
        self.checkBox_doBlackLevelCorrection.setText(_translate("MainWindow", "Black Level Correction"))
        self.checkBox_doGainCorrection.setText(_translate("MainWindow", "Gain Correction"))
        self.checkBox_doSaltAndPepperCorrection.setText(_translate("MainWindow", "Salt and Pepper Correction"))
        self.pushButton_loadGainImage.setText(_translate("MainWindow", "Load Gain Image"))
        self.checkBox_takeSaltAndPepperFromImages.setText(_translate("MainWindow", "take from Correction Images"))
        self.label.setText(_translate("MainWindow", "Sigma:"))
        self.pushButton_loadSaltAndPepperImage.setText(_translate("MainWindow", "Load Salt and Pepper Image"))
        self.tabWidget_ParamControls.setTabText(self.tabWidget_ParamControls.indexOf(self.PixelCorrections), _translate("MainWindow", "Pixel Corrections"))
        self.label_3.setText(_translate("MainWindow", "Algo:"))
        self.label_6.setText(_translate("MainWindow", "G:"))
        self.comboBox_BayerPattern.setItemText(0, _translate("MainWindow", "auto"))
        self.comboBox_BayerPattern.setItemText(1, _translate("MainWindow", "RGGB"))
        self.comboBox_BayerPattern.setItemText(2, _translate("MainWindow", "BGGR"))
        self.comboBox_BayerPattern.setItemText(3, _translate("MainWindow", "GRBG"))
        self.comboBox_BayerPattern.setItemText(4, _translate("MainWindow", "GBRG"))
        self.label_5.setText(_translate("MainWindow", "R:"))
        self.label_7.setText(_translate("MainWindow", "B:"))
        self.label_2.setText(_translate("MainWindow", "Patter:"))
        self.comboBox_DebayerAlgo.setItemText(0, _translate("MainWindow", "bilinear"))
        self.comboBox_DebayerAlgo.setItemText(1, _translate("MainWindow", "Malvar2004"))
        self.comboBox_DebayerAlgo.setItemText(2, _translate("MainWindow", "Menon2007"))
        self.comboBox_DebayerAlgo.setItemText(3, _translate("MainWindow", "DDFAPD"))
        self.label_4.setText(_translate("MainWindow", "Weights:"))
        self.tabWidget_ParamControls.setTabText(self.tabWidget_ParamControls.indexOf(self.tab_2), _translate("MainWindow", "Debayer"))
        self.label_10.setText(_translate("MainWindow", "Rotate:"))
        self.label_13.setText(_translate("MainWindow", "Value Range:"))
        self.label_11.setText(_translate("MainWindow", "Mirror:"))
        self.comboBox_Rotation.setItemText(0, _translate("MainWindow", "0deg"))
        self.comboBox_Rotation.setItemText(1, _translate("MainWindow", "90deg"))
        self.comboBox_Rotation.setItemText(2, _translate("MainWindow", "180deg"))
        self.comboBox_Rotation.setItemText(3, _translate("MainWindow", "270deg"))
        self.checkBox_AutoScale.setText(_translate("MainWindow", "Autoscale"))
        self.checkBox_flipH.setText(_translate("MainWindow", "flip H"))
        self.label_9.setText(_translate("MainWindow", "Gain:"))
        self.label_8.setText(_translate("MainWindow", "Offset:"))
        self.checkBox_flipV.setText(_translate("MainWindow", "flip V"))
        self.label_AutoscaleParams.setText(_translate("MainWindow", "offset: -, gain: -"))
        self.label_12.setText(_translate("MainWindow", "Gamma:"))
        self.label_14.setText(_translate("MainWindow", "percentiles:"))
        self.tabWidget_ParamControls.setTabText(self.tabWidget_ParamControls.indexOf(self.tab), _translate("MainWindow", "Postprocess"))
        self.pushButton_SaveImg.setText(_translate("MainWindow", "Save"))
from DirBrowserWidget import DirBrowserWidget
from pyqtgraph import ImageView
