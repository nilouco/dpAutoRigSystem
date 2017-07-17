# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/sbourgoing/dev/dpAutoRigSystem/dpAutoRigSystem/Extras/Ui/PoseReader.ui'
#
# Created: Thu Dec 10 14:03:17 2015
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from ...Vendor.Qt import QtCore, QtGui, QtWidgets, QtCompat

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(613, 282)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnCreate = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCreate.sizePolicy().hasHeightForWidth())
        self.btnCreate.setSizePolicy(sizePolicy)
        self.btnCreate.setMaximumSize(QtCore.QSize(93, 27))
        self.btnCreate.setObjectName("btnCreate")
        self.horizontalLayout.addWidget(self.btnCreate)
        self.edtNewName = QtWidgets.QLineEdit(self.centralwidget)
        self.edtNewName.setObjectName("edtNewName")
        self.horizontalLayout.addWidget(self.edtNewName)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblData = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblData.sizePolicy().hasHeightForWidth())
        self.tblData.setSizePolicy(sizePolicy)
        self.tblData.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tblData.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.tblData.setLineWidth(1)
        self.tblData.setMidLineWidth(0)
        self.tblData.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tblData.setAlternatingRowColors(False)
        self.tblData.setObjectName("tblData")
        self.tblData.setColumnCount(4)
        self.tblData.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblData.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblData.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblData.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblData.setHorizontalHeaderItem(3, item)
        self.tblData.horizontalHeader().setVisible(True)
        self.tblData.horizontalHeader().setCascadingSectionResizes(True)
        self.tblData.horizontalHeader().setDefaultSectionSize(150)
        self.tblData.horizontalHeader().setStretchLastSection(True)
        self.tblData.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblData)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.btnRefresh = QtWidgets.QPushButton(self.centralwidget)
        self.btnRefresh.setObjectName("btnRefresh")
        self.horizontalLayout_3.addWidget(self.btnRefresh)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtCompat.translate("MainWindow", "Main Window", None, -1))
        self.btnCreate.setText(QtCompat.translate("MainWindow", "Create", None, -1))
        self.tblData.setSortingEnabled(True)
        self.tblData.horizontalHeaderItem(0).setText(QtCompat.translate("MainWindow", "Name", None, -1))
        self.tblData.horizontalHeaderItem(1).setText(QtCompat.translate("MainWindow", "Axis", None, -1))
        self.tblData.horizontalHeaderItem(2).setText(QtCompat.translate("MainWindow", "Extract Axis Order", None, -1))
        self.tblData.horizontalHeaderItem(3).setText(QtCompat.translate("MainWindow", "Angle", None, -1))
        self.btnRefresh.setText(QtCompat.translate("MainWindow", "Refresh", None, -1))

