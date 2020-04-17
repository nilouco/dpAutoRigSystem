# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Steering"
TITLE = "m158_steering"
DESCRIPTION = "m159_steeringDesc"
ICON = "/Icons/dp_steering.png"


class Steering(Base.StartClass, Layout.LayoutClass):
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
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        self.cvJointLoc, shapeSizeCH = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_ParentConstraint")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_ParentConstraint")
        
        cmds.setAttr(self.moduleGrp+".translateY", 3)
        cmds.setAttr(self.moduleGrp+".rotateX", 45)
    
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declare lists to store names and attributes:
            self.steeringCtrlList = []
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
                
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.userGuideName+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd")
                # joint labelling:
                utils.setJointLabel(self.jnt, s+jointLabelAdd, 18, self.userGuideName+"_1")
                # create a control:
                self.steeringCtrl = self.ctrls.cvControl("id_065_SteeringWheel", side+self.userGuideName+"_"+self.langDic[self.langName]['m158_steering']+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                self.mainCtrl = self.ctrls.cvControl("id_066_SteeringMain", side+self.userGuideName+"_"+self.langDic[self.langName]['c058_main']+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                utils.originedFrom(objName=self.steeringCtrl, attrString=self.base+";"+self.guide)
                utils.originedFrom(objName=self.mainCtrl, attrString=self.base+";"+self.guide)
                self.steeringCtrlList.append(self.steeringCtrl)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.steeringCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.mainCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                cmds.setAttr(self.endJoint+".translateY", 1)
                # zeroOut controls:
                zeroOutCtrlGrpList = utils.zeroOut([self.steeringCtrl, self.mainCtrl])
                # hide visibility attribute:
                self.ctrls.setLockHide([self.steeringCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v'])
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleX", -1)
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleY", -1)
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleZ", -1)
                cmds.addAttr(self.steeringCtrl, longName='scaleCompensate', attributeType="bool", keyable=False)
                cmds.setAttr(self.steeringCtrl+".scaleCompensate", 1, channelBox=True)
                cmds.connectAttr(self.steeringCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                # integrating setup:
                cmds.addAttr(self.steeringCtrl, longName=self.langDic[self.langName]['c071_limit'], defaultValue=500, attributeType="float", keyable=False)
                cmds.addAttr(self.steeringCtrl, longName=self.langDic[self.langName]['c049_intensity'], min=0, defaultValue=0.8, attributeType="float", keyable=False)
                cmds.addAttr(self.steeringCtrl, longName=self.langDic[self.langName]['c070_steering'], attributeType="float", keyable=False)
                cmds.setAttr(self.steeringCtrl+"."+self.langDic[self.langName]['c071_limit'], 500, channelBox=True)
                cmds.setAttr(self.steeringCtrl+"."+self.langDic[self.langName]['c049_intensity'], 0.8, channelBox=True)
                self.steeringUnitMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_Unit_MD")
                self.steeringInvertMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_Rotate_MD")
                self.steeringMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_MD")
                cmds.setAttr(self.steeringInvertMD+".input2X", 0.1)
                cmds.setAttr(self.steeringUnitMD+".input2X", -1)
                cmds.transformLimits(self.steeringCtrl, enableRotationZ=(1, 1))
                cmds.connectAttr(self.steeringCtrl+"."+self.langDic[self.langName]['c071_limit'], self.steeringUnitMD+".input1X", force=True)
                cmds.connectAttr(self.steeringUnitMD+".outputX", self.steeringCtrl+".minRotLimit.minRotZLimit", force=True)
                cmds.connectAttr(self.steeringCtrl+"."+self.langDic[self.langName]['c071_limit'], self.steeringCtrl+".maxRotLimit.maxRotZLimit", force=True)
                cmds.connectAttr(self.steeringCtrl+".rotateZ", self.steeringInvertMD+".input1X", force=True)
                cmds.connectAttr(self.steeringInvertMD+".outputX", self.steeringMD+".input1X", force=True)
                cmds.connectAttr(self.steeringCtrl+"."+self.langDic[self.langName]['c049_intensity'], self.steeringMD+".input2X", force=True)
                cmds.connectAttr(self.steeringMD+".outputX", self.steeringCtrl+"."+self.langDic[self.langName]['c070_steering'], force=True)
                
                # grouping:
                cmds.parent(zeroOutCtrlGrpList[0], self.mainCtrl)
                # create parentConstraint from steeringCtrl to jnt:
                cmds.parentConstraint(self.steeringCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_ParentConstraint")
                # create scaleConstraint from steeringCtrl to jnt:
                cmds.scaleConstraint(self.steeringCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScaleConstraint")
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(zeroOutCtrlGrpList[1], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(side+self.userGuideName+"_1_Jnt", name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
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
                                                "steeringCtrlList"   : self.steeringCtrlList,
                                              }
                                    }
