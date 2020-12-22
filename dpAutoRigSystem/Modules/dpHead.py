# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Head"
TITLE = "m017_head"
DESCRIPTION = "m018_headDesc"
ICON = "/Icons/dp_head.png"


class Head(Base.StartClass, Layout.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 1)
        # create cvJointLoc and cvLocators:
        self.cvNeckLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Neck", r=0.5, d=1, rot=(-90, 90, 0), guide=True)
        self.cvHeadLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Head", r=0.4, d=1, guide=True)
        self.cvJawLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_Jaw", r=0.3, d=1, guide=True)
        self.cvChinLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Chin", r=0.3, d=1, guide=True)
        self.cvChewLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Chew", r=0.3, d=1, guide=True)
        self.cvLCornerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_LCornerLip", r=0.1, d=1, guide=True)
        self.cvRCornerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RCornerLip", r=0.1, d=1, guide=True)
        self.cvUpperJawLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_UpperJaw", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.cvUpperLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_UpperLip", r=0.15, d=1, guide=True)
        self.cvLowerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_LowerLip", r=0.15, d=1, guide=True)
        # create jointGuides:
        self.jGuideNeck = cmds.joint(name=self.guideName+"_JGuideNeck", radius=0.001)
        self.jGuideHead = cmds.joint(name=self.guideName+"_JGuideHead", radius=0.001)
        self.jGuideUpperJaw = cmds.joint(name=self.guideName+"_jGuideUpperJaw", radius=0.001)
        self.jGuideUpperLip = cmds.joint(name=self.guideName+"_jGuideUpperLip", radius=0.001)
        cmds.select(self.jGuideHead)
        self.jGuideJaw  = cmds.joint(name=self.guideName+"_JGuideJaw", radius=0.001)
        self.jGuideChin = cmds.joint(name=self.guideName+"_JGuideChin", radius=0.001)
        self.jGuideChew = cmds.joint(name=self.guideName+"_JGuideChew", radius=0.001)
        cmds.select(self.jGuideChin)
        self.jGuideLowerLip = cmds.joint(name=self.guideName+"_jGuideLowerLip", radius=0.001)
        cmds.select(self.jGuideJaw)
        self.jGuideLLip = cmds.joint(name=self.guideName+"_jGuideLLip", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideNeck+".template", 1)
        cmds.setAttr(self.jGuideHead+".template", 1)
        cmds.setAttr(self.jGuideUpperJaw+".template", 1)
        cmds.setAttr(self.jGuideJaw+".template", 1)
        cmds.setAttr(self.jGuideChin+".template", 1)
        cmds.setAttr(self.jGuideChew+".template", 1)
        cmds.setAttr(self.jGuideUpperLip+".template", 1)
        cmds.setAttr(self.jGuideLowerLip+".template", 1)
        cmds.parent(self.jGuideNeck, self.moduleGrp, relative=True)
        # create cvEnd:
        cmds.select(self.jGuideChew)
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvChewLoc)
        cmds.setAttr(self.cvEndJoint+".tz", self.ctrls.dpCheckLinearUnit(0.6))
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideChew)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvNeckLoc, self.jGuideNeck, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvHeadLoc, self.jGuideHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperJawLoc, self.jGuideUpperJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvJawLoc, self.jGuideJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChinLoc, self.jGuideChin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChewLoc, self.jGuideChew, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperLipLoc, self.jGuideUpperLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLowerLipLoc, self.jGuideLowerLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLCornerLipLoc, self.jGuideLLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
        cmds.setAttr(self.cvNeckLoc+".rotateZ", 90)
        cmds.makeIdentity(self.cvNeckLoc, rotate=True, apply=False)
        cmds.setAttr(self.cvHeadLoc+".translateY", 2)
        cmds.setAttr(self.cvUpperJawLoc+".translateY", 3.5)
        cmds.setAttr(self.cvUpperJawLoc+".translateZ", 0.25)
        cmds.setAttr(self.cvJawLoc+".translateY", 2.7)
        cmds.setAttr(self.cvJawLoc+".translateZ", 0.7)
        cmds.setAttr(self.cvChinLoc+".translateY", 2.5)
        cmds.setAttr(self.cvChinLoc+".translateZ", 1.0)
        cmds.setAttr(self.cvChewLoc+".translateY", 2.3)
        cmds.setAttr(self.cvChewLoc+".translateZ", 1.3)
        # lip cvLocs:
        cmds.setAttr(self.cvUpperLipLoc+".translateY", 2.9)
        cmds.setAttr(self.cvUpperLipLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvLowerLipLoc+".translateY", 2.3)
        cmds.setAttr(self.cvLowerLipLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvLCornerLipLoc+".translateX", 0.6)
        cmds.setAttr(self.cvLCornerLipLoc+".translateY", 2.6)
        cmds.setAttr(self.cvLCornerLipLoc+".translateZ", 3.4)
        self.lipMD = cmds.createNode("multiplyDivide", name=self.guideName+"_Lip_MD")
        cmds.connectAttr(self.cvLCornerLipLoc+".translateX", self.lipMD+".input1X", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".translateY", self.lipMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".translateZ", self.lipMD+".input1Z", force=True)
        cmds.connectAttr(self.lipMD+".outputX", self.cvRCornerLipLoc+".translateX", force=True)
        cmds.connectAttr(self.lipMD+".outputY", self.cvRCornerLipLoc+".translateY", force=True)
        cmds.connectAttr(self.lipMD+".outputZ", self.cvRCornerLipLoc+".translateZ", force=True)
        cmds.setAttr(self.lipMD+".input2X", -1)
        cmds.setAttr(self.cvRCornerLipLoc+".template", 1)
        # make parenting between cvLocs:
        cmds.parent(self.cvNeckLoc, self.moduleGrp)
        cmds.parent(self.cvHeadLoc, self.cvNeckLoc)
        cmds.parent(self.cvUpperJawLoc, self.cvJawLoc, self.cvHeadLoc)
        cmds.parent(self.cvChinLoc, self.cvJawLoc)
        cmds.parent(self.cvChewLoc, self.cvLowerLipLoc, self.cvChinLoc)
        cmds.parent(self.cvLCornerLipLoc, self.cvJawLoc)
        cmds.parent(self.cvRCornerLipLoc, self.cvJawLoc)
        cmds.parent(self.cvUpperLipLoc, self.cvUpperJawLoc)
    
    
    def setupJawMove(self, attrCtrl, openCloseID, positiveRotation=True, axis="Y", intAttrID="c049_intensity", invertRot=False, createOutput=False, fixValue=0.01, *args):
        """ Create the setup for move jaw group when jaw control rotates for open or close adjustements.
            Depends on axis and rotation done.
        """
        # declaring naming:
        attrBaseName = utils.extractSuffix(attrCtrl)
        drivenGrp = attrBaseName+"_"+self.langDic[self.langName][openCloseID]+self.langDic[self.langName]['c034_move']+"_Grp"
        # attribute names:
        intAttrName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName][intAttrID].capitalize()+axis
        startRotName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c110_start'].capitalize()+"Rotation"
        unitFixAttrName = self.langDic[self.langName][openCloseID].lower()+"UnitFix"+axis
        calibAttrName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c111_calibrate']+axis
        calibOutputAttrName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c111_calibrate']+self.langDic[self.langName]['c112_output']
        outputAttrName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c112_output']
        # utility node names:
        jawCalibrateMDName = attrBaseName+self.langDic[self.langName][openCloseID]+"_"+self.langDic[self.langName][intAttrID].capitalize()+"_"+self.langDic[self.langName]['c111_calibrate']+"_"+axis+"_MD"
        jawUnitFixMDName = attrBaseName+self.langDic[self.langName][openCloseID]+"_UnitFix_"+axis+"_MD"
        jawIntMDName = attrBaseName+self.langDic[self.langName][openCloseID]+"_"+self.langDic[self.langName][intAttrID].capitalize()+"_"+axis+"_MD"
        jawStartMDName = attrBaseName+self.langDic[self.langName][openCloseID]+"_Start_"+axis+"_MD"
        jawIntPMAName = attrBaseName+self.langDic[self.langName][openCloseID]+"_"+self.langDic[self.langName][intAttrID].capitalize()+"_Start_"+axis+"_PMA"
        jawIntCndName = attrBaseName+self.langDic[self.langName][openCloseID]+"_"+self.langDic[self.langName][intAttrID].capitalize()+"_"+axis+"_Cnd"
        jawOutputRmVName = attrBaseName+self.langDic[self.langName][openCloseID]+"_"+self.langDic[self.langName]['c112_output']+"_RmV"
        
        # create move group and its attributes:
        if not cmds.objExists(drivenGrp):
            drivenGrp = cmds.group(attrCtrl, name=drivenGrp)
        if not cmds.objExists(self.jawCtrl+"."+startRotName):
            if positiveRotation: #open
                cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=0, minValue=0, keyable=True)
            else: #close
                cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=0, maxValue=0, keyable=True)
            cmds.setAttr(self.jawCtrl+"."+startRotName, keyable=False, channelBox=True)
        if not cmds.objExists(attrCtrl+"."+unitFixAttrName):
            if positiveRotation: #open
                cmds.addAttr(attrCtrl, longName=unitFixAttrName, attributeType='float', defaultValue=fixValue)
            else:
                cmds.addAttr(attrCtrl, longName=unitFixAttrName, attributeType='float', defaultValue=-fixValue)
            cmds.setAttr(attrCtrl+"."+unitFixAttrName, lock=True)
        if not cmds.objExists(attrCtrl+"."+calibAttrName):
            cmds.addAttr(attrCtrl, longName=calibAttrName, attributeType='float', defaultValue=1)
        if not cmds.objExists(attrCtrl+"."+intAttrName):
            cmds.addAttr(attrCtrl, longName=intAttrName, attributeType='float', defaultValue=1, keyable=True)
            cmds.setAttr(attrCtrl+"."+intAttrName, keyable=False, channelBox=True)
        
        # create utility nodes:
        jawCalibrateMD = cmds.createNode('multiplyDivide', name=jawCalibrateMDName)
        jawUnitFixMD = cmds.createNode('multiplyDivide', name=jawUnitFixMDName)
        jawIntMD = cmds.createNode('multiplyDivide', name=jawIntMDName)
        jawStartMD = cmds.createNode('multiplyDivide', name=jawStartMDName)
        jawIntPMA = cmds.createNode('plusMinusAverage', name=jawIntPMAName)
        jawIntCnd = cmds.createNode('condition', name=jawIntCndName)
        
        # set attributes to move jaw group when open or close:
        cmds.setAttr(jawIntPMA+".operation", 2) #substract
        cmds.setAttr(jawIntCnd+".operation", 4) #less than
        if positiveRotation: #open
            cmds.setAttr(jawIntCnd+".operation", 2) #greater than
        cmds.setAttr(jawIntCnd+".colorIfFalseR", 0)
        
        # connect utility nodes:
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntMD+".input1"+axis, force=True)
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntCnd+".firstTerm", force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawStartMD+".input2"+axis, force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawIntCnd+".secondTerm", force=True)
        cmds.connectAttr(attrCtrl+"."+intAttrName, jawCalibrateMD+".input1"+axis, force=True)
        cmds.connectAttr(attrCtrl+"."+calibAttrName, jawCalibrateMD+".input2"+axis, force=True)
        cmds.connectAttr(attrCtrl+"."+unitFixAttrName, jawUnitFixMD+".input2"+axis, force=True)
        cmds.connectAttr(jawCalibrateMD+".output"+axis, jawUnitFixMD+".input1"+axis, force=True)
        cmds.connectAttr(jawUnitFixMD+".output"+axis, jawIntMD+".input2"+axis, force=True)
        cmds.connectAttr(jawUnitFixMD+".output"+axis, jawStartMD+".input1"+axis, force=True)
        cmds.connectAttr(jawIntMD+".output"+axis, jawIntPMA+".input1D[0]", force=True)
        cmds.connectAttr(jawStartMD+".output"+axis, jawIntPMA+".input1D[1]", force=True)
        cmds.connectAttr(jawIntPMA+".output1D", jawIntCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(jawIntCnd+".outColorR", drivenGrp+".translate"+axis, force=True)
        
        # invert rotation for lower lip exception:
        if invertRot:
            invetRotPMAName = attrBaseName+self.langDic[self.langName][openCloseID]+self.langDic[self.langName][intAttrID].capitalize()+"_"+axis+"_InvertRot_PMA"
            invetRotMDName = attrBaseName+self.langDic[self.langName][openCloseID]+self.langDic[self.langName][intAttrID].capitalize()+"_"+axis+"_InvertRot_MD"
            invetRotPMA = cmds.createNode('plusMinusAverage', name=invetRotPMAName)
            invetRotMD = cmds.createNode('multiplyDivide', name=invetRotMDName)
            cmds.setAttr(invetRotPMA+".operation", 2) #substract
            cmds.setAttr(invetRotMD+".input2X", -1)
            cmds.setAttr(jawIntCnd+".colorIfFalseG", 0)
            cmds.connectAttr(self.jawCtrl+".rotateX", invetRotPMA+".input1D[0]", force=True)
            cmds.connectAttr(self.jawCtrl+"."+startRotName, invetRotPMA+".input1D[1]", force=True)
            cmds.connectAttr(invetRotPMA+".output1D", jawIntCnd+".colorIfTrueG", force=True)
            cmds.connectAttr(jawIntCnd+".outColorG", invetRotMD+".input1X", force=True)
            cmds.connectAttr(invetRotMD+".outputX", drivenGrp+".rotateX", force=True)
            
        # output to a blendShape target value setup:
        if createOutput:
            if not cmds.objExists(self.jawCtrl+"."+outputAttrName):
                cmds.addAttr(self.jawCtrl, longName=calibOutputAttrName, attributeType='float', defaultValue=1)
                cmds.addAttr(self.jawCtrl, longName=outputAttrName, attributeType='float', defaultValue=1)
            jawOutputRmV = cmds.createNode('remapValue', name=jawOutputRmVName)
            cmds.connectAttr(self.jawCtrl+".rotateX", jawOutputRmV+".inputValue", force=True)
            cmds.connectAttr(self.jawCtrl+"."+calibOutputAttrName, jawOutputRmV+".inputMax", force=True)
            cmds.connectAttr(jawOutputRmV+".outValue", self.jawCtrl+"."+outputAttrName, force=True)
            cmds.setAttr(self.jawCtrl+"."+outputAttrName, lock=True)
    
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            # declare lists to store names and attributes:
            self.worldRefList, self.upperJawCtrlList = [], []
            self.aCtrls, self.aLCtrls, self.aRCtrls = [], [], []
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [ self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_' ]
                for s, side in enumerate(sideList):
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_Guide_Base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # redeclaring variables:
                self.base       = side+self.userGuideName+"_Guide_Base"
                self.cvNeckLoc  = side+self.userGuideName+"_Guide_Neck"
                self.cvHeadLoc  = side+self.userGuideName+"_Guide_Head"
                self.cvUpperJawLoc = side+self.userGuideName+"_Guide_UpperJaw"
                self.cvJawLoc   = side+self.userGuideName+"_Guide_Jaw"
                self.cvChinLoc  = side+self.userGuideName+"_Guide_Chin"
                self.cvChewLoc  = side+self.userGuideName+"_Guide_Chew"
                self.cvLCornerLipLoc  = side+self.userGuideName+"_Guide_LCornerLip"
                self.cvRCornerLipLoc  = side+self.userGuideName+"_Guide_RCornerLip"
                self.cvUpperLipLoc  = side+self.userGuideName+"_Guide_UpperLip"
                self.cvLowerLipLoc  = side+self.userGuideName+"_Guide_LowerLip"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                
                # generating naming:
                neckJntName = side+self.userGuideName+"_00_"+self.langDic[self.langName]['c023_neck']+"_Jnt"
                headJxtName = side+self.userGuideName+"_"+self.langDic[self.langName]['c024_head']+"_Jxt"
                headJntName = side+self.userGuideName+"_01_"+self.langDic[self.langName]['c024_head']+"_Jnt"
                if self.addArticJoint:
                    headJntName = side+self.userGuideName+"_02_"+self.langDic[self.langName]['c024_head']+"_Jnt"
                upperJawJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw']+"_Jnt"
                upperEndJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw']+"_JEnd"
                jawJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c025_jaw']+"_Jnt"
                chinJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c026_chin']+"_Jnt"
                chewJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c048_chew']+"_Jnt"
                endJntName = side+self.userGuideName+"_JEnd"
                lCornerLipJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c043_corner']+self.langDic[self.langName]['c039_lip']+"_Jnt"
                rCornerLipJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c043_corner']+self.langDic[self.langName]['c039_lip']+"_Jnt"
                upperLipJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c039_lip']+"_Jnt"
                lowerLipJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c045_lower']+self.langDic[self.langName]['c039_lip']+"_Jnt"
                neckCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c023_neck']+"_Ctrl"
                headCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c024_head']+"_Ctrl"
                upperJawCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw']+"_Ctrl"
                jawCtrlName  = side+self.userGuideName+"_"+self.langDic[self.langName]['c025_jaw']+"_Ctrl"
                chinCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c026_chin']+"_Ctrl"
                chewCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c048_chew']+"_Ctrl"
                lCornerLipCtrlName = self.langDic[self.langName]['p002_left']+"_"+self.userGuideName+"_"+self.langDic[self.langName]['c043_corner']+self.langDic[self.langName]['c039_lip']+"_Ctrl"
                rCornerLipCtrlName = self.langDic[self.langName]['p003_right']+"_"+self.userGuideName+"_"+self.langDic[self.langName]['c043_corner']+self.langDic[self.langName]['c039_lip']+"_Ctrl"
                upperLipCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c039_lip']+"_Ctrl"
                lowerLipCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c045_lower']+self.langDic[self.langName]['c039_lip']+"_Ctrl"
                
                # creating joints:
                self.neckJnt = cmds.joint(name=neckJntName)
                self.headJxt = cmds.joint(name=headJxtName)
                cmds.select(clear=True)
                self.headJnt = cmds.joint(name=headJntName, scaleCompensate=False)
                self.upperJawJnt = cmds.joint(name=upperJawJntName, scaleCompensate=False)
                self.upperEndJnt = cmds.joint(name=upperEndJntName, scaleCompensate=False, radius=0.5)
                cmds.setAttr(self.upperEndJnt+".translateY", 0.3*self.ctrlRadius)
                cmds.select(self.headJnt)
                self.jawJnt  = cmds.joint(name=jawJntName, scaleCompensate=False)
                self.chinJnt = cmds.joint(name=chinJntName, scaleCompensate=False)
                self.chewJnt = cmds.joint(name=chewJntName, scaleCompensate=False)
                self.endJnt  = cmds.joint(name=endJntName, scaleCompensate=False, radius=0.5)
                cmds.select(clear=True)
                self.lCornerLipJnt = cmds.joint(name=lCornerLipJntName, scaleCompensate=False)
                cmds.select(clear=True)
                self.rCornerLipJnt = cmds.joint(name=rCornerLipJntName, scaleCompensate=False)
                cmds.select(self.upperJawJnt)
                self.upperLipJnt = cmds.joint(name=upperLipJntName, scaleCompensate=False)
                cmds.select(self.chinJnt)
                self.lowerLipJnt = cmds.joint(name=lowerLipJntName, scaleCompensate=False)
                cmds.select(clear=True)
                dpARJointList = [self.neckJnt, self.headJnt, self.upperJawJnt, self.jawJnt, self.chinJnt, self.chewJnt, self.lCornerLipJnt, self.rCornerLipJnt, self.upperLipJnt, self.lowerLipJnt]
                for dpARJoint in dpARJointList:
                    cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                utils.setJointLabel(self.neckJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c023_neck'])
                utils.setJointLabel(self.headJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c024_head'])
                utils.setJointLabel(self.upperJawJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw'])
                utils.setJointLabel(self.jawJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c025_jaw'])
                utils.setJointLabel(self.chinJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c026_chin'])
                utils.setJointLabel(self.chewJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c048_chew'])
                utils.setJointLabel(self.lCornerLipJnt, 1, 18, self.userGuideName+"_"+self.langDic[self.langName]['c039_lip'])
                utils.setJointLabel(self.rCornerLipJnt, 2, 18, self.userGuideName+"_"+self.langDic[self.langName]['c039_lip'])
                utils.setJointLabel(self.upperLipJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c039_lip'])
                utils.setJointLabel(self.lowerLipJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c045_lower']+self.langDic[self.langName]['c039_lip'])
                # creating controls:
                self.neckCtrl = self.ctrls.cvControl("id_022_HeadNeck", ctrlName=neckCtrlName, r=(self.ctrlRadius * 1.5), d=self.curveDegree, dir="-Z")
                self.headCtrl = self.ctrls.cvControl("id_023_HeadHead", ctrlName=headCtrlName, r=(self.ctrlRadius * 2.5), d=self.curveDegree)
                self.upperJawCtrl = self.ctrls.cvControl("id_069_HeadUpperJaw", ctrlName=upperJawCtrlName, r=self.ctrlRadius, d=self.curveDegree)
                self.jawCtrl  = self.ctrls.cvControl("id_024_HeadJaw", ctrlName=jawCtrlName, r=self.ctrlRadius, d=self.curveDegree)
                self.chinCtrl = self.ctrls.cvControl("id_025_HeadChin", ctrlName=chinCtrlName, r=(self.ctrlRadius * 0.2), d=self.curveDegree)
                self.chewCtrl = self.ctrls.cvControl("id_026_HeadChew", ctrlName=chewCtrlName, r=(self.ctrlRadius * 0.15), d=self.curveDegree)
                self.lCornerLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=lCornerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                self.rCornerLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=rCornerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                self.upperLipCtrl = self.ctrls.cvControl("id_072_HeadUpperLip", ctrlName=upperLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                self.lowerLipCtrl = self.ctrls.cvControl("id_073_HeadLowerLip", ctrlName=lowerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                self.upperJawCtrlList.append(self.upperJawCtrl)
                self.aCtrls.append([self.neckCtrl, self.headCtrl, self.upperJawCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.upperLipCtrl, self.lowerLipCtrl])
                self.aLCtrls.append([self.lCornerLipCtrl])
                self.aRCtrls.append([self.rCornerLipCtrl])
                
                # optimize control CV shapes:
                tempHeadCluster = cmds.cluster(self.headCtrl)[1]
                cmds.setAttr(tempHeadCluster+".translateY", -0.5)
                tempJawCluster = cmds.cluster(self.jawCtrl)[1]
                cmds.setAttr(tempJawCluster+".translateY", -2)
                cmds.setAttr(tempJawCluster+".translateZ", 2.1)
                tempChinCluster = cmds.cluster(self.chinCtrl)[1]
                cmds.setAttr(tempChinCluster+".translateY", -1.4)
                cmds.setAttr(tempChinCluster+".translateZ", 3.6)
                cmds.setAttr(tempChinCluster+".rotateX", 22)
                tempChewCluster = cmds.cluster(self.chewCtrl)[1]
                cmds.setAttr(tempChewCluster+".translateY", -1.35)
                cmds.setAttr(tempChewCluster+".translateZ", 3.6)
                cmds.setAttr(tempChewCluster+".rotateX", 22)
                cmds.delete([self.headCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl], constructionHistory=True)
                
                #Setup Axis Order
                if self.rigType == Base.RigType.quadruped:
                    cmds.setAttr(self.neckCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.upperJawCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 1)
                    cmds.rotate(90, 0, 0, self.neckCtrl)
                    cmds.makeIdentity(self.neckCtrl, apply=True, rotate=True)
                else:
                    cmds.setAttr(self.neckCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.upperJawCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 3)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.neckCtrl, attrString=self.base+";"+self.cvNeckLoc+";"+self.radiusGuide)
                utils.originedFrom(objName=self.headCtrl, attrString=self.cvHeadLoc)
                utils.originedFrom(objName=self.upperJawCtrl, attrString=self.cvUpperJawLoc)
                utils.originedFrom(objName=self.jawCtrl, attrString=self.cvJawLoc)
                utils.originedFrom(objName=self.chinCtrl, attrString=self.cvChinLoc)
                utils.originedFrom(objName=self.chewCtrl, attrString=self.cvChewLoc+";"+self.cvEndJoint)
                utils.originedFrom(objName=self.lCornerLipCtrl, attrString=self.cvLCornerLipLoc)
                utils.originedFrom(objName=self.rCornerLipCtrl, attrString=self.cvRCornerLipLoc)
                utils.originedFrom(objName=self.upperLipCtrl, attrString=self.cvUpperLipLoc)
                utils.originedFrom(objName=self.lowerLipCtrl, attrString=self.cvLowerLipLoc)
                
                # edit the mirror shape to a good direction of controls:
                ctrlList = [self.neckCtrl, self.headCtrl, self.upperJawCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl]
                if s == 1:
                    for ctrl in ctrlList:
                        if self.mirrorAxis == 'X':
                            cmds.setAttr(ctrl+'.rotateY', 180)
                        elif self.mirrorAxis == 'Y':
                            cmds.setAttr(ctrl+'.rotateY', 180)
                        elif self.mirrorAxis == 'Z':
                            cmds.setAttr(ctrl+'.rotateX', 180)
                            cmds.setAttr(ctrl+'.rotateZ', 180)
                        elif self.mirrorAxis == 'XYZ':
                            cmds.setAttr(ctrl+'.rotateX', 180)
                            cmds.setAttr(ctrl+'.rotateZ', 180)
                    cmds.makeIdentity(ctrlList, apply=True, translate=False, rotate=True, scale=False)

                # temporary parentConstraints:
                cmds.delete(cmds.parentConstraint(self.cvNeckLoc, self.neckCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvHeadLoc, self.headCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperJawLoc, self.upperJawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvJawLoc, self.jawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChinLoc, self.chinCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChewLoc, self.chewCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLCornerLipLoc, self.lCornerLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvRCornerLipLoc, self.rCornerLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperLipLoc, self.upperLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLowerLipLoc, self.lowerLipCtrl, maintainOffset=False))
                
                # zeroOut controls:
                self.zeroCornerLipCtrlList = utils.zeroOut([self.lCornerLipCtrl, self.rCornerLipCtrl])
                self.lLipGrp = cmds.group(self.lCornerLipCtrl, name=self.lCornerLipCtrl+"_Grp")
                self.rLipGrp = cmds.group(self.rCornerLipCtrl, name=self.rCornerLipCtrl+"_Grp")
                cmds.setAttr(self.rLipGrp+".scaleX", -1)
                self.zeroCtrlList = utils.zeroOut([self.neckCtrl, self.headCtrl, self.upperJawCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.zeroCornerLipCtrlList[0], self.zeroCornerLipCtrlList[1], self.upperLipCtrl, self.lowerLipCtrl])

                # make joints be ride by controls:
                cmds.makeIdentity(self.neckJnt, self.headJxt, self.headJnt, self.jawJnt, self.chinJnt, self.chewJnt, self.endJnt, rotate=True, apply=True)
                cmds.parentConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_PaC")
                cmds.scaleConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_ScC")
                cmds.delete(cmds.parentConstraint(self.headCtrl, self.headJxt, maintainOffset=False))
                cmds.parentConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_PaC")
                cmds.parentConstraint(self.upperJawCtrl, self.upperJawJnt, maintainOffset=False, name=self.upperJawJnt+"_PaC")
                cmds.parentConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_PaC")
                cmds.parentConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_PaC")
                cmds.parentConstraint(self.chewCtrl, self.chewJnt, maintainOffset=False, name=self.chewJnt+"_PaC")
                cmds.parentConstraint(self.lCornerLipCtrl, self.lCornerLipJnt, maintainOffset=False, name=self.lCornerLipJnt+"_PaC")
                cmds.parentConstraint(self.rCornerLipCtrl, self.rCornerLipJnt, maintainOffset=False, name=self.rCornerLipJnt+"_PaC")
                cmds.parentConstraint(self.upperLipCtrl, self.upperLipJnt, maintainOffset=False, name=self.upperLipJnt+"_PaC")
                cmds.parentConstraint(self.lowerLipCtrl, self.lowerLipJnt, maintainOffset=False, name=self.lowerLipJnt+"_PaC")
                cmds.scaleConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_ScC")
                cmds.scaleConstraint(self.upperJawCtrl, self.upperJawJnt, maintainOffset=False, name=self.upperJawJnt+"_ScC")
                cmds.scaleConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_ScC")
                cmds.scaleConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_ScC")
                cmds.scaleConstraint(self.chewCtrl, self.chewJnt, maintainOffset=False, name=self.chewJnt+"_ScC")
                cmds.scaleConstraint(self.lCornerLipCtrl, self.lCornerLipJnt, maintainOffset=False, name=self.lCornerLipJnt+"_ScC")
                cmds.scaleConstraint(self.rCornerLipCtrl, self.rCornerLipJnt, maintainOffset=False, name=self.rCornerLipJnt+"_ScC")
                cmds.scaleConstraint(self.upperLipCtrl, self.upperLipJnt, maintainOffset=False, name=self.upperLipJnt+"_ScC")
                cmds.scaleConstraint(self.lowerLipCtrl, self.lowerLipJnt, maintainOffset=False, name=self.lowerLipJnt+"_ScC")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False))
                
                # create interations between neck and head:
                self.grpNeck = cmds.group(self.zeroCtrlList[0], name=self.neckCtrl+"_Grp")
                self.grpHeadA = cmds.group(empty=True, name=self.headCtrl+"_A_Grp")
                self.grpHead = cmds.group(self.grpHeadA, name=self.headCtrl+"_Grp")
                # arrange pivots:
                self.neckPivot = cmds.xform(self.neckCtrl, query=True, worldSpace=True, translation=True)
                self.headPivot = cmds.xform(self.headCtrl, query=True, worldSpace=True, translation=True)
                cmds.xform(self.grpNeck, pivots=(self.neckPivot[0], self.neckPivot[1], self.neckPivot[2]))
                cmds.xform(self.grpHead, self.grpHeadA, pivots=(self.headPivot[0], self.headPivot[1], self.headPivot[2]))
                
                self.worldRef = cmds.group(empty=True, name=side+self.userGuideName+"_WorldRef_Grp")
                self.worldRefList.append(self.worldRef)
                cmds.delete(cmds.parentConstraint(self.neckCtrl, self.worldRef, maintainOffset=False))
                cmds.parentConstraint(self.neckCtrl, self.grpHeadA, maintainOffset=True, skipRotate=["x", "y", "z"], name=self.grpHeadA+"_PaC")
                orientConst = cmds.orientConstraint(self.neckCtrl, self.worldRef, self.grpHeadA, maintainOffset=False, name=self.grpHeadA+"_OrC")[0]
                cmds.scaleConstraint(self.neckCtrl, self.grpHeadA, maintainOffset=True, name=self.grpHeadA+"_ScC")
                cmds.parent(self.zeroCtrlList[1], self.grpHeadA, absolute=True)

                # connect reverseNode:
                cmds.addAttr(self.headCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType='float', minValue=0, maxValue=1, keyable=True)
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c032_follow'], orientConst+"."+self.neckCtrl+"W0", force=True)
                self.headRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_Rev")
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c032_follow'], self.headRevNode+".inputX", force=True)
                cmds.connectAttr(self.headRevNode+'.outputX', orientConst+"."+self.worldRef+"W1", force=True)
                
                # setup neck autoRotate:
                self.neckOrientGrp = cmds.group(self.neckCtrl, name=self.neckCtrl+"_Orient_Grp")
                cmds.xform(self.neckOrientGrp, pivots=(self.neckPivot[0], self.neckPivot[1], self.neckPivot[2]), worldSpace=True)
                cmds.addAttr(self.neckCtrl, longName=self.langDic[self.langName]['c047_autoRotate'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.3, keyable=True)
                neckARMDName = self.langDic[self.langName]['c047_autoRotate'][0].capitalize()+self.langDic[self.langName]['c047_autoRotate'][1:]
                neckARMD = cmds.createNode('multiplyDivide', name=self.neckCtrl+"_"+neckARMDName+"_MD")
                cmds.connectAttr(self.headCtrl+".rotateX", neckARMD+".input1X", force=True)
                cmds.connectAttr(self.headCtrl+".rotateY", neckARMD+".input1Y", force=True)
                cmds.connectAttr(self.headCtrl+".rotateZ", neckARMD+".input1Z", force=True)
                cmds.connectAttr(self.neckCtrl+"."+self.langDic[self.langName]['c047_autoRotate'], neckARMD+".input2X", force=True)
                cmds.connectAttr(self.neckCtrl+"."+self.langDic[self.langName]['c047_autoRotate'], neckARMD+".input2Y", force=True)
                cmds.connectAttr(self.neckCtrl+"."+self.langDic[self.langName]['c047_autoRotate'], neckARMD+".input2Z", force=True)
                cmds.connectAttr(neckARMD+".outputX", self.neckOrientGrp+".rotateX", force=True)
                if self.rigType == Base.RigType.quadruped:
                    cmds.connectAttr(neckARMD+".outputY", self.neckOrientGrp+".rotateZ", force=True)
                    quadrupedRotYFixMD = cmds.createNode('multiplyDivide', name=self.neckCtrl+"_"+neckARMDName+"_YFix_MD")
                    cmds.connectAttr(neckARMD+".outputZ", quadrupedRotYFixMD+".input1X", force=True)
                    cmds.setAttr(quadrupedRotYFixMD+".input2X", -1)
                    cmds.connectAttr(quadrupedRotYFixMD+".outputX", self.neckOrientGrp+".rotateY", force=True)
                else:
                    cmds.connectAttr(neckARMD+".outputY", self.neckOrientGrp+".rotateY", force=True)
                    cmds.connectAttr(neckARMD+".outputZ", self.neckOrientGrp+".rotateZ", force=True)
                    
                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[2], self.headCtrl, absolute=True) #upperJawCtrl
                cmds.parent(self.zeroCtrlList[4], self.jawCtrl, absolute=True) #chinCtrl
                cmds.parent(self.zeroCtrlList[5], self.zeroCtrlList[9], self.chinCtrl, absolute=True) #chewCtrl, lowerLipCtrl
                cmds.parent(self.zeroCtrlList[8], self.upperJawCtrl, absolute=True) #upperLipCtrl
                
                # jaw follow head or root ctrl (using worldRef)
                jawParentConst = cmds.parentConstraint(self.headCtrl, self.worldRef, self.zeroCtrlList[3], maintainOffset=True, name=self.zeroCtrlList[3]+"_PaC")[0]
                cmds.setAttr(jawParentConst+".interpType", 2) #Shortest, no flip cause problem with scrubing
                cmds.addAttr(self.jawCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c032_follow'], jawParentConst+"."+self.headCtrl+"W0", force=True)
                jawFollowRev = cmds.createNode("reverse", name=self.jawCtrl+"_Rev")
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c032_follow'], jawFollowRev+".inputX", force=True)
                cmds.connectAttr(jawFollowRev+".outputX", jawParentConst+"."+self.worldRef+"W1", force=True)
                cmds.scaleConstraint(self.headCtrl, self.zeroCtrlList[3], maintainOffset=True, name=self.zeroCtrlList[3]+"_ScC")[0]
                
                # setup jaw move:
                # jaw open:
                self.setupJawMove(self.jawCtrl, "c108_open", True, "Y", "c049_intensity", createOutput=True, *args)
                self.setupJawMove(self.jawCtrl, "c108_open", True, "Z", "c049_intensity", *args)
                # jaw close:
                self.setupJawMove(self.jawCtrl, "c109_close", False, "Y", "c049_intensity", createOutput=True, *args)
                self.setupJawMove(self.jawCtrl, "c109_close", False, "Z", "c049_intensity", *args)
                # upper lid close:
                self.setupJawMove(self.upperLipCtrl, "c109_close", False, "Y", "c039_lip", *args)
                self.setupJawMove(self.upperLipCtrl, "c109_close", False, "Z", "c039_lip", *args)
                # lower lid close:
                self.setupJawMove(self.lowerLipCtrl, "c109_close", False, "Y", "c039_lip", invertRot=True, *args)
                self.setupJawMove(self.lowerLipCtrl, "c109_close", False, "Z", "c039_lip", *args)
                
                # set jaw move and lips calibrate default values:
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c108_open'].lower()+self.langDic[self.langName]['c110_start'].capitalize()+"Rotation", 5)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c108_open'].lower()+self.langDic[self.langName]['c111_calibrate']+"Y", -2)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c109_close'].lower()+self.langDic[self.langName]['c111_calibrate']+"Z", 0)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c108_open'].lower()+self.langDic[self.langName]['c111_calibrate']+self.langDic[self.langName]['c112_output'], 30)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c109_close'].lower()+self.langDic[self.langName]['c111_calibrate']+self.langDic[self.langName]['c112_output'], -10)
                cmds.setAttr(self.upperLipCtrl+"."+self.langDic[self.langName]['c109_close'].lower()+self.langDic[self.langName]['c111_calibrate']+"Z", 2)
                cmds.setAttr(self.lowerLipCtrl+"."+self.langDic[self.langName]['c109_close'].lower()+self.langDic[self.langName]['c111_calibrate']+"Y", 0)
                cmds.setAttr(self.lowerLipCtrl+"."+self.langDic[self.langName]['c109_close'].lower()+self.langDic[self.langName]['c111_calibrate']+"Z", 2)
                
                # left side lip:
                lLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperJawCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_PaC")[0]
                cmds.setAttr(lLipParentConst+".interpType", 2)
                cmds.addAttr(self.lCornerLipCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.lCornerLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], lLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.lLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c039_lip']+"_Rev")
                cmds.connectAttr(self.lCornerLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], self.lLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.lLipRevNode+'.outputX', lLipParentConst+"."+self.upperJawCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperJawCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_ScC")[0]
                # right side lip:
                rLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperJawCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_PaC")[0]
                cmds.setAttr(rLipParentConst+".interpType", 2)
                cmds.addAttr(self.rCornerLipCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.rCornerLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], rLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.rLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c039_lip']+"_Rev")
                cmds.connectAttr(self.rCornerLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], self.rLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.rLipRevNode+'.outputX', rLipParentConst+"."+self.upperJawCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperJawCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_ScC")[0]
                
                # articulation joint:
                if self.addArticJoint:
                    articJntList = utils.articulationJoint(self.neckJnt, self.headJnt) #could call to create corrective joints. See parameters to implement it, please.
                    utils.setJointLabel(articJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_01_"+self.langDic[self.langName]['c106_base'])
                    cmds.rename(articJntList[0], side+self.userGuideName+"_01_"+self.langDic[self.langName]['c106_base']+"_Jar")
                
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE_PLEASE_Loc")[0]
                cmds.parent(loc, self.worldRef, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                
                # hiding visibility attributes:
                self.ctrls.setLockHide([self.headCtrl, self.neckCtrl, self.upperJawCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.upperLipCtrl, self.lowerLipCtrl], ['v'], l=False)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.grpNeck, self.grpHead, self.zeroCtrlList[3], self.zeroCtrlList[6], self.zeroCtrlList[7], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.neckJnt, self.headJnt, self.lCornerLipJnt, self.rCornerLipJnt, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.grpHead, self.worldRef, name=side+self.userGuideName+"_Grp")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.grpHead, hookType='rootHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')

                #Ensure head Jxt matrix
                mHead = cmds.getAttr(self.headCtrl + ".worldMatrix")
                cmds.xform(self.headJxt, m=mHead, ws=True)

                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)
                
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
    
    
    def integratingInfo(self, *args):
        Base.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "worldRefList"     : self.worldRefList,
                                                "upperJawCtrlList" : self.upperJawCtrlList,
                                                "ctrlList"         : self.aCtrls,
                                                "lCtrls"           : self.aLCtrls,
                                                "rCtrls"           : self.aRCtrls,
                                              }
                                    }