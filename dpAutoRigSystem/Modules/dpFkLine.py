# importing libraries:
import maya.cmds as cmds
import dpControls as ctrls
import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:    
CLASS_NAME = "FkLine"
TITLE = "m001_fkLine"
DESCRIPTION = "m002_fkLineDesc"
ICON = "/Icons/dp_fkLine.png"


class FkLine(Base.StartClass, Layout.LayoutClass):
    def __init__(self, dpUIinst, langDic, langName, userGuideName):
        Base.StartClass.__init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON)
        pass
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        self.cvJointLoc = ctrls.cvJointLoc(ctrlName=self.guideName+"_jointLoc1", r=0.3)
        self.jGuide1 = cmds.joint(name=self.guideName+"_jGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint = ctrls.cvLocator(ctrlName=self.guideName+"_jointEnd", r=0.1)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_jGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=True, name=self.jGuide1+"_parentConstraint")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=True, name=self.jGuideEnd+"_parentConstraint")
        cmds.scaleConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=True, name=self.jGuide1+"_scaleConstraint")
        cmds.scaleConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=True, name=self.jGuideEnd+"_scaleConstraint")
    
    
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
            # check if the controls have scale changed values in order to avoid the transform groups created from maya without namespace:
            scaledCtrl = False
            scaledCtrlDic = {}
            for j in range(1, self.currentNJoints+1):
                if cmds.getAttr(self.guideName+"_jointLoc"+str(j)+".scaleX") != 1 or cmds.getAttr(self.guideName+"_jointLoc"+str(j)+".scaleY") != 1 or cmds.getAttr(self.guideName+"_jointLoc"+str(j)+".scaleZ") != 1:
                    scaledCtrl = True
                    # get scale values:
                    scaledX = cmds.getAttr(self.guideName+"_jointLoc"+str(j)+".scaleX")
                    scaledY = cmds.getAttr(self.guideName+"_jointLoc"+str(j)+".scaleY")
                    scaledZ = cmds.getAttr(self.guideName+"_jointLoc"+str(j)+".scaleZ")
                    # store scale values in the dictionary:
                    scaledCtrlDic[j] = [scaledX, scaledY, scaledZ]
                    # reset scales values to 1,1,1:
                    cmds.setAttr(self.guideName+"_jointLoc"+str(j)+".scaleX", 1)
                    cmds.setAttr(self.guideName+"_jointLoc"+str(j)+".scaleY", 1)
                    cmds.setAttr(self.guideName+"_jointLoc"+str(j)+".scaleZ", 1)
            # unparent temporarely the Ends:
            self.cvEndJoint = self.guideName+"_jointEnd"
            cmds.parent(self.cvEndJoint, world=True)
            self.jGuideEnd = (self.guideName+"_jGuideEnd")
            cmds.parent(self.jGuideEnd, world=True)
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvJointLoc:
                    self.cvJointLoc = ctrls.cvJointLoc( ctrlName=self.guideName+"_jointLoc"+str(n), r=0.3 )
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvJointLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvJointLoc, self.guideName+"_jointLoc"+str(n-1), relative=True)
                    cmds.setAttr(self.cvJointLoc+".translateZ", 2)
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.guideName+"_jGuide"+str(n), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    cmds.parent(self.jGuide, self.guideName+"_jGuide"+str(n-1))
                    cmds.parentConstraint(self.cvJointLoc, self.jGuide, maintainOffset=True, name=self.jGuide+"_parentConstraint")
                    cmds.scaleConstraint(self.cvJointLoc, self.jGuide, maintainOffset=True, name=self.jGuide+"_scaleConstraint")
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvEndJoint:
                self.cvJointLoc = self.guideName+"_jointLoc"+str(self.enteredNJoints)
                self.cvEndJoint = self.guideName+"_jointEnd"
                self.jGuide = self.guideName+"_jGuide"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = utils.getGuideChildrenList(self.cvJointLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvJointLoc)
                # delete difference of nJoints:
                cmds.delete(self.guideName+"_jointLoc"+str(self.enteredNJoints+1))
                cmds.delete(self.guideName+"_jGuide"+str(self.enteredNJoints+1))
            # re-parent cvEndJoint:
            cmds.parent(self.cvEndJoint, self.cvJointLoc)
            cmds.setAttr(self.cvEndJoint+".tz", 1.3)
            cmds.parent(self.jGuideEnd, self.jGuide)
            # actualise the nJoints in the moduleGrp:
            cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            # reset changed scale values again:
            if scaledCtrl:
                for j in scaledCtrlDic:
                    if cmds.objExists(self.guideName+"_jointLoc"+str(j)):
                        cmds.setAttr(self.guideName+"_jointLoc"+str(j)+".scaleX", scaledCtrlDic[j][0])
                        cmds.setAttr(self.guideName+"_jointLoc"+str(j)+".scaleY", scaledCtrlDic[j][1])
                        cmds.setAttr(self.guideName+"_jointLoc"+str(j)+".scaleZ", scaledCtrlDic[j][2])
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
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_guide_base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="guide_base_grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_guide_base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_guide_base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_guide_base', name="guide_base_grp", relative=True)
                #for Maya2012: self.userGuideName+'_'+self.moduleGrp+"_grp"
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                self.base = side+self.userGuideName+'_guide_base'
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                for n in range(1, self.nJoints+1):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.userGuideName+"_guide_jointLoc"+str(n)
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.userGuideName+"_"+str(n)+"_jnt")
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # create a control:
                    self.ctrl = cmds.circle(name=side+self.userGuideName+"_"+str(n)+"_ctrl", degree=1, normal=(0, 0, 1), r=self.ctrlRadius, s=6, ch=False)[0]
                    if n == 1:
                        utils.originedFrom(objName=self.ctrl, attrString=self.base+";"+self.guide)
                    else:
                        utils.originedFrom(objName=self.ctrl, attrString=self.guide)
                    # position and orientation of joint and control:
                    tempDel = cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False)
                    cmds.delete(tempDel)
                    tempDel = cmds.parentConstraint(self.guide, self.ctrl, maintainOffset=False)
                    cmds.delete(tempDel)
                    # zeroOut controls:
                    utils.zeroOut([self.ctrl])
                    # hide visibility attribute:
                    cmds.setAttr(self.ctrl+'.visibility', keyable=False)
                # create end joint:
                self.cvEndJoint = side+self.userGuideName+"_guide_jointEnd"
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_jEnd")
                tempDel = cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False)
                cmds.delete(tempDel)
                cmds.parent(self.endJoint, side+self.userGuideName+"_"+str(self.nJoints)+"_jnt", absolute=True)
                # grouping:
                for n in range(1, self.nJoints+1):
                    self.jnt      = side+self.userGuideName+"_"+str(n)+"_jnt"
                    self.ctrl     = side+self.userGuideName+"_"+str(n)+"_ctrl"
                    self.zeroCtrl = side+self.userGuideName+"_"+str(n)+"_ctrl_zero"
                    if n > 1:
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.userGuideName+"_"+str(n-1)+"_jnt"
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroCtrl Group to the before ctrl:
                        self.fatherCtrl = side+self.userGuideName+"_"+str(n-1)+"_ctrl"
                        cmds.parent(self.zeroCtrl, self.fatherCtrl, absolute=True)
                    # create parentConstraint from ctrl to jnt:
                    cmds.parentConstraint(self.ctrl, self.jnt, maintainOffset=False, name=self.jnt+"_parentConstraint")
                    # create scaleConstraint from ctrl to jnt:
                    cmds.scaleConstraint(self.ctrl, self.jnt, maintainOffset=True, name=self.jnt+"_scaleConstraint")
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(side+self.userGuideName+"_1_ctrl_zero", name=side+self.userGuideName+"_control_grp")
                self.toScalableHookGrp = cmds.group(side+self.userGuideName+"_1_jnt", name=side+self.userGuideName+"_joint_grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_grp")
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
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
