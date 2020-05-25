# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from dpAutoRigSystem.Modules.Library import dpControls
from dpAutoRigSystem.Modules.Library import dpUtils as utils


class ControlStartClass:
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, CLASS_NAME, TITLE, DESCRIPTION, ICON):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.cvName = None
        self.cvAction = None
        self.cvDegree = None
        self.cvSize = None
        self.cvDirection = None
        self.cvRot = None
        self.cvPointList = None
        self.cvKnotList = None
        self.cvPeriodic = None
        self.controlsGuideDir = 'Controls'
        self.suffix = "Ctrl"
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
    
    
    def getControlUIValues(self, cvName='', *args):
        """ Check and get all UI values to define variables.
            Return them in a list:
            [cvName, cvSize, cvDegree, cvDirection, cvAction]
        """
        # here we will use all info from UI elements in order to call the correct action to do:
        customName = cmds.textFieldGrp(self.dpUIinst.allUIs["controlNameTFG"], query=True, text=True)
        self.cvName = cvName
        if customName:
            self.cvName = customName
        # action
        self.cvAction = cmds.radioButtonGrp(self.dpUIinst.allUIs["controlActionRBG"], query=True, select=True)
        # degree
        degreeRBGValue = cmds.radioButtonGrp(self.dpUIinst.allUIs["degreeRBG"], query=True, select=True)
        self.cvDegree = 1 #linear
        if degreeRBGValue == 2:
            self.cvDegree = 3 #cubic
        # size
        self.cvSize = cmds.floatSliderGrp(self.dpUIinst.allUIs["controlSizeFSG"], query=True, value=True)
        # direction
        self.cvDirection = cmds.optionMenuGrp(self.dpUIinst.allUIs["directionOMG"], query=True, value=True)
        return [self.cvName, self.cvSize, self.cvDegree, self.cvDirection, self.cvAction]
    
    
    def addControlInfo(self, cvNode, className=True, size=True, degree=True, direction=True, rot=True, dpGuide=False, *args):
        """ Add some information in the curve transform node of the control.
        """
        cmds.addAttr(cvNode, longName="dpControl", attributeType='bool')
        cmds.setAttr(cvNode+".dpControl", 1)
        if dpGuide:
            cmds.addAttr(cvNode, longName="dpGuide", attributeType='bool')
            cmds.setAttr(cvNode+".dpGuide", 1)
        cmds.addAttr(cvNode, longName="version", dataType='string')
        cmds.setAttr(cvNode+".version", self.dpUIinst.dpARVersion, type="string")
        if self.cvID:
            cmds.addAttr(cvNode, longName="controlID", dataType='string')
            cmds.setAttr(cvNode+".controlID", self.cvID, type="string")
        if className:
            cmds.addAttr(cvNode, longName="className", dataType='string')
            cmds.setAttr(cvNode+".className", self.guideModuleName, type="string")
        if size:
            cmds.addAttr(cvNode, longName="size", attributeType='float')
            cmds.setAttr(cvNode+".size", self.cvSize)
        if degree:
            cmds.addAttr(cvNode, longName="degree", attributeType='short')
            cmds.setAttr(cvNode+".degree", self.cvDegree)
        if direction:
            cmds.addAttr(cvNode, longName="direction", dataType='string')
            cmds.setAttr(cvNode+".direction", self.cvDirection, type="string")
        if rot:
            cmds.addAttr(cvNode, longName="cvRotX", attributeType='double')
            cmds.addAttr(cvNode, longName="cvRotY", attributeType='double')
            cmds.addAttr(cvNode, longName="cvRotZ", attributeType='double')
            cmds.setAttr(cvNode+".cvRotX", self.cvRot[0])
            cmds.setAttr(cvNode+".cvRotY", self.cvRot[1])
            cmds.setAttr(cvNode+".cvRotZ", self.cvRot[2])
    
    
    def createCurve(self, cvName, cvDegree, cvPointList, cvKnot, cvPeriodic, dpGuide, *args):
        """ Create and return a simple curve using given parameters.
        """
        cvCurve = cmds.curve(name=cvName, point=cvPointList, degree=cvDegree, knot=cvKnot, periodic=cvPeriodic)
        self.addControlInfo(cvCurve, dpGuide=dpGuide)
        self.ctrls.renameShape([cvCurve])
        return cvCurve
    
    
    def combineCurves(self, curveList, *args):
        """ Combine all guiven curve to just one main curve and return it.
        """
        mainCurve = curveList[0]
        cmds.makeIdentity(mainCurve, translate=True, rotate=True, scale=True, apply=True)
        for item in curveList[1:]:
            cmds.makeIdentity(item, translate=True, rotate=True, scale=True, apply=True)
            self.ctrls.transferShape(True, False, item, [mainCurve])
        cmds.setAttr(mainCurve+".className", self.guideModuleName, type="string")
        return mainCurve
        
    
    def setControlDirection(self, cvNode, cvDirection, *args):
        """ Rotate the node given to have the correct direction orientation.
        """
        if cvDirection == "-X":
            cmds.setAttr(cvNode+".rotateX", 90)
            cmds.setAttr(cvNode+".rotateY", -90)
        elif cvDirection == "+X":
            cmds.setAttr(cvNode+".rotateX", -90)
            cmds.setAttr(cvNode+".rotateY", -90)
        elif cvDirection == "-Y":
            cmds.setAttr(cvNode+".rotateZ", 180)
        elif cvDirection == "-Z":
            cmds.setAttr(cvNode+".rotateX", -90)
        elif cvDirection == "+Z":
            cmds.setAttr(cvNode+".rotateX", 90)
        else:
            pass #default +Y, just pass
        cmds.makeIdentity(cvNode, rotate=True, apply=True)
        # rotate and freezeTransformation from given cvRot vector:
        cmds.rotate(self.cvRot[0], self.cvRot[1], self.cvRot[2], self.cvCurve)
        cmds.makeIdentity(self.cvCurve, rotate=True, apply=True)
    
    
    def doControlAction(self, destinationList, *args):
        """ Action to do when creating a control
            Do action as user wants:
                1 = New control
                2 = Add shape
                3 = Replace shapes
        """
        if self.cvAction == 1: #new control
            pass
        else:
            if destinationList:
                if self.cvAction == 2: #add shape
                    self.ctrls.transferShape(True, False, self.cvCurve, destinationList, True)
                elif self.cvAction == 3: #replace shapes
                    self.ctrls.transferShape(True, True, self.cvCurve, destinationList, True)
            else:
                cmds.delete(self.cvCurve)
                mel.eval("warning \""+self.langDic[self.langName]['e011_notSelShape']+"\";")
    
    
    def cvCreate(self, useUI, cvID, cvName='Control_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, combine=False, *args):
        """ Check if we need to get parameters from UI.
            Create a respective curve shape.
            Return the transform curve or a list of selected destination items.
        """
        # getting current selection:
        destinationList = cmds.ls(selection=True, type="transform")
        # check if the given name is good or add a sequencial number on it:
        self.cvName = utils.validateName(cvName, self.suffix)
        self.cvID = cvID
        self.cvSize = cvSize
        self.cvDegree = cvDegree
        self.cvDirection = cvDirection
        self.cvRot = cvRot
        self.cvAction = cvAction
        # getting UI info:
        if useUI:
            self.getControlUIValues(self.cvName)
        
        # combine or create curve using the parameters:
        if combine:
            self.cvCurve = self.generateCombineCurves(useUI, self.cvID, self.cvName, self.cvSize, self.cvDegree, self.cvDirection)
        else:
            # getting curve info to be created based on choose degree:
            if self.cvDegree == 1: #linear
                self.getLinearPoints()
            else: #cubic
                self.getCubicPoints()
            self.cvCurve = self.createCurve(self.cvName, self.cvDegree, self.cvPointList, self.cvKnotList, self.cvPeriodic, dpGuide)
        # set control direction for the control curve:
        self.setControlDirection(self.cvCurve, self.cvDirection)
        
        # working about action to do, like new control, add shape or replace shapes:
        self.doControlAction(destinationList)
        # select the result node and return it
        if self.cvAction == 1: #new control
            cmds.select(self.cvCurve)
            return self.cvCurve
        elif destinationList:
            cmds.select(destinationList)
            return destinationList