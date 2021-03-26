# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:
CLASS_NAME = "Nose"
TITLE = "m176_nose"
DESCRIPTION = "m177_noseDesc"
ICON = "/Icons/dp_nose.png"


class Nose(Base.StartClass, Layout.LayoutClass):
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
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 1)
        # create cvJointLoc and cvLocators:
        self.cvTopLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_cvTopLoc1", r=0.3, d=1, guide=True)
        self.cvMiddleLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_cvMiddleLoc", r=0.2, d=1, guide=True)
        self.cvPointLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvPointLoc", r=0.1, d=1, guide=True)
        self.cvSideLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvSideLoc", r=0.15, d=1, guide=True)
        self.cvNostrilLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvNostrilLoc", r=0.1, d=1, guide=True)
        self.cvBottomLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_cvBottomLoc", r=0.1, d=1, guide=True)
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.05, d=1, guide=True)
        # create jointGuides:
        self.jGuideTop1 = cmds.joint(name=self.guideName+"_JGuideTop1", radius=0.001)
        self.jGuideMiddle = cmds.joint(name=self.guideName+"_JGuideMiddle", radius=0.001)
        self.jGuidePoint = cmds.joint(name=self.guideName+"jGuidePoint", radius=0.001)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.select(self.jGuideMiddle)
        self.jGuideSide = cmds.joint(name=self.guideName+"jGuideSide", radius=0.001)
        self.jGuideNostril = cmds.joint(name=self.guideName+"jGuideNostril", radius=0.001)
        cmds.select(self.jGuideMiddle)
        self.jGuideBottom = cmds.joint(name=self.guideName+"jGuideBottom", radius=0.001)
        cmds.parent(self.jGuideTop1, self.moduleGrp, relative=True)
        # set jointGuides as templates:
        jGuideList = [self.jGuideTop1, self.jGuideMiddle, self.jGuidePoint, self.jGuideEnd, self.jGuideSide, self.jGuideNostril, self.jGuideBottom]
        for jGuide in jGuideList:
            cmds.setAttr(jGuide+".template", 1)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvTopLoc, self.jGuideTop1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvMiddleLoc, self.jGuideMiddle, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvPointLoc, self.jGuidePoint, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvSideLoc, self.jGuideSide, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvNostrilLoc, self.jGuideNostril, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvBottomLoc, self.jGuideBottom, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good nose guide setup:
        cmds.setAttr(self.cvTopLoc+".rotateX", 60)
        cmds.setAttr(self.cvMiddleLoc+".translateY", -0.6)
        cmds.setAttr(self.cvMiddleLoc+".translateZ", 0.35)
        cmds.setAttr(self.cvPointLoc+".translateY", -0.4)
        cmds.setAttr(self.cvPointLoc+".translateZ", 0.55)
        cmds.setAttr(self.cvEndJoint+".translateZ", 0.3)
        cmds.setAttr(self.cvSideLoc+".translateX", 0.35)
        cmds.setAttr(self.cvSideLoc+".translateY", -0.55)
        cmds.setAttr(self.cvSideLoc+".translateZ", 0.45)
        cmds.setAttr(self.cvNostrilLoc+".translateX", 0.25)
        cmds.setAttr(self.cvNostrilLoc+".translateY", -0.625)
        cmds.setAttr(self.cvNostrilLoc+".translateZ", 0.625)
        cmds.setAttr(self.cvBottomLoc+".translateY", -0.9)
        cmds.setAttr(self.cvBottomLoc+".translateZ", 0.6)
        # make parenting between cvLocs:
        cmds.parent(self.cvTopLoc, self.moduleGrp)
        cmds.parent(self.cvMiddleLoc, self.cvTopLoc, relative=False)
        cmds.parent(self.cvPointLoc, self.cvMiddleLoc, relative=False)
        cmds.parent(self.cvEndJoint, self.cvPointLoc, relative=True)
        cmds.parent(self.cvSideLoc, self.cvMiddleLoc, relative=False)
        cmds.parent(self.cvNostrilLoc, self.cvSideLoc, relative=False)
        cmds.parent(self.cvBottomLoc, self.cvMiddleLoc, relative=False)
        
        
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
                        if cmds.getAttr(self.moduleGrp+".flip") == 0:
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
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.nJoints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.userGuideName+"_Guide_cvTopLoc"+str(n+1)
                    self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                    self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.userGuideName+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    utils.setJointLabel(self.jnt, s+jointLabelAdd, 18, self.userGuideName+"_%02d"%(n))
                    self.skinJointList.append(self.jnt)
                    # create a control:
                    self.jntCtrl = self.ctrls.cvControl("id_007_FkLine", side+self.userGuideName+"_%02d_Ctrl"%(n), r=self.ctrlRadius, d=self.curveDegree)
                    # position and orientation of joint and control:
                    cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.guide, self.jntCtrl, maintainOffset=False))
                    # zeroOut controls:
                    self.zeroOutCtrlGrp = utils.zeroOut([self.jntCtrl])[0]
                    # hide visibility attribute:
                    cmds.setAttr(self.jntCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 1:
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleX", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleY", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleZ", -1)
                    cmds.addAttr(self.jntCtrl, longName='scaleCompensate', attributeType="bool", keyable=False)
                    cmds.setAttr(self.jntCtrl+".scaleCompensate", 1, channelBox=True)
                    cmds.connectAttr(self.jntCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                    if n == 0:
                        utils.originedFrom(objName=self.jntCtrl, attrString=self.base+";"+self.guide+";"+self.radiusGuide)
                        self.ctrlZeroGrp = self.zeroOutCtrlGrp
                    elif n == self.nJoints-1:
                        utils.originedFrom(objName=self.jntCtrl, attrString=self.guide+";"+self.cvEndJoint)
                    else:
                        utils.originedFrom(objName=self.jntCtrl, attrString=self.guide)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.userGuideName+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroCtrl Group to the before jntCtrl:
                        self.fatherCtrl = side+self.userGuideName+"_%02d_Ctrl"%(n-1)
                        cmds.parent(self.zeroOutCtrlGrp, self.fatherCtrl, absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(self.jntCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    cmds.scaleConstraint(self.jntCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                    # add articulationJoint:
                    if n == 1:
                        if self.addArticJoint:
                            artJntList = utils.articulationJoint(self.fatherJnt, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            utils.setJointLabel(artJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                

# WIP
# To do:
# Rig side point middle nostril guides



#                # end chain:
#                if n == self.nJoints-1:
#                    # create end joint:
#                    self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd", radius=0.5)
#                    cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
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
