try:
    import pymel.core as pymel
    try:
        from sstk.libs.libQt import QtCore, QtWidgets
        from sstk.libs import libSerialization
    except:
        from ..Vendor.Qt import QtCore, QtGui, QtWidgets, QtCompat
        from ..Modules.Library import libSerialization
    from Ui import PoseReader as poseReaderUI
    reload(poseReaderUI)
    from maya import OpenMayaUI
    from functools import partial
    import maya.cmds as cmds
except Exception as e:
    print "Error: importing python modules!!!\n",
    print e


# global variables to this module:
CLASS_NAME = "PoseReader"
TITLE = "m068_poseReader"
DESCRIPTION = "m069_poseReaderDesc"
ICON = "/Icons/sq_poseReader.png"

#Class to contain the data of the system that will be Monkey patched when needed.
#After Monkey patching, just print the __dict__ of the data and create the variable here
class PoseReaderData(object):
    def __init__(self):
        nParent = None #Parent Bone
        nDecM = None #Decompose Matrice
        nMultM = None #Multiply Matrice
        nChild = None #Child bone
        nMDActive = None #Multiply divide to put a manual intensity
        nCGrp = None #Child group
        nPGrp = None #Parent group
        nMD = None #Normalization multiply divide node
        nParentLoc = None #Parent locator
        nChildLoc = None #Child locator
        nCD = None #Condition to activate the blendshape
        nCDNoNeg = None #Ensure blend shape value is over 0 and under 1.0


# src: https://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/Maya-SDK/files/GUID-3F96AF53-A47E-4351-A86A-396E7BFD6665-htm.html
def getMayaWindow():
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(long(ptr), QtWidgets.QWidget)
    

class PoseReaderDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow(), *args, **kwargs):
        super(PoseReaderDialog, self).__init__(parent)
        self.ID_COL_NAME = 0
        self.ID_COL_AXIS = 1
        self.ID_COL_AXISORDER = 2
        self.ID_COL_ANGLE = 3
        self.ui = poseReaderUI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btnCreate.setEnabled(False)
        self.setupCallbacks()
        self.populateData()

    def setupCallbacks(self):
        self.ui.btnCreate.pressed.connect(self.on_action_create)
        self.ui.edtNewName.textChanged.connect(self.on_action_textChange)
        self.ui.btnRefresh.pressed.connect(self.refresh)

    def populateData(self):
        lstNetworkNode = libSerialization.getNetworksByClass(PoseReaderData.__name__)
        aToDel = []
        for pNet in lstNetworkNode:
            pData = libSerialization.import_network(pNet)
            #Ensure that the network is valid, if not, delete the network node
            for sVar in pData.__dict__ :
                #print "{0} --> {1}".format(sVar, pData.__dict__[sVar])
                if not (pData.__dict__[sVar]): #TODO --> Delete invalid system node ?
                    aToDel.append(pNet)
                    break;
            if not aToDel: self.addItem(pData)

        if aToDel:
            pymel.delete(aToDel)

    #We could use the function pymel.spaceLocator() :P
    def createLoc(self, sName, nParent):
        nTran = pymel.createNode("transform", n=sName, p=nParent)
        pymel.createNode("locator", n= (sName + "Shape"), p=nTran)
        return nTran

    def addItem(self, pData):
        #Extract the prefix of the PoseReader node that should be the name
        sName = pData.nChildLoc.name().split("_")[0]
        iAxisIdx = pData.nChildLoc.axis.get()
        iAxisOrder = pData.nDecM.inputRotateOrder.get()
        fAngle = pData.nChildLoc.angleMaxValue.get()

        iCurRowIdx = self.ui.tblData.rowCount()
        self.ui.tblData.insertRow(iCurRowIdx)

        #Create the name field
        pCellName = QtWidgets.QTableWidgetItem()
        self.ui.tblData.setItem(iCurRowIdx, self.ID_COL_NAME, pCellName)

        edtName = QtWidgets.QLineEdit()
        edtName.setText(sName)
        edtName.textChanged.connect(partial(self.on_action_nameChange, iCurRowIdx, self.ID_COL_NAME))

        #Monkey patch the mouse event function to create a right click menu on it.
        #I could have redefined a class that inherit the QLineEdit class, but....
        edtName.mousePressEvent = partial(self.mousePressEventEdt, iRow=iCurRowIdx, iCol = self.ID_COL_NAME)

        self.ui.tblData.setCellWidget(iCurRowIdx, self.ID_COL_NAME, edtName)

        #Set custom data to retrieve the object associated to the value in the cell
        pCellName.setData(QtCore.Qt.UserRole, pData)

        #Create the comboBox for axis selection
        pCellAxis = QtWidgets.QTableWidgetItem()
        self.ui.tblData.setItem(iCurRowIdx, self.ID_COL_AXIS, pCellAxis)

        cbAxis = QtWidgets.QComboBox()
        aAxisName = ("X", "Y", "Z")
        cbAxis.addItems(aAxisName)
        cbAxis.setCurrentIndex(iAxisIdx)
        cbAxis.currentIndexChanged.connect(partial(self.on_action_axisChange, iCurRowIdx, self.ID_COL_AXIS))
        self.ui.tblData.setCellWidget(iCurRowIdx, self.ID_COL_AXIS, cbAxis)

        #Pass the whole data since we will need to access more than one object
        pCellAxis.setData(QtCore.Qt.UserRole, pData)

        #Create the comboBox for axis order
        pCellAxisOrder = QtWidgets.QTableWidgetItem()
        self.ui.tblData.setItem(iCurRowIdx, self.ID_COL_AXISORDER, pCellAxisOrder)

        cbAxisOrder = QtWidgets.QComboBox()
        aAxisOrderName = ("XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX")
        cbAxisOrder.addItems(aAxisOrderName)
        cbAxisOrder.setCurrentIndex(iAxisOrder)
        cbAxisOrder.currentIndexChanged.connect(partial(self.on_action_axisOrderChange, iCurRowIdx, self.ID_COL_AXISORDER))
        self.ui.tblData.setCellWidget(iCurRowIdx, self.ID_COL_AXISORDER, cbAxisOrder)

        #Pass the whole data since we will need to access more than one object
        pCellAxisOrder.setData(QtCore.Qt.UserRole, pData)

        #Create a spinBox to restrict user to a range of angle
        pCellAngle = QtWidgets.QTableWidgetItem()
        self.ui.tblData.setItem(iCurRowIdx, self.ID_COL_ANGLE, pCellAngle)

        spnAngle = QtWidgets.QSpinBox()
        spnAngle.setRange(-360.0, 360.0)
        spnAngle.setValue(fAngle)
        spnAngle.valueChanged.connect(partial(self.on_action_angleChange, iCurRowIdx, self.ID_COL_AXIS))
        self.ui.tblData.setCellWidget(iCurRowIdx, self.ID_COL_ANGLE, spnAngle)

        #Pass the attribute set function
        pCellAngle.setData(QtCore.Qt.UserRole, pData)

    #Rename all object in the system to match the new prefix
    def on_action_nameChange(self, iRow, iCol, *args):
        pCell = self.ui.tblData.item(iRow,iCol)
        pData = pCell.data(QtCore.Qt.UserRole)
        sCurPrefix = pData.nChildLoc.name().split("_")[0]
        for sName in pData.__dict__:
            pCurObj = pData.__dict__[sName]
            sNewName = pCurObj.name().replace(sCurPrefix, args[0])
            pymel.rename(pCurObj, sNewName)

    #Change the axis connection of the system to connect in the good axis
    def on_action_axisChange(self, iRow, iCol, *args):
        pCell = self.ui.tblData.item(iRow,iCol)
        pData = pCell.data(QtCore.Qt.UserRole)

        pData.nChildLoc.axis.set(args[0])

        #Delete old connection
        pymel.disconnectAttr(pData.nMD.input1X)

        lstXCon = pData.nDecM.outputRotateX.listConnections()
        pymel.disconnectAttr(pData.nDecM.outputRotateX)
        pymel.delete(lstXCon)

        lstYCon = pData.nDecM.outputRotateY.listConnections()
        pymel.disconnectAttr(pData.nDecM.outputRotateY)
        pymel.delete(lstYCon)

        lstZCon = pData.nDecM.outputRotateZ.listConnections()
        pymel.disconnectAttr(pData.nDecM.outputRotateZ)
        pymel.delete(lstZCon)

        if args[0] == 0:
            pymel.connectAttr(pData.nDecM.outputRotateX, pData.nMD.input1X, f=True)
        elif args[0] == 1:
             pymel.connectAttr(pData.nDecM.outputRotateY, pData.nMD.input1X, f=True)
        elif args[0] == 2:
             pymel.connectAttr(pData.nDecM.outputRotateZ, pData.nMD.input1X, f=True)

    #Change the axis connection of the system to connect in the good axis
    def on_action_axisOrderChange(self, iRow, iCol, *args):
        pCell = self.ui.tblData.item(iRow,iCol)
        pData = pCell.data(QtCore.Qt.UserRole)

        pData.nDecM.inputRotateOrder.set(args[0])

    #Change the angle data value of the system
    def on_action_angleChange(self, iRow, iCol, *args):
        pCell = self.ui.tblData.item(iRow,iCol)
        pData = pCell.data(QtCore.Qt.UserRole)
        pData.nChildLoc.angleMaxValue.set(args[0])

    def on_action_textChange(self, *args):
        sName = self.ui.edtNewName.text()
        if sName:
            self.ui.btnCreate.setEnabled(True)
        else:
            self.ui.btnCreate.setEnabled(False)

    def on_action_create(self, *args):
        sName = self.ui.edtNewName.text()

        # loading Maya matrix node
        if not (cmds.pluginInfo("decomposeMatrix", query=True, loaded=True)):
            try: # Maya 2012
                cmds.loadPlugin("decomposeMatrix.mll")
            except:
                try: # Maya 2013 or earlier
                    cmds.loadPlugin("matrixNodes.mll")
                except:
                    print self.langDic[self.langName]['e002_decomposeMatrixNotFound']
                    
        aSel = pymel.selected()
        if (len(aSel) == 2):
            #Create the container of the system data
            pData = PoseReaderData()
            with pymel.UndoChunk():
                #Get Needed matrix information
                pData.nParent = aSel[1]
                pData.nChild = aSel[0]
                m4ParentMat = pData.nParent.getMatrix(worldSpace=True)
                m4ChildMat = pData.nChild.getMatrix(worldSpace=True)

                #Create the two node needed to extract the rotation
                pData.nPGrp = pymel.createNode("transform", name=sName + "_PoseReader_Parent_Grp", p=pData.nParent)
                pData.nPGrp.setMatrix(m4ChildMat, worldSpace=True)
                pData.nParentLoc = self.createLoc(sName+"_AngExtract_ParentLoc", pData.nPGrp)

                pData.nCGrp = pymel.createNode("transform", name=sName+"_PoseReader_Child_Grp", p=pData.nChild)
                pData.nCGrp.setMatrix(m4ChildMat, worldSpace=True)
                pData.nChildLoc = self.createLoc(sName+"_AngExtract_ChildLoc", pData.nCGrp)
                #Add usefull attributes for the tool
                pData.nChildLoc.setDynamicAttr("posereaderdata", True)
                pData.nChildLoc.addAttr("angleMaxValue", min=-360.0, max=360.0)
                pData.nChildLoc.setAttr("angleMaxValue", 180, edit=True, keyable=False, lock=False)
                pData.nChildLoc.addAttr("axis", at="enum", enumName="X:Y:Z")
                pData.nChildLoc.setAttr("axis", 1, edit=True, keyable=False, lock=False)

                #Setup the rotation extaction
                pData.nMultM = pymel.createNode("multMatrix", name=sName+"_ExtactAngle_MM")
                pymel.connectAttr(pData.nChildLoc.worldMatrix[0], pData.nMultM.matrixIn[0])
                pymel.connectAttr(pData.nParentLoc.worldInverseMatrix[0], pData.nMultM.matrixIn[1])
                pData.nDecM = pymel.createNode("decomposeMatrix", name=sName+"_ExtractAngle_DM")
                pymel.connectAttr(pData.nMultM.matrixSum, pData.nDecM.inputMatrix)

                #Setup the rotation affection
                pData.nMD = pymel.createNode("multiplyDivide", name=sName+"_NormValue_MD")
                pData.nMD.operation.set(2)
                pymel.connectAttr(pData.nDecM.outputRotateY, pData.nMD.input1X)
                pymel.connectAttr(pData.nChildLoc.angleMaxValue, pData.nMD.input2X)
                pData.nCD = pymel.createNode("condition", name=sName+"_SmallerThanOne_CD")
                pymel.connectAttr(pData.nMD.outputX, pData.nCD.firstTerm)
                pymel.connectAttr(pData.nMD.outputX, pData.nCD.colorIfTrueR)
                pData.nCD.secondTerm.set(1)
                pData.nCD.operation.set(5) #Less or equal
                pData.nCDNoNeg = pymel.createNode("condition", name=sName+"_OverZero_CD")
                pymel.connectAttr(pData.nCD.outColorR, pData.nCDNoNeg.firstTerm)
                pymel.connectAttr(pData.nCD.outColorR, pData.nCDNoNeg.colorIfTrueR)
                pData.nCDNoNeg.secondTerm.set(0)
                pData.nCDNoNeg.colorIfFalseR.set(0)
                pData.nCDNoNeg.operation.set(3) #Greater or Equal

                #Node for manual activation connection
                pData.nMDActive = pymel.createNode("multiplyDivide", name=sName+"_Active_MD")
                pymel.connectAttr(pData.nCDNoNeg.outColorR, pData.nMDActive.input1X)

            #for o in pData.__dict__:
                #print o

            libSerialization.export_network(pData)
            self.addItem(pData)
        else:
            pymel.confirmDialog( title='Selection Problem', message='You need to have exactly two nodes selected')


    def mousePressEventEdt(self, event, iCol=0, iRow=0):
        if event.button() == QtCore.Qt.RightButton:
            pCell = self.ui.tblData.item(iRow,iCol)
            pData = pCell.data(QtCore.Qt.UserRole) #Attr set function
            menu = QtWidgets.QMenu()
            action_sel_child = menu.addAction('Select Child')
            action_sel_child.triggered.connect(partial(pymel.select, pData.nChildLoc))
            action_sel_parent = menu.addAction('Select Parent');
            action_sel_parent.triggered.connect(partial(pymel.select, pData.nParentLoc))
            action_sel_parent = menu.addAction('Select Bones');
            action_sel_parent.triggered.connect(partial(pymel.select, [pData.nParent, pData.nChild]))
            action_sel_parent = menu.addAction('Delete');
            action_sel_parent.triggered.connect(partial(self.deleteSystem, pData))
            menu.exec_(QtGui.QCursor.pos())

    def deleteSystem(self, pData):
        aToDel = [pData.__dict__[sName] for sName in pData.__dict__ if sName != "nParent" and sName != "nChild"]
        pymel.delete(aToDel)
        self.refresh()

    def refresh(self):
        for iRow in xrange(self.ui.tblData.rowCount(), -1, -1):
            self.ui.tblData.removeRow(iRow)
        self.populateData()


class PoseReader():
    def __init__(self, *args, **kwargs):
        #Try to kill the existing window
        try:
            if cmds.window("PoseReader", ex=True):
                cmds.deleteUI("PoseReader")
        except:
            pass

        self.pDialog = PoseReaderDialog(getMayaWindow())
        self.centerDialog()
        self.pDialog.setWindowTitle("Pose Reader")
        self.pDialog.setObjectName("PoseReader")
        self.pDialog.show()

    def centerDialog(self):
        #Create a frame geo to easilly move it from the center
        pFrame = self.pDialog.frameGeometry()
        pScreen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        ptCenter = QtWidgets.QApplication.desktop().screenGeometry(pScreen).center()
        pFrame.moveCenter(ptCenter)
        self.pDialog.move(pFrame.topLeft())