# importing libraries:
from maya import cmds
from ..base import standard
from ...library.util import soft_ik
from ...library.util import ik_fk_snap
from ...library.util import ribbon
from importlib import reload
from maya.api import OpenMaya
import math

# global variables to this module:
CLASS_NAME = "Limb"
TITLE = "m019_limb"
DESCRIPTION = "m020_limbDesc"
WIKI = "03-‐-Guides#-limb"



class Limb(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.arm_name = "Arm"
        self.leg_name = "Leg"
        self.load_variables()
        if self.ar.dev:
            reload(soft_ik)
            reload(ik_fk_snap)
            reload(ribbon)
        self.soft_ik = soft_ik.SoftIk(self.ar)
        self.ribbon = ribbon.Ribbon(self.ar)


    def load_variables(self):
        """ Just load class variables here.
        """
        # returned data from the dictionary
        self.ik_extreme_ctrls = []
        self.ik_extreme_ctrl_zeros = []
        self.ik_pole_vector_ctrl_zeros = []
        self.to_rev_foot_ik_handle_grps = []
        self.ik_handle_constraints = []
        self.ik_handle_grp_constraints = []
        self.to_rf_blend_grps = []
        self.world_refs = []
        self.world_ref_shapes = []
        self.extreme_joints = []
        self.quad_front_legs = []
        self.integrate_orig_from_items = []
        self.ik_stretch_extreme_locs = []
        self.scalable_grps = []
        self.master_ctrl_ref_items = []
        self.root_ctrl_ref_items = []
        self.soft_ik_calibrate_items = []
        self.corrective_ctrl_grps = []
        self.ankle_articulations = []
        self.ankle_correctives = []


    def add_follow_attr_name(self, ctrl, attr):
        cmds.addAttr(ctrl, longName="followAttrName", dataType="string")
        cmds.setAttr(ctrl+".followAttrName", attr, type="string")


    # @utils.profiler
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.align_guide_corner()
        self.corner_guide_up_vector()
        self.set_lock_corner_attr(self.arm_name)
        self.re_orient_guide()
        self.prepare_auto_aim_setup()
        self.create_guide_auto_aim()
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.guide_before_loc, self.guide_main_loc, self.guide_corner_loc, self.guide_corner_b_loc, self.guide_extreme_loc, self.guide_up_vector_loc, self.guide_end_loc], 
                                   ["Before", "Main", "Corner", "CornerB", "Extrem", "CornerUpVector", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="type", attributeType='enum', enumName=self.ar.data.lang['m028_arm']+':'+self.ar.data.lang['m030_leg'])
        cmds.addAttr(self.guide_base, longName="hasBend", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="numBendJoints", defaultValue=5, attributeType='long')
        cmds.addAttr(self.guide_base, longName="style", attributeType='enum', enumName=self.ar.data.lang['m042_default']+':'+self.ar.data.lang['m026_biped']+':'+self.ar.data.lang['m037_quadruped'])
        cmds.addAttr(self.guide_base, longName="alignWorld", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="articulation", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="additional", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="softIk", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="corrective", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="reorient", attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_before_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_Before", r=0.3, d=1, guide=True)
        self.guide_main_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_Main", r=0.5, d=1, guide=True, pin=False)
        self.guide_corner_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Corner", r=0.3, d=1, guide=True)
        self.guide_corner_b_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_CornerB", r=0.5, d=1, guide=True)
        self.guide_extreme_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_Extrem", r=0.5, d=1, guide=True)
        self.guide_up_vector_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_CornerUpVector", r=0.5, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line_before = cmds.joint(name=self.name_guide+"_JGuideBefore", radius=0.001)
        self.line_main = cmds.joint(name=self.name_guide+"_JGuideMain", radius=0.001)
        self.line_corner = cmds.joint(name=self.name_guide+"_JGuideCorner", radius=0.001)
        self.line_extreme = cmds.joint(name=self.name_guide+"_JGuideExtrem", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_before, self.line_main, self.line_corner, self.line_extreme, self.line_end])
        cmds.setAttr(self.guide_corner_b_loc+".translateZ", 2)
        cmds.setAttr(self.guide_corner_b_loc+".visibility", 0)
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        # parenting
        self.corner_grp = cmds.group(self.guide_corner_loc, name=self.guide_corner_loc+"_Grp")
        cmds.parent(self.line_before, self.guide_before_loc, self.guide_main_loc, self.corner_grp, self.guide_extreme_loc, self.guide_up_vector_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_corner_b_loc, self.guide_corner_loc, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_extreme_loc)
        # edit
        self.ar.ctrls.direct_connect(self.guide_before_loc, self.line_before, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.guide_main_loc, self.line_main, maintainOffset=False, name=self.line_main+"_PaC")
        cmds.parentConstraint(self.guide_corner_loc, self.line_corner, maintainOffset=False, name=self.line_corner+"_PaC")
        cmds.parentConstraint(self.guide_extreme_loc, self.line_extreme, maintainOffset=False, name=self.line_extreme+"_PaC")
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.setAttr(self.guide_extreme_loc+".translateX", lock=True)


    def align_guide_corner(self):
        # align cornerLocs:
        self.corner_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_grp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType="object", worldUpObject=self.guide_up_vector_loc, name=self.corner_grp+"_AiC")[0]
        self.corner_point_grp = cmds.group(self.corner_grp, name=self.corner_grp+"_Zero_0_Grp")
        poc = cmds.pointConstraint(self.guide_main_loc, self.guide_extreme_loc, self.corner_point_grp, maintainOffset=False, name=self.corner_point_grp+"_PoC")[0]
        cmds.setAttr(poc+'.'+self.guide_main_loc[self.guide_main_loc.rfind(":")+1:]+'W0', 0.52)
        cmds.setAttr(poc+'.'+self.guide_extreme_loc[self.guide_extreme_loc.rfind(":")+1:]+'W1', 0.48)
        cmds.setAttr(self.guide_before_loc+".translateX", -0.5)
        cmds.setAttr(self.guide_before_loc+".translateZ", -2)
        cmds.setAttr(self.guide_extreme_loc+".translateZ", 10)
        cmds.setAttr(self.corner_grp+".translateY", -0.75)


    def corner_guide_up_vector(self):
        # editing cornerUpVector:
        self.guide_up_vector_grp = cmds.group(self.guide_up_vector_loc, name=self.guide_up_vector_loc+"_Grp")
        corner_position = cmds.xform(self.guide_corner_loc, query=True, worldSpace=True, rotatePivot=True)
        cmds.move(corner_position[0], corner_position[1], corner_position[2], self.guide_up_vector_grp)
        corner_up_vector_poc = cmds.pointConstraint(self.guide_main_loc, self.guide_extreme_loc, self.guide_up_vector_grp, maintainOffset=True, name=self.guide_up_vector_grp+"_PoC")[0]
        cmds.setAttr(corner_up_vector_poc+'.'+self.guide_main_loc[self.guide_main_loc.rfind(":")+1:]+'W0', 0.52)
        cmds.setAttr(corner_up_vector_poc+'.'+self.guide_extreme_loc[self.guide_extreme_loc.rfind(":")+1:]+'W1', 0.48)
        cmds.setAttr(self.guide_up_vector_loc+".translateY", -10)
        # display cornerUpVector:
        cmds.addAttr(self.guide_corner_loc, longName="displayUpVector", attributeType="bool")
        cmds.setAttr(self.guide_corner_loc+".displayUpVector", keyable=False, channelBox=True)
        cmds.connectAttr(self.guide_corner_loc+".displayUpVector", self.guide_up_vector_loc+".visibility", force=True)


    def set_lock_corner_attr(self, limb_type, *args):
        """ Set corner guide lock attributes to specific limb type (arm or leg).
        """
        tr_attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        corner_attrs = ['tx', 'ry', 'rz'] #arm
        if limb_type == self.leg_name:
            corner_attrs = ['ty', 'rx', 'rz'] #leg
        for attr in tr_attrs:
            if attr in corner_attrs:
                cmds.setAttr(self.guide_corner_loc+"."+attr, 0, lock=True)
                cmds.setAttr(self.guide_corner_b_loc+"."+attr, 0, lock=True)
            else:
                cmds.setAttr(self.guide_corner_loc+"."+attr, lock=False)
                cmds.setAttr(self.guide_corner_b_loc+"."+attr, lock=False)


    def re_orient_guide(self, *args):
        """ This function reorient guides orientations, creating temporary aimConstraints for them.
        """
        # re-declaring guide names:
        self.guide_before_loc = self.name_guide+"_Before"
        self.guide_main_loc = self.name_guide+"_Main"
        self.guide_corner_loc = self.name_guide+"_Corner"
        self.guide_extreme_loc = self.name_guide+"_Extrem"
        self.guide_up_vector_loc = self.name_guide+"_CornerUpVector"

        # Adjust offset when it's arm or leg. Using diferent axis for arm or leg.
        before_translate_axis = ".translateX"
        if self.get_limb_type() == self.arm_name:
            before_translate_axis = ".translateY"

        # re-orient clavicle rotations:
        temp_before_up_vector = cmds.group(empty=True, name=self.guide_before_loc+"_UpVector_Tmp")
        cmds.matchTransform(temp_before_up_vector, self.guide_before_loc, position=True)
        before_up_vector_translate = cmds.getAttr(temp_before_up_vector+before_translate_axis)
        cmds.setAttr(temp_before_up_vector+before_translate_axis, before_up_vector_translate+10)
        temp_before_aic = cmds.aimConstraint(self.guide_main_loc, self.guide_before_loc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=temp_before_up_vector, name=self.guide_before_loc+"_Tmp_AiC")[0]
        cmds.delete(temp_before_aic, temp_before_up_vector)
        
        # re-orient main shoulder guide
        temp_main_up_vector = cmds.group(empty=True, parent=self.guide_base, relative=True, name=self.guide_main_loc+"_UpVector_Tmp")
        cmds.setAttr(temp_main_up_vector+".translateX", 10)
        temp_main_aic = cmds.aimConstraint(self.guide_corner_loc, self.guide_main_loc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=temp_main_up_vector, name=self.guide_main_loc+"_Tmp_AiC")[0]
        
        # aim offset for aimConstraint depending on limb_type
        self.set_aim_offset(temp_main_aic)
        cmds.delete(temp_main_aic, temp_main_up_vector)


    def prepare_auto_aim_setup(self):
        # create autoAim null groups:
        self.guide_main_drv_null = cmds.group(empty=True, name=self.guide_main_loc+"_Drv_Null")
        self.corner_drv_null = cmds.group(empty=True, name=self.guide_corner_loc+"_Drv_Null")
        self.corner_drv_null_grp = cmds.group(self.corner_drv_null, name=self.corner_drv_null+"_Grp")
        cmds.parent(self.guide_main_drv_null, self.corner_drv_null_grp, self.guide_base)
        cmds.matchTransform(self.guide_main_drv_null, self.guide_main_loc)
        cmds.matchTransform(self.corner_drv_null_grp, self.guide_corner_loc)
        cmds.setAttr(self.guide_main_drv_null+".visibility", 0)
        cmds.setAttr(self.corner_drv_null+".visibility", 0)
        cmds.setAttr(self.corner_drv_null_grp+".visibility", 0)


    def create_guide_auto_aim(self, *args):
        """ AimConstraint setup in order to auto orient mainGuide with CornerGuide
        """ 
        # re-declaring guide names:
        self.guide_main_loc = self.name_guide+"_Main"
        self.guide_corner_loc = self.name_guide+"_Corner"
        self.guide_extreme_loc = self.name_guide+"_Extrem"
        self.guide_up_vector_loc = self.name_guide+"_CornerUpVector"
        self.corner_point_grp = self.name_guide+"_Corner_Grp_Zero_0_Grp"
        self.guide_main_drv_null = self.name_guide+"_Main_Drv_Null"
        self.corner_drv_null = self.name_guide+"_Corner_Drv_Null"
        self.corner_drv_null_grp =  self.name_guide+"_Corner_Drv_Null_Grp"

        # creating group to mainLoc:
        self.guide_main_loc_grp = self.ar.utils.create_zero_out([self.guide_main_loc])[0]

        # checking limb_type to create correctly up vector values:
        up_vector_values = (1.0, 0.0, 0.0)
        if  self.get_limb_type() == self.arm_name:
            up_vector_values = (0.0, -1.0, 0.0)

        # deleting point constraint to change to the new null grp:
        corner_point_grp_connections = cmds.listConnections(self.corner_point_grp, type="constraint", source=True, destination=False)
        guide_up_vector_grp_connections = cmds.listConnections(self.guide_up_vector_grp, type="constraint", source=True, destination=False)
        if corner_point_grp_connections and guide_up_vector_grp_connections:
            poc_connections = corner_point_grp_connections+guide_up_vector_grp_connections
            if poc_connections:
                for connection in poc_connections:
                    if cmds.objExists(connection):
                        cmds.delete(connection)
        
        # connecting guides transform to the null groups:
        for axis in self.ar.data.axes:
            cmds.connectAttr(self.guide_main_loc+".translate"+axis, self.guide_main_drv_null+".translate"+axis)
            cmds.connectAttr(self.guide_main_loc+".rotate"+axis, self.guide_main_drv_null+".rotate"+axis)
            cmds.connectAttr(self.guide_corner_loc+".translate"+axis, self.corner_drv_null+".translate"+axis)
            cmds.connectAttr(self.guide_corner_loc+".rotate"+axis, self.corner_drv_null+".rotate"+axis)
        
        # new point constraint from main null grp:
        self.corner_poc = cmds.pointConstraint(self.guide_main_drv_null, self.guide_extreme_loc, self.corner_point_grp, maintainOffset=True, name=self.corner_point_grp+"_PoC")[0]
        self.corner_up_vector_poc = cmds.pointConstraint(self.guide_main_drv_null, self.guide_extreme_loc, self.guide_up_vector_grp, maintainOffset=True, name=self.guide_up_vector_grp+"_PoC")[0]
        self.corner_null_poc = cmds.pointConstraint(self.guide_main_drv_null, self.guide_extreme_loc, self.corner_drv_null_grp, maintainOffset=True, name=self.corner_drv_null_grp+"_PoC")[0]
        self.corner_drv_null_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_drv_null_grp, aimVector=(0.0, 0.0, 1.0), upVector=up_vector_values, worldUpType="object", worldUpObject=self.guide_up_vector_loc, name=self.corner_drv_null_grp+"_AiC")

        # setting constraint values, using 0.5 to don't change the previous one which was used to correct placement:
        cmds.setAttr(self.corner_poc+'.'+self.guide_main_drv_null[self.guide_main_drv_null.rfind(":")+1:]+'W0', 0.5)
        cmds.setAttr(self.corner_poc+'.'+self.guide_extreme_loc[self.guide_extreme_loc.rfind(":")+1:]+'W1', 0.5)
        cmds.setAttr(self.corner_up_vector_poc+'.'+self.guide_main_drv_null[self.guide_main_drv_null.rfind(":")+1:]+'W0', 0.5)
        cmds.setAttr(self.corner_up_vector_poc+'.'+self.guide_extreme_loc[self.guide_extreme_loc.rfind(":")+1:]+'W1', 0.5)
        cmds.setAttr(self.corner_null_poc+'.'+self.guide_main_drv_null[self.guide_main_drv_null.rfind(":")+1:]+'W0', 0.5)
        cmds.setAttr(self.corner_null_poc+'.'+self.guide_extreme_loc[self.guide_extreme_loc.rfind(":")+1:]+'W1', 0.5)
        
        # main aimConstraint to the mainLocGrp:
        self.main_aic = cmds.aimConstraint(self.corner_drv_null, self.guide_main_loc_grp, maintainOffset=True, aimVector=(0.0, 0.0, 1.0), upVector=up_vector_values, worldUpType="object", worldUpObject=self.guide_up_vector_loc, name=self.guide_main_loc_grp+"_AiC")[0]
        cmds.select(self.guide_base)


    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".translateX", 4)
        cmds.setAttr(self.guide_base+".rotateX", 90)
        cmds.setAttr(self.guide_base+".rotateZ", 90)


    def recreate_auto_aim(self):
        """ Need to delete the previous setup in order to autoAim works with different type of limb
        """
        # re-declaring guide names:
        self.guide_main_loc = self.name_guide+"_Main"
        self.guide_main_loc_grp = self.name_guide+"_Main_Zero_0_Grp"
        self.guide_main_drv_null = self.name_guide+"_Main_Drv_Null"
        self.corner_drv_null = self.name_guide+"_Corner_Drv_Null"
        self.corner_drv_null_aic = self.name_guide+"_Corner_Drv_Null_Grp_AiC"
        self.corner_drv_null_grp = self.name_guide+"_Corner_Drv_Null_Grp"
        self.guide_corner_loc = self.name_guide+"_Corner"
        self.corner_poc = self.name_guide+"_Corner_Grp_Zero_0_Grp_PoC"
        
        # deleting previous constraints:
        cmds.delete(self.corner_poc, self.corner_drv_null_aic, self.corner_poc, self.corner_up_vector_poc, self.corner_null_poc)

        # disconnecting direct connections:
        for axis in self.ar.data.axes:
            cmds.disconnectAttr(self.guide_main_loc+".translate"+axis, self.guide_main_drv_null+".translate"+axis)
            cmds.disconnectAttr(self.guide_main_loc+".rotate"+axis, self.guide_main_drv_null+".rotate"+axis)
            cmds.disconnectAttr(self.guide_corner_loc+".translate"+axis, self.corner_drv_null+".translate"+axis)
            cmds.disconnectAttr(self.guide_corner_loc+".rotate"+axis, self.corner_drv_null+".rotate"+axis)
        
       # deleting mainLoc group, this group previous received the main auto aimConstraint:
        cmds.parent(self.guide_main_loc, self.guide_base)
        cmds.delete(self.guide_main_loc_grp)

        # setting new positions:
        cmds.matchTransform(self.guide_main_drv_null, self.guide_main_loc)
        cmds.matchTransform(self.corner_drv_null_grp, self.guide_corner_loc)

        # re-orient guides:
        self.re_orient_guide()

        # autoAim main function:
        self.create_guide_auto_aim()


    def cross_product(self, limb_type, *args):
        """ Calculate cross product between guides Main, Corner and Extrem
            It will check which side the corner is to adjust the aim constraint offset
        """
        # re-declaring variables:
        self.guide_main_loc = self.name_guide+"_Main"
        self.guide_corner_loc = self.name_guide+"_Corner"
        self.guide_extreme_loc = self.name_guide+"_Extrem"

        # get guides position in worldSpace:
        main_pos = OpenMaya.MVector(cmds.xform(self.guide_main_loc, query=True, worldSpace=True, translation=True))
        corner_pos = OpenMaya.MVector(cmds.xform(self.guide_corner_loc, query=True, worldSpace=True, translation=True))
        extreme_pos = OpenMaya.MVector(cmds.xform(self.guide_extreme_loc, query=True, worldSpace=True, translation=True))

        # create vector between guides position directions:
        main_to_corner_vector = corner_pos - main_pos
        main_to_extreme_vector = extreme_pos - main_pos

        # calculate cross_product between vectors:
        cross_product = main_to_corner_vector ^ main_to_extreme_vector

        # check position of cross_product depending on the limb_type:
        if limb_type == self.arm_name:
            # if the limb_type is arm the cross_product will look for the axis y:
            if cross_product.y <= 0:
                offset_value = 1
            else:
                offset_value = -1

        if limb_type == self.leg_name:
            # if the limbtype is leg the cross_product will look for the axis X
            if cross_product.x <= 0:
                offset_value = -1
            else:
                offset_value = 1
        return offset_value


    def set_aim_offset(self, aic):
        """ Adjust aimOffset depends on corner position
        """
        # re-declaring corner guide name:
        self.guide_corner_loc = self.name_guide+"_Corner"
        
        # when the limb_type is arm, it will call the cross_product function to get the right offset for X
        if self.get_limb_type() == self.arm_name:
            offset_axis = ".offsetX"
            offset_value = self.cross_product(self.arm_name)
        
        # when the limb_type is arm, it will call the cross_product function to get the right offset for Y:
        elif self.get_limb_type() == self.leg_name:
            offset_axis = ".offsetY"
            offset_value = self.cross_product(self.leg_name)

        # set the aimConstraint's offset according to limb_type:
        cmds.setAttr(aic+offset_axis, offset_value)
        

    def run_re_orient_guide(self, *args):
        """ New functions when the button reorient is pressed. For Arm, the extrem will point to the corner. For legs, the extrem will point to the ground.
        """
        # re-declaring guides names:
        self.main_aic = self.name_guide+"_Main_Zero_0_Grp_AiC"
        self.guide_before_loc = self.name_guide+"_Before"
        self.guide_main_loc = self.name_guide+"_Main"
        self.guide_corner_loc = self.name_guide+"_Corner"
        self.guide_extreme_loc = self.name_guide+"_Extrem"
        self.guide_up_vector_loc = self.name_guide+"_CornerUpVector"
        
        # re-orient extremLoc to align with cornerLoc if the clavicle and wrist aren't pinned.
        if not cmds.getAttr(self.guide_extreme_loc+".pinGuide") and not cmds.getAttr(self.guide_before_loc+".pinGuide"):
            # reorient guides first
            self.re_orient_guide()
            # do guide alignment
            if self.get_limb_type() == self.arm_name:
                temp_extreme_children_grp = False
                to_unparent_items = []
                pint_guide_state_data = {}
                cmds.setAttr(self.guide_extreme_loc+".pinGuide", 0)
                extreme_children = cmds.listRelatives(self.guide_extreme_loc, children=True, type="transform")
                if extreme_children:
                    has_sub_guide_base = False
                    for extreme_child in extreme_children:
                        if "pinGuide" in cmds.listAttr(extreme_child):
                            has_sub_guide_base = True
                    if has_sub_guide_base:
                        temp_extreme_children_grp = cmds.group(empty=True, name="extremChildren_Temp_Grp", parent=self.guide_base)
                        for extreme_child in extreme_children:
                            if "pinGuide" in cmds.listAttr(extreme_child):
                                to_unparent_items.append(extreme_child)
                                pint_guide_state_data[extreme_child] = cmds.getAttr(extreme_child+".pinGuide")
                                cmds.setAttr(extreme_child+".pinGuide", 0)
                                cmds.parent(extreme_child, temp_extreme_children_grp)
                    temp_up_vector_wrist_grp = cmds.group(empty=True, name="tempUpVectorWrist_Null")
                    cmds.parent(temp_up_vector_wrist_grp, self.guide_base)
                    cmds.matchTransform(temp_up_vector_wrist_grp, self.guide_extreme_loc)
                    cmds.setAttr(temp_up_vector_wrist_grp+".translateX", 2)
                    temp_wrist_aic = cmds.aimConstraint(self.guide_corner_loc, self.guide_extreme_loc, aimVector=(0.0, 0.0, -1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=temp_up_vector_wrist_grp, name=self.guide_extreme_loc+"_Tmp_AiC")
                    cmds.delete(temp_wrist_aic, temp_up_vector_wrist_grp)
                if to_unparent_items:
                    cmds.parent(to_unparent_items, self.guide_extreme_loc)
                for node in pint_guide_state_data.keys():
                    cmds.setAttr(node+".pinGuide", pint_guide_state_data[node])
                if temp_extreme_children_grp:
                    cmds.delete(temp_extreme_children_grp)

                # adjust offset depends on corner position
                cmds.setAttr(self.guide_main_loc+".rotateX", 0)
                self.set_aim_offset(self.main_aic)
            
            # setup to reorient the ankle guide to point to the ground when rotate mainGuide
            if self.get_limb_type() == self.leg_name:
                temp_ankle_to_aim_null = cmds.group(empty=True, world=True, name="Temp_Ankle_ToAim_Null")
                cmds.matchTransform(temp_ankle_to_aim_null, self.guide_extreme_loc, position=True)
                cmds.setAttr(temp_ankle_to_aim_null+".translateY", -10)
                temp_ankle_to_aic = cmds.aimConstraint(temp_ankle_to_aim_null, self.guide_extreme_loc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), name=self.guide_extreme_loc+"_Tmp_AiC")
                cmds.delete(temp_ankle_to_aic, temp_ankle_to_aim_null)

                # leg offset adjust
                cmds.setAttr(self.guide_main_loc+".rotateY", 0)
                self.set_aim_offset(self.main_aic)
        cmds.select(self.guide_base)


    def change_bend(self, value, *args):
        """ Just set bend values and enable or disable UI elements.
        """
        cmds.setAttr(self.guide_base+".hasBend", value)
        if self.ar.data.ui_state:
            cmds.optionMenu('edit_guide_bend_num_om', edit=True, enable=value)
            cmds.checkBox('edit_guide_additional_cb', edit=True, enable=value)


    def change_bend_number(self, value, *args):
        """ Change the number of joints used in the bend ribbon.
        """
        cmds.setAttr(self.guide_base+".numBendJoints", int(value))


    def change_type(self, type, *args):
        """ This function will modify the names of the rigged module to Arm or Leg options
            and rotate the main in order to be more easy to user edit.
        """
        # re-declaring guide names:
        self.guide_before_loc = self.name_guide+"_Before"
        self.guide_main_loc = self.name_guide+"_Main"
        self.corner_grp = self.name_guide+"_Corner_Grp"
        self.guide_corner_loc = self.name_guide+"_Corner"
        self.guide_corner_b_loc = self.name_guide+"_CornerB"
        self.guide_extreme_loc = self.name_guide+"_Extrem"
        self.guide_end_loc = self.name_guide+"_JointEnd"
        self.guide_up_vector_loc = self.name_guide+"_CornerUpVector"
        self.corner_aic = self.corner_grp+"_AiC"

        self.ar.utils.unlock_attr([self.guide_before_loc, self.guide_main_loc, self.corner_grp, self.guide_corner_loc, self.guide_corner_b_loc, self.guide_extreme_loc, self.guide_end_loc, self.guide_up_vector_loc, self.corner_aic])

        # reset translations:
        translation = ['tx', 'ty', 'tz']
        guide_items = [self.guide_before_loc, self.guide_main_loc, self.corner_grp, self.guide_extreme_loc, self.guide_up_vector_loc]
        for guide_node in guide_items:
            for t_attr in translation:
                cmds.setAttr(guide_node+"."+t_attr, lock=False)
                cmds.setAttr(guide_node+"."+t_attr, 0)

        # for Arm type:
        if type == self.ar.data.lang['m028_arm'] or type == 0:
            cmds.setAttr(self.guide_base+".type", 0)
            cmds.setAttr(self.guide_before_loc+".translateX", -1)
            cmds.setAttr(self.guide_before_loc+".translateZ", -4)
            cmds.setAttr(self.guide_extreme_loc+".translateZ", 10)
            cmds.setAttr(self.guide_extreme_loc+".translateX", lock=True)
            cmds.setAttr(self.corner_grp+".translateY", -0.75)
            cmds.setAttr(self.guide_corner_loc+".translateZ", 0)
            cmds.setAttr(self.guide_end_loc+".translateZ", 1.3)
            cmds.setAttr(self.guide_base+".rotateX", 90)
            cmds.setAttr(self.guide_base+".rotateY", 0)
            cmds.setAttr(self.guide_base+".rotateZ", 90)
            cmds.setAttr(self.guide_up_vector_loc+".translateY", -10)
            cmds.delete(self.corner_aic)
            self.corner_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_grp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType="object", worldUpObject=self.guide_up_vector_loc, name=self.corner_grp+"_AiC")[0]
            self.set_lock_corner_attr(self.arm_name)
            self.recreate_auto_aim()
            
        # for Leg type:
        elif type == self.ar.data.lang['m030_leg'] or type == 1:
            cmds.setAttr(self.guide_base+".type", 1)
            cmds.setAttr(self.guide_before_loc+".translateY", 1)
            cmds.setAttr(self.guide_before_loc+".translateZ", -2)
            cmds.setAttr(self.guide_extreme_loc+".translateZ", 10)
            cmds.setAttr(self.guide_extreme_loc+".translateY", lock=True)
            cmds.setAttr(self.corner_grp+".translateX", 0.75)
            cmds.setAttr(self.guide_corner_loc+".translateZ", 0)
            cmds.setAttr(self.guide_end_loc+".translateZ", 1.3)
            cmds.setAttr(self.guide_base+".rotateX", 0)
            cmds.setAttr(self.guide_base+".rotateY", -90)
            cmds.setAttr(self.guide_base+".rotateZ", 90)
            cmds.setAttr(self.guide_up_vector_loc+".translateX", 10)
            cmds.setAttr(self.guide_up_vector_loc+".translateY", 0.75)
            cmds.delete(self.corner_aic)
            self.corner_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_grp, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType="object", worldUpObject=self.guide_up_vector_loc, name=self.corner_grp+"_AiC")[0]
            self.set_lock_corner_attr(self.leg_name)
            self.recreate_auto_aim()
    
    
    def get_limb_type(self):
        """ This function will get the limb_type
        """
        enum_type = cmds.getAttr(self.guide_base+'.type')
        if enum_type == 0:
            self.limb_type = self.ar.data.lang['m028_arm']
            self.limb_types = self.arm_name
        elif enum_type == 1:
            self.limb_type = self.ar.data.lang['m030_leg']
            self.limb_types = self.leg_name
        return self.limb_types


    def get_limb_style(self):
        """ This function will get the limb_style
        """
        #
        #
        # TODO: cleanup the returned dictionary to remove this method
        #
        quadruped = False
        enum_style = cmds.getAttr(self.guide_base+'.style')
        if enum_style == 0:
            self.limb_style = self.ar.data.lang['m042_default']
        elif enum_style == 1:
            self.limb_style = self.ar.data.lang['m026_biped']
        elif enum_style == 2:
            self.limb_style = self.ar.data.lang['m037_quadruped']
            quadruped = True
        elif enum_style == 3:
            self.limb_style = self.ar.data.lang['m043_quadSpring']
            quadruped = True
        elif enum_style == 4:
            self.limb_style = self.ar.data.lang['m155_quadrupedExtra']
            quadruped = True
        return self.limb_style


    def get_original_rotation(self, ctrl):
        """ Use a temporary node to extract the world space rotation and returns it.
        """
        temp_dup = cmds.duplicate(ctrl)[0]
        cmds.parent(temp_dup, world=True)
        original_rotation = cmds.xform(temp_dup, query=True, rotation=True, worldSpace=True)
        cmds.delete(temp_dup)
        return original_rotation

    
    def rename_corner_rename(self, s, side, joints, number, name):
        """ Rename corner corrective joints and return a list of them.
        """
        results = []
        corrective_joints = cmds.listRelatives(joints, children=True, allDescendents=True)
        if corrective_joints:
            for j, jcr in enumerate(corrective_joints):
                self.ar.naming.set_joint_label(jcr, s+self.joint_label_add, 18, self.number_name+"_"+number+"_"+name+"_"+str(j))
                results.append(cmds.rename(jcr, side+self.number_name+"_"+number+"_"+name+"_"+str(j)+"_Jcr")) #renamedJcr
        return results


    def get_calibrate_presets(self, s, is_leg, first, main, corner, knee_b, extrem):
        """ Returns the calibration preset and invert lists for the asked limb joint.
        """
        presets = None
        inverts = None
        if first: #clavicle/hips
            presets = [{}, {"calibrateTX":1.0, "calibrateTZ":0.5, "calibrateRY":-30}]
            if s ==  1:
                inverts = [[], ["invertTX", "invertRY"]]
        elif main: #shoulder/leg
            if is_leg:
                presets = [{}, {"calibrateTY":-0.5, "calibrateTZ":-0.4, "calibrateRX":30}, {"calibrateTX":1.0, "calibrateRY":30}]
            else:
                presets = [{}, {"calibrateTY":0.5, "calibrateTZ":0.2}, {"calibrateTX":1.0, "calibrateRY":30}]
            if s == 1:
                inverts = [[], [], ["invertTX", "invertRY"]]
        elif corner: #elbow/knee
            presets = [{}, {"calibrateTX":0.1, "calibrateTZ":-0.6, "calibrateRY":45}, {"calibrateTX":-0.4, "calibrateTZ":0.8, "calibrateRY":-65}, {"calibrateTX":0.3, "calibrateTZ":0.8, "calibrateRY":65}]
            if not is_leg:
                inverts = [[], ["invertRY"], [], []]
                if s == 1:
                    if self.get_guide_attr('hasBend'):
                        inverts = [[], ["invertTX", "invertTZ", "invertRY"], ["invertTX", "invertTZ"], ["invertTX", "invertTZ"]]
                    else:
                        inverts = [[], ["invertRY"], [], []]
        elif knee_b: #knee_b
            presets = [{}, {"calibrateTX":0.1, "calibrateTZ":-0.6, "calibrateRY":-45}, {"calibrateTX":-0.4, "calibrateTZ":0.8, "calibrateRY":-65}, {"calibrateTX":0.3, "calibrateTZ":0.8, "calibrateRY":65}]
        elif extrem: #wrist/ankle
            presets = [{}, {"calibrateTX":0.7, "calibrateRY":-30}, {"calibrateTX":-0.7, "calibrateRY":30}, {"calibrateTY":0.7, "calibrateRX":30}, {"calibrateTY":-0.7, "calibrateRX":-30}]
            if s == 1:
                inverts = [[], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"], ["invertTX", "invertRY", "invertRZ"]]
        return presets, inverts


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                attr_name_lower = self.ar.naming.get_attr_name_lower(side, self.number_name)
                to_corner_bend_items = []
                
                # getting type of limb: (arm, leg)
                self.get_limb_type()

                # getting style of the limb: (default, biped, quadruped, etc)
                self.get_limb_style()
                style = cmds.getAttr(self.guide_base+".style")
                quadruped = False
                if style == 2:
                    quadruped = True

                # re-declaring guide names:
                self.guide_before_loc = side+self.number_name+"_Guide_Before"
                self.guide_main_loc = side+self.number_name+"_Guide_Main"
                self.guide_corner_loc = side+self.number_name+"_Guide_Corner"
                self.guide_corner_b_loc = side+self.number_name+"_Guide_CornerB"
                self.guide_extreme_loc = side+self.number_name+"_Guide_Extrem"
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"

                # getting names from data:
                if self.limb_types == self.arm_name:
                    before_name = self.ar.data.lang['c000_arm_before']
                    main_name = self.ar.data.lang['c001_arm_main']
                    corner_name = self.ar.data.lang['c002_arm_corner']
                    corner_b_name = self.ar.data.lang['c003_arm_cornerB']
                    extreme_name = self.ar.data.lang['c004_arm_extrem']
                else:
                    before_name = self.ar.data.lang['c005_leg_before']
                    main_name = self.ar.data.lang['c006_leg_main']
                    corner_name = self.ar.data.lang['c007_leg_corner']
                    corner_b_name = self.ar.data.lang['c008_leg_cornerB']
                    extreme_name = self.ar.data.lang['c009_leg_extrem']

                # mount cvLocList and jNameList:
                if quadruped:
                    guide_locs = [self.guide_before_loc, self.guide_main_loc, self.guide_corner_loc, self.guide_corner_b_loc, self.guide_extreme_loc]
                    joint_names = [before_name, main_name, corner_name, corner_b_name, extreme_name]
                else:
                    guide_locs = [self.guide_before_loc, self.guide_main_loc, self.guide_corner_loc, self.guide_extreme_loc]
                    joint_names = [before_name, main_name, corner_name, extreme_name]

                # creating joint chains:
                chain_data = {}
                suffixes = ['_Jnt', '_Ik_Jxt', '_Fk_Jxt', '_IkNotStretch_Jxt', '_IkAC_Jxt']
                end_suffixes = ['_'+self.ar.data.joint_end_attr, '_Ik_'+self.ar.data.joint_end_attr, '_Fk_'+self.ar.data.joint_end_attr, '_IkNotStretch_'+self.ar.data.joint_end_attr, '_IkAC_'+self.ar.data.joint_end_attr]
                for t, suffix in enumerate(suffixes):
                    wips = []
                    cmds.select(clear=True)
                    for n, joint_name in enumerate(joint_names):
                        wips.append(cmds.joint(name=side+self.number_name+"_"+joint_name+suffix))
                    joint_end = cmds.joint(name=side+self.number_name+end_suffixes[t])
                    self.ar.utils.add_joint_end_attr([joint_end])
                    wips.append(joint_end)
                    chain_data[suffix] = wips
                # getting jointLists:
                skin_joints = chain_data[suffixes[0]]
                ik_joints = chain_data[suffixes[1]]
                fk_joints = chain_data[suffixes[2]]
                ik_no_stretch_joints = chain_data[suffixes[3]]
                ik_auto_clavicle_joints = chain_data[suffixes[4]]
                
                # hide not skin joints in order to be more Rigger friendly when working the Skinning:
                cmds.setAttr(ik_joints[0]+".visibility", 0)
                cmds.setAttr(fk_joints[0]+".visibility", 0)
                cmds.setAttr(ik_no_stretch_joints[0]+".visibility", 0)
                cmds.setAttr(ik_auto_clavicle_joints[1]+".visibility", 0)

                for o, skin_joint in enumerate(skin_joints):
                    if o < len(skin_joints) - 2:
                        cmds.addAttr(skin_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                        self.ar.naming.set_joint_label(skin_joint, s+self.joint_label_add, 18, self.number_name+"_"+joint_names[o])

                # creating Fk controls and a hierarchy group to originedFrom data:
                fk_ctrls, orig_from_items = [], []
                for n, joint_name in enumerate(joint_names):
                    if n == 0:
                        fk_ctrl = self.ar.ctrls.create_controller("id_030_LimbClavicle", side+self.number_name+"_"+joint_name+"_Ctrl", r=(self.radius * 2), d=self.curve_degree, rot=(45, 0 ,-90), guide_source=self.name_guide+"_Before", parent_tag=self.get_parent_to_tag(fk_ctrls))
                    else:
                        fk_ctrl = self.ar.ctrls.create_controller("id_031_LimbFk", side+self.number_name+"_"+joint_name+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name+"__"+guide_locs[n][len(side):].replace("_Guide", ":Guide"), parent_tag=self.get_parent_to_tag(fk_ctrls))
                    
                    # Setup axis order
                    if joint_name == before_name:  # Clavicle and hip
                        cmds.setAttr(fk_ctrl+".rotateOrder", 3)
                    elif joint_name == extreme_name and self.limb_types == self.leg_name:  # Ankle
                        cmds.setAttr(fk_ctrl+".rotateOrder", 4)
                    elif joint_name == extreme_name and self.limb_types == self.arm_name:  # Hand
                        cmds.setAttr(fk_ctrl+".rotateOrder", 4)
                    elif joint_name == main_name:  # Leg and Shoulder
                        cmds.setAttr(fk_ctrl+".rotateOrder", 1)
                    elif self.limb_types == self.leg_name:  # Other legs ctrl
                        cmds.setAttr(fk_ctrl+".rotateOrder", 2)
                    elif self.limb_types == self.arm_name:  # Other arm ctrl
                        cmds.setAttr(fk_ctrl+".rotateOrder", 5)
                    else:
                        # Let the default axis order for other ctrl (Should not happen)
                        pass

                    # Other arm ctrl can keep the default xyz

                    fk_ctrls.append(fk_ctrl)
                    cmds.setAttr(fk_ctrl+'.visibility', keyable=False)
                    # creating the originedFrom attributes (in order to permit integrated parents in the future):
                    orig_grp = cmds.group(empty=True, name=side+self.number_name+"_"+joint_name+"_OrigFrom_Grp")
                    orig_from_items.append(orig_grp)
                    if n == 0: #Clavicle/Hips
                        self.ar.utils.set_origined_from_attr(orig_grp, guide_locs[n][guide_locs[n].find("__")+1:].replace(":", "_"))
                    elif n == 1: #Shoulder/Leg
                        self.ar.utils.set_origined_from_attr(orig_grp, guide_locs[n][guide_locs[n].find("__")+1:].replace(":", "_")+";"+self.guide_main_loc)
                    elif n == len(joint_names)-1: #Wrist/Ankle
                        self.ar.utils.set_origined_from_attr(orig_grp, guide_locs[n][guide_locs[n].find("__")+1:].replace(":", "_")+";"+self.guide_end_loc+";"+self.guide_radius)
                    else: #Corner
                        self.ar.utils.set_origined_from_attr(orig_grp, guide_locs[n][guide_locs[n].find("__")+1:].replace(":", "_"))
                        if self.get_guide_attr('hasBend'):
                            to_corner_bend_items.append(guide_locs[n][guide_locs[n].find("__")+1:].replace(":", "_"))
                    cmds.parentConstraint(skin_joints[n], orig_grp, maintainOffset=False, name=orig_grp+"_PaC")
                    if n > 1:
                        cmds.parent(fk_ctrl, fk_ctrls[n - 1])
                        cmds.parent(orig_grp, orig_from_items[n - 1])
                    # add wrist_toParent_Ctrl
                    if n == len(joint_names)-1:
                        to_parent_extrem_ctrl = self.ar.ctrls.create_controller("id_032_LimbToParent", ctrl_name=side+self.number_name+"_"+extreme_name+"_ToParent_Ctrl", r=(self.radius * 0.1), d=self.curve_degree, guide_source=self.name_guide+"_Extrem", parent_tag=fk_ctrls[-1])
                        cmds.parent(to_parent_extrem_ctrl, orig_grp)
                        if s == 0:
                            cmds.setAttr(to_parent_extrem_ctrl+".translateX", self.radius)
                        else:
                            cmds.setAttr(to_parent_extrem_ctrl+".translateX", -self.radius)
                        self.ar.utils.create_zero_out([to_parent_extrem_ctrl], not_transform_io=False)
                        self.ar.ctrls.set_lock_hide([to_parent_extrem_ctrl], ['v'])
                # create_zero_out controls:
                fk_ctrl_zeros = self.ar.utils.create_zero_out(fk_ctrls)
                fk_ctrl_zero_grp = cmds.group(fk_ctrl_zeros[0], fk_ctrl_zeros[1], name=side+self.number_name+"_Fk_Ctrl_Grp")
                
                # working with position, orientation of joints and make an orientConstrain for Fk controls:
                for n in range(len(joint_names)):
                    cmds.matchTransform(skin_joints[n], guide_locs[n], position=True, rotation=True)
                    cmds.matchTransform(ik_joints[n], guide_locs[n], position=True, rotation=True)
                    cmds.matchTransform(ik_no_stretch_joints[n], guide_locs[n], position=True, rotation=True)
                    cmds.matchTransform(ik_auto_clavicle_joints[n], guide_locs[n], position=True, rotation=True)
                    cmds.matchTransform(fk_joints[n], guide_locs[n], position=True, rotation=True)
                    cmds.matchTransform(fk_ctrl_zeros[n], guide_locs[n], position=True, rotation=True)
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(skin_joints[n], ik_joints[n], ik_no_stretch_joints[n], ik_auto_clavicle_joints[n], fk_joints[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    if n == 0:
                        cmds.parentConstraint(fk_ctrls[n], fk_joints[n], maintainOffset=True, name=side+self.number_name+"_"+joint_names[n]+"_PaC")
                    else:
                        cmds.parentConstraint(fk_ctrls[n], fk_joints[n], maintainOffset=True, name=side+self.number_name+"_"+joint_names[n]+"_Fk_PaC")
                    if n == 0:
                        clavicle_joints = [skin_joints[0], ik_joints[0], fk_joints[0], ik_no_stretch_joints[0]]
                        for clavicle_joint in clavicle_joints:
                            for axis in self.ar.data.axes:
                                cmds.connectAttr(fk_ctrls[0]+".scale"+axis, clavicle_joint+".scale"+axis, force=True)
                    elif n == 1 or n == 2: #shoulder/elbow
                        self.ar.ctrls.set_lock_hide([fk_ctrls[n]], ['sx', 'sy'])
                    else:
                        self.ar.ctrls.set_lock_hide([fk_ctrls[n]], ['sx', 'sy', 'sz'])
                
                # puting endJoints in the correct position:
                cmds.matchTransform(skin_joints[-1], self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(ik_joints[-1], self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(ik_no_stretch_joints[-1], self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(ik_auto_clavicle_joints[-1], self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(fk_joints[-1], self.guide_end_loc, position=True, rotation=True)

                # creating a group reference to recept the attributes:
                world_ref = self.ar.ctrls.create_controller("id_036_LimbWorldRef", side+self.number_name+"_WorldRef_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", guide_source=self.name_guide+"_Base")
                cmds.addAttr(world_ref, longName="ikFkSnap", attributeType='short', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(world_ref, longName=self.ar.data.lang['c113_length'], attributeType='float', defaultValue=1)
                self.world_refs.append(world_ref)
                self.world_ref_shapes.append(cmds.listRelatives(world_ref, children=True, type='nurbsCurve')[0])
                # creating a group reference to follow masterCtrl and rootCtrl:
                master_ctrl_ref = cmds.group(empty=True, name=side+self.number_name+"_MasterCtrlRef_Grp")
                self.master_ctrl_ref_items.append(master_ctrl_ref)
                root_ctrl_ref = cmds.group(empty=True, name=side+self.number_name+"_RootCtrlRef_Grp")
                self.root_ctrl_ref_items.append(root_ctrl_ref)

                # parenting fkControls from 2 hierarchies (before and limb) using constraint, attention to fkIsolated shoulder:
                # creating a shoulder_ref group in order to use it as position relative, joint articulation origin and aim constraint target to quad_extra_ctrl:
                shoulder_ref_grp = cmds.group(empty=True, name=skin_joints[1]+"_Ref_Grp")
                # ask if the module is self.arm_name and turn default value to 1 if true.
                isolate_default_value = 0
                if self.limb_types == self.arm_name:
                    isolate_default_value = 1  
                cmds.parent(shoulder_ref_grp, skin_joints[1], relative=True)
                cmds.parent(shoulder_ref_grp, skin_joints[0], relative=False)
                cmds.pointConstraint(shoulder_ref_grp, fk_ctrl_zeros[1], maintainOffset=True, name=fk_ctrl_zeros[1]+"_PoC")
                fk_isolate_pac = cmds.parentConstraint(shoulder_ref_grp, master_ctrl_ref, fk_ctrl_zeros[1], skipTranslate=["x", "y", "z"], maintainOffset=True, name=fk_ctrl_zeros[1]+"_PaC")[0]               
                cmds.addAttr(fk_ctrls[1], longName=self.ar.data.lang['m095_isolate'].lower(), attributeType='float', minValue=0, maxValue=1, defaultValue=isolate_default_value, keyable=True)
                self.add_follow_attr_name(fk_ctrls[1], self.ar.data.lang['m095_isolate'].lower())
                cmds.connectAttr(fk_ctrls[1]+'.'+self.ar.data.lang['m095_isolate'].lower(), fk_isolate_pac+"."+master_ctrl_ref+"W1", force=True)
                fk_isolate_rev = cmds.createNode('reverse', name=side+self.number_name+"_FkIsolate_Rev")
                cmds.connectAttr(fk_ctrls[1]+'.'+self.ar.data.lang['m095_isolate'].lower(), fk_isolate_rev+".inputX", force=True)
                cmds.connectAttr(fk_isolate_rev+'.outputX', fk_isolate_pac+"."+shoulder_ref_grp+"W0", force=True) 

                # create orient constrain in order to blend ikFk:
                ik_fk_rev = self.ar.utils.create_joint_blend(ik_joints[1:], fk_joints[1:], skin_joints[1:], "Fk_ikFkBlend", attr_name_lower, world_ref)

                # organize the ikFkBlend from before to limb:
                cmds.parentConstraint(fk_ctrls[0], ik_joints[0], maintainOffset=True, name=ik_joints[0]+"_PaC")
                cmds.parentConstraint(fk_ctrls[0], ik_no_stretch_joints[0], maintainOffset=True, name=ik_no_stretch_joints[0]+"_PaC")
                cmds.parentConstraint(fk_ctrls[0], fk_joints[0], maintainOffset=True, name=fk_joints[0]+"_PaC")
                cmds.parentConstraint(fk_ctrls[0], skin_joints[0], maintainOffset=True, name=skin_joints[0]+"_PaC")

                # creating ik controls:
                ik_extreme_ctrl = self.ar.ctrls.create_controller("id_033_LimbWrist", ctrl_name=side+self.number_name+"_"+extreme_name+"_Ik_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=self.name_guide+"_Extrem")
                ik_extreme_sub_ctrl = self.ar.ctrls.create_controller("id_094_LimbExtremSub", ctrl_name=side+self.number_name+"_"+extreme_name+"_Ik_Sub_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=self.name_guide+"_Extrem", parent_tag=ik_extreme_ctrl)
                cmds.parent(ik_extreme_sub_ctrl, ik_extreme_ctrl)
                self.ar.ctrls.set_lock_hide([ik_extreme_sub_ctrl], ["sx", "sy", "sz", "v"])
                self.ar.ctrls.set_sub_ctrl_display(ik_extreme_ctrl, ik_extreme_sub_ctrl, 0)
                
                # creating orient controller
                if self.limb_types == self.arm_name:
                    cmds.addAttr(ik_extreme_ctrl, longName="orient", attributeType="double", defaultValue=1, min=0, max=1, keyable=True)
                    extreme_orient_ctrl = self.ar.ctrls.create_controller("id_101_LimbExtremOrient", ctrl_name=side+self.number_name+"_"+extreme_name+"_Orient_Ctrl", r=(self.radius * 0.7), d=self.curve_degree, guide_source=self.name_guide+"_Extrem", parent_tag=fk_ctrls[0])
                    cmds.connectAttr(extreme_orient_ctrl+".message", to_parent_extrem_ctrl+".parentTag", force=True)
                    temp_orient_ctrl_cluster = cmds.cluster(extreme_orient_ctrl)[1]
                    if s == 0:
                        cmds.setAttr(temp_orient_ctrl_cluster+".tz", 0.2*self.radius)
                    else:
                        cmds.setAttr(temp_orient_ctrl_cluster+".tz", -0.2*self.radius)
                    cmds.delete(extreme_orient_ctrl, constructionHistory=True)
                    ik_corner_ctrl = self.ar.ctrls.create_controller("id_034_LimbElbow", ctrl_name=side+self.number_name+"_"+corner_name+"_Ik_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=self.name_guide+"_Corner", parent_tag=fk_ctrls[0])
                    cmds.setAttr(ik_extreme_ctrl+".rotateOrder", 2) #zxy
                    cmds.setAttr(ik_extreme_sub_ctrl+".rotateOrder", 2) #zxy
                    cmds.setAttr(extreme_orient_ctrl+".rotateOrder", 2) #zxy
                    extreme_orient_ctrl_zero = self.ar.utils.create_zero_out([extreme_orient_ctrl])[0]
                    cmds.matchTransform(extreme_orient_ctrl_zero, self.guide_extreme_loc, position=True, rotation=True)
                    self.ar.ctrls.set_lock_hide([extreme_orient_ctrl], ["tx", "ty", "tz", "sx", "sy", "sz", "v"])
                    cmds.delete(orig_grp+"_PaC")
                    cmds.parentConstraint(extreme_orient_ctrl, orig_grp, maintainOffset=False, name=orig_grp+"_PaC")
                else:
                    ik_corner_ctrl = self.ar.ctrls.create_controller("id_035_LimbKnee", ctrl_name=side+self.number_name+"_"+corner_name+"_Ik_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=self.name_guide+"_Corner", parent_tag=fk_ctrls[0])
                    cmds.connectAttr(ik_extreme_ctrl+".message", to_parent_extrem_ctrl+".parentTag", force=True)
                    cmds.setAttr(ik_extreme_ctrl+".rotateOrder", 3) #xzy
                    cmds.setAttr(ik_extreme_sub_ctrl+".rotateOrder", 3) #xzy
                self.ik_extreme_ctrls.append(ik_extreme_ctrl)
                self.ar.utils.set_origined_from_attr(ik_corner_ctrl, side+self.number_name+"_Guide_CornerUpVector")
                cmds.connectAttr(ik_corner_ctrl+".message", ik_extreme_ctrl+".parentTag", force=True)

                # getting them create_zero_out groups:
                ik_corner_ctrl_zero = self.ar.utils.create_zero_out([ik_corner_ctrl])[0]
                ik_extreme_ctrl_zero = self.ar.utils.create_zero_out([ik_extreme_ctrl])[0]
                self.ik_extreme_ctrl_zeros.append(ik_extreme_ctrl_zero)
                # putting ikCtrls in the correct position and orientation:
                cmds.matchTransform(ik_extreme_ctrl_zero, self.guide_extreme_loc, position=True, rotation=True)

                # fix stretch calcule to work with reverseFoot
                ik_stretch_extreme_loc = cmds.group(empty=True, name=side+self.number_name+"_"+extreme_name+"_Ik_Loc_Grp")
                if quadruped:
                    cmds.matchTransform(ik_stretch_extreme_loc, skin_joints[3], position=True, rotation=True) #snap to knee_b
                else:    
                    cmds.matchTransform(ik_stretch_extreme_loc, self.guide_extreme_loc, position=True, rotation=True)
                
                # fixing ikControl group to get a good mirror orientation more animator friendly:
                ik_extreme_ctrl_grp = cmds.group(ik_extreme_ctrl, name=side+self.number_name+"_"+extreme_name+"_Ik_Ctrl_Grp")
                ik_extreme_ctrl_orient_grp = cmds.group(ik_extreme_ctrl_grp, name=side+self.number_name+"_"+extreme_name+"_Ik_Ctrl_Orient_Grp")
                # adjust rotate orders:
                cmds.setAttr(ik_extreme_ctrl_grp+".rotateOrder", cmds.getAttr(ik_extreme_ctrl+".rotateOrder"))
                cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateOrder", cmds.getAttr(ik_extreme_ctrl+".rotateOrder"))

                # orient ik controls properly:
                if s == 0 or self.limb_types == self.arm_name:
                    cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateX", -90)
                    cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateZ", -90)

                # verify if user wants to apply the good mirror orientation:
                if s == 1:
                    if not style == 0: #default
                        # these options is valides for Biped, Quadruped, Quadruped Spring and Quadruped Extra
                        if self.mirror_axis != 'off':
                            for axis in self.mirror_axis:
                                if axis == "X":
                                    if self.limb_types == self.arm_name:
                                        cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateX", -90)
                                        cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateY", 90)
                                        if self.get_guide_attr('alignWorld'):
                                            cmds.setAttr(ik_extreme_ctrl_orient_grp+".scaleX", -1)
                                        else:
                                            cmds.setAttr(ik_extreme_ctrl_orient_grp+".scaleZ", -1)
                                    else: #leg
                                        cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateX", 90)
                                        cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotateZ", -90)
                                        cmds.setAttr(ik_extreme_ctrl_orient_grp+".scaleX", -1)
                
                # to fix quadruped stretch locator after rotated ik extrem controller:
                ik_stretch_extreme_loc_zero = self.ar.utils.create_zero_out([ik_stretch_extreme_loc])[0]
                cmds.parent(ik_stretch_extreme_loc_zero, ik_extreme_sub_ctrl, absolute=True)
                expose_corner_name = corner_name+"_Jnt"
                if self.get_guide_attr('hasBend'):
                    expose_corner_name = corner_name+"_Jxt"
                if quadruped:
                    self.ik_stretch_extreme_locs.append(None)
                    expose_corner_name = corner_b_name+"_Jnt"
                    if self.get_guide_attr('hasBend'):
                        expose_corner_name = corner_b_name+"_Jxt"
                else:
                    self.ik_stretch_extreme_locs.append(ik_stretch_extreme_loc_zero)
                
                # connecting visibilities:
                cmds.connectAttr(world_ref+"."+attr_name_lower+'Fk_ikFkBlend', fk_ctrl_zeros[1]+".visibility", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_corner_ctrl_zero+".visibility", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_extreme_ctrl_zero+".visibility", force=True)
                self.ar.ctrls.set_lock_hide([ik_corner_ctrl], ['v'], l=False)
                self.ar.ctrls.set_lock_hide([ik_extreme_ctrl], ['sx', 'sy', 'sz', 'v'])

                # creating ikHandles:
                # verify the limb style:
                if quadruped:
                    # creating double ikHandle in order to get an extra control for lower articulation in Quadruped Extra Control:
                    ik_handle_main_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_IKH", startJoint=ik_joints[1], endEffector=ik_joints[len(ik_joints) - 3], solver='ikRPsolver')
                    ik_handle_not_stretch_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_NotStretch_IKH", startJoint=ik_no_stretch_joints[1], endEffector=ik_no_stretch_joints[len(ik_no_stretch_joints) - 2], solver='ikRPsolver')
                    ik_handle_auto_clavicle_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_AC_IKH", startJoint=ik_auto_clavicle_joints[1], endEffector=ik_auto_clavicle_joints[len(ik_auto_clavicle_joints) - 2], solver='ikRPsolver')
                    ik_handle_extra_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_Extra_IKH", startJoint=ik_joints[len(ik_joints) - 3], endEffector=ik_joints[len(ik_joints) - 2], solver='ikRPsolver')
                else: #default, biped
                    # using regular solution as ikRPSolver:
                    ik_handle_main_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_IKH", startJoint=ik_joints[1], endEffector=ik_joints[len(ik_joints) - 2], solver='ikRPsolver')
                    ik_handle_not_stretch_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_NotStretch_IKH", startJoint=ik_no_stretch_joints[1], endEffector=ik_no_stretch_joints[len(ik_no_stretch_joints) - 2], solver='ikRPsolver')
                    ik_handle_auto_clavicle_items = cmds.ikHandle(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_AC_IKH", startJoint=ik_auto_clavicle_joints[1], endEffector=ik_auto_clavicle_joints[len(ik_auto_clavicle_joints) - 2], solver='ikRPsolver')

                # renaming effectors:
                cmds.rename(ik_handle_main_items[1], side+self.number_name+"_"+self.limb_type.capitalize()+"_Eff")
                cmds.rename(ik_handle_not_stretch_items[1], side+self.number_name+"_"+self.limb_type.capitalize()+"_NotStretch_Eff")
                cmds.rename(ik_handle_auto_clavicle_items[1], side+self.number_name+"_"+self.limb_type.capitalize()+"_AC_Eff")

                # creating ikHandle groups:
                cmds.setAttr(ik_handle_main_items[0]+'.visibility', 0)
                ik_handle_grp = cmds.group(empty=True, name=side+self.number_name+"_IKH_Grp")
                to_rf_ik_handle_grp = cmds.group(empty=True, name=side+self.number_name+"_IKHToRF_Grp")
                self.to_rev_foot_ik_handle_grps.append(ik_handle_grp)
                cmds.setAttr(to_rf_ik_handle_grp+'.visibility', 0)
                cmds.parent(to_rf_ik_handle_grp, ik_handle_grp)
                self.ik_handle_grp_constraints.append(cmds.parentConstraint(ik_extreme_ctrl, ik_handle_grp, maintainOffset=True, name=ik_handle_grp+"_PaC"))
                # for ikHandle not stretch group:
                ik_handle_not_stretch_grp = cmds.group(empty=True, name=side+self.number_name+"_NotStretch_IKH_Grp")
                cmds.setAttr(ik_handle_not_stretch_grp+'.visibility', 0)
                cmds.parent(ik_handle_not_stretch_items[0], ik_handle_not_stretch_grp)
                # for ikHandle auto clavicle group:
                ik_handle_auto_clavicle_grp = cmds.group(empty=True, name=side+self.number_name+"_AC_IKH_Grp")
                cmds.setAttr(ik_handle_auto_clavicle_grp+'.visibility', 0)
                cmds.parent(ik_handle_auto_clavicle_items[0], ik_handle_auto_clavicle_grp)

                # setup quadruped extra control:
                if quadruped:
                    cmds.rename(ik_handle_extra_items[1], side+self.number_name+"_"+self.limb_type.capitalize()+"_Extra_Eff")
                    quad_extra_ctrl = self.ar.ctrls.create_controller("id_058_LimbQuadExtra", ctrl_name=side+self.number_name+"_"+extreme_name+"_Ik_Extra_Ctrl", r=(self.radius * 0.7), d=self.curve_degree, dir="-Z", guide_source=self.name_guide+"_Extrem", parent_tag=ik_extreme_ctrl)
                    if s == 1:
                        cmds.setAttr(quad_extra_ctrl+".rotateY", 180)
                        cmds.makeIdentity(quad_extra_ctrl, rotate=True, apply=True)
                    quad_extra_ctrl_zero = self.ar.utils.create_zero_out([quad_extra_ctrl])[0]
                    cmds.matchTransform(quad_extra_ctrl_zero, ik_extreme_ctrl, position=True, rotation=True)
                    cmds.parent(quad_extra_ctrl_zero, ik_handle_grp)
                    cmds.parent(ik_handle_extra_items[0], to_rf_ik_handle_grp)
                    cmds.setAttr(ik_handle_extra_items[0]+".visibility", 0)
                    cmds.addAttr(quad_extra_ctrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(quad_extra_ctrl+'.twist', ik_handle_extra_items[0]+".twist", force=True)
                    cmds.connectAttr(ik_fk_rev+".outputX", quad_extra_ctrl_zero+".visibility", force=True)
                    self.ar.ctrls.set_lock_hide([quad_extra_ctrl], ['sx', 'sy', 'sz', 'v'])
                
                # working with world axis orientation for limb extrem ik controls
                if self.get_guide_attr('alignWorld'):
                    original_rotate_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_"+extreme_name+"_OriginalRotate_MD")
                    align_world_rev = cmds.createNode("reverse", name=side+self.number_name+"_"+extreme_name+"_AlighWorld_Rev")
                    self.to_ids.extend([original_rotate_md, align_world_rev])
                    cmds.addAttr(ik_extreme_ctrl, longName="alignWorld", attributeType="float", defaultValue=0, minValue=0, maxValue=1, keyable=True)
                    cmds.connectAttr(ik_extreme_ctrl+".alignWorld", align_world_rev+".inputX", force=True)
                    if s == 0:
                        original_rotation = self.get_original_rotation(ik_extreme_ctrl)
                    elif style == 0: #default
                        if self.limb_types == self.arm_name:
                            # get right side to alignWorld. It'll be a little glitch, but it seems be accordilly with the mirror using arm default setting. Recommended use biped limb_style instead.
                            original_rotation = self.get_original_rotation(ik_extreme_ctrl)
                    for a, axis in enumerate(self.ar.data.axes):
                        cmds.setAttr(ik_extreme_ctrl_orient_grp+".rotate"+axis, 0)
                        cmds.setAttr(ik_extreme_ctrl_zero+".rotate"+axis, 0)
                        # store original rotation values for initial default pose
                        cmds.addAttr(ik_extreme_ctrl, longName="originalRotate"+axis, attributeType="float", keyable=True)
                        cmds.setAttr(ik_extreme_ctrl+".originalRotate"+axis, original_rotation[a], lock=True)
                        cmds.connectAttr(ik_extreme_ctrl+".originalRotate"+axis, original_rotate_md+".input1"+axis, force=True)
                        cmds.connectAttr(align_world_rev+".outputX", original_rotate_md+".input2"+axis, force=True)
                        cmds.connectAttr(original_rotate_md+".output"+axis, ik_extreme_ctrl_grp+".rotate"+axis, force=True)

                # make ikControls lead ikHandles:
                ik_handle_extra_grp = cmds.group(empty=True, name=ik_handle_main_items[0]+"_Grp")
                cmds.matchTransform(ik_handle_extra_grp, ik_handle_main_items[0], position=True, rotation=True)
                cmds.parent(ik_handle_main_items[0], ik_handle_extra_grp)
                cmds.parent(ik_handle_extra_grp, to_rf_ik_handle_grp)
                if quadruped:
                    cmds.parent(ik_handle_extra_grp, ik_stretch_extreme_loc_zero, quad_extra_ctrl)
                ik_handle_poc = cmds.pointConstraint(ik_extreme_sub_ctrl, ik_handle_extra_grp, maintainOffset=True, name=ik_handle_grp+"_PoC")[0]
                self.ik_handle_constraints.append(ik_handle_poc)
                
                cmds.orientConstraint(ik_extreme_sub_ctrl, ik_joints[len(ik_joints) - 2], maintainOffset=True, name=ik_joints[len(ik_joints) - 2]+"_OrC")
                cmds.pointConstraint(ik_extreme_sub_ctrl, ik_handle_not_stretch_items[0], maintainOffset=True, name=ik_handle_not_stretch_items[0]+"_PoC")[0]
                cmds.pointConstraint(ik_extreme_sub_ctrl, ik_handle_auto_clavicle_items[0], maintainOffset=True, name=ik_handle_auto_clavicle_items[0]+"_PoC")[0]
                cmds.orientConstraint(ik_extreme_sub_ctrl, ik_no_stretch_joints[len(ik_no_stretch_joints) - 2], maintainOffset=True, name=ik_no_stretch_joints[len(ik_no_stretch_joints) - 2]+"_OrC")

                # twist:
                cmds.addAttr(ik_extreme_ctrl, longName='twist', attributeType='float', keyable=True)
                if s == 0:
                    cmds.connectAttr(ik_extreme_ctrl+'.twist', ik_handle_main_items[0]+".twist", force=True)
                    cmds.connectAttr(ik_extreme_ctrl+'.twist', ik_handle_not_stretch_items[0]+".twist", force=True)
                    cmds.connectAttr(ik_extreme_ctrl+'.twist', ik_handle_auto_clavicle_items[0]+".twist", force=True)
                else:
                    twist_md = cmds.createNode('multiplyDivide', name=ik_extreme_ctrl+"_MD")
                    self.to_ids.append(twist_md)
                    cmds.setAttr(twist_md+'.input2X', -1)
                    cmds.connectAttr(ik_extreme_ctrl+'.twist', twist_md+'.input1X', force=True)
                    cmds.connectAttr(twist_md+'.outputX', ik_handle_main_items[0]+".twist", force=True)
                    cmds.connectAttr(twist_md+'.outputX', ik_handle_not_stretch_items[0]+".twist", force=True)
                    cmds.connectAttr(twist_md+'.outputX', ik_handle_auto_clavicle_items[0]+".twist", force=True)

                # working on corner poleVector:
                # based on Renauld Lessard swivel code: 
                # https://github.com/renaudll/omtk/blob/master/omtk/modules/rigIK.py
                
                # get joint chain positions
                start_pos  = cmds.xform(ik_joints[1], query=True, worldSpace=True, rotatePivot=True) #shoulder, leg
                corner_pos = cmds.xform(ik_joints[2], query=True, worldSpace=True, rotatePivot=True) #elbow, knee
                end_pos    = cmds.xform(ik_joints[3], query=True, worldSpace=True, rotatePivot=True) #wrist, ankle
                # calculate distances (joint lenghts)
                upper_limb_len = self.ar.math.create_dist_between(ik_joints[1], ik_joints[2])[0]
                lower_limb_len = self.ar.math.create_dist_between(ik_joints[2], ik_joints[3])[0]
                chain_len = upper_limb_len+lower_limb_len
                # ratio of placement of the middle joint
                pv_ratio = upper_limb_len / chain_len
                # calculate the position of the base middle locator
                pv_base_pos_x = (end_pos[0] - start_pos[0]) * pv_ratio+start_pos[0]
                pv_base_pos_y = (end_pos[1] - start_pos[1]) * pv_ratio+start_pos[1]
                pv_base_pos_z = (end_pos[2] - start_pos[2]) * pv_ratio+start_pos[2]
                # working with vectors
                corner_base_pos_x = corner_pos[0] - pv_base_pos_x
                corner_base_pos_y = corner_pos[1] - pv_base_pos_y
                corner_base_pos_z = corner_pos[2] - pv_base_pos_z
                # magnitude of the vector
                mag_dir = self.ar.math.magnitude([corner_base_pos_x, corner_base_pos_y, corner_base_pos_z])
                # normalize the vector
                normal_dir_x = corner_base_pos_x / mag_dir
                normal_dir_y = corner_base_pos_y / mag_dir
                normal_dir_z = corner_base_pos_z / mag_dir
                # calculate the poleVector position by multiplying the unitary vector by the chain length
                pv_dist_x = normal_dir_x * chain_len
                pv_dist_y = normal_dir_y * chain_len
                pv_dist_z = normal_dir_z * chain_len
                # get the poleVector position
                pv_pos_x = pv_base_pos_x+pv_dist_x
                pv_pos_y = pv_base_pos_y+pv_dist_y
                pv_pos_z = pv_base_pos_z+pv_dist_z
                # place poleVector zero out group in the correct position
                cmds.move(pv_pos_x, pv_pos_y, pv_pos_z, ik_corner_ctrl_zero, objectSpace=False, worldSpaceDistance=True)

                # create poleVector constraint:
                cmds.poleVectorConstraint(ik_corner_ctrl, ik_handle_main_items[0], weight=1.0, name=ik_handle_main_items[0]+"_PVC")
                cmds.poleVectorConstraint(ik_corner_ctrl, ik_handle_not_stretch_items[0], weight=1.0, name=ik_handle_not_stretch_items[0]+"_PVC")
                cmds.poleVectorConstraint(ik_corner_ctrl, ik_handle_auto_clavicle_items[0], weight=1.0, name=ik_handle_auto_clavicle_items[0]+"_PVC")

                # create annotation:
                annot_loc = cmds.spaceLocator(name=side+self.number_name+"_"+self.limb_type.capitalize()+"_Ant_Loc", position=(0, 0, 0))[0]
                annotation = cmds.annotate(annot_loc, tx="", point=(pv_pos_x, pv_pos_y, pv_pos_z))
                annotation = cmds.listRelatives(annotation, parent=True)[0]
                annotation = cmds.rename(annotation, side+self.number_name+"_"+self.limb_type.capitalize()+"_Ant")
                cmds.parent(annotation, ik_corner_ctrl)
                cmds.parent(annot_loc, ik_joints[2], relative=True)
                cmds.setAttr(annotation+'.template', 1)
                cmds.setAttr(annot_loc+'.visibility', 0)
                # set annotation visibility as a display option attribute:
                cmds.addAttr(ik_corner_ctrl, longName="displayAnnotation", attributeType='short', minValue=0, maxValue=1, keyable=False, defaultValue=1)
                cmds.setAttr(ik_corner_ctrl+".displayAnnotation", channelBox=True)
                cmds.connectAttr(ik_corner_ctrl+".displayAnnotation", annotation+".visibility", force=True)

                # prepare groups to rotate and translate automatically:
                self.ar.ctrls.set_lock_hide([ik_corner_ctrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
                self.corner_grp = cmds.group(empty=True, name=side+self.number_name+"_"+self.limb_type.capitalize()+"_PoleVector_Grp", absolute=True)
                cmds.matchTransform(self.corner_grp, ik_extreme_ctrl, position=True, rotation=True)
                cmds.parent(ik_corner_ctrl_zero, self.corner_grp, absolute=True)
                # set a good orientation for the poleVector ctrl
                cmds.setAttr(ik_corner_ctrl_zero+".rotateX", 0)
                cmds.setAttr(ik_corner_ctrl_zero+".rotateY", 0)
                cmds.setAttr(ik_corner_ctrl_zero+".rotateZ", 0)
                if s == 1:
                    cmds.setAttr(ik_corner_ctrl_zero+".scaleX", -1)
                    cmds.setAttr(ik_corner_ctrl_zero+".scaleY", -1)
                    cmds.setAttr(ik_corner_ctrl_zero+".scaleZ", -1)
                corner_grp_zero = self.ar.utils.create_zero_out([self.corner_grp])[0]
                self.ik_pole_vector_ctrl_zeros.append(corner_grp_zero)

                # working with follow behavior of the poleVector:
                pv_aim_loc = cmds.spaceLocator(name=side+self.number_name+"_"+corner_name+"_Ik_Aim_Loc")[0]
                pv_up_loc = cmds.spaceLocator(name=side+self.number_name+"_"+corner_name+"_Ik_Up_Loc")[0]
                pv_up_loc_grp = cmds.group(pv_up_loc, name=pv_up_loc+"_Grp")
                pole_vector_loc_grp = cmds.group(pv_aim_loc, pv_up_loc_grp, name=side+self.number_name+"_"+corner_name+"_Ik_Loc_Grp")
                cmds.setAttr(pole_vector_loc_grp+".visibility", 0)
                cmds.setAttr(pv_up_loc+".translateZ", self.radius)
                if pv_pos_z < 0:
                    cmds.setAttr(pv_up_loc+".translateZ", -self.radius)
                cmds.delete(cmds.pointConstraint(self.guide_main_loc, pv_aim_loc, maintainOffset=False))
                cmds.pointConstraint(ik_extreme_sub_ctrl, pv_up_loc_grp, maintainOffset=False, name=pv_up_loc_grp+"_PoC")
                for axis in self.ar.data.axes:
                    cmds.connectAttr(world_ref+".scaleX", pole_vector_loc_grp+".scale"+axis, force=True)
                
                # working with autoOrient of poleVector:
                cmds.addAttr(ik_corner_ctrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                if self.limb_types == self.arm_name:
                    cmds.setAttr(ik_corner_ctrl+'.'+self.ar.data.lang['c033_autoOrient'], 0)
                    cmds.addAttr(ik_corner_ctrl+'.'+self.ar.data.lang['c033_autoOrient'], edit=True, defaultValue=0)
                up_loc_pac = cmds.parentConstraint(ik_extreme_ctrl, root_ctrl_ref, pv_up_loc_grp, skipTranslate=["x", "y", "z"], maintainOffset=True, name=pv_up_loc_grp+"_PaC")[0]
                cmds.setAttr(up_loc_pac+".interpType", 2) #shortest
                up_loc_orient_rev = cmds.createNode('reverse', name=side+self.number_name+"_UpLocOrient_Rev")
                cmds.connectAttr(ik_corner_ctrl+'.'+self.ar.data.lang['c033_autoOrient'], up_loc_orient_rev+".inputX", force=True)
                cmds.connectAttr(ik_corner_ctrl+'.'+self.ar.data.lang['c033_autoOrient'], up_loc_pac+"."+ik_extreme_ctrl+"W0", force=True)
                cmds.connectAttr(up_loc_orient_rev+'.outputX', up_loc_pac+"."+root_ctrl_ref+"W1", force=True)
                cmds.aimConstraint(ik_extreme_sub_ctrl, pv_aim_loc, worldUpType="object", worldUpObject=pv_up_loc, aimVector=(0, 0, 1), upVector=(1, 0, 0), maintainOffset=False, name=pv_up_loc+"_AiC")
                cmds.parentConstraint(pv_aim_loc, self.corner_grp, maintainOffset=True, name=self.corner_grp+"_PaC")

                # make poleVectorCtrl's follow really pin from masterCtrl:
                cmds.addAttr(ik_corner_ctrl, longName="pin", attributeType='short', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                pv_pin_pac = cmds.parentConstraint(master_ctrl_ref, ik_corner_ctrl_zero, maintainOffset=True, name=ik_corner_ctrl_zero+"_PaC")[0]
                cmds.connectAttr(ik_corner_ctrl+'.pin', pv_pin_pac+"."+master_ctrl_ref+"W0", force=True)

                # poleVector rest calibration setup:
                corner_invert_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_"+corner_name+"_Invert_MD")
                self.to_ids.append(corner_invert_md)
                if s == 0:
                    rest_items = []
                for r, rest_axis in enumerate(self.ar.data.axes):
                    cmds.addAttr(ik_corner_ctrl, longName=self.ar.data.lang['c053_invert']+rest_axis, attributeType="bool", defaultValue=s)
                for r, rest_axis in enumerate(self.ar.data.axes):
                    corner_invert_cnd = cmds.createNode('condition', name=side+self.number_name+"_"+corner_name+"_Invert"+rest_axis+"_Cnd")
                    self.to_ids.append(corner_invert_cnd)
                    cmds.setAttr(corner_invert_cnd+".colorIfTrueR", 1)
                    cmds.setAttr(corner_invert_cnd+".colorIfFalseR", -1)
                    if s == 0:
                        rest_items.append(cmds.getAttr(pv_pin_pac+".restTranslate"+rest_axis))
                    cmds.addAttr(ik_corner_ctrl, longName="calibrateRestT"+rest_axis, attributeType='float', defaultValue=rest_items[r], keyable=False)
                    cmds.connectAttr(corner_invert_md+".output"+rest_axis, pv_pin_pac+".restTranslate"+rest_axis, force=True)
                    cmds.connectAttr(ik_corner_ctrl+"."+self.ar.data.lang['c053_invert']+rest_axis, corner_invert_cnd+".firstTerm", force=True)
                    cmds.connectAttr(corner_invert_cnd+".outColorR", corner_invert_md+".input2"+rest_axis, force=True)
                    cmds.connectAttr(ik_corner_ctrl+".calibrateRestT"+rest_axis, corner_invert_md+".input1"+rest_axis, force=True)
                    
                # quadExtraCtrl autoOrient setup:
                if quadruped:
                    cmds.addAttr(quad_extra_ctrl, longName='autoOrient', attributeType='float', minValue=0, max=1, defaultValue=1, keyable=True)
                    cmds.setAttr(quad_extra_ctrl+".autoOrient", 0)
                    quad_extra_rot_null = cmds.group(name=quad_extra_ctrl+"_AutoOrient_Null", empty=True)
                    self.ar.utils.add_attr_to_items([quad_extra_rot_null], self.ar.utils.ignore_transform_io_attr)
                    cmds.matchTransform(quad_extra_rot_null, quad_extra_ctrl, position=True, rotation=True)
                    cmds.parent(quad_extra_rot_null, to_rf_ik_handle_grp)
                    auto_orient_rev = cmds.createNode("reverse", name=quad_extra_ctrl+"_AutoOrient_Rev")
                    self.to_ids.append(auto_orient_rev)
                    auto_orient_pac = cmds.parentConstraint(to_rf_ik_handle_grp, quad_extra_rot_null, quad_extra_ctrl_zero, skipTranslate=["x", "y", "z"], maintainOffset=True, name=quad_extra_ctrl_zero+"_PaC")[0]
                    cmds.setAttr(auto_orient_pac+".interpType", 0) #noflip
                    cmds.connectAttr(quad_extra_ctrl+".autoOrient", auto_orient_rev+".inputX", force=True)
                    cmds.connectAttr(auto_orient_rev+".outputX", auto_orient_pac+"."+to_rf_ik_handle_grp+"W0", force=True)
                    cmds.connectAttr(quad_extra_ctrl+".autoOrient", auto_orient_pac+"."+quad_extra_rot_null+"W1", force=True)
                    # avoid cycle error from Maya warning:
                    cmds.cycleCheck(evaluation=False)
                    cmds.aimConstraint(shoulder_ref_grp, quad_extra_rot_null, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=ik_corner_ctrl, name=quad_extra_ctrl_zero+"_AiC")[0]
                    cmds.cycleCheck(evaluation=True)
                    # hack to parent constraint offset recalculation (Update button on Attribute Editor):
                    cmds.parentConstraint(to_rf_ik_handle_grp, quad_extra_rot_null, quad_extra_ctrl_zero, edit=True, maintainOffset=True)
                    cmds.setAttr(quad_extra_ctrl+".autoOrient", 1)
                    # another hack to avoid uniformScale flip issue
                    cmds.scaleConstraint(ik_extreme_ctrl, quad_extra_ctrl_zero, maintainOffset=True, name=quad_extra_ctrl_zero+"_ScC")

                # stretch system:
                stretch_names = [before_name, self.limb_type.capitalize()]
                dist_bet_grp = cmds.group(empty=True, name=side+self.number_name+"_DistBet_Grp")
                joint_chain_lenght_value = self.ar.utils.joint_chain_length(ik_joints[1:4])

                # creating attributes:
                cmds.addAttr(ik_extreme_ctrl, longName="startChainLength", attributeType='float', defaultValue=joint_chain_lenght_value, keyable=False)
                cmds.addAttr(ik_extreme_ctrl, longName="stretchable", attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=True)
                cmds.addAttr(ik_extreme_ctrl, longName=self.ar.data.lang['c113_length'], attributeType='float', minValue=0.001, defaultValue=1, keyable=True)
                self.ar.ctrls.set_lock_hide([ik_extreme_ctrl], ['startChainLength'])

                # creating distance betweens, multiplyDivides and reverse nodes:
                dist_between_items = self.ar.math.create_dist_between(ik_joints[1], ik_stretch_extreme_loc, name=side+self.number_name+"_"+stretch_names[1]+"_DistBet", keep=True)
                cmds.setAttr(dist_between_items[5]+"."+dist_between_items[4]+"W1", 0)
                cmds.parent(dist_between_items[2], dist_between_items[3], dist_between_items[4], dist_bet_grp)
                cmds.connectAttr(ik_extreme_ctrl+"."+self.ar.data.lang['c113_length'], world_ref+"."+self.ar.data.lang['c113_length'], force=True)
                cmds.parentConstraint(skin_joints[0], dist_between_items[4], maintainOffset=True, name=dist_between_items[4]+"_PaC")
                cmds.connectAttr(world_ref+"."+attr_name_lower+'Fk_ikFkBlendRevOutputX', dist_between_items[5]+"."+ik_stretch_extreme_loc+"W0", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+'Fk_ikFkBlend', dist_between_items[5]+"."+dist_between_items[4]+"W1", force=True)

                # (James) if we use the ribbon controls we won't implement the forearm control
                # create the forearm control if limb type is arm and there is not bend (ribbon) implementation:
                if self.limb_types == self.arm_name and self.get_guide_attr('hasBend') == False:
                    # create forearm joint:
                    forearm_joint = cmds.duplicate(skin_joints[2], name=side+self.number_name+ "_" +self.ar.data.lang[ 'c030_forearm']+suffixes[0])[0]
                    self.ar.naming.set_joint_label(forearm_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang[ 'c030_forearm'])
                    # delete its children:
                    cmds.delete(cmds.listRelatives(forearm_joint, children=True, fullPath=True) or [])
                    cmds.parent(forearm_joint, skin_joints[2])
                    # move forearm_joint to correct position:
                    temp_dist = self.ar.math.create_dist_between(skin_joints[2], skin_joints[3])[0]
                    elbow_tx_value = cmds.xform(skin_joints[2], worldSpace=True, translation=True, query=True)[0]
                    wrist_tx_value = cmds.xform(skin_joints[3], worldSpace=True, translation=True, query=True)[0]
                    if (wrist_tx_value - elbow_tx_value) > 0:
                        forearm_dist_z = temp_dist / 3
                    else:
                        forearm_dist_z = -(temp_dist / 3)
                    cmds.move(0, 0, forearm_dist_z, forearm_joint, localSpace=True, worldSpaceDistance=True)
                    # create forearm_ctrl:
                    forearm_ctrl = self.ar.ctrls.create_controller("id_037_LimbForearm", side+self.number_name+"_"+self.ar.data.lang['c030_forearm']+"_Ctrl", r=(self.radius * 0.75), d=self.curve_degree, guide_source=self.name_guide+"_Corner", parent_tag=ik_corner_ctrl)
                    forearm_grp = cmds.group(forearm_ctrl, name=side+self.number_name+"_"+self.ar.data.lang['c030_forearm']+"_Grp")
                    forearm_zero = cmds.group(forearm_grp, name=side+self.number_name+"_"+self.ar.data.lang['c030_forearm']+"_Zero_0_Grp")
                    cmds.matchTransform(forearm_zero, forearm_joint, position=True, rotation=True)
                    cmds.parentConstraint(skin_joints[2], forearm_zero, maintainOffset=True, name=forearm_zero+"_PaC")
                    cmds.orientConstraint(forearm_ctrl, forearm_joint, skip=["x", "y"], maintainOffset=True, name=forearm_joint+"_OrC")
                    # create attribute to forearm autoRotate:
                    cmds.addAttr(forearm_ctrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                    self.ar.ctrls.set_lock_hide([forearm_ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                    # make rotate connections:
                    forearm_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_"+self.ar.data.lang[ 'c030_forearm']+"_MD")
                    self.to_ids.append(forearm_md)
                    cmds.connectAttr(forearm_ctrl+'.'+self.ar.data.lang['c033_autoOrient'], forearm_md+'.input1X')
                    cmds.connectAttr(skin_joints[3]+'.rotateZ', forearm_md+'.input2X')
                    cmds.connectAttr(forearm_md+'.outputX', forearm_grp+'.rotateZ')
                    ik_extreme_orient_pac = cmds.parentConstraint(forearm_ctrl, ik_extreme_sub_ctrl, fk_joints[-2], extreme_orient_ctrl_zero, skipTranslate=["x", "y", "z"], maintainOffset=True, name=extreme_orient_ctrl_zero+"_PaC")[0]
                    ik_extreme_orient_pac_w0 = forearm_ctrl+"W0"
                    cmds.pointConstraint(skin_joints[-2], extreme_orient_ctrl_zero, maintainOffset=True, name=extreme_orient_ctrl_zero+"_PoC")

                # creating a group to receive the reverseFootCtrlGrp (if module integration is on):
                to_rf_blend_grp = cmds.group(empty=True, name=side+self.number_name+"_IkFkBlendGrpToRevFoot_Grp")
                self.to_rf_blend_grps.append(to_rf_blend_grp)
                cmds.matchTransform(to_rf_blend_grp, ik_extreme_ctrl, position=True, rotation=True)

                # offset parent constraint
                to_rf_offset_pac = cmds.parentConstraint(ik_extreme_sub_ctrl, fk_ctrls[len(fk_ctrls) - 1], ik_no_stretch_joints[-2], to_rf_blend_grp, maintainOffset=True, name=to_rf_blend_grp+"_PaC")[0]
                cmds.connectAttr(world_ref+"."+attr_name_lower+'Fk_ikFkBlend', to_rf_offset_pac+"."+fk_ctrls[len(fk_ctrls) - 1]+"W1", force=True)

                # work with scalable extrem hand or foot:
                cmds.addAttr(fk_ctrls[-1], longName=self.ar.data.lang['c040_uniformScale'], attributeType="double", minValue=0.001, defaultValue=1)
                cmds.addAttr(ik_extreme_ctrl, longName=self.ar.data.lang['c040_uniformScale'], attributeType="double", minValue=0.001, defaultValue=1)
                cmds.setAttr(fk_ctrls[-1]+"."+self.ar.data.lang['c040_uniformScale'], edit=True, keyable=True)
                cmds.setAttr(ik_extreme_ctrl+"."+self.ar.data.lang['c040_uniformScale'], edit=True, keyable=True)
                # add scale multiplier attribute
                cmds.addAttr(fk_ctrls[-1], longName=self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize(), attributeType='double', minValue=0.001, defaultValue=1)
                cmds.addAttr(ik_extreme_ctrl, longName=self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize(), attributeType='double', minValue=0.001, defaultValue=1)
                ik_scale_md = cmds.rename(cmds.createNode('multiplyDivide'), side+self.number_name+"_"+self.ar.data.lang['c105_multiplier'].capitalize()+'_Ik_MD')
                fk_scale_md = cmds.rename(cmds.createNode('multiplyDivide'), side+self.number_name+"_"+self.ar.data.lang['c105_multiplier'].capitalize()+'_Fk_MD')
                cmds.connectAttr(ik_extreme_ctrl+"."+self.ar.data.lang['c040_uniformScale'], ik_scale_md+".input1X", force=True)
                cmds.connectAttr(ik_extreme_ctrl+"." +self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize(), ik_scale_md+".input2X", force=True)
                cmds.connectAttr(fk_ctrls[-1]+"."+self.ar.data.lang['c040_uniformScale'], fk_scale_md+".input1X", force=True)
                cmds.connectAttr(fk_ctrls[-1]+"."+self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize(), fk_scale_md+".input2X", force=True)
                # integrate uniformScale and scaleMultiplier attributes
                uni_blend = cmds.createNode("blendColors", name=side+self.number_name+"_"+self.ar.data.lang['c040_uniformScale'][0].capitalize()+self.ar.data.lang['c040_uniformScale'][1:]+"_BC")
                cmds.connectAttr(uni_blend+".outputR", orig_grp+".scaleX", force=True)
                cmds.connectAttr(uni_blend+".outputR", orig_grp+".scaleY", force=True)
                cmds.connectAttr(uni_blend+".outputR", orig_grp+".scaleZ", force=True)
                cmds.connectAttr(uni_blend+".outputR", skin_joints[-2]+".scaleX", force=True)
                cmds.connectAttr(uni_blend+".outputR", skin_joints[-2]+".scaleY", force=True)
                cmds.connectAttr(uni_blend+".outputR", skin_joints[-2]+".scaleZ", force=True)
                cmds.connectAttr(uni_blend+".outputR", to_rf_blend_grp+".scaleX", force=True)
                cmds.connectAttr(uni_blend+".outputR", to_rf_blend_grp+".scaleY", force=True)
                cmds.connectAttr(uni_blend+".outputR", to_rf_blend_grp+".scaleZ", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+'Fk_ikFkBlend', uni_blend+".blender", force=True)
                cmds.connectAttr(fk_scale_md+'.outputX', uni_blend+'.color1R', force=True)
                cmds.connectAttr(ik_scale_md+'.outputX', uni_blend+'.color2R', force=True)
                
                if quadruped:
                    # tell main script to create parent constraint from chestA to ikCtrl for front legs
                    self.quad_front_legs.append(ik_extreme_ctrl_orient_grp)

                # work with not stretch ik setup:
                ik_stretchable_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_IkStretchable_MD")
                cmds.connectAttr(ik_extreme_ctrl+".stretchable", ik_stretchable_md+".input1X", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_stretchable_md+".input2X", force=True)

                ik_stretch_ctrl_cnd = cmds.createNode('condition', name=side+self.number_name+"_IkStretchCtrl_Cnd")
                cmds.setAttr(ik_stretch_ctrl_cnd+".secondTerm", 1)
                cmds.setAttr(ik_stretch_ctrl_cnd+".operation", 3)
                cmds.connectAttr(ik_stretchable_md+".outputX", ik_stretch_ctrl_cnd+".colorIfFalseR", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_stretch_ctrl_cnd+".colorIfTrueR", force=True)
                cmds.connectAttr(ik_extreme_ctrl+".stretchable", ik_stretch_ctrl_cnd+".firstTerm", force=True)
                cmds.connectAttr(ik_stretch_ctrl_cnd+".outColorR", to_rf_offset_pac+"."+ik_extreme_sub_ctrl+"W0", force=True)

                ik_stretch_dif_pma = cmds.createNode('plusMinusAverage', name=side+self.number_name+"_Stretch_Dif_PMA")
                cmds.setAttr(ik_stretch_dif_pma+".operation", 2)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_stretch_dif_pma+".input1D[0]", force=True)
                cmds.connectAttr(ik_extreme_ctrl+".stretchable", ik_stretch_dif_pma+".input1D[1]", force=True)

                ik_stretch_cnd = cmds.createNode('condition', name=side+self.number_name+"_IkStretch_Cnd")
                cmds.setAttr(ik_stretch_cnd+".operation", 3)
                cmds.setAttr(ik_stretch_cnd+".secondTerm", 1)
                cmds.connectAttr(ik_stretch_dif_pma+".output1D", ik_stretch_cnd+".colorIfFalseR", force=True)
                cmds.connectAttr(ik_extreme_ctrl+".stretchable", ik_stretch_cnd+".firstTerm", force=True)

                ik_stretch_clp = cmds.createNode('clamp', name=side+self.number_name+"_IkStretch_Clp")
                cmds.setAttr(ik_stretch_clp+".maxR", 1)
                cmds.connectAttr(ik_stretch_cnd+".outColorR", ik_stretch_clp+".inputR", force=True)
                cmds.connectAttr(ik_stretch_clp+".outputR", to_rf_offset_pac+"."+ik_no_stretch_joints[-2]+"W2", force=True)

                # prepare to disable stretch in fk mode
                cmds.addAttr(ik_extreme_ctrl, longName="disableIkFkRevOutputX", attributeType="double", keyable=False)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_extreme_ctrl+".disableIkFkRevOutputX", force=True)

                # create a masterModuleGrp to be checked if this rig exists:
                if self.limb_types == self.arm_name:
                    ctrl_hook_items = [fk_ctrl_zero_grp, corner_grp_zero, ik_extreme_ctrl_zero, extreme_orient_ctrl_zero, dist_bet_grp, orig_from_items[0], orig_from_items[1], to_rf_blend_grp, world_ref, master_ctrl_ref, root_ctrl_ref]
                    # (James) not implementing the forearm control if we use ribbons (yet)
                    if not self.get_guide_attr('hasBend'):
                        # use forearm control
                        ctrl_hook_items.append(forearm_zero)
                else: #leg
                    ctrl_hook_items = [fk_ctrl_zero_grp, corner_grp_zero, ik_extreme_ctrl_zero, dist_bet_grp, orig_from_items[0], orig_from_items[1], to_rf_blend_grp, world_ref, master_ctrl_ref, root_ctrl_ref]
                self.create_hook_setup(side, ctrl_hook_items, [skin_joints[0], ik_joints[0], fk_joints[0], ik_no_stretch_joints[0], ik_auto_clavicle_joints[1]], [ik_handle_grp, ik_handle_not_stretch_grp, ik_handle_auto_clavicle_grp, pole_vector_loc_grp])
                
                # Ribbon feature by James do Carmo, thanks!
                # (James) add bend to limb
                if self.get_guide_attr('hasBend'):
                    bend_joints_number = self.get_guide_attr('numBendJoints')
                    initial_joint = side+self.number_name+"_"+main_name+'_Jnt'
                    corner = side+self.number_name+"_"+corner_name+'_Jnt'
                    corner_jxt = side+self.number_name+"_"+corner_name+'_Jxt'
                    corner_b = side+self.number_name+"_"+corner_b_name+'_Jnt'
                    
                    splited = self.number_name.split('_')
                    prefix = ''.join(side)
                    name = ''
                    if len(splited) > 1:
                        prefix += splited[0]
                        name += splited[1]
                    else:
                        name += self.number_name
                    loc = cmds.spaceLocator(n=side+self.number_name+'_auxOriLoc', p=(0, 0, 0))[0]
                    cmds.matchTransform(loc, initial_joint, position=True, rotation=True)
                    if name == self.ar.data.lang['c006_leg_main']:  # leg
                        if s == 0:  # left side (or first side = original)
                            cmds.delete(cmds.aimConstraint(corner, loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(1, 0, 0)))
                        else:
                            cmds.delete(cmds.aimConstraint(corner, loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(-1, 0, 0)))
                    else:
                        cmds.delete(cmds.aimConstraint(corner, loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0)))

                    if self.limb_types == self.arm_name: #biped arm
                        bend_grps = self.ribbon.add_ribbon_to_limb(self, prefix, name, loc, initial_joint, 'x', bend_joints_number, corner_jxt, side=s, arm=True, world_ref=world_ref, joint_label_add=self.joint_label_add, add_artic=self.articulation, additional=self.get_guide_attr('additional'), add_correct=self.corrective, jcr_number=3, jcr_pos=[(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)])
                    elif quadruped:
                        locB = cmds.spaceLocator(n=side+self.number_name+'_auxBOriLoc', p=(0, 0, 0))[0]
                        cmds.matchTransform(locB, corner_b, position=True, rotation=True)
                        cmds.delete(cmds.aimConstraint(cmds.listRelatives(corner_b, children=True)[0], locB, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(1, 0, 0)))
                        bend_grps = self.ribbon.add_ribbon_to_limb(self, prefix, name, loc, initial_joint, 'x', bend_joints_number, side=s, arm=False, world_ref=world_ref, joint_label_add=self.joint_label_add, add_artic=self.articulation, additional=self.get_guide_attr('additional'), add_correct=self.corrective, jcr_number=3, jcr_pos=[(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)], ori_b_loc=locB)
                        cmds.delete(locB)
                    else: #biped leg
                        bend_grps = self.ribbon.add_ribbon_to_limb(self, prefix, name, loc, initial_joint, 'x', bend_joints_number, side=s, arm=False, world_ref=world_ref, joint_label_add=self.joint_label_add, add_artic=self.articulation, additional=self.get_guide_attr('additional'), add_correct=self.corrective, jcr_number=3, jcr_pos=[(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)])
                    cmds.delete(loc)

                    if self.limb_types == self.arm_name:
                        ik_extreme_orient_pac = cmds.parentConstraint(bend_grps["extraCtrlList"][-1], ik_extreme_sub_ctrl, fk_joints[-2], extreme_orient_ctrl_zero, maintainOffset=True, skipTranslate=["x", "y", "z"], name=extreme_orient_ctrl_zero+"_PaC")[0]
                        ik_extreme_orient_pac_w0 = bend_grps["extraCtrlList"][-1]+"W0"
                        cmds.pointConstraint(skin_joints[-2], extreme_orient_ctrl_zero, maintainOffset=False, name=extreme_orient_ctrl_zero+"_PoC")

                    cmds.parent(bend_grps['ctrlsGrp'], self.ctrl_hook_grp)
                    cmds.parent(bend_grps['scaleGrp'], self.scalable_hook_grp)
                    cmds.parent(bend_grps['staticGrp'], self.static_hook_grp)

                    bend_grp_items = bend_grps['bendGrpList']
                    extra_bend_items = bend_grps['extraBendGrp']

                    if bend_grp_items:
                        if not cmds.objExists(world_ref+".bends"):
                            cmds.addAttr(world_ref, longName='bends', attributeType='long', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                            cmds.addAttr(world_ref, longName='extraBends', attributeType='long', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                        for bend_grp in bend_grp_items:
                            cmds.connectAttr(world_ref+".bends", bend_grp+".visibility", force=True)
                        for extra_bend_grp in extra_bend_items:
                            cmds.connectAttr(world_ref+".extraBends", extra_bend_grp+".visibility", force=True)
                    if bend_grps['controllers']:
                        for offset_ctrl in bend_grps['controllers']:
                            cmds.connectAttr(fk_ctrls[0]+".message", offset_ctrl+".parentTag", force=True)

                    # correct joint skin naming:
                    for jnt_index in range(1, len(skin_joints) - 2):
                        skin_joints[jnt_index] = skin_joints[jnt_index].replace("_Jnt", "_Jxt")
                    
                    # implementing auto rotate twist bones:
                    # check if we have loaded the quatNode.mll Maya plugin in order to create quatToEuler node, also decomposeMatrix from matrixNodes:
                    loaded_quaternion_plugin = self.ar.config.check_loaded_plugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
                    loaded_matrix_plugin = self.ar.config.check_loaded_plugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
                    if loaded_quaternion_plugin and loaded_matrix_plugin:
                        twist_bone_md = bend_grps['twistBoneMD']
                        shoulder_child_loc = cmds.spaceLocator(name=twist_bone_md+"_Child_Loc")[0]
                        shoulder_parent_loc = cmds.spaceLocator(name=twist_bone_md+"_Parent_Loc")[0]
                        cmds.setAttr(shoulder_child_loc+".visibility", 0)
                        cmds.setAttr(shoulder_parent_loc+".visibility", 0)
                        cmds.matchTransform(shoulder_parent_loc, skin_joints[1], position=True, rotation=True)
                        cmds.parent(shoulder_parent_loc, skin_joints[0])
                        cmds.parent(shoulder_child_loc, skin_joints[1], relative=True)
                        self.ar.math.create_twist_bone_matrix(shoulder_parent_loc, shoulder_child_loc, skin_joints[1], twist_bone_md)
                    
                    # fix autoRotate flipping issue:
                    if s == 0: #left
                        cmds.setAttr(bend_grps['controllers'][0]+".invert", 1) #upCtrl
                        cmds.setAttr(bend_grps['controllers'][1]+".invert", 1) #downCtrl
                        if quadruped:
                            cmds.setAttr(bend_grps['controllers'][3]+".invert", 1) #downBCtrl

                # orient controller nodes
                if self.limb_types == self.arm_name:
                    cmds.setAttr(ik_extreme_orient_pac+".interpType", 2) #shortest
                    orient_rev = cmds.createNode("reverse", name=side+self.number_name+"_"+extreme_name+"_Orient_Rev")
                    orient_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_"+extreme_name+"_Orient_MD")
                    self.to_ids.extend([orient_rev, orient_md])
                    cmds.connectAttr(ik_extreme_ctrl+".orient", orient_rev+".inputX")
                    cmds.connectAttr(ik_extreme_ctrl+".orient", orient_md+".input1Y")
                    cmds.connectAttr(orient_rev+".outputX", orient_md+".input1X")
                    cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", orient_md+".input2X")
                    cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", orient_md+".input2Y")
                    cmds.connectAttr(orient_md+".outputX", ik_extreme_orient_pac+"."+ik_extreme_orient_pac_w0)
                    cmds.connectAttr(orient_md+".outputY", ik_extreme_orient_pac+"."+ik_extreme_sub_ctrl+"W1")
                    cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlend", ik_extreme_orient_pac+"."+fk_joints[-2]+"W2")

                # auto clavicle:
                # loading Maya matrix node
                loaded_quaternion_plugin = self.ar.config.check_loaded_plugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
                loaded_matrix_plugin = self.ar.config.check_loaded_plugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
                if loaded_quaternion_plugin and loaded_matrix_plugin:
                    # create auto clavicle group:
                    clavicle_ctrl_grp = cmds.group(name=fk_ctrls[0]+"_Grp", empty=True)
                    cmds.matchTransform(clavicle_ctrl_grp, fk_ctrl_zeros[0], position=True, rotation=True)
                    cmds.parent(clavicle_ctrl_grp, fk_ctrl_zeros[0])
                    # invert scale for right side before:
                    if s == 1:
                        cmds.setAttr(clavicle_ctrl_grp+".scaleX", -1)
                        cmds.setAttr(clavicle_ctrl_grp+".scaleY", -1)
                        cmds.setAttr(clavicle_ctrl_grp+".scaleZ", -1)
                    cmds.parent(fk_ctrls[0], clavicle_ctrl_grp, relative=True)
                    
                    # create auto clavicle attribute:
                    cmds.addAttr(fk_ctrls[0], longName=self.ar.data.lang['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                    self.add_follow_attr_name(fk_ctrls[0], self.ar.data.lang['c032_follow'])
                    
                    # ik auto clavicle locators:
                    ac_ik_up_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Up_Loc")[0]
                    ac_ik_aim_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Aim_Loc")[0]
                    ac_orig_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Orig_Loc")[0]
                    ac_fk_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Fk_Loc")[0]
                    ac_ik_main_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Ik_"+main_name+"_Loc")[0]
                    ac_ik_corner_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Ik_"+corner_name+"_Loc")[0]
                    ac_ref_main_loc = cmds.spaceLocator(name=side+self.number_name+"_AC_Ref_"+main_name+"_Loc")[0]
                    cmds.parent(ac_ik_corner_loc, ac_ik_main_loc)
                    ac_loc_grp = cmds.group(ac_ik_up_loc, ac_ik_aim_loc, ac_orig_loc, ac_fk_loc, ac_ik_main_loc, name=side+self.number_name+"_AC_Loc_Grp")
                    cmds.setAttr(ac_loc_grp+".inheritsTransform", 0) #important to calculate world space matrix to extract rotations correctlly
                    cmds.setAttr(ac_loc_grp+".visibility", 0)
                    cmds.setAttr(ac_ref_main_loc+".visibility", 0)
                    if self.limb_types == self.arm_name:
                        cmds.setAttr(ac_ik_up_loc+".translateY", 1)
                    else:
                        cmds.setAttr(ac_ik_up_loc+".translateZ", 1)
                    cmds.delete(cmds.pointConstraint(fk_ctrls[1], ac_loc_grp, maintainOffset=False))
                    cmds.parent([ac_ref_main_loc, ac_loc_grp], self.scalable_hook_grp)
                    cmds.delete(cmds.pointConstraint(ik_auto_clavicle_joints[1], ac_ref_main_loc, maintainOffset=False))
                    cmds.parentConstraint(ik_auto_clavicle_joints[1], ac_ref_main_loc, skipTranslate=["x", "y", "z"], maintainOffset=False, name=ac_ref_main_loc+"_PaC")
                    self.ar.ctrls.direct_connect(ac_ref_main_loc, ac_ik_main_loc, ['rx', 'ry', 'rz']) #shoulder rotate
                    cmds.matchTransform(ac_ik_corner_loc, fk_ctrls[2], position=True, rotation=True)
                    cmds.parentConstraint(ac_ik_main_loc, ac_ik_up_loc, maintainOffset=True, name=ac_ik_up_loc+"_PaC")
                    
                    # aim constraint: (edited in order to point to limb corner (elbow/knee) outside of clavicle hierarchy to avoid cycle error).
                    if self.limb_types == self.arm_name:
                        if s == 0: #left
                            cmds.aimConstraint(ac_ik_corner_loc, ac_ik_aim_loc, maintainOffset=True, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="object", worldUpObject=ac_ik_up_loc, name=ac_ik_aim_loc+"_AiC")
                        else: #right
                            cmds.aimConstraint(ac_ik_corner_loc, ac_ik_aim_loc, maintainOffset=True, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0), worldUpType="object", worldUpObject=ac_ik_up_loc, name=ac_ik_aim_loc+"_AiC")
                    else: #leg
                        cmds.aimConstraint(ac_ik_corner_loc, ac_ik_aim_loc, maintainOffset=True, weight=1, aimVector=(0, -1, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=ac_ik_up_loc, name=ac_ik_aim_loc+"_AiC")
                    
                    # fk auto clavicle setup:
                    self.ar.ctrls.direct_connect(fk_ctrls[1], ac_fk_loc, ['rx', 'ry', 'rz'])
                    # auto clavicle matrix rotate extraction:
                    ac_ik_mm = cmds.createNode("multMatrix", name=side+self.number_name+"_AC_Ik_MM")
                    ac_ik_dm = cmds.createNode("decomposeMatrix", name=side+self.number_name+"_AC_Ik_DM")
                    ac_ik_qte = cmds.createNode("quatToEuler", name=side+self.number_name+"_AC_Ik_QtE")
                    ac_fk_mm = cmds.createNode("multMatrix", name=side+self.number_name+"_AC_Fk_MM")
                    ac_fk_dm = cmds.createNode("decomposeMatrix", name=side+self.number_name+"_AC_Fk_DM")
                    ac_fk_qte = cmds.createNode("quatToEuler", name=side+self.number_name+"_AC_Fk_QtE")
                    ac_bc = cmds.createNode("blendColors", name=side+self.number_name+"_AC_BC")
                    ac_inv_bc = cmds.createNode("blendColors", name=side+self.number_name+"_AC_Inv_BC")
                    ac_inv_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_AC_Inv_MD")
                    ac_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_AC_MD")
                    self.to_ids.extend([ac_ik_mm, ac_ik_dm, ac_ik_qte, ac_fk_mm, ac_fk_dm, ac_fk_qte, ac_bc, ac_inv_bc, ac_inv_md, ac_md])
                    cmds.setAttr(ac_fk_qte+".inputRotateOrder", 1) #yzx
                    # add attributes to control inverse value setup to blend ikFk:
                    for ik_fk_rot_attr in ["ikRotateX", "ikRotateY", "ikRotateZ", "fkRotateX", "fkRotateY", "fkRotateZ"]: #ikFkRotAttrList
                        cmds.addAttr(fk_ctrls[0], longName=ik_fk_rot_attr, attributeType="float", minValue=-1, defaultValue=1, maxValue=1)
                    # set values of ik and fk rotates:
                    if s == 0: #left side
                        if self.limb_types == self.leg_name:
                            cmds.setAttr(fk_ctrls[0]+".ikRotateY", -1)
                            cmds.setAttr(fk_ctrls[0]+".fkRotateX", -1)
                    else: #right side
                        if self.limb_types == self.arm_name:
                            cmds.setAttr(fk_ctrls[0]+".ikRotateY", -1)
                        else: #leg
                            cmds.setAttr(fk_ctrls[0]+".fkRotateX", -1)
                        cmds.setAttr(fk_ctrls[0]+".ikRotateZ", -1)

                    # connections inverse values from fkCtrlList[0] (Clavile or Hips) to inverseBlendColor:
                    cmds.connectAttr(fk_ctrls[0]+".ikRotateX", ac_inv_bc+".color2R", force=True)
                    cmds.connectAttr(fk_ctrls[0]+".ikRotateY", ac_inv_bc+".color2G", force=True)
                    cmds.connectAttr(fk_ctrls[0]+".ikRotateZ", ac_inv_bc+".color2B", force=True)
                    cmds.connectAttr(fk_ctrls[0]+".fkRotateX", ac_inv_bc+".color1R", force=True)
                    cmds.connectAttr(fk_ctrls[0]+".fkRotateY", ac_inv_bc+".color1G", force=True)
                    cmds.connectAttr(fk_ctrls[0]+".fkRotateZ", ac_inv_bc+".color1B", force=True)

                    # connections auto clavicle Ik:
                    cmds.connectAttr(ac_orig_loc+".worldInverseMatrix[0]", ac_ik_mm+".matrixIn[0]", force=True)
                    cmds.connectAttr(ac_ik_aim_loc+".worldMatrix[0]", ac_ik_mm+".matrixIn[1]", force=True)
                    cmds.connectAttr(ac_ik_mm+".matrixSum", ac_ik_dm+".inputMatrix", force=True)
                    cmds.connectAttr(ac_ik_dm+".outputQuatX", ac_ik_qte+".inputQuatX", force=True)
                    cmds.connectAttr(ac_ik_dm+".outputQuatY", ac_ik_qte+".inputQuatY", force=True)
                    cmds.connectAttr(ac_ik_dm+".outputQuatZ", ac_ik_qte+".inputQuatZ", force=True)
                    cmds.connectAttr(ac_ik_dm+".outputQuatW", ac_ik_qte+".inputQuatW", force=True)
                    # connections auto clavicle Fk:
                    cmds.connectAttr(ac_orig_loc+".worldInverseMatrix[0]", ac_fk_mm+".matrixIn[0]", force=True)
                    cmds.connectAttr(ac_fk_loc+".worldMatrix[0]", ac_fk_mm+".matrixIn[1]", force=True)
                    cmds.connectAttr(ac_fk_mm+".matrixSum", ac_fk_dm+".inputMatrix", force=True)
                    cmds.connectAttr(ac_fk_dm+".outputQuatX", ac_fk_qte+".inputQuatX", force=True)
                    cmds.connectAttr(ac_fk_dm+".outputQuatY", ac_fk_qte+".inputQuatY", force=True)
                    cmds.connectAttr(ac_fk_dm+".outputQuatZ", ac_fk_qte+".inputQuatZ", force=True)
                    cmds.connectAttr(ac_fk_dm+".outputQuatW", ac_fk_qte+".inputQuatW", force=True)
                    # fk to auto clavicle blend colors:
                    if self.limb_types == self.arm_name:
                        cmds.connectAttr(ac_fk_qte+".outputRotate.outputRotateX", ac_bc+".color1G", force=True)
                        cmds.connectAttr(ac_fk_qte+".outputRotate.outputRotateY", ac_bc+".color1B", force=True)
                        cmds.connectAttr(ac_fk_qte+".outputRotate.outputRotateZ", ac_bc+".color1R", force=True)
                    else: #leg
                        cmds.connectAttr(ac_fk_qte+".outputRotate.outputRotateX", ac_bc+".color1B", force=True)
                        cmds.connectAttr(ac_fk_qte+".outputRotate.outputRotateY", ac_bc+".color1R", force=True)
                        cmds.connectAttr(ac_fk_qte+".outputRotate.outputRotateZ", ac_bc+".color1G", force=True)
                    # ik to auto clavicle blend colors:
                    cmds.connectAttr(ac_ik_qte+".outputRotate.outputRotateX", ac_bc+".color2R", force=True)
                    cmds.connectAttr(ac_ik_qte+".outputRotate.outputRotateY", ac_bc+".color2G", force=True)
                    cmds.connectAttr(ac_ik_qte+".outputRotate.outputRotateZ", ac_bc+".color2B", force=True)
                    cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlend", ac_bc+".blender", force=True)
                    cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlend", ac_inv_bc+".blender", force=True)
                    cmds.connectAttr(ac_bc+".output.outputR", ac_inv_md+".input1X", force=True)
                    cmds.connectAttr(ac_bc+".output.outputG", ac_inv_md+".input1Y", force=True)
                    cmds.connectAttr(ac_bc+".output.outputB", ac_inv_md+".input1Z", force=True)
                    cmds.connectAttr(ac_inv_bc+".output.outputR", ac_inv_md+".input2X", force=True)
                    cmds.connectAttr(ac_inv_bc+".output.outputG", ac_inv_md+".input2Y", force=True)
                    cmds.connectAttr(ac_inv_bc+".output.outputB", ac_inv_md+".input2Z", force=True)
                    cmds.connectAttr(ac_inv_md+".outputX", ac_md+".input1X", force=True)
                    cmds.connectAttr(ac_inv_md+".outputY", ac_md+".input1Y", force=True)
                    cmds.connectAttr(ac_inv_md+".outputZ", ac_md+".input1Z", force=True)
                    cmds.connectAttr(fk_ctrls[0]+"."+self.ar.data.lang['c032_follow'], ac_md+".input2X", force=True)
                    cmds.connectAttr(fk_ctrls[0]+"."+self.ar.data.lang['c032_follow'], ac_md+".input2Y", force=True)
                    cmds.connectAttr(fk_ctrls[0]+"."+self.ar.data.lang['c032_follow'], ac_md+".input2Z", force=True)
                    if self.limb_types == self.arm_name:
                        cmds.connectAttr(ac_md+".outputX", clavicle_ctrl_grp+".rotateZ", force=True)
                        cmds.connectAttr(ac_md+".outputY", clavicle_ctrl_grp+".rotateX", force=True)
                        cmds.connectAttr(ac_md+".outputZ", clavicle_ctrl_grp+".rotateY", force=True)
                    else: #leg
                        cmds.connectAttr(ac_md+".outputX", clavicle_ctrl_grp+".rotateX", force=True)
                        cmds.connectAttr(ac_md+".outputY", clavicle_ctrl_grp+".rotateZ", force=True)
                        cmds.connectAttr(ac_md+".outputZ", clavicle_ctrl_grp+".rotateY", force=True)
                
                # arrange correct before and extrem skinning joints naming in order to be easy to skinning paint weight UI:
                # default value for 5 bend joints:
                before_number  = "00" #clavicle/hips
                first_number   = "01" #shoulder/leg
                corner_number  = "07" #elbow/knee
                corner_b_number = "13" #knee_b
                extreme_number  = "13" #wrist/ankle
                if quadruped:
                    extreme_number = "19" #ankle
                if self.get_guide_attr('hasBend'):
                    if not self.articulation:
                        extreme_number = "11"
                        if quadruped:
                            extreme_number = "16"
                    bend_joints_number = self.get_guide_attr('numBendJoints')
                    if bend_joints_number == 3:
                        corner_number = "05"
                        corner_b_number = "09"
                        extreme_number = "09"
                        if quadruped:
                            extreme_number = "13"
                        if not self.articulation:
                            extreme_number = "07"
                            if quadruped:
                                extreme_number = "10"
                    elif bend_joints_number == 7:
                        corner_number = "09"
                        corner_b_number = "17"
                        extreme_number = "17"
                        if quadruped:
                            extreme_number = "25"
                        if not self.articulation:
                            extreme_number = "15"
                            if quadruped:
                                extreme_number = "22"
                    skin_joints[0] = cmds.rename(skin_joints[0], side+self.number_name+"_"+before_number+"_"+before_name+suffixes[0]) #clavicle/hips
                    skin_joints[-2] = cmds.rename(skin_joints[-2], side+self.number_name+"_"+extreme_number+"_"+extreme_name+suffixes[0]) #wrist/ankle
                    if self.articulation:
                        corner_joints, corner_b_joints = [], []
                        if bend_grps:
                            bend_joints = cmds.listRelatives(bend_grps['jntGrp'])
                            self.ar.naming.set_joint_label(cmds.listRelatives(bend_joints[bend_joints_number])[0], s+self.joint_label_add, 18, self.number_name+"_"+corner_number+"_"+corner_name)
                            jar = cmds.rename(cmds.listRelatives(bend_joints[bend_joints_number])[0], side+self.number_name+"_"+corner_number+"_"+corner_name+"_Jar")
                            corner_joints.append(jar)
                            if quadruped:
                                self.ar.naming.set_joint_label(cmds.listRelatives(bend_joints[bend_joints_number*2+1])[0], s+self.joint_label_add, 18, self.number_name+"_"+corner_b_number+"_"+corner_b_name)
                                jar = cmds.rename(cmds.listRelatives(bend_joints[bend_joints_number*2+1])[0], side+self.number_name+"_"+corner_b_number+"_"+corner_b_name+"_Jar")
                                corner_b_joints.append(jar)
                                if self.ar.data.lang['c056_front'] in self.number_name:
                                    if s == 0:
                                        cmds.setAttr(corner_joints[0]+".rotateX", 0)
                                    else:
                                        cmds.setAttr(corner_joints[0]+".rotateX", 180)
                                else:
                                    if s == 0:
                                        cmds.setAttr(corner_b_joints[0]+".rotateX", 0)
                                    else:
                                        cmds.setAttr(corner_b_joints[0]+".rotateX", 180)
                            if self.corrective:
                                corner_joints.extend(self.rename_corner_rename(s, side, corner_joints[0], corner_number, corner_name))
                                if quadruped:
                                    corner_b_joints.extend(self.rename_corner_rename(s, side, corner_b_joints[0], corner_b_number, corner_b_name))
                            if to_corner_bend_items:
                                self.ar.utils.set_origined_from_attr(bend_grps['controllers'][2], ";".join(to_corner_bend_items))
                                cmds.delete(side+self.number_name+"_"+corner_name+"_OrigFrom_Grp_PaC")
                                cmds.parentConstraint(bend_grps['controllers'][2], side+self.number_name+"_"+corner_name+"_OrigFrom_Grp", maintainOffset=True, name=side+self.number_name+"_"+corner_name+"_OrigFrom_Grp_PaC")
                else:
                    if self.corrective:
                        corner_joints = self.ar.utils.create_articulation_joint(skin_joints[1], skin_joints[2], 3, [(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)])
                        if quadruped:
                            corner_b_joints = self.ar.utils.create_articulation_joint(skin_joints[2], skin_joints[3], 3, [(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)])
                    else:
                        corner_joints = self.ar.utils.create_articulation_joint(skin_joints[1], skin_joints[2])
                        if quadruped:
                            corner_b_joints = self.ar.utils.create_articulation_joint(skin_joints[2], skin_joints[3])
                    # fixing jar rotations
                    if s == 0:
                        if self.limb_type == self.arm_name:
                            cmds.setAttr(corner_joints[0]+".rotateY", -90)
                            cmds.setAttr(corner_joints[0]+".rotateZ", -90)
                        else:
                            cmds.setAttr(corner_joints[0]+".rotateY", 90)
                            if quadruped:
                                if self.ar.data.lang['c056_front'] in self.number_name:
                                    cmds.setAttr(corner_joints[0]+".rotateX", 180)
                                    cmds.setAttr(corner_b_joints[0]+".rotateX", -90)
                                    cmds.setAttr(corner_b_joints[0]+".rotateY", 90)
                                    cmds.setAttr(corner_b_joints[0]+".rotateZ", 180)
                                else:
                                    cmds.setAttr(corner_joints[0]+".rotateX", 0)
                                    cmds.setAttr(corner_b_joints[0]+".rotateY", 90)
                                cmds.setAttr(corner_joints[0]+".rotateZ", 180)
                                cmds.setAttr(corner_b_joints[0]+".rotateX", 0)
                            else:
                                cmds.setAttr(corner_joints[0]+".rotateX", -90)
                                cmds.setAttr(corner_joints[0]+".rotateZ", 90)
                    else:
                        if self.limb_type == self.arm_name:
                            cmds.setAttr(corner_joints[0]+".rotateX", 180)
                            cmds.setAttr(corner_joints[0]+".rotateY", 90)
                            cmds.setAttr(corner_joints[0]+".rotateZ", 90)
                        else:
                            cmds.setAttr(corner_joints[0]+".rotateY", -90)
                            if quadruped:
                                cmds.setAttr(corner_joints[0]+".rotateZ", 180)
                                if self.ar.data.lang['c056_front'] in self.number_name:
                                    cmds.setAttr(corner_joints[0]+".rotateX", 180)
                                    cmds.setAttr(corner_b_joints[0]+".rotateX", 90)
                                    cmds.setAttr(corner_b_joints[0]+".rotateY", -90)
                                    cmds.setAttr(corner_b_joints[0]+".rotateZ", 90)
                                else:
                                    cmds.setAttr(corner_b_joints[0]+".rotateY", -90)
                                    cmds.setAttr(corner_b_joints[0]+".rotateX", 0)
                            else:
                                cmds.setAttr(corner_joints[0]+".rotateX", 90)
                                cmds.setAttr(corner_joints[0]+".rotateZ", 90)

                # orient controller setup
                if self.limb_types == self.arm_name:
                    extreme_old_name = skin_joints[-2]
                    extreme_new_name = extreme_old_name.replace("_Jnt", "_Jxt")
                    cmds.setAttr(extreme_old_name+".visibility", 0)
                    cmds.rename(extreme_old_name, extreme_new_name)
                    skin_joints[-2] = extreme_new_name
                    cmds.select(clear=True)
                    cmds.joint(name=extreme_old_name)
                    orient_joint_end = cmds.joint(name=extreme_old_name.replace("Jnt", "Orient_"+self.ar.data.joint_end_attr))
                    self.ar.utils.add_joint_end_attr([orient_joint_end])
                    cmds.parentConstraint(extreme_orient_ctrl, extreme_old_name, maintainOffset=False, name=extreme_old_name+"_PaC")
                    cmds.matchTransform(orient_joint_end, skin_joints[-1], position=True, rotation=True)
                    cmds.addAttr(extreme_old_name, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.naming.set_joint_label(extreme_old_name, s+self.joint_label_add, 18, self.number_name+"_"+joint_names[len(skin_joints)-2])
                    cmds.parent(extreme_old_name, self.scalable_hook_grp)
                    cmds.connectAttr(uni_blend+".outputR", extreme_old_name+".scaleX", force=True)
                    cmds.connectAttr(uni_blend+".outputR", extreme_old_name+".scaleY", force=True)
                    cmds.connectAttr(uni_blend+".outputR", extreme_old_name+".scaleZ", force=True)
                    cmds.connectAttr(uni_blend+".outputR", extreme_orient_ctrl_zero+".scaleX", force=True)
                    cmds.connectAttr(uni_blend+".outputR", extreme_orient_ctrl_zero+".scaleY", force=True)
                    cmds.connectAttr(uni_blend+".outputR", extreme_orient_ctrl_zero+".scaleZ", force=True)

                # corrective variables:
                is_leg = False
                main_jar_y_value = 0.3
                main_axis_order = 0
                if self.limb_type == self.leg_name:
                    is_leg = True
                    main_jar_y_value = -0.3
                    main_axis_order = 3
                # Roll, Yaw, Pitch
                # Hour/AntiHour, Left/Right, Up/Down

                # corner corrective network:
                corrective_ctrl = to_parent_extrem_ctrl
                corrective_b_ctrl = to_parent_extrem_ctrl
                if self.get_guide_attr('hasBend'):
                    corrective_ctrl = bend_grps['controllers'][2]
                    if quadruped:
                        corrective_b_ctrl = bend_grps['controllers'][3]
                corner_corrective_net = self.setup_corrective_net(corrective_ctrl, skin_joints[1], skin_joints[2], side+self.number_name+"_"+joint_names[2]+"_YawRight", 0, 0, -110, is_leg, [side+self.number_name+"_"+joint_names[2]+"_YawLeft", 1, 1, -110])
                corrective_net_input_value = cmds.getAttr(corner_corrective_net+".inputValue")
                if corrective_net_input_value > 0:
                    cmds.setAttr(corner_corrective_net+".inputEnd", corrective_net_input_value+110)
                if quadruped:
                    corner_b_corrective_net = self.setup_corrective_net(corrective_b_ctrl, skin_joints[2], skin_joints[3], side+self.number_name+"_"+joint_names[3]+"_YawRight", 0, 0, -110, is_leg, [side+self.number_name+"_"+joint_names[3]+"_YawLeft", 1, 1, -110])
                    corrective_b_net_input_value = cmds.getAttr(corner_b_corrective_net+".inputValue")
                    if corrective_b_net_input_value <= 0:
                        cmds.setAttr(corner_b_corrective_net+".inputEnd", corrective_b_net_input_value+110)

                # add hook attributes to be read when rigging integrated modules:
                cmds.parentConstraint(self.ctrl_hook_grp, self.scalable_hook_grp, maintainOffset=True, name=self.scalable_hook_grp+"_PaC")
                cmds.parentConstraint(self.ctrl_hook_grp, pv_aim_loc, skipRotate=["x", "y", "z"], maintainOffset=True, name=pv_aim_loc+"_PaC")
                self.scalable_grps.append(self.scalable_hook_grp)

                # add main articulationJoint:
                if self.articulation:
                    before_jxt = cmds.duplicate(skin_joints[0], name=side+self.number_name+"_"+joint_names[0]+"_Jxt")[0]
                    cmds.delete(cmds.listRelatives(before_jxt, children=True, allDescendents=True, fullPath=True))
                    if self.corrective:
                        # corrective controls group
                        self.corrective_ctrls_grp = cmds.group(name=side+self.number_name+"_Corrective_Grp", empty=True)
                        self.corrective_ctrl_grps.append(self.corrective_ctrls_grp)
                        cmds.parent(self.corrective_ctrls_grp, self.ctrl_hook_grp)
                        
                        # clavicle / hips
                        before_corrective_nets = [None]
                        before_corrective_nets.append(self.setup_corrective_net(fk_ctrls[0], self.scalable_hook_grp, skin_joints[0], side+self.number_name+"_"+joint_names[0]+"_PitchUp", 1, 1, 60, is_leg, [side+self.number_name+"_"+joint_names[0]+"_PitchUp", 1, 1, 60]))
                        before_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, True, False, False, False, False)
                        before_joints = self.ar.utils.create_articulation_joint(before_jxt, skin_joints[0], 1, [(0.3*self.radius, 0, 0.3*self.radius)])
                        self.setup_corrective_controllers(before_joints, s, self.number_name+"_"+before_number+"_"+before_name, before_corrective_nets, before_calibrate_presets, inverts)

                        # shoulder / leg
                        main_corrective_nets = [None]
                        main_corrective_nets.append(self.setup_corrective_net(fk_ctrls[0], shoulder_ref_grp, skin_joints[1], side+self.number_name+"_"+joint_names[1]+"_PitchUp", 0, main_axis_order, -91, is_leg, [side+self.number_name+"_"+joint_names[1]+"_PitchDown", 0, main_axis_order, 91]))
                        main_corrective_nets.append(self.setup_corrective_net(fk_ctrls[0], shoulder_ref_grp, skin_joints[1], side+self.number_name+"_"+joint_names[1]+"_YawRight", 1, 1, 46, is_leg, [side+self.number_name+"_"+joint_names[1]+"_YawLeft", 1, 4, 91]))
                        main_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, True, False, False, False)
                        main_joints = self.ar.utils.create_articulation_joint(shoulder_ref_grp, skin_joints[1], 2, [(0, main_jar_y_value*self.radius, 0), (0.3*self.radius, 0, 0)])
                        self.setup_corrective_controllers(main_joints, s, self.number_name+"_"+first_number+"_"+main_name, main_corrective_nets, main_calibrate_presets, inverts)
                        
                        # elbow / knee
                        corner_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, False, True, False, False)
                        corner_corrective_nets = [None, corner_corrective_net, corner_corrective_net, corner_corrective_net]
                        self.setup_corrective_controllers(corner_joints, s, self.number_name+"_"+corner_number+"_"+corner_name, corner_corrective_nets, corner_calibrate_presets, inverts)

                        # quadruped knee_b
                        if quadruped:
                            corner_b_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, False, False, True, False)
                            corner_b_corrective_nets = [None, corner_b_corrective_net, corner_b_corrective_net, corner_b_corrective_net]
                            self.setup_corrective_controllers(corner_b_joints, s, self.number_name+"_"+corner_b_number+"_"+corner_b_name, corner_b_corrective_nets, corner_b_calibrate_presets, inverts)
                        
                        # wrist / ankle
                        extreme_corrective_nets = [None]
                        if self.limb_types == self.arm_name:
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, side+self.number_name+"_"+joint_names[-1]+"_PitchUp", 1, 4, 80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_PitchUp", 1, 1, 80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, side+self.number_name+"_"+joint_names[-1]+"_PitchDown", 1, 4, -80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_PitchDown", 1, 1, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, side+self.number_name+"_"+joint_names[-1]+"_YawRight", 0, 2, -80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_YawRight", 0, 0, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, side+self.number_name+"_"+joint_names[-1]+"_YawLeft", 0, 2, 80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_YawLeft", 0, 0, 80]))
                        else: #leg
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], side+self.number_name+"_"+joint_names[-1]+"_PitchUp", 1, 4, 80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_PitchUp", 1, 1, 80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], side+self.number_name+"_"+joint_names[-1]+"_PitchDown", 1, 4, -80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_PitchDown", 1, 1, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], side+self.number_name+"_"+joint_names[-1]+"_YawRight", 0, 2, -80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_YawRight", 0, 0, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], side+self.number_name+"_"+joint_names[-1]+"_YawLeft", 0, 2, 80, is_leg, [side+self.number_name+"_"+joint_names[-1]+"_YawLeft", 0, 0, 80]))
                        extreme_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, False, False, False, True)
                        if self.limb_types == self.arm_name:
                            extreme_joints = self.ar.utils.create_articulation_joint(skin_joints[-3], skin_joints[-2], 4, [(0.2*self.radius, 0, 0), (-0.2*self.radius, 0, 0), (0, 0.2*self.radius, 0), (0, -0.2*self.radius, 0)], orient_ctrl=extreme_orient_ctrl)
                        else:
                            extreme_joints = self.ar.utils.create_articulation_joint(skin_joints[-3], skin_joints[-2], 4, [(0.2*self.radius, 0, 0), (-0.2*self.radius, 0, 0), (0, 0.2*self.radius, 0), (0, -0.2*self.radius, 0)])
                        self.setup_corrective_controllers(extreme_joints, s, self.number_name+"_"+extreme_number+"_"+extreme_name, extreme_corrective_nets, extreme_calibrate_presets, inverts)
                        # fix rotate with 100% of value for the wrist axis - Thanks Andre Ruegger for the help!
                        extreme_jax = cmds.listRelatives(extreme_joints[0], parent=True, type="joint")[0]
                        orient_connection = cmds.listConnections(extreme_jax+".rotateZ", destination=False, source=True, plugs=True)[0]
                        cmds.disconnectAttr(orient_connection, extreme_jax+".rotateZ")
                        jax_rot_z_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_"+extreme_name+"_RotZ_Fix_MD")
                        self.to_ids.append(jax_rot_z_md)
                        cmds.setAttr(jax_rot_z_md+".input2Z", 2)
                        cmds.connectAttr(orient_connection, jax_rot_z_md+".input1Z", force=True)
                        cmds.connectAttr(jax_rot_z_md+".outputZ", extreme_jax+".rotateZ", force=True)
                        # expose ankle data to be replaced by foot connections when integrating modules
                        self.ankle_articulations.append([extreme_jax, extreme_joints[0]+"_OrC", side+self.number_name+"_"+expose_corner_name])
                        self.ankle_correctives.append(extreme_corrective_nets)

                    else:
                        before_joints = self.ar.utils.create_articulation_joint(before_jxt, skin_joints[0])
                        main_joints = self.ar.utils.create_articulation_joint(shoulder_ref_grp, skin_joints[1])
                        if not corner_joints:
                            corner_joints = self.ar.utils.create_articulation_joint(skin_joints[1], skin_joints[2], do_scale=False)
                            if quadruped:
                                corner_b_joints = self.ar.utils.create_articulation_joint(skin_joints[2], skin_joints[3], do_scale=False)
                        if self.limb_types == self.arm_name:
                            extreme_joints = self.ar.utils.create_articulation_joint(skin_joints[-3], skin_joints[-2], orient_ctrl=extreme_orient_ctrl)
                        else:
                            extreme_joints = self.ar.utils.create_articulation_joint(skin_joints[-3], skin_joints[-2])
                        self.ar.naming.set_joint_label(corner_joints[0], s+self.joint_label_add, 18, self.number_name+"_01_"+corner_name)
                        cmds.rename(corner_joints[0], side+self.number_name+"_"+corner_number+"_"+corner_name+"_Jar")
                        if quadruped:
                            self.ar.naming.set_joint_label(corner_b_joints[0], s+self.joint_label_add, 18, self.number_name+"_01_"+corner_b_name)
                            cmds.rename(corner_b_joints[0], side+self.number_name+"_"+corner_b_number+"_"+corner_b_name+"_Jar")
                        self.ankle_articulations.append([cmds.listRelatives(extreme_joints[0], parent=True, type="joint")[0], extreme_joints[0]+"_OrC", side+self.number_name+"_"+expose_corner_name])
                        self.ankle_correctives.append(None)
                        cmds.setAttr(before_joints[0]+"_OrC.interpType", 1) #average
                    if extreme_joints:
                        extreme_jax_items = cmds.listRelatives(extreme_joints[0], parent=True, type="joint")
                        if extreme_jax_items:
                            cmds.setAttr(extreme_jax_items[0]+".segmentScaleCompensate", 1)
                    if s == 1:
                        for jar in [before_joints[0], main_joints[0], extreme_joints[0]]:
                            cmds.setAttr(jar+".rotateX", 180)
                            cmds.setAttr(jar+".scaleX", -1)
                    self.ar.naming.set_joint_label(before_joints[0], s+self.joint_label_add, 18, self.number_name+"_00_"+before_name)
                    self.ar.naming.set_joint_label(main_joints[0], s+self.joint_label_add, 18, self.number_name+"_"+first_number+"_"+main_name)
                    self.ar.naming.set_joint_label(extreme_joints[0], s+self.joint_label_add, 18, self.number_name+"_"+extreme_number+"_"+extreme_name)
                    main_joints[0] = cmds.rename(main_joints[0], side+self.number_name+"_"+first_number+"_"+main_name+"_Jar")
                    extreme_joints[0] = cmds.rename(extreme_joints[0], side+self.number_name+"_"+extreme_number+"_"+extreme_name+"_Jar")
                else:
                    self.ankle_articulations.append(None)
                    self.ankle_correctives.append(None)

                # add main sub controller
                if self.articulation:
                    if self.get_guide_attr('hasBend'):
                        if bend_grps:
                            main_jar = main_joints[0]
                            main_jax = cmds.listRelatives(main_joints[0], parent=True, type="joint")[0]
                            main_sub_ctrl = self.ar.ctrls.create_controller("id_095_LimbMainSub", ctrl_name=side+self.number_name+"_"+main_name+"_Sub_Ctrl", r=(self.radius * 0.9), d=self.curve_degree, guide_source=self.name_guide+"_Main", parent_tag=fk_ctrls[0])
                            self.ar.ctrls.set_lock_hide([main_sub_ctrl], ["sx", "sy", "sz", "v"])
                            self.ar.ctrls.set_sub_ctrl_display(fk_ctrls[0], main_sub_ctrl, 0)
                            main_sub_ctrl_zero = self.ar.utils.create_zero_out([main_sub_ctrl])[0]
                            cmds.delete(bend_grps['bottomPosPaC'][1])
                            pac1 = cmds.parentConstraint(main_jax, main_sub_ctrl_zero, maintainOffset=False, name=main_sub_ctrl_zero+"_PaC")[0]
                            pac2 = cmds.parentConstraint(main_sub_ctrl, main_jar, maintainOffset=True, name=main_jar+"_PaC")[0]
                            pac3 = cmds.parentConstraint(main_jar, bend_grps['bottomPosPaC'][0], maintainOffset=True, name=bend_grps['bottomPosPaC'][0]+"_PaC")[0]
                            cmds.setAttr(pac1+".interpType", 0) #noFlip
                            cmds.setAttr(pac2+".interpType", 0) #noFlip
                            cmds.setAttr(pac3+".interpType", 0) #noFlip
                            cmds.parent(main_sub_ctrl_zero, self.ctrl_hook_grp)

                # softIk:
                self.soft_ik_calibrate_items.append(self.soft_ik.create_soft_ik(side+self.number_name, ik_extreme_ctrl, ik_handle_main_items[0], ik_joints[1:4], skin_joints[1:4], dist_between_items[1], world_ref))
                # orient ikHandle group setup:
                soft_ik_orient_loc = cmds.spaceLocator(name=side+self.number_name+"_SoftIk_Aim_Loc")[0]
                cmds.matchTransform(soft_ik_orient_loc, ik_joints[1], position=True, rotation=True)
                cmds.parent(soft_ik_orient_loc, ik_joints[0])
                cmds.aimConstraint(ik_extreme_ctrl, soft_ik_orient_loc, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, 1.0, 0.0), worldUpType="object", worldUpObject=ik_corner_ctrl, name=soft_ik_orient_loc+"_AiC")
                cmds.orientConstraint(soft_ik_orient_loc, ik_handle_extra_grp, maintainOffset=False, name=ik_handle_grp+"_OrC")
                # leg with softIk on and stretchable equals to zero reverser foot issue fix:
                if self.limb_type == self.leg_name:
                    rf_dist_bet_items = self.ar.math.create_dist_between(ik_no_stretch_joints[3], ik_extreme_ctrl, name=side+self.number_name+"_"+stretch_names[1]+"_RF_DistBet", keep=True)
                    cmds.delete(rf_dist_bet_items[4])
                    cmds.parent(rf_dist_bet_items[2:4], dist_bet_grp)
                    rf_soft_ik_cnd = cmds.createNode("condition", name=side+self.number_name+"_RF_SoftIk_Cnd")
                    rf_stretchable_cnd = cmds.createNode("condition", name=side+self.number_name+"_RF_Stretchable_Cnd")
                    rf_dist_inv_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_RF_DistInv_MD")
                    self.to_ids.extend([rf_soft_ik_cnd, rf_stretchable_cnd, rf_dist_inv_md])
                    cmds.setAttr(rf_dist_inv_md+".input2X", -1)
                    cmds.setAttr(rf_stretchable_cnd+".colorIfFalseR", 0)
                    cmds.connectAttr(rf_dist_bet_items[1]+".distance", rf_soft_ik_cnd+".colorIfFalseR", force=True)
                    cmds.connectAttr(ik_extreme_ctrl+".softIk", rf_soft_ik_cnd+".firstTerm", force=True)
                    cmds.connectAttr(rf_soft_ik_cnd+".outColorR", rf_dist_inv_md+".input1X", force=True)
                    cmds.connectAttr(rf_dist_inv_md+".outputX", rf_stretchable_cnd+".colorIfTrueR", force=True)
                    cmds.connectAttr(ik_extreme_ctrl+".stretchable", rf_stretchable_cnd+".firstTerm", force=True)
                    cmds.connectAttr(rf_stretchable_cnd+".outColorR", ik_stretch_extreme_loc+".translateZ", force=True)
                    cmds.orientConstraint(soft_ik_orient_loc, ik_stretch_extreme_loc_zero, maintainOffset=False, name=ik_stretch_extreme_loc_zero+"_OrC")
                
                # ikFkSnap
                ik_fk_snap.IkFkSnap(self.ar, side+self.number_name, world_ref, fk_ctrls, [ik_corner_ctrl, ik_extreme_ctrl, ik_extreme_sub_ctrl], ik_joints, [self.ar.data.lang['c018_revFoot_roll'], self.ar.data.lang['c019_revFoot_spin'], self.ar.data.lang['c020_revFoot_turn']], self.ar.data.lang['c040_uniformScale'], dp_dev=self.ar.dev)
                
                # calibration attribute:
                if self.limb_types == self.arm_name:
                    ik_extreme_calibrations = [
                                            self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize(),
                                            "softIk_"+self.ar.data.lang['c111_calibrate']
                    ]
                else: #leg
                    ik_extreme_calibrations = [
                                            self.ar.data.lang['c015_revFoot_F']+self.ar.data.lang['c018_revFoot_roll'].capitalize()+self.ar.data.lang['c102_angle'].capitalize(),
                                            self.ar.data.lang['c015_revFoot_F']+self.ar.data.lang['c018_revFoot_roll'].capitalize()+self.ar.data.lang['c103_plant'].capitalize(),
                                            self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize(),
                                            "softIk_"+self.ar.data.lang['c111_calibrate']
                    ]
                fk_extreme_calibrations = [self.ar.data.lang['c040_uniformScale']+self.ar.data.lang['c105_multiplier'].capitalize()]
                fk_before_calibrations = [self.ar.data.lang['c032_follow']]
                corner_calibrations = ["calibrateRestTX", "calibrateRestTY", "calibrateRestTZ"]
                corner_not_mirrors = [self.ar.data.lang['c053_invert']+"X",
                                        self.ar.data.lang['c053_invert']+"Y",
                                        self.ar.data.lang['c053_invert']+"Z"]
                if quadruped:
                    self.ar.ctrls.set_string_attr_from_items(quad_extra_ctrl, ['autoOrient'])
                self.ar.ctrls.set_string_attr_from_items(ik_extreme_ctrl, ik_extreme_calibrations)
                self.ar.ctrls.set_string_attr_from_items(fk_ctrls[-1], fk_extreme_calibrations)
                self.ar.ctrls.set_string_attr_from_items(fk_ctrls[0], fk_before_calibrations)
                self.ar.ctrls.set_string_attr_from_items(ik_corner_ctrl, corner_calibrations)
                self.ar.ctrls.set_string_attr_from_items(ik_corner_ctrl, corner_not_mirrors, "notMirrorList") #useful to export calibrationIO and not mirror them

                # integrating dics:
                self.extreme_joints.append(skin_joints[-2])
                self.integrate_orig_from_items.append(orig_from_items)
                
                # clean-up before joint, it isn't used to autoClavicle:
                cmds.delete(ik_auto_clavicle_joints[0])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.add_attr_to_items([fk_ctrl_zero_grp, master_ctrl_ref, root_ctrl_ref, shoulder_ref_grp, ik_stretch_extreme_loc, ik_extreme_ctrl_grp, ik_extreme_ctrl_orient_grp, to_rf_ik_handle_grp, self.corner_grp, ik_handle_auto_clavicle_grp, clavicle_ctrl_grp, ac_loc_grp], self.ar.utils.ignore_transform_io_attr)
                self.ar.utils.add_attr_to_items(self.to_rev_foot_ik_handle_grps, self.ar.utils.ignore_transform_io_attr)
                self.to_ids.extend([fk_isolate_rev, up_loc_pac, up_loc_orient_rev, ik_scale_md, fk_scale_md, uni_blend, ik_stretchable_md, ik_stretch_ctrl_cnd, ik_stretch_dif_pma, ik_stretch_cnd, ik_stretch_clp])
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
                            "ikCtrlList": self.ik_extreme_ctrls,
                            "ikCtrlZeroList": self.ik_extreme_ctrl_zeros,
                            "ikPoleVectorZeroList": self.ik_pole_vector_ctrl_zeros,
                            "ikHandleGrpList": self.to_rev_foot_ik_handle_grps,
                            "ikHandleConstList": self.ik_handle_constraints, 
                            "ikHandleGrpConstList": self.ik_handle_grp_constraints, 
                            "ikFkBlendGrpToRevFootList": self.to_rf_blend_grps,
                            "worldRefList": self.world_refs,
                            "worldRefShapeList": self.world_ref_shapes,
                            "limbTypeName": self.limb_types,
                            "extremJntList": self.extreme_joints,
                            "limbStyle": self.get_limb_style(),
                            "quadFrontLegList": self.quad_front_legs,
                            "integrateOrigFromList": self.integrate_orig_from_items,
                            "ikStretchExtremLoc": self.ik_stretch_extreme_locs,
                            "limbManualVolume": self.ar.data.lang['m019_limb'].lower()+"Manual_"+self.ar.data.lang['c031_volumeVariation'],
                            "scalableGrp": self.scalable_grps,
                            "masterCtrlRefList": self.master_ctrl_ref_items,
                            "rootCtrlRefList": self.root_ctrl_ref_items,
                            "softIkCalibrateList": self.soft_ik_calibrate_items,
                            "correctiveCtrlGrpList": self.corrective_ctrl_grps,
                            "addArticJoint": self.articulation,
                            "addCorrective": self.corrective, 
                            "ankleArticList": self.ankle_articulations,
                            "ankleCorrectiveList": self.ankle_correctives
                        }
