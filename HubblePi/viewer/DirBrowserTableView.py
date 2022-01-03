from PyQt5 import QtCore, QtGui, QtWidgets
import send2trash
import os
import pandas as pd
import logging




class DirBrowserTableModel(QtCore.QAbstractTableModel):
    TableHeader = ["file name", "exp. time", "analog gain", "comment"]
    DataHeader = ["FileName", "ExposureSpeed", "AnalogGain", "comment"]

    def __init__(self, parent, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.parent = parent
        self.Data = pd.DataFrame()


    def setData(self, df):
        self.layoutAboutToBeChanged.emit()
        self.Data = df.copy()
        self.Data["__isMarked"] = False
        self.layoutChanged.emit()


    def getFileName(self, index):
        return self.Data.iloc[index.row()]["FileName"]


    def markLine(self, index):
        self.layoutAboutToBeChanged.emit()
        self.Data["__isMarked"] = False
        self.Data.at[self.Data.index[index.row()], "__isMarked"] = True
        self.layoutChanged.emit()


    def removeFilesFromList(self, FileNames):
        self.layoutAboutToBeChanged.emit()
        self.Data = self.Data[self.Data["FileName"].isin(FileNames) == False]
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.Data)


    def columnCount(self, parent):
        return len(self.TableHeader)


    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.TableHeader[col]
        return None


    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            Val = self.Data.iloc[index.row()][self.DataHeader[index.column()]]
            if pd.isna(Val):
                return ""
            if self.DataHeader[index.column()] == "AnalogGain":
                return "%.1f" % Val
            if self.DataHeader[index.column()] == "ExposureSpeed":
                if Val < 1e3:
                    return "%.0f us" % (Val)
                if Val < 1e6:
                    return "%.1f ms" % (Val / 1e3)
                return "%.1f s" % (Val / 1e6)
            return Val
        elif role == QtCore.Qt.ForegroundRole:
            if self.Data.iloc[index.row()]["__isMarked"]:
                return QtGui.QBrush(QtCore.Qt.green)
            #else:
            #    return QtGui.QBrush(QtCore.Qt.white)
        else:
            return None


    # def flags(self, index):
    #     if not index.isValid():
    #         return None
    #     if self.Header[index.column()] == "cor_factor":
    #         return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
    #     else:
    #         return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    # def setData(self, index, value, role=QtCore.Qt.EditRole):
    #     if type(value) in [str, unicode]:
    #         Locale = QtCore.QLocale()
    #         (val, ok) = Locale.toFloat(value)
    #         if not ok:
    #             QtGui.QMessageBox.critical(self.parent, "Error in number input",
    #                                        "Wrong input format: %s" % (value))
    #             return False
    #     else:
    #         val = value
    #     row = index.row()
    #     Sensor = self.ListOfSensors[row]
    #     SensorInst = Sensor["Path"].getInstance()
    #     BestFactor = self.CalcBestFactor(SensorInst, val)
    #     self.ListOfSensors[row]["cor_factor"] = BestFactor
    #     self.ListOfSensors[row]["HasChanged"] = self.NeedsReprogramming(Sensor)
    #     self.dataChanged.emit(index, index)
    #     return True


    def sort(self, col, order):
        """sort table by given column number col"""
        if len(self.Data) > 0:
            self.layoutAboutToBeChanged.emit()
            Key = self.DataHeader[col]
            if order == QtCore.Qt.DescendingOrder:
                self.Data.sort_values(by=Key, ascending=False, inplace=True)
            else:
                self.Data.sort_values(by=Key, ascending=True, inplace=True)
            self.layoutChanged.emit()


class DirBrowserTableView(QtWidgets.QTableView):

    def __init__(self, parent=None):
        super(DirBrowserTableView, self).__init__(parent)
        self.FileTableModel = DirBrowserTableModel(self)
        self.setModel(self.FileTableModel)
        self.horizontalHeader().setSectionResizeMode(
            self.FileTableModel.DataHeader.index("FileName"), QtWidgets.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(
            self.FileTableModel.DataHeader.index("comment"), QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(
            self.FileTableModel.DataHeader.index("ExposureSpeed"), QtWidgets.QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(
            self.FileTableModel.DataHeader.index("AnalogGain"), QtWidgets.QHeaderView.Interactive)
        #self.tableView_Files.horizontalHeader().setDefaultSectionSize(200)
        self.setSortingEnabled(True)

    def setData(self, df, RootDir=None):
        self.FileTableModel.setData(df)
        self.RootDir = RootDir


    def getFileName(self, idx):
        if self.RootDir is None:
            return self.FileTableModel.getFileName(idx)
        else:
            return os.path.join(self.RootDir, self.FileTableModel.getFileName(idx))


    def markLine(self, idx):
        self.FileTableModel.markLine(idx)


    def contextMenuEvent(self, event):
        self.menu = QtWidgets.QMenu(self)
        HideAction = QtWidgets.QAction('Remove from list', self)
        HideAction.triggered.connect(self.removeFromList)
        self.menu.addAction(HideAction)
        DeleteAction = QtWidgets.QAction('Delete from disk', self)
        DeleteAction.triggered.connect(self.deleteFiles)
        self.menu.addAction(DeleteAction)
        # add other required actions
        self.menu.popup(QtGui.QCursor.pos())


    def removeFromList(self):
        logging.debug("Removing files from list...")
        # get the selected rows
        FNs = [self.FileTableModel.getFileName(i) for i in self.selectionModel().selection().indexes()]
        logging.debug("  %s" % str(FNs))
        self.FileTableModel.removeFilesFromList(FNs)


    def deleteFiles(self):
        logging.debug("Deleting files from disk...")
        # get the selected rows
        FNs = [self.FileTableModel.getFileName(i) for i in self.selectionModel().selection().indexes()]
        if QtWidgets.QMessageBox.question(self, "Are you sure to delete these files?", "\n".join(FNs),
                                          buttons= QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Abort,
                                          defaultButton = QtWidgets.QMessageBox.Abort) == QtWidgets.QMessageBox.Ok:
            logging.debug("moving to trash: %s" % str(FNs))
            for FN in FNs:
                send2trash.send2trash(
                    FN if self.RootDir is None else os.path.join(self.RootDir, FN)
                )
            self.FileTableModel.removeFilesFromList(FNs)



