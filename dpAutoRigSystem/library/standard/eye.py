# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Eye"
TITLE = "m063_eye"
DESCRIPTION = "m064_eyeDesc"
WIKI = "03-‐-Guides#-eye"

EYELID = "eyelid"
IRIS = "iris"
PUPIL = "pupil"
SPEC = "specular"
PIVOT = "lidPivot"



class Eye(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.corrective_value = 70
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc, self.guide_lid_pivot_loc, self.guide_upper_eyelid_loc, self.guide_lower_eyelid_loc, self.guide_iris_loc, self.guide_pupil_loc, self.guide_specular_loc], 
                                    ["JointLoc1", "JointEnd", "_LidPivotLoc", "_UpperEyelidLoc", "_LowerEyelidLoc", "_IrisLoc", "_PupilLoc", "_SpecularLoc"])

    
    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="aimDirection", attributeType='enum', enumName="+X:-X:+Y:-Y:+Z:-Z")
        cmds.addAttr(self.guide_base, longName="aimDirectionName", dataType='string')
        cmds.addAttr(self.guide_base, longName="aimDirectionPositive", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName=EYELID, defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName=IRIS, defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName=PUPIL, defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName=SPEC, attributeType='bool')
        cmds.addAttr(self.guide_base, longName=PIVOT, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=1, maxValue=3, attributeType='long')
        cmds.addAttr(self.guide_base, longName="corrective", attributeType='bool')
        cmds.setAttr(self.guide_base+".aimDirection", 4)
        cmds.setAttr(self.guide_base+".aimDirectionName", "Z", type="string")


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_controller("id_059_AimLoc", ctrl_name=self.name_guide+"_JointEnd", r=0.5, d=1, rot=(-90, 0, -90))
        self.guide_lid_pivot_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_LidPivotLoc", r=0.5, d=1, guide=True)
        self.guide_upper_eyelid_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_UpperEyelidLoc", r=0.2, d=1, guide=True)
        self.guide_lower_eyelid_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_LowerEyelidLoc", r=0.2, d=1, guide=True)
        self.guide_iris_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_IrisLoc", r=0.15, d=1, guide=True)
        self.guide_pupil_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_PupilLoc", r=0.12, d=1, guide=True)
        self.guide_specular_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_SpecularLoc", r=0.12, d=1, guide=True)
        self.guide_up_loc = cmds.spaceLocator(name=self.guide_end_loc+"_UpLoc")[0]
        # joints
        self.line = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.line_eyelid = cmds.joint(name=self.name_guide+"_JEyelid", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        self.line_upper_eyelid = cmds.joint(name=self.name_guide+"_JUpperEyelid", radius=0.001)
        self.line_lower_eyelid = cmds.joint(name=self.name_guide+"_JLowerEyelid", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line, self.line_end, self.line_upper_eyelid, self.line_lower_eyelid])
        cmds.setAttr(self.guide_end_loc+".tz", 13)
        cmds.setAttr(self.guide_up_loc+".ty", 13)
        cmds.setAttr(self.guide_upper_eyelid_loc+".ty", 0.5)
        cmds.setAttr(self.guide_upper_eyelid_loc+".tz", 0.5)
        cmds.setAttr(self.guide_lower_eyelid_loc+".ty", -0.5)
        cmds.setAttr(self.guide_lower_eyelid_loc+".tz", 0.5)
        cmds.setAttr(self.guide_iris_loc+".tz", 0.4)
        cmds.setAttr(self.guide_pupil_loc+".tz", 0.3)
        cmds.setAttr(self.guide_specular_loc+".tz", 1)
        cmds.setAttr(self.guide_up_loc+".visibility", 0)
        cmds.setAttr(self.guide_specular_loc+".visibility", 0)
        cmds.setAttr(self.guide_lid_pivot_loc+"0Shape.visibility", 0)
        # parenting
        self.guide_end_loc_zero = cmds.group(self.guide_end_loc, self.guide_up_loc, name=self.guide_end_loc+"_Grp")
        self.guide_end_back_rot_zero = cmds.group(self.guide_end_loc_zero, name=self.guide_end_loc_zero+"_Back_Grp")
        cmds.parent(self.line, self.guide_base, relative=True)
        cmds.parent(self.guide_loc, self.guide_end_back_rot_zero, self.guide_base)
        cmds.parent(self.guide_lid_pivot_loc, self.guide_iris_loc, self.guide_pupil_loc, self.guide_loc)
        cmds.parent(self.guide_upper_eyelid_loc, self.guide_lower_eyelid_loc, self.guide_lid_pivot_loc)
        cmds.parent(self.guide_specular_loc, self.guide_loc)
        cmds.parent(self.line_upper_eyelid, self.line_lower_eyelid, self.line_eyelid)
        cmds.parent(self.line_end, self.line)
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.parentConstraint(self.guide_upper_eyelid_loc, self.line_upper_eyelid, maintainOffset=False, name=self.line_upper_eyelid+"_PaC")
        cmds.parentConstraint(self.guide_lower_eyelid_loc, self.line_lower_eyelid, maintainOffset=False, name=self.line_lower_eyelid+"_PaC")
        cmds.parentConstraint(self.guide_end_loc, self.line_end, maintainOffset=False, name=self.line_end+"_PaC")
        cmds.parentConstraint(self.guide_lid_pivot_loc, self.line_eyelid, maintainOffset=False, name=self.line_eyelid+"_PaC")
        # edit
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        cmds.orientConstraint(self.ar.data.temp_grp, self.guide_end_back_rot_zero, maintainOffset=False, name=self.guide_end_back_rot_zero+"_OrC")
        self.ar.ctrls.color_shape([self.guide_end_loc], "blue")
        self.ar.ctrls.shape_size_setup(self.guide_end_loc)
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        self.ar.ctrls.set_lock_hide([self.guide_upper_eyelid_loc, self.guide_lower_eyelid_loc], ['tx', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def change_eyelid(self, value, *args):
        """ Set the attribute value for eyelid.
        """
        cmds.setAttr(self.guide_base+".eyelid", value)
        cmds.setAttr(self.name_guide+"_UpperEyelidLoc.visibility", value)
        cmds.setAttr(self.name_guide+"_LowerEyelidLoc.visibility", value)
        cmds.setAttr(self.name_guide+"_JEyelid.visibility", value)
        cmds.setAttr(self.name_guide+"_JUpperEyelid.visibility", value)
        cmds.setAttr(self.name_guide+"_JLowerEyelid.visibility", value)
        self.change_lid_pivot(value)
        
        
    def change_eye_guide_attr(self, attr, value, *args):
        """ Set the attribute value for specular.
        """
        cmds.setAttr(f"{self.guide_base}.{attr}", value)
        cmds.setAttr(f"{self.name_guide}_{attr.capitalize()}Loc.visibility", value)


    def change_lid_pivot(self, value, *args):
        """ Set the attribute value for eyelid center pivot.
        """
        cmds.setAttr(self.guide_base+".lidPivot", value)
        cmds.setAttr(self.name_guide+"_LidPivotLoc0Shape.visibility", value)
    
    
    def change_aim_direction(self, value, *args):
        """ Set the good direction for Eye look at Aim setup.
        """
        if self.check_guide_integrity():
            # re-declaring variables:
            self.line_end = self.name_guide+"_JGuideEnd"
            self.guide_end_loc_zero = self.name_guide+"_JointEnd_Grp"
            # setting attributes:
            cmds.setAttr(self.guide_base+".aimDirection", self.ar.data.directions.index(value))
            cmds.setAttr(self.guide_base+".aimDirectionName", value[1], type='string')
            cmds.setAttr(self.guide_base+".aimDirectionPositive", 0)
            if value[0] == "+":
                cmds.setAttr(self.guide_base+".aimDirectionPositive", 1)
            # changing module aim guides:
            cmds.setAttr(self.guide_end_loc_zero+".rotateX", 0)
            cmds.setAttr(self.guide_end_loc_zero+".rotateY", 0)
            if value[1] == "X":
                if value[0] == "+":
                    cmds.setAttr(self.guide_end_loc_zero+".rotateY", 90)
                else:
                    cmds.setAttr(self.guide_end_loc_zero+".rotateY", -90)
            if value[1] == "Y":
                if value[0] == "+":
                    cmds.setAttr(self.guide_end_loc_zero+".rotateX", -90)
                else:
                    cmds.setAttr(self.guide_end_loc_zero+".rotateX", 90)
            if value[1] == "Z":
                if value[0] == "-":
                    cmds.setAttr(self.guide_end_loc_zero+".rotateY", 180)
    
    
    def create_eyelids_joints(self, side, lid, middle, guide_eyelid_loc, joint_label_number):
        ''' Create the eyelid joints to be used in the needed setup.
            Returns EyelidBaseJxt and EyelidJnt created for rotate and skinning.
        '''
        # declating a concatenated name used for base to compose:
        base_name = side+self.number_name+"_"+self.ar.data.lang[lid]+"_"+self.ar.data.lang['c042_eyelid']+middle
        # creating joints:
        eyelid_base_zero_jxt = cmds.joint(name=base_name+"_Base_Zero_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelid_base_jxt = cmds.joint(name=base_name+"_Base_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelid_zero_jxt = cmds.joint(name=base_name+"_Zero_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelid_jnt = cmds.joint(name=base_name+"_Jnt", rotationOrder="yzx", scaleCompensate=False)
        cmds.addAttr(eyelid_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
        self.ar.utils.setJointLabel(eyelid_jnt, joint_label_number, 18, self.number_name+"_"+self.ar.data.lang[lid]+"_"+self.ar.data.lang['c042_eyelid']+middle)
        cmds.select(eyelid_zero_jxt)
        eyelid_support_jxt = cmds.joint(name=base_name+"_Jxt", rotationOrder="yzx", scaleCompensate=False)
        cmds.setAttr(eyelid_support_jxt+".translateX", self.radius*0.1)
        # positioning and orienting correctely eyelid joints:
        cmds.delete(cmds.aimConstraint(guide_eyelid_loc, eyelid_base_zero_jxt, aimVector=(0,0,1), worldUpType="objectrotation", worldUpObject=self.eyelid_jxt))
        cmds.matchTransform(eyelid_zero_jxt, guide_eyelid_loc, position=True, rotation=True)
        cmds.setAttr(eyelid_zero_jxt+".rotateX", 0)
        cmds.setAttr(eyelid_zero_jxt+".rotateY", 0)
        cmds.setAttr(eyelid_zero_jxt+".rotateZ", 0)
        cmds.select(self.eyelid_jxt)
        return eyelid_base_jxt, eyelid_jnt


    def create_eyelid_setup(self, side, lid, eyelid_jnt, eyelid_base_jxt, eyelid_middle_base_jxt, eyelid_middle_jnt, preset, rot_ctrl, guide_eyelid_loc):
        ''' Work with the joints created in order to develop a solid and stable eyelid setup for blink and facial eye expressions using direct skinning process in the final render mesh.
            Returns the main controller and its zeroOut group.
        '''
        # declating a concatenated name used for base to compose:
        base_name = side+self.number_name+"_"+self.ar.data.lang[lid]+"_"+self.ar.data.lang['c042_eyelid']
        # creating eyelid control:
        eyelid_ctrl = self.ar.ctrls.create_controller("id_008_Eyelid", base_name+"_Ctrl", self.radius*0.4, d=self.curve_degree, rot=rot_ctrl, head_def=self.head_def_value, guide_source=self.name_guide+"__"+guide_eyelid_loc.replace("_Guide", ":Guide"), parent_tag=self.fk_eye_sub_ctrl)
        self.ar.utils.originedFrom(objName=eyelid_ctrl, attrString=guide_eyelid_loc)
        eyelid_ctrl_zero = self.ar.utils.zeroOut([eyelid_ctrl])[0]
        self.ar.ctrls.set_lock_hide([eyelid_ctrl], ['tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
        cmds.parent(eyelid_ctrl_zero, self.base_eye_ctrl)
        # positioning correctely eyelid control:
        cmds.matchTransform(eyelid_ctrl_zero, self.eyelid_jxt, position=True, rotation=True)
        cmds.delete(cmds.pointConstraint(eyelid_jnt, eyelid_ctrl_zero, mo=False))
        cmds.xform(eyelid_ctrl_zero, translation=(0, 0, self.radius), relative=True)
        # adding useful control attributes to calibrate eyelid setup:
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c049_intensity']+"X", attributeType="float", minValue=0, defaultValue=1)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c049_intensity']+"Y", attributeType="float", minValue=0, defaultValue=1)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType="float", minValue=0, defaultValue=0.6, maxValue=1)
        cmds.setAttr(eyelid_ctrl+"."+self.ar.data.lang['c049_intensity']+"X", keyable=False, channelBox=True)
        cmds.setAttr(eyelid_ctrl+"."+self.ar.data.lang['c049_intensity']+"Y", keyable=False, channelBox=True)
        cmds.setAttr(eyelid_ctrl+"."+self.ar.data.lang['c032_follow'], channelBox=True)
        cmds.setAttr(eyelid_ctrl+"."+self.ar.data.lang['c032_follow'], keyable=True)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c053_invert']+"X", attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c053_invert']+"Y", attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c051_preset']+"X", attributeType="float", defaultValue=preset, keyable=False)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c051_preset']+"Y", attributeType="float", defaultValue=preset, keyable=False)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], attributeType="float", minValue=0, defaultValue=0.5, maxValue=1, keyable=False)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c052_fix']+"ScaleX", attributeType="float", defaultValue=0.01, minValue=0, keyable=False)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c052_fix']+"TranslateZ", attributeType="float", defaultValue=0.15, minValue=0, keyable=False)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c052_fix']+self.ar.data.lang['c029_middle']+"TranslateZ", attributeType="float", defaultValue=0.3, minValue=0, keyable=False)
        cmds.addAttr(eyelid_ctrl, longName=self.ar.data.lang['c107_reduce']+self.ar.data.lang['c029_middle']+"Open", attributeType="float", defaultValue=0.2, minValue=0, maxValue=1, keyable=False)
        # creating utility nodes to eyelid setup:
        eyelid_intensity_md = cmds.createNode('multiplyDivide', name=base_name+"_Intensity_MD")
        eyelid_invert_md = cmds.createNode('multiplyDivide', name=base_name+"_Invert_MD")
        eyelid_invert_x_cnd = cmds.createNode('condition', name=base_name+"_InvertX_Cnd")
        eyelid_invert_y_cnd = cmds.createNode('condition', name=base_name+"_InvertY_Cnd")
        eyelid_invert_middle_cnd = cmds.createNode('condition', name=base_name+"_InvertY_Middle_Cnd")
        eyelid_invert_fix_middle_cnd = cmds.createNode('condition', name=base_name+"_InvertFix_Middle_Cnd")
        eyelid_preset_md = cmds.createNode('multiplyDivide', name=base_name+"_Preset_MD")
        eyelid_middle_md = cmds.createNode('multiplyDivide', name=base_name+"_Middle_MD")
        eyelid_middle_cnd = cmds.createNode('condition', name=base_name+"_Middle_Cnd")
        eyelid_fix_md = cmds.createNode('multiplyDivide', name=base_name+"_Fix_MD")
        eyelid_fix_pma = cmds.createNode('plusMinusAverage', name=base_name+"_Fix_PMA")
        eyelid_fix_modulus_x_cnd = cmds.createNode('condition', name=base_name+"_Fix_ModulusX_Cnd")
        eyelid_fix_modulus_y_middle_cnd = cmds.createNode('condition', name=base_name+"_Fix_ModulusYMiddle_Cnd")
        eyelid_fix_modulus_y_cnd = cmds.createNode('condition', name=base_name+"_Fix_ModulusY_Cnd")
        eyelid_fix_negative_md = cmds.createNode('multiplyDivide', name=base_name+"_Fix_Negative_MD")
        eyelid_reduce_open_middle_md = cmds.createNode('multiplyDivide', name=base_name+"_Reduce_MiddleOpen_MD")
        eyelid_invert_open_middle_md = cmds.createNode('multiplyDivide', name=base_name+"_Invert_MiddleOpen_MD")
        eyelid_fix_invert_open_middle_md = cmds.createNode('multiplyDivide', name=base_name+"_Fix_Invert_MiddleOpen_MD")
        eyelid_fix_middle_md = cmds.createNode('multiplyDivide', name=base_name+"_Fix_Middle_MD")
        eyelid_fix_middle_tz_md = cmds.createNode('multiplyDivide', name=base_name+"_Fix_MiddleTZ_MD")
        eyelid_fix_middle_scale_clp = cmds.createNode('clamp', name=base_name+"_Fix_Middle_Clp")
        eyelid_follow_rev = cmds.createNode('reverse', name=base_name+"_Follow_Rev")
        self.to_ids.extend([eyelid_intensity_md, eyelid_invert_md, eyelid_invert_x_cnd, eyelid_invert_y_cnd, eyelid_invert_middle_cnd, eyelid_invert_fix_middle_cnd, eyelid_preset_md, eyelid_middle_md, eyelid_middle_cnd, eyelid_fix_md,
                              eyelid_fix_pma, eyelid_fix_modulus_x_cnd, eyelid_fix_modulus_y_middle_cnd, eyelid_fix_modulus_y_cnd, eyelid_fix_negative_md, eyelid_reduce_open_middle_md, eyelid_invert_open_middle_md, eyelid_fix_invert_open_middle_md,
                              eyelid_fix_middle_md, eyelid_fix_middle_tz_md, eyelid_fix_middle_scale_clp, eyelid_follow_rev])
        # seting up the node attributes:
        cmds.setAttr(eyelid_invert_x_cnd+".colorIfTrueR", 1)
        cmds.setAttr(eyelid_invert_x_cnd+".colorIfFalseR", -1)
        cmds.setAttr(eyelid_invert_y_cnd+".colorIfTrueR", 1)
        cmds.setAttr(eyelid_invert_y_cnd+".colorIfFalseR", -1)
        cmds.setAttr(eyelid_invert_middle_cnd+".colorIfTrueR", 4)
        cmds.setAttr(eyelid_invert_middle_cnd+".colorIfFalseR", 2)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".secondTerm", 1)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".colorIfTrueR", 5)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".colorIfFalseR", 3)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".colorIfTrueG", -1)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".colorIfFalseG", 1)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".colorIfTrueB", 1)
        cmds.setAttr(eyelid_invert_fix_middle_cnd+".colorIfFalseB", -1)
        cmds.setAttr(eyelid_fix_negative_md+".input2X", -1)
        cmds.setAttr(eyelid_fix_modulus_x_cnd+".operation", 3)
        cmds.setAttr(eyelid_fix_pma+".input3D[0].input3Dx", 1)
        cmds.setAttr(eyelid_fix_negative_md+".input2Y", -1)
        cmds.setAttr(eyelid_fix_modulus_y_cnd+".operation", 3)
        cmds.setAttr(eyelid_fix_middle_scale_clp+".minR", 1)
        cmds.setAttr(eyelid_fix_middle_scale_clp+".maxR", 1000)
        cmds.setAttr(eyelid_middle_cnd+".colorIfFalseR", 1)
        # connecting eyelid control to nodes and joints:
        cmds.connectAttr(eyelid_ctrl+".translateX", eyelid_invert_md+".input1X", force=True)
        cmds.connectAttr(eyelid_ctrl+".translateY", eyelid_invert_md+".input1Y", force=True)
        # working with invert nodes in order to be able to adjust the control by User after the setup done:
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"X", eyelid_invert_x_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"Y", eyelid_invert_y_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"Y", eyelid_invert_middle_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], eyelid_invert_fix_middle_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_invert_x_cnd+".outColorR", eyelid_invert_md+".input2X", force=True)
        cmds.connectAttr(eyelid_invert_y_cnd+".outColorR", eyelid_invert_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_invert_md+".outputX", eyelid_intensity_md+".input1X", force=True)
        cmds.connectAttr(eyelid_invert_md+".outputY", eyelid_intensity_md+".input1Y", force=True)
        # working with intensity attributes in order to chose the control force by User:
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c049_intensity']+"X", eyelid_intensity_md+".input2X", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c049_intensity']+"Y", eyelid_intensity_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_intensity_md+".outputX", eyelid_preset_md+".input1X", force=True)
        cmds.connectAttr(eyelid_intensity_md+".outputY", eyelid_preset_md+".input1Y", force=True)
        # working with the predefined values in order to help the Rigger calibrate the control intensity preset:
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c051_preset']+"X", eyelid_preset_md+".input2X", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c051_preset']+"Y", eyelid_preset_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_preset_md+".outputX", eyelid_base_jxt+".rotateZ", force=True)
        cmds.connectAttr(eyelid_preset_md+".outputY", eyelid_base_jxt+".rotateX", force=True)
        # setup the middle extra joint to be skinned as a helper to deform correctly the mesh following the main eyelid joint:
        cmds.connectAttr(eyelid_preset_md+".outputX", eyelid_middle_md+".input1X", force=True)
        cmds.connectAttr(eyelid_preset_md+".outputY", eyelid_middle_md+".input1Y", force=True)
        # using the proximity attribute to let User chose the good deformation on the skinning:
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelid_middle_md+".input2X", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelid_middle_cnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelid_base_jxt+".rotateX", eyelid_middle_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_middle_cnd+".outColorR", eyelid_middle_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_invert_middle_cnd+".outColorR", eyelid_middle_cnd+".operation", force=True)
        cmds.connectAttr(eyelid_middle_md+".outputX", eyelid_middle_base_jxt+".rotateZ", force=True)
        cmds.connectAttr(eyelid_middle_md+".outputY", eyelid_middle_base_jxt+".rotateX", force=True)
        if "lower" in lid:
            cmds.setAttr(eyelid_invert_middle_cnd+".secondTerm", 1)
        # try to fix the maintain volume by mimic the SetDrivenKey and SculptDeform technique using nodes to scale and translate the skinned joints:
        cmds.connectAttr(eyelid_intensity_md+".outputY", eyelid_fix_md+".input1X", force=True)
        cmds.connectAttr(eyelid_intensity_md+".outputY", eyelid_fix_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_intensity_md+".outputY", eyelid_fix_middle_tz_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c052_fix']+"ScaleX", eyelid_fix_md+".input2X", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c052_fix']+"TranslateZ", eyelid_fix_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c052_fix']+self.ar.data.lang['c029_middle']+"TranslateZ", eyelid_fix_middle_tz_md+".input2Y", force=True)
        # modulus of fix values in order to avoid opositive values when the control pass to another direction from start position:
        cmds.connectAttr(eyelid_fix_md+".outputX", eyelid_fix_modulus_x_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_fix_md+".outputX", eyelid_fix_modulus_x_cnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelid_fix_md+".outputX", eyelid_fix_negative_md+".input1X", force=True)
        cmds.connectAttr(eyelid_fix_negative_md+".outputX", eyelid_fix_modulus_x_cnd+".colorIfFalseR", force=True)
        cmds.connectAttr(eyelid_fix_modulus_x_cnd+".outColorR", eyelid_fix_pma+".input3D[1].input3Dx", force=True)
        cmds.connectAttr(eyelid_fix_md+".outputY", eyelid_fix_modulus_y_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_fix_md+".outputY", eyelid_fix_modulus_y_cnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelid_fix_md+".outputY", eyelid_fix_negative_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_fix_negative_md+".outputY", eyelid_fix_modulus_y_cnd+".colorIfFalseR", force=True)
        cmds.connectAttr(eyelid_fix_pma+".output3Dx", eyelid_jnt+".scaleX", force=True)
        cmds.connectAttr(eyelid_fix_modulus_y_cnd+".outColorR", eyelid_jnt+".translateZ", force=True)
        # fixing middle joint proximity:
        cmds.connectAttr(eyelid_fix_middle_tz_md+".outputY", eyelid_reduce_open_middle_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c107_reduce']+self.ar.data.lang['c029_middle']+"Open", eyelid_reduce_open_middle_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_reduce_open_middle_md+".outputY", eyelid_invert_open_middle_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_fix_middle_tz_md+".outputY", eyelid_fix_modulus_y_middle_cnd+".firstTerm", force=True)
        cmds.connectAttr(eyelid_fix_middle_tz_md+".outputY", eyelid_fix_invert_open_middle_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_fix_invert_open_middle_md+".outputY", eyelid_fix_modulus_y_middle_cnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelid_invert_open_middle_md+".outputY", eyelid_fix_modulus_y_middle_cnd+".colorIfFalseR", force=True)
        cmds.connectAttr(eyelid_fix_modulus_y_middle_cnd+".outColorR", eyelid_fix_middle_md+".input1Y", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelid_fix_middle_md+".input2X", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelid_fix_middle_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_fix_middle_md+".outputX", eyelid_fix_middle_scale_clp+".inputR", force=True)
        cmds.connectAttr(eyelid_fix_middle_scale_clp+".outputR", eyelid_middle_jnt+".scaleX", force=True)
        cmds.connectAttr(eyelid_fix_middle_md+".outputY", eyelid_middle_jnt+".translateZ", force=True)
        cmds.connectAttr(eyelid_invert_fix_middle_cnd+".outColorR", eyelid_fix_modulus_y_middle_cnd+".operation", force=True)
        cmds.connectAttr(eyelid_invert_fix_middle_cnd+".outColorG", eyelid_fix_invert_open_middle_md+".input2Y", force=True)
        cmds.connectAttr(eyelid_invert_fix_middle_cnd+".outColorB", eyelid_invert_open_middle_md+".input2Y", force=True)
        # follow setup:
        eyelid_base_zero_jxt = cmds.listRelatives(eyelid_base_jxt, parent=True)[0]
        eyelid_middle_base_zero_jxt = cmds.listRelatives(eyelid_middle_base_jxt, parent=True)[0]
        follow_pac = cmds.parentConstraint(self.jxt, self.eye_scale_jnt, eyelid_base_zero_jxt, skipTranslate=["x", "y", "z"], skipRotate=["y", "z"], maintainOffset=1, name=base_name+"_Follow_PaC")[0]
        cmds.setAttr(follow_pac+".interpType", 2)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c032_follow'], follow_pac+"."+self.jxt+"W0", force=True)
        cmds.connectAttr(eyelid_ctrl+"."+self.ar.data.lang['c032_follow'], eyelid_follow_rev+".inputX", force=True)
        cmds.connectAttr(eyelid_follow_rev+".outputX", follow_pac+"."+self.eye_scale_jnt+"W1", force=True)
        cmds.connectAttr(eyelid_base_zero_jxt+".rotateX", eyelid_middle_base_zero_jxt+".rotateX", force=True)
        # corrective network
        if self.corrective:
            self.setup_corrective_net(eyelid_ctrl, eyelid_base_jxt, cmds.listRelatives(eyelid_base_jxt, parent=True)[0], base_name, 0, 0, -self.corrective_value)
        # calibration attribute:
        eyelid_calibrations = [
            self.ar.data.lang['c049_intensity']+"X",
            self.ar.data.lang['c049_intensity']+"Y",
            self.ar.data.lang['c032_follow'],
            self.ar.data.lang['c053_invert']+"X",
            self.ar.data.lang['c053_invert']+"Y",
            self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'],
            self.ar.data.lang['c051_preset']+"X",
            self.ar.data.lang['c051_preset']+"Y",
            self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'],
            self.ar.data.lang['c052_fix']+"ScaleX",
            self.ar.data.lang['c052_fix']+"TranslateZ",
            self.ar.data.lang['c052_fix']+self.ar.data.lang['c029_middle']+"TranslateZ",
            self.ar.data.lang['c107_reduce']+self.ar.data.lang['c029_middle']+"Open"
        ]
        eyelid_not_mirrors = [self.ar.data.lang['c053_invert']+"X",
                               self.ar.data.lang['c053_invert']+"Y",
                               self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle']]
        self.ar.ctrls.set_string_attr_from_items(eyelid_ctrl, eyelid_calibrations)
        self.ar.ctrls.set_string_attr_from_items(eyelid_ctrl, eyelid_not_mirrors, "notMirrorList") #useful to export calibrationIO and not mirror them
        return eyelid_ctrl, eyelid_ctrl_zero
        
        
    def create_iris_pupil_setup(self, s, side, type, code_name, joint_label_number):
        ''' Predefined function to add Iris or Pupil setup.
            Returns controller.
        '''
        # declare cv guides:
        guide_loc = side+self.number_name+"_Guide_"+type.capitalize()+"Loc"
        # creating joint:
        main_jnt = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang[code_name]+"_1_Jnt", scaleCompensate=False)
        cmds.addAttr(main_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
        self.ar.utils.setJointLabel(main_jnt, joint_label_number, 18, self.number_name+"_"+self.ar.data.lang[code_name]+"_1")
        # joint position:
        cmds.matchTransform(main_jnt, guide_loc, position=True, rotation=True)
        end_joint = self.create_end_joint(side+self.number_name+"_"+self.ar.data.lang[code_name], main_jnt, tz=self.radius)
        # creating control:
        if type == IRIS:
            ctrl_id = "id_012_EyeIris"
            radius = 0.4*self.radius
        else:
            ctrl_id = "id_013_EyePupil"
            radius = 0.2*self.radius
        ctrl = self.ar.ctrls.create_controller(ctrl_id, side+self.number_name+"_"+self.ar.data.lang[code_name]+"_1_Ctrl", r=radius, d=self.curve_degree, head_def=self.head_def_value, guide_source=self.name_guide+"__"+guide_loc.replace("_Guide", ":Guide"), parent_tag=self.fk_eye_sub_ctrl)
        self.ar.utils.originedFrom(objName=ctrl, attrString=guide_loc)
        cmds.makeIdentity(ctrl, rotate=True, apply=True)
        # create constraints and arrange hierarchy:
        ctrl_zero = self.ar.utils.zeroOut([ctrl], offset=True)
        cmds.setAttr(cmds.listRelatives(ctrl_zero, children=True, type="transform")[0]+".dpNotTransformIO", 0)
        cmds.matchTransform(ctrl_zero[0], guide_loc, position=True, rotation=True)
        cmds.parent(ctrl_zero[0], self.base_eye_ctrl)
        # fixing flip mirror:
        if s == 1:
            if cmds.getAttr(self.guide_base+".flip") == 1:
                if not "X" == cmds.getAttr(self.guide_base+".aimDirectionName"):
                    cmds.setAttr(ctrl_zero[0]+".scaleX", -1)
                else:
                    cmds.setAttr(ctrl_zero[0]+".scaleX", 1)
                if not "Y" == cmds.getAttr(self.guide_base+".aimDirectionName"):
                    cmds.setAttr(ctrl_zero[0]+".scaleY", -1)
                else:
                    cmds.setAttr(ctrl_zero[0]+".scaleY", 1)
                if not "Z" == cmds.getAttr(self.guide_base+".aimDirectionName"):
                    cmds.setAttr(ctrl_zero[0]+".scaleZ", -1)
                else:
                    cmds.setAttr(ctrl_zero[0]+".scaleZ", 1)
            cmds.setAttr(end_joint+".translateZ", -self.radius)
        cmds.parentConstraint(self.fk_eye_sub_ctrl, ctrl_zero[0], maintainOffset=True, name=ctrl_zero[0]+"_PaC")
        cmds.scaleConstraint(self.fk_eye_sub_ctrl, ctrl_zero[0], maintainOffset=True, name=ctrl_zero[0]+"_ScC")
        cmds.parent(main_jnt, self.jnt)
        cmds.parentConstraint(ctrl, main_jnt, maintainOffset=False, name=main_jnt+"_PaC")
        cmds.scaleConstraint(ctrl, main_jnt, maintainOffset=True, name=main_jnt+"_ScC")
        return ctrl
    
    
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # create lists to export:
            self.eye_scale_grps, self.iris_ctrls, self.pupil_ctrls = [], [], []
            self.has_iris = False
            self.has_pupil = False
            # create the main control:
            self.eye_ctrl = self.ar.ctrls.create_controller("id_010_EyeLookAtMain", self.number_name+"_"+self.ar.data.lang['c058_main']+"_Ctrl", r=(2.25*self.radius), d=self.curve_degree, guide_source=self.name_guide+"_JointEnd")
            cmds.addAttr(self.eye_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', keyable=True, minValue=0, maxValue=1, defaultValue=1)
            cmds.matchTransform(self.eye_ctrl, self.sides[0]+self.number_name+"_Guide_JointEnd", position=True, rotation=True)
            if self.mirror_axis != 'off':
                cmds.setAttr(self.eye_ctrl+".translate"+self.mirror_axis, 0)
            self.eye_grp = cmds.group(self.eye_ctrl, name=self.number_name+"_"+self.ar.data.lang['c058_main']+"_Grp")
            self.ar.utils.zeroOut([self.eye_ctrl])
            self.up_loc_grp = cmds.group(name=self.number_name+"_UpLoc_Grp", empty=True)
            self.to_ids.append(self.up_loc_grp)
            # run for all sides:
            for s, side in enumerate(self.sides):
                cmds.select(clear=True)
                self.base = side+self.number_name+'_Guide_Base'
                # declare guide:
                self.guide = side+self.number_name+"_Guide_JointLoc1"
                self.guide_end_loc_zero = side+self.number_name+"_Guide_JointEnd_Grp"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                self.guide_specular_loc = side+self.number_name+"_Guide_SpecularLoc"
                self.head_def_value = cmds.getAttr(self.base+".deformedBy")
                # create a joint:
                self.jxt = cmds.joint(name=side+self.number_name+"_1_Jxt", scaleCompensate=False)
                sub_jnt = cmds.joint(name=side+self.number_name+"_1_Sub_Jxt", scaleCompensate=False)
                self.jnt = cmds.joint(name=side+self.number_name+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_1")
                if s == 1:
                    left_eye_fk_ctrl_data = self.ar.utils.getTransformData(fk_eye_ctrl)
                self.base_eye_ctrl = self.ar.ctrls.create_controller("id_009_EyeBase", ctrl_name=side+self.number_name+"_Base_Ctrl", r=self.radius, d=self.curve_degree, head_def=self.head_def_value, guide_source=self.name_guide+"_JointLoc1")
                fk_eye_ctrl = self.ar.ctrls.create_controller("id_014_EyeFk", side+self.number_name+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, head_def=self.head_def_value, guide_source=self.name_guide+"_JointLoc1", parent_tag=self.base_eye_ctrl)
                self.fk_eye_sub_ctrl = self.ar.ctrls.create_controller("id_070_EyeFkSub", side+self.number_name+"_Fk_Sub_Ctrl", r=(0.75*self.radius), d=self.curve_degree, head_def=self.head_def_value, guide_source=self.name_guide+"_JointLoc1", parent_tag=fk_eye_ctrl)
                self.ar.utils.originedFrom(objName=fk_eye_ctrl, attrString=self.base+";"+self.guide+";"+self.guide_radius)
                self.ar.utils.originedFrom(objName=self.base_eye_ctrl, attrString=self.base+";"+self.guide)
                cmds.parent(self.fk_eye_sub_ctrl, fk_eye_ctrl)
                # position and orientation of joint and control:
                cmds.delete(cmds.pointConstraint(self.guide, self.jxt, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.guide_end_loc_zero, self.jxt, maintainOffset=False))
                cmds.delete(cmds.pointConstraint(self.guide, fk_eye_ctrl, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.guide_end_loc_zero, fk_eye_ctrl, maintainOffset=False))
                cmds.matchTransform(self.base_eye_ctrl, self.guide, position=True, rotation=True)
                # zeroOut controls:
                eye_zeros = self.ar.utils.zeroOut([self.base_eye_ctrl])
                eye_zeros.append(self.ar.utils.zeroOut([fk_eye_ctrl], offset=True))
                eye_zero_offset_grp = cmds.listRelatives(eye_zeros[1], children=True)[0]
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.setAttr(eye_zeros[0]+".scaleX", -1)
                        cmds.setAttr(eye_zeros[0]+".scaleY", -1)
                        cmds.setAttr(eye_zeros[0]+".scaleZ", -1)                        
                cmds.parent(eye_zeros[1], self.base_eye_ctrl)
                # calibrate offset rotate:
                for offset_axis in self.ar.data.axes:
                    cmds.addAttr(fk_eye_ctrl, longName="calibrateR"+offset_axis, attributeType='float', defaultValue=0, keyable=False)
                    cmds.connectAttr(fk_eye_ctrl+".calibrateR"+offset_axis, eye_zero_offset_grp+".rotate"+offset_axis, force=True)
                self.ar.ctrls.set_string_attr_from_items(fk_eye_ctrl, ["calibrateRX", "calibrateRY", "calibrateRZ"]) #fkCtrlCalibrationList
                # hide visibility attribute:
                cmds.setAttr(fk_eye_ctrl+'.visibility', keyable=False)
                self.ar.ctrls.set_lock_hide([fk_eye_ctrl], ['tx', 'ty', 'tz'])
                # create end joint:
                cmds.select(self.jnt)
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                self.create_end_joint(side+self.number_name)
                # create parent and scale constraint from ctrl to jxt:
                cmds.parentConstraint(fk_eye_ctrl, self.jxt, maintainOffset=False, name=self.jxt+"_PaC")
                cmds.scaleConstraint(fk_eye_ctrl, self.jxt, maintainOffset=True, name=self.jxt+"_ScC")
                # constraint from sub control to sub joint:
                cmds.parentConstraint(self.fk_eye_sub_ctrl, sub_jnt, maintainOffset=False, name=sub_jnt+"_PaC")
                cmds.scaleConstraint(self.fk_eye_sub_ctrl, sub_jnt, maintainOffset=True, name=sub_jnt+"_ScC")
                
                # lookAt control:
                look_at_ctrl = self.ar.ctrls.create_controller("id_011_EyeLookAt", side+self.number_name+"_LookAt_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointEnd", parent_tag=self.eye_ctrl)
                cmds.matchTransform(look_at_ctrl, self.guide_end_loc, position=True, rotation=True)
                cmds.parent(self.ar.utils.zeroOut([look_at_ctrl]), self.eye_ctrl, relative=False) #lookAtCtrlZeroGrp
                cmds.addAttr(look_at_ctrl, longName=self.ar.data.lang['c118_active'], attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                self.ar.utils.originedFrom(objName=look_at_ctrl, attrString=side+self.number_name+"_Guide_JointEnd")
                
                # up locator:
                self.guide_up_loc = side+self.number_name+"_Guide_JointEnd_UpLoc"
                left_up_grp_loc = cmds.group(name=side+self.number_name+"_Up_Loc_Grp", empty=True)
                cmds.delete(cmds.pointConstraint(self.jnt, left_up_grp_loc, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.guide_end_loc_zero, left_up_grp_loc, maintainOffset=False))
                left_up_loc = cmds.spaceLocator(name=side+self.number_name+"_Up_Loc")[0]
                cmds.matchTransform(left_up_loc, self.guide_up_loc, position=True, rotation=True)
                cmds.parent(left_up_loc, left_up_grp_loc, relative=False)
                cmds.parent(left_up_grp_loc, self.up_loc_grp, relative=False)
                
                # look at aim constraint:
                aic = cmds.aimConstraint(look_at_ctrl, eye_zeros[1], worldUpType="object", worldUpObject=self.up_loc_grp+"|"+left_up_grp_loc+"|"+left_up_loc, maintainOffset=True, name=fk_eye_ctrl+"_Zero_0_Grp"+"_AiC")[0]
                cmds.connectAttr(look_at_ctrl+"."+self.ar.data.lang['c118_active'], aic+"."+look_at_ctrl+"W0", force=True)
                # eye aim rotation
                cmds.addAttr(fk_eye_ctrl, longName="aimRotation", attributeType="float", keyable=True)
                cmds.connectAttr(fk_eye_ctrl+".aimRotation", self.jnt+".rotateZ", force=True)
                cmds.pointConstraint(self.base_eye_ctrl, left_up_grp_loc, maintainOffset=True, name=left_up_grp_loc+"_PoC")
                
                # create eyeScale setup:
                cmds.select(clear=True)
                self.eye_scale_jnt = cmds.joint(name=side+self.number_name+"Scale_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.eye_scale_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.ar.utils.setJointLabel(self.eye_scale_jnt, s+self.joint_label_add, 18, self.number_name+"Scale_1")
                # jointScale position:
                cmds.matchTransform(self.eye_scale_jnt, self.guide, position=True, rotation=True)
                # create endScale joint:
                end_scale_joint = self.create_end_joint(side+self.number_name+'Scale', self.eye_scale_jnt, tz=self.radius)
                if s == 1:
                    cmds.setAttr(end_scale_joint+".translateZ", -self.radius)
                # create constraints to eyeScale:
                cmds.pointConstraint(self.jnt, self.eye_scale_jnt, maintainOffset=False, name=self.eye_scale_jnt+"_PoC")
                cmds.orientConstraint(self.base_eye_ctrl, self.eye_scale_jnt, maintainOffset=False, name=self.eye_scale_jnt+"_OrC")
                cmds.scaleConstraint(self.jnt, self.eye_scale_jnt, maintainOffset=True, name=self.eye_scale_jnt+"_ScC")
                self.eye_scale_grp = cmds.group(self.eye_scale_jnt, name=self.eye_scale_jnt+"_Grp")
                self.eye_scale_grps.append(self.eye_scale_grp)
                
                # create specular setup:
                if self.get_guide_attr(SPEC):
                    cmds.select(clear=True)
                    self.guide_specular_loc = side+self.number_name+"_Guide_SpecularLoc"
                    # specular joint:
                    eye_spec_jnt = cmds.joint(name=side+self.number_name+"Specular_1_Jnt", scaleCompensate=False)
                    cmds.addAttr(eye_spec_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.utils.setJointLabel(eye_spec_jnt, s+self.joint_label_add, 18, self.number_name+"Specular_1")
                    # specular joint scale:
                    eye_spec_scale_jnt = cmds.joint(name=side+self.number_name+"Specular_2_Jnt", scaleCompensate=False)
                    cmds.addAttr(eye_spec_scale_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.utils.setJointLabel(eye_spec_scale_jnt, s+self.joint_label_add, 18, self.number_name+"Specular_2")
                    cmds.setAttr(eye_spec_scale_jnt+".translateZ", self.radius)
                    self.create_end_joint(side+self.number_name+'Specular', eye_spec_scale_jnt, tz=0.2*self.radius)
                    cmds.parent(eye_spec_jnt, self.eye_scale_jnt)
                    # specular control:
                    eye_spec_ctrl = self.ar.ctrls.create_controller("id_071_EyeSpec", ctrl_name=side+self.number_name+"_Spec_Ctrl", r=self.radius, d=self.curve_degree, head_def=self.head_def_value, guide_source=self.name_guide+"_SpecularLoc", parent_tag=self.fk_eye_sub_ctrl)
                    cmds.matchTransform(eye_spec_ctrl, self.guide, position=True, rotation=True)
                    eye_spec_zero_grp = self.ar.utils.zeroOut([eye_spec_ctrl])[0]
                    cmds.parent(eye_spec_zero_grp, self.base_eye_ctrl)
                    cmds.parentConstraint(eye_spec_ctrl, eye_spec_jnt, maintainOffset=False, name=eye_spec_jnt+"_PaC")
                    cmds.scaleConstraint(eye_spec_ctrl, eye_spec_jnt, maintainOffset=True, name=eye_spec_jnt+"_ScC")
                    # specular follow subcontrol
                    cmds.addAttr(eye_spec_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', keyable=True, minValue=0, maxValue=1, defaultValue=1)
                    follow_spec_pac = cmds.parentConstraint(self.fk_eye_sub_ctrl, self.base_eye_ctrl, eye_spec_zero_grp, maintainOffset=True, name=eye_spec_zero_grp+"_PaC")[0]
                    eye_spec_follow_rev = cmds.createNode('reverse', name=side+self.number_name+"_Spec_Follow_Rev")
                    self.to_ids.append(eye_spec_follow_rev)
                    cmds.connectAttr(eye_spec_ctrl+"."+self.ar.data.lang['c032_follow'], follow_spec_pac+"."+self.fk_eye_sub_ctrl+"W0", force=True)
                    cmds.connectAttr(eye_spec_ctrl+"."+self.ar.data.lang['c032_follow'], eye_spec_follow_rev+".inputX", force=True)
                    cmds.connectAttr(eye_spec_follow_rev+".outputX", follow_spec_pac+"."+self.base_eye_ctrl+"W1", force=True)
                    # specular scale control:
                    eye_spec_scale_ctrl = self.ar.ctrls.create_controller("id_091_EyeSpecScale", ctrl_name=side+self.number_name+"_SpecScale_Ctrl", r=0.2*self.radius, d=self.curve_degree, head_def=self.head_def_value, guide_source=self.name_guide+"_SpecularLoc", parent_tag=eye_spec_ctrl)
                    cmds.matchTransform(eye_spec_scale_ctrl, self.guide_specular_loc, position=True, rotation=True)
                    if s == 1:
                        no_wsl_eye_spec_scale_zero_grp_data = self.ar.utils.getTransformData(eye_spec_scale_zero_grp, useWorldSpace=False)
                        left_eye_spec_scale_zero_grp_data = self.ar.utils.getTransformData(eye_spec_scale_zero_grp)
                        rigth_eye_fk_ctrl_data = self.ar.utils.getTransformData(fk_eye_ctrl)
                    eye_spec_scale_zero_grp = self.ar.utils.zeroOut([eye_spec_scale_ctrl])[0]
                    cmds.parent(eye_spec_scale_zero_grp, eye_spec_ctrl)
                    cmds.parentConstraint(eye_spec_scale_ctrl, eye_spec_scale_jnt, maintainOffset=False, name=eye_spec_scale_jnt+"_PaC")
                    cmds.scaleConstraint(eye_spec_scale_ctrl, eye_spec_scale_jnt, maintainOffset=True, name=eye_spec_scale_jnt+"_ScC")
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 0:
                            cmds.xform(eye_spec_scale_zero_grp, translation=no_wsl_eye_spec_scale_zero_grp_data["translation"], worldSpace=False)
                        else:
                            translations, temps = [], []
                            for i, j in zip(left_eye_spec_scale_zero_grp_data["translation"], left_eye_fk_ctrl_data["translation"]):
                                temps.append(i-j)
                            for k, w in zip(temps, rigth_eye_fk_ctrl_data["translation"]):
                                translations.append(k+w)
                            cmds.xform(eye_spec_scale_zero_grp, translation=translations, worldSpace=True)
                            cmds.xform(eye_spec_scale_zero_grp, rotation=left_eye_spec_scale_zero_grp_data["rotation"], worldSpace=True)

                # create eyelid setup:
                if self.get_guide_attr(EYELID):
                    # declare eyelid guides:
                    self.guide_upper_eyelid_loc = side+self.number_name+"_Guide_UpperEyelidLoc"
                    self.guide_lower_eyelid_loc = side+self.number_name+"_Guide_LowerEyelidLoc"
                    self.guide_lid_pivot_loc = side+self.number_name+"_Guide_LidPivotLoc"
                    
                    # creating eyelids joints:
                    cmds.select(clear=True)
                    self.eyelid_jxt = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang['c042_eyelid']+"_Jxt", scaleCompensate=False)
                    cmds.matchTransform(self.eyelid_jxt, self.guide_lid_pivot_loc, position=True, rotation=True)
                    cmds.parent(self.eyelid_jxt, self.eye_scale_jnt)
                    upper_eyelid_base_jxt, upper_eyelid_jnt = self.create_eyelids_joints(side, 'c044_upper', "", self.guide_upper_eyelid_loc, s+self.joint_label_add)
                    upper_eyelid_middle_base_jxt, upper_eyelid_middle_jnt = self.create_eyelids_joints(side, 'c044_upper', self.ar.data.lang['c029_middle'], self.guide_upper_eyelid_loc, s+self.joint_label_add)
                    lower_eyelid_base_jxt, lower_eyelid_jnt = self.create_eyelids_joints(side, 'c045_lower', "", self.guide_lower_eyelid_loc, s+self.joint_label_add)
                    lowerEyelidMiddleBaseJxt, lower_eyelid_middle_jnt = self.create_eyelids_joints(side, 'c045_lower', self.ar.data.lang['c029_middle'], self.guide_lower_eyelid_loc, s+self.joint_label_add)
                    
                    # creating eyelids controls and setup:
                    upper_eyelid_ctrl, upper_eyelid_ctrl_zero = self.create_eyelid_setup(side, 'c044_upper', upper_eyelid_jnt, upper_eyelid_base_jxt, upper_eyelid_middle_base_jxt, upper_eyelid_middle_jnt, 30, (0, 0, 0), self.guide_upper_eyelid_loc)
                    lower_eyelid_ctrl, lower_eyelid_ctrl_zero = self.create_eyelid_setup(side, 'c045_lower', lower_eyelid_jnt, lower_eyelid_base_jxt, lowerEyelidMiddleBaseJxt, lower_eyelid_middle_jnt, 30, (0, 0, 180), self.guide_lower_eyelid_loc)
                    # fixing mirror behavior for side controls:
                    if s == 0: #left
                        cmds.setAttr(upper_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"X", 1)
                        cmds.setAttr(upper_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                        cmds.setAttr(lower_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                        cmds.setAttr(lower_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], 1)
                        if self.corrective:
                            cmds.setAttr(lower_eyelid_ctrl[0].upper()+lower_eyelid_ctrl[1:].replace("Ctrl", "00_Net")+".inputEnd", self.corrective_value)
                    else: #right
                        if cmds.getAttr(self.guide_base+".flip") == 0:
                            cmds.setAttr(upper_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                            cmds.setAttr(lower_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"X", 1)
                            cmds.setAttr(lower_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                            cmds.setAttr(lower_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], 1)
                            cmds.setAttr(upper_eyelid_ctrl_zero+".rotateY", 180)
                            cmds.setAttr(lower_eyelid_ctrl_zero+".rotateY", 180)
                            if self.corrective:
                                cmds.setAttr(lower_eyelid_ctrl[0].upper()+lower_eyelid_ctrl[1:].replace("Ctrl", "00_Net")+".inputEnd", self.corrective_value)
                        else:
                            cmds.setAttr(upper_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], 1)
                            cmds.setAttr(lower_eyelid_ctrl+"."+self.ar.data.lang['c053_invert']+"X", 1)
                            if self.corrective:
                                cmds.setAttr(upper_eyelid_ctrl[0].upper()+upper_eyelid_ctrl[1:].replace("Ctrl", "00_Net")+".inputEnd", self.corrective_value)
                    # set eyelid scale by Base control attribute:
                    cmds.addAttr(self.base_eye_ctrl, longName=self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], attributeType='float', minValue=0.001, defaultValue=1, keyable=True)
                    cmds.connectAttr(self.base_eye_ctrl+"."+self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], self.eyelid_jxt+".scaleX", force=True)
                    cmds.connectAttr(self.base_eye_ctrl+"."+self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], self.eyelid_jxt+".scaleY", force=True)
                    cmds.connectAttr(self.base_eye_ctrl+"."+self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], self.eyelid_jxt+".scaleZ", force=True)
                    
                # create iris setup:
                if self.get_guide_attr(IRIS):
                    self.iris_ctrl = self.create_iris_pupil_setup(s, side, IRIS, 'i080_iris', s+self.joint_label_add)
                    self.iris_ctrls.append(self.iris_ctrl)
                    self.has_iris = True
                    
                # create pupil setup:
                if self.get_guide_attr(PUPIL):
                    self.pupil_ctrl = self.create_iris_pupil_setup(s, side, PUPIL, 'i081_pupil', s+self.joint_label_add)
                    self.pupil_ctrls.append(self.pupil_ctrl)
                    self.has_pupil = True
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [eye_zeros[0]], [self.jxt, self.eye_scale_grp])
                if s == 0:
                    cmds.parent(self.eye_grp, self.ctrl_hook_grp)
                    cmds.parent(self.up_loc_grp, self.scalable_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.addCustomAttr([self.eye_grp, self.up_loc_grp, left_up_grp_loc, self.eye_scale_grp], self.ar.utils.ignoreTransformIOAttr)
                self.ar.custom_attr.add_attr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.add_attr(0, self.to_ids, descendents=True) #dpID
        
        
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "eyeCtrl"     : self.eye_ctrl,
                            "eyeGrp"      : self.eye_grp,
                            "upLocGrp"    : self.up_loc_grp,
                            "eyeScaleGrp" : self.eye_scale_grps,
                            "irisCtrl"    : self.iris_ctrls,
                            "pupilCtrl"   : self.pupil_ctrls,
                            "hasIris"     : self.has_iris,
                            "hasPupil"    : self.has_pupil,
                        }
