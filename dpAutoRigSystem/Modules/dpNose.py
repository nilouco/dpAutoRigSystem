# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:
CLASS_NAME = "Nose"
TITLE = "m078_nose"
DESCRIPTION = "m176_noseDesc"
ICON = "/Icons/dp_nose.png"


class Nose(Base.StartClass, Layout.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)
        self.cvLNostrilLoc = self.guideName+"_cvLNostrilLoc"
        self.cvRNostrilLoc = self.guideName+"_cvRNostrilLoc"
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 1)
        cmds.addAttr(self.moduleGrp, longName="nostril", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".nostril", 1)
        # create cvJointLoc and cvLocators:
        self.cvTopLoc      = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_cvTopLoc1", r=0.3, d=1, guide=True)
        self.cvMiddleLoc   = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_cvMiddleLoc", r=0.2, d=1, guide=True)
        self.cvTipLoc      = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvTipLoc", r=0.1, d=1, guide=True)
        self.cvLSideLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvLSideLoc", r=0.15, d=1, guide=True)
        self.cvRSideLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvRSideLoc", r=0.15, d=1, guide=True)
        self.cvLNostrilLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvLNostrilLoc", r=0.1, d=1, guide=True)
        self.cvRNostrilLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvRNostrilLoc", r=0.1, d=1, guide=True)
        self.cvBottomLoc   = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvBottomLoc", r=0.1, d=1, guide=True)
        self.cvEndJoint    = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.05, d=1, guide=True)
        # create jointGuides:
        self.jGuideTop1   = cmds.joint(name=self.guideName+"_JGuideTop1", radius=0.001)
        self.jGuideMiddle = cmds.joint(name=self.guideName+"_JGuideMiddle", radius=0.001)
        self.jGuideTip    = cmds.joint(name=self.guideName+"jGuideTip", radius=0.001)
        self.jGuideEnd    = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.select(self.jGuideMiddle)
        self.jGuideSide    = cmds.joint(name=self.guideName+"jGuideSide", radius=0.001)
        self.jGuideNostril = cmds.joint(name=self.guideName+"jGuideNostril", radius=0.001)
        cmds.select(self.jGuideMiddle)
        self.jGuideBottom = cmds.joint(name=self.guideName+"jGuideBottom", radius=0.001)
        cmds.parent(self.jGuideTop1, self.moduleGrp, relative=True)
        # set jointGuides as templates:
        jGuideList = [self.jGuideTop1, self.jGuideMiddle, self.jGuideTip, self.jGuideEnd, self.jGuideSide, self.jGuideNostril, self.jGuideBottom, self.cvRSideLoc, self.cvRNostrilLoc]
        for jGuide in jGuideList:
            cmds.setAttr(jGuide+".template", 1)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvTopLoc, self.jGuideTop1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvMiddleLoc, self.jGuideMiddle, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvTipLoc, self.jGuideTip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLSideLoc, self.jGuideSide, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLNostrilLoc, self.jGuideNostril, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvBottomLoc, self.jGuideBottom, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good nose guide setup:
        cmds.setAttr(self.cvTopLoc+".rotateX", 60)
        cmds.setAttr(self.cvMiddleLoc+".translateY", -0.6)
        cmds.setAttr(self.cvMiddleLoc+".translateZ", 0.35)
        cmds.setAttr(self.cvTipLoc+".translateY", -0.4)
        cmds.setAttr(self.cvTipLoc+".translateZ", 0.55)
        cmds.setAttr(self.cvEndJoint+".translateZ", 0.3)
        cmds.setAttr(self.cvLSideLoc+".translateX", 0.35)
        cmds.setAttr(self.cvLSideLoc+".translateY", -0.55)
        cmds.setAttr(self.cvLSideLoc+".translateZ", 0.45)
        cmds.setAttr(self.cvLNostrilLoc+".translateX", 0.25)
        cmds.setAttr(self.cvLNostrilLoc+".translateY", -0.625)
        cmds.setAttr(self.cvLNostrilLoc+".translateZ", 0.625)
        cmds.setAttr(self.cvBottomLoc+".translateY", -0.9)
        cmds.setAttr(self.cvBottomLoc+".translateZ", 0.6)
        # make parenting between cvLocs:
        cmds.parent(self.cvTopLoc, self.moduleGrp)
        cmds.parent(self.cvMiddleLoc, self.cvTopLoc, relative=False)
        cmds.parent(self.cvTipLoc, self.cvMiddleLoc, relative=False)
        cmds.parent(self.cvEndJoint, self.cvTipLoc, relative=True)
        cmds.parent(self.cvLSideLoc, self.cvRSideLoc, self.cvMiddleLoc, relative=False)
        cmds.parent(self.cvLNostrilLoc, self.cvLSideLoc, relative=False)
        cmds.parent(self.cvRNostrilLoc, self.cvRSideLoc, relative=False)
        cmds.parent(self.cvBottomLoc, self.cvMiddleLoc, relative=False)
        # mirror right side guides:
        self.sideTMD = cmds.createNode("multiplyDivide", name=self.guideName+"_Side_Translate_MD")
        self.sideRMD = cmds.createNode("multiplyDivide", name=self.guideName+"_Side_Rotate_MD")
        self.nostrilMD = cmds.createNode("multiplyDivide", name=self.guideName+"_Nostril_MD")
        cmds.connectAttr(self.cvLSideLoc+".translateX", self.sideTMD+".input1X", force=True)
        cmds.connectAttr(self.cvLSideLoc+".translateY", self.sideTMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLSideLoc+".translateZ", self.sideTMD+".input1Z", force=True)
        cmds.connectAttr(self.cvLSideLoc+".rotateX", self.sideRMD+".input1X", force=True)
        cmds.connectAttr(self.cvLSideLoc+".rotateY", self.sideRMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLSideLoc+".rotateZ", self.sideRMD+".input1Z", force=True)
        cmds.connectAttr(self.sideTMD+".outputX", self.cvRSideLoc+".translateX", force=True)
        cmds.connectAttr(self.sideTMD+".outputY", self.cvRSideLoc+".translateY", force=True)
        cmds.connectAttr(self.sideTMD+".outputZ", self.cvRSideLoc+".translateZ", force=True)
        cmds.connectAttr(self.sideRMD+".outputX", self.cvRSideLoc+".rotateX", force=True)
        cmds.connectAttr(self.sideRMD+".outputY", self.cvRSideLoc+".rotateY", force=True)
        cmds.connectAttr(self.sideRMD+".outputZ", self.cvRSideLoc+".rotateZ", force=True)
        cmds.connectAttr(self.cvLNostrilLoc+".translateX", self.nostrilMD+".input1X", force=True)
        cmds.connectAttr(self.cvLNostrilLoc+".translateY", self.nostrilMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLNostrilLoc+".translateZ", self.nostrilMD+".input1Z", force=True)
        cmds.connectAttr(self.nostrilMD+".outputX", self.cvRNostrilLoc+".translateX", force=True)
        cmds.connectAttr(self.nostrilMD+".outputY", self.cvRNostrilLoc+".translateY", force=True)
        cmds.connectAttr(self.nostrilMD+".outputZ", self.cvRNostrilLoc+".translateZ", force=True)
        cmds.setAttr(self.sideTMD+".input2X", -1)
        cmds.setAttr(self.sideRMD+".input2Y", -1)
        cmds.setAttr(self.sideRMD+".input2Z", -1)
        cmds.setAttr(self.nostrilMD+".input2X", -1)
        
        
    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        utils.useDefaultRenderLayer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            try:
                self.enteredNJoints = cmds.intField(self.nJointsIF, query=True, value=True)
            except:
                return
        else:
            self.enteredNJoints = enteredNJoints
        # get the number of joints existing:
        self.currentNJoints = cmds.getAttr(self.moduleGrp+".nJoints")
        # start analisys the difference between values:
        if self.enteredNJoints != self.currentNJoints:
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvTopLoc:
                    self.cvTopLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_cvTopLoc"+str(n), r=0.3, d=1, guide=True)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvTopLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvTopLoc, self.guideName+"_cvTopLoc"+str(n-1), relative=True)
                    # translate new topLoc in the middle of distance of last top and middle guides:
                    dist = self.ctrls.distanceBet(self.guideName+"_cvTopLoc"+str(n-1), self.guideName+"_cvMiddleLoc")[0]
                    cmds.setAttr(self.cvTopLoc+".translateZ", (0.5*dist))
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.guideName+"_JGuideTop"+str(n), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    #Prevent a intermidiate node to be added
                    cmds.parent(self.jGuide, self.guideName+"_JGuideTop"+str(n-1), relative=True)
                    #Do not maintain offset and ensure cv will be at the same place than the joint
                    cmds.parentConstraint(self.cvTopLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                    cmds.scaleConstraint(self.cvTopLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvTopLoc:
                self.cvTopLoc = self.guideName+"_cvTopLoc"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = utils.getGuideChildrenList(self.cvTopLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvTopLoc)
                # delete difference of nJoints:
                cmds.delete(self.guideName+"_cvTopLoc"+str(self.enteredNJoints+1))
                cmds.delete(self.guideName+"_JGuideTop"+str(self.enteredNJoints+1))
            cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            # re-build the preview mirror:
            Layout.LayoutClass.createPreviewMirror(self)
        cmds.select(self.moduleGrp)
    

    def changeNostril(self, *args):
        """ Set the attribute value for nostril.
        """
        nostrilValue = cmds.checkBox(self.nostrilCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".nostril", nostrilValue)
        cmds.setAttr(self.cvLNostrilLoc+".visibility", nostrilValue)
        cmds.setAttr(self.cvRNostrilLoc+".visibility", nostrilValue)
    

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
            self.addFlip = self.getModuleAttr("flip")
            # declare lists to store names and attributes:
            self.aCtrls, self.aLCtrls, self.aRCtrls = [], [], []
            # check if need to add nostril:
            self.addNostril = self.getModuleAttr("nostril")
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
                        if not self.addFlip:
                            for axis in self.mirrorAxis:
                                gotValue = cmds.getAttr(side+self.userGuideName+"_Guide_Base.translate"+axis)
                                flipedValue = gotValue*(-2)
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                        else:
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
                #for Maya2012: self.userGuideName+'_'+self.moduleGrp+"_Grp"
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                self.base = side+self.userGuideName+'_Guide_Base'
                self.ctrlZeroGrp = side+self.userGuideName+"_00_Ctrl_Zero_0_Grp"
                self.skinJointList = []
                self.centerList, self.leftList, self.rightList = [], [], []
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                # creating top nose top controls and joints:
                for n in range(0, self.nJoints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.cvTopLoc = side+self.userGuideName+"_Guide_cvTopLoc"+str(n+1)
                    self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.userGuideName+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    utils.setJointLabel(self.jnt, s+jointLabelAdd, 18, self.userGuideName+"_%02d"%(n))
                    self.skinJointList.append(self.jnt)
                    # create a control:
                    self.noseCtrl = self.ctrls.cvControl("id_075_NoseTop", side+self.userGuideName+"_%02d_Ctrl"%(n), r=self.ctrlRadius, d=self.curveDegree)
                    self.centerList.append(self.noseCtrl)
                    # position and orientation of joint and control:
                    cmds.delete(cmds.parentConstraint(self.cvTopLoc, self.jnt, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.cvTopLoc, self.noseCtrl, maintainOffset=False))
                    # zeroOut controls:
                    self.zeroOutCtrlGrp = utils.zeroOut([self.noseCtrl])[0]
                    # hide visibility attribute:
                    cmds.setAttr(self.noseCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if self.addFlip:
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleX", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleY", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleZ", -1)
                    if n == 0:
                        utils.originedFrom(objName=self.noseCtrl, attrString=self.base+";"+self.cvTopLoc+";"+self.radiusGuide)
                        self.ctrlZeroGrp = self.zeroOutCtrlGrp
                    else:
                        utils.originedFrom(objName=self.noseCtrl, attrString=self.cvTopLoc)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.userGuideName+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroCtrl Group to the before noseCtrl:
                        self.fatherCtrl = side+self.userGuideName+"_%02d_Ctrl"%(n-1)
                        cmds.parent(self.zeroOutCtrlGrp, self.fatherCtrl, absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(self.noseCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    cmds.scaleConstraint(self.noseCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                    # add articulationJoint:
                    if n == 1:
                        if self.addArticJoint:
                            artJntList = utils.articulationJoint(self.fatherJnt, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            utils.setJointLabel(artJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                
                # declaring guides:
                self.cvMiddleLoc   = side+self.userGuideName+"_Guide_cvMiddleLoc"
                self.cvTipLoc      = side+self.userGuideName+"_Guide_cvTipLoc"
                self.cvLSideLoc    = side+self.userGuideName+"_Guide_cvLSideLoc"
                self.cvRSideLoc    = side+self.userGuideName+"_Guide_cvRSideLoc"
                self.cvLNostrilLoc = side+self.userGuideName+"_Guide_cvLNostrilLoc"
                self.cvRNostrilLoc = side+self.userGuideName+"_Guide_cvRNostrilLoc"
                self.cvBottomLoc   = side+self.userGuideName+"_Guide_cvBottomLoc"
                self.cvEndJoint    = side+self.userGuideName+"_Guide_JointEnd"
                
                # generating naming:
                leftSideName  = self.langDic[self.langName]['p002_left']
                rightSideName = self.langDic[self.langName]['p003_right']
                if self.addFlip:
                    leftSideName = self.langDic[self.langName]['c123_outer']
                    rightSideName = self.langDic[self.langName]['c122_inner']
                middleJntName    = side+self.userGuideName+"_%02d_"%(n+1)+self.langDic[self.langName]['c029_middle']+"_Jnt"
                tipJntName       = side+self.userGuideName+"_%02d_"%(n+2)+self.langDic[self.langName]['c120_tip']+"_Jnt"
                bottomJntName    = side+self.userGuideName+"_%02d_"%(n+2)+self.langDic[self.langName]['c100_bottom']+"_Jnt"
                lSideJntName     = side+self.userGuideName+"_%02d_"%(n+3)+leftSideName+"_"+self.langDic[self.langName]['c121_side']+"_Jnt"
                rSideJntName     = side+self.userGuideName+"_%02d_"%(n+3)+rightSideName+"_"+self.langDic[self.langName]['c121_side']+"_Jnt"
                lNostrilJntName  = side+self.userGuideName+"_%02d_"%(n+4)+leftSideName+"_"+self.langDic[self.langName]['m079_nostril']+"_Jnt"
                rNostrilJntName  = side+self.userGuideName+"_%02d_"%(n+4)+rightSideName+"_"+self.langDic[self.langName]['m079_nostril']+"_Jnt"
                middleCtrlName   = side+self.userGuideName+"_"+self.langDic[self.langName]['c029_middle']+"_Ctrl"
                tipCtrlName      = side+self.userGuideName+"_"+self.langDic[self.langName]['c120_tip']+"_Ctrl"
                bottomCtrlName   = side+self.userGuideName+"_"+self.langDic[self.langName]['c100_bottom']+"_Ctrl"
                lSideCtrlName    = side+self.userGuideName+"_"+leftSideName+"_"+self.langDic[self.langName]['c121_side']+"_Ctrl"
                rSideCtrlName    = side+self.userGuideName+"_"+rightSideName+"_"+self.langDic[self.langName]['c121_side']+"_Ctrl"
                lNostrilCtrlName = side+self.userGuideName+"_"+leftSideName+"_"+self.langDic[self.langName]['m079_nostril']+"_Ctrl"
                rNostrilCtrlName = side+self.userGuideName+"_"+rightSideName+"_"+self.langDic[self.langName]['m079_nostril']+"_Ctrl"
                
                # creating joints:
                self.middleJnt = cmds.joint(name=middleJntName, scaleCompensate=False)
                self.tipJnt = cmds.joint(name=tipJntName, scaleCompensate=False)
                cmds.select(self.middleJnt)
                self.bottomJnt = cmds.joint(name=bottomJntName, scaleCompensate=False)
                cmds.select(self.middleJnt)
                self.lSideJnt = cmds.joint(name=lSideJntName, scaleCompensate=False)
                if self.addNostril:
                    self.lNostrilJnt = cmds.joint(name=lNostrilJntName, scaleCompensate=False)
                cmds.select(self.middleJnt)
                self.rSideJnt = cmds.joint(name=rSideJntName, scaleCompensate=False)
                if self.addNostril:
                    self.rNostrilJnt = cmds.joint(name=rNostrilJntName, scaleCompensate=False)
                    dpARJointList = [self.middleJnt, self.tipJnt, self.lSideJnt, self.rSideJnt, self.lNostrilJnt, self.rNostrilJnt, self.bottomJnt]
                else:
                    dpARJointList = [self.middleJnt, self.tipJnt, self.lSideJnt, self.rSideJnt, self.bottomJnt]
                for dpARJoint in dpARJointList:
                    if cmds.objExists(dpARJoint):
                        cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                utils.setJointLabel(self.middleJnt, s+jointLabelAdd, 18, self.userGuideName+"_%02d_"%(n+1)+self.langDic[self.langName]['c029_middle'])
                utils.setJointLabel(self.tipJnt, s+jointLabelAdd, 18, self.userGuideName+"_%02d_"%(n+2)+self.langDic[self.langName]['c120_tip'])
                utils.setJointLabel(self.bottomJnt, s+jointLabelAdd, 18, self.userGuideName+"_%02d_"%(n+2)+self.langDic[self.langName]['c100_bottom'])
                utils.setJointLabel(self.lSideJnt, 1, 18, self.userGuideName+"_%02d_L_"%(n+3)+self.langDic[self.langName]['c121_side'])
                utils.setJointLabel(self.rSideJnt, 2, 18, self.userGuideName+"_%02d_R_"%(n+3)+self.langDic[self.langName]['c121_side'])
                if self.addNostril:
                    utils.setJointLabel(self.lNostrilJnt, 1, 18, self.userGuideName+"_%02d_L_"%(n+4)+self.langDic[self.langName]['m079_nostril'])
                    utils.setJointLabel(self.rNostrilJnt, 2, 18, self.userGuideName+"_%02d_R_"%(n+4)+self.langDic[self.langName]['m079_nostril'])
                
                # creating controls:
                self.middleCtrl = self.ctrls.cvControl("id_076_NoseMiddle", ctrlName=middleCtrlName, r=(self.ctrlRadius), d=self.curveDegree)
                self.tipCtrl = self.ctrls.cvControl("id_077_NoseTip", ctrlName=tipCtrlName, r=(self.ctrlRadius * 0.3), d=self.curveDegree)
                self.bottomCtrl = self.ctrls.cvControl("id_080_NoseBottom", ctrlName=bottomCtrlName, r=(self.ctrlRadius * 0.5), d=self.curveDegree, dir="-Y")
                self.lSideCtrl = self.ctrls.cvControl("id_078_NoseSide", ctrlName=lSideCtrlName, r=(self.ctrlRadius * 0.5), d=self.curveDegree, rot=(0, 0, -90))
                self.rSideCtrl = self.ctrls.cvControl("id_078_NoseSide", ctrlName=rSideCtrlName, r=(self.ctrlRadius * 0.5), d=self.curveDegree, rot=(0, 0, -90))
                if self.addNostril:
                    self.lNostrilCtrl = self.ctrls.cvControl("id_079_Nostril", ctrlName=lNostrilCtrlName, r=(self.ctrlRadius * 0.2), d=self.curveDegree)
                    self.rNostrilCtrl = self.ctrls.cvControl("id_079_Nostril", ctrlName=rNostrilCtrlName, r=(self.ctrlRadius * 0.2), d=self.curveDegree)
                    self.leftList.append(self.lNostrilCtrl)
                    self.rightList.append(self.rNostrilCtrl)
                self.centerList.append(self.middleCtrl)
                self.centerList.append(self.tipCtrl)
                self.centerList.append(self.bottomCtrl)
                self.aCtrls.append(self.centerList)
                self.leftList.append(self.lSideCtrl)
                self.rightList.append(self.rSideCtrl)
                self.aLCtrls.append(self.leftList)
                self.aRCtrls.append(self.rightList)
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.middleCtrl, attrString=self.cvMiddleLoc)
                utils.originedFrom(objName=self.tipCtrl, attrString=self.cvTipLoc)
                utils.originedFrom(objName=self.bottomCtrl, attrString=self.cvBottomLoc)
                utils.originedFrom(objName=self.lSideCtrl, attrString=self.cvLSideLoc)
                utils.originedFrom(objName=self.rSideCtrl, attrString=self.cvRSideLoc)
                if self.addNostril:
                    utils.originedFrom(objName=self.lNostrilCtrl, attrString=self.cvLNostrilLoc)
                    utils.originedFrom(objName=self.rNostrilCtrl, attrString=self.cvRNostrilLoc)

                # temporary parentConstraints:
                cmds.delete(cmds.parentConstraint(self.cvMiddleLoc, self.middleCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvTipLoc, self.tipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvBottomLoc, self.bottomCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLSideLoc, self.lSideCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvRSideLoc, self.rSideCtrl, maintainOffset=False))
                if self.addNostril:
                    cmds.delete(cmds.parentConstraint(self.cvLNostrilLoc, self.lNostrilCtrl, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.cvRNostrilLoc, self.rNostrilCtrl, maintainOffset=False))
                
                # fixing flip mirror:
                if s == 1:
                    if self.addFlip:
                        ctrlToFlipList = [self.middleCtrl, self.bottomCtrl, self.tipCtrl, self.lSideCtrl, self.rSideCtrl]
                        if self.addNostril:
                            ctrlToFlipList.append(self.lNostrilCtrl)
                            ctrlToFlipList.append(self.rNostrilCtrl)
                        for ctrlToFlip in ctrlToFlipList:
                            cmds.setAttr(ctrlToFlip+".scaleX", -1)
                            cmds.setAttr(ctrlToFlip+".scaleY", -1)
                            cmds.setAttr(ctrlToFlip+".scaleZ", -1)
                    else:
                        cmds.setAttr(self.rSideCtrl+".scaleX", -1)
                        if self.addNostril:
                            cmds.setAttr(self.rNostrilCtrl+".scaleX", -1)

                # zeroOut controls:
                self.zeroSideCtrlList = utils.zeroOut([self.lSideCtrl, self.rSideCtrl])
                if s == 0:
                    cmds.setAttr(self.zeroSideCtrlList[1]+".scaleX", -1)
                elif self.addFlip:
                    cmds.setAttr(self.zeroSideCtrlList[1]+".scaleX", 1)
                if self.addNostril:
                    self.zeroNostrilCtrlList = utils.zeroOut([self.lNostrilCtrl, self.rNostrilCtrl])
                    if s == 0:
                        cmds.setAttr(self.zeroNostrilCtrlList[1]+".scaleX", -1)
                    elif self.addFlip:
                        cmds.setAttr(self.zeroNostrilCtrlList[1]+".scaleX", 1)
                self.zeroCtrlList = utils.zeroOut([self.middleCtrl,  self.tipCtrl, self.bottomCtrl])

                # make controls drive joints:
                cmds.parentConstraint(self.middleCtrl, self.middleJnt, maintainOffset=False, name=self.middleJnt+"_PaC")
                cmds.scaleConstraint(self.middleCtrl, self.middleJnt, maintainOffset=False, name=self.middleJnt+"_ScC")
                cmds.parentConstraint(self.tipCtrl, self.tipJnt, maintainOffset=False, name=self.tipJnt+"_PaC")
                cmds.scaleConstraint(self.tipCtrl, self.tipJnt, maintainOffset=False, name=self.tipJnt+"_ScC")
                cmds.parentConstraint(self.bottomCtrl, self.bottomJnt, maintainOffset=False, name=self.bottomJnt+"_PaC")
                cmds.scaleConstraint(self.bottomCtrl, self.bottomJnt, maintainOffset=False, name=self.bottomJnt+"_ScC")
                cmds.parentConstraint(self.lSideCtrl, self.lSideJnt, maintainOffset=False, name=self.lSideJnt+"_PaC")
                cmds.scaleConstraint(self.lSideCtrl, self.lSideJnt, maintainOffset=False, name=self.lSideJnt+"_ScC")
                cmds.parentConstraint(self.rSideCtrl, self.rSideJnt, maintainOffset=False, name=self.rSideJnt+"_PaC")
                cmds.scaleConstraint(self.rSideCtrl, self.rSideJnt, maintainOffset=False, name=self.rSideJnt+"_ScC")
                if self.addNostril:
                    cmds.parentConstraint(self.lNostrilCtrl, self.lNostrilJnt, maintainOffset=False, name=self.lNostrilJnt+"_PaC")
                    cmds.scaleConstraint(self.lNostrilCtrl, self.lNostrilJnt, maintainOffset=False, name=self.lNostrilJnt+"_ScC")
                    cmds.parentConstraint(self.rNostrilCtrl, self.rNostrilJnt, maintainOffset=False, name=self.rNostrilJnt+"_PaC")
                    cmds.scaleConstraint(self.rNostrilCtrl, self.rNostrilJnt, maintainOffset=False, name=self.rNostrilJnt+"_ScC")

                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[0], self.noseCtrl, absolute=True) #middleCtrl
                cmds.parent(self.zeroCtrlList[1], self.zeroCtrlList[2], self.zeroSideCtrlList[0], self.zeroSideCtrlList[1], self.middleCtrl, absolute=True) #tipCtrl, bottomCtrl, lSideCtrl, rSideCtrl
                if self.addNostril:
                    cmds.parent(self.zeroNostrilCtrlList[0], self.lSideCtrl, absolute=True) #lNostrilCtrl
                    cmds.parent(self.zeroNostrilCtrlList[1], self.rSideCtrl, absolute=True) #rNostrilCtrl

                # create end joint:
                cmds.select(self.tipJnt)
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd", radius=0.5)
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))

                # optimize control CV shapes:
                tempTipCluster = cmds.cluster(self.tipCtrl)[1]
                cmds.parentConstraint(self.cvEndJoint, tempTipCluster, maintainOffset=False)
                cmds.delete([self.tipCtrl], constructionHistory=True)

                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.ctrlZeroGrp, name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.skinJointList[0], name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE_PLEASE_Loc")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
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
                                                "ctrlList" : self.aCtrls,
                                                "lCtrls"   : self.aLCtrls,
                                                "rCtrls"   : self.aRCtrls,
                                              }
                                    }
