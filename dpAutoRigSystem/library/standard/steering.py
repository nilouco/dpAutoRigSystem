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
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc], 
                                   ["JointLoc1", "JointEnd"])
    

    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line, self.line_end])
        cmds.setAttr(self.guide_end_loc+".tz", 3)
        # parenting
        cmds.parent(self.line, self.guide_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.parentConstraint(self.guide_end_loc, self.line_end, maintainOffset=False, name=self.line_end+"_PaC")


    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".translateY", 3)
        cmds.setAttr(self.guide_base+".rotateX", 45)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.steering_ctrls = []
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.number_name+"_Guide_JointLoc1"
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = cmds.joint(name=side+self.number_name+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.create_end_joint(side+self.number_name, ty=1)
                # joint labelling:
                self.ar.utils.set_joint_label(self.jnt, s+self.joint_label_add, 18, self.number_name+"_1")
                # create a control:
                steering_ctrl = self.ar.ctrls.create_controller("id_065_SteeringWheel", side+self.number_name+"_"+self.ar.data.lang['m158_steering']+"_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc1")
                main_ctrl = self.ar.ctrls.create_controller("id_066_SteeringMain", side+self.number_name+"_"+self.ar.data.lang['c058_main']+"_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointEnd", parent_tag=steering_ctrl)
                self.ar.utils.set_origined_from_attr(steering_ctrl, self.guide)
                self.ar.utils.set_origined_from_attr(main_ctrl, self.base+";"+self.guide_end_loc+";"+self.guide_radius)
                self.steering_ctrls.append(steering_ctrl)
                # position and orientation of joint and control:
                cmds.matchTransform(self.jnt, self.guide, position=True, rotation=True)
                cmds.matchTransform(steering_ctrl, self.guide, position=True, rotation=True)
                cmds.matchTransform(main_ctrl, self.guide_end_loc, position=True, rotation=True)
                # create_zero_out controls:
                zeros = self.ar.utils.create_zero_out([steering_ctrl, main_ctrl])
                # hide visibility attribute:
                self.ar.ctrls.set_lock_hide([steering_ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.setAttr(zeros[0]+".scaleX", -1)
                        cmds.setAttr(zeros[0]+".scaleY", -1)
                        cmds.setAttr(zeros[0]+".scaleZ", -1)
                cmds.addAttr(steering_ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                cmds.setAttr(steering_ctrl+".scaleCompensate", channelBox=True)
                cmds.connectAttr(steering_ctrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                # integrating setup:
                cmds.addAttr(steering_ctrl, longName=self.ar.data.lang['c071_limit'], defaultValue=500, attributeType="float", keyable=False)
                cmds.addAttr(steering_ctrl, longName=self.ar.data.lang['c049_intensity'], min=0, defaultValue=0.8, attributeType="float", keyable=False)
                cmds.addAttr(steering_ctrl, longName=self.ar.data.lang['c070_steering'], attributeType="float", keyable=False)
                cmds.setAttr(steering_ctrl+"."+self.ar.data.lang['c071_limit'], 500, channelBox=True)
                cmds.setAttr(steering_ctrl+"."+self.ar.data.lang['c049_intensity'], 0.8, channelBox=True)
                unit_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Unit_MD")
                invert_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Rotate_MD")
                steering_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_MD")
                self.to_ids.extend([unit_md, invert_md, steering_md])
                cmds.setAttr(invert_md+".input2X", 0.1)
                cmds.setAttr(unit_md+".input2X", -1)
                cmds.transformLimits(steering_ctrl, enableRotationZ=(1, 1))
                cmds.connectAttr(steering_ctrl+"."+self.ar.data.lang['c071_limit'], unit_md+".input1X", force=True)
                cmds.connectAttr(unit_md+".outputX", steering_ctrl+".minRotLimit.minRotZLimit", force=True)
                cmds.connectAttr(steering_ctrl+"."+self.ar.data.lang['c071_limit'], steering_ctrl+".maxRotLimit.maxRotZLimit", force=True)
                cmds.connectAttr(steering_ctrl+".rotateZ", invert_md+".input1X", force=True)
                cmds.connectAttr(invert_md+".outputX", steering_md+".input1X", force=True)
                cmds.connectAttr(steering_ctrl+"."+self.ar.data.lang['c049_intensity'], steering_md+".input2X", force=True)
                cmds.connectAttr(steering_md+".outputX", steering_ctrl+"."+self.ar.data.lang['c070_steering'], force=True)
                
                # calibration attributes:
                steering_calibrates = [
                                            self.ar.data.lang['c071_limit'],
                                            self.ar.data.lang['c049_intensity']
                                            ]
                self.ar.ctrls.set_string_attr_from_items(steering_ctrl, steering_calibrates)

                # grouping:
                cmds.parent(zeros[0], main_ctrl)
                # create parentConstraint from steeringCtrl to jnt:
                cmds.parentConstraint(steering_ctrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                # create scaleConstraint from steeringCtrl to jnt:
                cmds.scaleConstraint(steering_ctrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [zeros[1]], [side+self.number_name+"_1_Jnt"])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.custom_attr.add_attr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "steeringCtrlList"   : self.steering_ctrls,
                        }
