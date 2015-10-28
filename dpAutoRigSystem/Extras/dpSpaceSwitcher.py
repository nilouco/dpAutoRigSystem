try:
    import math
    import maya.cmds as cmds
    import pymel.core as pymel
    import maya.OpenMaya as om
    from ..Modules.Library import dpControls as ctrlUtil
    from ..Modules.Library import dpUtils as utils
    from Ui import SpaceSwitcher as spaceSwitcherUI
    reload(spaceSwitcherUI)
    import shiboken
    from maya import OpenMayaUI
    from sstk.libs.libQt import QtCore, QtGui
    from sstk.libs import libSerialization
    from functools import partial
except Exception as e:
    print "Error: importing python modules!!!\n",
    print e


# global variables to this module:
CLASS_NAME = "SpaceSwitcher"
TITLE = "m071_SpaceSwitcher"
DESCRIPTION = "m072_SpaceSwitcherDesc"
ICON = ""

class SpaceSwitcherLogic(object):

    """
    This class is used to setup a spaceSwitch system on a node
    """

    WORLD_NODE_NAME = "dp_sp_worldNode"

    def __init__(self):
        self.aDrivers = {}
        self.nDriven = None
        self.nSwConst = None #SpaceSwitch constraint for the system
        self.nSwConstRecept = None #Space Switch receiver
        self.nSwOff = None #Space Switch offset
        tempWorld = pymel.ls(self.WORLD_NODE_NAME)
        if tempWorld:
            self.worldNode = tempWorld[0]
        else:
            self.worldNode = None

    def setup_space_switch(self, nDriven=None, aDrivers=None, bCreateWolrdNode=False, bCreateParent=True):
            aCurSel = pymel.selected()
            if aDrivers == None:
                aParent = aCurSel[0:-1]
            else:
                aParent = aDrivers

            bContinue = False
            #Create the worldNode
            if (not self.worldNode and bCreateWolrdNode):
                self.worldNode = pymel.createNode("transform", n="dp_sp_worldNode")
                ctrlUtil.setLockHide([self.worldNode.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

            if (self.worldNode):
                self.aDrivers.append(self.worldNode)

            if (not nDriven):
                if (len(aCurSel) == 0):
                    pymel.informBox("Space Switcher", "You need to choose at least the node to constraint")
                #The user only selected the driven node, so create a space switch between it's parent and the world
                elif (len(aCurSel) == 1):
                    self.nDriven = aCurSel[0]
                    bContinue = True
                else:
                    self.nDriven = aCurSel[-1]
                    bContinue = True
            else:
                self.nDriven = nDriven
                bContinue = True

            if bContinue:
                #Setup the intermediate node to manage the spaceSwitch
                if bCreateParent:
                    self.nSwConstRecept = pymel.PyNode(utils.zeroOut(transformList=[self.nDriven.__melobject__()])[0])
                    self.nSwConstRecept.rename(self.nDriven.name() + "_SW_Const")
                else:
                    self.nSwConstRecept = self.nDriven.getParent()
                m4Driven = self.nDriven.getMatrix(worldSpace=True)
                self.nSwConstRecept.setMatrix(m4Driven, worldSpace=True)
                self.nDriven.setParent(self.nSwConstRecept)

                #Create the parent constraint for the first node, but add the other target manually
                if (bCreateWolrdNode):
                    self.nSwConst = pymel.parentConstraint(self.worldNode, self.nSwConstRecept, n=self.nDriven.name() + "_SpaceSwitch_Const", mo=True)
                else:
                    self.nSwConst = pymel.parentConstraint(aParent[0], self.nSwConstRecept, n=self.nDriven.name() + "_SpaceSwitch_Const", mo=True)
                    self.aDrivers.append(aParent[0])
                    aParent = aParent[1:]

                self.nSwConst.getWeightAliasList()[0].set(0.0)

                #Setup the first key for the current activate constraint, targets offset and rest position
                pymel.setKeyframe(self.nSwConst.getWeightAliasList()[0], t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[0].targetOffsetTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[0].targetOffsetRotate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.restTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.restRotate, t=0, ott="step")

                self.add_target(aParent)

    def add_target(self, aNewParent, firstSetup=False):
        iNbTgt = len(self.nSwConst.getWeightAliasList())
        aExistTgt = self.nSwConst.getTargetList()
        bContinue = True

        if aExistTgt:
            for nTgt in aExistTgt:
                if (nTgt in aNewParent) and bContinue:
                    pymel.informBox("Space Switcher", "Cannot add target " + nTgt.name() + " because it is already added to the list of parent")
                    bContinue = False

        if bContinue:
            for nParent in aNewParent:
                #First, calculate the offset between the parent and the driven node
                vTrans = self._get_tm_offset(nParent, type="t")
                vRot = self._get_tm_offset(nParent, type="r")

                #Connect the new target manually in the parent constraint
                if (iNbTgt == 0):
                    self.nSwConst.addAttr(nParent.name() + "W" + str(iNbTgt), at="double", min=0, max=1, dv=1, k=True, h=False)
                else:
                    self.nSwConst.addAttr(nParent.name() + "W" + str(iNbTgt), at="double", min=0, max=1, dv=0, k=True, h=False)

                pymel.connectAttr(nParent.parentMatrix, self.nSwConst.target[iNbTgt].targetParentMatrix)
                pymel.connectAttr(nParent.scale, self.nSwConst.target[iNbTgt].targetScale)
                pymel.connectAttr(nParent.rotateOrder, self.nSwConst.target[iNbTgt].targetRotateOrder)
                pymel.connectAttr(nParent.rotate, self.nSwConst.target[iNbTgt].targetRotate)
                pymel.connectAttr(nParent.rotatePivotTranslate, self.nSwConst.target[iNbTgt].targetRotateTranslate)
                pymel.connectAttr(nParent.rotatePivot, self.nSwConst.target[iNbTgt].targetRotatePivot)
                pymel.connectAttr(nParent.translate, self.nSwConst.target[iNbTgt].targetTranslate)
                #Link the created attributes to the weight value of the target
                nConstTgtWeight = pymel.Attribute(self.nSwConst.name() + "." + nParent.name() + "W" + str(iNbTgt))
                pymel.connectAttr(nConstTgtWeight, self.nSwConst.target[iNbTgt].targetWeight)

                #Set the offset information
                self.nSwConst.target[iNbTgt].targetOffsetTranslate.targetOffsetTranslateX.set(vTrans[0])
                self.nSwConst.target[iNbTgt].targetOffsetTranslate.targetOffsetTranslateY.set(vTrans[1])
                self.nSwConst.target[iNbTgt].targetOffsetTranslate.targetOffsetTranslateZ.set(vTrans[2])
                self.nSwConst.target[iNbTgt].targetOffsetRotate.targetOffsetRotateX.set(vRot[0])
                self.nSwConst.target[iNbTgt].targetOffsetRotate.targetOffsetRotateY.set(vRot[1])
                self.nSwConst.target[iNbTgt].targetOffsetRotate.targetOffsetRotateZ.set(vRot[2])

                #Need to be setted with cmds, because pymel give strange error
                """
                cmds.setAttr("%s.target[%s].targetOffsetTranslateX"%(self.nSwConst.__melobject__(), iNbTgt), vTrans[0])
                cmds.setAttr("%s.target[%s].targetOffsetTranslateY"%(self.nSwConst.__melobject__(), iNbTgt), vTrans[1])
                cmds.setAttr("%s.target[%s].targetOffsetTranslateZ"%(self.nSwConst.__melobject__(), iNbTgt), vTrans[2])
                cmds.setAttr("%s.target[%s].targetOffsetRotateX"%(self.nSwConst.__melobject__(), iNbTgt), vRot[0])
                cmds.setAttr("%s.target[%s].targetOffsetRotateY"%(self.nSwConst.__melobject__(), iNbTgt), vRot[1])
                cmds.setAttr("%s.target[%s].targetOffsetRotateZ"%(self.nSwConst.__melobject__(), iNbTgt), vRot[2])
                """

                pymel.setKeyframe(nConstTgtWeight, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetRotate, t=0, ott="step")
                self.aDrivers.append(nParent)
                iNbTgt += 1


    def _get_tm_offset(self, nParent, type="t"):
        mStart = om.MMatrix()
        mEnd =  om.MMatrix()

        wmStart = nParent.worldMatrix.get().__melobject__()
        wmEnd = self.nDriven.worldMatrix.get().__melobject__()

        om.MScriptUtil().createMatrixFromList(wmStart,mStart)
        om.MScriptUtil().createMatrixFromList(wmEnd,mEnd)

        mOut = om.MTransformationMatrix(mEnd * mStart.inverse())

        if type == "t":
            vTran = om.MVector(mOut.getTranslation(om.MSpace.kTransform))
            return vTran.x,vTran.y,vTran.z
        if type == "r":
            ro = self.nDriven.rotateOrder.get()
            vRot = om.MEulerRotation(mOut.eulerRotation().reorder(ro))
            return math.degrees(vRot.x), math.degrees(vRot.y), math.degrees(vRot.z)


    def do_switch(self, iIdx):
        fCurTime = pymel.currentTime()
        #Just try to update the offset of the parent constraint before the switch
        iActiveWeight = -1
        aWeight = self.nSwConst.getWeightAliasList()

        #If none is set to 1.0, the value will be -1 which represent the current parent
        for i, fValue in enumerate(aWeight):
            if fValue == 1.0:
                iActiveWeight = i
        if (iIdx == -1): #Special case to deactivate all constraint and let the parent work correctly
            #Update the rest pose with the current offset and key it to prevent the parent change too move
            self.nSwConst.restRotate.set(self.nSwConst.constraintRotate.get())
            self.nSwConst.restTranslate.set(self.nSwConst.constraintTranslate.get())
            pymel.setKeyframe(self.nSwConst.restTranslate, t=fCurTime, ott="step")
            pymel.setKeyframe(self.nSwConst.restRotate, t=fCurTime, ott="step")
            for wAlias in aWeight:
                wAlias.set(0.0)
            pymel.setKeyframe(aWeight, t=fCurTime, ott="step")
        elif (len(aWeight) > iIdx):
            if (iActiveWeight != iIdx):
                iActiveWeight = iIdx
                #Update constraint offset of the next index in the constraint
                pymel.parentConstraint(self.aDrivers[iIdx], self.nSwConst, mo=True, e=True)
                #Key the offset to prevent offset problem when coming back to the same parent
                pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetTranslate, t=fCurTime, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetRotate, t=fCurTime, ott="step")
                for i,wAlias in enumerate(aWeight):
                    if (i == iIdx):
                        wAlias.set(1.0)
                    else:
                        wAlias.set(0.0)
                #Set a keyframe on the weight to keep the animation
                pymel.setKeyframe(aWeight, t=fCurTime, ott="step")
                
        else:
            print "Cannot switch target, index is bigger than the number of target"


# src: http://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/Maya-SDK/files/GUID-3F96AF53-A47E-4351-A86A-396E7BFD6665-htm.html
def getMayaWindow():
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtGui.QWidget)


