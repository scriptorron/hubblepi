# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConnectDlg_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(339, 177)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEdit_IP = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_IP.setObjectName("lineEdit_IP")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_IP)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.spinBox_CommandPort = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_CommandPort.setMaximum(65535)
        self.spinBox_CommandPort.setProperty("value", 60000)
        self.spinBox_CommandPort.setObjectName("spinBox_CommandPort")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.spinBox_CommandPort)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.spinBox_StreamingPort = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_StreamingPort.setMaximum(65535)
        self.spinBox_StreamingPort.setProperty("value", 60001)
        self.spinBox_StreamingPort.setObjectName("spinBox_StreamingPort")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.spinBox_StreamingPort)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Camera"))
        self.label.setText(_translate("Dialog", "IP:"))
        self.label_2.setText(_translate("Dialog", "Command Port:"))
        self.label_3.setText(_translate("Dialog", "Streaming Port:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

