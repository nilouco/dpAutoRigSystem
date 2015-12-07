# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/sbourgoing/dev/dpAutoRigSystem/dpAutoRigSystem/Extras/Ui/SpaceSwitcher.ui'
#
# Created: Fri Dec  4 17:24:43 2015
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_win_main(object):
    def setupUi(self, win_main):
        win_main.setObjectName("win_main")
        win_main.resize(479, 517)
        win_main.setSizeIncrement(QtCore.QSize(0, 0))
        win_main.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.centralwidget = QtGui.QWidget(win_main)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblSetupInfo = QtGui.QLabel(self.centralwidget)
        self.lblSetupInfo.setObjectName("lblSetupInfo")
        self.verticalLayout.addWidget(self.lblSetupInfo)
        self.lblStatus = QtGui.QLabel(self.centralwidget)
        self.lblStatus.setObjectName("lblStatus")
        self.verticalLayout.addWidget(self.lblStatus)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAction = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAction.sizePolicy().hasHeightForWidth())
        self.btnAction.setSizePolicy(sizePolicy)
        self.btnAction.setMinimumSize(QtCore.QSize(100, 0))
        self.btnAction.setObjectName("btnAction")
        self.horizontalLayout.addWidget(self.btnAction)
        self.lstParent = QtGui.QListView(self.centralwidget)
        self.lstParent.setModelColumn(0)
        self.lstParent.setObjectName("lstParent")
        self.horizontalLayout.addWidget(self.lstParent)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(458, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.lblFrameInfo = QtGui.QLabel(self.centralwidget)
        self.lblFrameInfo.setTextFormat(QtCore.Qt.AutoText)
        self.lblFrameInfo.setObjectName("lblFrameInfo")
        self.verticalLayout.addWidget(self.lblFrameInfo)
        self.tblFrameInfo = QtGui.QTableWidget(self.centralwidget)
        self.tblFrameInfo.setObjectName("tblFrameInfo")
        self.tblFrameInfo.setColumnCount(2)
        self.tblFrameInfo.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tblFrameInfo.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tblFrameInfo.setHorizontalHeaderItem(1, item)
        self.tblFrameInfo.horizontalHeader().setVisible(True)
        self.tblFrameInfo.horizontalHeader().setCascadingSectionResizes(True)
        self.tblFrameInfo.horizontalHeader().setDefaultSectionSize(100)
        self.tblFrameInfo.horizontalHeader().setStretchLastSection(True)
        self.tblFrameInfo.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblFrameInfo)
        win_main.setCentralWidget(self.centralwidget)

        self.retranslateUi(win_main)
        QtCore.QMetaObject.connectSlotsByName(win_main)

    def retranslateUi(self, win_main):
        win_main.setWindowTitle(QtGui.QApplication.translate("win_main", "Space Switcher", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSetupInfo.setText(QtGui.QApplication.translate("win_main", "<b>Parent Info</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("win_main", "Current Node --> None", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAction.setText(QtGui.QApplication.translate("win_main", "Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFrameInfo.setText(QtGui.QApplication.translate("win_main", "<b>Frame/Constraint Info</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.tblFrameInfo.setSortingEnabled(True)
        self.tblFrameInfo.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("win_main", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.tblFrameInfo.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("win_main", "Parent", None, QtGui.QApplication.UnicodeUTF8))

