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
    try:
        from sstk.libs.libQt import QtCore, QtGui
        from sstk.libs import libSerialization
    except:
        from PySide import QtCore, QtGui
        from ..Modules.Library import libSerialization
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
        self.aDrivers = []
        self.aDriversSubName = []
        self.nDriven = None
        self.nSwConst = None #SpaceSwitch constraint for the system
        self.nSwConstRecept = None #Space Switch receiver
        self.pNetwork = None

        #TODO - Find a better way to constraint the world...
        tempWorld = pymel.ls(self.WORLD_NODE_NAME)
        if tempWorld:
            self.worldNode = tempWorld[0]
        else:
            self.worldNode = None

    def setup_space_switch(self, nDriven=None, aDrivers=None, bCreateWolrdNode=False, bCreateParent=True):
            """
            Setup a new space switch system on the node
            """
            aCurSel = pymel.selected()
            if aDrivers == None:
                aParent = aCurSel[0:-1]
            else:
                aParent = aDrivers

            bContinue = False
            #Create the worldNode
            if (not self.worldNode and bCreateWolrdNode):
                self.worldNode = pymel.createNode("transform", n="dp_sp_worldNode")
                for pAttr in self.worldNode.listAttr(keyable=True):
                    pymel.setAttr(pAttr, keyable=False, lock=True)
                pymel.worldNode.hiddenInOutliner = True

            if (self.worldNode):
                self.aDrivers.append(self.worldNode)
                self.aDriversSubName.append("World")

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
                    self.aDriversSubName.append(aParent[0].name())
                    #Remove the first parent setuped before
                    aParent = aParent[1:]

                self.nSwConst.getWeightAliasList()[0].set(0.0)

                #Setup the first key for the current activate constraint, targets offset and rest position
                pymel.setKeyframe(self.nSwConst.getWeightAliasList()[0], t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[0].targetOffsetTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[0].targetOffsetRotate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.restTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.restRotate, t=0, ott="step")

                if aParent:
                    self.add_target(aParent, firstSetup=True)
                else: #If this is the only parent setuped, automaticly switch to it
                    self.do_switch(0)

                pymel.select(nDriven)

    def _is_parent_exist(self, aNewParentList):
        aExistTgt = self.nSwConst.getTargetList()

        for nParent in aNewParentList:
            if nParent in aExistTgt:
                return True

        return False

    def add_target(self, aNewParent, firstSetup=False):
        """
        Add a new target to the space switch system
        """
        iNbTgt = len(self.nSwConst.getWeightAliasList())
        aExistTgt = self.nSwConst.getTargetList()

        for nParent in aNewParent:
            #Ensure that the parent doesn't already exist in the drivers list
            if not nParent in aExistTgt:
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

                pymel.setKeyframe(nConstTgtWeight, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetRotate, t=0, ott="step")
                self.aDrivers.append(nParent)
                self.aDriversSubName.append(nParent.name())
                iNbTgt += 1
            else:
                print("Warning: " + nParent.name() + " is already a driver for " + self.nDriven)

        #If this is the only parent, do the switch right now on the frame the user is
        if (len(aNewParent) == 1):
            self.do_switch(iNbTgt - 1) #Since a new target have been added, iNbTgt equal the index to switch too

    def remove_target(self, iIdx):
        aExistTgt = self.nSwConst.getTargetList()
        iNbTgt = len(aExistTgt)

        if (iNbTgt > iIdx):
            pTgt = aExistTgt[iIdx]
            pymel.parentConstraint(pTgt, self.nSwConstRecept, e=True, rm=True)
            self.aDrivers.pop(iIdx)
            self.aDriversSubName.pop(iIdx)

    def _get_tm_offset(self, nParent, type="t"):
        """
        Get the offset between the driven and a driver node
        """
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
        """
        Switch the driver which will constraint the driven. Ensure that the switch is done without any snap
        of the driven object
        """
        fCurTime = pymel.currentTime()
        #Just try to update the offset of the parent constraint before the switch
        iActiveWeight = -1
        aWeight = self.nSwConst.getWeightAliasList()

        #If none is set to 1.0, the value will be -1 which represent the current parent
        for i, fValue in enumerate(aWeight):
            if fValue.get() == 1.0:
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
                #Update constraint offset of the next index in the constraint
                pymel.parentConstraint(self.aDrivers[iIdx], self.nSwConst, mo=True, e=True)
                #Key the offset to prevent offset problem when coming back to the same parent
                pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetTranslate, t=fCurTime, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetRotate, t=fCurTime, ott="step")

                if (iActiveWeight != -1):
                    #Also update the offset of the previous parent to prevent any snap
                    self.nSwConst.target[iActiveWeight].targetOffsetTranslate.set(self.nSwConst.constraintTranslate.get())
                    self.nSwConst.target[iActiveWeight].targetOffsetRotate.set(self.nSwConst.constraintRotate.get())
                    #pymel.parentConstraint(self.aDrivers[iActiveWeight], self.nSwConst, mo=True, e=True)
                    pymel.setKeyframe(self.nSwConst.target[iActiveWeight].targetOffsetTranslate, t=fCurTime, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[iActiveWeight].targetOffsetRotate, t=fCurTime, ott="step")
                else:
                    self.nSwConst.restRotate.set(self.nSwConst.constraintRotate.get())
                    self.nSwConst.restTranslate.set(self.nSwConst.constraintTranslate.get())
                    pymel.setKeyframe(self.nSwConst.restTranslate, t=fCurTime, ott="step")
                    pymel.setKeyframe(self.nSwConst.restRotate, t=fCurTime, ott="step")
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
    """
    Return the pointer to maya window
    """
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
        self.parentItem.setCheckable(False)
        self.parentItem.setEditable(False)
        self.createModel.appendRow(self.parentItem)
        self.ui.lstParent.setModel(self.createModel)

        self.ui.btnAction.setEnabled(False)
        self.ui.btnAction.setText("Select a Node")
        self.ui.lstParent.setEnabled(False)

        #Intern variable
        self.iJobNum = 0
        self.action = "#create" #Can be #create, #switch, #add
        self.nSelDriven = None
        self.aSelDrivers = []
        self.pSelSpSys = None
        self.toRemove = []
        self.aSceneSpaceSwitch = []

        self.colorTemplate = "<font color={0}>{1}</font>"

        self._setupCallbacks()

        #Force the tool to check the selection on it's opening
        self._fetch_system_from_scene()
        self._selectionChange()

    def _setupCallbacks(self):
        """
        Setup the  button callback and also a callback in maya to know when a selection is changed
        """
        self.ui.btnHelpParent.pressed.connect(self._action_show_parent_help)
        self.ui.btnAction.pressed.connect(self._action_execute)
        self.ui.lstParent.clicked.connect(self._action_lstChanged)

        self.iJobNum = pymel.scriptJob(event=('SelectionChanged', self._selectionChange),compressUndo=False)

    def _fetch_system_from_scene(self):
        """
        Get all SpaceSwitch system in the scene
        """
        lstNetworkNode = libSerialization.getNetworksByClass(SpaceSwitcherLogic.__name__)
        for pNet in lstNetworkNode:
            pData = libSerialization.import_network(pNet)
            self.aSceneSpaceSwitch.append(pData)

    def _selectionChange(self, *args):
        """
        Manage the selection change to know which action the user want to do. The remove action
        need to be implemented another way
        """
        aCurSel = pymel.selected()

        if (len(aCurSel) == 0):
            self.nSelDriven = None
            self.aSelDrivers = []
        elif (len(aCurSel) == 1):
            self.nSelDriven = aCurSel[0]
            self.aSelDrivers = []
        else:
            self.nSelDriven = aCurSel[-1]
            self.aSelDrivers = aCurSel[0:-1]

        self.ui.lblStatus.setText("Driven Node --> " + str(self.nSelDriven) + "")

        if (self.nSelDriven != None):
            if pymel.referenceQuery(self.nSelDriven, isNodeReferenced=True):
                self.ui.chkUseParent.setEnabled(False)
            else:
                self.ui.chkUseParent.setEnabled(True)
            #Look for existing space switcher system
            self.pSelSpSys = None
            for pSp in self.aSceneSpaceSwitch:
                if (pSp.nDriven == self.nSelDriven):
                    self.pSelSpSys = pSp
                    break;
            self._update_parentList(self.pSelSpSys)
            if self.pSelSpSys == None:
                self.action = "#create"
                self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("yellow", "(First Setup)"))
                self.ui.btnAction.setEnabled(True)
                self.ui.btnAction.setText("Setup Space Switch System for [" + self.nSelDriven.name() + "]")
            else:
                if (self.aSelDrivers):
                    self.action = "#add"
                    self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green", "(Add Parent)"))
                    if not self.pSelSpSys._is_parent_exist(self.aSelDrivers):
                        self.ui.btnAction.setEnabled(True)
                        sParentList = "("
                        for pParent in self.aSelDrivers:
                            sParentList += "[" + pParent.name() + "]"
                        sParentList += ")"
                        self.ui.btnAction.setText("Add " + sParentList +" as new parent")
                    else:
                        if (len(self.aSelDrivers) == 1):
                            self.action = "#switchSelect"
                            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green", "(Switch Parent)"))
                            self.ui.btnAction.setEnabled(True)
                            self.ui.btnAction.setText("Switch " + self.nSelDriven.name() + " to follow -->" + self.aSelDrivers[0].name())
                        else:
                            self.ui.btnAction.setEnabled(False)
                            self.ui.btnAction.setText("Too many parent selected to switch and can't add parent because they are already in the system")
                else:
                    #If a parent is selected in the list, active the button to do the switch
                    pSel = self.ui.lstParent.selectedIndexes()
                    self.action = "#switch"
                    self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green", "(Switch Parent)"))
                    self.ui.btnAction.setEnabled(False)
                    self.ui.btnAction.setText("Select a parent in the list to switch the parent")
                    if (pSel):
                        pSel = pSel[0]
                        self.ui.btnAction.setEnabled(True)
                        self.ui.btnAction.setText("Switch " + self.nSelDriven.name() + " to follow -->" + pSel.data())
        else:
            self.ui.btnAction.setEnabled(False)
            self.ui.chkUseParent.setEnabled(True)
            self.ui.btnAction.setText("Choose a node")
            self._update_parentList(None)

    def closeEvent(self, *args, **kwargs):
        """
        Try to kill the script job when the window is closed
        """
        try:
            pymel.scriptJob(kill=self.iJobNum, force=True)
        except:
            pass

    def _action_show_parent_help(self):
        """
        Show a small help window about the use direct parent option
        """
        sHelpMsg = "If checked, the direct parent of the driven node will be" \
                   " use as the recept of the parent constraint. Else, a new parent will be created. \n" \
                   "WARNING : New parent cannot be used on referenced node"
        pymel.informBox("Space Switcher", sHelpMsg)

    def _update_parentList(self, pSpData):
        """
        Update the parent list after some operation
        """
        if (pSpData):
            self.ui.lstParent.setEnabled(True)
            self.createModel.clear()
            self.createModel.appendRow(self.parentItem)
            for iIdx, nParentInfo in enumerate(pSpData.aDrivers):
                newParentItem = QtGui.QStandardItem(pSpData.aDriversSubName[iIdx])
                newParentItem.setEditable(False)
                newParentItem.setCheckable(True)
                self.createModel.appendRow(newParentItem)
        else:
            self.ui.lstParent.setEnabled(False)
            self.createModel.clear()
            self.createModel.appendRow(self.parentItem)

    def _action_execute(self):
        """
        Manage the different action that can happen on the tool. Will change depending on the selection
        """
        if (self.action == "#create"):
            if pymel.referenceQuery(self.nSelDriven, isNodeReferenced=True):
                bCreateParent = False
            else:
                bCreateParent = not self.ui.chkUseParent.isChecked()
            pNewSp = SpaceSwitcherLogic()
            with pymel.UndoChunk():
                if self.aSelDrivers:
                    pNewSp.setup_space_switch(self.nSelDriven, self.aSelDrivers, bCreateWolrdNode=False, bCreateParent=bCreateParent)
                else: #There is no drivers, so the user want the world to be one of them
                    pNewSp.setup_space_switch(self.nSelDriven, self.aSelDrivers, bCreateWolrdNode=True, bCreateParent=bCreateParent)
            self._update_parentList(pNewSp)
            pNewSp.pNetwork = libSerialization.export_network(pNewSp)
            self.aSceneSpaceSwitch.append(pNewSp)
            pymel.select(self.nSelDriven)

        elif (self.action == "#add"):
            self.pSelSpSys.add_target(self.aSelDrivers)
            self._update_parentList(self.pSelSpSys)
            #Delete the old network before updating a new one
            if (self.pSelSpSys.pNetwork):
                pymel.delete(self.pSelSpSys.pNetwork)
                self.pSelSpSys.pNetwork = None
            self.pSelSpSys.pNetwork = libSerialization.export_network(self.pSelSpSys)
            pymel.select(self.nSelDriven)

        elif (self.action == "#switch"):
            pCurParent = self.ui.lstParent.selectedIndexes()[0]
            #Remove one to the index since the original parent doesn't really exist in the list of parent in the system
            self.pSelSpSys.do_switch(pCurParent.row() - 1)

        elif (self.action == "#switchSelect"):
            #Find the selected parent index
            iSwitchIdx = 0
            for idx, nDriver in enumerate(self.pSelSpSys.aDrivers):
                if nDriver == self.aSelDrivers[0]:
                    iSwitchIdx = idx
            self.pSelSpSys.do_switch(iSwitchIdx)

        elif (self.action == "#remove"):
            for iIdx in self.toRemove:
                self.pSelSpSys.remove_target(iIdx - 1)

            #Check if it worth it to keep the system, if not, delete the network and parent constraint
            if not self.pSelSpSys.aDrivers:
                self.aSceneSpaceSwitch.remove(self.pSelSpSys)
                if (self.pSelSpSys.nSwConst):
                    pymel.delete(self.pSelSpSys.nSwConst)
                if (self.pSelSpSys.pNetwork):
                    pymel.delete(self.pSelSpSys.pNetwork)

                #Return to the create state action since the node is still selected, but everything is deleted
                self.action = "#create"
                self.ui.lblStatus.setText("Driven Node --> " + str(self.nSelDriven) + "")
                self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("yellow", "(First Setup)"))
                self.ui.btnAction.setEnabled(True)
                self.ui.btnAction.setText("Setup Space Switch System for [" + self.nSelDriven.name() + "]")
            else:
                if (self.pSelSpSys.pNetwork):
                    pymel.delete(self.pSelSpSys.pNetwork)
                    self.pSelSpSys.pNetwork = None
                self.pSelSpSys.pNetwork = libSerialization.export_network(self.pSelSpSys)
                pymel.select(self.nSelDriven)

            self._update_parentList(self.pSelSpSys)


    def _action_lstChanged(self):
        """
        Manage the parent list selection change
        """
        #First look if there is any checked out item
        self.toRemove = []
        for iIdx in xrange(self.createModel.rowCount()):
            pItem = self.createModel.item(iIdx)
            if (pItem.isCheckable()):
                if (pItem.checkState() == QtCore.Qt.Checked):
                    self.toRemove.append(iIdx)

        if (self.toRemove):
            self.action = "#remove"
            self.toRemove.sort(reverse=True)
            self.ui.btnAction.setEnabled(True)
            self.ui.lblStatus.setText("Driven Node --> " + str(self.nSelDriven) + "")
            self.ui.btnAction.setText("Remove checked parent from the system")
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("red", "(Remove Parent)"))
        else:
            #Prevent a stuck status when unchecking all item
            self.ui.btnAction.setEnabled(False)
            self.action = "#switch"

        if (self.action == "#switch"):
            pSel = self.ui.lstParent.selectedIndexes()
            if (pSel):
                pSel = pSel[0]
                self.ui.btnAction.setEnabled(True)
                self.ui.btnAction.setText("Switch " + self.nSelDriven.name() + " to follow --> " + pSel.data())
            else:
                self.ui.btnAction.setText("Select a parent in the list to switch the parent")





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