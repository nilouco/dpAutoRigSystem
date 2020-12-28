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

DPZIP_VERSION = "2.2"


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
        self.firstCurve = None
        self.secondCurve = None
        self.middleCurve = None
        self.curveAxis = 0
        self.curveDirection = "X"
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
        
        self.first_BT = cmds.button('first_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['c114_first']+" "+self.langDic[self.langName]['i189_curve']+" >>", command=partial(self.dpCreateCurveFromEdge, "c114_first"), parent=zipperLayoutA)
        self.first_TF = cmds.textField('first_TF', editable=False, parent=zipperLayoutA)
        self.second_BT = cmds.button('second_BT', label=self.langDic[self.langName]['i187_load']+" "+self.langDic[self.langName]['c115_second']+" "+self.langDic[self.langName]['i189_curve']+" >>", command=partial(self.dpCreateCurveFromEdge, "c115_second"), parent=zipperLayoutA)
        self.second_TF = cmds.textField('second_TF', editable=False, parent=zipperLayoutA)
        
        self.curveDirectionRB = cmds.radioButtonGrp('curveDirectionRB', label='Curve '+self.langDic[self.langName]['i106_direction'], labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3, select=1, changeCommand=self.dpGetCurveDirection, parent=zipperLayout)
        
        cmds.text("WIP - Select a closed edgeLoop and press the run button", parent=zipperLayout)
        cmds.button(label="WIP - RUN - WIP", command=self.dpCreateZipper, backgroundColor=[0.3, 1, 0.7], parent=zipperLayout)
        # check if exists zipper curves and load them:
        self.dpLoadData()
    
    
    def dpCreateCurveFromEdge(self, zipperId, *args):
        """ Create curve from selected polygon edges.
        """
        self.dpGetCurveDirection()
        # declaring names:
        thisName = self.firstName
        if zipperId == "c115_second":
            thisName = self.secondName
        curveName = "dpZipper_"+thisName+"_Crv"
        pecName = "dpZipper_"+thisName+"_PEC"
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
            cmds.button(self.first_BT, edit=True, label=self.firstName+" "+self.langDic[self.langName]['i189_curve'])
            self.firstCurve = curveName
        elif zipperId == "c115_second":
            cmds.textField(self.second_TF, edit=True, text=curveName)
            cmds.button(self.second_BT, edit=True, label=self.secondName+" "+self.langDic[self.langName]['i189_curve'])
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
        self.middleCurve = cmds.duplicate(origCurve, name="dpZipper_"+self.langDic[self.langName]['c029_middle']+"_Crv")[0]
        averageCurveNode = cmds.createNode('avgCurves', name="dpZipper_"+self.langDic[self.langName]['c029_middle']+"_AvgC")
        cmds.setAttr(averageCurveNode+".automaticWeight", 0)
        cmds.connectAttr(self.firstCurve+".worldSpace", averageCurveNode+".inputCurve1", force=True)
        cmds.connectAttr(self.secondCurve+".worldSpace", averageCurveNode+".inputCurve2", force=True)
        cmds.connectAttr(averageCurveNode+".outputCurve", self.middleCurve+".create", force=True)
    
    
    def dpCreateCurveBlendSetup(self, *args):
        print "WIP = creating curve blend setup..."
        
        # declaring names:
        activeAttr = "zipper"+self.langDic[self.langName]['c118_active'].capitalize()
        crescentAttr = "zipper"+self.langDic[self.langName]['c116_crescent']
        decrescentAttr = "zipper"+self.langDic[self.langName]['c117_decrescent']
        
        # create zipper control and attributes:
        self.zipperCtrl = self.ctrls.cvControl('id_074_Zipper', "dpZipper_Ctrl")
        cmds.addAttr(self.zipperCtrl, longName=activeAttr, attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=crescentAttr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipperCtrl, longName=decrescentAttr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        
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
        
        
        
        # WIP --------------------------
        
        
        # calculate iter counter from middle curve length:
        cmds.select(self.middleCurve+".cv[*]")
        curveLength = len(cmds.ls(selection=True, flatten=True))
        
        
        
        # To Do:
        
        # blend crescent side
        # blend decrescent side
        # Add two sides
        # Clamp max value to 1 in order to connect it to the blendShape node
        
    
    
    
        cmds.select(clear=True)
    
    
    
    
    
    
    
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
            self.dpGetCurveDirection()
            self.dpSetCurveDirection(self.firstCurve)
            self.dpSetCurveDirection(self.secondCurve)
            self.dpGenerateMiddleCurve(self.firstCurve)
            self.dpCreateCurveBlendSetup()
            
            #self.dpSetUsedCurves()
        else:
            mel.eval('warning \"'+self.langDic[self.langName]['i190_createCurves']+'\";')




