#!/usr/bin/python
# -*- coding: utf-8 -*-

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

DPZIP_VERSION = "2.9"


class Zipper():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.firstName = self.langDic[self.langName]['c114_first']
        self.secondName = self.langDic[self.langName]['c115_second']
        self.origModel = None
        self.firstCurve = None
        self.secondCurve = None
        self.middleCurve = None
        self.firstBlendCurve = None
        self.secondBlendCurve = None
        self.deformType = 1 #wire
        self.curveAxis = 0
        self.curveDirection = "X"
        self.jointList = []
        # call main UI function
        self.dpZipperUI(self)
    
    
    def dpZipperUI(self, *args):
        # delete existing window if it exists:
        if cmds.window('dpZipperWindow', query=True, exists=True):
            cmds.deleteUI('dpZipperWindow', window=True)
        zipper_winWidth  = 305
        zipper_winHeight = 470
        cmds.window('dpZipperWindow', title='dpZipper - v'+str(DPZIP_VERSION)+' - UI', widthHeight=(zipper_winHeight, zipper_winWidth), menuBar=False, sizeable=False, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpZipperWindow')
        
        # create UI layout and elements:
        zipperLayout = cmds.columnLayout('zipperLayout', adjustableColumn=True, columnOffset=("left", 10))
        cmds.text("Select polygon edges and create curves:", align="left", parent=zipperLayout)
        zipperLayoutA = cmds.rowColumnLayout('zipperLayoutA', numberOfColumns=2, columnWidth=[(1, 160), (2, 200)], parent=zipperLayout)
        self.origModel_BT = cmds.button('origModel_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['m152_originalModel']+" >>", command=self.dpLoadOrigModel, backgroundColor=[0.5, 0.5, 0.2], parent=zipperLayoutA)
        self.origModel_TF = cmds.textField('origModel_TF', editable=False, parent=zipperLayoutA)
        
        self.first_BT = cmds.button('first_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['c114_first']+" "+self.langDic[self.langName]['i189_curve']+" >>", command=partial(self.dpCreateCurveFromEdge, "c114_first"), backgroundColor=[0.5, 0.5, 0.2], parent=zipperLayoutA)
        self.first_TF = cmds.textField('first_TF', editable=False, parent=zipperLayoutA)
        self.second_BT = cmds.button('second_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['c115_second']+" "+self.langDic[self.langName]['i189_curve']+" >>", command=partial(self.dpCreateCurveFromEdge, "c115_second"), backgroundColor=[0.5, 0.5, 0.2], parent=zipperLayoutA)
        self.second_TF = cmds.textField('second_TF', editable=False, parent=zipperLayoutA)
        
        self.curveDirectionRB = cmds.radioButtonGrp('curveDirectionRB', label='Curve '+self.langDic[self.langName]['i106_direction'], labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3, select=1, changeCommand=self.dpGetCurveDirection, parent=zipperLayout)
        
        self.deformTypeRB = cmds.radioButtonGrp('deformTypeRB', label=self.langDic[self.langName]['i192_deformation'], labelArray2=['Wire Deformer', 'Joint Skinning'], numberOfRadioButtons=2, select=2, changeCommand=self.dpChangeDeformType, vertical=True, parent=zipperLayout)
        self.deformMethodRB = cmds.radioButtonGrp('deformMethodRB', label=self.langDic[self.langName]['i192_deformation']+" METHOD", labelArray2=['Before', 'After'], numberOfRadioButtons=2, select=2, changeCommand=self.dpChangeDeformMethod, vertical=True, parent=zipperLayout)
        
        cmds.text("WIP - text", parent=zipperLayout)
        cmds.button(label="WIP - RUN - WIP", command=self.dpCreateZipper, backgroundColor=[0.3, 1, 0.7], parent=zipperLayout)
        # check if exists zipper curves and load them:
        self.dpLoadData()
    
    
    def dpLoadOrigModel(self, *args):
        """ Load selected object as original model.
        """
        selectedList = cmds.ls(selection=True)
        if selectedList:
            if cmds.objectType(cmds.listRelatives(selectedList[0], children=True)[0]) == "mesh":
                cmds.textField(self.origModel_TF, edit=True, text=selectedList[0])
                cmds.button(self.origModel_BT, edit=True, label=self.langDic[self.langName]['m152_originalModel'], backgroundColor=[0.5, 0.5, 0.8])
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
        curveName = "Zipper_"+thisName+"_Crv"
        pecName = "Zipper_"+thisName+"_PEC"
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
            cmds.button(self.first_BT, edit=True, label=self.firstName+" "+self.langDic[self.langName]['i189_curve'], backgroundColor=[0.5, 0.5, 0.8])
            self.firstCurve = curveName
        elif zipperId == "c115_second":
            cmds.textField(self.second_TF, edit=True, text=curveName)
            cmds.button(self.second_BT, edit=True, label=self.secondName+" "+self.langDic[self.langName]['i189_curve'], backgroundColor=[0.5, 0.5, 0.8])
            self.secondCurve = curveName
    
    
    def dpGetDeformType(self, *args):
        """
        """
        self.deformType = cmds.radioButtonGrp(self.deformTypeRB, query=True, select=True)
    
    
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
    
    
    def dpChangeDeformType(self, *args):
        """
        """
        print "wip --- changing deformation type"
        
        
        
        
        
    def dpChangeDeformMethod(self, *args):
        """
        """
        print "wip --- changing deformation method"
        
        
    
    
    def dpSetCurveDirection(self, curveName, *args):
        """ Check and set the curve direction.
            Reverse curve direction if the first CV position is greather than last CV position by current axis.
        """
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
        self.middleCurve = cmds.duplicate(origCurve, name="Zipper_"+self.langDic[self.langName]['c029_middle']+"_Crv")[0]
        averageCurveNode = cmds.createNode('avgCurves', name="Zipper_"+self.langDic[self.langName]['c029_middle']+"_AvgC")
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
        self.zipperCtrl = self.ctrls.cvControl('id_074_Zipper', "Zipper_Ctrl")
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
        
        # check if there's a dpAR Option_Ctrl:
        optionCtrl = utils.getGroupByMessage("optionCtrl")
        if optionCtrl:
            optCtrlRigScaleNode = cmds.listConnections(optionCtrl+"."+rigScaleAttr, source=False, destination=True)[0]
            cmds.connectAttr(optCtrlRigScaleNode+".outputX", self.zipperCtrl+"."+rigScaleAttr, force=True)
            cmds.setAttr(self.zipperCtrl+"."+rigScaleAttr, lock=True)
        
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
        distDimTransform = cmds.listRelatives(distDimShape, parent=True, type="transform")[0]
        distDimTransform = cmds.rename(distDimTransform, "Zipper_"+autoAttr.capitalize()+"_DD")
        distDimShape = distDimTransform+"Shape"
        cmds.connectAttr(distDimShape+"."+distanceAttr, self.zipperCtrl+"."+distanceAttr, force=True)
        cmds.setAttr(self.zipperCtrl+"."+distanceAttr, lock=True)
        firstLoc = cmds.listConnections(distDimShape+".startPoint", source=True, destination=False)[0]
        firstLoc = cmds.rename(firstLoc, "Zipper_"+autoAttr.capitalize()+"_"+self.firstName+"_Loc")
        secondLoc = cmds.listConnections(distDimShape+".endPoint", source=True, destination=False)[0]
        secondLoc = cmds.rename(secondLoc, "Zipper_"+autoAttr.capitalize()+"_"+self.secondName+"_Loc")
        # attach locators to original curves:
        firstMoP = utils.attachToMotionPath(firstLoc, self.firstCurve, "Zipper_"+autoAttr.capitalize()+"_"+self.firstName+"_MoP", 0.5)
        secondMoP = utils.attachToMotionPath(secondLoc, self.secondCurve, "Zipper_"+autoAttr.capitalize()+"_"+self.secondName+"_MoP", 0.5)
        
        # automatic intensity and calibration:
        autoOnOffMD = cmds.createNode("multiplyDivide", name="Zipper_"+autoAttr.capitalize()+"_OnOff_MD")
        autoMaxCalibrateMD = cmds.createNode("multiplyDivide", name="Zipper_"+autoAttr.capitalize()+"_MD")
        rigScaleMD = cmds.createNode("multiplyDivide", name="Zipper_RigScale_MD")
        rigScaleAutoMD = cmds.createNode("multiplyDivide", name="Zipper_RigScale_Auto_MD")
        hyperboleScaleMD = cmds.createNode("multiplyDivide", name="Zipper_HyperboleScale_MD")
        autoMainSR = cmds.createNode("setRange", name="Zipper_"+autoAttr.capitalize()+"_SR")
        cmds.connectAttr(self.zipperCtrl+"."+autoAttr, autoOnOffMD+".input1X", force=True)
        cmds.connectAttr(autoMainSR+".outValueX", autoOnOffMD+".input2X", force=True)
        cmds.connectAttr(self.zipperCtrl+"."+autoIntensityAttr, autoMaxCalibrateMD+".input1X", force=True)
        cmds.connectAttr(self.zipperCtrl+"."+autoCalibrateMaxAttr, autoMaxCalibrateMD+".input2X", force=True)
        
        # auto distance:
        initialDistance = cmds.getAttr(distDimShape+"."+distanceAttr)
        cmds.setAttr(self.zipperCtrl+"."+initialDistanceAttr, initialDistance, lock=True)
        cmds.setAttr(self.zipperCtrl+"."+autoCalibrateMinAttr, initialDistance)
        cmds.setAttr(self.zipperCtrl+"."+autoCalibrateMaxAttr, initialDistance*20) #magic number, need to be calibrated
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
        # parent if need:
        modelGrp = utils.getGroupByMessage("modelsGrp")
        if modelGrp:
            cmds.parent(self.origModel, modelGrp)
        renderGrp = utils.getGroupByMessage("renderGrp")
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
    
    
    def dpCreateJointAndCtrl(self, thisName, blendCurve, distrib, i, *args):
        """ Create a joint and a simple fk control.
            Attach the setup to a motion path.
            Return the created joint and the control zeroOut group.
        """
        cmds.select(clear=True)
        jnt = cmds.joint(name="Zipper_"+thisName+"_"+str(i).zfill(2)+"_Jpm")
        ctrl = self.ctrls.cvControl('id_075_ZipperCtrl', "Zipper_"+thisName+"_"+str(i).zfill(2)+"_Ctrl")
        cmds.parentConstraint(ctrl, jnt, maintainOffset=False, name="Zipper_"+thisName+"_"+str(i).zfill(2)+"_PaC")
        cmds.scaleConstraint(ctrl, jnt, maintainOffset=False, name="Zipper_"+thisName+"_"+str(i).zfill(2)+"_ScC")
        ctrlZero = utils.zeroOut([ctrl])[0]
        utils.attachToMotionPath(ctrlZero, blendCurve, "Zipper_"+thisName+"_"+str(i).zfill(2)+"_MoP", (i * distrib))
        return jnt, ctrlZero
        
    
    
    def dpCreateJointSetup(self, *args):
        """
        """
        print "wip - creating joint setup here...."
        ctrlGrp = cmds.group(empty=True, name="Zipper_Ctrls_Grp")
        jointGrp = cmds.group(empty=True, name="Zipper_Joints_Grp")
        holderJnt = cmds.joint(name="Zipper_Holder_Jpm")
        self.jointList.append(holderJnt)
        
        distribution = 1.0 / self.curveLength
        for i in range(0, self.curveLength+1):
            firstJnt, firstCtrlZero = self.dpCreateJointAndCtrl(self.firstName, self.firstBlendCurve, distribution, i)
            secondJnt, secondCtrlZero = self.dpCreateJointAndCtrl(self.secondName, self.secondBlendCurve, distribution, i)
            self.jointList.append(firstJnt)
            self.jointList.append(secondJnt)
            cmds.parent(firstJnt, secondJnt, jointGrp)
            cmds.parent(firstCtrlZero, secondCtrlZero, ctrlGrp)
            
        
            
            
            
            
            
    
    def dpSetUsedCurves(self, *args):
        """ Set zipper attribute to off in order to desactivate finding this zipper curve by UI.
        """
        cmds.setAttr(self.firstCurve+"."+ZIPPER_ATTR, 0)
        cmds.setAttr(self.secondCurve+"."+ZIPPER_ATTR, 0)
        self.dpLoadData()
    
    
    def dpCreateZipper(self, *args):
        """ Main method to buid the all zipper setup.
            Uses the pre-defined and loaded curves.
        """
        print "wip...."
        if self.firstCurve and self.secondCurve:
            if self.origModel:
                self.dpGetCurveDirection()
                self.dpSetCurveDirection(self.firstCurve)
                self.dpSetCurveDirection(self.secondCurve)
                self.dpGenerateMiddleCurve(self.firstCurve)
                self.dpCreateCurveBlendSetup()
                self.dpCreateDeformMesh()
                
                
                
                # WIP -----------------
                
                self.dpGetDeformType()
                if self.deformType == 1:
                    self.dpCreateWireDeform()
                else:
                    self.dpCreateJointSetup()
                
                
                #self.dpSetUsedCurves()
                
            else:
                mel.eval('warning \"'+self.langDic[self.langName]['i191_selectPoly']+'\";')
        else:
            mel.eval('warning \"'+self.langDic[self.langName]['i190_createCurves']+'\";')



# TO DO:
        #
        # orient ctrl zeroOut in motionPath
        # skinning
        # bind pre matrix
        # group all and parent to dpAR
        # clear and organize UI
        # set good button colors
        # create a new zipperCtrl shape
        #


