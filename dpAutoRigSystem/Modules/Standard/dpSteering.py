# importing libraries:
from maya import cmds
from ..Base import dpBaseStandard
from ..Base import dpBaseLayout

# global variables to this module:    
CLASS_NAME = "Steering"
TITLE = "m158_steering"
DESCRIPTION = "m159_steeringDesc"
ICON = "/Icons/dp_steering.png"
WIKI = "03-‐-Guides#-steering"

DP_STEERING_VERSION = 2.03


class Steering(dpBaseStandard.BaseStandard, dpBaseLayout.BaseLayout):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseStandard.BaseStandard.__init__(self, *args, **kwargs)
    
    
    def createModuleLayout(self, *args):
        dpBaseStandard.BaseStandard.createModuleLayout(self)
        dpBaseLayout.BaseLayout.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        dpBaseStandard.BaseStandard.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        
        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        
        cmds.setAttr(self.moduleGrp+".translateY", 3)
        cmds.setAttr(self.moduleGrp+".rotateX", 45)
        # include nodes into net
        self.addNodeToGuideNet([self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointEnd"])
    
    
    def rigModule(self, *args):
        dpBaseStandard.BaseStandard.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # declare lists to store names and attributes:
            self.steeringCtrlList = []
            # run for all sides
            for s, side in enumerate(self.sideList):
                self.base = side+self.userGuideName+'_Guide_Base'
                
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.userGuideName+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_"+self.dpUIinst.jointEndAttr, radius=0.5)
                self.utils.addJointEndAttr([self.endJoint])
                # joint labelling:
                self.utils.setJointLabel(self.jnt, s+self.jointLabelAdd, 18, self.userGuideName+"_1")
                # create a control:
                self.steeringCtrl = self.ctrls.cvControl("id_065_SteeringWheel", side+self.userGuideName+"_"+self.dpUIinst.lang['m158_steering']+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree, guideSource=self.guideName+"_JointLoc1")
                self.mainCtrl = self.ctrls.cvControl("id_066_SteeringMain", side+self.userGuideName+"_"+self.dpUIinst.lang['c058_main']+"_Ctrl", r=self.ctrlRadius, d=self.curveDegree, guideSource=self.guideName+"_JointEnd")
                self.utils.originedFrom(objName=self.steeringCtrl, attrString=self.guide)
                self.utils.originedFrom(objName=self.mainCtrl, attrString=self.base+";"+self.cvEndJoint+";"+self.radiusGuide)
                self.steeringCtrlList.append(self.steeringCtrl)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.steeringCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.mainCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                cmds.setAttr(self.endJoint+".translateY", 1)
                # zeroOut controls:
                zeroOutCtrlGrpList = self.utils.zeroOut([self.steeringCtrl, self.mainCtrl])
                # hide visibility attribute:
                self.ctrls.setLockHide([self.steeringCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleX", -1)
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleY", -1)
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleZ", -1)
                cmds.addAttr(self.steeringCtrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                cmds.setAttr(self.steeringCtrl+".scaleCompensate", channelBox=True)
                cmds.connectAttr(self.steeringCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                # integrating setup:
                cmds.addAttr(self.steeringCtrl, longName=self.dpUIinst.lang['c071_limit'], defaultValue=500, attributeType="float", keyable=False)
                cmds.addAttr(self.steeringCtrl, longName=self.dpUIinst.lang['c049_intensity'], min=0, defaultValue=0.8, attributeType="float", keyable=False)
                cmds.addAttr(self.steeringCtrl, longName=self.dpUIinst.lang['c070_steering'], attributeType="float", keyable=False)
                cmds.setAttr(self.steeringCtrl+"."+self.dpUIinst.lang['c071_limit'], 500, channelBox=True)
                cmds.setAttr(self.steeringCtrl+"."+self.dpUIinst.lang['c049_intensity'], 0.8, channelBox=True)
                self.steeringUnitMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_Unit_MD")
                self.steeringInvertMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_Rotate_MD")
                self.steeringMD = cmds.createNode('multiplyDivide', name=side+self.userGuideName+"_MD")
                self.toIDList.extend([self.steeringUnitMD, self.steeringInvertMD, self.steeringMD])
                cmds.setAttr(self.steeringInvertMD+".input2X", 0.1)
                cmds.setAttr(self.steeringUnitMD+".input2X", -1)
                cmds.transformLimits(self.steeringCtrl, enableRotationZ=(1, 1))
                cmds.connectAttr(self.steeringCtrl+"."+self.dpUIinst.lang['c071_limit'], self.steeringUnitMD+".input1X", force=True)
                cmds.connectAttr(self.steeringUnitMD+".outputX", self.steeringCtrl+".minRotLimit.minRotZLimit", force=True)
                cmds.connectAttr(self.steeringCtrl+"."+self.dpUIinst.lang['c071_limit'], self.steeringCtrl+".maxRotLimit.maxRotZLimit", force=True)
                cmds.connectAttr(self.steeringCtrl+".rotateZ", self.steeringInvertMD+".input1X", force=True)
                cmds.connectAttr(self.steeringInvertMD+".outputX", self.steeringMD+".input1X", force=True)
                cmds.connectAttr(self.steeringCtrl+"."+self.dpUIinst.lang['c049_intensity'], self.steeringMD+".input2X", force=True)
                cmds.connectAttr(self.steeringMD+".outputX", self.steeringCtrl+"."+self.dpUIinst.lang['c070_steering'], force=True)
                
                # calibration attributes:
                steeringCalibrationList = [
                                            self.dpUIinst.lang['c071_limit'],
                                            self.dpUIinst.lang['c049_intensity']
                                            ]
                self.ctrls.setStringAttrFromList(self.steeringCtrl, steeringCalibrationList)

                # grouping:
                cmds.parent(zeroOutCtrlGrpList[0], self.mainCtrl)
                # create parentConstraint from steeringCtrl to jnt:
                cmds.parentConstraint(self.steeringCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                # create scaleConstraint from steeringCtrl to jnt:
                cmds.scaleConstraint(self.steeringCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.hookSetup(side, [zeroOutCtrlGrpList[1]], [side+self.userGuideName+"_1_Jnt"])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
                self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
        self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID
    
    
    def integratingInfo(self, *args):
        dpBaseStandard.BaseStandard.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "steeringCtrlList"   : self.steeringCtrlList,
                                              }
                                    }
