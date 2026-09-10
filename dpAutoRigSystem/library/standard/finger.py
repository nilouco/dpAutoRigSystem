from maya import cmds

from ..base import standard

# global variables to this module:
CLASS_NAME = 'Finger'
TITLE = 'm007_finger'
DESCRIPTION = 'm008_fingerDesc'
WIKI = '03-‐-Guides#-finger'



class Finger(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.corrective_ctrl_grps = []


    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.change_joint_number(3)
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.guide_base_joint_loc, self.guide_joint_1_loc, self.guide_loc, self.guide_end_loc], 
                                   ['JointLoc0', 'JointLoc1', 'JointLoc2', 'JointEnd'])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName='nJoints', attributeType='long', minValue=2, defaultValue=2)
        cmds.addAttr(self.guide_base, longName='articulation', defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName='corrective', attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_base_joint_loc = self.ar.ctrls.create_curve_locator(ctrl_name=f"{self.name_guide}_JointLoc0", r=0.2, d=1, guide=True)
        self.guide_joint_1_loc = self.ar.ctrls.create_joint_locator(ctrl_name=f"{self.name_guide}_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_loc = self.ar.ctrls.create_joint_locator(ctrl_name=f"{self.name_guide}_JointLoc2", r=0.25, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=f"{self.name_guide}_JointEnd", r=0.2, d=1, guide=True)
        # joints
        self.line1 = cmds.joint(name=f"{self.name_guide}_JGuide1", radius=0.001)
        self.line0 = cmds.joint(name=f"{self.name_guide}_JGuide0", radius=0.001)
        self.line = cmds.joint(name=f"{self.name_guide}_JGuide2", radius=0.001)
        self.line_end = cmds.joint(name=f"{self.name_guide}_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line0, self.line1, self.line, self.line_end])
        cmds.setAttr(f"{self.guide_base_joint_loc}.translateZ", -1)
        cmds.setAttr(f"{self.guide_base_joint_loc}.rotateZ", lock=True)
        cmds.setAttr(f"{self.guide_loc}.translateZ", 1)
        cmds.setAttr(f"{self.guide_loc}.translateX", -0.01)
        cmds.setAttr(f"{self.guide_loc}.rotateY", -1)
        cmds.setAttr(f"{self.guide_end_loc}.translateZ", 1.3)
        # parenting
        cmds.parent(self.line1, self.guide_base_joint_loc, self.guide_joint_1_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_loc, self.guide_joint_1_loc, relative=True)
        cmds.parent(self.line, self.line_end, self.line1)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        cmds.parentConstraint(self.guide_base_joint_loc, self.line0, maintainOffset=False, name=f"{self.line0}_PaC")
        self.ar.ctrls.direct_connect(self.guide_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_joint_1_loc, self.line1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def set_guide_base_initial_position(self):
        cmds.setAttr(f"{self.guide_base}.rotateX", 90)
        cmds.setAttr(f"{self.guide_base}.rotateZ", 90)


        

    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number >= 2:
            self.ar.opt.check_use_default_render_layer()
            self.current_joint_number = cmds.getAttr(f"{self.guide_base}.nJoints")
            if joint_number != self.current_joint_number:
                self.guide_end_loc = f"{self.name_guide}_JointEnd"
                self.line_end = f"{self.name_guide}_JGuideEnd"
                cmds.parent(self.guide_end_loc, self.line_end, world=True)
                if joint_number > self.current_joint_number:
                    for n in range(self.current_joint_number+1, joint_number+1):
                        self.guide_loc = self.ar.ctrls.create_joint_locator(ctrl_name=f"{self.name_guide}_JointLoc{n}", r=0.2, d=1, guide=True)
                        self.increment_joint_number(n)
                        cmds.setAttr(f"{self.guide_loc}.translateZ", 1)
                        cmds.setAttr(f"{self.guide_loc}.rotateY", -1)
                        self.ar.ctrls.direct_connect(self.guide_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
                        self.add_node_to_guide_net([self.guide_loc], [f"JointLoc{n}"])
                elif joint_number < self.current_joint_number:
                    self.line = f"{self.name_guide}_JGuide{joint_number}"
                    self.guide_loc = self.reduce_joint_number(joint_number)
                cmds.parent(self.guide_end_loc, self.guide_loc)
                cmds.setAttr(f"{self.guide_end_loc}.translateZ", 1.3)
                cmds.parent(self.line_end, self.line)
                cmds.setAttr(f"{self.guide_base}.nJoints", joint_number)
                self.current_joint_number = joint_number
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.change_joint_number(2)


    def get_calibrate_presets(self, s):
        """ Returns the calibration preset and invert lists for finger joints.
        """
        inverts = None
        presets = [{}, {'calibrateTX':1}]
        if s == 1:
           inverts = [[], ['invertTX']]
        return presets, inverts


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declaring lists to send information for integration:
            self.scalable_grps, self.ik_ctrl_zeros = [], []
            # run for all sides
            for s, side in enumerate(self.sides):
                skin_joints, self.controllers = [], []
                self.base = f"{side}{self.number_name}_Guide_Base"
                if self.articulation and self.corrective:
                    # corrective controls group
                    self.corrective_ctrls_grp = cmds.group(name=f"{side}{self.number_name}_Corrective_Grp", empty=True)
                    self.corrective_ctrl_grps.append(self.corrective_ctrls_grp)
                    phalange_calibrate_presets, inverts = self.get_calibrate_presets(s)
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(f"{self.base}.nJoints")
                for n in range(self.n_joints+1):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = f"{side}{self.number_name}_Guide_JointLoc{n}"
                    self.guide_end_loc = f"{side}{self.number_name}_Guide_JointEnd"
                    self.guide_radius = f"{side}{self.number_name}_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=f"{side}{self.number_name}_{n:02d}_Jnt", scaleCompensate=False)
                    skin_joints.append(self.jnt)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.naming.set_joint_label(self.jnt, s+self.joint_label_add, 18, f"{self.number_name}_{n:02d}")
                    # create a control:
                    if n == 1:
                        finger_ctrl = self.ar.ctrls.create_controller('id_015_FingerMain', ctrl_name=f"{side}{self.number_name}_{n:02d}_Ctrl", r=(self.radius * 2.0), d=self.curve_degree, rot=(0, 0, -90), guide_source=f"{self.name_guide}_JointLoc{n}", parent_tag=self.controllers[0])
                        cmds.setAttr(f"{finger_ctrl}.rotateOrder", 1)
                        self.ar.utils.set_origined_from_attr(finger_ctrl, f"{self.base};{self.guide}")   
                        # edit the mirror shape to a good direction of controls:
                        if s == 1:
                            if self.mirror_axis == 'X':
                                cmds.setAttr(f"{finger_ctrl}.rotateZ", 180)
                            elif self.mirror_axis == 'Y':
                                cmds.setAttr(f"{finger_ctrl}.rotateY", 180)
                            elif self.mirror_axis == 'Z':
                                cmds.setAttr(f"{finger_ctrl}.rotateZ", 180)
                            elif self.mirror_axis == 'XY':
                                cmds.setAttr(f"{finger_ctrl}.rotateX", 180)
                            elif self.mirror_axis == 'XYZ':
                                cmds.setAttr(f"{finger_ctrl}.rotateZ", 180)
                            cmds.makeIdentity(finger_ctrl, apply=True, translate=False, rotate=True, scale=False)
                        # scale compensate attribute:
                        if not cmds.objExists(f"{finger_ctrl}.ikFkBlend"):
                            cmds.addAttr(finger_ctrl, longName='ikFkBlend', attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                            ik_fk_rev = cmds.createNode('reverse', name=f"{side}{self.number_name}_ikFk_Rev")
                            self.to_ids.append(ik_fk_rev)
                            cmds.connectAttr(f"{finger_ctrl}.ikFkBlend", f"{ik_fk_rev}.inputX", force=True)
                        if not cmds.objExists(f"{finger_ctrl}.scaleCompensate"):
                            cmds.addAttr(finger_ctrl, longName='scaleCompensate', attributeType='short', minValue=0, defaultValue=1, maxValue=1, keyable=False)
                            cmds.setAttr(f"{finger_ctrl}.scaleCompensate", channelBox=True)
                            scale_compensate_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_{n:02d}_ScaleCompensate_MD")
                            scale_compensate_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_{n:02d}_ScaleCompensate_Cnd")
                            self.to_ids.extend([scale_compensate_md, scale_compensate_cnd])
                            cmds.connectAttr(f"{finger_ctrl}.scaleCompensate", f"{scale_compensate_md}.input1X", force=True)
                            cmds.connectAttr(f"{ik_fk_rev}.outputX", f"{scale_compensate_md}.input2X", force=True)
                            cmds.connectAttr(f"{scale_compensate_md}.outputX", f"{scale_compensate_cnd}.firstTerm", force=True)
                            cmds.setAttr(f"{scale_compensate_cnd}.secondTerm", 1)
                            cmds.setAttr(f"{scale_compensate_cnd}.colorIfFalseR", 0)
                            cmds.connectAttr(f"{finger_ctrl}.scaleCompensate", f"{scale_compensate_cnd}.colorIfTrueR", force=True)
                            cmds.connectAttr(f"{scale_compensate_cnd}.outColorR", f"{self.jnt}.segmentScaleCompensate", force=True)
                            cmds.connectAttr(f"{scale_compensate_cnd}.outColorR", f"{skin_joints[0]}.segmentScaleCompensate", force=True)
                    else:
                        finger_ctrl = self.ar.ctrls.create_controller('id_016_FingerFk', ctrl_name=f"{side}{self.number_name}_{n:02d}_Ctrl", r=self.radius, d=self.curve_degree, guide_source=f"{self.name_guide}_JointLoc{n}", parent_tag=self.get_parent_to_tag(self.controllers))
                        cmds.setAttr(f"{finger_ctrl}.rotateOrder", 1)
                        if n == self.n_joints:
                            self.ar.utils.set_origined_from_attr(finger_ctrl, f"{self.guide};{self.guide_end_loc};{self.guide_radius}")
                        else:
                            self.ar.utils.set_origined_from_attr(finger_ctrl, self.guide)
                        if n == 0:
                            if self.n_joints == 2:
                                # problably we are creating the first control to a thumb
                                cmds.scale(2, 2, 2, finger_ctrl, relative=True)
                                cmds.makeIdentity(finger_ctrl, apply=True)
                            else:
                                # problably we are creating other base controls
                                cmds.scale(2, 0.5, 1, finger_ctrl, relative=True)
                                cmds.makeIdentity(finger_ctrl, apply=True)
                    self.controllers.append(finger_ctrl)

                    # scaleCompensate attribute:
                    if n > 1:
                        cmds.connectAttr(f"{scale_compensate_cnd}.outColorR", f"{self.jnt}.segmentScaleCompensate", force=True)

                    # hide visibility attribute:
                    cmds.setAttr(f"{finger_ctrl}.visibility", keyable=False)
                    # put another group over the control in order to use this to connect values from mainFingerCtrl:
                    pose_grp = cmds.group(finger_ctrl, name=f"{side}{self.number_name}_{n:02d}_Pose_Grp")
                    sdk_grp = cmds.group(pose_grp, name=f"{side}{self.number_name}_{n:02d}_SDK_Grp")
                    self.ar.utils.add_attr_to_items([pose_grp, sdk_grp], self.ar.utils.ignore_transform_io_attr)
                    if n == 1:
                        # change pivot of those groups to control pivot:
                        pivot_position = cmds.xform(finger_ctrl, query=True, worldSpace=True, rotatePivot=True)
                        for grp in [pose_grp, sdk_grp]:
                            cmds.setAttr(f"{grp}.rotatePivotX", pivot_position[0])
                            cmds.setAttr(f"{grp}.rotatePivotY", pivot_position[1])
                            cmds.setAttr(f"{grp}.rotatePivotZ", pivot_position[2])
                    # position and orientation of joint and controller:
                    cmds.matchTransform(self.jnt, sdk_grp, self.guide, position=True, rotation=True)
                    # create_zero_out controls:
                    zero_grp = self.ar.utils.create_zero_out([sdk_grp])
                    
                    # grouping:
                    if n > 0:
                        if n == 1:
                            if not cmds.objExists(f"{finger_ctrl}.{self.ar.data.lang['c021_showControls']}"):
                                cmds.addAttr(finger_ctrl, longName=self.ar.data.lang['c021_showControls'], attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                                ctrl_shape_0 = cmds.listRelatives(f"{side}{self.number_name}_00_Ctrl", children=True, type='nurbsCurve')[0]
                                cmds.connectAttr(f"{finger_ctrl}.{self.ar.data.lang['c021_showControls']}", f"{ctrl_shape_0}.visibility", force=True)
                                cmds.setAttr(f"{finger_ctrl}.{self.ar.data.lang['c021_showControls']}", keyable=False, channelBox=True)
                            for j in range(1, self.n_joints+1):
                                cmds.addAttr(finger_ctrl, longName=f"{self.ar.data.lang['c022_phalange']}{j}", attributeType='float', keyable=True)
                        # parent joints as a simple chain (line)
                        father_joint = f"{side}{self.number_name}_{(n-1):02d}_Jnt"
                        cmds.parent(self.jnt, father_joint, absolute=True)
                        # parent zero_grp Group to the before ctrl:
                        cmds.parent(zero_grp, f"{side}{self.number_name}_{(n-1):02d}_Ctrl", absolute=True)
                    # freeze joints rotation
                    cmds.makeIdentity(self.jnt, apply=True)
                    # create parent and scale constraints from ctrl to jnt:
                    cmds.matchTransform(self.jnt, finger_ctrl, position=True, rotation=True)
                    
                    # add articulationJoint:
                    if n > 0 and self.articulation:
                        if self.corrective:
                            corrective_nets = [None]
                            corrective_nets.append(self.setup_corrective_net(f"{side}{self.number_name}_01_Ctrl", skin_joints[n-1], skin_joints[n], f"{side}{self.number_name}_{n}_PitchDown", 1, 1, -90))
                            articulation_joints = self.ar.utils.create_articulation_joint(father_joint, self.jnt, 1, [(0.3*self.radius, 0, 0)])
                            self.setup_corrective_controllers(articulation_joints, s, f"{self.number_name}_{n}", corrective_nets, phalange_calibrate_presets, inverts)
                            if s == 1:
                                cmds.setAttr(f"{articulation_joints[0]}.scaleX", -1)
                                cmds.setAttr(f"{articulation_joints[0]}.scaleY", -1)
                                cmds.setAttr(f"{articulation_joints[0]}.scaleZ", -1)
                        else:
                            articulation_joints = self.ar.utils.create_articulation_joint(father_joint, self.jnt)
                            cmds.connectAttr(f"{scale_compensate_cnd}.outColorR", f"{articulation_joints[0]}.segmentScaleCompensate", force=True)
                        self.ar.naming.set_joint_label(articulation_joints[0], s+self.joint_label_add, 18, f"{self.number_name}_{n:02d}_Jar")
                    cmds.select(self.jnt)
                    
                    if n == self.n_joints:
                        self.create_end_joint(f"{side}{self.number_name}")
                
                # make first phalange be leads from base finger control:
                cmds.parentConstraint(f"{side}{self.number_name}_00_Ctrl", f"{side}{self.number_name}_01_SDK_Zero_0_Grp", maintainOffset=True, name=f"{side}{self.number_name}_01_SDK_Zero_0_Grp_PaC")
                cmds.scaleConstraint(f"{side}{self.number_name}_00_Ctrl", f"{side}{self.number_name}_01_SDK_Zero_0_Grp", maintainOffset=True, name=f"{side}{self.number_name}_01_SDK_Zero_0_Grp_ScC")
                if self.n_joints != 2:
                    cmds.parentConstraint(f"{side}{self.number_name}_00_Ctrl", f"{side}{self.number_name}_00_Jnt", maintainOffset=True, name=f"{side}{self.number_name}_PaC")
                    cmds.scaleConstraint(f"{side}{self.number_name}_00_Ctrl", f"{side}{self.number_name}_00_Jnt", maintainOffset=True, name=f"{side}{self.number_name}_ScC")
                # connecting the attributes from control 1 to phalanges rotate:
                for n in range(1, self.n_joints+1):
                    finger_ctrl = f"{side}{self.number_name}_01_Ctrl"
                    sdk_grp = f"{side}{self.number_name}_{n:02d}_SDK_Grp"
                    cmds.connectAttr(f"{finger_ctrl}.{self.ar.data.lang['c022_phalange']}{n}", f"{sdk_grp}.rotateY", force=True)
                    if n > 1:
                        ctrl_shape = cmds.listRelatives(f"{side}{self.number_name}_{n:02d}_Ctrl", children=True, type='nurbsCurve')[0]
                        cmds.connectAttr(f"{finger_ctrl}.{self.ar.data.lang['c021_showControls']}", f"{ctrl_shape}.visibility", force=True)

                # ik and Fk setup
                if self.n_joints == 2:
                    dup_ik = cmds.duplicate(skin_joints[0])[0]
                    dup_fk = cmds.duplicate(skin_joints[0])[0]
                else:
                    dup_ik = cmds.duplicate(skin_joints[1])[0]
                    dup_fk = cmds.duplicate(skin_joints[1])[0]
                
                # hide ik and fk joints in order to be Rigger friendly while skinning
                cmds.setAttr(f"{dup_ik}.visibility", 0)
                cmds.setAttr(f"{dup_fk}.visibility", 0)
                
                # ik setup
                for child in cmds.listRelatives(dup_ik, children=True, allDescendents=True, fullPath=True) or []:
                    if cmds.objectType(child) != 'joint':
                        cmds.delete(child)
                    if child.endswith('_Jax'):
                        cmds.delete(child)
                for joint_node in cmds.listRelatives(dup_ik, children=True, allDescendents=True, fullPath=True) or []:
                    if '_Jnt' in joint_node[joint_node.rfind('|'):]:
                        # set joint preferred angle
                        current_ry = cmds.getAttr(f"{joint_node}.rotateY")
                        cmds.setAttr(f"{joint_node}.rotateY", -90)
                        cmds.joint(joint_node, edit=True, setPreferredAngles=True)
                        cmds.setAttr(f"{joint_node}.rotateY", current_ry)
                        cmds.rename(joint_node, joint_node[joint_node.rfind('|')+1:].replace('_Jnt', '_Ik_Jxt'))
                    elif f"_{self.ar.data.joint_end_attr}" in joint_node[joint_node.rfind('|'):]:
                        cmds.rename(joint_node, joint_node[joint_node.rfind('|')+1:].replace(f"_{self.ar.data.joint_end_attr}", f"_Ik_{self.ar.data.joint_end_attr}"))
                ik_base_joint = cmds.rename(dup_ik, dup_ik.replace('_Jnt1', '_Ik_Jxt'))
                ik_joints = cmds.listRelatives(ik_base_joint, children=True, allDescendents=True)
                ik_joints.append(ik_base_joint)

                # Fk setup
                for child in cmds.listRelatives(dup_fk, children=True, allDescendents=True, fullPath=True) or []:
                    if cmds.objectType(child) != 'joint':
                        cmds.delete(child)
                    if child.endswith('_Jax'):
                        cmds.delete(child)
                for joint_node in cmds.listRelatives(dup_fk, children=True, allDescendents=True, fullPath=True) or []:
                    if '_Jnt' in joint_node[joint_node.rfind('|'):]:
                        cmds.rename(joint_node, joint_node[joint_node.rfind('|')+1:].replace('_Jnt', '_Fk_Jxt'))
                    elif f"_{self.ar.data.joint_end_attr}" in joint_node[joint_node.rfind('|'):]:
                        cmds.rename(joint_node, joint_node[joint_node.rfind('|')+1:].replace(f"_{self.ar.data.joint_end_attr}", f"_Fk_{self.ar.data.joint_end_attr}"))
                fk_base_joint = cmds.rename(dup_fk, dup_fk.replace('_Jnt2', '_Fk_Jxt'))
                fk_joints = cmds.listRelatives(fk_base_joint, children=True, allDescendents=True)
                fk_joints.append(fk_base_joint)

                # fk control drives fk joints
                for i, fk_joint in enumerate(fk_joints):
                    if not f"_{self.ar.data.joint_end_attr}" in fk_joint:
                        self.ar.utils.clear_dpar_attr([fk_joint])
                        fk_ctrl = fk_joint.replace('_Fk_Jxt', '_Ctrl')
                        scale_compensate_cnd = fk_ctrl.replace('_Ctrl', '_ScaleCompensate_Cnd')
                        cmds.parentConstraint(fk_ctrl, fk_joint, maintainOffset=True, name=f"{fk_joint}_PaC")
                        cmds.scaleConstraint(fk_ctrl, fk_joint, maintainOffset=True, name=f"{fk_joint}_ScC")
                        cmds.setAttr(f"{fk_joint}.segmentScaleCompensate", 0)
                        cmds.setAttr(f"{fk_ctrl}.rotateOrder", 1)

                # ik handle
                if self.n_joints >= 2:
                    if self.n_joints == 2:
                        ik_handles = cmds.ikHandle(startJoint=f"{side}{self.number_name}_00_Ik_Jxt", endEffector=f"{side}{self.number_name}_{self.n_joints:02d}_Ik_Jxt", solver="ikRPsolver", name=f"{side}{self.number_name}_IKH")
                    else:
                        ik_handles = cmds.ikHandle(startJoint=f"{side}{self.number_name}_01_Ik_Jxt", endEffector=f"{side}{self.number_name}_{self.n_joints:02d}_Ik_Jxt", solver="ikRPsolver", name=f"{side}{self.number_name}_IKH")
                    cmds.rename(ik_handles[1], f"{side}{self.number_name}_Eff")
                    end_ik_handles = cmds.ikHandle(startJoint=f"{side}{self.number_name}_{self.n_joints:02d}_Ik_Jxt", endEffector=f"{side}{self.number_name}_Ik_{self.ar.data.joint_end_attr}", solver="ikSCsolver", name=f"{side}{self.number_name}_EndIkHandle")
                    cmds.rename(end_ik_handles[1], f"{side}{self.number_name}_End_Eff")
                    ik_ctrl = self.ar.ctrls.create_controller('id_017_FingerIk', ctrl_name=f"{side}{self.number_name}_Ik_Ctrl", r=(self.radius * 0.3), d=self.curve_degree, guide_source=f"{self.name_guide}_JointEnd", parent_tag=self.controllers[1])
                    cmds.addAttr(ik_ctrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(f"{ik_ctrl}.twist", f"{ik_handles[0]}.twist", force=True)
                    cmds.setAttr(f"{ik_ctrl}.rotateOrder", 1)
                    self.ik_ctrl_zero = self.ar.utils.create_zero_out([ik_ctrl])[0]
                    self.ik_ctrl_zeros.append(self.ik_ctrl_zero)
                    cmds.matchTransform(self.ik_ctrl_zero, skin_joints[-1], position=True, rotation=True)
                    cmds.delete(cmds.pointConstraint(self.guide_end_loc, self.ik_ctrl_zero, maintainOffset=False))
                    cmds.connectAttr(f"{ik_fk_rev}.outputX", f"{self.ik_ctrl_zero}.visibility", force=True)
                    for q in range(2, self.n_joints+1):
                        cmds.connectAttr(f"{side}{self.number_name}_01_Ctrl.ikFkBlend", f"{side}{self.number_name}_{q:02d}_Ctrl.visibility", force=True)
                    cmds.parentConstraint(ik_ctrl, ik_handles[0], name=f"{side}{self.number_name}_IKH_PaC", maintainOffset=True)
                    cmds.parentConstraint(ik_ctrl, end_ik_handles[0], name=f"{side}{self.number_name}_EndIkHandle_PaC", maintainOffset=True)
                    ik_handle_grp = cmds.group(ik_handles[0], end_ik_handles[0], name=f"{side}{self.number_name}_IKH_Grp")
                    cmds.setAttr(f"{ik_handle_grp}.visibility", 0)
                    self.ar.ctrls.set_lock_hide([ik_ctrl], ['sx', 'sy', 'sz', 'v'])

                    if self.n_joints == 2:
                        cmds.parentConstraint(f"{side}{self.number_name}_00_Ctrl", f"{side}{self.number_name}_00_Ik_Jxt", maintainOffset=True, name=f"{side}{self.number_name}_00_Ik_Jxt_PaC")
                        cmds.scaleConstraint(f"{side}{self.number_name}_00_Ctrl", f"{side}{self.number_name}_00_Ik_Jxt", maintainOffset=True, name=f"{side}{self.number_name}_00_Ik_Jxt_ScC")

                # ik stretch
                cmds.addAttr(ik_ctrl, longName='stretchable', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                stretch_norm_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_StretchNormalize_MD")
                cmds.setAttr(f"{stretch_norm_md}.operation", 2)
                dist_betweens = self.ar.math.create_dist_between(f"{side}{self.number_name}_01_Ctrl", ik_ctrl, name=f"{side}{self.number_name}_DistBet", keep=True)
                cmds.connectAttr(f"{ik_fk_rev}.outputX", f"{dist_betweens[5]}.{ik_ctrl}W0", force=True)
                cmds.connectAttr(f"{finger_ctrl}.ikFkBlend", f"{dist_betweens[5]}.{dist_betweens[4]}W1", force=True)
                cmds.connectAttr(f"{dist_betweens[1]}.distance", f"{stretch_norm_md}.input1X", force=True)
                # TO DO? stretch compensate to ik Z axis
                ik_stretch_z_uniform_scale_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_IkStretchZ_MD")
                cmds.setAttr(f"{ik_stretch_z_uniform_scale_md}.input2X", dist_betweens[0])
                cmds.connectAttr(f"{skin_joints[0]}.scaleZ", f"{ik_stretch_z_uniform_scale_md}.input1X", force=True)
                cmds.connectAttr(f"{ik_stretch_z_uniform_scale_md}.outputX", f"{stretch_norm_md}.input2X", force=True)
                stretch_scale_md = cmds.createNode('multiplyDivide', name=f"{side}{self.number_name}_StretchScale_MD")
                cmds.connectAttr(f"{stretch_norm_md}.outputX", f"{stretch_scale_md}.input1X", force=True)
                cmds.connectAttr(f"{ik_ctrl}.stretchable", f"{stretch_scale_md}.input2X", force=True)
                stretch_cnd = cmds.createNode('condition', name=f"{side}{self.number_name}_Stretch_Cnd")
                cmds.connectAttr(f"{stretch_scale_md}.outputX", f"{stretch_cnd}.firstTerm", force=True)
                cmds.setAttr(f"{stretch_cnd}.secondTerm", 1)
                cmds.setAttr(f"{stretch_cnd}.operation", 2)
                cmds.connectAttr(f"{stretch_scale_md}.outputX", f"{stretch_cnd}.colorIfTrueR", force=True)
                self.to_ids.extend([stretch_norm_md, ik_stretch_z_uniform_scale_md, stretch_scale_md, stretch_cnd])

                # ik fk blend connnections
                for i, ik_joint in enumerate(ik_joints):
                    if not f"_{self.ar.data.joint_end_attr}" in ik_joint:
                        self.ar.utils.clear_dpar_attr([ik_joint])
                        fk_joint = ik_joint.replace('_Ik_Jxt', '_Fk_Jxt')
                        skin_joint = ik_joint.replace('_Ik_Jxt', '_Jnt')
                        finger_ctrl = f"{side}{self.number_name}_01_Ctrl"
                        scale_compensate_cnd = ik_joint.replace('_Ik_Jxt', '_ScaleCompensate_Cnd')
                        ik_fk_pac = cmds.parentConstraint(ik_joint, fk_joint, skin_joint, maintainOffset=True, name=f"{skin_joint}_PaC")[0]
                        cmds.connectAttr(f"{finger_ctrl}.ikFkBlend", f"{ik_fk_pac}.{fk_joint}W1", force=True)
                        cmds.connectAttr(f"{ik_fk_rev}.outputX", f"{ik_fk_pac}.{ik_joint}W0", force=True)
                        scale_bc = cmds.createNode('blendColors', name=f"{skin_joint}_BC")
                        self.to_ids.append(scale_bc)
                        cmds.connectAttr(f"{fk_joint}.scaleX", f"{scale_bc}.color1R", force=True)
                        cmds.connectAttr(f"{fk_joint}.scaleY", f"{scale_bc}.color1G", force=True)
                        cmds.connectAttr(f"{fk_joint}.scaleZ", f"{scale_bc}.color1B", force=True)
                        cmds.connectAttr(f"{ik_joint}.scaleX", f"{scale_bc}.color2R", force=True)
                        cmds.connectAttr(f"{ik_joint}.scaleY", f"{scale_bc}.color2G", force=True)
                        cmds.connectAttr(f"{ik_joint}.scaleZ", f"{scale_bc}.color2B", force=True)
                        if self.n_joints == 2:
                            if not '00_Ik_Jxt' in ik_joint: # to avoid thumb cycle error about the stretch
                                cmds.connectAttr(f"{stretch_cnd}.outColorR", f"{ik_joint}.scaleZ", force=True)
                        else:
                            cmds.connectAttr(f"{stretch_cnd}.outColorR", f"{ik_joint}.scaleZ", force=True)
                        cmds.connectAttr(f"{finger_ctrl}.ikFkBlend", f"{scale_bc}.blender", force=True)
                        cmds.connectAttr(f"{scale_bc}.output.outputR", f"{skin_joint}.scaleX", force=True)
                        cmds.connectAttr(f"{scale_bc}.output.outputG", f"{skin_joint}.scaleY", force=True)
                        cmds.connectAttr(f"{scale_bc}.output.outputB", f"{skin_joint}.scaleZ", force=True)
                        cmds.setAttr(f"{ik_joint}.segmentScaleCompensate", 1)
                        if '01_Ik_Jxt' in ik_joint and self.n_joints != 2: # to avoid thumb cycle error when parenting All_Grp transform node
                            cmds.pointConstraint(finger_ctrl, ik_joint, maintainOffset=True, name=f"{ik_joint}_PoC")
                        if self.n_joints > 2 and i > 0:
                            # fix ik scale
                            cmds.connectAttr(f"{skin_joints[0]}.scaleX", f"{ik_joint}.scaleX", force=True)
                            cmds.connectAttr(f"{skin_joints[0]}.scaleY", f"{ik_joint}.scaleY", force=True)
                # create a masterModuleGrp to be checked if this rig exists:
                ctrl_hooks = [f"{side}{self.number_name}_00_SDK_Zero_0_Grp", f"{side}{self.number_name}_01_SDK_Zero_0_Grp"]
                if self.n_joints >= 2:
                    if self.n_joints == 2:
                        scalable_hooks = [skin_joints[0], ik_base_joint, fk_base_joint, ik_handle_grp, dist_betweens[2], dist_betweens[3], dist_betweens[4]]
                    else:
                        scalable_hooks = [skin_joints[0], ik_handle_grp, dist_betweens[2], dist_betweens[3], dist_betweens[4]]
                else:
                    ctrl_hooks.append(self.ik_ctrl_zero)
                    scalable_hooks = [f"{side}{self.number_name}_00_Jnt"]
                self.create_hook_setup(side, ctrl_hooks, scalable_hooks)
                if self.corrective:
                    cmds.parent(self.corrective_ctrls_grp, self.ctrl_hook_grp)
                self.scalable_grps.append(self.scalable_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(f"{side}{self.number_name}_{self.mirror_grp}")
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
                            'scalableGrpList': self.scalable_grps,
                            'ikCtrlZeroList': self.ik_ctrl_zeros,
                            'correctiveCtrlGrpList': self.corrective_ctrl_grps
                        }
