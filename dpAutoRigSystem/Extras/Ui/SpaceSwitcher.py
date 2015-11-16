# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/sbourgoing/dev/dpAutoRigSystem/dpAutoRigSystem/Extras/Ui/SpaceSwitcher.ui'
#
# Created: Mon Nov 16 10:24:55 2015
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_win_main(object):
    def setupUi(self, win_main):
        win_main.setObjectName("win_main")
        win_main.resize(380, 267)
        self.centralwidget = QtGui.QWidget(win_main)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblInfo = QtGui.QLabel(self.centralwidget)
        self.lblInfo.setObjectName("lblInfo")
        self.verticalLayout.addWidget(self.lblInfo)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chkUseParent = QtGui.QCheckBox(self.centralwidget)
        self.chkUseParent.setChecked(True)
        self.chkUseParent.setObjectName("chkUseParent")
        self.horizontalLayout.addWidget(self.chkUseParent)
        self.btnHelpParent = QtGui.QPushButton(self.centralwidget)
        self.btnHelpParent.setMaximumSize(QtCore.QSize(20, 16777215))
        self.btnHelpParent.setObjectName("btnHelpParent")
        self.horizontalLayout.addWidget(self.btnHelpParent)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lblStatus = QtGui.QLabel(self.centralwidget)
        self.lblStatus.setObjectName("lblStatus")
        self.verticalLayout.addWidget(self.lblStatus)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lstParent = QtGui.QListView(self.centralwidget)
        self.lstParent.setModelColumn(0)
        self.lstParent.setObjectName("lstParent")
        self.horizontalLayout_3.addWidget(self.lstParent)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.btnAction = QtGui.QPushButton(self.centralwidget)
        self.btnAction.setObjectName("btnAction")
        self.verticalLayout.addWidget(self.btnAction)
        win_main.setCentralWidget(self.centralwidget)

        self.retranslateUi(win_main)
        QtCore.QMetaObject.connectSlotsByName(win_main)

    def retranslateUi(self, win_main):
        win_main.setWindowTitle(QtGui.QApplication.translate("win_main", "Space Switcher", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInfo.setText(QtGui.QApplication.translate("win_main", "Choose the Drivers and after Driven Node to constraint", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUseParent.setText(QtGui.QApplication.translate("win_main", "Use Direct Parent", None, QtGui.QApplication.UnicodeUTF8))
        self.btnHelpParent.setText(QtGui.QApplication.translate("win_main", "?", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("win_main", "Driven Node --> None", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAction.setText(QtGui.QApplication.translate("win_main", "Switch Driver", None, QtGui.QApplication.UnicodeUTF8))

