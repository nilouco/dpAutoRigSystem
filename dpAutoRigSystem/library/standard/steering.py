# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Steering"
TITLE = "m158_steering"
DESCRIPTION = "m159_steeringDesc"
WIKI = "03-‐-Guides#-steering"



class Steering(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    
    
    def create_guide(self, *args):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.cvJointLoc, self.cvEndJoint], 
                                   ["JointLoc1", "JointEnd"])
    

    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.cvJointLoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.cvEndJoint = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.jGuide1 = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.jGuideEnd = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.jGuide1, self.jGuideEnd])
        cmds.setAttr(self.cvEndJoint+".tz", 3)
        # parenting
        cmds.parent(self.jGuide1, self.cvJointLoc, self.guide_base, relative=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        # edit
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        

    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".translateY", 3)
        cmds.setAttr(self.guide_base+".rotateX", 45)


        
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.steeringCtrlList = []
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.number_name+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.number_name+"_Guide_JointEnd"
                self.radiusGuide = side+self.number_name+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.number_name+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.endJoint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.joint_end_attr, radius=0.5)
                self.ar.utils.addJointEndAttr([self.endJoint])
                # joint labelling:
                self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_1")
                # create a control:
                self.steeringCtrl = self.ar.ctrls.cvControl("id_065_SteeringWheel", side+self.number_name+"_"+self.ar.data.lang['m158_steering']+"_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc1")
                self.mainCtrl = self.ar.ctrls.cvControl("id_066_SteeringMain", side+self.number_name+"_"+self.ar.data.lang['c058_main']+"_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointEnd", parentTag=self.steeringCtrl)
                self.ar.utils.originedFrom(objName=self.steeringCtrl, attrString=self.guide)
                self.ar.utils.originedFrom(objName=self.mainCtrl, attrString=self.base+";"+self.cvEndJoint+";"+self.radiusGuide)
                self.steeringCtrlList.append(self.steeringCtrl)
                # position and orientation of joint and control:
                cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.steeringCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.mainCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                cmds.setAttr(self.endJoint+".translateY", 1)
                # zeroOut controls:
                zeroOutCtrlGrpList = self.ar.utils.zeroOut([self.steeringCtrl, self.mainCtrl])
                # hide visibility attribute:
                self.ar.ctrls.setLockHide([self.steeringCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleX", -1)
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleY", -1)
                        cmds.setAttr(zeroOutCtrlGrpList[0]+".scaleZ", -1)
                cmds.addAttr(self.steeringCtrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                cmds.setAttr(self.steeringCtrl+".scaleCompensate", channelBox=True)
                cmds.connectAttr(self.steeringCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                # integrating setup:
                cmds.addAttr(self.steeringCtrl, longName=self.ar.data.lang['c071_limit'], defaultValue=500, attributeType="float", keyable=False)
                cmds.addAttr(self.steeringCtrl, longName=self.ar.data.lang['c049_intensity'], min=0, defaultValue=0.8, attributeType="float", keyable=False)
                cmds.addAttr(self.steeringCtrl, longName=self.ar.data.lang['c070_steering'], attributeType="float", keyable=False)
                cmds.setAttr(self.steeringCtrl+"."+self.ar.data.lang['c071_limit'], 500, channelBox=True)
                cmds.setAttr(self.steeringCtrl+"."+self.ar.data.lang['c049_intensity'], 0.8, channelBox=True)
                self.steeringUnitMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Unit_MD")
                self.steeringInvertMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Rotate_MD")
                self.steeringMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_MD")
                self.to_ids.extend([self.steeringUnitMD, self.steeringInvertMD, self.steeringMD])
                cmds.setAttr(self.steeringInvertMD+".input2X", 0.1)
                cmds.setAttr(self.steeringUnitMD+".input2X", -1)
                cmds.transformLimits(self.steeringCtrl, enableRotationZ=(1, 1))
                cmds.connectAttr(self.steeringCtrl+"."+self.ar.data.lang['c071_limit'], self.steeringUnitMD+".input1X", force=True)
                cmds.connectAttr(self.steeringUnitMD+".outputX", self.steeringCtrl+".minRotLimit.minRotZLimit", force=True)
                cmds.connectAttr(self.steeringCtrl+"."+self.ar.data.lang['c071_limit'], self.steeringCtrl+".maxRotLimit.maxRotZLimit", force=True)
                cmds.connectAttr(self.steeringCtrl+".rotateZ", self.steeringInvertMD+".input1X", force=True)
                cmds.connectAttr(self.steeringInvertMD+".outputX", self.steeringMD+".input1X", force=True)
                cmds.connectAttr(self.steeringCtrl+"."+self.ar.data.lang['c049_intensity'], self.steeringMD+".input2X", force=True)
                cmds.connectAttr(self.steeringMD+".outputX", self.steeringCtrl+"."+self.ar.data.lang['c070_steering'], force=True)
                
                # calibration attributes:
                steeringCalibrationList = [
                                            self.ar.data.lang['c071_limit'],
                                            self.ar.data.lang['c049_intensity']
                                            ]
                self.ar.ctrls.setStringAttrFromList(self.steeringCtrl, steeringCalibrationList)

                # grouping:
                cmds.parent(zeroOutCtrlGrpList[0], self.mainCtrl)
                # create parentConstraint from steeringCtrl to jnt:
                cmds.parentConstraint(self.steeringCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                # create scaleConstraint from steeringCtrl to jnt:
                cmds.scaleConstraint(self.steeringCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [zeroOutCtrlGrpList[1]], [side+self.number_name+"_1_Jnt"])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.addAttr(0, self.to_ids) #dpID
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "steeringCtrlList"   : self.steeringCtrlList,
                        }
