try:
    import math
    import maya.cmds as cmds
    import pymel.core as pymel
    import maya.OpenMaya as om
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
                self.worldNode.visibility.set(False)
                for pAttr in self.worldNode.listAttr(keyable=True):
                    pymel.setAttr(pAttr, keyable=False, lock=True)
                self.worldNode.hiddenInOutliner = True

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
                    self.nSwConstRecept = pymel.createNode("transform", ss=True)
                    mDriven = self.nDriven.getMatrix(worldSpace=True)
                    self.nSwConstRecept.setMatrix(mDriven, worldSpace=True)
                    self.nSwConstRecept.rename(self.nDriven.name() + "_SW_Const")
                    self.nDriven.setParent(self.nSwConstRecept)
                else:
                    self.nSwConstRecept = self.nDriven.getParent()

                #Create the parent constraint for the first node, but add the other target manually
                if (bCreateWolrdNode):
                    self.nSwConst = pymel.parentConstraint(self.worldNode, self.nSwConstRecept,
                                                           n=self.nDriven.name() + "_SpaceSwitch_Const", mo=True)
                else:
                    self.nSwConst = pymel.parentConstraint(aParent[0], self.nSwConstRecept,
                                                           n=self.nDriven.name() + "_SpaceSwitch_Const", mo=True)
                    self.aDrivers.append(aParent[0])
                    self.aDriversSubName.append(aParent[0].name())
                    #Remove the first parent setuped before
                    aParent = aParent[1:]

                self.nSwConst.getWeightAliasList()[0].set(0.0)

                #Setup the first key for the current activate constraint, targets offset and rest position
                if pymel.referenceQuery(self.nDriven, isNodeReferenced=True):
                    pymel.setKeyframe(self.nSwConst.getWeightAliasList()[0], t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[0].targetOffsetTranslate, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[0].targetOffsetRotate, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.restTranslate, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.restRotate, t=0, ott="step")

                if aParent:
                    self.add_target(aParent, firstSetup=True)
                else: #If this is the only parent setuped, automaticly switch to it
                    #Do not switch in a non-reference scene to prevent problem with referenced object
                    if pymel.referenceQuery(self.nDriven, isNodeReferenced=True):
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
                    self.nSwConst.addAttr(nParent.name().replace("|", "_") + "W" +
                                          str(iNbTgt), at="double", min=0, max=1, dv=1, k=True, h=False)
                else:
                    self.nSwConst.addAttr(nParent.name().replace("|", "_") + "W" +
                                          str(iNbTgt), at="double", min=0, max=1, dv=0, k=True, h=False)

                pymel.connectAttr(nParent.parentMatrix, self.nSwConst.target[iNbTgt].targetParentMatrix)
                pymel.connectAttr(nParent.scale, self.nSwConst.target[iNbTgt].targetScale)
                pymel.connectAttr(nParent.rotateOrder, self.nSwConst.target[iNbTgt].targetRotateOrder)
                pymel.connectAttr(nParent.rotate, self.nSwConst.target[iNbTgt].targetRotate)
                pymel.connectAttr(nParent.rotatePivotTranslate, self.nSwConst.target[iNbTgt].targetRotateTranslate)
                pymel.connectAttr(nParent.rotatePivot, self.nSwConst.target[iNbTgt].targetRotatePivot)
                pymel.connectAttr(nParent.translate, self.nSwConst.target[iNbTgt].targetTranslate)
                #Link the created attributes to the weight value of the target
                nConstTgtWeight = pymel.Attribute(self.nSwConst.name() + "." + nParent.name().replace("|", "_") + "W"
                                                  + str(iNbTgt))
                pymel.connectAttr(nConstTgtWeight, self.nSwConst.target[iNbTgt].targetWeight)

                #Set the offset information
                self.nSwConst.target[iNbTgt].targetOffsetTranslate.targetOffsetTranslateX.set(vTrans[0])
                self.nSwConst.target[iNbTgt].targetOffsetTranslate.targetOffsetTranslateY.set(vTrans[1])
                self.nSwConst.target[iNbTgt].targetOffsetTranslate.targetOffsetTranslateZ.set(vTrans[2])
                self.nSwConst.target[iNbTgt].targetOffsetRotate.targetOffsetRotateX.set(vRot[0])
                self.nSwConst.target[iNbTgt].targetOffsetRotate.targetOffsetRotateY.set(vRot[1])
                self.nSwConst.target[iNbTgt].targetOffsetRotate.targetOffsetRotateZ.set(vRot[2])

                #Do not key an non-referenced object to prevent problem when referencing the scene
                if pymel.referenceQuery(self.nDriven, isNodeReferenced=True):
                    pymel.setKeyframe(nConstTgtWeight, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetTranslate, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetRotate, t=0, ott="step")
                self.aDrivers.append(nParent)
                self.aDriversSubName.append(nParent.name())
                iNbTgt += 1
            else:
                print("Warning: " + nParent.name() + " is already a driver for " + self.nDriven)

        #If this is the only parent and it is not referenced, do the switch right now on the frame the user is
        if (len(aNewParent) == 1 and not firstSetup and pymel.referenceQuery(self.nDriven, isNodeReferenced=True)):
            self.do_switch(iNbTgt - 1) #Since a new target have been added, iNbTgt equal the index to switch too

    def remove_target(self, iIdx):
        aExistTgt = self.nSwConst.getTargetList()
        iNbTgt = len(aExistTgt)

        if (iNbTgt > iIdx):
            pTgt = aExistTgt[iIdx]
            pymel.parentConstraint(pTgt, self.nSwConstRecept, e=True, rm=True)
            self.aDrivers.pop(iIdx)
            self.aDriversSubName.pop(iIdx)

    def _get_tm_offset(self, nParent, iTime=pymel.currentTime(), type="t"):
        """
        Get the offset between the driven and a driver node
        """
        mStart = om.MMatrix()
        mEnd =  om.MMatrix()

        wmStart = nParent.worldMatrix.get().__melobject__()
        wmEnd = self.nSwConstRecept.worldMatrix.get().__melobject__()

        om.MScriptUtil().createMatrixFromList(wmStart,mStart)
        om.MScriptUtil().createMatrixFromList(wmEnd,mEnd)

        mOut = om.MTransformationMatrix(mEnd * mStart.inverse())

        if type == "t":
            #Extract Translation
            vTran = om.MVector(mOut.getTranslation(om.MSpace.kTransform))
            vTranPymel = [vTran.x,vTran.y,vTran.z]
            return vTranPymel
        if type == "r":
            #Extract Rotation
            ro = self.nSwConstRecept.rotateOrder.get()
            vRot = om.MEulerRotation(mOut.eulerRotation().reorder(ro))
            vRotDeg = [math.degrees(vRot.x), math.degrees(vRot.y), math.degrees(vRot.z)]
            return vRotDeg


    def do_switch(self, iIdx):
        """
        Switch the driver which will constraint the driven. Ensure that the switch is done without any snap
        of the driven object
        """
        fCurTime = pymel.currentTime()
        iActiveWeight = -1
        aWeight = self.nSwConst.getWeightAliasList()
        iNbTarget = len(aWeight)

        #If none is set to 1.0, the value will be -1 which represent the current parent
        for i, fValue in enumerate(aWeight):
            if fValue.get() == 1.0:
                iActiveWeight = i
                break;

        if (iNbTarget > iIdx):
            if (iActiveWeight != iIdx):
                #Update the constraint information for the offset of the parent on which we will switch
                if (iIdx == -1):
                    pymel.parentConstraint(self.nSwConst, mo=True, e=True)
                    pymel.setKeyframe(self.nSwConst.restTranslate, t=fCurTime, ott="step")
                    pymel.setKeyframe(self.nSwConst.restRotate, t=fCurTime, ott="step")
                    pymel.keyTangent(self.nSwConst.restTranslate, t=fCurTime, ott="step") #Force step
                    pymel.keyTangent(self.nSwConst.restRotate, t=fCurTime, ott="step") #Force step
                else:
                    pymel.parentConstraint(self.aDrivers[iIdx], self.nSwConst, mo=True, e=True)
                    pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetTranslate, t=fCurTime, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetRotate, t=fCurTime, ott="step")
                    pymel.keyTangent(self.nSwConst.target[iIdx].targetOffsetTranslate, t=fCurTime, ott="step") #Force step
                    pymel.keyTangent(self.nSwConst.target[iIdx].targetOffsetRotate, t=fCurTime, ott="step") #Force step


                if (iIdx == -1):
                    for wAlias in aWeight:
                        wAlias.set(0.0)
                else:
                    for i,wAlias in enumerate(aWeight):
                        if (i == iIdx):
                            wAlias.set(1.0)
                        else:
                            wAlias.set(0.0)
                #Set a keyframe on the weight to keep the animation
                pymel.setKeyframe(aWeight, t=fCurTime, ott="step")
                pymel.keyTangent(aWeight, ott="step") #Force step

                #List to stock information we need to update in the good frame order
                aKeyIndex = []

                #Check to collect the rest pos/rot key already created
                aKeyTime = pymel.keyframe(self.nSwConst.restTranslate.restTranslateX, q=True)
                for t in aKeyTime:
                    if (t > fCurTime):
                        aKeyIndex.append((t, -1))

                #Check to collect all constraint keys we would need to update
                for i,w in enumerate(aWeight):
                    aKeyTime = pymel.keyframe(w, q=True)
                    for t in aKeyTime:
                        if (t > fCurTime):
                            if w.get(time=t) == 1.0: #Only update the key if the constraint is active
                                aKeyIndex.append((t,i))

                #Sort the key index list of tuple to ensure we update the data in the good frame order
                aKeyIndex.sort()
                pymel.refresh(su=True)
                for t, i in aKeyIndex:
                    pymel.setCurrentTime(t-1)
                    if (i >= 0):
                        #Compute the offset between the parent and the driver
                        vTrans = self._get_tm_offset(self.aDrivers[i], type="t")
                        vRot = self._get_tm_offset(self.aDrivers[i], type="r")

                        #Set the offset information
                        self.nSwConst.target[i].targetOffsetTranslate.targetOffsetTranslateX.set(vTrans[0])
                        self.nSwConst.target[i].targetOffsetTranslate.targetOffsetTranslateY.set(vTrans[1])
                        self.nSwConst.target[i].targetOffsetTranslate.targetOffsetTranslateZ.set(vTrans[2])
                        self.nSwConst.target[i].targetOffsetRotate.targetOffsetRotateX.set(vRot[0])
                        self.nSwConst.target[i].targetOffsetRotate.targetOffsetRotateY.set(vRot[1])
                        self.nSwConst.target[i].targetOffsetRotate.targetOffsetRotateZ.set(vRot[2])

                        #Update keys
                        pymel.setKeyframe(self.nSwConst.target[i].targetOffsetTranslate, t=t, ott="step")
                        pymel.setKeyframe(self.nSwConst.target[i].targetOffsetRotate, t=t, ott="step")
                        pymel.keyTangent(self.nSwConst.target[i].targetOffsetTranslate, t=t, ott="step") #Force step
                        pymel.keyTangent(self.nSwConst.target[i].targetOffsetRotate, t=t, ott="step") #Force step
                    else:
                        #Get the offset information from the constraint trans and rot at the time before the key
                        vTrans = self.nSwConst.constraintTranslate.get()
                        vRot = self.nSwConst.constraintRotate.get()

                        #Set the offset information
                        self.nSwConst.restTranslate.set(vTrans)
                        self.nSwConst.restRotate.set(vRot)

                        #Update keys
                        pymel.setKeyframe(self.nSwConst.restTranslate, t=t, ott="step")
                        pymel.setKeyframe(self.nSwConst.restRotate, t=t, ott="step")
                        pymel.keyTangent(self.nSwConst.restTranslate, t=t, ott="step") #Force step
                        pymel.keyTangent(self.nSwConst.restRotate, t=t, ott="step") #Force step

                pymel.setCurrentTime(fCurTime)
                pymel.refresh(su=False)
                
        else:
            print "Cannot switch target, index is bigger than the number of target"


