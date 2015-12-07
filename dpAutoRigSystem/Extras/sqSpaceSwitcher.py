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
        self.aFreeIndex = [] #List of free index (Can only happen when a item is removed) in the parent constraint

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
                #else: #If this is the only parent setuped, automaticly switch to it
                    #Do not switch in a non-reference scene to prevent problem with referenced object
                    #if pymel.referenceQuery(self.nDriven, isNodeReferenced=True):
                        #self.do_switch(0)

                pymel.select(nDriven)

    def _is_parent_exist(self, aNewParentList):
        """
        Look if a node is already a possible parent in the system
        """
        aExistTgt = self.nSwConst.getTargetList()

        for nParent in aNewParentList:
            if nParent in aExistTgt:
                return True

        return False

    def _get_adjusted_index(self, _iCurIndex):
        """
        Return the good index in the parent constraint to prevent any problem if
        one parent have been removed from it
        """
        if _iCurIndex in self.aFreeIndex:
            return self._get_adjusted_index(_iCurIndex+1)
        else:
            return _iCurIndex

        pass

    def add_target(self, aNewParent, firstSetup=False):
        """
        Add a new target to the space switch system
        """
        aExistTgt = self.nSwConst.getTargetList()

        for nParent in aNewParent:
            #Check if we need to use an free index that could exist after some target removing
            if len(self.aFreeIndex) != 0:
                iNewIdx = self.aFreeIndex[0]
                self.aFreeIndex.pop(0)
            else:
                iNewIdx = len(self.nSwConst.getWeightAliasList())

            #Ensure that the parent doesn't already exist in the drivers list
            if not nParent in aExistTgt:
                #First, calculate the offset between the parent and the driven node
                vTrans = self._get_tm_offset(nParent, type="t")
                vRot = self._get_tm_offset(nParent, type="r")

                #Connect the new target manually in the parent constraint
                if (iNewIdx == 0):
                    self.nSwConst.addAttr(nParent.name().replace("|", "_") + "W" +
                                          str(iNewIdx), at="double", min=0, max=1, dv=1, k=True, h=False)
                else:
                    self.nSwConst.addAttr(nParent.name().replace("|", "_") + "W" +
                                          str(iNewIdx), at="double", min=0, max=1, dv=0, k=True, h=False)

                pymel.connectAttr(nParent.parentMatrix, self.nSwConst.target[iNewIdx].targetParentMatrix)
                pymel.connectAttr(nParent.scale, self.nSwConst.target[iNewIdx].targetScale)
                pymel.connectAttr(nParent.rotateOrder, self.nSwConst.target[iNewIdx].targetRotateOrder)
                pymel.connectAttr(nParent.rotate, self.nSwConst.target[iNewIdx].targetRotate)
                pymel.connectAttr(nParent.rotatePivotTranslate, self.nSwConst.target[iNewIdx].targetRotateTranslate)
                pymel.connectAttr(nParent.rotatePivot, self.nSwConst.target[iNewIdx].targetRotatePivot)
                pymel.connectAttr(nParent.translate, self.nSwConst.target[iNewIdx].targetTranslate)
                #Link the created attributes to the weight value of the target
                nConstTgtWeight = pymel.Attribute(self.nSwConst.name() + "." + nParent.name().replace("|", "_") + "W"
                                                  + str(iNewIdx))
                pymel.connectAttr(nConstTgtWeight, self.nSwConst.target[iNewIdx].targetWeight)

                #Set the offset information
                self.nSwConst.target[iNewIdx].targetOffsetTranslate.targetOffsetTranslateX.set(vTrans[0])
                self.nSwConst.target[iNewIdx].targetOffsetTranslate.targetOffsetTranslateY.set(vTrans[1])
                self.nSwConst.target[iNewIdx].targetOffsetTranslate.targetOffsetTranslateZ.set(vTrans[2])
                self.nSwConst.target[iNewIdx].targetOffsetRotate.targetOffsetRotateX.set(vRot[0])
                self.nSwConst.target[iNewIdx].targetOffsetRotate.targetOffsetRotateY.set(vRot[1])
                self.nSwConst.target[iNewIdx].targetOffsetRotate.targetOffsetRotateZ.set(vRot[2])

                #Do not key an non-referenced object to prevent problem when referencing the scene
                if pymel.referenceQuery(self.nDriven, isNodeReferenced=True):
                    pymel.setKeyframe(nConstTgtWeight, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[iNewIdx].targetOffsetTranslate, t=0, ott="step")
                    pymel.setKeyframe(self.nSwConst.target[iNewIdx].targetOffsetRotate, t=0, ott="step")
                self.aDrivers.insert(iNewIdx, nParent)
                self.aDriversSubName.insert(iNewIdx, nParent.name())
            else:
                print("Warning: " + nParent.name() + " is already a driver for " + self.nDriven)

        #If this is the only parent and it is not referenced, do the switch right now on the frame the user is
        #if (len(aNewParent) == 1 and not firstSetup and pymel.referenceQuery(self.nDriven, isNodeReferenced=True)):
            #self.do_switch(iNbTgt - 1) #Since a new target have been added, iNbTgt equal the index to switch too

    def remove_target(self, iIdx, all=False):

        if all:
            #Remove the constraint and reset some variable
            pymel.delete(self.nSwConst)
            self.aDrivers = []
            self.aDriversSubName = []
            self.nDriven = None
            self.nSwConst = None #SpaceSwitch constraint for the system
            self.nSwConstRecept = None #Space Switch receiver
            self.aFreeIndex = [] #List of free index (Can only happen when a item is removed) in the parent constraint
        else:
            aExistTgt = self.nSwConst.getTargetList()
            iNbTgt = len(aExistTgt)

            #Before removing the target, we need to readjust the weight value and offset if needed
            aWeight = self.nSwConst.getWeightAliasList()

            if (iNbTgt > iIdx):
                #Get all the frames where the removed index is active
                if (iIdx == -1):
                    aKeyTime = pymel.keyframe(self.nSwConst.restTranslate.restTranslateX, q=True)
                else:
                    aKeyTime = pymel.keyframe(aWeight[iIdx], q=True)

                #Cut the keys of all weight at time where the removed target was active.
                for t in aKeyTime:
                    if aWeight[iIdx].get(time=t) == 1.0:
                        for w in aWeight:
                            try:
                                pymel.cutKey(w, time=t)
                            except:
                                pass

                #Remove the target
                pTgt = aExistTgt[iIdx]
                pymel.parentConstraint(pTgt, self.nSwConstRecept, e=True, rm=True)
                self.aFreeIndex.append(iIdx)
                self.aFreeIndex.sort()
                self.aDrivers.pop(iIdx)
                self.aDriversSubName.pop(iIdx)

                #Update all constraint when removing one
                self._update_constraint_keys()



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

    def _update_constraint_keys(self):
        """
        Update all key in the constraint to refresh the offset when needed and prevent any snap
        """
        aWeight = self.nSwConst.getWeightAliasList()
        fCurTime = pymel.currentTime()

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
                iAjustedIdx = self._get_adjusted_index(i)
                #Compute the offset between the parent and the driver
                vTrans = self._get_tm_offset(self.aDrivers[iAjustedIdx], type="t")
                vRot = self._get_tm_offset(self.aDrivers[iAjustedIdx], type="r")

                #Set the offset information
                self.nSwConst.target[iAjustedIdx].targetOffsetTranslate.targetOffsetTranslateX.set(vTrans[0])
                self.nSwConst.target[iAjustedIdx].targetOffsetTranslate.targetOffsetTranslateY.set(vTrans[1])
                self.nSwConst.target[iAjustedIdx].targetOffsetTranslate.targetOffsetTranslateZ.set(vTrans[2])
                self.nSwConst.target[iAjustedIdx].targetOffsetRotate.targetOffsetRotateX.set(vRot[0])
                self.nSwConst.target[iAjustedIdx].targetOffsetRotate.targetOffsetRotateY.set(vRot[1])
                self.nSwConst.target[iAjustedIdx].targetOffsetRotate.targetOffsetRotateZ.set(vRot[2])

                #Update keys
                pymel.setKeyframe(self.nSwConst.target[iAjustedIdx].targetOffsetTranslate, t=t, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iAjustedIdx].targetOffsetRotate, t=t, ott="step")
                pymel.keyTangent(self.nSwConst.target[iAjustedIdx].targetOffsetTranslate, t=t, ott="step") #Force step
                pymel.keyTangent(self.nSwConst.target[iAjustedIdx].targetOffsetRotate, t=t, ott="step") #Force step
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

    def do_switch(self, iIdx):
        """
        Switch the driver which will constraint the driven. Ensure that the switch is done without any snap
        of the driven object
        """
        fCurTime = pymel.currentTime()
        iActiveWeight = -1
        aWeight = self.nSwConst.getWeightAliasList()

        #If none is set to 1.0, the value will be -1 which represent the current parent
        for i, fValue in enumerate(aWeight):
            #Get the value at the frame before and do not update the offset if we return to same one
            if fValue.get(time=fCurTime-1) == 1.0:
                iActiveWeight = i
                break;

        if (iActiveWeight != iIdx): #Check is good, but we need to adjust the index after
            #Update the constraint information for the offset of the parent on which we will switch
            if (iIdx == -1):
                pymel.parentConstraint(self.nSwConst, mo=True, e=True)
                pymel.setKeyframe(self.nSwConst.restTranslate, t=fCurTime, ott="step")
                pymel.setKeyframe(self.nSwConst.restRotate, t=fCurTime, ott="step")
                pymel.keyTangent(self.nSwConst.restTranslate, t=fCurTime, ott="step") #Force step
                pymel.keyTangent(self.nSwConst.restRotate, t=fCurTime, ott="step") #Force step
            else:
                iAdjustedIdx = self._get_adjusted_index(iIdx)
                pymel.parentConstraint(self.aDrivers[iIdx], self.nSwConst, mo=True, e=True)
                pymel.setKeyframe(self.nSwConst.target[iAdjustedIdx].targetOffsetTranslate, t=fCurTime, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iAdjustedIdx].targetOffsetRotate, t=fCurTime, ott="step")
                pymel.keyTangent(self.nSwConst.target[iAdjustedIdx].targetOffsetTranslate, t=fCurTime, ott="step") #Force step
                pymel.keyTangent(self.nSwConst.target[iAdjustedIdx].targetOffsetRotate, t=fCurTime, ott="step") #Force step


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

        self._update_constraint_keys()


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
        self.ID_COL_FRAME = 0
        self.ID_COL_PARENT = 1
        self.sOriginalParent = "Original Parent"

        self.ui = spaceSwitcherUI.Ui_win_main()
        self.ui.setupUi(self)

        #Setup the base list of parent
        self.createModel = QtGui.QStandardItemModel(self.ui.lstParent)
        self.parentItem = QtGui.QStandardItem(self.sOriginalParent)
        self.parentItem.setCheckable(False)
        self.parentItem.setEditable(False)
        self.createModel.appendRow(self.parentItem)
        self.ui.lstParent.setModel(self.createModel)

        self.ui.btnAction.setEnabled(False)
        self.ui.btnAction.setText("Select a Node")
        self.ui.lstParent.setEnabled(False)

        #TODO - Fix header which don't want to change it's text value...
        '''
        aHeader = []
        aHeader.append(QtGui.QApplication.translate("win_main", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        aHeader.append(QtGui.QApplication.translate("win_main", "Parent", None, QtGui.QApplication.UnicodeUTF8))

        #Bypass header naming problem
        pHeaderFrame = QtGui.QTableWidgetItem()
        pHeaderFrame.setText(aHeader[0])
        self.ui.tblFrameInfo.setHorizontalHeaderItem(0, pHeaderFrame)
        pHeaderParent = QtGui.QTableWidgetItem()
        pHeaderParent.setText(aHeader[0])
        self.ui.tblFrameInfo.setHorizontalHeaderItem(1, pHeaderParent)
        self.ui.tblFrameInfo.setHorizontalHeaderLabels(aHeader)
        self.ui.tblFrameInfo.setColumnCount(2)
        '''

        #Intern variable
        self.iJobSelChange = 0
        self.iJobSceneOpen = 0
        self.iJobUndo = 0
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
        self.ui.btnAction.pressed.connect(self._action_btnAction_pressed)
        self.ui.lstParent.clicked.connect(self._action_lstParent_selection_changed)

        self.iJobSelChange = pymel.scriptJob(event=('SelectionChanged', self._selection_change),compressUndo=False)
        self.iJobSceneOpen = pymel.scriptJob(event=('SceneOpened', self._scene_opened),compressUndo=False)
        self.iJobUndo = pymel.scriptJob(event=('Undo', self._scene_undo),compressUndo=False)

    def _fetch_system_from_scene(self):
        """
        Get all SpaceSwitch system in the scene
        """
        lstNetworkNode = libSerialization.getNetworksByClass(SpaceSwitcherLogic.__name__)
        for pNet in lstNetworkNode:
            pData = libSerialization.import_network(pNet)
            self.aSceneSpaceSwitch.append(pData)

    def _set_mode_info(self, _mode, _bButtonEnabled):
        self.ui.lblStatus.setText("Current Node --> " + str(self.nSelDriven) + "")

        self.mode = _mode
        self.ui.btnAction.setEnabled(_bButtonEnabled)

        #Set the status label info depending of the current mode
        if _mode == Mode.Create:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("yellow",
                                                                                                 "(First Setup)"))
            self.ui.btnAction.setText("Setup")
        elif _mode == Mode.Add:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green",
                                                                                                 "(Add Parent)"))
            self.ui.btnAction.setText("Add")
        elif _mode == Mode.Switch or _mode == Mode.SwitchSelect:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("green",
                                                                                                 "(Switch Parent)"))
            self.ui.btnAction.setText("Switch")
        elif _mode == Mode.Remove:
            self.ui.lblStatus.setText(self.ui.lblStatus.text() + " " + self.colorTemplate.format("red",
                                                                                                 "(Remove Parent)"))
            self.ui.btnAction.setText("Remove")
        else:
            self.ui.btnAction.setText("Select a Node")

    def _selection_change(self, *args):
        """
        Manage the selection change to know which action the user want to do. The remove action
        need to be implemented another way
        """
        print "SEL CHANGED"
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

        self._set_mode_info(Mode.Inactive, False)
        self._update_info(None)

        if (self.nSelDriven != None):
            #Look for existing space switcher system
            self.pSelSpSys = None
            for pSp in self.aSceneSpaceSwitch:
                if (pSp.nDriven == self.nSelDriven):
                    self.pSelSpSys = pSp
                    break;
            self._update_info(self.pSelSpSys)

            if self.pSelSpSys == None:
                nDrivenParent = self.nSelDriven.getParent()
                if nDrivenParent == None and pymel.referenceQuery(self.nSelDriven, isNodeReferenced=True):
                    self._set_mode_info(Mode.Create, False)
                else:
                    #TODO - Check if the parent can possibly receive a constraint on it
                    self._set_mode_info(Mode.Create, True)
            else:
                if (self.aSelDrivers):
                    if not self.pSelSpSys._is_parent_exist(self.aSelDrivers): #If no selected parent already exist
                        self._set_mode_info(Mode.Add, True)
                    else:
                        if (len(self.aSelDrivers) == 1):
                            self._set_mode_info(Mode.SwitchSelect, True)
                        else:
                            self._set_mode_info(Mode.Add, True)
                else:
                    #If a parent is selected in the list, active the button to do the switch
                    pSel = self.ui.lstParent.selectedIndexes()
                    if (pSel):
                        self._set_mode_info(Mode.Switch, True)
                    else:
                        self._set_mode_info(Mode.SwitchSelect, True)

    def _scene_opened(self, *args):
        """
        Find all SpaceSwitcher system in the scene
        """
        self._fetch_system_from_scene()

    def _scene_undo(self, *args):
        """
        Ensure to refresh the UI on a undo in the scene
        """
        self._fetch_system_from_scene()
        if (self.pSelSpSys and pymel.selected()):
            self._update_info(self.pSelSpSys)
        else:
            self._update_info(None)

        print ("UNDO")

    def closeEvent(self, *args, **kwargs):
        """
        Try to kill the script job when the window is closed
        """
        try:
            if pymel.scriptJob(ex=self.iJobSelChange):
                pymel.scriptJob(kill=self.iJobSelChange, force=True)
            if pymel.scriptJob(ex=self.iJobSceneOpen):
                pymel.scriptJob(kill=self.iJobSceneOpen, force=True)
            if pymel.scriptJob(ex=self.iJobUndo):
                pymel.scriptJob(kill=self.iJobUndo, force=True)
        except:
            pass

    def _update_info(self, pSpData):
        """
        Small wrapper to update all needed info in the UI
        """
        self._update_lstParent(pSpData)
        self._update_tblFrameInfo(pSpData)

    def _update_lstParent(self, pSpData):
        """
        Update the parent list for the selected system
        """
        self.createModel.clear()
        if (pSpData):
            self.ui.lstParent.setEnabled(True)
            self.createModel.appendRow(self.parentItem)
            for iIdx, nParentInfo in enumerate(pSpData.aDrivers):
                newParentItem = QtGui.QStandardItem(pSpData.aDriversSubName[iIdx])
                newParentItem.setEditable(False)
                newParentItem.setCheckable(True)
                self.createModel.appendRow(newParentItem)
        else:
            self.ui.lstParent.setEnabled(False)
            self.createModel.appendRow(self.parentItem)

    def _update_tblFrameInfo(self, pSpData):
        """
        Update the frame/parent info with the selected system
        """

        #Clear the table info and refresh it
        self.ui.tblFrameInfo.clear()
        self.ui.tblFrameInfo.setRowCount(0)

        if (pSpData):
            aWeight = pSpData.nSwConst.getWeightAliasList()

            aZeroKey = [] #List of frame which have key at 0 on all parent
            aPreventZeroKey = [] #List of frame we know it's not all parent to 0
            aKeyParent = [] #List of tuple representing the frame with the parent index

            #Check to collect all constraint keys we would need to update
            for i,w in enumerate(aWeight):
                aKeyTime = pymel.keyframe(w, q=True)
                for iTime in aKeyTime:
                    if w.get(time=iTime) == 1.0: #Keep info about frame/parent
                        aKeyParent.append((iTime,i))
                        if iTime not in aPreventZeroKey:
                            aPreventZeroKey.append(iTime)
                    else:
                        if iTime not in aZeroKey:
                            aZeroKey.append(iTime) #Keep possible frame to be one without any parent active

            for iTime in aZeroKey:
                if iTime not in aPreventZeroKey:
                    aKeyParent.append((iTime, -1))

            #Sort by Frame order (Need to be reversed to be in the good frame order)
            aKeyParent.sort(reverse=True)

            #Create a list of the parent name to use in the combo box that will be created
            aParentName = [nParent.name() for nParent in pSpData.aDrivers]
            aParentName.insert(0, self.sOriginalParent)

            iNbRow = self.ui.tblFrameInfo.rowCount()
            for pTblInfo in aKeyParent:
                self.ui.tblFrameInfo.insertRow(iNbRow)

                #Frame Field
                pFrameCell = QtGui.QTableWidgetItem()
                self.ui.tblFrameInfo.setItem(iNbRow, self.ID_COL_FRAME, pFrameCell)
                edtFrame = QtGui.QLineEdit()
                edtFrame.setValidator(QtGui.QDoubleValidator(-1000.00, 1000.00, 0))
                edtFrame.setText(str(int(pTblInfo[0])))
                edtFrame.textChanged.connect(partial(self._action_edtFrame_changed, iNbRow))
                #Monkey patch the mouse event function to create a right click menu on it.
                #I could have redefined a class that inherit the QLineEdit class, but....
                #edtFrame.mousePressEvent = partial(self.mousePressEventEdt, iRow=iCurRowIdx, iCol = self.ID_COL_NAME)
                self.ui.tblFrameInfo.setCellWidget(iNbRow, self.ID_COL_FRAME, edtFrame)

                #Parent Field
                pCellParent = QtGui.QTableWidgetItem()
                self.ui.tblFrameInfo.setItem(iNbRow, self.ID_COL_PARENT, pCellParent)
                cbParent = QtGui.QComboBox()
                cbParent.addItems(aParentName)
                cbParent.setCurrentIndex(pTblInfo[1] + 1) #Index is always +1 since original parent it -1 in the system
                cbParent.currentIndexChanged.connect(partial(self._action_cbParent_indexChanged, iNbRow))
                self.ui.tblFrameInfo.setCellWidget(iNbRow, self.ID_COL_PARENT, cbParent)

    def _action_btnAction_pressed(self):
        """
        Manage the different action that can happen on the tool. Will change depending on the selection
        """
        if (self.mode == Mode.Create):
            if pymel.referenceQuery(self.nSelDriven, isNodeReferenced=True):
                bCreateParent = False
            else:
                if (self.nSelDriven.getParent() != None):
                    bCreateParent = False
                else:
                    bCreateParent = True

            with pymel.UndoChunk():
                pNewSp = SpaceSwitcherLogic()
                if self.aSelDrivers:
                    pNewSp.setup_space_switch(self.nSelDriven, self.aSelDrivers, bCreateWolrdNode=False, bCreateParent=bCreateParent)
                else: #There is no drivers, so the user want the world to be one of them
                    pNewSp.setup_space_switch(self.nSelDriven, self.aSelDrivers, bCreateWolrdNode=True, bCreateParent=bCreateParent)
                self._update_info(pNewSp)
                libSerialization.export_network(pNewSp)
                self.aSceneSpaceSwitch.append(pNewSp)

        elif (self.mode == Mode.Add):
            with pymel.UndoChunk():
                self.pSelSpSys.add_target(self.aSelDrivers)
                self._update_info(self.pSelSpSys)
                #Delete the old network before updating a new one
                aNetwork = libSerialization.getConnectedNetworks(self.pSelSpSys.nDriven, recursive=False)
                pymel.delete(aNetwork)
                libSerialization.export_network(self.pSelSpSys)

        elif (self.mode == Mode.Switch):
            pCurParent = self.ui.lstParent.selectedIndexes()[0]
            #Remove one to the index since the original parent doesn't really exist in the list of parent in the system
            with pymel.UndoChunk():
                self.pSelSpSys.do_switch(pCurParent.row() - 1)
                self._update_tblFrameInfo(self.pSelSpSys)

        elif (self.mode == Mode.SwitchSelect):
            #Find the selected parent index
            if len(self.aSelDrivers) == 0:
                iSwitchIdx = -1
            else:
                iSwitchIdx = 0
                for idx, nDriver in enumerate(self.pSelSpSys.aDrivers):
                    if nDriver == self.aSelDrivers[0]:
                        iSwitchIdx = idx
            with pymel.UndoChunk():
                self.pSelSpSys.do_switch(iSwitchIdx)
                self._update_tblFrameInfo(self.pSelSpSys)

        elif (self.mode == Mode.Remove):
            iNbTarget = len(self.pSelSpSys.aDrivers)
            self.toRemove.sort(reverse=True) #Ensure to remove from the bigger to the smaller index

            #Delete the network
            with pymel.UndoChunk():
                aNetwork = libSerialization.getConnectedNetworks(self.pSelSpSys.nDriven, recursive=False)
                pymel.delete(aNetwork)
                if (iNbTarget == len(self.toRemove)):
                    #Totally remove the constraint
                    self.pSelSpSys.remove_target(-1, all=True)
                    self.aSceneSpaceSwitch.remove(self.pSelSpSys)
                else:
                    for iIdx in self.toRemove:
                        self.pSelSpSys.remove_target(iIdx - 1)
                    #Recreate the network with refreshed data
                    libSerialization.export_network(self.pSelSpSys)

        pymel.select(self.nSelDriven)

        '''
        if (self.pSelSpSys and pymel.selected()):
            self._update_info(self.pSelSpSys)
        else:
            self._update_info(None)
        '''

    def _action_lstParent_selection_changed(self):
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
            self._set_mode_info(Mode.Remove, True)
        else:
            #Prevent a stuck status when unchecking all item
            self._set_mode_info(Mode.Switch, False)

        if (self.mode == Mode.Switch):
            pSel = self.ui.lstParent.selectedIndexes()
            if (pSel):
                self._set_mode_info(Mode.Switch, True)
            else:
                self._set_mode_info(Mode.Switch, False)

    def _action_edtFrame_changed(self, iRow):
        """
        Manage a frame change in the frame info table
        """
        pass

    def _action_cbParent_indexChanged(self, iRow):
        """
        Manage a parent change in the frame info table
        """
        pass

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