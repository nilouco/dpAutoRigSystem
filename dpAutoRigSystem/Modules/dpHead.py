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
        self.cvLLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_LLip", r=0.1, d=1, guide=True)
        self.cvRLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RLip", r=0.1, d=1, guide=True)
        self.cvUpperLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Upper", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        # create jointGuides:
        self.jGuideNeck = cmds.joint(name=self.guideName+"_JGuideNeck", radius=0.001)
        self.jGuideHead = cmds.joint(name=self.guideName+"_JGuideHead", radius=0.001)
        self.jGuideUpper = cmds.joint(name=self.guideName+"_JGuideUpper", radius=0.001)
        cmds.select(self.jGuideHead)
        self.jGuideJaw  = cmds.joint(name=self.guideName+"_JGuideJaw", radius=0.001)
        self.jGuideChin = cmds.joint(name=self.guideName+"_JGuideChin", radius=0.001)
        self.jGuideChew = cmds.joint(name=self.guideName+"_JGuideChew", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideNeck+".template", 1)
        cmds.setAttr(self.jGuideHead+".template", 1)
        cmds.setAttr(self.jGuideUpper+".template", 1)
        cmds.setAttr(self.jGuideJaw+".template", 1)
        cmds.setAttr(self.jGuideChin+".template", 1)
        cmds.setAttr(self.jGuideChew+".template", 1)
        cmds.parent(self.jGuideNeck, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvChewLoc)
        cmds.setAttr(self.cvEndJoint+".tz", self.ctrls.dpCheckLinearUnit(1.3))
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideChew)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvNeckLoc, self.jGuideNeck, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvHeadLoc, self.jGuideHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperLoc, self.jGuideUpper, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvJawLoc, self.jGuideJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChinLoc, self.jGuideChin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChewLoc, self.jGuideChew, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
        cmds.setAttr(self.cvNeckLoc+".rotateZ", 90)
        cmds.makeIdentity(self.cvNeckLoc, rotate=True, apply=False)
        cmds.setAttr(self.cvHeadLoc+".translateY", 2)
        cmds.setAttr(self.cvUpperLoc+".translateY", 3.5)
        cmds.setAttr(self.cvUpperLoc+".translateZ", 0.25)
        cmds.setAttr(self.cvJawLoc+".translateY", 2.7)
        cmds.setAttr(self.cvJawLoc+".translateZ", 0.7)
        cmds.setAttr(self.cvChinLoc+".translateY", 2.5)
        cmds.setAttr(self.cvChinLoc+".translateZ", 1.0)
        cmds.setAttr(self.cvChewLoc+".translateY", 2.3)
        cmds.setAttr(self.cvChewLoc+".translateZ", 1.3)

        # lip cvLocs:
        cmds.setAttr(self.cvLLipLoc+".translateX", 0.6)
        cmds.setAttr(self.cvLLipLoc+".translateY", 2.6)
        cmds.setAttr(self.cvLLipLoc+".translateZ", 3.4)
        self.lipMD = cmds.createNode("multiplyDivide", name=self.guideName+"_Lip_MD")
        cmds.connectAttr(self.cvLLipLoc+".translateX", self.lipMD+".input1X", force=True)
        cmds.connectAttr(self.cvLLipLoc+".translateY", self.lipMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLLipLoc+".translateZ", self.lipMD+".input1Z", force=True)
        cmds.connectAttr(self.lipMD+".outputX", self.cvRLipLoc+".translateX", force=True)
        cmds.connectAttr(self.lipMD+".outputY", self.cvRLipLoc+".translateY", force=True)
        cmds.connectAttr(self.lipMD+".outputZ", self.cvRLipLoc+".translateZ", force=True)
        cmds.setAttr(self.lipMD+".input2X", -1)
        cmds.setAttr(self.cvRLipLoc+".template", 1)

      # make parents between cvLocs:
        cmds.parent(self.cvNeckLoc, self.moduleGrp)
        cmds.parent(self.cvHeadLoc, self.cvNeckLoc)
        cmds.parent(self.cvUpperLoc, self.cvJawLoc, self.cvHeadLoc)
        cmds.parent(self.cvChinLoc, self.cvJawLoc)
        cmds.parent(self.cvChewLoc, self.cvChinLoc)
        cmds.parent(self.cvLLipLoc, self.cvJawLoc)
        cmds.parent(self.cvRLipLoc, self.cvJawLoc)
    
    
    def setupJawMove(self, openCloseID, positiveRotation, *args):
        """ Create the setup for move jaw group when jaw control rotates for open or close adjustements.
        """
        # declaring naming:
        jawBaseName = utils.extractSuffix(self.jawCtrl)
        jawMoveGrpName = jawBaseName+"_"+self.langDic[self.langName]['c034_move'].capitalize()+self.langDic[self.langName][openCloseID]+"_Grp"
        intYName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c049_intensity'].capitalize()+"Y"
        intZName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c049_intensity'].capitalize()+"Z"
        startRotName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c110_start'].capitalize()+"Rotation"
        unitFixYName = self.langDic[self.langName][openCloseID].lower()+"UnitFixY"
        unitFixZName = self.langDic[self.langName][openCloseID].lower()+"UnitFixZ"
        multYName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c105_multiplier'].capitalize()+"Y"
        multZName = self.langDic[self.langName][openCloseID].lower()+self.langDic[self.langName]['c105_multiplier'].capitalize()+"Z"
        jawMultiplierMDName = jawBaseName+self.langDic[self.langName][openCloseID]+"_IntensityMultiplier_MD"
        jawUnitFixMDName = jawBaseName+self.langDic[self.langName][openCloseID]+"_UnitFix_MD"
        jawIntYMDName = jawBaseName+self.langDic[self.langName][openCloseID]+"_IntensityY_MD"
        jawIntZMDName = jawBaseName+self.langDic[self.langName][openCloseID]+"_IntensityZ_MD"
        jawStartMDName = jawBaseName+self.langDic[self.langName][openCloseID]+"_Start_MD"
        jawIntPMAName = jawBaseName+self.langDic[self.langName][openCloseID]+"_IntensityStart_PMA"
        jawIntCndName = jawBaseName+self.langDic[self.langName][openCloseID]+"_Intensity_Cnd"
        
        # create move group and attributes:
        self.jawMoveGrp = cmds.group(self.jawCtrl, name=jawMoveGrpName)
        cmds.addAttr(self.jawCtrl, longName=intYName, attributeType='float', defaultValue=1, keyable=True)
        cmds.addAttr(self.jawCtrl, longName=intZName, attributeType='float', defaultValue=1, keyable=True)
        if positiveRotation: #open
            cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=0, minValue=0, keyable=True)
        else: #close
            cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=0, maxValue=0, keyable=True)
        cmds.addAttr(self.jawCtrl, longName=unitFixYName, attributeType='float', defaultValue=-0.01)
        cmds.addAttr(self.jawCtrl, longName=unitFixZName, attributeType='float', defaultValue=-0.1)
        if positiveRotation: #open
            cmds.addAttr(self.jawCtrl, longName=multYName, attributeType='float', defaultValue=1)
            cmds.addAttr(self.jawCtrl, longName=multZName, attributeType='float', defaultValue=2)
        else: #close
            cmds.addAttr(self.jawCtrl, longName=multYName, attributeType='float', defaultValue=-1)
            cmds.addAttr(self.jawCtrl, longName=multZName, attributeType='float', defaultValue=-1)
        cmds.setAttr(self.jawCtrl+"."+intYName, keyable=False, channelBox=True)
        cmds.setAttr(self.jawCtrl+"."+intZName, keyable=False, channelBox=True)
        cmds.setAttr(self.jawCtrl+"."+startRotName, keyable=False, channelBox=True)
        
        # create utility nodes:
        jawMultiplierMD = cmds.createNode('multiplyDivide', name=jawMultiplierMDName)
        jawUnitFixMD = cmds.createNode('multiplyDivide', name=jawUnitFixMDName)
        jawIntYMD = cmds.createNode('multiplyDivide', name=jawIntYMDName)
        jawIntZMD = cmds.createNode('multiplyDivide', name=jawIntZMDName)
        jawStartMD = cmds.createNode('multiplyDivide', name=jawStartMDName)
        jawIntPMA = cmds.createNode('plusMinusAverage', name=jawIntPMAName)
        jawIntCnd = cmds.createNode('condition', name=jawIntCndName)
        
        # set and connect attributes to move jaw group when open or close:
        cmds.setAttr(jawIntPMA+".operation", 2)
        cmds.setAttr(jawIntCnd+".operation", 4) #less than
        if positiveRotation: #open
            cmds.setAttr(jawIntCnd+".operation", 2) #greater than
        cmds.setAttr(jawIntCnd+".colorIfFalseG", 0)
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntYMD+".input1Y", force=True)
        cmds.connectAttr(self.jawCtrl+"."+intYName, jawMultiplierMD+".input1Y", force=True)
        cmds.connectAttr(self.jawCtrl+"."+multYName, jawMultiplierMD+".input2Y", force=True)
        cmds.connectAttr(self.jawCtrl+"."+intZName, jawMultiplierMD+".input1Z", force=True)
        cmds.connectAttr(self.jawCtrl+"."+multZName, jawMultiplierMD+".input2Z", force=True)
        cmds.connectAttr(jawMultiplierMD+".outputY", jawUnitFixMD+".input1Y", force=True)
        cmds.connectAttr(self.jawCtrl+"."+unitFixYName, jawUnitFixMD+".input2Y", force=True)
        cmds.connectAttr(jawMultiplierMD+".outputZ", jawUnitFixMD+".input1Z", force=True)
        cmds.connectAttr(self.jawCtrl+"."+unitFixZName, jawUnitFixMD+".input2Z", force=True)
        cmds.connectAttr(jawUnitFixMD+".outputY", jawIntYMD+".input2Y", force=True)
        cmds.connectAttr(jawUnitFixMD+".outputY", jawStartMD+".input1X", force=True)
        cmds.connectAttr(jawUnitFixMD+".outputZ", jawIntZMD+".input2Z", force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawStartMD+".input2X", force=True)
        cmds.connectAttr(jawIntYMD+".outputY", jawIntPMA+".input1D[0]", force=True)
        cmds.connectAttr(jawStartMD+".outputX", jawIntPMA+".input1D[1]", force=True)
        cmds.connectAttr(jawIntPMA+".output1D", jawIntCnd+".colorIfTrueG", force=True)
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntCnd+".firstTerm", force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawIntCnd+".secondTerm", force=True)
        cmds.connectAttr(jawIntCnd+".outColorG", self.jawMoveGrp+".translateY", force=True)
        cmds.connectAttr(jawIntCnd+".outColorG", jawIntZMD+".input1Z", force=True)
        cmds.connectAttr(jawIntZMD+".outputZ", self.jawMoveGrp+".translateZ", force=True)
    
    
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
            self.worldRefList, self.upperCtrlList = [], []
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
                self.cvUpperLoc = side+self.userGuideName+"_Guide_Upper"
                self.cvJawLoc   = side+self.userGuideName+"_Guide_Jaw"
                self.cvChinLoc  = side+self.userGuideName+"_Guide_Chin"
                self.cvChewLoc  = side+self.userGuideName+"_Guide_Chew"
                self.cvLLipLoc  = side+self.userGuideName+"_Guide_LLip"
                self.cvRLipLoc  = side+self.userGuideName+"_Guide_RLip"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                
                # generating naming:
                neckJntName = side+self.userGuideName+"_00_"+self.langDic[self.langName]['c023_neck']+"_Jnt"
                headJxtName = side+self.userGuideName+"_"+self.langDic[self.langName]['c024_head']+"_Jxt"
                headJntName = side+self.userGuideName+"_01_"+self.langDic[self.langName]['c024_head']+"_Jnt"
                if self.addArticJoint:
                    headJntName = side+self.userGuideName+"_02_"+self.langDic[self.langName]['c024_head']+"_Jnt"
                upperJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw']+"_Jnt"
                upperEndJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw']+"_JEnd"
                jawJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c025_jaw']+"_Jnt"
                chinJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c026_chin']+"_Jnt"
                chewJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['c048_chew']+"_Jnt"
                endJntName = side+self.userGuideName+"_JEnd"
                lLipJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c039_lip']+"_Jnt"
                rLipJntName = side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c039_lip']+"_Jnt"
                neckCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c023_neck']+"_Ctrl"
                headCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c024_head']+"_Ctrl"
                upperCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw']+"_Ctrl"
                jawCtrlName  = side+self.userGuideName+"_"+self.langDic[self.langName]['c025_jaw']+"_Ctrl"
                chinCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c026_chin']+"_Ctrl"
                chewCtrlName = side+self.userGuideName+"_"+self.langDic[self.langName]['c048_chew']+"_Ctrl"
                lLipCtrlName = self.langDic[self.langName]['p002_left']+"_"+self.userGuideName+"_"+self.langDic[self.langName]['c039_lip']+"_Ctrl"
                rLipCtrlName = self.langDic[self.langName]['p003_right']+"_"+self.userGuideName+"_"+self.langDic[self.langName]['c039_lip']+"_Ctrl"
                
                # creating joints:
                self.neckJnt = cmds.joint(name=neckJntName)
                self.headJxt = cmds.joint(name=headJxtName)
                cmds.select(clear=True)
                self.headJnt = cmds.joint(name=headJntName, scaleCompensate=False)
                self.upperJnt = cmds.joint(name=upperJntName, scaleCompensate=False)
                self.upperEndJnt = cmds.joint(name=upperEndJntName, scaleCompensate=False, radius=0.5)
                cmds.setAttr(self.upperEndJnt+".translateY", 0.3*self.ctrlRadius)
                cmds.select(self.headJnt)
                self.jawJnt  = cmds.joint(name=jawJntName, scaleCompensate=False)
                self.chinJnt = cmds.joint(name=chinJntName, scaleCompensate=False)
                self.chewJnt = cmds.joint(name=chewJntName, scaleCompensate=False)
                self.endJnt  = cmds.joint(name=endJntName, scaleCompensate=False, radius=0.5)
                cmds.select(clear=True)
                self.lLipJnt = cmds.joint(name=lLipJntName, scaleCompensate=False)
                cmds.select(clear=True)
                self.rLipJnt = cmds.joint(name=rLipJntName, scaleCompensate=False)
                cmds.select(clear=True)
                dpARJointList = [self.neckJnt, self.headJnt, self.upperJnt, self.jawJnt, self.chinJnt, self.chewJnt, self.lLipJnt, self.rLipJnt]
                for dpARJoint in dpARJointList:
                    cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                utils.setJointLabel(self.neckJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c023_neck'])
                utils.setJointLabel(self.headJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c024_head'])
                utils.setJointLabel(self.upperJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c044_upper']+self.langDic[self.langName]['c025_jaw'])
                utils.setJointLabel(self.jawJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c025_jaw'])
                utils.setJointLabel(self.chinJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c026_chin'])
                utils.setJointLabel(self.chewJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.langDic[self.langName]['c048_chew'])
                utils.setJointLabel(self.lLipJnt, 1, 18, self.userGuideName+"_"+self.langDic[self.langName]['c039_lip'])
                utils.setJointLabel(self.rLipJnt, 2, 18, self.userGuideName+"_"+self.langDic[self.langName]['c039_lip'])
                # creating controls:
                self.neckCtrl = self.ctrls.cvControl("id_022_HeadNeck", ctrlName=neckCtrlName, r=(self.ctrlRadius * 1.5), d=self.curveDegree, dir="-Z")
                self.headCtrl = self.ctrls.cvControl("id_023_HeadHead", ctrlName=headCtrlName, r=(self.ctrlRadius * 2.5), d=self.curveDegree)
                self.upperCtrl = self.ctrls.cvControl("id_069_HeadUpperJaw", ctrlName=upperCtrlName, r=self.ctrlRadius, d=self.curveDegree)
                self.jawCtrl  = self.ctrls.cvControl("id_024_HeadJaw", ctrlName=jawCtrlName, r=self.ctrlRadius, d=self.curveDegree)
                self.chinCtrl = self.ctrls.cvControl("id_025_HeadChin", ctrlName=chinCtrlName, r=(self.ctrlRadius * 0.2), d=self.curveDegree)
                self.chewCtrl = self.ctrls.cvControl("id_026_HeadChew", ctrlName=chewCtrlName, r=(self.ctrlRadius * 0.15), d=self.curveDegree)
                self.lLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=lLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                self.rLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=rLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree)
                self.upperCtrlList.append(self.upperCtrl)
                self.aCtrls.append([self.neckCtrl, self.headCtrl, self.upperCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl])
                self.aLCtrls.append([self.lLipCtrl])
                self.aRCtrls.append([self.rLipCtrl])
                
                # optimize control CV shapes:
                tempHeadCluster = cmds.cluster(self.headCtrl)[1]
                cmds.setAttr(tempHeadCluster+".translateY", -0.5)
                tempJawCluster = cmds.cluster(self.jawCtrl)[1]
                cmds.setAttr(tempJawCluster+".translateY", -1)
                cmds.setAttr(tempJawCluster+".translateZ", 1.5)
                tempChinCluster = cmds.cluster(self.chinCtrl)[1]
                cmds.setAttr(tempChinCluster+".translateY", -0.25)
                cmds.setAttr(tempChinCluster+".translateZ", 2.85)
                cmds.setAttr(tempChinCluster+".rotateX", 22)
                tempChewCluster = cmds.cluster(self.chewCtrl)[1]
                cmds.setAttr(tempChewCluster+".translateZ", 2.54)
                cmds.setAttr(tempChewCluster+".rotateX", 22)
                cmds.delete([self.headCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl], constructionHistory=True)
                
                #Setup Axis Order
                if self.rigType == Base.RigType.quadruped:
                    cmds.setAttr(self.neckCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.upperCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 1)
                    cmds.rotate(90, 0, 0, self.neckCtrl)
                    cmds.makeIdentity(self.neckCtrl, apply=True, rotate=True)
                else:
                    cmds.setAttr(self.neckCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.upperCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 3)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.neckCtrl, attrString=self.base+";"+self.cvNeckLoc+";"+self.radiusGuide)
                utils.originedFrom(objName=self.headCtrl, attrString=self.cvHeadLoc)
                utils.originedFrom(objName=self.upperCtrl, attrString=self.cvUpperLoc)
                utils.originedFrom(objName=self.jawCtrl, attrString=self.cvJawLoc)
                utils.originedFrom(objName=self.chinCtrl, attrString=self.cvChinLoc)
                utils.originedFrom(objName=self.chewCtrl, attrString=self.cvChewLoc+";"+self.cvEndJoint)
                utils.originedFrom(objName=self.lLipCtrl, attrString=self.cvLLipLoc)
                utils.originedFrom(objName=self.rLipCtrl, attrString=self.cvRLipLoc)
                
                # edit the mirror shape to a good direction of controls:
                ctrlList = [self.neckCtrl, self.headCtrl, self.upperCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl]
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
                cmds.delete(cmds.parentConstraint(self.cvUpperLoc, self.upperCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvJawLoc, self.jawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChinLoc, self.chinCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChewLoc, self.chewCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLLipLoc, self.lLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvRLipLoc, self.rLipCtrl, maintainOffset=False))
                
                # zeroOut controls:
                self.zeroLipCtrlList = utils.zeroOut([self.lLipCtrl, self.rLipCtrl])
                self.lLipGrp = cmds.group(self.lLipCtrl, name=self.lLipCtrl+"_Grp")
                self.rLipGrp = cmds.group(self.rLipCtrl, name=self.rLipCtrl+"_Grp")
                cmds.setAttr(self.rLipGrp+".scaleX", -1)
                self.zeroCtrlList = utils.zeroOut([self.neckCtrl, self.headCtrl, self.upperCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.zeroLipCtrlList[0], self.zeroLipCtrlList[1]])

                # make joints be ride by controls:
                cmds.makeIdentity(self.neckJnt, self.headJxt, self.headJnt, self.jawJnt, self.chinJnt, self.chewJnt, self.endJnt, rotate=True, apply=True)
                cmds.parentConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_PaC")
                cmds.scaleConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_ScC")
                cmds.delete(cmds.parentConstraint(self.headCtrl, self.headJxt, maintainOffset=False))
                cmds.parentConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_PaC")
                cmds.parentConstraint(self.upperCtrl, self.upperJnt, maintainOffset=False, name=self.upperJnt+"_PaC")
                cmds.parentConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_PaC")
                cmds.parentConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_PaC")
                cmds.parentConstraint(self.chewCtrl, self.chewJnt, maintainOffset=False, name=self.chewJnt+"_PaC")
                cmds.parentConstraint(self.lLipCtrl, self.lLipJnt, maintainOffset=False, name=self.lLipJnt+"_PaC")
                cmds.parentConstraint(self.rLipCtrl, self.rLipJnt, maintainOffset=False, name=self.rLipJnt+"_PaC")
                cmds.scaleConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_ScC")
                cmds.scaleConstraint(self.upperCtrl, self.upperJnt, maintainOffset=False, name=self.upperJnt+"_ScC")
                cmds.scaleConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_ScC")
                cmds.scaleConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_ScC")
                cmds.scaleConstraint(self.chewCtrl, self.chewJnt, maintainOffset=False, name=self.chewJnt+"_ScC")
                cmds.scaleConstraint(self.lLipCtrl, self.lLipJnt, maintainOffset=False, name=self.lLipJnt+"_ScC")
                cmds.scaleConstraint(self.rLipCtrl, self.rLipJnt, maintainOffset=False, name=self.rLipJnt+"_ScC")
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
                
                self.worldRef = cmds.group(empty=True, name=side+self.userGuideName+"_WorldRef")
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
                cmds.parent(self.zeroCtrlList[2], self.headCtrl, absolute=True)
                cmds.parent(self.zeroCtrlList[4], self.jawCtrl, absolute=True)
                cmds.parent(self.zeroCtrlList[5], self.chinCtrl, absolute=True)
                
                # jaw follow head or root ctrl (using worldRef)
                jawParentConst = cmds.parentConstraint(self.headCtrl, self.worldRef, self.zeroCtrlList[3], maintainOffset=True, name=self.zeroCtrlList[3]+"_PaC")[0]
                cmds.setAttr(jawParentConst+".interpType", 2) #Shortest, no flip cause problem with scrubing
                cmds.addAttr(self.jawCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c032_follow'], jawParentConst+"."+self.headCtrl+"W0", force=True)
                jawFollowRev = cmds.createNode("reverse", name=self.jawCtrl+"_Rev")
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c032_follow'], jawFollowRev+".inputX", force=True)
                cmds.connectAttr(jawFollowRev+".outputX", jawParentConst+"."+self.worldRef+"W1", force=True)
                cmds.scaleConstraint(self.headCtrl, self.zeroCtrlList[3], maintainOffset=True, name=self.zeroCtrlList[3]+"_ScC")[0]
                
                # setup jaw open:
                self.setupJawMove("c108_open", True, *args)
                # setup jaw close:
                self.setupJawMove("c109_close", False, *args)
                
                # create lip setup:
                # upper lip:
                
                # WIP - TO DO here
                
                
                
                
                
                
                
                
                # left side lip:
                lLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_PaC")[0]
                cmds.setAttr(lLipParentConst+".interpType", 2)
                cmds.addAttr(self.lLipCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.lLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], lLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.lLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c039_lip']+"_Rev")
                cmds.connectAttr(self.lLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], self.lLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.lLipRevNode+'.outputX', lLipParentConst+"."+self.upperCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_ScC")[0]
                # right side lip:
                rLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_PaC")[0]
                cmds.setAttr(rLipParentConst+".interpType", 2)
                cmds.addAttr(self.rLipCtrl, longName=self.langDic[self.langName]['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.rLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], rLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.rLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c039_lip']+"_Rev")
                cmds.connectAttr(self.rLipCtrl+'.'+self.langDic[self.langName]['c032_follow'], self.rLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.rLipRevNode+'.outputX', rLipParentConst+"."+self.upperCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_ScC")[0]
                
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
                self.ctrls.setLockHide([self.headCtrl, self.neckCtrl, self.upperCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl], ['v'], l=False)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.grpNeck, self.grpHead, self.zeroCtrlList[3], self.zeroCtrlList[6], self.zeroCtrlList[7], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.neckJnt, self.headJnt, self.lLipJnt, self.rLipJnt, name=side+self.userGuideName+"_Joint_Grp")
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
                                                "worldRefList" : self.worldRefList,
                                                "upperCtrlList" : self.upperCtrlList,
                                                "ctrlList"     : self.aCtrls,
                                                "lCtrls"       : self.aLCtrls,
                                                "rCtrls"       : self.aRCtrls,
                                              }
                                    }