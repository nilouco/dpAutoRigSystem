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

DPZIP_VERSION = "2.0"


class Zipper():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.upperCurve = None
        self.lowerCurve = None
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
        zipperLayoutA = cmds.rowColumnLayout('zipperLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 160)], parent=zipperLayout)
        cmds.button(label="WIP - Upper >>", command=partial(self.dpCreateCurveFromEdge, "c044_upper"), parent=zipperLayoutA)
        self.upper_TF = cmds.textField('upper_TF', editable=False, parent=zipperLayoutA)
        cmds.button(label="WIP - Lower >>", command=partial(self.dpCreateCurveFromEdge, "c045_lower"), parent=zipperLayoutA)
        self.lower_TF = cmds.textField('lower_TF', editable=False, parent=zipperLayoutA)
        
        self.curveDirectionRB = cmds.radioButtonGrp('curveDirectionRB', label='Curve '+self.langDic[self.langName]['i106_direction'], labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3, select=1, parent=zipperLayout)
        
        cmds.text("WIP - Select a closed edgeLoop and press the run button", parent=zipperLayout)
        cmds.button(label="WIP - RUN - WIP", command=self.dpCreateZipper, backgroundColor=[0.3, 1, 0.7], parent=zipperLayout)
        # check if exists zipper curves and load them:
        self.dpLoadData()
    
    
    
    
    
    
    
    def dpCreateCurveFromEdge(self, zipperId, *args):
        curveName = "dpZipper_"+self.langDic[self.langName][zipperId]+"_Crv"
        edgeList = cmds.ls(selection=True, flatten=True)
        if not edgeList == None and not edgeList == [] and not edgeList == "":
            # clear old curve:
            self.dpDeleteOldCurve(zipperId)
            # create curve:
            baseCurve = cmds.polyToCurve(name=curveName, form=2, degree=3, conformToSmoothMeshPreview=0)[0]
            # rename polyEdgeToCurve node:
            cmds.rename(cmds.listConnections(baseCurve+".create")[0], "dpZipper_"+self.langDic[self.langName][zipperId]+"_PEC")
            # add attributes:
            cmds.addAttr(baseCurve, longName=ZIPPER_ATTR, attributeType='bool')
            cmds.addAttr(baseCurve, longName=ZIPPER_ID, dataType='string')
            cmds.setAttr(baseCurve+"."+ZIPPER_ATTR, 1)
            cmds.setAttr(baseCurve+"."+ZIPPER_ID, zipperId, type="string")
            # load curve data:
            self.dpLoadData(baseCurve)
        else:
            print "WIP - Select edges to build zipper curves from polygon, please.",
    
    
    def dpDeleteOldCurve(self, zipperId, *args):
        print "WIP --- clearing oldCurves"
        transformList = cmds.ls(selection=False, type="transform")
        if transformList:
            for node in transformList:
                if cmds.objExists(node+"."+ZIPPER_ATTR):
                    if cmds.getAttr(node+"."+ZIPPER_ATTR) == 1:
                        if cmds.getAttr(node+"."+ZIPPER_ID) == zipperId:
                            cmds.delete(node)
    
    
    def dpLoadData(self, curveName=None, *args):
        print "WIP --- loading data",
        if curveName:
            zipperId = cmds.getAttr(curveName+"."+ZIPPER_ID)
            self.dpUpdateUI(curveName, zipperId)
        else:
            cmds.textField(self.upper_TF, edit=True, text="")
            cmds.textField(self.lower_TF, edit=True, text="")
            transformList = cmds.ls(selection=False, type="transform")
            if transformList:
                for node in transformList:
                    if cmds.objExists(node+"."+ZIPPER_ATTR):
                        if cmds.getAttr(node+"."+ZIPPER_ATTR) == 1:
                            zipperId = cmds.getAttr(node+"."+ZIPPER_ID)
                            self.dpUpdateUI(node, zipperId)
    
    
    def dpUpdateUI(self, curveName, zipperId, *args):
        print "WIP --- updating UI"
        if zipperId == "c044_upper":
            cmds.textField(self.upper_TF, edit=True, text=curveName)
            self.upperCurve = curveName
        elif zipperId == "c045_lower":
            cmds.textField(self.lower_TF, edit=True, text=curveName)
            self.lowerCurve = curveName
        
        
    def dpGetCurveDirection(self, *args):
        print "wip, change curveDirection",
        selectedItem = cmds.radioButtonGrp(self.curveDirectionRB, query=True, select=True)
        self.curveAxis = selectedItem-1
        if selectedItem == 1:
            self.curveDirection = "X"
        elif selectedItem == 2:
            self.curveDirection = "Y"
        elif selectedItem == 3:
            self.curveDirection = "Z"
        print "self.curveDirection =", self.curveDirection
        return self.curveDirection

    
    def dpCheckCurveDirection(self, curveName, *args):
        cmds.select(curveName+".cv[*]")
        curveLength = len(cmds.ls(selection=True, flatten=True))
        cmds.select(clear=True)
        minPos = cmds.xform(curveName+".cv[0]", query=True, worldSpace=True, translation=True)[self.curveAxis]
        maxPos = cmds.xform(curveName+".cv["+str(curveLength-1)+"]", query=True, worldSpace=True, translation=True)[self.curveAxis]
        if minPos > maxPos:
            cmds.reverseCurve(curveName, constructionHistory=True, replaceOriginal=True)
            cmds.rename(cmds.listConnections(curveName+".create")[0], utils.extractSuffix(curveName)+"_"+self.curveDirection+"_RevC")
    
    
    def dpGenerateMiddleCurve(self, origCurve, *args):
        print "WIP - generating middle curve"
        self.middleCurve = cmds.duplicate(origCurve, name="dpZipper_"+self.langDic[self.langName]['c029_middle']+"_Crv")[0]
        averageCurveNode = cmds.createNode('avgCurves', name="dpZipper_"+self.langDic[self.langName]['c029_middle']+"_AvgC")
        cmds.setAttr(averageCurveNode+".automaticWeight", 0)
        cmds.connectAttr(self.upperCurve+".worldSpace", averageCurveNode+".inputCurve1", force=True)
        cmds.connectAttr(self.lowerCurve+".worldSpace", averageCurveNode+".inputCurve2", force=True)
        cmds.connectAttr(averageCurveNode+".outputCurve", self.middleCurve+".create", force=True)
    
    
    def dpSetUsedCurves(self, *args):
        cmds.setAttr(self.upperCurve+"."+ZIPPER_ATTR, 0)
        cmds.setAttr(self.lowerCurve+"."+ZIPPER_ATTR, 0)
        self.dpLoadData()
        
    
    def dpCreateZipper(self, *args):
        print "wip...."
        self.dpGetCurveDirection()
        self.dpCheckCurveDirection(self.upperCurve)
        self.dpCheckCurveDirection(self.lowerCurve)
        self.dpGenerateMiddleCurve(self.upperCurve)
        #self.dpSetUsedCurves()
        
        
    
    
    
    
    