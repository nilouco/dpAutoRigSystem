# importing libraries:
import maya.cmds as cmds
import dpControls as ctrls
import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:    
CLASS_NAME = "Head"
TITLE = "m017_head"
DESCRIPTION = "m018_headDesc"
ICON = "/Icons/dp_head.png"


class Head(Base.StartClass, Layout.LayoutClass):
    def __init__(self, dpUIinst, langDic, langName, userGuideName):
        Base.StartClass.__init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON)
        pass
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        # create cvJointLoc and cvLocators:
        self.cvNeckLoc = ctrls.cvJointLoc(ctrlName=self.guideName+"_neck", r=0.5)
        self.cvHeadLoc = ctrls.cvLocator(ctrlName=self.guideName+"_head", r=0.4)
        self.cvJawLoc  = ctrls.cvLocator(ctrlName=self.guideName+"_jaw", r=0.3)
        self.cvChinLoc = ctrls.cvLocator(ctrlName=self.guideName+"_chin", r=0.3)
        # create jointGuides:
        self.jGuideNeck = cmds.joint(name=self.guideName+"_jGuideNeck", radius=0.001)
        self.jGuideHead = cmds.joint(name=self.guideName+"_jGuideHead", radius=0.001)
        self.jGuideJaw  = cmds.joint(name=self.guideName+"_jGuideJaw", radius=0.001)
        self.jGuideChin = cmds.joint(name=self.guideName+"_jGuideChin", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideNeck+".template", 1)
        cmds.setAttr(self.jGuideHead+".template", 1)
        cmds.setAttr(self.jGuideJaw+".template", 1)
        cmds.setAttr(self.jGuideChin+".template", 1)
        cmds.parent(self.jGuideNeck, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint = ctrls.cvLocator(ctrlName=self.guideName+"_jointEnd", r=0.1)
        cmds.parent(self.cvEndJoint, self.cvChinLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_jGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideChin)
        # make parents between cvLocs:
        cmds.parent(self.cvNeckLoc, self.moduleGrp)
        cmds.parent(self.cvHeadLoc, self.cvNeckLoc)
        cmds.parent(self.cvJawLoc, self.cvHeadLoc)
        cmds.parent(self.cvChinLoc, self.cvJawLoc)
        # connect cvLocs in jointGuides:
        ctrls.directConnect(self.cvNeckLoc, self.jGuideNeck, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvHeadLoc, self.jGuideHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvJawLoc, self.jGuideJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvChinLoc, self.jGuideChin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.cvNeckLoc+".rotateY", -10)
        cmds.setAttr(self.cvHeadLoc+".translateZ", 2)
        cmds.setAttr(self.cvHeadLoc+".rotateY", 5)
        cmds.setAttr(self.cvJawLoc+".translateX", -0.5)
        cmds.setAttr(self.cvJawLoc+".translateZ", 1.25)
        cmds.setAttr(self.cvJawLoc+".rotateY", -95)
        cmds.setAttr(self.cvChinLoc+".translateZ", 0.25)
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
    
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declare lists to store names and attributes:
            self.grpHeadBList, self.headRevNodeList = [], []
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
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # redeclaring variables:
                self.base       = side+self.userGuideName+"_guide_base"
                self.cvNeckLoc  = side+self.userGuideName+"_guide_neck"
                self.cvHeadLoc  = side+self.userGuideName+"_guide_head"
                self.cvJawLoc   = side+self.userGuideName+"_guide_jaw"
                self.cvChinLoc  = side+self.userGuideName+"_guide_chin"
                self.cvEndJoint = side+self.userGuideName+"_guide_jointEnd"
                
                # creating joints:
                self.neckJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_neck']+"_jnt")
                self.headJxt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_head']+"_jxt")
                self.headJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_head']+"_jnt")
                self.jawJnt  = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_jaw']+"_jnt")
                self.chinJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_chin']+"_jnt")
                self.endJnt  = cmds.joint(name=side+self.userGuideName+"_jEnd")
                dpARJointList = [self.neckJnt, self.headJnt, self.jawJnt, self.chinJnt]
                for dpARJoint in dpARJointList:
                    cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # creating controls:
                self.neckCtrl = ctrls.cvNeck(ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_neck']+"_ctrl", r=self.ctrlRadius/2.0)
                self.headCtrl = ctrls.cvHead(ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_head']+"_ctrl", r=self.ctrlRadius/2.0)
                self.jawCtrl  = ctrls.cvJaw( ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_jaw']+"_ctrl",  r=self.ctrlRadius/2.0)
                self.chinCtrl = ctrls.cvChin(ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_chin']+"_ctrl", r=self.ctrlRadius/2.0)
                
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.neckCtrl, attrString=self.base+";"+self.cvNeckLoc)
                utils.originedFrom(objName=self.headCtrl, attrString=self.cvHeadLoc)
                utils.originedFrom(objName=self.jawCtrl, attrString=self.cvJawLoc)
                utils.originedFrom(objName=self.chinCtrl, attrString=self.cvChinLoc+";"+self.cvEndJoint)
                
                # orientation of controls:
                ctrls.setAndFreeze(nodeName=self.neckCtrl, rx=90, rz=-90)
                ctrls.setAndFreeze(nodeName=self.headCtrl, rx=90, rz=-90)
                ctrls.setAndFreeze(nodeName=self.jawCtrl, rz=-90)
                ctrls.setAndFreeze(nodeName=self.chinCtrl, rz=-90)
                
                # edit the mirror shape to a good direction of controls:
                ctrlList = [ self.neckCtrl, self.headCtrl, self.jawCtrl, self.chinCtrl ]
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
                tempDelNeck = cmds.parentConstraint(self.cvNeckLoc, self.neckCtrl, maintainOffset=False)
                tempDelHead = cmds.parentConstraint(self.cvHeadLoc, self.headCtrl, maintainOffset=False)
                tempDelJaw  = cmds.parentConstraint(self.cvJawLoc, self.jawCtrl, maintainOffset=False)
                tempDelChin = cmds.parentConstraint(self.cvChinLoc, self.chinCtrl, maintainOffset=False)
                cmds.delete(tempDelNeck, tempDelHead, tempDelJaw, tempDelChin)
                
                # zeroOut controls:
                self.zeroCtrlList = utils.zeroOut([self.neckCtrl, self.headCtrl, self.jawCtrl, self.chinCtrl])
                
                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[3], self.jawCtrl, absolute=True)
                cmds.parent(self.zeroCtrlList[2], self.headCtrl, absolute=True)
                
                # make joints ride controls:
                cmds.makeIdentity(self.neckJnt, self.headJxt, self.headJnt, self.jawJnt, self.chinJnt, self.endJnt, rotate=True, apply=True)
                cmds.parentConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_parentConstraint")
                tempToDeleteJxt = cmds.parentConstraint(self.headCtrl, self.headJxt, maintainOffset=False)
                cmds.parentConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_parentConstraint")
                cmds.parentConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_parentConstraint")
                cmds.parentConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_parentConstraint")
                tempToDeleteEnd = cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False)
                cmds.delete(tempToDeleteJxt, tempToDeleteEnd)
                
                # create interations between neck and head:
                self.grpNeck = cmds.group(self.zeroCtrlList[0], name=self.neckCtrl+"_grp")
                self.grpHeadB = cmds.group(self.zeroCtrlList[1], name=self.headCtrl+"_B_grp")
                self.grpHeadA = cmds.group(self.grpHeadB, name=self.headCtrl+"_A_grp")
                self.grpHead = cmds.group(self.grpHeadA, name=self.headCtrl+"_grp")
                # store grpHeadB in the list to integrate:
                self.grpHeadBList.append(self.grpHeadB)
                # arrange pivots:
                self.neckPivot = cmds.xform(self.neckCtrl, query=True, worldSpace=True, translation=True)
                self.headPivot = cmds.xform(self.headCtrl, query=True, worldSpace=True, translation=True)
                cmds.xform(self.grpNeck, pivots=(self.neckPivot[0], self.neckPivot[1], self.neckPivot[2]))
                cmds.xform(self.grpHead, self.grpHeadA, self.grpHeadB, pivots=(self.headPivot[0], self.headPivot[1], self.headPivot[2]))
                
                self.worldRef = cmds.group(empty=True, name=side+self.userGuideName+"_worldRef")
                cmds.pointConstraint(self.headJxt, self.grpHeadB, maintainOffset=True, name=self.grpHeadB+"_pointConstraint")
                parentConst = cmds.parentConstraint(self.headJxt, self.worldRef, self.grpHeadA, maintainOffset=True, name=self.grpHeadA+"_parentConstraint")[0]
                orientConst = cmds.orientConstraint(self.grpHeadA, self.grpHeadB, maintainOffset=True, name=self.grpHeadB+"_orientConstraint")[0]
                # connect reverseNode:
                cmds.addAttr(self.headCtrl, longName=self.langDic[self.langName]['c_follow'], attributeType='float', minValue=0, maxValue=1, keyable=True)
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c_follow'], parentConst+"."+self.headJxt+"W0", force=True)
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c_follow'], orientConst+"."+self.grpHeadA+"W0", force=True)
                self.headRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_rev")
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c_follow'], self.headRevNode+".inputX", force=True)
                cmds.connectAttr(self.headRevNode+'.outputX', parentConst+"."+self.worldRef+"W1", force=True)
                self.headRevNodeList.append(self.headRevNode)
                
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
                cmds.parent(loc, self.worldRef, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                
                # hiding visibility attributes:
                ctrls.setLockHide([self.headCtrl, self.neckCtrl, self.jawCtrl, self.chinCtrl], ['v'], l=False)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.grpNeck, name=side+self.userGuideName+"_control_grp")
                self.toScalableHookGrp = cmds.group(self.neckJnt, name=side+self.userGuideName+"_joint_grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.grpHead, self.worldRef, name=side+self.userGuideName+"_grp")
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
                                                "grpHeadBList"     : self.grpHeadBList,
                                                "headRevNodeList"  : self.headRevNodeList,
                                              }
                                    }
