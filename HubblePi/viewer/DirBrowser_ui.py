# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DirBrowser_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(801, 440)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_ReloadDir = QtWidgets.QPushButton(Form)
        self.pushButton_ReloadDir.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_ReloadDir.setObjectName("pushButton_ReloadDir")
        self.gridLayout.addWidget(self.pushButton_ReloadDir, 0, 5, 1, 1)
        self.label_Dir = QtWidgets.QLabel(Form)
        self.label_Dir.setText("")
        self.label_Dir.setObjectName("label_Dir")
        self.gridLayout.addWidget(self.label_Dir, 0, 1, 1, 1)
        self.pushButton_Dir = QtWidgets.QPushButton(Form)
        self.pushButton_Dir.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_Dir.setObjectName("pushButton_Dir")
        self.gridLayout.addWidget(self.pushButton_Dir, 0, 0, 1, 1)
        self.tableView_Files = DirBrowserTableView(Form)
        self.tableView_Files.setObjectName("tableView_Files")
        self.gridLayout.addWidget(self.tableView_Files, 1, 0, 1, 6)
        self.checkBox_DNG = QtWidgets.QCheckBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_DNG.sizePolicy().hasHeightForWidth())
        self.checkBox_DNG.setSizePolicy(sizePolicy)
        self.checkBox_DNG.setChecked(True)
        self.checkBox_DNG.setObjectName("checkBox_DNG")
        self.gridLayout.addWidget(self.checkBox_DNG, 0, 3, 1, 1)
        self.checkBox_JPG = QtWidgets.QCheckBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_JPG.sizePolicy().hasHeightForWidth())
        self.checkBox_JPG.setSizePolicy(sizePolicy)
        self.checkBox_JPG.setChecked(True)
        self.checkBox_JPG.setObjectName("checkBox_JPG")
        self.gridLayout.addWidget(self.checkBox_JPG, 0, 2, 1, 1)
        self.checkBox_NPY = QtWidgets.QCheckBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_NPY.sizePolicy().hasHeightForWidth())
        self.checkBox_NPY.setSizePolicy(sizePolicy)
        self.checkBox_NPY.setChecked(True)
        self.checkBox_NPY.setObjectName("checkBox_NPY")
        self.gridLayout.addWidget(self.checkBox_NPY, 0, 4, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_ReloadDir.setText(_translate("Form", "Reload"))
        self.pushButton_Dir.setText(_translate("Form", "Directory"))
        self.checkBox_DNG.setText(_translate("Form", "DNG"))
        self.checkBox_JPG.setText(_translate("Form", "JPG"))
        self.checkBox_NPY.setText(_translate("Form", "NPY/NPZ"))

from HubblePi.viewer.DirBrowserTableView import DirBrowserTableView
