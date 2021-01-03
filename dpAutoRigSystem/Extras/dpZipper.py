# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import dpAutoRigSystem.Modules.Library.dpControls as dpControls
import dpAutoRigSystem.Modules.Library.dpUtils as utils


# global variables to this module:    
CLASS_NAME = "Zipper"
TITLE = "m061_zipper"
DESCRIPTION = "m062_zipperDesc"
ICON = "/Icons/dp_zipper.png"

ZIPPER_ATTR = "dpZipper"
ZIPPER_ID = "dpZipperID"

DPZIP_VERSION = "2.13"


class Zipper():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.zipperName = self.langDic[self.langName]['m061_zipper']
        self.firstName = self.langDic[self.langName]['c114_first']
        self.secondName = self.langDic[self.langName]['c115_second']
        self.goodToDPAR = True
        self.origModel = None
        self.firstCurve = None
        self.secondCurve = None
        self.middleCurve = None
        self.firstBlendCurve = None
        self.secondBlendCurve = None
        self.curveAxis = 0
        self.curveDirection = "X"
        # call main UI function
        self.dpZipperCloseUI()
        self.dpZipperUI()
        self.dpLoadData()
    
    
    def dpZipperCloseUI(self, *args):
        """ Delete existing Zipper window if it exists.
        """
        if cmds.window('dpZipperWindow', query=True, exists=True):
            cmds.deleteUI('dpZipperWindow', window=True)
    
    
    def dpZipperUI(self, *args):
        """ Zipper UI layout and elements.
        """
        zipper_winWidth  = 380
        zipper_winHeight = 300
        cmds.window('dpZipperWindow', title=self.zipperName+" "+str(DPZIP_VERSION), widthHeight=(zipper_winWidth, zipper_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpZipperWindow')
        
        # create UI layout and elements:
        zipperLayout = cmds.columnLayout('zipperLayout', adjustableColumn=True, columnOffset=("left", 10))
        cmds.text(label=self.langDic[self.langName]['i191_selectPoly'], align="left", height=30, font='boldLabelFont', parent=zipperLayout)
        # original model layout:
        zipperLayoutA = cmds.rowColumnLayout('zipperLayoutA', numberOfColumns=2, columnWidth=[(1, 160), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=zipperLayout)
        self.origModel_BT = cmds.button('origModel_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['m152_originalModel']+" >>", command=self.dpLoadOrigModel, backgroundColor=(1.0, 0.9, 0.4), parent=zipperLayoutA)
        self.origModel_TF = cmds.textField('origModel_TF', editable=False, parent=zipperLayoutA)
        cmds.separator(style='in', height=15, width=100, parent=zipperLayout)
        # polygon edges to curves layout:
        cmds.text(label=self.langDic[self.langName]['i188_selectEdges'], align="left", height=30, font='boldLabelFont', parent=zipperLayout)
        zipperLayoutB = cmds.rowColumnLayout('zipperLayoutB', numberOfColumns=2, columnWidth=[(1, 160), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], rowSpacing=(1, 3), parent=zipperLayout)
        self.first_BT = cmds.button('first_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['c114_first']+" "+self.langDic[self.langName]['i189_curve']+" >>", command=partial(self.dpCreateCurveFromEdge, "c114_first"), backgroundColor=(1.0, 0.9, 0.4), parent=zipperLayoutB)
        self.first_TF = cmds.textField('first_TF', editable=False, parent=zipperLayoutB)
        self.second_BT = cmds.button('second_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['c115_second']+" "+self.langDic[self.langName]['i189_curve']+" >>", command=partial(self.dpCreateCurveFromEdge, "c115_second"), backgroundColor=(1.0, 0.9, 0.4), parent=zipperLayoutB)
        self.second_TF = cmds.textField('second_TF', editable=False, parent=zipperLayoutB)
        cmds.separator(style='in', height=15, width=100, parent=zipperLayout)
        # options layout:
        cmds.text(label=self.langDic[self.langName]["i002_options"]+":", height=30, font='boldLabelFont', align='left', parent=zipperLayout)
        zipperLayoutC = cmds.columnLayout('zipperLayoutC', adjustableColumn=True, columnOffset=("left", 10), rowSpacing=3, parent=zipperLayout)
        self.curveDirectionRB = cmds.radioButtonGrp('curveDirectionRB', label=self.langDic[self.langName]['i189_curve']+' '+self.langDic[self.langName]['i106_direction'], labelArray3=['X', 'Y', 'Z'], columnAlign=[(1, 'left'), (2, 'left')], columnWidth=[(1, 100), (2, 50), (3, 50), (4, 50)], adjustableColumn=4, numberOfRadioButtons=3, select=1, changeCommand=self.dpGetCurveDirection, vertical=False, parent=zipperLayoutC)
        self.goodToDPAR_CB = cmds.checkBox("goodToDPAR_CB", label=self.langDic[self.langName]['i190_integrateDPAR'], value=1, align='left', parent=zipperLayoutC)
        cmds.separator(style='none', height=15, width=100, parent=zipperLayout)
        createLayout = cmds.columnLayout('createLayout', columnOffset=("left", 10), parent=zipperLayout)
        cmds.button(label=self.langDic[self.langName]["i158_create"]+" "+self.zipperName, annotation=self.langDic[self.langName]["i158_create"]+" "+self.zipperName, command=self.dpCreateZipper, width=350, backgroundColor=(0.3, 1, 0.7), parent=createLayout)
    
    
    def dpGetGoodToDPAR(self, *args):
        """ Check if we'll integrate with dpAutoRigSystem.
        """
        self.goodToDPAR = cmds.checkBox(self.goodToDPAR_CB, query=True, value=True)
        return self.goodToDPAR
    
    
    def dpLoadOrigModel(self, *args):
        """ Load selected object as original model.
        """
        selectedList = cmds.ls(selection=True)
        if selectedList:
            if cmds.objectType(cmds.listRelatives(selectedList[0], children=True)[0]) == "mesh":
                cmds.textField(self.origModel_TF, edit=True, text=selectedList[0])
                cmds.button(self.origModel_BT, edit=True, label=self.langDic[self.langName]['m152_originalModel'], backgroundColor=(0.3, 0.8, 1.0))
                self.origModel = selectedList[0]
        else:
            mel.eval('warning \"'+self.langDic[self.langName]['i191_selectPoly']+'\";')
    
    
    def dpCreateCurveFromEdge(self, zipperId, *args):
        """ Create curve from selected polygon edges.
        """
        self.dpGetCurveDirection()
        # declaring names:
        thisName = self.firstName
        if zipperId == "c115_second":
            thisName = self.secondName
        curveName = self.zipperName+"_"+thisName+"_Crv"
        pecName = self.zipperName+"_"+thisName+"_PEC"
        # get selected edges:
        edgeList = cmds.ls(selection=True, flatten=True)
        if not edgeList == None and not edgeList == [] and not edgeList == "":
            # delete old curve:
            self.dpDeleteOldCurve(zipperId)
            # create curve:
            baseCurve = cmds.polyToCurve(name=curveName, form=2, degree=3, conformToSmoothMeshPreview=0)[0]
            # rename polyEdgeToCurve node:
            cmds.rename(cmds.listConnections(baseCurve+".create")[0], pecName)
            # add attributes:
            cmds.addAttr(baseCurve, longName=ZIPPER_ATTR, attributeType='bool')
            cmds.addAttr(baseCurve, longName=ZIPPER_ID, dataType='string')
            cmds.setAttr(baseCurve+"."+ZIPPER_ATTR, 1)
            cmds.setAttr(baseCurve+"."+ZIPPER_ID, zipperId, type="string")
            # load curve data:
            self.dpLoadData(baseCurve)
        else:
            mel.eval('warning \"'+self.langDic[self.langName]['i188_selectEdges']+'\";')
    
    
    def dpDeleteOldCurve(self, zipperId, *args):
        """ Check if exist the same old curve to delete it.
        """
        transformList = cmds.ls(selection=False, type="transform")
        if transformList:
            for node in transformList:
                if cmds.objExists(node+"."+ZIPPER_ATTR):
                    if cmds.getAttr(node+"."+ZIPPER_ATTR) == 1:
                        if cmds.getAttr(node+"."+ZIPPER_ID) == zipperId:
                            cmds.delete(node)
    
    
    def dpLoadData(self, curveName=None, *args):
        """ Load curve info from given curve name or try to find any zipper curve existing in the scene.
            Updates de UI after finding curves.
        """
        if curveName:
            zipperId = cmds.getAttr(curveName+"."+ZIPPER_ID)
            self.dpUpdateUI(curveName, zipperId)
        else:
            cmds.textField(self.first_TF, edit=True, text="")
            cmds.textField(self.second_TF, edit=True, text="")
            transformList = cmds.ls(selection=False, type="transform")
            if transformList:
                for node in transformList:
                    if cmds.objExists(node+"."+ZIPPER_ATTR):
                        if cmds.getAttr(node+"."+ZIPPER_ATTR) == 1:
                            zipperId = cmds.getAttr(node+"."+ZIPPER_ID)
                            self.dpUpdateUI(node, zipperId)
    
    
    def dpUpdateUI(self, curveName, zipperId, *args):
        """ Updates zipper UI with the given curve name and refresh the button, text field and curve variable.
        """        
        if zipperId == "c114_first":
            cmds.textField(self.first_TF, edit=True, text=curveName)
            cmds.button(self.first_BT, edit=True, label=self.firstName+" "+self.langDic[self.langName]['i189_curve'], backgroundColor=(0.3, 0.8, 1.0))
            self.firstCurve = curveName
        elif zipperId == "c115_second":
            cmds.textField(self.second_TF, edit=True, text=curveName)
            cmds.button(self.second_BT, edit=True, label=self.secondName+" "+self.langDic[self.langName]['i189_curve'], backgroundColor=(0.3, 0.8, 1.0))
            self.secondCurve = curveName
    
    
    def dpGetCurveDirection(self, *args):
        """ Read radioButtonGrp selected item from UI.
            Set curveAxis variable to be used in the curve reverse setup if needed to set up curve direction.
            Update curveDirection variable value to be "X", "Y" or "Z".
        """
        selectedItem = cmds.radioButtonGrp(self.curveDirectionRB, query=True, select=True)
        self.curveAxis = selectedItem-1
        if selectedItem == 1:
            self.curveDirection = "X"
        elif selectedItem == 2:
            self.curveDirection = "Y"
        elif selectedItem == 3:
            self.curveDirection = "Z"
    
    
    def dpSetCurveDirection(self, curveName, *args):
        """ Check and set the curve direction.
            Reverse curve direction if the first CV position is greather than last CV position by current axis.
        """
        cmds.setAttr(curveName+"."+ZIPPER_ATTR, 0)
        cmds.select(curveName+".cv[*]")
        curveLength = len(cmds.ls(selection=True, flatten=True))
        cmds.select(clear=True)
        minPos = cmds.xform(curveName+".cv[0]", query=True, worldSpace=True, translation=True)[self.curveAxis]
        maxPos = cmds.xform(curveName+".cv["+str(curveLength-1)+"]", query=True, worldSpace=True, translation=True)[self.curveAxis]
        if minPos > maxPos:
            cmds.reverseCurve(curveName, constructionHistory=True, replaceOriginal=True)
            cmds.rename(cmds.listConnections(curveName+".create")[0], utils.extractSuffix(curveName)+"_"+self.curveDirection+"_RevC")
    
    
    def dpGenerateMiddleCurve(self, origCurve, *args):
        """ Create a middle curve using an avgCurves node.
        """
        self.middleCurve = cmds.duplicate(origCurve, name=self.zipperName+"_"+self.langDic[self.langName]['c029_middle']+"_Crv")[0]
        averageCurveNode = cmds.createNode('avgCurves', name=self.zipperName+"_"+self.langDic[self.langName]['c029_middle']+"_AvgC")
        cmds.setAttr(averageCurveNode+".automaticWeight", 0)
        cmds.connectAttr(self.firstCurve+".worldSpace", averageCurveNode+".inputCurve1", force=True)
        cmds.connectAttr(self.secondCurve+".worldSpace", averageCurveNode+".inputCurve2", force=True)
        cmds.connectAttr(averageCurveNode+".outputCurve", self.middleCurve+".create", force=True)
    
    
    def dpCreateCurveBlendSetup(self, *args):
        """ Create the main curve setup using blendShapes.
            Zipper_Ctrl has attributes to control automatic or manual blend.
            This method calculate the setRange values and clamp them to target weights of the curve blendShapes.
        """
        # declaring names:
        activeAttr = "zipper"+self.langDic[self.langName]['c118_active'].capitalize()
        crescentAttr = self.langDic[self.langName]['c116_crescent']
        decrescentAttr = self.langDic[self.langName]['c117_decrescent']
        autoAttr = self.langDic[self.langName]['c119_auto']
        autoIntensityAttr = self.langDic[self.langName]['c119_auto']+self.langDic[self.langName]['c049_intensity'].capitalize()
        autoCalibrateMinAttr = self.langDic[self.langName]['c119_auto']+self.langDic[self.langName]['c111_calibrate']+"Min"
        autoCalibrateMaxAttr = self.langDic[self.langName]['c119_auto']+self.langDic[self.langName]['c111_calibrate']+"Max"
        initialDistanceAttr = "initialDistance"
        distanceAttr = "distance"
        rigScaleAttr = "rigScale"
        
        # create zipper control and attributes:
        self.zipperCtrl = self.ctrls.cvControl('id_074_Zipper', self.zipperName+"_Ctrl", d=0)
        cmds.addAttr(self.zipperCtrl, longName=activeAttr, attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=crescentAttr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=decrescentAttr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=autoAttr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=autoIntensityAttr, attributeType='float', defaultValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=autoCalibrateMinAttr, attributeType='float', defaultValue=0)
        cmds.addAttr(self.zipperCtrl, longName=autoCalibrateMaxAttr, attributeType='float', defaultValue=1)
        cmds.addAttr(self.zipperCtrl, longName=initialDistanceAttr, attributeType='float', defaultValue=0)
        cmds.addAttr(self.zipperCtrl, longName=distanceAttr, attributeType='float', defaultValue=0)
        cmds.addAttr(self.zipperCtrl, longName=rigScaleAttr, attributeType='float', defaultValue=1)
        
        ctrlGrp = cmds.group(self.zipperCtrl, name=self.zipperName+"_Control_Grp")
        
        # check if there's a dpAR Option_Ctrl:
        if self.goodToDPAR:
            optionCtrl = utils.getNodeByMessage("optionCtrl")
            if optionCtrl:
                optCtrlRigScaleNode = cmds.listConnections(optionCtrl+"."+rigScaleAttr, source=False, destination=True)[0]
                cmds.connectAttr(optCtrlRigScaleNode+".outputX", self.zipperCtrl+"."+rigScaleAttr, force=True)
                cmds.setAttr(self.zipperCtrl+"."+rigScaleAttr, lock=True)
            ctrlsVisibilityGrp = utils.getNodeByMessage("ctrlsVisibilityGrp")
            if ctrlsVisibilityGrp:
                cmds.parent(ctrlGrp, ctrlsVisibilityGrp)
        
        # create blend curves and connect create input from first and second curves:
        self.firstBlendCurve = cmds.duplicate(self.firstCurve, name=utils.extractSuffix(self.firstCurve)+"_Blend_Crv")[0]
        self.secondBlendCurve = cmds.duplicate(self.secondCurve, name=utils.extractSuffix(self.secondCurve)+"_Blend_Crv")[0]
        cmds.connectAttr(self.firstCurve+".worldSpace", self.firstBlendCurve+".create", force=True)
        cmds.connectAttr(self.secondCurve+".worldSpace", self.secondBlendCurve+".create", force=True)
        
        # create curve blendShapes
        self.firstBS = cmds.blendShape(self.middleCurve, self.firstBlendCurve, topologyCheck=False, name=utils.extractSuffix(self.firstCurve)+"_BS")[0]
        self.secondBS = cmds.blendShape(self.middleCurve, self.secondBlendCurve, topologyCheck=False, name=utils.extractSuffix(self.secondCurve)+"_BS")[0]
        cmds.connectAttr(self.zipperCtrl+"."+activeAttr, self.firstBS+"."+self.middleCurve, force=True)
        cmds.connectAttr(self.zipperCtrl+"."+activeAttr, self.secondBS+"."+self.middleCurve, force=True)
        
        # distance dimension to calculate automatic setup:
        distDimShape = cmds.distanceDimension(startPoint=(10, 100, 1000), endPoint=(11, 101, 101)) #magic numbers to avoid get existing locator at origin
        self.distDimTransform = cmds.listRelatives(distDimShape, parent=True, type="transform")[0]
        self.distDimTransform = cmds.rename(self.distDimTransform, self.zipperName+"_"+autoAttr.capitalize()+"_DD")
        distDimShape = self.distDimTransform+"Shape"
        cmds.connectAttr(distDimShape+"."+distanceAttr, self.zipperCtrl+"."+distanceAttr, force=True)
        cmds.setAttr(self.zipperCtrl+"."+distanceAttr, lock=True)
        self.firstLoc = cmds.listConnections(distDimShape+".startPoint", source=True, destination=False)[0]
        self.firstLoc = cmds.rename(self.firstLoc, self.zipperName+"_"+autoAttr.capitalize()+"_"+self.firstName+"_Loc")
        self.secondLoc = cmds.listConnections(distDimShape+".endPoint", source=True, destination=False)[0]
        self.secondLoc = cmds.rename(self.secondLoc, self.zipperName+"_"+autoAttr.capitalize()+"_"+self.secondName+"_Loc")
        # attach locators to original curves:
        firstMoP = utils.attachToMotionPath(self.firstLoc, self.firstCurve, self.zipperName+"_"+autoAttr.capitalize()+"_"+self.firstName+"_MoP", 0.5)
        secondMoP = utils.attachToMotionPath(self.secondLoc, self.secondCurve, self.zipperName+"_"+autoAttr.capitalize()+"_"+self.secondName+"_MoP", 0.5)
        
        # automatic intensity and calibration:
        autoOnOffMD = cmds.createNode("multiplyDivide", name=self.zipperName+"_"+autoAttr.capitalize()+"_OnOff_MD")
        autoMaxCalibrateMD = cmds.createNode("multiplyDivide", name=self.zipperName+"_"+autoAttr.capitalize()+"_MD")
        rigScaleMD = cmds.createNode("multiplyDivide", name=self.zipperName+"_RigScale_MD")
        rigScaleAutoMD = cmds.createNode("multiplyDivide", name=self.zipperName+"_RigScale_Auto_MD")
        hyperboleScaleMD = cmds.createNode("multiplyDivide", name=self.zipperName+"_HyperboleScale_MD")
        autoMainSR = cmds.createNode("setRange", name=self.zipperName+"_"+autoAttr.capitalize()+"_SR")
        cmds.connectAttr(self.zipperCtrl+"."+autoAttr, autoOnOffMD+".input1X", force=True)
        cmds.connectAttr(autoMainSR+".outValueX", autoOnOffMD+".input2X", force=True)
        cmds.connectAttr(self.zipperCtrl+"."+autoIntensityAttr, autoMaxCalibrateMD+".input1X", force=True)
        cmds.connectAttr(self.zipperCtrl+"."+autoCalibrateMaxAttr, autoMaxCalibrateMD+".input2X", force=True)
        
        # auto distance:
        initialDistance = cmds.getAttr(distDimShape+"."+distanceAttr)
        cmds.setAttr(self.zipperCtrl+"."+initialDistanceAttr, initialDistance, lock=True)
        cmds.setAttr(self.zipperCtrl+"."+autoCalibrateMinAttr, (-10)*initialDistance)
        cmds.setAttr(self.zipperCtrl+"."+autoCalibrateMaxAttr, (20)*initialDistance) #magic numbers, need to be calibrated
        cmds.setAttr(autoMainSR+".minX", 1)
        cmds.setAttr(hyperboleScaleMD+".input1X", 1)
        cmds.setAttr(hyperboleScaleMD+".operation", 2) #divide
        cmds.connectAttr(self.zipperCtrl+"."+autoCalibrateMinAttr, autoMainSR+".oldMinX", force=True)
        cmds.connectAttr(autoMaxCalibrateMD+".outputX", autoMainSR+".oldMaxX", force=True)
        # rig scale setup to work with automatic distance:
        cmds.connectAttr(self.zipperCtrl+"."+initialDistanceAttr, rigScaleMD+".input1X", force=True)
        cmds.connectAttr(self.zipperCtrl+"."+rigScaleAttr, rigScaleMD+".input2X", force=True)
        cmds.connectAttr(rigScaleMD+".outputX", hyperboleScaleMD+".input2X", force=True)
        cmds.connectAttr(self.zipperCtrl+"."+distanceAttr, rigScaleAutoMD+".input1X", force=True)
        cmds.connectAttr(hyperboleScaleMD+".outputX", rigScaleAutoMD+".input2X", force=True)
        cmds.connectAttr(rigScaleAutoMD+".outputX", autoMainSR+".valueX", force=True)
        
        # calculate iter counter from middle curve length:
        cmds.select(self.middleCurve+".cv[*]")
        self.curveLength = len(cmds.ls(selection=True, flatten=True))
        halfCurveLength = self.curveLength * 0.5
        # calculate distance position based 1.0 from our control attribute:
        distPos = 1.0 / self.curveLength
        for c, curve in enumerate([self.firstCurve, self.secondCurve]):
            baseName = utils.extractSuffix(curve)
            for i in range(0, self.curveLength+1):
                lPosA = (i * distPos)
                lPosB = (lPosA + distPos)
                rPosB = 1 - (i * distPos)
                rPosA = (rPosB - distPos)
                if i > 0:
                    lPosA = lPosA - (distPos*0.5)
                    rPosA = rPosA - (distPos*0.5)
                if lPosA < 0:
                    lPosA = 0
                if rPosA < 0:
                    rPosA = 0
                # create setRange nodes:
                crescentSR = cmds.createNode("setRange", name=baseName+"_"+crescentAttr+"_"+str(i)+"_SR")
                decrescentSR = cmds.createNode("setRange", name=baseName+"_"+decrescentAttr+"_"+str(i)+"_SR")
                # set values for serRange nodes:
                cmds.setAttr(crescentSR+".oldMinX", lPosA)
                cmds.setAttr(crescentSR+".oldMaxX", lPosB)
                cmds.setAttr(crescentSR+".maxX", 1)
                cmds.setAttr(decrescentSR+".oldMinX", rPosA)
                cmds.setAttr(decrescentSR+".oldMaxX", rPosB)
                cmds.setAttr(decrescentSR+".maxX", 1)
                # connect attributes from control to setRange:
                cmds.connectAttr(self.zipperCtrl+"."+crescentAttr, crescentSR+".valueX", force=True)
                cmds.connectAttr(self.zipperCtrl+"."+decrescentAttr, decrescentSR+".valueX", force=True)
                # add values for two sides and auto too:
                zipperPMA = cmds.createNode("plusMinusAverage", name=baseName+"_"+str(i)+"_PMA")
                cmds.connectAttr(crescentSR+".outValueX", zipperPMA+".input1D[0]", force=True)
                cmds.connectAttr(decrescentSR+".outValueX", zipperPMA+".input1D[1]", force=True)
                # add auto setRange value:
                autoPosA = lPosA
                autoPosB = lPosB
                if i > halfCurveLength:
                    autoPosA = rPosA
                    autoPosB = rPosB
                autoSR = cmds.createNode("setRange", name=baseName+"_"+autoAttr.capitalize()+"_"+str(i)+"_SR")
                cmds.setAttr(autoSR+".oldMinX", autoPosA)
                cmds.setAttr(autoSR+".oldMaxX", autoPosB)
                cmds.setAttr(autoSR+".maxX", 1)
                # turn on or off this channel by zipperCtrl attribute:
                cmds.connectAttr(autoOnOffMD+".outputX", autoSR+".valueX", force=True)
                cmds.connectAttr(autoSR+".outValueX", zipperPMA+".input1D[2]", force=True)
                # clamp max value to 1 in order to connect it to the blend setup
                zipperClp = cmds.createNode("clamp", name=baseName+"_"+str(i)+"_Clp")
                cmds.setAttr(zipperClp+".maxR", 1)
                cmds.connectAttr(zipperPMA+".output1D", zipperClp+".inputR", force=True)
                # output clamp value to blendShape node target weights:
                if c == 0:
                    cmds.connectAttr(zipperClp+".outputR", self.firstBS+".inputTarget[0].inputTargetGroup[0].targetWeights["+str(i)+"]")
                    cmds.connectAttr(zipperClp+".outputR", self.secondBS+".inputTarget[0].inputTargetGroup[0].targetWeights["+str(i)+"]")
    
    
    def dpCreateDeformMesh(self, *args):
        """ Generate a final deformable mesh from original loaded mesh.
            Parent old original model to Model_Grp and rename it to _Geo.
            Rename the new final dformable mesh as _Def_Mesh and put it inside Render_Grp.
        """
        # store old mesh name:
        oldMeshName = self.origModel
        # generate deformMesh from origModel:
        self.deformMesh = cmds.polyDuplicateAndConnect(self.origModel)
        # rename geometries:
        self.origModel = cmds.rename(self.origModel, utils.extractSuffix(self.origModel)+"_Orig_Geo")
        self.deformMesh = cmds.rename(self.deformMesh, utils.extractSuffix(oldMeshName)+"_Def_Mesh")
        cmds.setAttr(self.origModel+".visibility", 0)
        # parent if need:
        modelGrp = utils.getNodeByMessage("modelsGrp")
        if modelGrp:
            cmds.parent(self.origModel, modelGrp)
        renderGrp = utils.getNodeByMessage("renderGrp")
        if renderGrp:
            # avoid reparent deformMesh if already inside RenderGrp:
            parentList, allParentList = [], []
            parentList.append(self.deformMesh)
            while parentList:
                parentList = cmds.listRelatives(parentList[0], allParents=True, type="transform")
                if parentList:
                    allParentList.append(parentList[0])
            if not renderGrp in allParentList:
                cmds.parent(self.deformMesh, renderGrp)
    
    
    def dpCreateWireDeform(self, *args):
        """ Create two wire deformer for first and second curves.
        """
        firstWireDef = cmds.wire(self.deformMesh, groupWithBase=False, crossingEffect=0, localInfluence=1, dropoffDistance=(0, 1), name=utils.extractSuffix(self.deformMesh)+"_First_Wire")[0]
        secondWireDef = cmds.wire(self.deformMesh, groupWithBase=False, crossingEffect=0, localInfluence=1, dropoffDistance=(0, 1), name=utils.extractSuffix(self.deformMesh)+"_Second_Wire")[0]
        cmds.connectAttr(self.firstCurve+".worldSpace[0]", firstWireDef+".baseWire[0]", force=True)
        cmds.connectAttr(self.secondCurve+".worldSpace[0]", secondWireDef+".baseWire[1]", force=True)
        cmds.connectAttr(self.firstBlendCurve+".worldSpace[0]", firstWireDef+".deformedWire[0]", force=True)
        cmds.connectAttr(self.secondBlendCurve+".worldSpace[0]", secondWireDef+".deformedWire[1]", force=True)
    
    
    def dpZipperDataGrp(self, *args):
        """ Store nodes to Static Group in Data Group.
        """
        zipperCurvesGrp = cmds.group(self.firstCurve, self.secondCurve, self.middleCurve, self.firstBlendCurve, self.secondBlendCurve, name=self.zipperName+"_Curves_Grp")
        zipperDistanceGrp = cmds.group(self.firstLoc, self.secondLoc, self.distDimTransform, name=self.zipperName+"_Distance_Grp")
        zipperDataGrp = cmds.group(zipperCurvesGrp, zipperDistanceGrp, name=self.zipperName+"_Data_Grp")
        if self.goodToDPAR:
            staticGrp = utils.getNodeByMessage("staticGrp")
            if staticGrp:
                cmds.parent(zipperDataGrp, staticGrp)
    
    
    def dpCreateZipper(self, *args):
        """ Main method to buid the all zipper setup.
            Uses the pre-defined and loaded curves.
        """
        dialogRun = cmds.confirmDialog(title="Zipper", message=self.langDic[self.langName]["i120_notUndoable"], button=[self.langDic[self.langName]["i174_continue"],self.langDic[self.langName]["i132_cancel"]], defaultButton=self.langDic[self.langName]["i174_continue"], cancelButton=self.langDic[self.langName]["i132_cancel"], dismissString=self.langDic[self.langName]["i132_cancel"])
        if dialogRun == self.langDic[self.langName]["i174_continue"]:
            self.dpGetGoodToDPAR()
            if self.firstCurve and self.secondCurve:
                if self.origModel:
                    self.dpGetCurveDirection()
                    self.dpSetCurveDirection(self.firstCurve)
                    self.dpSetCurveDirection(self.secondCurve)
                    self.dpGenerateMiddleCurve(self.firstCurve)
                    self.dpCreateCurveBlendSetup()
                    self.dpCreateDeformMesh()
                    self.dpCreateWireDeform()
                    self.dpZipperDataGrp()
                    self.dpZipperCloseUI()
                    cmds.select(self.zipperCtrl)
                    print self.langDic[self.langName]['m174_createdZipper'],
                else:
                    mel.eval('warning \"'+self.langDic[self.langName]['i191_selectPoly']+'\";')
            else:
                mel.eval('warning \"'+self.langDic[self.langName]['i188_selectEdges']+'\";')
