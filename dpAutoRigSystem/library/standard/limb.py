from importlib import reload

from maya import cmds
from maya.api import OpenMaya

from ...library.util import ik_fk_snap, ribbon, soft_ik
from ..base import standard

# global variables to this module:
CLASS_NAME = 'Limb'
TITLE = 'm019_limb'
DESCRIPTION = 'm020_limbDesc'
WIKI = '03-‐-Guides#-limb'



class Limb(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.arm_name = 'Arm'
        self.leg_name = 'Leg'
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
        cmds.addAttr(ctrl, longName='followAttrName', dataType='string')
        cmds.setAttr(f"{ctrl}.followAttrName", attr, type='string')


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
                                   ['Before', 'Main', 'Corner', 'CornerB', 'Extrem', 'CornerUpVector', 'JointEnd'])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName='type', attributeType='enum', enumName=f"{self.ar.data.lang['m028_arm']}:{self.ar.data.lang['m030_leg']}")
        cmds.addAttr(self.guide_base, longName='hasBend', defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName='numBendJoints', defaultValue=5, attributeType='long')
        cmds.addAttr(self.guide_base, longName='style', attributeType='enum', enumName=f"{self.ar.data.lang['m042_default']}:{self.ar.data.lang['m026_biped']}:{self.ar.data.lang['m037_quadruped']}")
        cmds.addAttr(self.guide_base, longName='alignWorld', defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName='articulation', defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName='additional', attributeType='bool')
        cmds.addAttr(self.guide_base, longName='softIk', defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName='corrective', attributeType='bool')
        cmds.addAttr(self.guide_base, longName='reorient', attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_before_loc = self.ar.ctrls.create_joint_locator(ctrl_name=f"{self.name_guide}_Before", r=0.3, d=1, guide=True)
        self.guide_main_loc = self.ar.ctrls.create_joint_locator(ctrl_name=f"{self.name_guide}_Main", r=0.5, d=1, guide=True, pin=False)
        self.guide_corner_loc = self.ar.ctrls.create_curve_locator(ctrl_name=f"{self.name_guide}_Corner", r=0.3, d=1, guide=True)
        self.guide_corner_b_loc = self.ar.ctrls.create_curve_locator(ctrl_name=f"{self.name_guide}_CornerB", r=0.5, d=1, guide=True)
        self.guide_extreme_loc = self.ar.ctrls.create_joint_locator(ctrl_name=f"{self.name_guide}_Extrem", r=0.5, d=1, guide=True)
        self.guide_up_vector_loc = self.ar.ctrls.create_curve_locator(ctrl_name=f"{self.name_guide}_CornerUpVector", r=0.5, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=f"{self.name_guide}_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line_before = cmds.joint(name=f"{self.name_guide}_JGuideBefore", radius=0.001)
        self.line_main = cmds.joint(name=f"{self.name_guide}_JGuideMain", radius=0.001)
        self.line_corner = cmds.joint(name=f"{self.name_guide}_JGuideCorner", radius=0.001)
        self.line_extreme = cmds.joint(name=f"{self.name_guide}_JGuideExtrem", radius=0.001)
        self.line_end = cmds.joint(name=f"{self.name_guide}_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_before, self.line_main, self.line_corner, self.line_extreme, self.line_end])
        cmds.setAttr(f"{self.guide_corner_b_loc}.translateZ", 2)
        cmds.setAttr(f"{self.guide_corner_b_loc}.visibility", 0)
        cmds.setAttr(f"{self.guide_end_loc}.translateZ", 1.3)
        # parenting
        self.corner_grp = cmds.group(self.guide_corner_loc, name=f"{self.guide_corner_loc}_Grp")
        cmds.parent(self.line_before, self.guide_before_loc, self.guide_main_loc, self.corner_grp, self.guide_extreme_loc, self.guide_up_vector_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_corner_b_loc, self.guide_corner_loc, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_extreme_loc)
        # edit
        self.ar.ctrls.direct_connect(self.guide_before_loc, self.line_before, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.guide_main_loc, self.line_main, maintainOffset=False, name=f"{self.line_main}_PaC")
        cmds.parentConstraint(self.guide_corner_loc, self.line_corner, maintainOffset=False, name=f"{self.line_corner}_PaC")
        cmds.parentConstraint(self.guide_extreme_loc, self.line_extreme, maintainOffset=False, name=f"{self.line_extreme}_PaC")
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.setAttr(f"{self.guide_extreme_loc}.translateX", lock=True)


    def align_guide_corner(self):
        # align cornerLocs:
        self.corner_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_grp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType='object', worldUpObject=self.guide_up_vector_loc, name=f"{self.corner_grp}_AiC")[0]
        self.corner_point_grp = cmds.group(self.corner_grp, name=f"{self.corner_grp}_Zero_0_Grp")
        poc = cmds.pointConstraint(self.guide_main_loc, self.guide_extreme_loc, self.corner_point_grp, maintainOffset=False, name=f"{self.corner_point_grp}_PoC")[0]
        cmds.setAttr(f"{poc}.{self.guide_main_loc[self.guide_main_loc.rfind(':')+1:]}W0", 0.52)
        cmds.setAttr(f"{poc}.{self.guide_extreme_loc[self.guide_extreme_loc.rfind(':')+1:]}W1", 0.48)
        cmds.setAttr(f"{self.guide_before_loc}.translateX", -0.5)
        cmds.setAttr(f"{self.guide_before_loc}.translateZ", -2)
        cmds.setAttr(f"{self.guide_extreme_loc}.translateZ", 10)
        cmds.setAttr(f"{self.corner_grp}.translateY", -0.75)


    def corner_guide_up_vector(self):
        # editing cornerUpVector:
        self.guide_up_vector_grp = cmds.group(self.guide_up_vector_loc, name=f"{self.guide_up_vector_loc}_Grp")
        corner_position = cmds.xform(self.guide_corner_loc, query=True, worldSpace=True, rotatePivot=True)
        cmds.move(corner_position[0], corner_position[1], corner_position[2], self.guide_up_vector_grp)
        corner_up_vector_poc = cmds.pointConstraint(self.guide_main_loc, self.guide_extreme_loc, self.guide_up_vector_grp, maintainOffset=True, name=f"{self.guide_up_vector_grp}_PoC")[0]
        cmds.setAttr(f"{corner_up_vector_poc}.{self.guide_main_loc[self.guide_main_loc.rfind(':')+1:]}W0", 0.52)
        cmds.setAttr(f"{corner_up_vector_poc}.{self.guide_extreme_loc[self.guide_extreme_loc.rfind(':')+1:]}W1", 0.48)
        cmds.setAttr(f"{self.guide_up_vector_loc}.translateY", -10)
        # display cornerUpVector:
        cmds.addAttr(self.guide_corner_loc, longName='displayUpVector', attributeType='bool')
        cmds.setAttr(f"{self.guide_corner_loc}.displayUpVector", keyable=False, channelBox=True)
        cmds.connectAttr(f"{self.guide_corner_loc}.displayUpVector", f"{self.guide_up_vector_loc}.visibility", force=True)


    def set_lock_corner_attr(self, limb_type, *args):
        """ Set corner guide lock attributes to specific limb type (arm or leg).
        """
        tr_attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        corner_attrs = ['tx', 'ry', 'rz'] #arm
        if limb_type == self.leg_name:
            corner_attrs = ['ty', 'rx', 'rz'] #leg
        for attr in tr_attrs:
            if attr in corner_attrs:
                cmds.setAttr(f"{self.guide_corner_loc}.{attr}", 0, lock=True)
                cmds.setAttr(f"{self.guide_corner_b_loc}.{attr}", 0, lock=True)
            else:
                cmds.setAttr(f"{self.guide_corner_loc}.{attr}", lock=False)
                cmds.setAttr(f"{self.guide_corner_b_loc}.{attr}", lock=False)


    def re_orient_guide(self, *args):
        """ This function reorient guides orientations, creating temporary aimConstraints for them.
        """
        # re-declaring guide names:
        self.guide_before_loc = f"{self.name_guide}_Before"
        self.guide_main_loc = f"{self.name_guide}_Main"
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        self.guide_extreme_loc = f"{self.name_guide}_Extrem"
        self.guide_up_vector_loc = f"{self.name_guide}_CornerUpVector"

        # Adjust offset when it's arm or leg. Using diferent axis for arm or leg.
        before_translate_axis = ".translateX"
        if self.get_limb_type() == self.arm_name:
            before_translate_axis = ".translateY"

        # re-orient clavicle rotations:
        temp_before_up_vector = cmds.group(empty=True, name=f"{self.guide_before_loc}_UpVector_Tmp")
        cmds.matchTransform(temp_before_up_vector, self.guide_before_loc, position=True)
        before_up_vector_translate = cmds.getAttr(f"{temp_before_up_vector}{before_translate_axis}")
        cmds.setAttr(f"{temp_before_up_vector}{before_translate_axis}", before_up_vector_translate+10)
        temp_before_aic = cmds.aimConstraint(self.guide_main_loc, self.guide_before_loc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType='object', worldUpObject=temp_before_up_vector, name=f"{self.guide_before_loc}_Tmp_AiC")[0]
        cmds.delete(temp_before_aic, temp_before_up_vector)
        
        # re-orient main shoulder guide
        temp_main_up_vector = cmds.group(empty=True, parent=self.guide_base, relative=True, name=f"{self.guide_main_loc}_UpVector_Tmp")
        cmds.setAttr(f"{temp_main_up_vector}.translateX", 10)
        temp_main_aic = cmds.aimConstraint(self.guide_corner_loc, self.guide_main_loc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType='object', worldUpObject=temp_main_up_vector, name=f"{self.guide_main_loc}_Tmp_AiC")[0]
        
        # aim offset for aimConstraint depending on limb_type
        self.set_aim_offset(temp_main_aic)
        cmds.delete(temp_main_aic, temp_main_up_vector)


    def prepare_auto_aim_setup(self):
        # create autoAim null groups:
        self.guide_main_drv_null = cmds.group(empty=True, name=f"{self.guide_main_loc}_Drv_Null")
        self.corner_drv_null = cmds.group(empty=True, name=f"{self.guide_corner_loc}_Drv_Null")
        self.corner_drv_null_grp = cmds.group(self.corner_drv_null, name=f"{self.corner_drv_null}_Grp")
        cmds.parent(self.guide_main_drv_null, self.corner_drv_null_grp, self.guide_base)
        cmds.matchTransform(self.guide_main_drv_null, self.guide_main_loc)
        cmds.matchTransform(self.corner_drv_null_grp, self.guide_corner_loc)
        cmds.setAttr(f"{self.guide_main_drv_null}.visibility", 0)
        cmds.setAttr(f"{self.corner_drv_null}.visibility", 0)
        cmds.setAttr(f"{self.corner_drv_null_grp}.visibility", 0)


    def create_guide_auto_aim(self, *args):
        """ AimConstraint setup in order to auto orient mainGuide with CornerGuide
        """ 
        # re-declaring guide names:
        self.guide_main_loc = f"{self.name_guide}_Main"
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        self.guide_extreme_loc = f"{self.name_guide}_Extrem"
        self.guide_up_vector_loc = f"{self.name_guide}_CornerUpVector"
        self.corner_point_grp = f"{self.name_guide}_Corner_Grp_Zero_0_Grp"
        self.guide_main_drv_null = f"{self.name_guide}_Main_Drv_Null"
        self.corner_drv_null = f"{self.name_guide}_Corner_Drv_Null"
        self.corner_drv_null_grp =  f"{self.name_guide}_Corner_Drv_Null_Grp"

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
            cmds.connectAttr(f"{self.guide_main_loc}.translate{axis}", f"{self.guide_main_drv_null}.translate{axis}")
            cmds.connectAttr(f"{self.guide_main_loc}.rotate{axis}", f"{self.guide_main_drv_null}.rotate{axis}")
            cmds.connectAttr(f"{self.guide_corner_loc}.translate{axis}", f"{self.corner_drv_null}.translate{axis}")
            cmds.connectAttr(f"{self.guide_corner_loc}.rotate{axis}", f"{self.corner_drv_null}.rotate{axis}")
        
        # new point constraint from main null grp:
        self.corner_poc = cmds.pointConstraint(self.guide_main_drv_null, self.guide_extreme_loc, self.corner_point_grp, maintainOffset=True, name=f"{self.corner_point_grp}_PoC")[0]
        self.corner_up_vector_poc = cmds.pointConstraint(self.guide_main_drv_null, self.guide_extreme_loc, self.guide_up_vector_grp, maintainOffset=True, name=f"{self.guide_up_vector_grp}_PoC")[0]
        self.corner_null_poc = cmds.pointConstraint(self.guide_main_drv_null, self.guide_extreme_loc, self.corner_drv_null_grp, maintainOffset=True, name=f"{self.corner_drv_null_grp}_PoC")[0]
        self.corner_drv_null_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_drv_null_grp, aimVector=(0.0, 0.0, 1.0), upVector=up_vector_values, worldUpType='object', worldUpObject=self.guide_up_vector_loc, name=f"{self.corner_drv_null_grp}_AiC")

        # setting constraint values, using 0.5 to don't change the previous one which was used to correct placement:
        cmds.setAttr(f"{self.corner_poc}.{self.guide_main_drv_null[self.guide_main_drv_null.rfind(':')+1:]}W0", 0.5)
        cmds.setAttr(f"{self.corner_poc}.{self.guide_extreme_loc[self.guide_extreme_loc.rfind(':')+1:]}W1", 0.5)
        cmds.setAttr(f"{self.corner_up_vector_poc}.{self.guide_main_drv_null[self.guide_main_drv_null.rfind(':')+1:]}W0", 0.5)
        cmds.setAttr(f"{self.corner_up_vector_poc}.{self.guide_extreme_loc[self.guide_extreme_loc.rfind(':')+1:]}W1", 0.5)
        cmds.setAttr(f"{self.corner_null_poc}.{self.guide_main_drv_null[self.guide_main_drv_null.rfind(':')+1:]}W0", 0.5)
        cmds.setAttr(f"{self.corner_null_poc}.{self.guide_extreme_loc[self.guide_extreme_loc.rfind(':')+1:]}W1", 0.5)
        
        # main aimConstraint to the mainLocGrp:
        self.main_aic = cmds.aimConstraint(self.corner_drv_null, self.guide_main_loc_grp, maintainOffset=True, aimVector=(0.0, 0.0, 1.0), upVector=up_vector_values, worldUpType='object', worldUpObject=self.guide_up_vector_loc, name=f"{self.guide_main_loc_grp}_AiC")[0]
        cmds.select(self.guide_base)


    def set_guide_base_initial_position(self):
        cmds.setAttr(f"{self.guide_base}.translateX", 4)
        cmds.setAttr(f"{self.guide_base}.rotateX", 90)
        cmds.setAttr(f"{self.guide_base}.rotateZ", 90)


    def recreate_auto_aim(self):
        """ Need to delete the previous setup in order to autoAim works with different type of limb
        """
        # re-declaring guide names:
        self.guide_main_loc = f"{self.name_guide}_Main"
        self.guide_main_loc_grp = f"{self.name_guide}_Main_Zero_0_Grp"
        self.guide_main_drv_null = f"{self.name_guide}_Main_Drv_Null"
        self.corner_drv_null = f"{self.name_guide}_Corner_Drv_Null"
        self.corner_drv_null_aic = f"{self.name_guide}_Corner_Drv_Null_Grp_AiC"
        self.corner_drv_null_grp = f"{self.name_guide}_Corner_Drv_Null_Grp"
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        self.corner_poc = f"{self.name_guide}_Corner_Grp_Zero_0_Grp_PoC"
        
        # deleting previous constraints:
        cmds.delete(self.corner_poc, self.corner_drv_null_aic, self.corner_poc, self.corner_up_vector_poc, self.corner_null_poc)

        # disconnecting direct connections:
        for axis in self.ar.data.axes:
            cmds.disconnectAttr(f"{self.guide_main_loc}.translate{axis}", f"{self.guide_main_drv_null}.translate{axis}")
            cmds.disconnectAttr(f"{self.guide_main_loc}.rotate{axis}", f"{self.guide_main_drv_null}.rotate{axis}")
            cmds.disconnectAttr(f"{self.guide_corner_loc}.translate{axis}", f"{self.corner_drv_null}.translate{axis}")
            cmds.disconnectAttr(f"{self.guide_corner_loc}.rotate{axis}", f"{self.corner_drv_null}.rotate{axis}")
        
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
        self.guide_main_loc = f"{self.name_guide}_Main"
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        self.guide_extreme_loc = f"{self.name_guide}_Extrem"

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
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        
        # when the limb_type is arm, it will call the cross_product function to get the right offset for X
        if self.get_limb_type() == self.arm_name:
            offset_axis = '.offsetX'
            offset_value = self.cross_product(self.arm_name)
        
        # when the limb_type is arm, it will call the cross_product function to get the right offset for Y:
        elif self.get_limb_type() == self.leg_name:
            offset_axis = '.offsetY'
            offset_value = self.cross_product(self.leg_name)

        # set the aimConstraint's offset according to limb_type:
        cmds.setAttr(f"{aic}{offset_axis}", offset_value)
        

    def run_re_orient_guide(self, *args):
        """ New functions when the button reorient is pressed. For Arm, the extrem will point to the corner. For legs, the extrem will point to the ground.
        """
        # re-declaring guides names:
        self.main_aic = f"{self.name_guide}_Main_Zero_0_Grp_AiC"
        self.guide_before_loc = f"{self.name_guide}_Before"
        self.guide_main_loc = f"{self.name_guide}_Main"
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        self.guide_extreme_loc = f"{self.name_guide}_Extrem"
        self.guide_up_vector_loc = f"{self.name_guide}_CornerUpVector"
        
        # re-orient extremLoc to align with cornerLoc if the clavicle and wrist aren't pinned.
        if not cmds.getAttr(f"{self.guide_extreme_loc}.pinGuide") and not cmds.getAttr(f"{self.guide_before_loc}.pinGuide"):
            # reorient guides first
            self.re_orient_guide()
            # do guide alignment
            if self.get_limb_type() == self.arm_name:
                temp_extreme_children_grp = False
                to_unparent_items = []
                pin_guide_state_data = {}
                cmds.setAttr(f"{self.guide_extreme_loc}.pinGuide", 0)
                extreme_children = cmds.listRelatives(self.guide_extreme_loc, children=True, type='transform')
                if extreme_children:
                    has_sub_guide_base = False
                    for extreme_child in extreme_children:
                        if 'pinGuide' in cmds.listAttr(extreme_child):
                            has_sub_guide_base = True
                    if has_sub_guide_base:
                        temp_extreme_children_grp = cmds.group(empty=True, name='extremChildren_Temp_Grp', parent=self.guide_base)
                        for extreme_child in extreme_children:
                            if 'pinGuide' in cmds.listAttr(extreme_child):
                                to_unparent_items.append(extreme_child)
                                pin_guide_state_data[extreme_child] = cmds.getAttr(f"{extreme_child}.pinGuide")
                                cmds.setAttr(f"{extreme_child}.pinGuide", 0)
                                cmds.parent(extreme_child, temp_extreme_children_grp)
                    temp_up_vector_wrist_grp = cmds.group(empty=True, name='tempUpVectorWrist_Null')
                    cmds.parent(temp_up_vector_wrist_grp, self.guide_base)
                    cmds.matchTransform(temp_up_vector_wrist_grp, self.guide_extreme_loc)
                    cmds.setAttr(f"{temp_up_vector_wrist_grp}.translateX", 2)
                    temp_wrist_aic = cmds.aimConstraint(self.guide_corner_loc, self.guide_extreme_loc, aimVector=(0.0, 0.0, -1.0), upVector=(1.0, 0.0, 0.0), worldUpType='object', worldUpObject=temp_up_vector_wrist_grp, name=f"{self.guide_extreme_loc}_Tmp_AiC")
                    cmds.delete(temp_wrist_aic, temp_up_vector_wrist_grp)
                if to_unparent_items:
                    cmds.parent(to_unparent_items, self.guide_extreme_loc)
                for node, value in pin_guide_state_data.items():
                    cmds.setAttr(f"{node}.pinGuide", value)
                if temp_extreme_children_grp:
                    cmds.delete(temp_extreme_children_grp)

                # adjust offset depends on corner position
                cmds.setAttr(f"{self.guide_main_loc}.rotateX", 0)
                self.set_aim_offset(self.main_aic)
            
            # setup to reorient the ankle guide to point to the ground when rotate mainGuide
            if self.get_limb_type() == self.leg_name:
                temp_ankle_to_aim_null = cmds.group(empty=True, world=True, name='Temp_Ankle_ToAim_Null')
                cmds.matchTransform(temp_ankle_to_aim_null, self.guide_extreme_loc, position=True)
                cmds.setAttr(f"{temp_ankle_to_aim_null}.translateY", -10)
                temp_ankle_to_aic = cmds.aimConstraint(temp_ankle_to_aim_null, self.guide_extreme_loc, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), name=f"{self.guide_extreme_loc}_Tmp_AiC")
                cmds.delete(temp_ankle_to_aic, temp_ankle_to_aim_null)

                # leg offset adjust
                cmds.setAttr(f"{self.guide_main_loc}.rotateY", 0)
                self.set_aim_offset(self.main_aic)
        cmds.select(self.guide_base)


    def change_bend(self, value, *args):
        """ Just set bend values and enable or disable UI elements.
        """
        cmds.setAttr(f"{self.guide_base}.hasBend", value)
        if self.ar.data.ui_state:
            cmds.optionMenu('edit_guide_bend_num_om', edit=True, enable=value)
            cmds.checkBox('edit_guide_additional_cb', edit=True, enable=value)


    def change_bend_number(self, value, *args):
        """ Change the number of joints used in the bend ribbon.
        """
        cmds.setAttr(f"{self.guide_base}.numBendJoints", int(value))


    def change_type(self, type, *args):
        """ This function will modify the names of the rigged module to Arm or Leg options
            and rotate the main in order to be more easy to user edit.
        """
        # re-declaring guide names:
        self.guide_before_loc = f"{self.name_guide}_Before"
        self.guide_main_loc = f"{self.name_guide}_Main"
        self.corner_grp = f"{self.name_guide}_Corner_Grp"
        self.guide_corner_loc = f"{self.name_guide}_Corner"
        self.guide_corner_b_loc = f"{self.name_guide}_CornerB"
        self.guide_extreme_loc = f"{self.name_guide}_Extrem"
        self.guide_end_loc = f"{self.name_guide}_JointEnd"
        self.guide_up_vector_loc = f"{self.name_guide}_CornerUpVector"
        self.corner_aic = f"{self.corner_grp}_AiC"

        self.ar.utils.unlock_attr([self.guide_before_loc, self.guide_main_loc, self.corner_grp, self.guide_corner_loc, self.guide_corner_b_loc, self.guide_extreme_loc, self.guide_end_loc, self.guide_up_vector_loc, self.corner_aic])

        # reset translations:
        translation = ['tx', 'ty', 'tz']
        guide_items = [self.guide_before_loc, self.guide_main_loc, self.corner_grp, self.guide_extreme_loc, self.guide_up_vector_loc]
        for guide_node in guide_items:
            for t_attr in translation:
                cmds.setAttr(f"{guide_node}.{t_attr}", lock=False)
                cmds.setAttr(f"{guide_node}.{t_attr}", 0)

        # for Arm type:
        if type == self.ar.data.lang['m028_arm'] or type == 0:
            cmds.setAttr(f"{self.guide_base}.type", 0)
            cmds.setAttr(f"{self.guide_before_loc}.translateX", -1)
            cmds.setAttr(f"{self.guide_before_loc}.translateZ", -4)
            cmds.setAttr(f"{self.guide_extreme_loc}.translateZ", 10)
            cmds.setAttr(f"{self.guide_extreme_loc}.translateX", lock=True)
            cmds.setAttr(f"{self.corner_grp}.translateY", -0.75)
            cmds.setAttr(f"{self.guide_corner_loc}.translateZ", 0)
            cmds.setAttr(f"{self.guide_end_loc}.translateZ", 1.3)
            cmds.setAttr(f"{self.guide_base}.rotateX", 90)
            cmds.setAttr(f"{self.guide_base}.rotateY", 0)
            cmds.setAttr(f"{self.guide_base}.rotateZ", 90)
            cmds.setAttr(f"{self.guide_up_vector_loc}.translateY", -10)
            cmds.delete(self.corner_aic)
            self.corner_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_grp, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, -1.0, 0.0), worldUpType='object', worldUpObject=self.guide_up_vector_loc, name=f"{self.corner_grp}_AiC")[0]
            self.set_lock_corner_attr(self.arm_name)
            self.recreate_auto_aim()
            
        # for Leg type:
        elif type == self.ar.data.lang['m030_leg'] or type == 1:
            cmds.setAttr(f"{self.guide_base}.type", 1)
            cmds.setAttr(f"{self.guide_before_loc}.translateY", 1)
            cmds.setAttr(f"{self.guide_before_loc}.translateZ", -2)
            cmds.setAttr(f"{self.guide_extreme_loc}.translateZ", 10)
            cmds.setAttr(f"{self.guide_extreme_loc}.translateY", lock=True)
            cmds.setAttr(f"{self.corner_grp}.translateX", 0.75)
            cmds.setAttr(f"{self.guide_corner_loc}.translateZ", 0)
            cmds.setAttr(f"{self.guide_end_loc}.translateZ", 1.3)
            cmds.setAttr(f"{self.guide_base}.rotateX", 0)
            cmds.setAttr(f"{self.guide_base}.rotateY", -90)
            cmds.setAttr(f"{self.guide_base}.rotateZ", 90)
            cmds.setAttr(f"{self.guide_up_vector_loc}.translateX", 10)
            cmds.setAttr(f"{self.guide_up_vector_loc}.translateY", 0.75)
            cmds.delete(self.corner_aic)
            self.corner_aic = cmds.aimConstraint(self.guide_extreme_loc, self.corner_grp, aimVector=(0.0, 0.0, 1.0), upVector=(1.0, 0.0, 0.0), worldUpType='object', worldUpObject=self.guide_up_vector_loc, name=f"{self.corner_grp}_AiC")[0]
            self.set_lock_corner_attr(self.leg_name)
            self.recreate_auto_aim()
    
    
    def get_limb_type(self):
        """ This function will get the limb_type
        """
        enum_type = cmds.getAttr(f"{self.guide_base}.type")
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
        enum_style = cmds.getAttr(f"{self.guide_base}.style")
        if enum_style == 0:
            self.limb_style = self.ar.data.lang['m042_default']
        elif enum_style == 1:
            self.limb_style = self.ar.data.lang['m026_biped']
        elif enum_style == 2:
            self.limb_style = self.ar.data.lang['m037_quadruped']
        elif enum_style == 3:
            self.limb_style = self.ar.data.lang['m043_quadSpring']
        elif enum_style == 4:
            self.limb_style = self.ar.data.lang['m155_quadrupedExtra']
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
                self.ar.naming.set_joint_label(jcr, s+self.joint_label_add, 18, f"{self.number_name}_{number}_{name}_{j}")
                results.append(cmds.rename(jcr, f"{side}{self.number_name}_{number}_{name}_{j}_Jcr")) #renamedJcr
        return results


    def get_calibrate_presets(self, s, is_leg, first, main, corner, knee_b, extrem):
        """ Returns the calibration preset and invert lists for the asked limb joint.
        """
        presets = None
        inverts = None
        if first: #clavicle/hips
            presets = [{}, {'calibrateTX':1.0, 'calibrateTZ':0.5, 'calibrateRY':-30}]
            if s ==  1:
                inverts = [[], ['invertTX', 'invertRY']]
        elif main: #shoulder/leg
            if is_leg:
                presets = [{}, {'calibrateTY':-0.5, 'calibrateTZ':-0.4, 'calibrateRX':30}, {'calibrateTX':1.0, 'calibrateRY':30}]
            else:
                presets = [{}, {'calibrateTY':0.5, 'calibrateTZ':0.2}, {'calibrateTX':1.0, 'calibrateRY':30}]
            if s == 1:
                inverts = [[], [], ['invertTX', 'invertRY']]
        elif corner: #elbow/knee
            presets = [{}, {'calibrateTX':0.1, 'calibrateTZ':-0.6, 'calibrateRY':45}, {'calibrateTX':-0.4, 'calibrateTZ':0.8, 'calibrateRY':-65}, {'calibrateTX':0.3, 'calibrateTZ':0.8, 'calibrateRY':65}]
            if not is_leg:
                inverts = [[], ['invertRY'], [], []]
                if s == 1:
                    if self.get_guide_attr('hasBend'):
                        inverts = [[], ['invertTX', 'invertTZ', 'invertRY'], ['invertTX', 'invertTZ'], ['invertTX', 'invertTZ']]
                    else:
                        inverts = [[], ['invertRY'], [], []]
        elif knee_b: #knee_b
            presets = [{}, {'calibrateTX':0.1, 'calibrateTZ':-0.6, 'calibrateRY':-45}, {'calibrateTX':-0.4, 'calibrateTZ':0.8, 'calibrateRY':-65}, {'calibrateTX':0.3, 'calibrateTZ':0.8, 'calibrateRY':65}]
        elif extrem: #wrist/ankle
            presets = [{}, {'calibrateTX':0.7, 'calibrateRY':-30}, {'calibrateTX':-0.7, 'calibrateRY':30}, {'calibrateTY':0.7, 'calibrateRX':30}, {'calibrateTY':-0.7, 'calibrateRX':-30}]
            if s == 1:
                inverts = [[], ['invertTX', 'invertRY', 'invertRZ'], ['invertTX', 'invertRY', 'invertRZ'], ['invertTX', 'invertRY', 'invertRZ'], ['invertTX', 'invertRY', 'invertRZ']]
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
                style = cmds.getAttr(f"{self.guide_base}.style")
                quadruped = False
                if style == 2:
                    quadruped = True

                # re-declaring guide names:
                self.guide_before_loc = f"{side}{self.number_name}_Guide_Before"
                self.guide_main_loc = f"{side}{self.number_name}_Guide_Main"
                self.guide_corner_loc = f"{side}{self.number_name}_Guide_Corner"
                self.guide_corner_b_loc = f"{side}{self.number_name}_Guide_CornerB"
                self.guide_extreme_loc = f"{side}{self.number_name}_Guide_Extrem"
                self.guide_end_loc = f"{side}{self.number_name}_Guide_JointEnd"
                self.guide_radius = f"{side}{self.number_name}_Guide_Base_RadiusCtrl"

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
                end_suffixes = [f"_{self.ar.data.joint_end_attr}", f"_Ik_{self.ar.data.joint_end_attr}", f"_Fk_{self.ar.data.joint_end_attr}", f"_IkNotStretch_{self.ar.data.joint_end_attr}", f"_IkAC_{self.ar.data.joint_end_attr}"]
                for t, suffix in enumerate(suffixes):
                    wips = []
                    cmds.select(clear=True)
                    for n, joint_name in enumerate(joint_names):
                        wips.append(cmds.joint(name=f"{side}{self.number_name}_{joint_name}{suffix}"))
                    joint_end = cmds.joint(name=f"{side}{self.number_name}{end_suffixes[t]}")
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
                cmds.setAttr(f"{ik_joints[0]}.visibility", 0)
                cmds.setAttr(f"{fk_joints[0]}.visibility", 0)
                cmds.setAttr(f"{ik_no_stretch_joints[0]}.visibility", 0)
                cmds.setAttr(f"{ik_auto_clavicle_joints[1]}.visibility", 0)

                for b, skin_joint in enumerate(skin_joints):
                    if b < len(skin_joints) - 2:
                        cmds.addAttr(skin_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                        self.ar.naming.set_joint_label(skin_joint, s+self.joint_label_add, 18, f"{self.number_name}_{joint_names[b]}")

                # creating Fk controls and a hierarchy group to originedFrom data:
                fk_ctrls, orig_from_items = [], []
                for n, joint_name in enumerate(joint_names):
                    if n == 0:
                        fk_ctrl = self.ar.ctrls.create_controller('id_030_LimbClavicle', f"{side}{self.number_name}_{joint_name}_Ctrl", r=(self.radius * 2), d=self.curve_degree, rot=(45, 0 ,-90), guide_source=f"{self.name_guide}_Before", parent_tag=self.get_parent_to_tag(fk_ctrls))
                    else:
                        fk_ctrl = self.ar.ctrls.create_controller('id_031_LimbFk', f"{side}{self.number_name}_{joint_name}_Fk_Ctrl", r=self.radius, d=self.curve_degree, guide_source=f"{self.name}__{guide_locs[n][len(side):].replace('_Guide', ':Guide')}", parent_tag=self.get_parent_to_tag(fk_ctrls))
                    
                    # Setup axis order
                    if joint_name == before_name:  # Clavicle and hip
                        cmds.setAttr(f"{fk_ctrl}.rotateOrder", 3)
                    elif joint_name == extreme_name and self.limb_types == self.leg_name or joint_name == extreme_name and self.limb_types == self.arm_name:  # Ankle
                        cmds.setAttr(f"{fk_ctrl}.rotateOrder", 4)
                    elif joint_name == main_name:  # Leg and Shoulder
                        cmds.setAttr(f"{fk_ctrl}.rotateOrder", 1)
                    elif self.limb_types == self.leg_name:  # Other legs ctrl
                        cmds.setAttr(f"{fk_ctrl}.rotateOrder", 2)
                    elif self.limb_types == self.arm_name:  # Other arm ctrl
                        cmds.setAttr(f"{fk_ctrl}.rotateOrder", 5)
                    else:
                        # Let the default axis order for other ctrl (Should not happen)
                        pass

                    # Other arm ctrl can keep the default xyz

                    fk_ctrls.append(fk_ctrl)
                    cmds.setAttr(f"{fk_ctrl}.visibility", keyable=False)
                    # creating the originedFrom attributes (in order to permit integrated parents in the future):
                    orig_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_{joint_name}_OrigFrom_Grp")
                    orig_from_items.append(orig_grp)
                    if n == 0: #Clavicle/Hips
                        self.ar.utils.set_origined_from_attr(orig_grp, guide_locs[n][guide_locs[n].find('__')+1:].replace(':', '_'))
                    elif n == 1: #Shoulder/Leg
                        self.ar.utils.set_origined_from_attr(orig_grp, f"{guide_locs[n][guide_locs[n].find('__')+1:].replace(':', '_')};{self.guide_main_loc}")
                    elif n == len(joint_names)-1: #Wrist/Ankle
                        self.ar.utils.set_origined_from_attr(orig_grp, f"{guide_locs[n][guide_locs[n].find('__')+1:].replace(':', '_')};{self.guide_end_loc};{self.guide_radius}")
                    else: #Corner
                        self.ar.utils.set_origined_from_attr(orig_grp, guide_locs[n][guide_locs[n].find('__')+1:].replace(':', '_'))
                        if self.get_guide_attr('hasBend'):
                            to_corner_bend_items.append(guide_locs[n][guide_locs[n].find('__')+1:].replace(':', '_'))
                    cmds.parentConstraint(skin_joints[n], orig_grp, maintainOffset=False, name=f"{orig_grp}_PaC")
                    if n > 1:
                        cmds.parent(fk_ctrl, fk_ctrls[n - 1])
                        cmds.parent(orig_grp, orig_from_items[n - 1])
                    # add wrist_toParent_Ctrl
                    if n == len(joint_names)-1:
                        to_parent_extrem_ctrl = self.ar.ctrls.create_controller('id_032_LimbToParent', ctrl_name=f"{side}{self.number_name}_{extreme_name}_ToParent_Ctrl", r=(self.radius * 0.1), d=self.curve_degree, guide_source=f"{self.name_guide}_Extrem", parent_tag=fk_ctrls[-1])
                        cmds.parent(to_parent_extrem_ctrl, orig_grp)
                        if s == 0:
                            cmds.setAttr(f"{to_parent_extrem_ctrl}.translateX", self.radius)
                        else:
                            cmds.setAttr(f"{to_parent_extrem_ctrl}.translateX", -self.radius)
                        self.ar.utils.create_zero_out([to_parent_extrem_ctrl], not_transform_io=False)
                        self.ar.ctrls.set_lock_hide([to_parent_extrem_ctrl], ['v'])
                # create_zero_out controls:
                fk_ctrl_zeros = self.ar.utils.create_zero_out(fk_ctrls)
                fk_ctrl_zero_grp = cmds.group(fk_ctrl_zeros[0], fk_ctrl_zeros[1], name=f"{side}{self.number_name}_Fk_Ctrl_Grp")
                
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
                        cmds.parentConstraint(fk_ctrls[n], fk_joints[n], maintainOffset=True, name=f"{side}{self.number_name}_{joint_names[n]}_PaC")
                    else:
                        cmds.parentConstraint(fk_ctrls[n], fk_joints[n], maintainOffset=True, name=f"{side}{self.number_name}_{joint_names[n]}_Fk_PaC")
                    if n == 0:
                        clavicle_joints = [skin_joints[0], ik_joints[0], fk_joints[0], ik_no_stretch_joints[0]]
                        for clavicle_joint in clavicle_joints:
                            for axis in self.ar.data.axes:
                                cmds.connectAttr(f"{fk_ctrls[0]}.scale{axis}", f"{clavicle_joint}.scale{axis}", force=True)
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
                world_ref = self.ar.ctrls.create_controller('id_036_LimbWorldRef', f"{side}{self.number_name}_WorldRef_Ctrl", r=self.radius, d=self.curve_degree, dir='+Z', guide_source=f"{self.name_guide}_Base")
                cmds.addAttr(world_ref, longName='ikFkSnap', attributeType='short', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(world_ref, longName=self.ar.data.lang['c113_length'], attributeType='float', defaultValue=1)
                self.world_refs.append(world_ref)
                self.world_ref_shapes.append(cmds.listRelatives(world_ref, children=True, type='nurbsCurve')[0])
                # creating a group reference to follow masterCtrl and rootCtrl:
                master_ctrl_ref = cmds.group(empty=True, name=f"{side}{self.number_name}_MasterCtrlRef_Grp")
                self.master_ctrl_ref_items.append(master_ctrl_ref)
                root_ctrl_ref = cmds.group(empty=True, name=f"{side}{self.number_name}_RootCtrlRef_Grp")
                self.root_ctrl_ref_items.append(root_ctrl_ref)

                # parenting fkControls from 2 hierarchies (before and limb) using constraint, attention to fkIsolated shoulder:
                # creating a shoulder_ref group in order to use it as position relative, joint articulation origin and aim constraint target to quad_extra_ctrl:
                shoulder_ref_grp = cmds.group(empty=True, name=f"{skin_joints[1]}_Ref_Grp")
                # ask if the module is self.arm_name and turn default value to 1 if true.
                isolate_default_value = 0
                if self.limb_types == self.arm_name:
                    isolate_default_value = 1  
                cmds.parent(shoulder_ref_grp, skin_joints[1], relative=True)
                cmds.parent(shoulder_ref_grp, skin_joints[0], relative=False)
                cmds.pointConstraint(shoulder_ref_grp, fk_ctrl_zeros[1], maintainOffset=True, name=f"{fk_ctrl_zeros[1]}_PoC")
                fk_isolate_pac = cmds.parentConstraint(shoulder_ref_grp, master_ctrl_ref, fk_ctrl_zeros[1], skipTranslate=['x', 'y', 'z'], maintainOffset=True, name=f"{fk_ctrl_zeros[1]}_PaC")[0]               
                cmds.addAttr(fk_ctrls[1], longName=self.ar.data.lang['m095_isolate'].lower(), attributeType='float', minValue=0, maxValue=1, defaultValue=isolate_default_value, keyable=True)
                self.add_follow_attr_name(fk_ctrls[1], self.ar.data.lang['m095_isolate'].lower())
                cmds.connectAttr(f"{fk_ctrls[1]}.{self.ar.data.lang['m095_isolate'].lower()}", f"{fk_isolate_pac}.{master_ctrl_ref}W1", force=True)
                fk_isolate_rev = cmds.createNode('reverse', name=f"{side}{self.number_name}_FkIsolate_Rev")
                cmds.connectAttr(f"{fk_ctrls[1]}.{self.ar.data.lang['m095_isolate'].lower()}", f"{fk_isolate_rev}.inputX", force=True)
                cmds.connectAttr(f"{fk_isolate_rev}.outputX", f"{fk_isolate_pac}.{shoulder_ref_grp}W0", force=True) 

                # create orient constrain in order to blend ikFk:
                ik_fk_rev = self.ar.utils.create_joint_blend(ik_joints[1:], fk_joints[1:], skin_joints[1:], 'Fk_ikFkBlend', attr_name_lower, world_ref)

                # organize the ikFkBlend from before to limb:
                cmds.parentConstraint(fk_ctrls[0], ik_joints[0], maintainOffset=True, name=f"{ik_joints[0]}_PaC")
                cmds.parentConstraint(fk_ctrls[0], ik_no_stretch_joints[0], maintainOffset=True, name=f"{ik_no_stretch_joints[0]}_PaC")
                cmds.parentConstraint(fk_ctrls[0], fk_joints[0], maintainOffset=True, name=f"{fk_joints[0]}_PaC")
                cmds.parentConstraint(fk_ctrls[0], skin_joints[0], maintainOffset=True, name=f"{skin_joints[0]}_PaC")

                # creating ik controls:
                ik_extreme_ctrl = self.ar.ctrls.create_controller('id_033_LimbWrist', ctrl_name=f"{side}{self.number_name}_{extreme_name}_Ik_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=f"{self.name_guide}_Extrem")
                ik_extreme_sub_ctrl = self.ar.ctrls.create_controller('id_094_LimbExtremSub', ctrl_name=f"{side}{self.number_name}_{extreme_name}_Ik_Sub_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=f"{self.name_guide}_Extrem", parent_tag=ik_extreme_ctrl)
                cmds.parent(ik_extreme_sub_ctrl, ik_extreme_ctrl)
                self.ar.ctrls.set_lock_hide([ik_extreme_sub_ctrl], ['sx', 'sy', 'sz', 'v'])
                self.ar.ctrls.set_sub_ctrl_display(ik_extreme_ctrl, ik_extreme_sub_ctrl, 0)
                
                # creating orient controller
                if self.limb_types == self.arm_name:
                    cmds.addAttr(ik_extreme_ctrl, longName='orient', attributeType='double', defaultValue=1, min=0, max=1, keyable=True)
                    extreme_orient_ctrl = self.ar.ctrls.create_controller('id_101_LimbExtremOrient', ctrl_name=f"{side}{self.number_name}_{extreme_name}_Orient_Ctrl", r=(self.radius * 0.7), d=self.curve_degree, guide_source=f"{self.name_guide}_Extrem", parent_tag=fk_ctrls[0])
                    cmds.connectAttr(f"{extreme_orient_ctrl}.message", f"{to_parent_extrem_ctrl}.parentTag", force=True)
                    temp_orient_ctrl_cluster = cmds.cluster(extreme_orient_ctrl)[1]
                    if s == 0:
                        cmds.setAttr(f"{temp_orient_ctrl_cluster}.translateZ", 0.2*self.radius)
                    else:
                        cmds.setAttr(f"{temp_orient_ctrl_cluster}.translateZ", -0.2*self.radius)
                    cmds.delete(extreme_orient_ctrl, constructionHistory=True)
                    ik_corner_ctrl = self.ar.ctrls.create_controller('id_034_LimbElbow', ctrl_name=f"{side}{self.number_name}_{corner_name}_Ik_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=f"{self.name_guide}_Corner", parent_tag=fk_ctrls[0])
                    cmds.setAttr(f"{ik_extreme_ctrl}.rotateOrder", 2) #zxy
                    cmds.setAttr(f"{ik_extreme_sub_ctrl}.rotateOrder", 2) #zxy
                    cmds.setAttr(f"{extreme_orient_ctrl}.rotateOrder", 2) #zxy
                    extreme_orient_ctrl_zero = self.ar.utils.create_zero_out([extreme_orient_ctrl])[0]
                    cmds.matchTransform(extreme_orient_ctrl_zero, self.guide_extreme_loc, position=True, rotation=True)
                    self.ar.ctrls.set_lock_hide([extreme_orient_ctrl], ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'])
                    cmds.delete(f"{orig_grp}_PaC")
                    cmds.parentConstraint(extreme_orient_ctrl, orig_grp, maintainOffset=False, name=f"{orig_grp}_PaC")
                else:
                    ik_corner_ctrl = self.ar.ctrls.create_controller('id_035_LimbKnee', ctrl_name=f"{side}{self.number_name}_{corner_name}_Ik_Ctrl", r=(self.radius * 0.5), d=self.curve_degree, guide_source=f"{self.name_guide}_Corner", parent_tag=fk_ctrls[0])
                    cmds.connectAttr(f"{ik_extreme_ctrl}.message", f"{to_parent_extrem_ctrl}.parentTag", force=True)
                    cmds.setAttr(f"{ik_extreme_ctrl}.rotateOrder", 3) #xzy
                    cmds.setAttr(f"{ik_extreme_sub_ctrl}.rotateOrder", 3) #xzy
                self.ik_extreme_ctrls.append(ik_extreme_ctrl)
                self.ar.utils.set_origined_from_attr(ik_corner_ctrl, f"{side}{self.number_name}_Guide_CornerUpVector")
                cmds.connectAttr(f"{ik_corner_ctrl}.message", f"{ik_extreme_ctrl}.parentTag", force=True)

                # getting them create_zero_out groups:
                ik_corner_ctrl_zero = self.ar.utils.create_zero_out([ik_corner_ctrl])[0]
                ik_extreme_ctrl_zero = self.ar.utils.create_zero_out([ik_extreme_ctrl])[0]
                self.ik_extreme_ctrl_zeros.append(ik_extreme_ctrl_zero)
                # putting ikCtrls in the correct position and orientation:
                cmds.matchTransform(ik_extreme_ctrl_zero, self.guide_extreme_loc, position=True, rotation=True)

                # fix stretch calcule to work with reverseFoot
                ik_stretch_extreme_loc = cmds.group(empty=True, name=f"{side}{self.number_name}_{extreme_name}_Ik_Loc_Grp")
                if quadruped:
                    cmds.matchTransform(ik_stretch_extreme_loc, skin_joints[3], position=True, rotation=True) #snap to knee_b
                else:    
                    cmds.matchTransform(ik_stretch_extreme_loc, self.guide_extreme_loc, position=True, rotation=True)
                
                # fixing ikControl group to get a good mirror orientation more animator friendly:
                ik_extreme_ctrl_grp = cmds.group(ik_extreme_ctrl, name=f"{side}{self.number_name}_{extreme_name}_Ik_Ctrl_Grp")
                ik_extreme_ctrl_orient_grp = cmds.group(ik_extreme_ctrl_grp, name=f"{side}{self.number_name}_{extreme_name}_Ik_Ctrl_Orient_Grp")
                # adjust rotate orders:
                cmds.setAttr(f"{ik_extreme_ctrl_grp}.rotateOrder", cmds.getAttr(f"{ik_extreme_ctrl}.rotateOrder"))
                cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateOrder", cmds.getAttr(f"{ik_extreme_ctrl}.rotateOrder"))

                # orient ik controls properly:
                if s == 0 or self.limb_types == self.arm_name:
                    cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateX", -90)
                    cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateZ", -90)

                # verify if user wants to apply the good mirror orientation:
                if s == 1 and style != 0 and self.mirror_axis != 'off': #default
                    # these options is valides for Biped, Quadruped, Quadruped Spring and Quadruped Extra
                    for axis in self.mirror_axis:
                        if axis == 'X':
                            if self.limb_types == self.arm_name:
                                cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateX", -90)
                                cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateY", 90)
                                if self.get_guide_attr('alignWorld'):
                                    cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.scaleX", -1)
                                else:
                                    cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.scaleZ", -1)
                            else: #leg
                                cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateX", 90)
                                cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotateZ", -90)
                                cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.scaleX", -1)
                
                # to fix quadruped stretch locator after rotated ik extrem controller:
                ik_stretch_extreme_loc_zero = self.ar.utils.create_zero_out([ik_stretch_extreme_loc])[0]
                cmds.parent(ik_stretch_extreme_loc_zero, ik_extreme_sub_ctrl, absolute=True)
                expose_corner_name = f"{corner_name}_Jnt"
                if self.get_guide_attr('hasBend'):
                    expose_corner_name = f"{corner_name}_Jxt"
                if quadruped:
                    self.ik_stretch_extreme_locs.append(None)
                    expose_corner_name = f"{corner_b_name}_Jnt"
                    if self.get_guide_attr('hasBend'):
                        expose_corner_name = f"{corner_b_name}_Jxt"
                else:
                    self.ik_stretch_extreme_locs.append(ik_stretch_extreme_loc_zero)
                
                # connecting visibilities:
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{fk_ctrl_zeros[1]}.visibility", force=True)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{ik_corner_ctrl_zero}.visibility", force=True)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{ik_extreme_ctrl_zero}.visibility", force=True)
                self.ar.ctrls.set_lock_hide([ik_corner_ctrl], ['v'], l=False)
                self.ar.ctrls.set_lock_hide([ik_extreme_ctrl], ['sx', 'sy', 'sz', 'v'])

                # creating ikHandles:
                # verify the limb style:
                if quadruped:
                    # creating double ikHandle in order to get an extra control for lower articulation in Quadruped Extra Control:
                    ik_handle_main_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_IKH", startJoint=ik_joints[1], endEffector=ik_joints[len(ik_joints) - 3], solver='ikRPsolver')
                    ik_handle_not_stretch_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_NotStretch_IKH", startJoint=ik_no_stretch_joints[1], endEffector=ik_no_stretch_joints[len(ik_no_stretch_joints) - 2], solver='ikRPsolver')
                    ik_handle_auto_clavicle_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_AC_IKH", startJoint=ik_auto_clavicle_joints[1], endEffector=ik_auto_clavicle_joints[len(ik_auto_clavicle_joints) - 2], solver='ikRPsolver')
                    ik_handle_extra_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_Extra_IKH", startJoint=ik_joints[len(ik_joints) - 3], endEffector=ik_joints[len(ik_joints) - 2], solver='ikRPsolver')
                else: #default, biped
                    # using regular solution as ikRPSolver:
                    ik_handle_main_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_IKH", startJoint=ik_joints[1], endEffector=ik_joints[len(ik_joints) - 2], solver='ikRPsolver')
                    ik_handle_not_stretch_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_NotStretch_IKH", startJoint=ik_no_stretch_joints[1], endEffector=ik_no_stretch_joints[len(ik_no_stretch_joints) - 2], solver='ikRPsolver')
                    ik_handle_auto_clavicle_items = cmds.ikHandle(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_AC_IKH", startJoint=ik_auto_clavicle_joints[1], endEffector=ik_auto_clavicle_joints[len(ik_auto_clavicle_joints) - 2], solver='ikRPsolver')

                # renaming effectors:
                cmds.rename(ik_handle_main_items[1], f"{side}{self.number_name}_{self.limb_type.capitalize()}_Eff")
                cmds.rename(ik_handle_not_stretch_items[1], f"{side}{self.number_name}_{self.limb_type.capitalize()}_NotStretch_Eff")
                cmds.rename(ik_handle_auto_clavicle_items[1], f"{side}{self.number_name}_{self.limb_type.capitalize()}_AC_Eff")

                # creating ikHandle groups:
                cmds.setAttr(f"{ik_handle_main_items[0]}.visibility", 0)
                ik_handle_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_IKH_Grp")
                to_rf_ik_handle_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_IKHToRF_Grp")
                self.to_rev_foot_ik_handle_grps.append(ik_handle_grp)
                cmds.setAttr(f"{to_rf_ik_handle_grp}.visibility", 0)
                cmds.parent(to_rf_ik_handle_grp, ik_handle_grp)
                self.ik_handle_grp_constraints.append(cmds.parentConstraint(ik_extreme_ctrl, ik_handle_grp, maintainOffset=True, name=f"{ik_handle_grp}_PaC"))
                # for ikHandle not stretch group:
                ik_handle_not_stretch_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_NotStretch_IKH_Grp")
                cmds.setAttr(f"{ik_handle_not_stretch_grp}.visibility", 0)
                cmds.parent(ik_handle_not_stretch_items[0], ik_handle_not_stretch_grp)
                # for ikHandle auto clavicle group:
                ik_handle_auto_clavicle_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_AC_IKH_Grp")
                cmds.setAttr(f"{ik_handle_auto_clavicle_grp}.visibility", 0)
                cmds.parent(ik_handle_auto_clavicle_items[0], ik_handle_auto_clavicle_grp)

                # setup quadruped extra control:
                if quadruped:
                    cmds.rename(ik_handle_extra_items[1], f"{side}{self.number_name}_{self.limb_type.capitalize()}_Extra_Eff")
                    quad_extra_ctrl = self.ar.ctrls.create_controller('id_058_LimbQuadExtra', ctrl_name=f"{side}{self.number_name}_{extreme_name}_Ik_Extra_Ctrl", r=(self.radius * 0.7), d=self.curve_degree, dir='-Z', guide_source=f"{self.name_guide}_Extrem", parent_tag=ik_extreme_ctrl)
                    if s == 1:
                        cmds.setAttr(f"{quad_extra_ctrl}.rotateY", 180)
                        cmds.makeIdentity(quad_extra_ctrl, rotate=True, apply=True)
                    quad_extra_ctrl_zero = self.ar.utils.create_zero_out([quad_extra_ctrl])[0]
                    cmds.matchTransform(quad_extra_ctrl_zero, ik_extreme_ctrl, position=True, rotation=True)
                    cmds.parent(quad_extra_ctrl_zero, ik_handle_grp)
                    cmds.parent(ik_handle_extra_items[0], to_rf_ik_handle_grp)
                    cmds.setAttr(f"{ik_handle_extra_items[0]}.visibility", 0)
                    cmds.addAttr(quad_extra_ctrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(f"{quad_extra_ctrl}.twist", f"{ik_handle_extra_items[0]}.twist", force=True)
                    cmds.connectAttr(f"{ik_fk_rev}.outputX", f"{quad_extra_ctrl_zero}.visibility", force=True)
                    self.ar.ctrls.set_lock_hide([quad_extra_ctrl], ['sx', 'sy', 'sz', 'v'])
                
                # working with world axis orientation for limb extrem ik controls
                if self.get_guide_attr('alignWorld'):
                    original_rotate_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_{extreme_name}_OriginalRotate_MD")
                    align_world_rev = cmds.createNode('reverse', name=f"{side}{self.number_name}_{extreme_name}_AlighWorld_Rev")
                    self.to_ids.extend([original_rotate_md, align_world_rev])
                    cmds.addAttr(ik_extreme_ctrl, longName='alignWorld', attributeType='float', defaultValue=0, minValue=0, maxValue=1, keyable=True)
                    cmds.connectAttr(f"{ik_extreme_ctrl}.alignWorld", f"{align_world_rev}.inputX", force=True)
                    if s == 0:
                        original_rotation = self.get_original_rotation(ik_extreme_ctrl)
                    elif style == 0 and self.limb_types == self.arm_name: #default
                        # get right side to alignWorld. It'll be a little glitch, but it seems be accordilly with the mirror using arm default setting. Recommended use biped limb_style instead.
                        original_rotation = self.get_original_rotation(ik_extreme_ctrl)
                    for a, axis in enumerate(self.ar.data.axes):
                        cmds.setAttr(f"{ik_extreme_ctrl_orient_grp}.rotate{axis}", 0)
                        cmds.setAttr(f"{ik_extreme_ctrl_zero}.rotate{axis}", 0)
                        # store original rotation values for initial default pose
                        cmds.addAttr(ik_extreme_ctrl, longName=f"originalRotate{axis}", attributeType='float', keyable=True)
                        cmds.setAttr(f"{ik_extreme_ctrl}.originalRotate{axis}", original_rotation[a], lock=True)
                        cmds.connectAttr(f"{ik_extreme_ctrl}.originalRotate{axis}", f"{original_rotate_md}.input1{axis}", force=True)
                        cmds.connectAttr(f"{align_world_rev}.outputX", f"{original_rotate_md}.input2{axis}", force=True)
                        cmds.connectAttr(f"{original_rotate_md}.output{axis}", f"{ik_extreme_ctrl_grp}.rotate{axis}", force=True)

                # make ikControls lead ikHandles:
                ik_handle_extra_grp = cmds.group(empty=True, name=f"{ik_handle_main_items[0]}_Grp")
                cmds.matchTransform(ik_handle_extra_grp, ik_handle_main_items[0], position=True, rotation=True)
                cmds.parent(ik_handle_main_items[0], ik_handle_extra_grp)
                cmds.parent(ik_handle_extra_grp, to_rf_ik_handle_grp)
                if quadruped:
                    cmds.parent(ik_handle_extra_grp, ik_stretch_extreme_loc_zero, quad_extra_ctrl)
                ik_handle_poc = cmds.pointConstraint(ik_extreme_sub_ctrl, ik_handle_extra_grp, maintainOffset=True, name=f"{ik_handle_grp}_PoC")[0]
                self.ik_handle_constraints.append(ik_handle_poc)
                
                cmds.orientConstraint(ik_extreme_sub_ctrl, ik_joints[len(ik_joints) - 2], maintainOffset=True, name=f"{ik_joints[len(ik_joints) - 2]}_OrC")
                cmds.pointConstraint(ik_extreme_sub_ctrl, ik_handle_not_stretch_items[0], maintainOffset=True, name=f"{ik_handle_not_stretch_items[0]}_PoC")[0]
                cmds.pointConstraint(ik_extreme_sub_ctrl, ik_handle_auto_clavicle_items[0], maintainOffset=True, name=f"{ik_handle_auto_clavicle_items[0]}_PoC")[0]
                cmds.orientConstraint(ik_extreme_sub_ctrl, ik_no_stretch_joints[len(ik_no_stretch_joints) - 2], maintainOffset=True, name=f"{ik_no_stretch_joints[len(ik_no_stretch_joints) - 2]}_OrC")

                # twist:
                cmds.addAttr(ik_extreme_ctrl, longName='twist', attributeType='float', keyable=True)
                if s == 0:
                    cmds.connectAttr(f"{ik_extreme_ctrl}.twist", f"{ik_handle_main_items[0]}.twist", force=True)
                    cmds.connectAttr(f"{ik_extreme_ctrl}.twist", f"{ik_handle_not_stretch_items[0]}.twist", force=True)
                    cmds.connectAttr(f"{ik_extreme_ctrl}.twist", f"{ik_handle_auto_clavicle_items[0]}.twist", force=True)
                else:
                    twist_md = cmds.createNode('multiplyDivide', name=f"{ik_extreme_ctrl}_MD")
                    self.to_ids.append(twist_md)
                    cmds.setAttr(f"{twist_md}.input2X", -1)
                    cmds.connectAttr(f"{ik_extreme_ctrl}.twist", f"{twist_md}.input1X", force=True)
                    cmds.connectAttr(f"{twist_md}.outputX", f"{ik_handle_main_items[0]}.twist", force=True)
                    cmds.connectAttr(f"{twist_md}.outputX", f"{ik_handle_not_stretch_items[0]}.twist", force=True)
                    cmds.connectAttr(f"{twist_md}.outputX", f"{ik_handle_auto_clavicle_items[0]}.twist", force=True)

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
                pv_pos_x = pv_base_pos_x + pv_dist_x
                pv_pos_y = pv_base_pos_y + pv_dist_y
                pv_pos_z = pv_base_pos_z + pv_dist_z
                # place poleVector zero out group in the correct position
                cmds.move(pv_pos_x, pv_pos_y, pv_pos_z, ik_corner_ctrl_zero, objectSpace=False, worldSpaceDistance=True)

                # create poleVector constraint:
                cmds.poleVectorConstraint(ik_corner_ctrl, ik_handle_main_items[0], weight=1.0, name=f"{ik_handle_main_items[0]}_PVC")
                cmds.poleVectorConstraint(ik_corner_ctrl, ik_handle_not_stretch_items[0], weight=1.0, name=f"{ik_handle_not_stretch_items[0]}_PVC")
                cmds.poleVectorConstraint(ik_corner_ctrl, ik_handle_auto_clavicle_items[0], weight=1.0, name=f"{ik_handle_auto_clavicle_items[0]}_PVC")

                # create annotation:
                annot_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_Ant_Loc", position=(0, 0, 0))[0]
                annotation = cmds.annotate(annot_loc, tx="", point=(pv_pos_x, pv_pos_y, pv_pos_z))
                annotation = cmds.listRelatives(annotation, parent=True)[0]
                annotation = cmds.rename(annotation, f"{side}{self.number_name}_{self.limb_type.capitalize()}_Ant")
                cmds.parent(annotation, ik_corner_ctrl)
                cmds.parent(annot_loc, ik_joints[2], relative=True)
                cmds.setAttr(f"{annotation}.template", 1)
                cmds.setAttr(f"{annot_loc}.visibility", 0)
                # set annotation visibility as a display option attribute:
                cmds.addAttr(ik_corner_ctrl, longName='displayAnnotation', attributeType='short', minValue=0, maxValue=1, keyable=False, defaultValue=1)
                cmds.setAttr(f"{ik_corner_ctrl}.displayAnnotation", channelBox=True)
                cmds.connectAttr(f"{ik_corner_ctrl}.displayAnnotation", f"{annotation}.visibility", force=True)

                # prepare groups to rotate and translate automatically:
                self.ar.ctrls.set_lock_hide([ik_corner_ctrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
                self.corner_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_{self.limb_type.capitalize()}_PoleVector_Grp", absolute=True)
                cmds.matchTransform(self.corner_grp, ik_extreme_ctrl, position=True, rotation=True)
                cmds.parent(ik_corner_ctrl_zero, self.corner_grp, absolute=True)
                # set a good orientation for the poleVector ctrl
                cmds.setAttr(f"{ik_corner_ctrl_zero}.rotateX", 0)
                cmds.setAttr(f"{ik_corner_ctrl_zero}.rotateY", 0)
                cmds.setAttr(f"{ik_corner_ctrl_zero}.rotateZ", 0)
                if s == 1:
                    cmds.setAttr(f"{ik_corner_ctrl_zero}.scaleX", -1)
                    cmds.setAttr(f"{ik_corner_ctrl_zero}.scaleY", -1)
                    cmds.setAttr(f"{ik_corner_ctrl_zero}.scaleZ", -1)
                corner_grp_zero = self.ar.utils.create_zero_out([self.corner_grp])[0]
                self.ik_pole_vector_ctrl_zeros.append(corner_grp_zero)

                # working with follow behavior of the poleVector:
                pv_aim_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_{corner_name}_Ik_Aim_Loc")[0]
                pv_up_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_{corner_name}_Ik_Up_Loc")[0]
                pv_up_loc_grp = cmds.group(pv_up_loc, name=f"{pv_up_loc}_Grp")
                pole_vector_loc_grp = cmds.group(pv_aim_loc, pv_up_loc_grp, name=f"{side}{self.number_name}_{corner_name}_Ik_Loc_Grp")
                cmds.setAttr(f"{pole_vector_loc_grp}.visibility", 0)
                cmds.setAttr(f"{pv_up_loc}.translateZ", self.radius)
                if pv_pos_z < 0:
                    cmds.setAttr(f"{pv_up_loc}.translateZ", -self.radius)
                cmds.delete(cmds.pointConstraint(self.guide_main_loc, pv_aim_loc, maintainOffset=False))
                cmds.pointConstraint(ik_extreme_sub_ctrl, pv_up_loc_grp, maintainOffset=False, name=f"{pv_up_loc_grp}_PoC")
                for axis in self.ar.data.axes:
                    cmds.connectAttr(f"{world_ref}.scaleX", f"{pole_vector_loc_grp}.scale{axis}", force=True)
                
                # working with autoOrient of poleVector:
                cmds.addAttr(ik_corner_ctrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                if self.limb_types == self.arm_name:
                    cmds.setAttr(f"{ik_corner_ctrl}.{self.ar.data.lang['c033_autoOrient']}", 0)
                    cmds.addAttr(f"{ik_corner_ctrl}.{self.ar.data.lang['c033_autoOrient']}", edit=True, defaultValue=0)
                up_loc_pac = cmds.parentConstraint(ik_extreme_ctrl, root_ctrl_ref, pv_up_loc_grp, skipTranslate=['x', 'y', 'z'], maintainOffset=True, name=f"{pv_up_loc_grp}_PaC")[0]
                cmds.setAttr(f"{up_loc_pac}.interpType", 2) #shortest
                up_loc_orient_rev = cmds.createNode('reverse', name=f"{side}{self.number_name}_UpLocOrient_Rev")
                cmds.connectAttr(f"{ik_corner_ctrl}.{self.ar.data.lang['c033_autoOrient']}", f"{up_loc_orient_rev}.inputX", force=True)
                cmds.connectAttr(f"{ik_corner_ctrl}.{self.ar.data.lang['c033_autoOrient']}", f"{up_loc_pac}.{ik_extreme_ctrl}W0", force=True)
                cmds.connectAttr(f"{up_loc_orient_rev}.outputX", f"{up_loc_pac}.{root_ctrl_ref}W1", force=True)
                cmds.aimConstraint(ik_extreme_sub_ctrl, pv_aim_loc, worldUpType='object', worldUpObject=pv_up_loc, aimVector=(0, 0, 1), upVector=(1, 0, 0), maintainOffset=False, name=f"{pv_up_loc}_AiC")
                cmds.parentConstraint(pv_aim_loc, self.corner_grp, maintainOffset=True, name=f"{self.corner_grp}_PaC")

                # make poleVectorCtrl's follow really pin from masterCtrl:
                cmds.addAttr(ik_corner_ctrl, longName='pin', attributeType='short', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                pv_pin_pac = cmds.parentConstraint(master_ctrl_ref, ik_corner_ctrl_zero, maintainOffset=True, name=f"{ik_corner_ctrl_zero}_PaC")[0]
                cmds.connectAttr(f"{ik_corner_ctrl}.pin", f"{pv_pin_pac}.{master_ctrl_ref}W0", force=True)

                # poleVector rest calibration setup:
                corner_invert_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_{corner_name}_Invert_MD")
                self.to_ids.append(corner_invert_md)
                if s == 0:
                    rest_items = []
                for r, rest_axis in enumerate(self.ar.data.axes):
                    cmds.addAttr(ik_corner_ctrl, longName=f"{self.ar.data.lang['c053_invert']}{rest_axis}", attributeType='bool', defaultValue=s)
                for r, rest_axis in enumerate(self.ar.data.axes):
                    corner_invert_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_{corner_name}_Invert{rest_axis}_Cnd")
                    self.to_ids.append(corner_invert_cnd)
                    cmds.setAttr(f"{corner_invert_cnd}.colorIfTrueR", 1)
                    cmds.setAttr(f"{corner_invert_cnd}.colorIfFalseR", -1)
                    if s == 0:
                        rest_items.append(cmds.getAttr(f"{pv_pin_pac}.restTranslate{rest_axis}"))
                    cmds.addAttr(ik_corner_ctrl, longName=f"calibrateRestT{rest_axis}", attributeType='float', defaultValue=rest_items[r], keyable=False)
                    cmds.connectAttr(f"{corner_invert_md}.output{rest_axis}", f"{pv_pin_pac}.restTranslate{rest_axis}", force=True)
                    cmds.connectAttr(f"{ik_corner_ctrl}.{self.ar.data.lang['c053_invert']}{rest_axis}", f"{corner_invert_cnd}.firstTerm", force=True)
                    cmds.connectAttr(f"{corner_invert_cnd}.outColorR", f"{corner_invert_md}.input2{rest_axis}", force=True)
                    cmds.connectAttr(f"{ik_corner_ctrl}.calibrateRestT{rest_axis}", f"{corner_invert_md}.input1{rest_axis}", force=True)
                    
                # quadExtraCtrl autoOrient setup:
                if quadruped:
                    cmds.addAttr(quad_extra_ctrl, longName='autoOrient', attributeType='float', minValue=0, max=1, defaultValue=1, keyable=True)
                    cmds.setAttr(f"{quad_extra_ctrl}.autoOrient", 0)
                    quad_extra_rot_null = cmds.group(name=f"{quad_extra_ctrl}_AutoOrient_Null", empty=True)
                    self.ar.utils.add_attr_to_items([quad_extra_rot_null], self.ar.utils.ignore_transform_io_attr)
                    cmds.matchTransform(quad_extra_rot_null, quad_extra_ctrl, position=True, rotation=True)
                    cmds.parent(quad_extra_rot_null, to_rf_ik_handle_grp)
                    auto_orient_rev = cmds.createNode('reverse', name=f"{quad_extra_ctrl}_AutoOrient_Rev")
                    self.to_ids.append(auto_orient_rev)
                    auto_orient_pac = cmds.parentConstraint(to_rf_ik_handle_grp, quad_extra_rot_null, quad_extra_ctrl_zero, skipTranslate=['x', 'y', 'z'], maintainOffset=True, name=f"{quad_extra_ctrl_zero}_PaC")[0]
                    cmds.setAttr(f"{auto_orient_pac}.interpType", 0) #noflip
                    cmds.connectAttr(f"{quad_extra_ctrl}.autoOrient", f"{auto_orient_rev}.inputX", force=True)
                    cmds.connectAttr(f"{auto_orient_rev}.outputX", f"{auto_orient_pac}.{to_rf_ik_handle_grp}W0", force=True)
                    cmds.connectAttr(f"{quad_extra_ctrl}.autoOrient", f"{auto_orient_pac}.{quad_extra_rot_null}W1", force=True)
                    # avoid cycle error from Maya warning:
                    cmds.cycleCheck(evaluation=False)
                    cmds.aimConstraint(shoulder_ref_grp, quad_extra_rot_null, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=ik_corner_ctrl, name=f"{quad_extra_ctrl_zero}_AiC")[0]
                    cmds.cycleCheck(evaluation=True)
                    # hack to parent constraint offset recalculation (Update button on Attribute Editor):
                    cmds.parentConstraint(to_rf_ik_handle_grp, quad_extra_rot_null, quad_extra_ctrl_zero, edit=True, maintainOffset=True)
                    cmds.setAttr(f"{quad_extra_ctrl}.autoOrient", 1)
                    # another hack to avoid uniformScale flip issue
                    cmds.scaleConstraint(ik_extreme_ctrl, quad_extra_ctrl_zero, maintainOffset=True, name=f"{quad_extra_ctrl_zero}_ScC")

                # stretch system:
                stretch_names = [before_name, self.limb_type.capitalize()]
                dist_bet_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_DistBet_Grp")
                joint_chain_lenght_value = self.ar.utils.joint_chain_length(ik_joints[1:4])

                # creating attributes:
                cmds.addAttr(ik_extreme_ctrl, longName='startChainLength', attributeType='float', defaultValue=joint_chain_lenght_value, keyable=False)
                cmds.addAttr(ik_extreme_ctrl, longName='stretchable', attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=True)
                cmds.addAttr(ik_extreme_ctrl, longName=self.ar.data.lang['c113_length'], attributeType='float', minValue=0.001, defaultValue=1, keyable=True)
                self.ar.ctrls.set_lock_hide([ik_extreme_ctrl], ['startChainLength'])

                # creating distance betweens, multiplyDivides and reverse nodes:
                dist_between_items = self.ar.math.create_dist_between(ik_joints[1], ik_stretch_extreme_loc, name=f"{side}{self.number_name}_{stretch_names[1]}_DistBet", keep=True)
                cmds.setAttr(f"{dist_between_items[5]}.{dist_between_items[4]}W1", 0)
                cmds.parent(dist_between_items[2], dist_between_items[3], dist_between_items[4], dist_bet_grp)
                cmds.connectAttr(f"{ik_extreme_ctrl}.{self.ar.data.lang['c113_length']}", f"{world_ref}.{self.ar.data.lang['c113_length']}", force=True)
                cmds.parentConstraint(skin_joints[0], dist_between_items[4], maintainOffset=True, name=f"{dist_between_items[4]}_PaC")
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{dist_between_items[5]}.{ik_stretch_extreme_loc}W0", force=True)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{dist_between_items[5]}.{dist_between_items[4]}W1", force=True)

                # (James) if we use the ribbon controls we won't implement the forearm control
                # create the forearm control if limb type is arm and there is not bend (ribbon) implementation:
                if self.limb_types == self.arm_name and self.get_guide_attr('hasBend') == False:
                    # create forearm joint:
                    forearm_joint = cmds.duplicate(skin_joints[2], name=f"{side}{self.number_name}_{self.ar.data.lang['c030_forearm']}{suffixes[0]}")[0]
                    self.ar.naming.set_joint_label(forearm_joint, s+self.joint_label_add, 18, f"{self.number_name}_{self.ar.data.lang['c030_forearm']}")
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
                    forearm_ctrl = self.ar.ctrls.create_controller('id_037_LimbForearm', f"{side}{self.number_name}_{self.ar.data.lang['c030_forearm']}_Ctrl", r=(self.radius * 0.75), d=self.curve_degree, guide_source=f"{self.name_guide}_Corner", parent_tag=ik_corner_ctrl)
                    forearm_grp = cmds.group(forearm_ctrl, name=f"{side}{self.number_name}_{self.ar.data.lang['c030_forearm']}_Grp")
                    forearm_zero = cmds.group(forearm_grp, name=f"{side}{self.number_name}_{self.ar.data.lang['c030_forearm']}_Zero_0_Grp")
                    cmds.matchTransform(forearm_zero, forearm_joint, position=True, rotation=True)
                    cmds.parentConstraint(skin_joints[2], forearm_zero, maintainOffset=True, name=f"{forearm_zero}_PaC")
                    cmds.orientConstraint(forearm_ctrl, forearm_joint, skip=['x', 'y'], maintainOffset=True, name=f"{forearm_joint}_OrC")
                    # create attribute to forearm autoRotate:
                    cmds.addAttr(forearm_ctrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.75, keyable=True)
                    self.ar.ctrls.set_lock_hide([forearm_ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                    # make rotate connections:
                    forearm_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_{self.ar.data.lang[ 'c030_forearm']}_MD")
                    self.to_ids.append(forearm_md)
                    cmds.connectAttr(f"{forearm_ctrl}.{self.ar.data.lang['c033_autoOrient']}", f"{forearm_md}.input1X")
                    cmds.connectAttr(f"{skin_joints[3]}.rotateZ", f"{forearm_md}.input2X")
                    cmds.connectAttr(f"{forearm_md}.outputX", f"{forearm_grp}.rotateZ")
                    ik_extreme_orient_pac = cmds.parentConstraint(forearm_ctrl, ik_extreme_sub_ctrl, fk_joints[-2], extreme_orient_ctrl_zero, skipTranslate=['x', 'y', 'z'], maintainOffset=True, name=f"{extreme_orient_ctrl_zero}_PaC")[0]
                    ik_extreme_orient_pac_w0 = f"{forearm_ctrl}W0"
                    cmds.pointConstraint(skin_joints[-2], extreme_orient_ctrl_zero, maintainOffset=True, name=f"{extreme_orient_ctrl_zero}_PoC")

                # creating a group to receive the reverseFootCtrlGrp (if module integration is on):
                to_rf_blend_grp = cmds.group(empty=True, name=f"{side}{self.number_name}_IkFkBlendGrpToRevFoot_Grp")
                self.to_rf_blend_grps.append(to_rf_blend_grp)
                cmds.matchTransform(to_rf_blend_grp, ik_extreme_ctrl, position=True, rotation=True)

                # offset parent constraint
                to_rf_offset_pac = cmds.parentConstraint(ik_extreme_sub_ctrl, fk_ctrls[len(fk_ctrls) - 1], ik_no_stretch_joints[-2], to_rf_blend_grp, maintainOffset=True, name=f"{to_rf_blend_grp}_PaC")[0]
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{to_rf_offset_pac}.{fk_ctrls[len(fk_ctrls) - 1]}W1", force=True)

                # work with scalable extrem hand or foot:
                cmds.addAttr(fk_ctrls[-1], longName=self.ar.data.lang['c040_uniformScale'], attributeType='double', minValue=0.001, defaultValue=1)
                cmds.addAttr(ik_extreme_ctrl, longName=self.ar.data.lang['c040_uniformScale'], attributeType='double', minValue=0.001, defaultValue=1)
                cmds.setAttr(f"{fk_ctrls[-1]}.{self.ar.data.lang['c040_uniformScale']}", edit=True, keyable=True)
                cmds.setAttr(f"{ik_extreme_ctrl}.{self.ar.data.lang['c040_uniformScale']}", edit=True, keyable=True)
                # add scale multiplier attribute
                cmds.addAttr(fk_ctrls[-1], longName=f"{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}", attributeType='double', minValue=0.001, defaultValue=1)
                cmds.addAttr(ik_extreme_ctrl, longName=f"{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}", attributeType='double', minValue=0.001, defaultValue=1)
                ik_scale_md = cmds.rename(cmds.createNode('multiplyDivide'), f"{side}{self.number_name}_{self.ar.data.lang['c105_multiplier'].capitalize()}_Ik_MD")
                fk_scale_md = cmds.rename(cmds.createNode('multiplyDivide'), f"{side}{self.number_name}_{self.ar.data.lang['c105_multiplier'].capitalize()}_Fk_MD")
                cmds.connectAttr(f"{ik_extreme_ctrl}.{self.ar.data.lang['c040_uniformScale']}", f"{ik_scale_md}.input1X", force=True)
                cmds.connectAttr(f"{ik_extreme_ctrl}.{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}", f"{ik_scale_md}.input2X", force=True)
                cmds.connectAttr(f"{fk_ctrls[-1]}.{self.ar.data.lang['c040_uniformScale']}", f"{fk_scale_md}.input1X", force=True)
                cmds.connectAttr(f"{fk_ctrls[-1]}.{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}", f"{fk_scale_md}.input2X", force=True)
                # integrate uniformScale and scaleMultiplier attributes
                uni_blend = cmds.createNode('blendColors', name=f"{side}{self.number_name}_{self.ar.data.lang['c040_uniformScale'][0].capitalize()}{self.ar.data.lang['c040_uniformScale'][1:]}_BC")
                cmds.connectAttr(f"{uni_blend}.outputR", f"{orig_grp}.scaleX", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{orig_grp}.scaleY", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{orig_grp}.scaleZ", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{skin_joints[-2]}.scaleX", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{skin_joints[-2]}.scaleY", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{skin_joints[-2]}.scaleZ", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{to_rf_blend_grp}.scaleX", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{to_rf_blend_grp}.scaleY", force=True)
                cmds.connectAttr(f"{uni_blend}.outputR", f"{to_rf_blend_grp}.scaleZ", force=True)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{uni_blend}.blender", force=True)
                cmds.connectAttr(f"{fk_scale_md}.outputX", f"{uni_blend}.color1R", force=True)
                cmds.connectAttr(f"{ik_scale_md}.outputX", f"{uni_blend}.color2R", force=True)
                
                if quadruped:
                    # tell main script to create parent constraint from chestA to ikCtrl for front legs
                    self.quad_front_legs.append(ik_extreme_ctrl_orient_grp)

                # work with not stretch ik setup:
                ik_stretchable_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_IkStretchable_MD")
                cmds.connectAttr(f"{ik_extreme_ctrl}.stretchable", f"{ik_stretchable_md}.input1X", force=True)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{ik_stretchable_md}.input2X", force=True)

                ik_stretch_ctrl_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_IkStretchCtrl_Cnd")
                cmds.setAttr(f"{ik_stretch_ctrl_cnd}.secondTerm", 1)
                cmds.setAttr(f"{ik_stretch_ctrl_cnd}.operation", 3)
                cmds.connectAttr(f"{ik_stretchable_md}.outputX", f"{ik_stretch_ctrl_cnd}.colorIfFalseR", force=True)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{ik_stretch_ctrl_cnd}.colorIfTrueR", force=True)
                cmds.connectAttr(f"{ik_extreme_ctrl}.stretchable", f"{ik_stretch_ctrl_cnd}.firstTerm", force=True)
                cmds.connectAttr(f"{ik_stretch_ctrl_cnd}.outColorR", f"{to_rf_offset_pac}.{ik_extreme_sub_ctrl}W0", force=True)

                ik_stretch_dif_pma = cmds.createNode('plusMinusAverage', name=f"{side}{self.number_name}_Stretch_Dif_PMA")
                cmds.setAttr(f"{ik_stretch_dif_pma}.operation", 2)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{ik_stretch_dif_pma}.input1D[0]", force=True)
                cmds.connectAttr(f"{ik_extreme_ctrl}.stretchable", f"{ik_stretch_dif_pma}.input1D[1]", force=True)

                ik_stretch_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_IkStretch_Cnd")
                cmds.setAttr(f"{ik_stretch_cnd}.operation", 3)
                cmds.setAttr(f"{ik_stretch_cnd}.secondTerm", 1)
                cmds.connectAttr(f"{ik_stretch_dif_pma}.output1D", f"{ik_stretch_cnd}.colorIfFalseR", force=True)
                cmds.connectAttr(f"{ik_extreme_ctrl}.stretchable", f"{ik_stretch_cnd}.firstTerm", force=True)

                ik_stretch_clp = cmds.createNode('clamp', name=f"{side}{self.number_name}_IkStretch_Clp")
                cmds.setAttr(f"{ik_stretch_clp}.maxR", 1)
                cmds.connectAttr(f"{ik_stretch_cnd}.outColorR", f"{ik_stretch_clp}.inputR", force=True)
                cmds.connectAttr(f"{ik_stretch_clp}.outputR", f"{to_rf_offset_pac}.{ik_no_stretch_joints[-2]}W2", force=True)

                # prepare to disable stretch in fk mode
                cmds.addAttr(ik_extreme_ctrl, longName="disableIkFkRevOutputX", attributeType='double', keyable=False)
                cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{ik_extreme_ctrl}.disableIkFkRevOutputX", force=True)

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
                    initial_joint = f"{side}{self.number_name}_{main_name}_Jnt"
                    corner = f"{side}{self.number_name}_{corner_name}_Jnt"
                    corner_jxt = f"{side}{self.number_name}_{corner_name}_Jxt"
                    corner_b = f"{side}{self.number_name}_{corner_b_name}_Jnt"
                    
                    splited = self.number_name.split('_')
                    prefix = ''.join(side)
                    name = ''
                    if len(splited) > 1:
                        prefix += splited[0]
                        name += splited[1]
                    else:
                        name += self.number_name
                    loc = cmds.spaceLocator(n=f"{side}{self.number_name}_auxOriLoc", p=(0, 0, 0))[0]
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
                        locB = cmds.spaceLocator(n=f"{side}{self.number_name}_auxBOriLoc", p=(0, 0, 0))[0]
                        cmds.matchTransform(locB, corner_b, position=True, rotation=True)
                        cmds.delete(cmds.aimConstraint(cmds.listRelatives(corner_b, children=True)[0], locB, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(1, 0, 0)))
                        bend_grps = self.ribbon.add_ribbon_to_limb(self, prefix, name, loc, initial_joint, 'x', bend_joints_number, side=s, arm=False, world_ref=world_ref, joint_label_add=self.joint_label_add, add_artic=self.articulation, additional=self.get_guide_attr('additional'), add_correct=self.corrective, jcr_number=3, jcr_pos=[(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)], ori_b_loc=locB)
                        cmds.delete(locB)
                    else: #biped leg
                        bend_grps = self.ribbon.add_ribbon_to_limb(self, prefix, name, loc, initial_joint, 'x', bend_joints_number, side=s, arm=False, world_ref=world_ref, joint_label_add=self.joint_label_add, add_artic=self.articulation, additional=self.get_guide_attr('additional'), add_correct=self.corrective, jcr_number=3, jcr_pos=[(0, 0, -0.25*self.radius), (0.2*self.radius, 0, 0.4*self.radius), (-0.2*self.radius, 0, 0.4*self.radius)])
                    cmds.delete(loc)

                    if self.limb_types == self.arm_name:
                        ik_extreme_orient_pac = cmds.parentConstraint(bend_grps['extraCtrlList'][-1], ik_extreme_sub_ctrl, fk_joints[-2], extreme_orient_ctrl_zero, maintainOffset=True, skipTranslate=['x', 'y', 'z'], name=f"{extreme_orient_ctrl_zero}_PaC")[0]
                        ik_extreme_orient_pac_w0 = f"{bend_grps['extraCtrlList'][-1]}W0"
                        cmds.pointConstraint(skin_joints[-2], extreme_orient_ctrl_zero, maintainOffset=False, name=f"{extreme_orient_ctrl_zero}_PoC")

                    cmds.parent(bend_grps['ctrlsGrp'], self.ctrl_hook_grp)
                    cmds.parent(bend_grps['scaleGrp'], self.scalable_hook_grp)
                    cmds.parent(bend_grps['staticGrp'], self.static_hook_grp)

                    bend_grp_items = bend_grps['bendGrpList']
                    extra_bend_items = bend_grps['extraBendGrp']

                    if bend_grp_items:
                        if not cmds.objExists(f"{world_ref}.bends"):
                            cmds.addAttr(world_ref, longName='bends', attributeType='long', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                            cmds.addAttr(world_ref, longName='extraBends', attributeType='long', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                        for bend_grp in bend_grp_items:
                            cmds.connectAttr(f"{world_ref}.bends", f"{bend_grp}.visibility", force=True)
                        for extra_bend_grp in extra_bend_items:
                            cmds.connectAttr(f"{world_ref}.extraBends", f"{extra_bend_grp}.visibility", force=True)
                    if bend_grps['controllers']:
                        for offset_ctrl in bend_grps['controllers']:
                            cmds.connectAttr(f"{fk_ctrls[0]}.message", f"{offset_ctrl}.parentTag", force=True)

                    # correct joint skin naming:
                    for jnt_index in range(1, len(skin_joints) - 2):
                        skin_joints[jnt_index] = skin_joints[jnt_index].replace('_Jnt', '_Jxt')
                    
                    # implementing auto rotate twist bones:
                    # check if we have loaded the quatNode.mll Maya plugin in order to create quatToEuler node, also decomposeMatrix from matrixNodes:
                    loaded_quaternion_plugin = self.ar.config.check_loaded_plugin('quatNodes', self.ar.data.lang['e014_cantLoadQuatNode'])
                    loaded_matrix_plugin = self.ar.config.check_loaded_plugin('matrixNodes', self.ar.data.lang['e002_matrixPluginNotFound'])
                    if loaded_quaternion_plugin and loaded_matrix_plugin:
                        twist_bone_md = bend_grps['twistBoneMD']
                        shoulder_child_loc = cmds.spaceLocator(name=f"{twist_bone_md}_Child_Loc")[0]
                        shoulder_parent_loc = cmds.spaceLocator(name=f"{twist_bone_md}_Parent_Loc")[0]
                        cmds.setAttr(f"{shoulder_child_loc}.visibility", 0)
                        cmds.setAttr(f"{shoulder_parent_loc}.visibility", 0)
                        cmds.matchTransform(shoulder_parent_loc, skin_joints[1], position=True, rotation=True)
                        cmds.parent(shoulder_parent_loc, skin_joints[0])
                        cmds.parent(shoulder_child_loc, skin_joints[1], relative=True)
                        self.ar.math.create_twist_bone_matrix(shoulder_parent_loc, shoulder_child_loc, skin_joints[1], twist_bone_md)
                    
                    # fix autoRotate flipping issue:
                    if s == 0: #left
                        cmds.setAttr(f"{bend_grps['controllers'][0]}.invert", 1) #upCtrl
                        cmds.setAttr(f"{bend_grps['controllers'][1]}.invert", 1) #downCtrl
                        if quadruped:
                            cmds.setAttr(f"{bend_grps['controllers'][3]}.invert", 1) #downBCtrl

                # orient controller nodes
                if self.limb_types == self.arm_name:
                    cmds.setAttr(f"{ik_extreme_orient_pac}.interpType", 2) #shortest
                    orient_rev = cmds.createNode('reverse', name=f"{side}{self.number_name}_{extreme_name}_Orient_Rev")
                    orient_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_{extreme_name}_Orient_MD")
                    self.to_ids.extend([orient_rev, orient_md])
                    cmds.connectAttr(f"{ik_extreme_ctrl}.orient", f"{orient_rev}.inputX")
                    cmds.connectAttr(f"{ik_extreme_ctrl}.orient", f"{orient_md}.input1Y")
                    cmds.connectAttr(f"{orient_rev}.outputX", f"{orient_md}.input1X")
                    cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{orient_md}.input2X")
                    cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlendRevOutputX", f"{orient_md}.input2Y")
                    cmds.connectAttr(f"{orient_md}.outputX", f"{ik_extreme_orient_pac}.{ik_extreme_orient_pac_w0}")
                    cmds.connectAttr(f"{orient_md}.outputY", f"{ik_extreme_orient_pac}.{ik_extreme_sub_ctrl}W1")
                    cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{ik_extreme_orient_pac}.{fk_joints[-2]}W2")

                # auto clavicle:
                # loading Maya matrix node
                loaded_quaternion_plugin = self.ar.config.check_loaded_plugin('quatNodes', self.ar.data.lang['e014_cantLoadQuatNode'])
                loaded_matrix_plugin = self.ar.config.check_loaded_plugin('matrixNodes', self.ar.data.lang['e002_matrixPluginNotFound'])
                if loaded_quaternion_plugin and loaded_matrix_plugin:
                    # create auto clavicle group:
                    clavicle_ctrl_grp = cmds.group(name=f"{fk_ctrls[0]}_Grp", empty=True)
                    cmds.matchTransform(clavicle_ctrl_grp, fk_ctrl_zeros[0], position=True, rotation=True)
                    cmds.parent(clavicle_ctrl_grp, fk_ctrl_zeros[0])
                    # invert scale for right side before:
                    if s == 1:
                        cmds.setAttr(f"{clavicle_ctrl_grp}.scaleX", -1)
                        cmds.setAttr(f"{clavicle_ctrl_grp}.scaleY", -1)
                        cmds.setAttr(f"{clavicle_ctrl_grp}.scaleZ", -1)
                    cmds.parent(fk_ctrls[0], clavicle_ctrl_grp, relative=True)
                    
                    # create auto clavicle attribute:
                    cmds.addAttr(fk_ctrls[0], longName=self.ar.data.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                    self.add_follow_attr_name(fk_ctrls[0], self.ar.data.lang['c032_follow'])
                    
                    # ik auto clavicle locators:
                    ac_ik_up_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Up_Loc")[0]
                    ac_ik_aim_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Aim_Loc")[0]
                    ac_orig_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Orig_Loc")[0]
                    ac_fk_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Fk_Loc")[0]
                    ac_ik_main_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Ik_{main_name}_Loc")[0]
                    ac_ik_corner_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Ik_{corner_name}_Loc")[0]
                    ac_ref_main_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_AC_Ref_{main_name}_Loc")[0]
                    cmds.parent(ac_ik_corner_loc, ac_ik_main_loc)
                    ac_loc_grp = cmds.group(ac_ik_up_loc, ac_ik_aim_loc, ac_orig_loc, ac_fk_loc, ac_ik_main_loc, name=f"{side}{self.number_name}_AC_Loc_Grp")
                    cmds.setAttr(f"{ac_loc_grp}.inheritsTransform", 0) #important to calculate world space matrix to extract rotations correctlly
                    cmds.setAttr(f"{ac_loc_grp}.visibility", 0)
                    cmds.setAttr(f"{ac_ref_main_loc}.visibility", 0)
                    if self.limb_types == self.arm_name:
                        cmds.setAttr(f"{ac_ik_up_loc}.translateY", 1)
                    else:
                        cmds.setAttr(f"{ac_ik_up_loc}.translateZ", 1)
                    cmds.delete(cmds.pointConstraint(fk_ctrls[1], ac_loc_grp, maintainOffset=False))
                    cmds.parent([ac_ref_main_loc, ac_loc_grp], self.scalable_hook_grp)
                    cmds.delete(cmds.pointConstraint(ik_auto_clavicle_joints[1], ac_ref_main_loc, maintainOffset=False))
                    cmds.parentConstraint(ik_auto_clavicle_joints[1], ac_ref_main_loc, skipTranslate=['x', 'y', 'z'], maintainOffset=False, name=f"{ac_ref_main_loc}_PaC")
                    self.ar.ctrls.direct_connect(ac_ref_main_loc, ac_ik_main_loc, ['rx', 'ry', 'rz']) #shoulder rotate
                    cmds.matchTransform(ac_ik_corner_loc, fk_ctrls[2], position=True, rotation=True)
                    cmds.parentConstraint(ac_ik_main_loc, ac_ik_up_loc, maintainOffset=True, name=f"{ac_ik_up_loc}_PaC")
                    
                    # aim constraint: (edited in order to point to limb corner (elbow/knee) outside of clavicle hierarchy to avoid cycle error).
                    if self.limb_types == self.arm_name:
                        if s == 0: #left
                            cmds.aimConstraint(ac_ik_corner_loc, ac_ik_aim_loc, maintainOffset=True, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType='object', worldUpObject=ac_ik_up_loc, name=f"{ac_ik_aim_loc}_AiC")
                        else: #right
                            cmds.aimConstraint(ac_ik_corner_loc, ac_ik_aim_loc, maintainOffset=True, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0), worldUpType='object', worldUpObject=ac_ik_up_loc, name=f"{ac_ik_aim_loc}_AiC")
                    else: #leg
                        cmds.aimConstraint(ac_ik_corner_loc, ac_ik_aim_loc, maintainOffset=True, weight=1, aimVector=(0, -1, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=ac_ik_up_loc, name=f"{ac_ik_aim_loc}_AiC")
                    
                    # fk auto clavicle setup:
                    self.ar.ctrls.direct_connect(fk_ctrls[1], ac_fk_loc, ['rx', 'ry', 'rz'])
                    # auto clavicle matrix rotate extraction:
                    ac_ik_mm = cmds.createNode('multMatrix', name=f"{side}{self.number_name}_AC_Ik_MM")
                    ac_ik_dm = cmds.createNode('decomposeMatrix', name=f"{side}{self.number_name}_AC_Ik_DM")
                    ac_ik_qte = cmds.createNode('quatToEuler', name=f"{side}{self.number_name}_AC_Ik_QtE")
                    ac_fk_mm = cmds.createNode('multMatrix', name=f"{side}{self.number_name}_AC_Fk_MM")
                    ac_fk_dm = cmds.createNode('decomposeMatrix', name=f"{side}{self.number_name}_AC_Fk_DM")
                    ac_fk_qte = cmds.createNode('quatToEuler', name=f"{side}{self.number_name}_AC_Fk_QtE")
                    ac_bc = cmds.createNode('blendColors', name=f"{side}{self.number_name}_AC_BC")
                    ac_inv_bc = cmds.createNode('blendColors', name=f"{side}{self.number_name}_AC_Inv_BC")
                    ac_inv_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_AC_Inv_MD")
                    ac_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_AC_MD")
                    self.to_ids.extend([ac_ik_mm, ac_ik_dm, ac_ik_qte, ac_fk_mm, ac_fk_dm, ac_fk_qte, ac_bc, ac_inv_bc, ac_inv_md, ac_md])
                    cmds.setAttr(f"{ac_fk_qte}.inputRotateOrder", 1) #yzx
                    # add attributes to control inverse value setup to blend ikFk:
                    for ik_fk_rot_attr in ['ikRotateX', 'ikRotateY', 'ikRotateZ', 'fkRotateX', 'fkRotateY', 'fkRotateZ']: #ikFkRotAttrList
                        cmds.addAttr(fk_ctrls[0], longName=ik_fk_rot_attr, attributeType='float', minValue=-1, defaultValue=1, maxValue=1)
                    # set values of ik and fk rotates:
                    if s == 0: #left side
                        if self.limb_types == self.leg_name:
                            cmds.setAttr(f"{fk_ctrls[0]}.ikRotateY", -1)
                            cmds.setAttr(f"{fk_ctrls[0]}.fkRotateX", -1)
                    else: #right side
                        if self.limb_types == self.arm_name:
                            cmds.setAttr(f"{fk_ctrls[0]}.ikRotateY", -1)
                        else: #leg
                            cmds.setAttr(f"{fk_ctrls[0]}.fkRotateX", -1)
                        cmds.setAttr(f"{fk_ctrls[0]}.ikRotateZ", -1)

                    # connections inverse values from fkCtrlList[0] (Clavile or Hips) to inverseBlendColor:
                    cmds.connectAttr(f"{fk_ctrls[0]}.ikRotateX", f"{ac_inv_bc}.color2R", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.ikRotateY", f"{ac_inv_bc}.color2G", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.ikRotateZ", f"{ac_inv_bc}.color2B", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.fkRotateX", f"{ac_inv_bc}.color1R", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.fkRotateY", f"{ac_inv_bc}.color1G", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.fkRotateZ", f"{ac_inv_bc}.color1B", force=True)

                    # connections auto clavicle Ik:
                    cmds.connectAttr(f"{ac_orig_loc}.worldInverseMatrix[0]", f"{ac_ik_mm}.matrixIn[0]", force=True)
                    cmds.connectAttr(f"{ac_ik_aim_loc}.worldMatrix[0]", f"{ac_ik_mm}.matrixIn[1]", force=True)
                    cmds.connectAttr(f"{ac_ik_mm}.matrixSum", f"{ac_ik_dm}.inputMatrix", force=True)
                    cmds.connectAttr(f"{ac_ik_dm}.outputQuatX", f"{ac_ik_qte}.inputQuatX", force=True)
                    cmds.connectAttr(f"{ac_ik_dm}.outputQuatY", f"{ac_ik_qte}.inputQuatY", force=True)
                    cmds.connectAttr(f"{ac_ik_dm}.outputQuatZ", f"{ac_ik_qte}.inputQuatZ", force=True)
                    cmds.connectAttr(f"{ac_ik_dm}.outputQuatW", f"{ac_ik_qte}.inputQuatW", force=True)
                    # connections auto clavicle Fk:
                    cmds.connectAttr(f"{ac_orig_loc}.worldInverseMatrix[0]", f"{ac_fk_mm}.matrixIn[0]", force=True)
                    cmds.connectAttr(f"{ac_fk_loc}.worldMatrix[0]", f"{ac_fk_mm}.matrixIn[1]", force=True)
                    cmds.connectAttr(f"{ac_fk_mm}.matrixSum", f"{ac_fk_dm}.inputMatrix", force=True)
                    cmds.connectAttr(f"{ac_fk_dm}.outputQuatX", f"{ac_fk_qte}.inputQuatX", force=True)
                    cmds.connectAttr(f"{ac_fk_dm}.outputQuatY", f"{ac_fk_qte}.inputQuatY", force=True)
                    cmds.connectAttr(f"{ac_fk_dm}.outputQuatZ", f"{ac_fk_qte}.inputQuatZ", force=True)
                    cmds.connectAttr(f"{ac_fk_dm}.outputQuatW", f"{ac_fk_qte}.inputQuatW", force=True)
                    # fk to auto clavicle blend colors:
                    if self.limb_types == self.arm_name:
                        cmds.connectAttr(f"{ac_fk_qte}.outputRotate.outputRotateX", f"{ac_bc}.color1G", force=True)
                        cmds.connectAttr(f"{ac_fk_qte}.outputRotate.outputRotateY", f"{ac_bc}.color1B", force=True)
                        cmds.connectAttr(f"{ac_fk_qte}.outputRotate.outputRotateZ", f"{ac_bc}.color1R", force=True)
                    else: #leg
                        cmds.connectAttr(f"{ac_fk_qte}.outputRotate.outputRotateX", f"{ac_bc}.color1B", force=True)
                        cmds.connectAttr(f"{ac_fk_qte}.outputRotate.outputRotateY", f"{ac_bc}.color1R", force=True)
                        cmds.connectAttr(f"{ac_fk_qte}.outputRotate.outputRotateZ", f"{ac_bc}.color1G", force=True)
                    # ik to auto clavicle blend colors:
                    cmds.connectAttr(f"{ac_ik_qte}.outputRotate.outputRotateX", f"{ac_bc}.color2R", force=True)
                    cmds.connectAttr(f"{ac_ik_qte}.outputRotate.outputRotateY", f"{ac_bc}.color2G", force=True)
                    cmds.connectAttr(f"{ac_ik_qte}.outputRotate.outputRotateZ", f"{ac_bc}.color2B", force=True)
                    cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{ac_bc}.blender", force=True)
                    cmds.connectAttr(f"{world_ref}.{attr_name_lower}Fk_ikFkBlend", f"{ac_inv_bc}.blender", force=True)
                    cmds.connectAttr(f"{ac_bc}.output.outputR", f"{ac_inv_md}.input1X", force=True)
                    cmds.connectAttr(f"{ac_bc}.output.outputG", f"{ac_inv_md}.input1Y", force=True)
                    cmds.connectAttr(f"{ac_bc}.output.outputB", f"{ac_inv_md}.input1Z", force=True)
                    cmds.connectAttr(f"{ac_inv_bc}.output.outputR", f"{ac_inv_md}.input2X", force=True)
                    cmds.connectAttr(f"{ac_inv_bc}.output.outputG", f"{ac_inv_md}.input2Y", force=True)
                    cmds.connectAttr(f"{ac_inv_bc}.output.outputB", f"{ac_inv_md}.input2Z", force=True)
                    cmds.connectAttr(f"{ac_inv_md}.outputX", f"{ac_md}.input1X", force=True)
                    cmds.connectAttr(f"{ac_inv_md}.outputY", f"{ac_md}.input1Y", force=True)
                    cmds.connectAttr(f"{ac_inv_md}.outputZ", f"{ac_md}.input1Z", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.{self.ar.data.lang['c032_follow']}", f"{ac_md}.input2X", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.{self.ar.data.lang['c032_follow']}", f"{ac_md}.input2Y", force=True)
                    cmds.connectAttr(f"{fk_ctrls[0]}.{self.ar.data.lang['c032_follow']}", f"{ac_md}.input2Z", force=True)
                    if self.limb_types == self.arm_name:
                        cmds.connectAttr(f"{ac_md}.outputX", f"{clavicle_ctrl_grp}.rotateZ", force=True)
                        cmds.connectAttr(f"{ac_md}.outputY", f"{clavicle_ctrl_grp}.rotateX", force=True)
                        cmds.connectAttr(f"{ac_md}.outputZ", f"{clavicle_ctrl_grp}.rotateY", force=True)
                    else: #leg
                        cmds.connectAttr(f"{ac_md}.outputX", f"{clavicle_ctrl_grp}.rotateX", force=True)
                        cmds.connectAttr(f"{ac_md}.outputY", f"{clavicle_ctrl_grp}.rotateZ", force=True)
                        cmds.connectAttr(f"{ac_md}.outputZ", f"{clavicle_ctrl_grp}.rotateY", force=True)
                
                # arrange correct before and extrem skinning joints naming in order to be easy to skinning paint weight UI:
                # default value for 5 bend joints:
                before_number  = '00' #clavicle/hips
                first_number   = '01' #shoulder/leg
                corner_number  = '07' #elbow/knee
                corner_b_number = '13' #knee_b
                extreme_number  = '13' #wrist/ankle
                if quadruped:
                    extreme_number = '19' #ankle
                if self.get_guide_attr('hasBend'):
                    if not self.articulation:
                        extreme_number = '11'
                        if quadruped:
                            extreme_number = '16'
                    bend_joints_number = self.get_guide_attr('numBendJoints')
                    if bend_joints_number == 3:
                        corner_number = '05'
                        corner_b_number = '09'
                        extreme_number = '09'
                        if quadruped:
                            extreme_number = '13'
                        if not self.articulation:
                            extreme_number = '07'
                            if quadruped:
                                extreme_number = '10'
                    elif bend_joints_number == 7:
                        corner_number = '09'
                        corner_b_number = '17'
                        extreme_number = '17'
                        if quadruped:
                            extreme_number = '25'
                        if not self.articulation:
                            extreme_number = '15'
                            if quadruped:
                                extreme_number = '22'
                    skin_joints[0] = cmds.rename(skin_joints[0], f"{side}{self.number_name}_{before_number}_{before_name}{suffixes[0]}") #clavicle/hips
                    skin_joints[-2] = cmds.rename(skin_joints[-2], f"{side}{self.number_name}_{extreme_number}_{extreme_name}{suffixes[0]}") #wrist/ankle
                    if self.articulation:
                        corner_joints, corner_b_joints = [], []
                        if bend_grps:
                            bend_joints = cmds.listRelatives(bend_grps['jntGrp'])
                            self.ar.naming.set_joint_label(cmds.listRelatives(bend_joints[bend_joints_number])[0], s+self.joint_label_add, 18, f"{self.number_name}_{corner_number}_{corner_name}")
                            jar = cmds.rename(cmds.listRelatives(bend_joints[bend_joints_number])[0], f"{side}{self.number_name}_{corner_number}_{corner_name}_Jar")
                            corner_joints.append(jar)
                            if quadruped:
                                self.ar.naming.set_joint_label(cmds.listRelatives(bend_joints[bend_joints_number*2+1])[0], s+self.joint_label_add, 18, f"{self.number_name}_{corner_b_number}_{corner_b_name}")
                                jar = cmds.rename(cmds.listRelatives(bend_joints[bend_joints_number*2+1])[0], f"{side}{self.number_name}_{corner_b_number}_{corner_b_name}_Jar")
                                corner_b_joints.append(jar)
                                if self.ar.data.lang['c056_front'] in self.number_name:
                                    if s == 0:
                                        cmds.setAttr(f"{corner_joints[0]}.rotateX", 0)
                                    else:
                                        cmds.setAttr(f"{corner_joints[0]}.rotateX", 180)
                                else:
                                    if s == 0:
                                        cmds.setAttr(f"{corner_b_joints[0]}.rotateX", 0)
                                    else:
                                        cmds.setAttr(f"{corner_b_joints[0]}.rotateX", 180)
                            if self.corrective:
                                corner_joints.extend(self.rename_corner_rename(s, side, corner_joints[0], corner_number, corner_name))
                                if quadruped:
                                    corner_b_joints.extend(self.rename_corner_rename(s, side, corner_b_joints[0], corner_b_number, corner_b_name))
                            if to_corner_bend_items:
                                self.ar.utils.set_origined_from_attr(bend_grps['controllers'][2], ";".join(to_corner_bend_items))
                                cmds.delete(f"{side}{self.number_name}_{corner_name}_OrigFrom_Grp_PaC")
                                cmds.parentConstraint(bend_grps['controllers'][2], f"{side}{self.number_name}_{corner_name}_OrigFrom_Grp", maintainOffset=True, name=f"{side}{self.number_name}_{corner_name}_OrigFrom_Grp_PaC")
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
                            cmds.setAttr(f"{corner_joints[0]}.rotateY", -90)
                            cmds.setAttr(f"{corner_joints[0]}.rotateZ", -90)
                        else:
                            cmds.setAttr(f"{corner_joints[0]}.rotateY", 90)
                            if quadruped:
                                if self.ar.data.lang['c056_front'] in self.number_name:
                                    cmds.setAttr(f"{corner_joints[0]}.rotateX", 180)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateX", -90)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateY", 90)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateZ", 180)
                                else:
                                    cmds.setAttr(f"{corner_joints[0]}.rotateX", 0)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateY", 90)
                                cmds.setAttr(f"{corner_joints[0]}.rotateZ", 180)
                                cmds.setAttr(f"{corner_b_joints[0]}.rotateX", 0)
                            else:
                                cmds.setAttr(f"{corner_joints[0]}.rotateX", -90)
                                cmds.setAttr(f"{corner_joints[0]}.rotateZ", 90)
                    else:
                        if self.limb_type == self.arm_name:
                            cmds.setAttr(f"{corner_joints[0]}.rotateX", 180)
                            cmds.setAttr(f"{corner_joints[0]}.rotateY", 90)
                            cmds.setAttr(f"{corner_joints[0]}.rotateZ", 90)
                        else:
                            cmds.setAttr(f"{corner_joints[0]}.rotateY", -90)
                            if quadruped:
                                cmds.setAttr(f"{corner_joints[0]}.rotateZ", 180)
                                if self.ar.data.lang['c056_front'] in self.number_name:
                                    cmds.setAttr(f"{corner_joints[0]}.rotateX", 180)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateX", 90)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateY", -90)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateZ", 90)
                                else:
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateY", -90)
                                    cmds.setAttr(f"{corner_b_joints[0]}.rotateX", 0)
                            else:
                                cmds.setAttr(f"{corner_joints[0]}.rotateX", 90)
                                cmds.setAttr(f"{corner_joints[0]}.rotateZ", 90)

                # orient controller setup
                if self.limb_types == self.arm_name:
                    extreme_old_name = skin_joints[-2]
                    extreme_new_name = extreme_old_name.replace('_Jnt', '_Jxt')
                    cmds.setAttr(f"{extreme_old_name}.visibility", 0)
                    cmds.rename(extreme_old_name, extreme_new_name)
                    skin_joints[-2] = extreme_new_name
                    cmds.select(clear=True)
                    cmds.joint(name=extreme_old_name)
                    orient_joint_end = cmds.joint(name=extreme_old_name.replace('Jnt', f"Orient_{self.ar.data.joint_end_attr}"))
                    self.ar.utils.add_joint_end_attr([orient_joint_end])
                    cmds.parentConstraint(extreme_orient_ctrl, extreme_old_name, maintainOffset=False, name=f"{extreme_old_name}_PaC")
                    cmds.matchTransform(orient_joint_end, skin_joints[-1], position=True, rotation=True)
                    cmds.addAttr(extreme_old_name, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.naming.set_joint_label(extreme_old_name, s+self.joint_label_add, 18, f"{self.number_name}_{joint_names[len(skin_joints)-2]}")
                    cmds.parent(extreme_old_name, self.scalable_hook_grp)
                    cmds.connectAttr(f"{uni_blend}.outputR", f"{extreme_old_name}.scaleX", force=True)
                    cmds.connectAttr(f"{uni_blend}.outputR", f"{extreme_old_name}.scaleY", force=True)
                    cmds.connectAttr(f"{uni_blend}.outputR", f"{extreme_old_name}.scaleZ", force=True)
                    cmds.connectAttr(f"{uni_blend}.outputR", f"{extreme_orient_ctrl_zero}.scaleX", force=True)
                    cmds.connectAttr(f"{uni_blend}.outputR", f"{extreme_orient_ctrl_zero}.scaleY", force=True)
                    cmds.connectAttr(f"{uni_blend}.outputR", f"{extreme_orient_ctrl_zero}.scaleZ", force=True)

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
                corner_corrective_net = self.setup_corrective_net(corrective_ctrl, skin_joints[1], skin_joints[2], f"{side}{self.number_name}_{joint_names[2]}_YawRight", 0, 0, -110, is_leg, [f"{side}{self.number_name}_{joint_names[2]}_YawLeft", 1, 1, -110])
                corrective_net_input_value = cmds.getAttr(f"{corner_corrective_net}.inputValue")
                if corrective_net_input_value > 0:
                    cmds.setAttr(f"{corner_corrective_net}.inputEnd", corrective_net_input_value+110)
                if quadruped:
                    corner_b_corrective_net = self.setup_corrective_net(corrective_b_ctrl, skin_joints[2], skin_joints[3], f"{side}{self.number_name}_{joint_names[3]}_YawRight", 0, 0, -110, is_leg, [f"{side}{self.number_name}_{joint_names[3]}_YawLeft", 1, 1, -110])
                    corrective_b_net_input_value = cmds.getAttr(f"{corner_b_corrective_net}.inputValue")
                    if corrective_b_net_input_value <= 0:
                        cmds.setAttr(f"{corner_b_corrective_net}.inputEnd", corrective_b_net_input_value+110)

                # add hook attributes to be read when rigging integrated modules:
                cmds.parentConstraint(self.ctrl_hook_grp, self.scalable_hook_grp, maintainOffset=True, name=f"{self.scalable_hook_grp}_PaC")
                cmds.parentConstraint(self.ctrl_hook_grp, pv_aim_loc, skipRotate=['x', 'y', 'z'], maintainOffset=True, name=f"{pv_aim_loc}_PaC")
                self.scalable_grps.append(self.scalable_hook_grp)

                # add main articulationJoint:
                if self.articulation:
                    before_jxt = cmds.duplicate(skin_joints[0], name=f"{side}{self.number_name}_{joint_names[0]}_Jxt")[0]
                    cmds.delete(cmds.listRelatives(before_jxt, children=True, allDescendents=True, fullPath=True))
                    if self.corrective:
                        # corrective controls group
                        self.corrective_ctrls_grp = cmds.group(name=f"{side}{self.number_name}_Corrective_Grp", empty=True)
                        self.corrective_ctrl_grps.append(self.corrective_ctrls_grp)
                        cmds.parent(self.corrective_ctrls_grp, self.ctrl_hook_grp)
                        
                        # clavicle / hips
                        before_corrective_nets = [None]
                        before_corrective_nets.append(self.setup_corrective_net(fk_ctrls[0], self.scalable_hook_grp, skin_joints[0], f"{side}{self.number_name}_{joint_names[0]}_PitchUp", 1, 1, 60, is_leg, [f"{side}{self.number_name}_{joint_names[0]}_PitchUp", 1, 1, 60]))
                        before_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, True, False, False, False, False)
                        before_joints = self.ar.utils.create_articulation_joint(before_jxt, skin_joints[0], 1, [(0.3*self.radius, 0, 0.3*self.radius)])
                        self.setup_corrective_controllers(before_joints, s, f"{self.number_name}_{before_number}_{before_name}", before_corrective_nets, before_calibrate_presets, inverts)

                        # shoulder / leg
                        main_corrective_nets = [None]
                        main_corrective_nets.append(self.setup_corrective_net(fk_ctrls[0], shoulder_ref_grp, skin_joints[1], f"{side}{self.number_name}_{joint_names[1]}_PitchUp", 0, main_axis_order, -91, is_leg, [f"{side}{self.number_name}_{joint_names[1]}_PitchDown", 0, main_axis_order, 91]))
                        main_corrective_nets.append(self.setup_corrective_net(fk_ctrls[0], shoulder_ref_grp, skin_joints[1], f"{side}{self.number_name}_{joint_names[1]}_YawRight", 1, 1, 46, is_leg, [f"{side}{self.number_name}_{joint_names[1]}_YawLeft", 1, 4, 91]))
                        main_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, True, False, False, False)
                        main_joints = self.ar.utils.create_articulation_joint(shoulder_ref_grp, skin_joints[1], 2, [(0, main_jar_y_value*self.radius, 0), (0.3*self.radius, 0, 0)])
                        self.setup_corrective_controllers(main_joints, s, f"{self.number_name}_{first_number}_{main_name}", main_corrective_nets, main_calibrate_presets, inverts)
                        
                        # elbow / knee
                        corner_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, False, True, False, False)
                        corner_corrective_nets = [None, corner_corrective_net, corner_corrective_net, corner_corrective_net]
                        self.setup_corrective_controllers(corner_joints, s, f"{self.number_name}_{corner_number}_{corner_name}", corner_corrective_nets, corner_calibrate_presets, inverts)

                        # quadruped knee_b
                        if quadruped:
                            corner_b_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, False, False, True, False)
                            corner_b_corrective_nets = [None, corner_b_corrective_net, corner_b_corrective_net, corner_b_corrective_net]
                            self.setup_corrective_controllers(corner_b_joints, s, f"{self.number_name}_{corner_b_number}_{corner_b_name}", corner_b_corrective_nets, corner_b_calibrate_presets, inverts)
                        
                        # wrist / ankle
                        extreme_corrective_nets = [None]
                        if self.limb_types == self.arm_name:
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, f"{side}{self.number_name}_{joint_names[-1]}_PitchUp", 1, 4, 80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_PitchUp", 1, 1, 80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, f"{side}{self.number_name}_{joint_names[-1]}_PitchDown", 1, 4, -80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_PitchDown", 1, 1, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, f"{side}{self.number_name}_{joint_names[-1]}_YawRight", 0, 2, -80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_YawRight", 0, 0, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], extreme_orient_ctrl, f"{side}{self.number_name}_{joint_names[-1]}_YawLeft", 0, 2, 80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_YawLeft", 0, 0, 80]))
                        else: #leg
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], f"{side}{self.number_name}_{joint_names[-1]}_PitchUp", 1, 4, 80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_PitchUp", 1, 1, 80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], f"{side}{self.number_name}_{joint_names[-1]}_PitchDown", 1, 4, -80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_PitchDown", 1, 1, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], f"{side}{self.number_name}_{joint_names[-1]}_YawRight", 0, 2, -80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_YawRight", 0, 0, -80]))
                            extreme_corrective_nets.append(self.setup_corrective_net(to_parent_extrem_ctrl, skin_joints[-3], skin_joints[-2], f"{side}{self.number_name}_{joint_names[-1]}_YawLeft", 0, 2, 80, is_leg, [f"{side}{self.number_name}_{joint_names[-1]}_YawLeft", 0, 0, 80]))
                        extreme_calibrate_presets, inverts = self.get_calibrate_presets(s, is_leg, False, False, False, False, True)
                        if self.limb_types == self.arm_name:
                            extreme_joints = self.ar.utils.create_articulation_joint(skin_joints[-3], skin_joints[-2], 4, [(0.2*self.radius, 0, 0), (-0.2*self.radius, 0, 0), (0, 0.2*self.radius, 0), (0, -0.2*self.radius, 0)], orient_ctrl=extreme_orient_ctrl)
                        else:
                            extreme_joints = self.ar.utils.create_articulation_joint(skin_joints[-3], skin_joints[-2], 4, [(0.2*self.radius, 0, 0), (-0.2*self.radius, 0, 0), (0, 0.2*self.radius, 0), (0, -0.2*self.radius, 0)])
                        self.setup_corrective_controllers(extreme_joints, s, f"{self.number_name}_{extreme_number}_{extreme_name}", extreme_corrective_nets, extreme_calibrate_presets, inverts)
                        # fix rotate with 100% of value for the wrist axis - Thanks Andre Ruegger for the help!
                        extreme_jax = cmds.listRelatives(extreme_joints[0], parent=True, type='joint')[0]
                        orient_connection = cmds.listConnections(f"{extreme_jax}.rotateZ", destination=False, source=True, plugs=True)[0]
                        cmds.disconnectAttr(orient_connection, f"{extreme_jax}.rotateZ")
                        jax_rot_z_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_{extreme_name}_RotZ_Fix_MD")
                        self.to_ids.append(jax_rot_z_md)
                        cmds.setAttr(f"{jax_rot_z_md}.input2Z", 2)
                        cmds.connectAttr(orient_connection, f"{jax_rot_z_md}.input1Z", force=True)
                        cmds.connectAttr(f"{jax_rot_z_md}.outputZ", f"{extreme_jax}.rotateZ", force=True)
                        # expose ankle data to be replaced by foot connections when integrating modules
                        self.ankle_articulations.append([extreme_jax, f"{extreme_joints[0]}_OrC", f"{side}{self.number_name}_{expose_corner_name}"])
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
                        self.ar.naming.set_joint_label(corner_joints[0], s+self.joint_label_add, 18, f"{self.number_name}_01_{corner_name}")
                        cmds.rename(corner_joints[0], f"{side}{self.number_name}_{corner_number}_{corner_name}_Jar")
                        if quadruped:
                            self.ar.naming.set_joint_label(corner_b_joints[0], s+self.joint_label_add, 18, f"{self.number_name}_01_{corner_b_name}")
                            cmds.rename(corner_b_joints[0], f"{side}{self.number_name}_{corner_b_number}_{corner_b_name}_Jar")
                        self.ankle_articulations.append([cmds.listRelatives(extreme_joints[0], parent=True, type='joint')[0], f"{extreme_joints[0]}_OrC", f"{side}{self.number_name}_{expose_corner_name}"])
                        self.ankle_correctives.append(None)
                        cmds.setAttr(f"{before_joints[0]}_OrC.interpType", 1) #average
                    if extreme_joints:
                        extreme_jax_items = cmds.listRelatives(extreme_joints[0], parent=True, type='joint')
                        if extreme_jax_items:
                            cmds.setAttr(f"{extreme_jax_items[0]}.segmentScaleCompensate", 1)
                    if s == 1:
                        for jar in [before_joints[0], main_joints[0], extreme_joints[0]]:
                            cmds.setAttr(f"{jar}.rotateX", 180)
                            cmds.setAttr(f"{jar}.scaleX", -1)
                    self.ar.naming.set_joint_label(before_joints[0], s+self.joint_label_add, 18, f"{self.number_name}_00_{before_name}")
                    self.ar.naming.set_joint_label(main_joints[0], s+self.joint_label_add, 18, f"{self.number_name}_{first_number}_{main_name}")
                    self.ar.naming.set_joint_label(extreme_joints[0], s+self.joint_label_add, 18, f"{self.number_name}_{extreme_number}_{extreme_name}")
                    main_joints[0] = cmds.rename(main_joints[0], f"{side}{self.number_name}_{first_number}_{main_name}_Jar")
                    extreme_joints[0] = cmds.rename(extreme_joints[0], f"{side}{self.number_name}_{extreme_number}_{extreme_name}_Jar")
                else:
                    self.ankle_articulations.append(None)
                    self.ankle_correctives.append(None)

                # add main sub controller
                if self.articulation and self.get_guide_attr('hasBend') and bend_grps:
                    main_jar = main_joints[0]
                    main_jax = cmds.listRelatives(main_joints[0], parent=True, type='joint')[0]
                    main_sub_ctrl = self.ar.ctrls.create_controller('id_095_LimbMainSub', ctrl_name=f"{side}{self.number_name}_{main_name}_Sub_Ctrl", r=(self.radius * 0.9), d=self.curve_degree, guide_source=f"{self.name_guide}_Main", parent_tag=fk_ctrls[0])
                    self.ar.ctrls.set_lock_hide([main_sub_ctrl], ['sx', 'sy', 'sz', 'v'])
                    self.ar.ctrls.set_sub_ctrl_display(fk_ctrls[0], main_sub_ctrl, 0)
                    main_sub_ctrl_zero = self.ar.utils.create_zero_out([main_sub_ctrl])[0]
                    cmds.delete(bend_grps['bottomPosPaC'][1])
                    pac1 = cmds.parentConstraint(main_jax, main_sub_ctrl_zero, maintainOffset=False, name=f"{main_sub_ctrl_zero}_PaC")[0]
                    pac2 = cmds.parentConstraint(main_sub_ctrl, main_jar, maintainOffset=True, name=f"{main_jar}_PaC")[0]
                    pac3 = cmds.parentConstraint(main_jar, bend_grps['bottomPosPaC'][0], maintainOffset=True, name=f"{bend_grps['bottomPosPaC'][0]}_PaC")[0]
                    cmds.setAttr(f"{pac1}.interpType", 0) #noFlip
                    cmds.setAttr(f"{pac2}.interpType", 0) #noFlip
                    cmds.setAttr(f"{pac3}.interpType", 0) #noFlip
                    cmds.parent(main_sub_ctrl_zero, self.ctrl_hook_grp)

                # softIk:
                self.soft_ik_calibrate_items.append(self.soft_ik.create_soft_ik(f"{side}{self.number_name}", ik_extreme_ctrl, ik_handle_main_items[0], ik_joints[1:4], skin_joints[1:4], dist_between_items[1], world_ref))
                # orient ikHandle group setup:
                soft_ik_orient_loc = cmds.spaceLocator(name=f"{side}{self.number_name}_SoftIk_Aim_Loc")[0]
                cmds.matchTransform(soft_ik_orient_loc, ik_joints[1], position=True, rotation=True)
                cmds.parent(soft_ik_orient_loc, ik_joints[0])
                cmds.aimConstraint(ik_extreme_ctrl, soft_ik_orient_loc, aimVector=(0.0, 0.0, 1.0), upVector=(0.0, 1.0, 0.0), worldUpType='object', worldUpObject=ik_corner_ctrl, name=f"{soft_ik_orient_loc}_AiC")
                cmds.orientConstraint(soft_ik_orient_loc, ik_handle_extra_grp, maintainOffset=False, name=f"{ik_handle_grp}_OrC")
                # leg with softIk on and stretchable equals to zero reverser foot issue fix:
                if self.limb_type == self.leg_name:
                    rf_dist_bet_items = self.ar.math.create_dist_between(ik_no_stretch_joints[3], ik_extreme_ctrl, name=f"{side}{self.number_name}_{stretch_names[1]}_RF_DistBet", keep=True)
                    cmds.delete(rf_dist_bet_items[4])
                    cmds.parent(rf_dist_bet_items[2:4], dist_bet_grp)
                    rf_soft_ik_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_RF_SoftIk_Cnd")
                    rf_stretchable_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_RF_Stretchable_Cnd")
                    rf_dist_inv_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_RF_DistInv_MD")
                    self.to_ids.extend([rf_soft_ik_cnd, rf_stretchable_cnd, rf_dist_inv_md])
                    cmds.setAttr(f"{rf_dist_inv_md}.input2X", -1)
                    cmds.setAttr(f"{rf_stretchable_cnd}.colorIfFalseR", 0)
                    cmds.connectAttr(f"{rf_dist_bet_items[1]}.distance", f"{rf_soft_ik_cnd}.colorIfFalseR", force=True)
                    cmds.connectAttr(f"{ik_extreme_ctrl}.softIk", f"{rf_soft_ik_cnd}.firstTerm", force=True)
                    cmds.connectAttr(f"{rf_soft_ik_cnd}.outColorR", f"{rf_dist_inv_md}.input1X", force=True)
                    cmds.connectAttr(f"{rf_dist_inv_md}.outputX", f"{rf_stretchable_cnd}.colorIfTrueR", force=True)
                    cmds.connectAttr(f"{ik_extreme_ctrl}.stretchable", f"{rf_stretchable_cnd}.firstTerm", force=True)
                    cmds.connectAttr(f"{rf_stretchable_cnd}.outColorR", f"{ik_stretch_extreme_loc}.translateZ", force=True)
                    cmds.orientConstraint(soft_ik_orient_loc, ik_stretch_extreme_loc_zero, maintainOffset=False, name=f"{ik_stretch_extreme_loc_zero}_OrC")
                
                # ikFkSnap
                ik_fk_snap.IkFkSnap(self.ar, f"{side}{self.number_name}", world_ref, fk_ctrls, [ik_corner_ctrl, ik_extreme_ctrl, ik_extreme_sub_ctrl], ik_joints, [self.ar.data.lang['c018_revFoot_roll'], self.ar.data.lang['c019_revFoot_spin'], self.ar.data.lang['c020_revFoot_turn']], self.ar.data.lang['c040_uniformScale'], dp_dev=self.ar.dev)
                
                # calibration attribute:
                if self.limb_types == self.arm_name:
                    ik_extreme_calibrations = [
                                            f"{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}",
                                            f"softIk_{self.ar.data.lang['c111_calibrate']}"
                    ]
                else: #leg
                    ik_extreme_calibrations = [
                                            f"{self.ar.data.lang['c015_revFoot_F']}{self.ar.data.lang['c018_revFoot_roll'].capitalize()}{self.ar.data.lang['c102_angle'].capitalize()}",
                                            f"{self.ar.data.lang['c015_revFoot_F']}{self.ar.data.lang['c018_revFoot_roll'].capitalize()}{self.ar.data.lang['c103_plant'].capitalize()}",
                                            f"{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}",
                                            f"softIk_{self.ar.data.lang['c111_calibrate']}"
                    ]
                fk_extreme_calibrations = [f"{self.ar.data.lang['c040_uniformScale']}{self.ar.data.lang['c105_multiplier'].capitalize()}"]
                fk_before_calibrations = [self.ar.data.lang['c032_follow']]
                corner_calibrations = ['calibrateRestTX', 'calibrateRestTY', 'calibrateRestTZ']
                corner_not_mirrors = [f"{self.ar.data.lang['c053_invert']}X",
                                        f"{self.ar.data.lang['c053_invert']}Y",
                                        f"{self.ar.data.lang['c053_invert']}Z"]
                if quadruped:
                    self.ar.ctrls.set_string_attr_from_items(quad_extra_ctrl, ['autoOrient'])
                self.ar.ctrls.set_string_attr_from_items(ik_extreme_ctrl, ik_extreme_calibrations)
                self.ar.ctrls.set_string_attr_from_items(fk_ctrls[-1], fk_extreme_calibrations)
                self.ar.ctrls.set_string_attr_from_items(fk_ctrls[0], fk_before_calibrations)
                self.ar.ctrls.set_string_attr_from_items(ik_corner_ctrl, corner_calibrations)
                self.ar.ctrls.set_string_attr_from_items(ik_corner_ctrl, corner_not_mirrors, 'notMirrorList') #useful to export calibrationIO and not mirror them

                # integrating dics:
                self.extreme_joints.append(skin_joints[-2])
                self.integrate_orig_from_items.append(orig_from_items)
                
                # clean-up before joint, it isn't used to autoClavicle:
                cmds.delete(ik_auto_clavicle_joints[0])
                # delete duplicated group for side (mirror):
                cmds.delete(f"{side}{self.number_name}_{self.mirror_grp}")
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
                            'ikCtrlList': self.ik_extreme_ctrls,
                            'ikCtrlZeroList': self.ik_extreme_ctrl_zeros,
                            'ikPoleVectorZeroList': self.ik_pole_vector_ctrl_zeros,
                            'ikHandleGrpList': self.to_rev_foot_ik_handle_grps,
                            'ikHandleConstList': self.ik_handle_constraints, 
                            'ikHandleGrpConstList': self.ik_handle_grp_constraints, 
                            'ikFkBlendGrpToRevFootList': self.to_rf_blend_grps,
                            'worldRefList': self.world_refs,
                            'worldRefShapeList': self.world_ref_shapes,
                            'limbTypeName': self.limb_types,
                            'extremJntList': self.extreme_joints,
                            'limbStyle': self.get_limb_style(),
                            'quadFrontLegList': self.quad_front_legs,
                            'integrateOrigFromList': self.integrate_orig_from_items,
                            'ikStretchExtremLoc': self.ik_stretch_extreme_locs,
                            'limbManualVolume': f"{self.ar.data.lang['m019_limb'].lower()}Manual_{self.ar.data.lang['c031_volumeVariation']}",
                            'scalableGrp': self.scalable_grps,
                            'masterCtrlRefList': self.master_ctrl_ref_items,
                            'rootCtrlRefList': self.root_ctrl_ref_items,
                            'softIkCalibrateList': self.soft_ik_calibrate_items,
                            'correctiveCtrlGrpList': self.corrective_ctrl_grps,
                            'addArticJoint': self.articulation,
                            'addCorrective': self.corrective, 
                            'ankleArticList': self.ankle_articulations,
                            'ankleCorrectiveList': self.ankle_correctives
                        }
