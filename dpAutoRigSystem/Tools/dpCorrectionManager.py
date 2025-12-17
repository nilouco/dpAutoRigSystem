# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from . import dpRivet
from ..Modules.Library import dpControls

# global variables to this module:    
CLASS_NAME = "CorrectionManager"
TITLE = "m068_correctionManager"
DESCRIPTION = "m069_correctionManagerDesc"
ICON = "/Icons/dp_correctionManager.png"
WIKI = "06-‐-Tools#-correction-manager"

ANGLE = "Angle"
DISTANCE = "Distance"

DP_CORRECTIONMANAGER_VERSION = 2.12


class CorrectionManager(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.ui = ui
        self.utils = dpUIinst.utils
        self.ctrls = dpControls.ControlClass(self.dpUIinst)
        self.correctionManagerName = self.dpUIinst.lang['m068_correctionManager']
        self.angleName = ANGLE
        self.distanceName = DISTANCE
        self.netSuffix = "Net"
        self.correctionManagerDataGrp = "CorrectionManager_Data_Grp"
        self.netList = []
        self.net = None
        # call main UI function
        if self.ui:
            self.closeUI()
            self.mainUI()
            self.refreshUI()
            

    def refreshUI(self, *args):
        """ Just call populate UI and actualize layout methodes.
        """
        self.populateNetUI()
        self.actualizeEditLayout()

        
    def closeUI(self, *args):
        """ Delete existing CorrectionManager window if it exists.
        """
        if cmds.window('dpCorrectionManagerWindow', query=True, exists=True):
            cmds.deleteUI('dpCorrectionManagerWindow', window=True)


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
            This is based in the old dpPoseReader, now without PyMEL or Qt.
        """
        # window
        correctionManager_winWidth  = 380
        correctionManager_winHeight = 300
        cmds.window('dpCorrectionManagerWindow', title=self.correctionManagerName+" "+str(DP_CORRECTIONMANAGER_VERSION), widthHeight=(correctionManager_winWidth, correctionManager_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpCorrectionManagerWindow')
        # create UI layout and elements:
        correctionManagerLayout = cmds.columnLayout('correctionManagerLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text("infoTxt", label=self.dpUIinst.lang['m066_selectTwo'], align="left", height=30, font='boldLabelFont', parent=correctionManagerLayout)
        correctionManagerLayoutA = cmds.rowColumnLayout('correctionManagerLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=correctionManagerLayout)
        self.createBT = cmds.button('createBT', label=self.dpUIinst.lang['i158_create'], command=partial(self.createCorrectionManager, fromUI=True), backgroundColor=(0.7, 1.0, 0.7), parent=correctionManagerLayoutA)
        self.createTF = cmds.textField('createTF', editable=True, parent=correctionManagerLayoutA)
        cmds.separator(style='none', height=10, width=100, parent=correctionManagerLayout)
        refreshLayout = cmds.rowColumnLayout('refreshLayoutA', numberOfColumns=4, columnWidth=[(1, 50), (2, 150), (2, 100), (3, 80)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'center'), (4, 'left')], columnAttach=[(1, 'both', 10), (2, 'left', 0), (3, 'left', 10), (4, 'left', 90)], parent=correctionManagerLayout)
        cmds.text(self.dpUIinst.lang['i138_type'], parent=refreshLayout)
        radioLayout = cmds.columnLayout("radioLayout", parent=refreshLayout)
        self.correctTypeCollection = cmds.radioCollection("correctTypeCollection", parent=radioLayout)
        typeAngle = cmds.radioButton(label=self.dpUIinst.lang['c102_angle'].capitalize(), annotation=self.angleName, collection=self.correctTypeCollection)
        cmds.radioButton(label=self.dpUIinst.lang['m182_distance'], annotation=self.distanceName, collection=self.correctTypeCollection)
        cmds.radioCollection(self.correctTypeCollection, edit=True, select=typeAngle)
        self.rivetCB = cmds.checkBox('rivetCB', label="Rivet", parent=refreshLayout)
        cmds.refreshBT = cmds.button('refreshBT', label=self.dpUIinst.lang['m181_refresh'], command=self.refreshUI, parent=refreshLayout)
        cmds.separator(style='in', height=15, width=100, parent=correctionManagerLayout)
        # existing:
        cmds.text("existingTxt", label=self.dpUIinst.lang['m071_existing'], align="left", height=25, font='boldLabelFont', parent=correctionManagerLayout)
        self.filterNameTF = cmds.textField('filterNameTF', width=30, changeCommand=self.populateNetUI, parent=correctionManagerLayout)
        cmds.separator(style='none', height=10, width=100, parent=correctionManagerLayout)
        self.existingNetTSL = cmds.textScrollList('existingNetTSL', width=20, allowMultiSelection=False, selectCommand=self.actualizeEditLayout, parent=correctionManagerLayout)
        cmds.separator(style='none', height=10, width=100, parent=correctionManagerLayout)
        # edit selected net layout:
        self.editSelectedNetLayout = cmds.frameLayout('editSelectedNetLayout', label=self.dpUIinst.lang['i011_editSelected'], collapsable=True, collapse=False, parent=correctionManagerLayout)


    def renameLinkedNodes(self, oldName, name, *args):
        """ List all connected nodes by message into the network and rename them using given parameters.
        """
        messageAttrList = []
        attrList = cmds.listAttr(self.net)
        for attr in attrList:
            if cmds.getAttr(self.net+"."+attr, type=True) == "message":
                messageAttrList.append(attr)
        if messageAttrList:
            for messageAttr in messageAttrList:
                connectedNodeList = cmds.listConnections(self.net+"."+messageAttr)
                if connectedNodeList:
                    childrenList = cmds.listRelatives(connectedNodeList[0], children=True, allDescendents=True)
                    cmds.rename(connectedNodeList[0], connectedNodeList[0].replace(oldName, name))
                    self.dpUIinst.customAttr.updateID([connectedNodeList[0].replace(oldName, name)])
                    if childrenList:
                        for children in childrenList:
                            try:
                                cmds.rename(children, children.replace(oldName, name))
                                self.dpUIinst.customAttr.updateID([children.replace(oldName, name)])
                            except:
                                pass


    def getDistance(self, *args):
        """ Returns the distance value read from the distance between node.
        """
        if cmds.getAttr(self.net+".type") == self.distanceName:
            distBet = cmds.listConnections(self.net+".distanceBet")[0]
            if distBet:
                return cmds.getAttr(distBet+".distance")


    def readDistance(self, *args):
        """ Update the UI text field with the current distance.
        """
        if cmds.getAttr(self.net+".type") == self.distanceName:
            currentDist = self.getDistance()
            cmds.textFieldButtonGrp("distanceTFBG", edit=True, text=str(round(currentDist, 4)))


    def changeName(self, name=None, *args):
        """ Edit name of the current network node selected.
            If there isn't any given name, it will try to get from the UI.
            Returns the name result.
        """
        oldName = cmds.getAttr(self.net+".name")
        if not name:
            if self.ui:
                name = cmds.textFieldGrp(self.nameTFG, query=True, text=True)
        if name:
            name = self.utils.resolveName(name, self.netSuffix)[0]
            self.renameLinkedNodes(oldName, name)
            cmds.setAttr(self.net+".name", name, type="string")
            self.net = cmds.rename(self.net, self.net.replace(oldName, name))
            if self.ui:
                self.populateNetUI()
                #self.actualizeEditLayout() #Bug: if we call this method here it will crash Maya! Error report: 322305477
                cmds.textFieldGrp(self.nameTFG, label=self.dpUIinst.lang['m006_name'], edit=True, text=name)
        return name


    def changeAxis(self, axis=None, *args):
        """ Update the setup to read the correct axis to extract angle or decompose distance vector.
        """
        cmds.setAttr(self.net+".axis", self.axisMenuItemList.index(axis.upper()))
        
        
    def changeAxisOrder(self, axisOrder=None, *args):
        """ Update the setup to set the correct axis order to extract angle.
        """
        if cmds.getAttr(self.net+".type") == self.angleName:
            cmds.setAttr(self.net+".axisOrder", self.axisOrderMenuItemList.index(axisOrder.upper()))


    def changeInputValues(self, minValue=None, maxValue=None, *args):
        """ Update the setup to set the choose input min and max values.
            That means we can read the angle or distance in this given range.
        """
        cmds.setAttr(self.net+".inputStart", minValue)
        cmds.setAttr(self.net+".inputEnd", maxValue)


    def changeOutputValues(self, minValue=None, maxValue=None, *args):
        """ Update the setup to set the choose output min and max values.
            That means we can output the final value in this given range.
        """
        cmds.setAttr(self.net+".outputStart", minValue)
        cmds.setAttr(self.net+".outputEnd", maxValue)


    def changeDecompose(self, value=None, *args):
        """ Update the decompose boolean attribute using the value comming from the UI checkBox.
        """
        cmds.setAttr(self.net+".decompose", value)
        cmds.optionMenu(self.axisMenu, edit=True, enable=value)


    def changeInterpolation(self, interp=None, *args):
        """ Just set the interpolation method of the remapValue to this given argument.
        """
        if interp == "Linear":
            cmds.setAttr(self.net+".interpolation", 0)
        elif interp == "Smooth":
            cmds.setAttr(self.net+".interpolation", 1)
        else: #Spline
            cmds.setAttr(self.net+".interpolation", 2)


    def deleteSetup(self, *args):
        """ Just delete these nodes to clear this current system setup:
            - Rivets if exists
            - Rivet_Grp if exists and empty
            - Correction Data Group
            - Network Data Node
            - Correction Manager Data Group if empty
        """
        netAttrList = cmds.listAttr(self.net)
        if netAttrList:
            for netAttr in netAttrList:
                if "Rivet" in netAttr:
                    try:
                        cmds.delete(self.utils.getNodeByMessage(netAttr, self.net))
                    except:
                        pass
        if cmds.objExists("Rivet_Grp"):
            if not cmds.listRelatives("Rivet_Grp", allDescendents=True, children=True):
                cmds.delete("Rivet_Grp")
        try:
            cmds.delete(self.utils.getNodeByMessage("correctionDataGrp", self.net))
        except:
            pass
        cmds.delete(self.net)
        if cmds.objExists(self.correctionManagerDataGrp):
            if not cmds.listRelatives(self.correctionManagerDataGrp, allDescendents=True, children=True):
                try:
                    cmds.delete(self.correctionManagerDataGrp)
                except:
                    pass
        if self.ui:
            self.populateNetUI()
            self.actualizeEditLayout()


    def recreateSelectedLayout(self, node=None, *args):
        """ It will recreate the edit layout for the selected network node.
        """
        if self.net:
            if cmds.objExists(self.net):
                # name:
                self.selectedLayout = cmds.columnLayout('selectedLayout', adjustableColumn=True, parent=self.editSelectedNetLayout)
                self.nameLayout = cmds.rowLayout('nameLayout', numberOfColumns=2, columnWidth2=(220, 50), columnAlign=[(1, 'left'), (2, 'right')], adjustableColumn=1, columnAttach=[(1, 'right', 50), (2, 'right', 2)], height=30, parent=self.selectedLayout)
                currentName = cmds.getAttr(self.net+".name")
                self.nameTFG = cmds.textFieldGrp("nameTFG", label=self.dpUIinst.lang['m006_name'], text=currentName, editable=True, columnWidth2=(40, 180), columnAttach=[(1, 'right', 2), (2, 'left', 2)], adjustableColumn2=2, changeCommand=self.changeName, parent=self.nameLayout)
                self.delete_BT = cmds.button('delete_BT', label=self.dpUIinst.lang['m005_delete'], command=self.deleteSetup, backgroundColor=(1.0, 0.7, 0.7), parent=self.nameLayout)
                # type:
                self.typeLayout = cmds.rowLayout('typeLayout', numberOfColumns=2, columnWidth2=(220, 50), columnAlign=[(1, 'left'), (2, 'right')], adjustableColumn=1, columnAttach=[(1, 'right', 50), (2, 'right', 2)], height=30, parent=self.selectedLayout)
                currentType = cmds.getAttr(self.net+".type")
                self.typeTFG = cmds.textFieldGrp("typeTFG", label=self.dpUIinst.lang['i138_type'], text=currentType, editable=False, columnWidth2=(40, 100), columnAttach=[(1, 'right', 2), (2, 'left', 2)], adjustableColumn2=2, changeCommand=self.changeName, parent=self.typeLayout)
                # axis:
                self.axisLayout = cmds.rowLayout('axisLayout', numberOfColumns=5, columnWidth5=(85, 80, 80, 50, 10), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right'), (4, 'left'), (5, 'left')], adjustableColumn=5, columnAttach=[(1, 'right', 2), (2, 'right', 2), (3, 'right', 2), (4, 'left', 2), (5, 'left', 10)], height=30, parent=self.selectedLayout)
                if cmds.getAttr(self.net+".type") == self.distanceName:
                    self.decomposeCB = cmds.checkBox("decomposeCB", label=self.dpUIinst.lang['m185_decompose'], value=cmds.getAttr(self.net+".decompose"), changeCommand=self.changeDecompose, parent=self.axisLayout)
                self.axisMenu = cmds.optionMenu("axisMenu", label=self.dpUIinst.lang['i052_axis'], changeCommand=self.changeAxis, parent=self.axisLayout)
                self.axisMenuItemList = ['X', 'Y', 'Z']
                for axis in self.axisMenuItemList:
                    cmds.menuItem(label=axis, parent=self.axisMenu)
                currentAxis = cmds.getAttr(self.net+".axis")
                cmds.optionMenu(self.axisMenu, edit=True, value=self.axisMenuItemList[currentAxis])
                if cmds.getAttr(self.net+".type") == self.angleName:
                    # axis order:
                    cmds.text("axisOrderTxt", label=self.dpUIinst.lang['i052_axis']+" "+self.dpUIinst.lang['m045_order'], parent=self.axisLayout)
                    self.axisOrderMenu = cmds.optionMenu("axisOrderMenu", label='', changeCommand=self.changeAxisOrder, parent=self.axisLayout)
                    self.axisOrderMenuItemList = ['XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX']
                    for axisOrder in self.axisOrderMenuItemList:
                        cmds.menuItem(label=axisOrder, parent=self.axisOrderMenu)
                    currentAxisOrder = cmds.getAttr(self.net+".axisOrder")
                    cmds.optionMenu(self.axisOrderMenu, edit=True, value=self.axisOrderMenuItemList[currentAxisOrder])
                else: #Distance
                    self.distanceLayout = cmds.columnLayout('distanceLayout', adjustableColumn=True, height=30, parent=self.selectedLayout)
                    currentDistance = self.getDistance()
                    self.distanceTFBG = cmds.textFieldButtonGrp("distanceTFBG", label=self.dpUIinst.lang['m182_distance'], text=str(round(currentDistance, 4)), buttonLabel=self.dpUIinst.lang['m183_readValue'], buttonCommand=self.readDistance, columnAlign=[(1, "left"), (2, "left"), (3, "left")], columnWidth=[(1, 50), (2, 60), (3, 80)], parent=self.distanceLayout)
                    if not cmds.getAttr(self.net+".decompose"):
                        cmds.optionMenu(self.axisMenu, edit=True, enable=False)
                # input and output values:
                currentInputStart = cmds.getAttr(self.net+".inputStart")
                currentInputEnd = cmds.getAttr(self.net+".inputEnd")
                currentOutputStart = cmds.getAttr(self.net+".outputStart")
                currentOutputEnd = cmds.getAttr(self.net+".outputEnd")
                # interpolation:
                self.interpolationLayout = cmds.columnLayout('interpolationLayout', adjustableColumn=False, columnAlign="left", parent=self.selectedLayout)
                self.interpMenu = cmds.optionMenu("interpMenu", label=self.dpUIinst.lang['m210_interpolation'], changeCommand=self.changeInterpolation, parent=self.interpolationLayout)
                self.interpMenuItemList = ['Linear', 'Smooth', 'Spline']
                for interp in self.interpMenuItemList:
                    cmds.menuItem(label=interp, parent=self.interpMenu)
                currentInterp = cmds.getAttr(self.net+".interpolation")
                cmds.optionMenu(self.interpMenu, edit=True, value=self.interpMenuItemList[currentInterp])
                # range:
                rangeLayout = cmds.columnLayout('rangeLayout', adjustableColumn=True, columnAlign="right", parent=self.selectedLayout)
                rangeLabelLayout = cmds.rowLayout('rangeLabelLayout', numberOfColumns=3, adjustableColumn=1, columnWidth=[(1, 10), (2, 58), (3, 80)], columnAttach=[(1, "right", 0), (2, "right", 20), (3, "right", 30)], parent=rangeLayout)
                cmds.text("rangeTxt", label=self.dpUIinst.lang['m072_range'], align="right", parent=rangeLabelLayout)
                cmds.text("startTxt", label=self.dpUIinst.lang['c110_start'], align="right", parent=rangeLabelLayout)
                cmds.text("endTxt", label=self.dpUIinst.lang['m184_end'], align="right", parent=rangeLabelLayout)
                cmds.floatFieldGrp("inputFFG", label=self.dpUIinst.lang['m137_input'], numberOfFields=2, value1=currentInputStart, value2=currentInputEnd, columnWidth3=(40, 70, 70), columnAttach=[(1, 'right', 5), (2, 'left', 2), (3, 'left', 0)], adjustableColumn3=1, changeCommand=self.changeInputValues, parent=rangeLayout)
                cmds.floatFieldGrp("outputFFG", label=self.dpUIinst.lang['m138_output'], numberOfFields=2, value1=currentOutputStart, value2=currentOutputEnd, columnWidth3=(40, 70, 70), columnAttach=[(1, 'right', 5), (2, 'left', 2), (3, 'left', 0)], adjustableColumn3=1, changeCommand=self.changeOutputValues, parent=rangeLayout)

    
    def actualizeEditLayout(self, *args):
        """ Clean up the current edit layout, check the selected node and update the UI.
        """
        self.clearEditLayout()
        selList = cmds.textScrollList(self.existingNetTSL, query=True, selectItem=True)
        if selList:
            if cmds.objExists(selList[0]):
                cmds.select(selList[0])
                self.net = selList[0]
        self.recreateSelectedLayout()


    def populateNetUI(self, *args):
        """ Check existing network node to populate UI.
        """
        cmds.textScrollList(self.existingNetTSL, edit=True, deselectAll=True)
        cmds.textScrollList(self.existingNetTSL, edit=True, removeAll=True)
        currentNetList = cmds.ls(selection=False, type="network")
        if currentNetList:
            self.netList = []
            filterName = cmds.textField(self.filterNameTF, query=True, text=True)
            if filterName:
                self.net = None
                self.clearEditLayout()
                currentNetList = self.utils.filterName(filterName, currentNetList, " ")
            for item in currentNetList:
                if cmds.objExists(item+".dpNetwork"):
                    if cmds.getAttr(item+".dpNetwork") == 1:
                        if cmds.objExists(item+".dpCorrectionManager"):
                            if cmds.getAttr(item+".dpCorrectionManager") == 1:
                                #TODO validate correctionManager node integrity here
                                self.netList.append(item)
            if self.netList:
                cmds.textScrollList(self.existingNetTSL, edit=True, append=self.netList)
                if self.net:
                    if cmds.objExists(self.net):
                        cmds.textScrollList(self.existingNetTSL, edit=True, selectItem=self.net)


    def clearEditLayout(self, *args):
        """ Just clean up the selected layout.
        """
        try:
            cmds.deleteUI(self.selectedLayout)
        except:
            pass


    def createCorrectiveLocator(self, name, toAttach, toRivet=False, *args):
        """ Creates a space locator, zeroOut it to receive a parentConstraint.
            Return the locator to use it as a reader node to the system.
        """
        if cmds.objExists(toAttach):
            loc = cmds.spaceLocator(name=name+"_Loc")[0]
            cmds.addAttr(loc, longName="inputNode", attributeType="message")
            cmds.connectAttr(toAttach+".message", loc+".inputNode", force=True)
            grp = self.utils.zeroOut([loc])[0]
            if toRivet:
                rivetNode = self.dpRivetInst.dpCreateRivet(toAttach, "AnyUVSet", [grp], True, False, False, False, False, False, False, useOffset=False)[-1]
                cmds.addAttr(self.net, longName=toAttach+"_Rivet", attributeType="message")
                cmds.connectAttr(rivetNode+".message", self.net+"."+toAttach+"_Rivet", force=True)
            else:
                cmds.parentConstraint(toAttach, grp, maintainOffset=False, name=grp+"_PaC")
                cmds.scaleConstraint(toAttach, grp, maintainOffset=True, name=grp+"_ScC")
            cmds.parent(grp, self.utils.getNodeByMessage("correctionDataGrp", self.net))
            return loc
        else:
            mel.eval('warning \"'+toAttach+' '+self.dpUIinst.lang['i061_notExists']+'\";')


    def createCorrectionManager(self, nodeList=None, name=None, correctType=None, toRivet=False, fromUI=False, *args):
        """ Create nodes to calculate the correction we want to mapper fix.
            Returns the created network node.
        """
        # loading Maya matrix node
        loadedQuatNode = self.utils.checkLoadedPlugin("quatNodes", self.dpUIinst.lang['e014_cantLoadQuatNode'])
        loadedMatrixPlugin = self.utils.checkLoadedPlugin("matrixNodes", self.dpUIinst.lang['e002_matrixPluginNotFound'])
        if loadedQuatNode and loadedMatrixPlugin:
            if not nodeList:
                nodeList = cmds.ls(selection=True, flatten=True)
            if nodeList:
                if len(nodeList) == 2:
                    self.toIDList = []
                    origNode = nodeList[0]
                    actionNode = nodeList[1]
                    cmds.undoInfo(openChunk=True)
                    
                    # main group
                    if not cmds.objExists(self.correctionManagerDataGrp):
                        self.correctionManagerDataGrp = cmds.group(empty=True, name=self.correctionManagerDataGrp)
                        cmds.addAttr(self.correctionManagerDataGrp, longName="dpCorrectionManagerDataGrp", attributeType="bool")
                        cmds.setAttr(self.correctionManagerDataGrp+".dpCorrectionManagerDataGrp", 1)
                        self.ctrls.setLockHide([self.correctionManagerDataGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        scalableGrp = self.utils.getNodeByMessage("scalableGrp")
                        if scalableGrp:
                            cmds.parent(self.correctionManagerDataGrp, scalableGrp)
                        cmds.setAttr(self.correctionManagerDataGrp+".visibility", 0)

                    # naming
                    if not name:
                        name = cmds.textField(self.createTF, query=True, text=True)
                        if not name:
                            name = "Correction"
                    correctionName, name = self.utils.resolveName(name, self.netSuffix)
                    
                    # type
                    if not correctType:
                        typeSelectedRadioButton = cmds.radioCollection(self.correctTypeCollection, query=True, select=True)
                        correctType = cmds.radioButton(typeSelectedRadioButton, query=True, annotation=True)
                        if not correctType:
                            correctType = self.angleName

                    # rivet
                    if fromUI:
                        toRivet = cmds.checkBox(self.rivetCB, query=True, value=True)
                    if toRivet:
                        self.dpRivetInst = dpRivet.Rivet(self.dpUIinst, False)

                    # create the container of the system data using a network node
                    self.net = cmds.createNode("network", name=name)
                    cmds.addAttr(self.net, longName="dpNetwork", attributeType="bool")
                    cmds.addAttr(self.net, longName="dpCorrectionManager", attributeType="bool")
                    cmds.addAttr(self.net, longName="name", dataType="string")
                    cmds.addAttr(self.net, longName="type", dataType="string")
                    cmds.addAttr(self.net, longName="inputValue", attributeType="float")
                    cmds.addAttr(self.net, longName="interpolation", attributeType='enum', enumName="Linear:Smooth:Spline")
                    cmds.addAttr(self.net, longName="decompose", attributeType="bool", defaultValue=0)
                    cmds.addAttr(self.net, longName="axis", attributeType='enum', enumName="X:Y:Z")
                    cmds.addAttr(self.net, longName="axisOrder", attributeType='enum', enumName="XYZ:YZX:ZXY:XZY:YXZ:ZYX")
                    cmds.addAttr(self.net, longName="inputStart", attributeType="float", defaultValue=0)
                    cmds.addAttr(self.net, longName="inputEnd", attributeType="float", defaultValue=90)
                    cmds.addAttr(self.net, longName="outputStart", attributeType="float", defaultValue=0)
                    cmds.addAttr(self.net, longName="outputEnd", attributeType="float", defaultValue=1)
                    # add serialization attributes
                    messageAttrList = ["correctionDataGrp", "originalLoc", "actionLoc", "correctiveMD", "extractAngleMM", "extractAngleDM", "extractAngleQtE", "extractAngleMD", "angleAxisChc", "smallerThanOneCnd", "overZeroCnd", "interpolationPMA", "inputRmV", "outputSR"]
                    if correctType == self.distanceName:
                        messageAttrList = ["correctionDataGrp", "originalLoc", "actionLoc", "correctiveMD", "outputRmV", "distanceBet", "distanceAllCnd", "distanceAxisExtractPMA", "distanceAxisXCnd", "distanceAxisYZCnd", "interpolationPMA", "distanceScaleMD"]
                    for messageAttr in messageAttrList:
                        cmds.addAttr(self.net, longName=messageAttr, attributeType="message")
                    cmds.addAttr(self.net, longName="inputRigScale", attributeType="float", defaultValue=1)
                    optionCtrl = self.utils.getNodeByMessage("optionCtrl")
                    if optionCtrl:
                        cmds.connectAttr(optionCtrl+".rigScaleOutput", self.net+".inputRigScale", force=True)
                    cmds.addAttr(self.net, longName="corrective", attributeType="float", minValue=0, defaultValue=1, maxValue=1)
                    cmds.addAttr(self.net, longName="outputValue", attributeType="float")
                    cmds.setAttr(self.net+".dpNetwork", 1)
                    cmds.setAttr(self.net+".dpCorrectionManager", 1)
                    cmds.setAttr(self.net+".name", correctionName, type="string")
                    cmds.setAttr(self.net+".type", correctType, type="string")
                    # setup group
                    correctionDataGrp = cmds.group(empty=True, name=correctionName+"_Grp")
                    cmds.parent(correctionDataGrp, self.correctionManagerDataGrp)
                    cmds.connectAttr(correctionDataGrp+".message", self.net+".correctionDataGrp", force=True)
                    originalLoc = self.createCorrectiveLocator(correctionName+"_Original", origNode, toRivet)
                    actionLoc = self.createCorrectiveLocator(correctionName+"_Action", actionNode, toRivet)
                    cmds.connectAttr(originalLoc+".message", self.net+".originalLoc", force=True)
                    cmds.connectAttr(actionLoc+".message", self.net+".actionLoc", force=True)

                    # create corrective, interpolation and rigScale nodes:
                    correctiveMD = cmds.createNode("multiplyDivide", name=correctionName+"_Corrective_MD")
                    interpolationPMA = cmds.createNode("plusMinusAverage", name=correctionName+"_Interpolation_PMA")
                    self.toIDList.extend([self.net, correctiveMD, interpolationPMA])
                    cmds.connectAttr(correctiveMD+".message", self.net+".correctiveMD", force=True)
                    cmds.connectAttr(interpolationPMA+".message", self.net+".interpolationPMA", force=True)
                    cmds.connectAttr(self.net+".corrective", correctiveMD+".input2X", force=True)
                    cmds.connectAttr(self.net+".interpolation", interpolationPMA+".input1D[0]", force=True)
                    cmds.setAttr(interpolationPMA+".input1D[1]", 1)
                    
                    # if rotate extration option:
                    if correctType == self.angleName:                        
                        # write a new self.utils function to generate these matrix nodes here:
                        extractAngleMM = cmds.createNode("multMatrix", name=correctionName+"_ExtractAngle_MM")
                        extractAngleDM = cmds.createNode("decomposeMatrix", name=correctionName+"_ExtractAngle_DM")
                        extractAngleQtE = cmds.createNode("quatToEuler", name=correctionName+"_ExtractAngle_QtE")
                        extractAngleMD = cmds.createNode("multiplyDivide", name=correctionName+"_ExtractAngle_MD")
                        # workaround to generate UnitConversion nodes before connect to Choice node (passing by a temporary MultiplyDivide)
                        angleUnitConversionMD = cmds.createNode("multiplyDivide", name=correctionName+"_ExtractAngle_UnitConversion_MD")
                        angleAxisChc = cmds.createNode("choice", name=correctionName+"_ExtractAngle_Axis_Chc")
                        smallerThanOneCnd = cmds.createNode("condition", name=correctionName+"_ExtractAngle_SmallerThanOne_Cnd")
                        overZeroCnd = cmds.createNode("condition", name=correctionName+"_ExtractAngle_OverZero_Cnd")
                        inputRmV = cmds.createNode("remapValue", name=correctionName+"_Input_RmV")
                        outputSR = cmds.createNode("setRange", name=correctionName+"_Output_SR")
                        self.toIDList.extend([extractAngleMM, extractAngleDM, extractAngleQtE, extractAngleMD, angleUnitConversionMD, angleAxisChc, smallerThanOneCnd, overZeroCnd, inputRmV, outputSR])
                        cmds.setAttr(extractAngleMD+".operation", 2)
                        cmds.setAttr(smallerThanOneCnd+".operation", 5) #less or equal
                        cmds.setAttr(smallerThanOneCnd+".secondTerm", 1)
                        cmds.setAttr(overZeroCnd+".secondTerm", 0)
                        cmds.setAttr(overZeroCnd+".colorIfFalseR", 0)
                        cmds.setAttr(overZeroCnd+".operation", 3) #greater or equal
                        cmds.connectAttr(actionLoc+".worldMatrix[0]", extractAngleMM+".matrixIn[0]", force=True)
                        cmds.connectAttr(originalLoc+".worldInverseMatrix[0]", extractAngleMM+".matrixIn[1]", force=True)
                        cmds.connectAttr(extractAngleMM+".matrixSum", extractAngleDM+".inputMatrix", force=True)
                        # set general values and connections:
                        cmds.setAttr(outputSR+".oldMaxX", 1)
                        cmds.connectAttr(self.net+".inputStart", inputRmV+".inputMin", force=True)
                        cmds.connectAttr(self.net+".inputEnd", inputRmV+".inputMax", force=True)
                        cmds.connectAttr(self.net+".inputEnd", inputRmV+".outputMax", force=True)
                        cmds.connectAttr(self.net+".outputStart", outputSR+".minX", force=True)
                        cmds.connectAttr(self.net+".outputEnd", outputSR+".maxX", force=True)
                        cmds.connectAttr(interpolationPMA+".output1D", inputRmV+".value[0].value_Interp", force=True)
                        # setup the rotation affection
                        cmds.connectAttr(extractAngleDM+".outputQuatX", extractAngleQtE+".inputQuatX", force=True)
                        cmds.connectAttr(extractAngleDM+".outputQuatY", extractAngleQtE+".inputQuatY", force=True)
                        cmds.connectAttr(extractAngleDM+".outputQuatZ", extractAngleQtE+".inputQuatZ", force=True)
                        cmds.connectAttr(extractAngleDM+".outputQuatW", extractAngleQtE+".inputQuatW", force=True)
                        # axis setup
                        cmds.connectAttr(extractAngleQtE+".outputRotateX", angleUnitConversionMD+".input1X", force=True)
                        cmds.connectAttr(extractAngleQtE+".outputRotateY", angleUnitConversionMD+".input1Y", force=True)
                        cmds.connectAttr(extractAngleQtE+".outputRotateZ", angleUnitConversionMD+".input1Z", force=True)
                        cmds.connectAttr(cmds.listConnections(angleUnitConversionMD+".input1X", source=True, destination=False, plugs=True)[0], angleAxisChc+".input[0]", force=True)
                        cmds.connectAttr(cmds.listConnections(angleUnitConversionMD+".input1Y", source=True, destination=False, plugs=True)[0], angleAxisChc+".input[1]", force=True)
                        cmds.connectAttr(cmds.listConnections(angleUnitConversionMD+".input1Z", source=True, destination=False, plugs=True)[0], angleAxisChc+".input[2]", force=True)
                        cmds.delete(angleUnitConversionMD)
                        cmds.connectAttr(self.net+".axis", angleAxisChc+".selector", force=True)
                        cmds.connectAttr(angleAxisChc+".output", inputRmV+".inputValue", force=True)
                        cmds.connectAttr(inputRmV+".outValue", extractAngleMD+".input1X", force=True)
                        cmds.connectAttr(angleAxisChc+".output", self.net+".inputValue", force=True)
                        cmds.setAttr(self.net+".inputValue", lock=True)
                        # axis order setup
                        cmds.connectAttr(self.net+".inputEnd", extractAngleMD+".input2X", force=True) #it'll be updated when changing angle
                        cmds.connectAttr(extractAngleMD+".outputX", smallerThanOneCnd+".firstTerm", force=True)
                        cmds.connectAttr(extractAngleMD+".outputX", smallerThanOneCnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(smallerThanOneCnd+".outColorR", overZeroCnd+".firstTerm", force=True)
                        cmds.connectAttr(smallerThanOneCnd+".outColorR", overZeroCnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(self.net+".axisOrder", extractAngleDM+".inputRotateOrder", force=True)
                        cmds.connectAttr(self.net+".axisOrder", extractAngleQtE+".inputRotateOrder", force=True)
                        # corrective setup:
                        cmds.connectAttr(overZeroCnd+".outColorR", correctiveMD+".input1X", force=True)
                        cmds.connectAttr(correctiveMD+".outputX", outputSR+".valueX", force=True)
                        # TODO create a way to avoid manual connection here, maybe using the UI new tab?
                        cmds.connectAttr(outputSR+".outValueX", self.net+".outputValue", force=True)
                        cmds.setAttr(self.net+".outputValue", lock=True)
                        # serialize angle nodes
                        cmds.connectAttr(extractAngleMM+".message", self.net+".extractAngleMM", force=True)
                        cmds.connectAttr(extractAngleDM+".message", self.net+".extractAngleDM", force=True)
                        cmds.connectAttr(extractAngleQtE+".message", self.net+".extractAngleQtE", force=True)
                        cmds.connectAttr(extractAngleMD+".message", self.net+".extractAngleMD", force=True)
                        cmds.connectAttr(angleAxisChc+".message", self.net+".angleAxisChc", force=True)
                        cmds.connectAttr(smallerThanOneCnd+".message", self.net+".smallerThanOneCnd", force=True)
                        cmds.connectAttr(overZeroCnd+".message", self.net+".overZeroCnd", force=True)
                        cmds.connectAttr(inputRmV+".message", self.net+".inputRmV", force=True)
                        cmds.connectAttr(outputSR+".message", self.net+".outputSR", force=True)
                        
                    else: #Distance
                        distanceScaleMD = cmds.createNode("multiplyDivide", name=correctionName+"_DistanceRigScale_MD")
                        outputRmV = cmds.createNode("remapValue", name=correctionName+"_Output_RmV")
                        distBet = cmds.createNode("distanceBetween", name=correctionName+"_Distance_DB")
                        distanceAxisExtractPMA = cmds.createNode("plusMinusAverage", name=correctionName+"_DistanceAxisExtract_PMA")
                        distanceAllCnd = cmds.createNode("condition", name=correctionName+"_ExtractDistance_Cnd")
                        distanceAxisXCnd = cmds.createNode("condition", name=correctionName+"_ExtractDistance_AxisX_Cnd")
                        distanceAxisYZCnd = cmds.createNode("condition", name=correctionName+"_ExtractDistance_AxisYZ_Cnd")
                        self.toIDList.extend([distanceScaleMD, outputRmV, distBet, distanceAxisExtractPMA, distanceAllCnd, distanceAxisXCnd, distanceAxisYZCnd])
                        # connect locators source position values to extract distance from them
                        cmds.connectAttr(originalLoc+".worldPosition.worldPositionX", distBet+".point1X")
                        cmds.connectAttr(originalLoc+".worldPosition.worldPositionY", distBet+".point1Y")
                        cmds.connectAttr(originalLoc+".worldPosition.worldPositionZ", distBet+".point1Z")
                        cmds.connectAttr(actionLoc+".worldPosition.worldPositionX", distBet+".point2X")
                        cmds.connectAttr(actionLoc+".worldPosition.worldPositionY", distBet+".point2Y")
                        cmds.connectAttr(actionLoc+".worldPosition.worldPositionZ", distBet+".point2Z")
                        # setup distance input and output connections
                        cmds.connectAttr(outputRmV+".outValue", correctiveMD+".input1X", force=True)
                        cmds.connectAttr(distanceScaleMD+".message", self.net+".distanceScaleMD", force=True)
                        cmds.connectAttr(self.net+".inputRigScale", distanceScaleMD+".input2X", force=True)
                        cmds.connectAttr(self.net+".inputRigScale", distanceScaleMD+".input2Y", force=True)
                        cmds.connectAttr(self.net+".inputStart", distanceScaleMD+".input1X", force=True)
                        cmds.connectAttr(distanceScaleMD+".outputX", outputRmV+".inputMin", force=True)
                        cmds.connectAttr(self.net+".inputEnd", distanceScaleMD+".input1Y", force=True)
                        cmds.connectAttr(distanceScaleMD+".outputY", outputRmV+".inputMax", force=True)
                        cmds.connectAttr(self.net+".outputStart", outputRmV+".outputMin", force=True)
                        cmds.connectAttr(self.net+".outputEnd", outputRmV+".outputMax", force=True)
                        cmds.connectAttr(interpolationPMA+".output1D", outputRmV+".value[0].value_Interp", force=True)
                        # set default distance input values
                        cmds.setAttr(self.net+".inputStart", 10)
                        cmds.setAttr(self.net+".inputEnd", 0)
                        # TODO create a way to avoid manual connection here, maybe using the UI new tab?
                        cmds.connectAttr(correctiveMD+".outputX", self.net+".outputValue", force=True)
                        cmds.setAttr(self.net+".outputValue", lock=True)
                        # extract axis by decomposing distance vector:
                        cmds.setAttr(distanceAxisExtractPMA+".operation", 2) #Substract
                        cmds.setAttr(distanceAxisYZCnd+".secondTerm", 1) #Y
                        cmds.connectAttr(originalLoc+".worldPosition.worldPositionX", distanceAxisExtractPMA+".input3D[0].input3Dx", force=True)
                        cmds.connectAttr(originalLoc+".worldPosition.worldPositionY", distanceAxisExtractPMA+".input3D[0].input3Dy", force=True)
                        cmds.connectAttr(originalLoc+".worldPosition.worldPositionZ", distanceAxisExtractPMA+".input3D[0].input3Dz", force=True)
                        cmds.connectAttr(actionLoc+".worldPosition.worldPositionX", distanceAxisExtractPMA+".input3D[1].input3Dx", force=True)
                        cmds.connectAttr(actionLoc+".worldPosition.worldPositionY", distanceAxisExtractPMA+".input3D[1].input3Dy", force=True)
                        cmds.connectAttr(actionLoc+".worldPosition.worldPositionZ", distanceAxisExtractPMA+".input3D[1].input3Dz", force=True)
                        cmds.connectAttr(self.net+".decompose", distanceAllCnd+".firstTerm", force=True)
                        cmds.connectAttr(self.net+".axis", distanceAxisXCnd+".firstTerm", force=True)
                        cmds.connectAttr(self.net+".axis", distanceAxisYZCnd+".firstTerm", force=True)
                        cmds.connectAttr(distBet+".distance", distanceAllCnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(distanceAxisXCnd+".outColorR", distanceAllCnd+".colorIfFalseR", force=True)
                        cmds.connectAttr(distanceAxisExtractPMA+".output3Dx", distanceAxisXCnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(distanceAxisYZCnd+".outColorR", distanceAxisXCnd+".colorIfFalseR", force=True)
                        cmds.connectAttr(distanceAxisExtractPMA+".output3Dy", distanceAxisYZCnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(distanceAxisExtractPMA+".output3Dz", distanceAxisYZCnd+".colorIfFalseR", force=True)
                        cmds.connectAttr(distanceAllCnd+".outColorR", outputRmV+".inputValue", force=True)
                        cmds.connectAttr(distanceAllCnd+".outColorR", self.net+".inputValue", force=True)
                        cmds.setAttr(self.net+".inputValue", lock=True)
                        # serialize distance nodes
                        cmds.connectAttr(distBet+".message", self.net+".distanceBet", force=True)
                        cmds.connectAttr(outputRmV+".message", self.net+".outputRmV", force=True)
                        cmds.connectAttr(distanceAxisExtractPMA+".message", self.net+".distanceAxisExtractPMA", force=True)
                        cmds.connectAttr(distanceAllCnd+".message", self.net+".distanceAllCnd", force=True)
                        cmds.connectAttr(distanceAxisXCnd+".message", self.net+".distanceAxisXCnd", force=True)
                        cmds.connectAttr(distanceAxisYZCnd+".message", self.net+".distanceAxisYZCnd", force=True)
                    
                    self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID
                    self.dpUIinst.customAttr.addAttr(0, [self.correctionManagerDataGrp], descendents=True) #dpID
                    # update UI                    
                    if self.ui:
                        self.populateNetUI()
                        self.actualizeEditLayout()
                    cmds.undoInfo(closeChunk=True)
                else:
                    mel.eval('warning \"'+self.dpUIinst.lang['m065_selOrigAction']+'\";')
            else:
                mel.eval('warning \"'+self.dpUIinst.lang['m066_selectTwo']+'\";')
        return self.net
