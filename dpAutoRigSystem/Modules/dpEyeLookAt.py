# importing libraries:
import maya.cmds as cmds
import dpControls as ctrls
import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:    
CLASS_NAME = "EyeLookAt"
TITLE = "m063_eyeLookAt"
DESCRIPTION = "m064_eyeLookAtDesc"
ICON = "/Icons/dp_eyeLookAt.png"


class EyeLookAt(Base.StartClass, Layout.LayoutClass):
    def __init__(self, dpUIinst, langDic, langName, userGuideName):
        Base.StartClass.__init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON)
        pass
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        self.cvJointLoc, shapeSizeCH = ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 13)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=True, name=self.jGuide1+"_ParentConstraint")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=True, name=self.jGuideEnd+"_ParentConstraint")
        cmds.scaleConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=True, name=self.jGuide1+"_ScaleConstraint")
        cmds.scaleConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=True, name=self.jGuideEnd+"_ScaleConstraint")
    
    
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
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                #for Maya2012: self.userGuideName+'_'+self.moduleGrp+"_Grp"
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type:
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # create a list to export:
            self.eyeScaleGrpList = []
            # create the main control:
            self.eyeCtrl = cmds.circle(name=self.userGuideName+"_A_Ctrl", radius=(2.25*self.ctrlRadius), normal=(0,0,1), degree=3, constructionHistory=False)[0]
            cmds.addAttr(self.eyeCtrl, longName=self.langDic[self.langName]['c_Follow'], attributeType='float', keyable=True, minValue=0, maxValue=1)
            cmds.setAttr(self.eyeCtrl+"."+self.langDic[self.langName]['c_Follow'], 1)
            cmds.move(0,-1,0, self.eyeCtrl+".cv[1]", relative=True)
            cmds.move(0,1,0, self.eyeCtrl+".cv[5]", relative=True)
            cmds.delete(cmds.parentConstraint(sideList[0]+self.userGuideName+"_Guide_JointEnd", self.eyeCtrl, maintainOffset=False))
            cmds.setAttr(self.eyeCtrl+".translateX", 0)
            self.eyeGrp = cmds.group(self.eyeCtrl, name=self.userGuideName+"_A_Grp")
            utils.zeroOut([self.eyeCtrl])
            self.upLocGrp = cmds.group(name=self.userGuideName+"_UpLoc_Grp", empty=True)
            # run for all sides:
            for s, side in enumerate(sideList):
                cmds.select(clear=True)
                self.base = side+self.userGuideName+'_Guide_Base'
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                # create a joint:
                self.jxt = cmds.joint(name=side+self.userGuideName+"_1_Jxt", scaleCompensate=False)
                self.jnt = cmds.joint(name=side+self.userGuideName+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.fkEyeCtrl = cmds.circle(name=side+self.userGuideName+"_Fk_Ctrl", radius=self.ctrlRadius, normal=(0,0,1), degree=1, sections=6, constructionHistory=False)[0]
                utils.originedFrom(objName=self.fkEyeCtrl, attrString=self.base+";"+self.guide)
                self.baseEyeCtrl = ctrls.cvBox(ctrlName=side+self.userGuideName+"_Base_Ctrl", r=self.ctrlRadius)
                utils.originedFrom(objName=self.baseEyeCtrl, attrString=self.base+";"+self.guide)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jxt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.fkEyeCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.baseEyeCtrl, maintainOffset=False))
                cmds.makeIdentity(self.baseEyeCtrl, self.fkEyeCtrl, apply=True)
                # zeroOut controls:
                eyeZeroList = utils.zeroOut([self.baseEyeCtrl, self.fkEyeCtrl])
                cmds.parent(eyeZeroList[1], self.baseEyeCtrl)
                # hide visibility attribute:
                cmds.setAttr(self.fkEyeCtrl+'.visibility', keyable=False)
                ctrls.setLockHide([self.fkEyeCtrl], ['tx', 'ty', 'tz'])
                # create end joint:
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                cmds.parent(self.endJoint, self.jnt, absolute=True)
                # create parentConstraint from ctrl to jxt:
                cmds.parentConstraint(self.fkEyeCtrl, self.jxt, maintainOffset=False, name=self.jnt+"_ParentConstraint")
                # create scaleConstraint from ctrl to jnt:
                cmds.scaleConstraint(self.fkEyeCtrl, self.jxt, maintainOffset=True, name=self.jnt+"_ScaleConstraint")
                
                # lookAt control:
                self.lookAtCtrl = cmds.circle(name=side+self.userGuideName+"_LookAt_Ctrl", radius=self.ctrlRadius, normal=(0,0,1), degree=3, constructionHistory=False)[0]
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.lookAtCtrl, maintainOffset=False))
                cmds.parent(self.lookAtCtrl, self.eyeCtrl, relative=False)
                cmds.makeIdentity(self.lookAtCtrl, apply=True)
                cmds.addAttr(self.lookAtCtrl, longName="active", attributeType="bool", defaultValue=1, keyable=True)
                
                # up locator:
                self.lUpGrpLoc = cmds.group(name=side+self.userGuideName+"_Up_Loc_Grp", empty=True)
                cmds.delete(cmds.parentConstraint(self.jnt, self.lUpGrpLoc, maintainOffset=False))
                self.lUpLoc = cmds.spaceLocator(name=side+self.userGuideName+"_Up_Loc")[0]
                cmds.delete(cmds.parentConstraint(self.jnt, self.lUpLoc, maintainOffset=False))
                cmds.move(cmds.getAttr(self.guideName+"_JointEnd.translateZ"), self.lUpLoc, moveY=True, relative=True)
                cmds.parent(self.lUpLoc, self.lUpGrpLoc, relative=False)
                cmds.parent(self.lUpGrpLoc, self.upLocGrp, relative=False)
                # look at aim constraint:
                aimConst = cmds.aimConstraint(self.lookAtCtrl, self.fkEyeCtrl+"_Zero", worldUpType="object", worldUpObject=self.upLocGrp+"|"+self.lUpGrpLoc+"|"+self.lUpLoc, maintainOffset=True)[0]
                cmds.connectAttr(self.lookAtCtrl+".active", aimConst+"."+self.lookAtCtrl+"W0", force=True)
                # eye aim rotation
                cmds.addAttr(self.fkEyeCtrl, longName="aimRotation", attributeType="float", keyable=True)
                cmds.connectAttr(self.fkEyeCtrl+".aimRotation", self.jnt+".rotateZ", force=True)
                cmds.pointConstraint(self.baseEyeCtrl, self.lUpGrpLoc, maintainOffset=True, name=self.lUpGrpLoc+"_PointConstraint")
                
                # create eyeScale setup:
                cmds.select(clear=True)
                self.eyeScaleJnt = cmds.joint(name=side+self.userGuideName+"Scale_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.eyeScaleJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                # jointScale position:
                cmds.delete(cmds.parentConstraint(self.guide, self.eyeScaleJnt, maintainOffset=False))
                # create endScale joint:
                self.endScaleJoint = cmds.joint(name=side+self.userGuideName+"Scale_JEnd")
                cmds.delete(cmds.parentConstraint(self.eyeScaleJnt, self.endScaleJoint, maintainOffset=False))
                cmds.setAttr(self.endScaleJoint+".translateZ", 1)
                # create constraints to eyeScale:
                cmds.pointConstraint(self.jnt, self.eyeScaleJnt, maintainOffset=False, name=self.eyeScaleJnt+"_PointConstraint")
                cmds.scaleConstraint(self.jnt, self.eyeScaleJnt, maintainOffset=True, name=self.eyeScaleJnt+"_ScaleConstraint")
                self.eyeScaleGrp = cmds.group(self.eyeScaleJnt, name=self.eyeScaleJnt+"_Grp")
                self.eyeScaleGrpList.append(self.eyeScaleGrp)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(eyeZeroList[0], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.jxt, self.eyeScaleGrp, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                if s == 0:
                    cmds.parent(self.eyeGrp, self.toCtrlHookGrp)
                    cmds.parent(self.upLocGrp, self.toScalableHookGrp)
                # create a locator in order to avoid delete static group:
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
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "eyeCtrl"     : self.eyeCtrl,
                                                "eyeGrp"      : self.eyeGrp,
                                                "upLocGrp"    : self.upLocGrp,
                                                "eyeScaleGrp" : self.eyeScaleGrpList,
                                              }
                                    }