class SpaceSwitcherDialog(QtGui.QMainWindow):
    def __init__(self, parent=getMayaWindow(), *args, **kwargs):
        super(SpaceSwitcherDialog, self).__init__(parent)
        self.ui = spaceSwitcherUI.Ui_win_main()
        self.ui.setupUi(self)

        #Setup the base list of parent
        self.createModel = QtGui.QStandardItemModel(self.ui.lstParent)
        self.parentItem = QtGui.QStandardItem("Original Parent")
        self.createModel.appendRow(self.parentItem)
        self.ui.lstParent.setModel(self.createModel)
        self.createModel.item(0).setEnabled(False)


        self.ui.btnAdd.setEnabled(False)
        self.ui.btnAction.setEnabled(False)
        self.ui.btnAction.setText("Select a Node")
        self.ui.btnRemove.setEnabled(False)
        self.ui.lstParent.setEnabled(False)

        #Intern variable
        self.iJobNum = 0
        self.action = "#create" #Can be #create or #switch
        self.nDriven = None
        self.aDrivers = []
        self.aSceneSpaceSwitch = []

        self.colorTemplate = "<font color={0}>{1}</font>"

        self.setupCallbacks()

        #Force the tool to check the selection on it's opening
        self._selectionChange()
        self._fetch_system_from_scene()

    def setupCallbacks(self):
        self.ui.btnHelpParent.pressed.connect(self.action_show_parent_help)
        self.ui.btnAdd.pressed.connect(self.action_add_parent)
        self.ui.btnRemove.pressed.connect(self.action_remove_parent)
        self.ui.btnAction.pressed.connect(self.action_execute)

        self.iJobNum = pymel.scriptJob(event=('SelectionChanged', self._selectionChange),
                                       killWithScene=True, compressUndo=False)

    def _fetch_system_from_scene(self):
        lstNetworkNode = libSerialization.getNetworksByClass(SpaceSwitcherLogic.__name__)
        for pNet in lstNetworkNode:
            pData = libSerialization.import_network(pNet)
            self.aSceneSpaceSwitch.append(pData)

    def _selectionChange(self, *args):
        aCurSel = pymel.selected()

        if (len(aCurSel) == 0):
            self.nDriven = None
            self.aDrivers = []
        elif (len(aCurSel) == 1):
            self.nDriven = aCurSel[0]
            self.aDrivers = []
        else:
            self.nDriven = aCurSel[-1]
            self.aDrivers = aCurSel[0:-1]

        self.ui.lblStatus.setText("Driven Node --> " + str(self.nDriven) + "")

        if (self.nDriven != None):
            self.action = "#create"
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("yellow", "(First Setup)"))
            self.ui.btnAction.setEnabled(True)
            self.ui.btnAction.setText("Setup Space Switch System for [" + self.nDriven.name() + "]")
        else:
            self.ui.btnAction.setEnabled(False)
            self.ui.btnAction.setText("Choose a node")

    def closeEvent(self, *args, **kwargs):
        pymel.scriptJob(kill=self.iJobNum, force=True)

    def action_show_parent_help(self):
        sHelpMsg = "If checked, the direct parent of the driven node will be" \
                   " use as the recept of the parent constraint. Else, a new parent will be created. \n" \
                   "WARNING : New parent cannot be used on referenced node"
        pymel.informBox("Space Switcher", sHelpMsg)

    def action_add_parent(self):
        aSel = pymel.selected()
        aToAdd = []
        bCanAdd = True

        for pNode in aSel:
            sNodeName = pNode.name()
            if sNodeName != self.ui.edtDriven.text():
                bAlreadyExist = False
                for i in range(0, self.createModel.rowCount()):
                    if (self.createModel.item(i).text() == sNodeName):
                        bAlreadyExist = True
                        break;
                if (not bAlreadyExist):
                    pNewItem = QtGui.QStandardItem(sNodeName)
                    aToAdd.append(pNewItem)
            else:
                pymel.informBox("Space Switcher", "You cannot add the driven node as it's own parent")
                bCanAdd = False
                break

        if (bCanAdd):
            for pItem in aToAdd:
                self.createModel.appendRow(pItem)

        self._can_create()

    def action_remove_parent(self):
        aSelIdx = self.ui.lstNewParent.selectionModel().selectedIndexes()

        for pModelIdx in aSelIdx:
            iIdx = pModelIdx.row()
            self.createModel.removeRow(iIdx)

        self._can_create()

    def action_execute(self):
        if (self.action == "#create"):
            bCreateParent = not self.ui.chkUseParent.isChecked()
            pNewSp = SpaceSwitcherLogic()
            with pymel.UndoChunk():
                if self.aDrivers:
                    pNewSp.setup_space_switch(self.nDriven, self.aDrivers, bCreateWolrdNode=False, bCreateParent=bCreateParent)
                else: #There is no drivers, so the user want the world to be one of them
                    pNewSp.setup_space_switch(self.nDriven, self.aDrivers, bCreateWolrdNode=True, bCreateParent=bCreateParent)

            #libSerialization.export_network(pNewSp)



class SpaceSwitcher(object):
    """
    This class is used to create the main dialog and have the name of the file, so it need to exist to be correctly called
    """
    def __init__(self, *args, **kwargs):
        #Try to kill the existing window
        try:
            if cmds.window("SpaceSwitcher", ex=True):
                cmds.deleteUI("SpaceSwitcher")
        except:
            pass

        self.pDialog = SpaceSwitcherDialog(getMayaWindow())
        self.centerDialog()
        self.pDialog.setWindowTitle("Space Switcher")
        self.pDialog.setObjectName("SpaceSwitcher")
        self.pDialog.show()

    def centerDialog(self):
        #Create a frame geo to easilly move it from the center
        pFrame = self.pDialog.frameGeometry()
        pScreen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        ptCenter = QtGui.QApplication.desktop().screenGeometry(pScreen).center()
        pFrame.moveCenter(ptCenter)
        self.pDialog.move(pFrame.topLeft())