# src: http://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/Maya-SDK/files/
# GUID-3F96AF53-A47E-4351-A86A-396E7BFD6665-htm.html
def getMayaWindow():
    """
    Return the pointer to maya window
    """
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtGui.QWidget)


class Mode:
    Inactive = 0,
    Create = 1,
    Add = 2,
    Switch = 3,
    SwitchSelect = 4,
    Remove = 5

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
        self.iJobSceneOpen = 0
        self.mode = Mode.Inactive
        self.nSelDriven = None
        self.aSelDrivers = []
        self.pSelSpSys = None
        self.toRemove = []
        self.aSceneSpaceSwitch = []

        self.colorTemplate = "<font color={0}>{1}</font>"

        self._setup_callbacks()

        #Force the tool to check the selection on it's opening
        self._fetch_system_from_scene()
        self._selection_change()

    def _setup_callbacks(self):
        """
        Setup the  button callback and also a callback in maya to know when a selection is changed
        """
        self.ui.btnHelpParent.pressed.connect(self._action_show_parent_help)
        self.ui.btnAction.pressed.connect(self._action_execute)
        self.ui.lstParent.clicked.connect(self._action_lstChanged)
        self.ui.chkUseParent.clicked.connect(self._action_chkChanged)

        self.iJobNum = pymel.scriptJob(event=('SelectionChanged', self._selection_change),compressUndo=False)
        self.iJobSceneOpen = pymel.scriptJob(event=('SceneOpened', self._scene_opened),compressUndo=False)

    def _fetch_system_from_scene(self):
        """
        Get all SpaceSwitch system in the scene
        """
        lstNetworkNode = libSerialization.getNetworksByClass(SpaceSwitcherLogic.__name__)
        for pNet in lstNetworkNode:
            pData = libSerialization.import_network(pNet)
            self.aSceneSpaceSwitch.append(pData)

    def _set_mode_info(self, _mode, _bButtonEnabled, _sButtonText):
        self.ui.lblStatus.setText("Driven Node --> " + str(self.nSelDriven) + "")

        self.mode = _mode
        self.ui.btnAction.setEnabled(_bButtonEnabled)
        self.ui.btnAction.setText(_sButtonText)

        #Set the status label info depending of the current mode
        if _mode == Mode.Create:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("yellow",
                                                                                                 "(First Setup)"))
        elif _mode == Mode.Add:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green",
                                                                                                 "(Add Parent)"))
        elif _mode == Mode.Switch or _mode == Mode.SwitchSelect:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green",
                                                                                                 "(Switch Parent)"))
        elif _mode == Mode.Remove:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("red",
                                                                                                 "(Remove Parent)"))

    def _selection_change(self, *args):
        """
        Manage the selection change to know which action the user want to do. The remove action
        need to be implemented another way
        """
        aCurSel = pymel.selected()
        sInfoText = "Select a node"

        if (len(aCurSel) == 0):
            self.nSelDriven = None
            self.aSelDrivers = []
        elif (len(aCurSel) == 1):
            self.nSelDriven = aCurSel[0]
            self.aSelDrivers = []
        else:
            self.nSelDriven = aCurSel[-1]
            self.aSelDrivers = aCurSel[0:-1]

        self._set_mode_info(Mode.Inactive, False, sInfoText)
        self.ui.chkUseParent.setEnabled(True)
        self._update_parentList(None)

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
                nDrivenParent = self.nSelDriven.getParent()
                if nDrivenParent == None and self.ui.chkUseParent.isChecked():
                    sInfoText = "Cannot Setup Space Switch System because no parent is found or can be created"
                    self._set_mode_info(Mode.Create, False, sInfoText)
                else:
                    sInfoText = "Setup Space Switch System for" + self.nSelDriven.name()
                    self._set_mode_info(Mode.Create, True, sInfoText)
            else:
                if (self.aSelDrivers):
                    if not self.pSelSpSys._is_parent_exist(self.aSelDrivers): #If no selected parent already exist
                        sParentList = "("
                        for iIdx, pParent in enumerate(self.aSelDrivers):
                            sParentList += pParent.name()
                            if (iIdx != len(self.aSelDrivers) - 1):
                                sParentList += ","
                        sParentList += ")"
                        sInfoText = "Add " + sParentList +" as new parent"
                        self._set_mode_info(Mode.Add, True, sInfoText)
                    else:
                        if (len(self.aSelDrivers) == 1):
                            sInfoText = "Switch to " + self.aSelDrivers[0].name()
                            self._set_mode_info(Mode.SwitchSelect, True, sInfoText)
                        else:
                            sInfoText = "Too many parent selected to switch and can't add parent because " \
                                        "they are already in the system"
                            self._set_mode_info(Mode.Add, False, sInfoText)
                else:
                    #If a parent is selected in the list, active the button to do the switch
                    pSel = self.ui.lstParent.selectedIndexes()
                    if (pSel):
                        pSel = pSel[0]
                        sInfoText = "Switch Too " + pSel.data()
                        self._set_mode_info(Mode.Switch, True, sInfoText)
                    else:
                        sInfoText = "Switch Too original parent"
                        self._set_mode_info(Mode.SwitchSelect, True, sInfoText)

    def _scene_opened(self, *args):
        self._fetch_system_from_scene()

    def closeEvent(self, *args, **kwargs):
        """
        Try to kill the script job when the window is closed
        """
        try:
            if pymel.scriptJob(ex=self.iJobNum):
                pymel.scriptJob(kill=self.iJobNum, force=True)
            if pymel.scriptJob(ex=self.iJobSceneOpen):
                pymel.scriptJob(kill=self.iJobSceneOpen, force=True)
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
        if (self.mode == Mode.Create):
            if pymel.referenceQuery(self.nSelDriven, isNodeReferenced=True):
                bCreateParent = False
            else:
                bCreateParent = not self.ui.chkUseParent.isChecked()

            pNewSp = SpaceSwitcherLogic()
            if self.aSelDrivers:
                pNewSp.setup_space_switch(self.nSelDriven, self.aSelDrivers, bCreateWolrdNode=False, bCreateParent=bCreateParent)
            else: #There is no drivers, so the user want the world to be one of them
                pNewSp.setup_space_switch(self.nSelDriven, self.aSelDrivers, bCreateWolrdNode=True, bCreateParent=bCreateParent)
            self._update_parentList(pNewSp)
            pNewSp.pNetwork = libSerialization.export_network(pNewSp)
            self.aSceneSpaceSwitch.append(pNewSp)
            pymel.select(self.nSelDriven)

        elif (self.mode == Mode.Add):
            self.pSelSpSys.add_target(self.aSelDrivers)
            self._update_parentList(self.pSelSpSys)
            #Delete the old network before updating a new one
            if (self.pSelSpSys.pNetwork):
                pymel.delete(self.pSelSpSys.pNetwork)
                self.pSelSpSys.pNetwork = None
            self.pSelSpSys.pNetwork = libSerialization.export_network(self.pSelSpSys)
            pymel.select(self.nSelDriven)


        elif (self.mode == Mode.Switch):
            pCurParent = self.ui.lstParent.selectedIndexes()[0]
            #Remove one to the index since the original parent doesn't really exist in the list of parent in the system
            self.pSelSpSys.do_switch(pCurParent.row() - 1)

        elif (self.mode == Mode.SwitchSelect):
            #Find the selected parent index
            if len(self.aSelDrivers) == 0:
                iSwitchIdx = -1
            else:
                iSwitchIdx = 0
                for idx, nDriver in enumerate(self.pSelSpSys.aDrivers):
                    if nDriver == self.aSelDrivers[0]:
                        iSwitchIdx = idx
            self.pSelSpSys.do_switch(iSwitchIdx)

        elif (self.mode == Mode.Remove):
            self.toRemove.sort(reverse=True) #Ensure to remove from the bigger to the smaller index
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
                sInfoText = "Setup Space Switch System for" + self.nSelDriven.name()
                self._set_mode_info(Mode.Create, True, sInfoText)
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
            sInfoText = "Remove checked parent from the system"
            self._set_mode_info(Mode.Remove, True, sInfoText)
        else:
            #Prevent a stuck status when unchecking all item
            sInfoText = "Select a driver in the list and hit the button to switch to it"
            self._set_mode_info(Mode.Switch, False, sInfoText)

        if (self.mode == Mode.Switch):
            pSel = self.ui.lstParent.selectedIndexes()
            if (pSel):
                pSel = pSel[0]
                sInfoText = "Switch Too " + pSel.data()
                self._set_mode_info(Mode.Switch, True, sInfoText)
            else:
                sInfoText = "Select a driver in the list and hit the button to switch to it"
                self._set_mode_info(Mode.Switch, False, sInfoText)

    def _action_chkChanged(self, *args, **kwargs):
        """
        Ensure that when we create a new system, if the node have no parent, it's node possible to do it without
        the Use Direct Parent unchecked option
        """
        if (self.mode == Mode.Create):
            if self.nSelDriven:
                if self.ui.chkUseParent.isChecked():
                    if self.nSelDriven.getParent() == None:
                        sInfo = "Cannot Setup Space Switch System because no parent is found or can be created"
                        self._set_mode_info(Mode.Create, False, sInfo)
                    else:
                        sInfoText = "Setup Space Switch System for" + self.nSelDriven.name()
                        self._set_mode_info(Mode.Create, True, sInfoText)
                else:
                    sInfoText = "Setup Space Switch System for" + self.nSelDriven.name()
                    self._set_mode_info(Mode.Create, True, sInfoText)





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