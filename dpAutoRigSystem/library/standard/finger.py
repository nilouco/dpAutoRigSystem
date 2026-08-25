# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "Finger"
TITLE = "m007_finger"
DESCRIPTION = "m008_fingerDesc"
WIKI = "03-‐-Guides#-finger"



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
                                   ["JointLoc0", "JointLoc1", "JointLoc2", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", attributeType='long', minValue=2, defaultValue=2)
        cmds.addAttr(self.guide_base, longName="articulation", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="corrective", attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_base_joint_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_JointLoc0", r=0.2, d=1, guide=True)
        self.guide_joint_1_loc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_loc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_JointLoc2", r=0.25, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_JointEnd", r=0.2, d=1, guide=True)
        # joints
        self.line1 = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.line0 = cmds.joint(name=self.name_guide+"_JGuide0", radius=0.001)
        self.line = cmds.joint(name=self.name_guide+"_JGuide2", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line0, self.line, self.line, self.line_end])
        cmds.setAttr(self.guide_base_joint_loc+".translateZ", -1)
        cmds.setAttr(self.guide_base_joint_loc+".rotateZ", lock=True)
        cmds.setAttr(self.guide_loc+".translateZ", 1)
        cmds.setAttr(self.guide_loc+".translateX", -0.01)
        cmds.setAttr(self.guide_loc+".rotateY", -1)
        cmds.setAttr(self.guide_end_loc+".translateZ", 1.3)
        # parenting
        cmds.parent(self.line1, self.guide_base_joint_loc, self.guide_joint_1_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_loc, self.guide_joint_1_loc, relative=True)
        cmds.parent(self.line, self.line_end, self.line1)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        cmds.parentConstraint(self.guide_base_joint_loc, self.line0, maintainOffset=False, name=self.line0+"_PaC")
        self.ar.ctrls.directConnect(self.guide_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_joint_1_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.setLockHide([self.guide_end_loc], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".rotateX", 90)
        cmds.setAttr(self.guide_base+".rotateZ", 90)


        

    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number >= 2:
            self.ar.opt.check_use_default_render_layer()
            self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
            if joint_number != self.current_joint_number:
                self.guide_end_loc = self.name_guide+"_JointEnd"
                self.line_end = self.name_guide+"_JGuideEnd"
                cmds.parent(self.guide_end_loc, self.line_end, world=True)
                if joint_number > self.current_joint_number:
                    for n in range(self.current_joint_number+1, joint_number+1):
                        self.guide_loc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_JointLoc"+str(n), r=0.2, d=1, guide=True)
                        self.increment_joint_number(n)
                        cmds.setAttr(self.guide_loc+".translateZ", 1)
                        cmds.setAttr(self.guide_loc+".rotateY", -1)
                        self.ar.ctrls.directConnect(self.guide_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
                        self.add_node_to_guide_net([self.guide_loc], ["JointLoc"+str(n)])
                elif joint_number < self.current_joint_number:
                    self.line = self.name_guide+"_JGuide"+str(joint_number)
                    self.guide_loc = self.reduce_joint_number(joint_number)
                cmds.parent(self.guide_end_loc, self.guide_loc)
                cmds.setAttr(self.guide_end_loc+".tz", 1.3)
                cmds.parent(self.line_end, self.line)
                cmds.setAttr(self.guide_base+".nJoints", joint_number)
                self.current_joint_number = joint_number
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.change_joint_number(2)


    def get_calibrate_presets(self, s):
        """ Returns the calibration preset and invert lists for finger joints.
        """
        inverts = None
        presets = [{}, {"calibrateTX":1}]
        if s == 1:
           inverts = [[], ["invertTX"]]
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
                self.base = side+self.number_name+'_Guide_Base'
                if self.articulation:
                    if self.corrective:
                        # corrective controls group
                        self.corrective_ctrls_grp = cmds.group(name=side+self.number_name+"_Corrective_Grp", empty=True)
                        self.corrective_ctrl_grps.append(self.corrective_ctrls_grp)
                        phalange_calibrate_presets, inverts = self.get_calibrate_presets(s)
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.n_joints+1):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.number_name+"_Guide_JointLoc"+str(n)
                    self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                    self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.number_name+"_%02d_Jnt"%(n), scaleCompensate=False)
                    skin_joints.append(self.jnt)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_%02d"%(n))
                    # create a control:
                    if n == 1:
                        finger_ctrl = self.ar.ctrls.cvControl("id_015_FingerMain", ctrl_name=side+self.number_name+"_%02d_Ctrl"%(n), r=(self.radius * 2.0), d=self.curve_degree, rot=(0, 0, -90), guideSource=self.name_guide+"_JointLoc"+str(n), parentTag=self.controllers[0])
                        cmds.setAttr(finger_ctrl+".rotateOrder", 1)
                        self.ar.utils.originedFrom(objName=finger_ctrl, attrString=self.base+";"+self.guide)   
                        # edit the mirror shape to a good direction of controls:
                        if s == 1:
                            if self.mirror_axis == 'X':
                                cmds.setAttr(finger_ctrl+'.rotateZ', 180)
                            elif self.mirror_axis == 'Y':
                                cmds.setAttr(finger_ctrl+'.rotateY', 180)
                            elif self.mirror_axis == 'Z':
                                cmds.setAttr(finger_ctrl+'.rotateZ', 180)
                            elif self.mirror_axis == 'XY':
                                cmds.setAttr(finger_ctrl+'.rotateX', 180)
                            elif self.mirror_axis == 'XYZ':
                                cmds.setAttr(finger_ctrl+'.rotateZ', 180)
                            cmds.makeIdentity(finger_ctrl, apply=True, translate=False, rotate=True, scale=False)
                        # scale compensate attribute:
                        if not cmds.objExists(finger_ctrl+'.ikFkBlend'):
                            cmds.addAttr(finger_ctrl, longName="ikFkBlend", attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                            ik_fk_rev = cmds.createNode("reverse", name=side+self.number_name+"_ikFk_Rev")
                            self.to_ids.append(ik_fk_rev)
                            cmds.connectAttr(finger_ctrl+".ikFkBlend", ik_fk_rev+".inputX", force=True)
                        if not cmds.objExists(finger_ctrl+'.scaleCompensate'):
                            cmds.addAttr(finger_ctrl, longName="scaleCompensate", attributeType='short', minValue=0, defaultValue=1, maxValue=1, keyable=False)
                            cmds.setAttr(finger_ctrl+".scaleCompensate", channelBox=True)
                            scale_compensate_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_%02d_ScaleCompensate_MD"%(n))
                            scale_compensate_cnd = cmds.createNode("condition", name=side+self.number_name+"_%02d_ScaleCompensate_Cnd"%(n))
                            self.to_ids.extend([scale_compensate_md, scale_compensate_cnd])
                            cmds.connectAttr(finger_ctrl+".scaleCompensate", scale_compensate_md+".input1X", force=True)
                            cmds.connectAttr(ik_fk_rev+".outputX", scale_compensate_md+".input2X", force=True)
                            cmds.connectAttr(scale_compensate_md+".outputX", scale_compensate_cnd+".firstTerm", force=True)
                            cmds.setAttr(scale_compensate_cnd+".secondTerm", 1)
                            cmds.setAttr(scale_compensate_cnd+".colorIfFalseR", 0)
                            cmds.connectAttr(finger_ctrl+".scaleCompensate", scale_compensate_cnd+".colorIfTrueR", force=True)
                            cmds.connectAttr(scale_compensate_cnd+".outColorR", self.jnt+".segmentScaleCompensate", force=True)
                            cmds.connectAttr(scale_compensate_cnd+".outColorR", skin_joints[0]+".segmentScaleCompensate", force=True)
                    else:
                        finger_ctrl = self.ar.ctrls.cvControl("id_016_FingerFk", ctrl_name=side+self.number_name+"_%02d_Ctrl"%(n), r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+str(n), parentTag=self.get_parent_to_tag(self.controllers))
                        cmds.setAttr(finger_ctrl+".rotateOrder", 1)
                        if n == self.n_joints:
                            self.ar.utils.originedFrom(objName=finger_ctrl, attrString=self.guide+";"+self.guide_end_loc+";"+self.guide_radius)
                        else:
                            self.ar.utils.originedFrom(objName=finger_ctrl, attrString=self.guide)
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
                        cmds.connectAttr(scale_compensate_cnd+".outColorR", self.jnt+".segmentScaleCompensate", force=True)

                    # hide visibility attribute:
                    cmds.setAttr(finger_ctrl+'.visibility', keyable=False)
                    # put another group over the control in order to use this to connect values from mainFingerCtrl:
                    pose_grp = cmds.group(finger_ctrl, name=side+self.number_name+"_%02d_Pose_Grp"%(n))
                    sdk_grp = cmds.group(pose_grp, name=side+self.number_name+"_%02d_SDK_Grp"%(n))
                    self.ar.utils.addCustomAttr([pose_grp, sdk_grp], self.ar.utils.ignoreTransformIOAttr)
                    if n == 1:
                        # change pivot of those groups to control pivot:
                        pivot_position = cmds.xform(finger_ctrl, query=True, worldSpace=True, rotatePivot=True)
                        for grp in [pose_grp, sdk_grp]:
                            cmds.setAttr(grp+'.rotatePivotX', pivot_position[0])
                            cmds.setAttr(grp+'.rotatePivotY', pivot_position[1])
                            cmds.setAttr(grp+'.rotatePivotZ', pivot_position[2])
                    # position and orientation of joint and controller:
                    cmds.matchTransform(self.jnt, sdk_grp, self.guide, position=True, rotation=True)
                    # zeroOut controls:
                    zero_grp = self.ar.utils.zeroOut([sdk_grp])
                    
                    # grouping:
                    if n > 0:
                        if n == 1:
                            if not cmds.objExists(finger_ctrl+'.'+self.ar.data.lang['c021_showControls']):
                                cmds.addAttr(finger_ctrl, longName=self.ar.data.lang['c021_showControls'], attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                                ctrl_shape_0 = cmds.listRelatives(side+self.number_name+"_00_Ctrl", children=True, type='nurbsCurve')[0]
                                cmds.connectAttr(finger_ctrl+"."+self.ar.data.lang['c021_showControls'], ctrl_shape_0+".visibility", force=True)
                                cmds.setAttr(finger_ctrl+'.'+self.ar.data.lang['c021_showControls'], keyable=False, channelBox=True)
                            for j in range(1, self.n_joints+1):
                                cmds.addAttr(finger_ctrl, longName=self.ar.data.lang['c022_phalange']+str(j), attributeType='float', keyable=True)
                        # parent joints as a simple chain (line)
                        father_joint = side+self.number_name+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, father_joint, absolute=True)
                        # parent zero_grp Group to the before ctrl:
                        cmds.parent(zero_grp, side+self.number_name+"_%02d_Ctrl"%(n-1), absolute=True)
                    # freeze joints rotation
                    cmds.makeIdentity(self.jnt, apply=True)
                    # create parent and scale constraints from ctrl to jnt:
                    cmds.matchTransform(self.jnt, finger_ctrl, position=True, rotation=True)
                    
                    # add articulationJoint:
                    if n > 0:
                        if self.articulation:
                            if self.corrective:
                                corrective_nets = [None]
                                corrective_nets.append(self.setup_corrective_net(side+self.number_name+"_01_Ctrl", skin_joints[n-1], skin_joints[n], side+self.number_name+"_"+str(n)+"_PitchDown", 1, 1, -90))
                                articulation_joints = self.ar.utils.articulationJoint(father_joint, self.jnt, 1, [(0.3*self.radius, 0, 0)])
                                self.setup_corrective_controllers(articulation_joints, s, self.number_name+"_"+str(n), corrective_nets, phalange_calibrate_presets, inverts)
                                if s == 1:
                                    cmds.setAttr(articulation_joints[0]+".scaleX", -1)
                                    cmds.setAttr(articulation_joints[0]+".scaleY", -1)
                                    cmds.setAttr(articulation_joints[0]+".scaleZ", -1)
                            else:
                                articulation_joints = self.ar.utils.articulationJoint(father_joint, self.jnt)
                                cmds.connectAttr(scale_compensate_cnd+".outColorR", articulation_joints[0]+".segmentScaleCompensate", force=True)
                            self.ar.utils.setJointLabel(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                    
                    if n == self.n_joints:
                        self.create_end_joint(side+self.number_name)
                
                # make first phalange be leads from base finger control:
                cmds.parentConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.number_name+"_01_SDK_Zero_0_Grp"+"_PaC")
                cmds.scaleConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.number_name+"_01_SDK_Zero_0_Grp"+"_ScC")
                if self.n_joints != 2:
                    cmds.parentConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Jnt", maintainOffset=True, name=side+self.number_name+"_PaC")
                    cmds.scaleConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Jnt", maintainOffset=True, name=side+self.number_name+"_ScC")
                # connecting the attributes from control 1 to phalanges rotate:
                for n in range(1, self.n_joints+1):
                    finger_ctrl = side+self.number_name+"_01_Ctrl"
                    sdk_grp = side+self.number_name+"_%02d_SDK_Grp"%(n)
                    cmds.connectAttr(finger_ctrl+"."+self.ar.data.lang['c022_phalange']+str(n), sdk_grp+".rotateY", force=True)
                    if n > 1:
                        ctrl_shape = cmds.listRelatives(side+self.number_name+"_%02d_Ctrl"%(n), children=True, type='nurbsCurve')[0]
                        cmds.connectAttr(finger_ctrl+"."+self.ar.data.lang['c021_showControls'], ctrl_shape+".visibility", force=True)

                # ik and Fk setup
                if self.n_joints == 2:
                    dup_ik = cmds.duplicate(skin_joints[0])[0]
                    dup_fk = cmds.duplicate(skin_joints[0])[0]
                else:
                    dup_ik = cmds.duplicate(skin_joints[1])[0]
                    dup_fk = cmds.duplicate(skin_joints[1])[0]
                
                # hide ik and fk joints in order to be Rigger friendly while skinning
                cmds.setAttr(dup_ik+".visibility", 0)
                cmds.setAttr(dup_fk+".visibility", 0)
                
                # ik setup
                for child in cmds.listRelatives(dup_ik, children=True, allDescendents=True, fullPath=True) or []:
                    if not cmds.objectType(child) == "joint":
                        cmds.delete(child)
                    if child.endswith("_Jax"):
                        cmds.delete(child)
                for joint_node in cmds.listRelatives(dup_ik, children=True, allDescendents=True, fullPath=True) or []:
                    if "_Jnt" in joint_node[joint_node.rfind("|"):]:
                        # set joint preferred angle
                        current_ry = cmds.getAttr(joint_node+".rotateY")
                        cmds.setAttr(joint_node+".rotateY", -90)
                        cmds.joint(joint_node, edit=True, setPreferredAngles=True)
                        cmds.setAttr(joint_node+".rotateY", current_ry)
                        cmds.rename(joint_node, joint_node[joint_node.rfind("|")+1:].replace("_Jnt", "_Ik_Jxt"))
                    elif "_"+self.ar.data.joint_end_attr in joint_node[joint_node.rfind("|"):]:
                        cmds.rename(joint_node, joint_node[joint_node.rfind("|")+1:].replace("_"+self.ar.data.joint_end_attr, "_Ik_"+self.ar.data.joint_end_attr))
                ik_base_joint = cmds.rename(dup_ik, dup_ik.replace("_Jnt1", "_Ik_Jxt"))
                ik_joints = cmds.listRelatives(ik_base_joint, children=True, allDescendents=True)
                ik_joints.append(ik_base_joint)

                # Fk setup
                for child in cmds.listRelatives(dup_fk, children=True, allDescendents=True, fullPath=True) or []:
                    if not cmds.objectType(child) == "joint":
                        cmds.delete(child)
                    if child.endswith("_Jax"):
                        cmds.delete(child)
                for joint_node in cmds.listRelatives(dup_fk, children=True, allDescendents=True, fullPath=True) or []:
                    if "_Jnt" in joint_node[joint_node.rfind("|"):]:
                        cmds.rename(joint_node, joint_node[joint_node.rfind("|")+1:].replace("_Jnt", "_Fk_Jxt"))
                    elif "_"+self.ar.data.joint_end_attr in joint_node[joint_node.rfind("|"):]:
                        cmds.rename(joint_node, joint_node[joint_node.rfind("|")+1:].replace("_"+self.ar.data.joint_end_attr, "_Fk_"+self.ar.data.joint_end_attr))
                fk_base_joint = cmds.rename(dup_fk, dup_fk.replace("_Jnt2", "_Fk_Jxt"))
                fk_joints = cmds.listRelatives(fk_base_joint, children=True, allDescendents=True)
                fk_joints.append(fk_base_joint)

                # fk control drives fk joints
                for i, fk_joint in enumerate(fk_joints):
                    if not "_"+self.ar.data.joint_end_attr in fk_joint:
                        self.ar.utils.clearDpArAttr([fk_joint])
                        fk_ctrl = fk_joint.replace("_Fk_Jxt", "_Ctrl")
                        scale_compensate_cnd = fk_ctrl.replace("_Ctrl", "_ScaleCompensate_Cnd")
                        cmds.parentConstraint(fk_ctrl, fk_joint, maintainOffset=True, name=fk_joint+"_PaC")
                        cmds.scaleConstraint(fk_ctrl, fk_joint, maintainOffset=True, name=fk_joint+"_ScC")
                        cmds.setAttr(fk_joint+".segmentScaleCompensate", 0)
                        cmds.setAttr(fk_ctrl+".rotateOrder", 1)

                # ik handle
                if self.n_joints >= 2:
                    if self.n_joints == 2:
                        ik_handles = cmds.ikHandle(startJoint=side+self.number_name+"_00_Ik_Jxt", endEffector=side+self.number_name+"_%02d_Ik_Jxt"%(self.n_joints), solver="ikRPsolver", name=side+self.number_name+"_IKH")
                    else:
                        ik_handles = cmds.ikHandle(startJoint=side+self.number_name+"_01_Ik_Jxt", endEffector=side+self.number_name+"_%02d_Ik_Jxt"%(self.n_joints), solver="ikRPsolver", name=side+self.number_name+"_IKH")
                    cmds.rename(ik_handles[1], side+self.number_name+"_Eff")
                    end_ik_handles = cmds.ikHandle(startJoint=side+self.number_name+"_%02d_Ik_Jxt"%(self.n_joints), endEffector=side+self.number_name+"_Ik_"+self.ar.data.joint_end_attr, solver="ikSCsolver", name=side+self.number_name+"_EndIkHandle")
                    cmds.rename(end_ik_handles[1], side+self.number_name+"_End_Eff")
                    ik_ctrl = self.ar.ctrls.cvControl("id_017_FingerIk", ctrl_name=side+self.number_name+"_Ik_Ctrl", r=(self.radius * 0.3), d=self.curve_degree, guideSource=self.name_guide+"_JointEnd", parentTag=self.controllers[1])
                    cmds.addAttr(ik_ctrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(ik_ctrl+".twist", ik_handles[0]+".twist", force=True)
                    cmds.setAttr(ik_ctrl+".rotateOrder", 1)
                    self.ik_ctrl_zero = self.ar.utils.zeroOut([ik_ctrl])[0]
                    self.ik_ctrl_zeros.append(self.ik_ctrl_zero)
                    cmds.matchTransform(self.ik_ctrl_zero, skin_joints[-1], position=True, rotation=True)
                    cmds.delete(cmds.pointConstraint(self.guide_end_loc, self.ik_ctrl_zero, maintainOffset=False))
                    cmds.connectAttr(ik_fk_rev+".outputX", self.ik_ctrl_zero+".visibility", force=True)
                    for q in range(2, self.n_joints+1):
                        cmds.connectAttr(side+self.number_name+"_01_Ctrl.ikFkBlend", side+self.number_name+"_%02d_Ctrl.visibility"%(q), force=True)
                    cmds.parentConstraint(ik_ctrl, ik_handles[0], name=side+self.number_name+"_IKH_PaC", maintainOffset=True)
                    cmds.parentConstraint(ik_ctrl, end_ik_handles[0], name=side+self.number_name+"_EndIkHandle_PaC", maintainOffset=True)
                    ik_handle_grp = cmds.group(ik_handles[0], end_ik_handles[0], name=side+self.number_name+"_IKH_Grp")
                    cmds.setAttr(ik_handle_grp+".visibility", 0)
                    self.ar.ctrls.setLockHide([ik_ctrl], ['sx', 'sy', 'sz', 'v'])

                    if self.n_joints == 2:
                        cmds.parentConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Ik_Jxt", maintainOffset=True, name=side+self.number_name+"_00_Ik_Jxt_PaC")
                        cmds.scaleConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Ik_Jxt", maintainOffset=True, name=side+self.number_name+"_00_Ik_Jxt_ScC")

                # ik stretch
                cmds.addAttr(ik_ctrl, longName='stretchable', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                stretch_norm_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_StretchNormalize_MD")
                cmds.setAttr(stretch_norm_md+".operation", 2)
                dist_betweens = self.ar.utils.distanceBet(side+self.number_name+"_01_Ctrl", ik_ctrl, name=side+self.number_name+"_DistBet", keep=True)
                cmds.connectAttr(ik_fk_rev+".outputX", dist_betweens[5]+"."+ik_ctrl+"W0", force=True)
                cmds.connectAttr(finger_ctrl+".ikFkBlend", dist_betweens[5]+"."+dist_betweens[4]+"W1", force=True)
                cmds.connectAttr(dist_betweens[1]+".distance", stretch_norm_md+".input1X", force=True)
                # TO DO? stretch compensate to ik Z axis
                ik_stretch_z_uniform_scale_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_IkStretchZ_MD")
                cmds.setAttr(ik_stretch_z_uniform_scale_md+".input2X", dist_betweens[0])
                cmds.connectAttr(skin_joints[0]+".scaleZ", ik_stretch_z_uniform_scale_md+".input1X", force=True)
                cmds.connectAttr(ik_stretch_z_uniform_scale_md+".outputX", stretch_norm_md+".input2X", force=True)
                stretch_scale_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_StretchScale_MD")
                cmds.connectAttr(stretch_norm_md+".outputX", stretch_scale_md+".input1X", force=True)
                cmds.connectAttr(ik_ctrl+".stretchable", stretch_scale_md+".input2X", force=True)
                stretch_cnd = cmds.createNode("condition", name=side+self.number_name+"_Stretch_Cnd")
                cmds.connectAttr(stretch_scale_md+".outputX", stretch_cnd+".firstTerm", force=True)
                cmds.setAttr(stretch_cnd+".secondTerm", 1)
                cmds.setAttr(stretch_cnd+".operation", 2)
                cmds.connectAttr(stretch_scale_md+".outputX", stretch_cnd+".colorIfTrueR", force=True)
                self.to_ids.extend([stretch_norm_md, ik_stretch_z_uniform_scale_md, stretch_scale_md, stretch_cnd])

                # ik fk blend connnections
                for i, ik_joint in enumerate(ik_joints):
                    if not "_"+self.ar.data.joint_end_attr in ik_joint:
                        self.ar.utils.clearDpArAttr([ik_joint])
                        fk_joint = ik_joint.replace("_Ik_Jxt", "_Fk_Jxt")
                        skin_joint = ik_joint.replace("_Ik_Jxt", "_Jnt")
                        finger_ctrl = side+self.number_name+"_01_Ctrl"
                        scale_compensate_cnd = ik_joint.replace("_Ik_Jxt", "_ScaleCompensate_Cnd")
                        ik_fk_pac = cmds.parentConstraint(ik_joint, fk_joint, skin_joint, maintainOffset=True, name=skin_joint+"_PaC")[0]
                        cmds.connectAttr(finger_ctrl+".ikFkBlend", ik_fk_pac+"."+fk_joint+"W1", force=True)
                        cmds.connectAttr(ik_fk_rev+".outputX", ik_fk_pac+"."+ik_joint+"W0", force=True)
                        scale_bc = cmds.createNode("blendColors", name=skin_joint+"_BC")
                        self.to_ids.append(scale_bc)
                        cmds.connectAttr(fk_joint+".scaleX", scale_bc+".color1R", force=True)
                        cmds.connectAttr(fk_joint+".scaleY", scale_bc+".color1G", force=True)
                        cmds.connectAttr(fk_joint+".scaleZ", scale_bc+".color1B", force=True)
                        cmds.connectAttr(ik_joint+".scaleX", scale_bc+".color2R", force=True)
                        cmds.connectAttr(ik_joint+".scaleY", scale_bc+".color2G", force=True)
                        cmds.connectAttr(ik_joint+".scaleZ", scale_bc+".color2B", force=True)
                        if self.n_joints == 2:
                            if not "00_Ik_Jxt" in ik_joint: # to avoid thumb cycle error about the stretch
                                cmds.connectAttr(stretch_cnd+".outColorR", ik_joint+".scaleZ", force=True)
                        else:
                            cmds.connectAttr(stretch_cnd+".outColorR", ik_joint+".scaleZ", force=True)
                        cmds.connectAttr(finger_ctrl+".ikFkBlend", scale_bc+".blender", force=True)
                        cmds.connectAttr(scale_bc+".output.outputR", skin_joint+".scaleX", force=True)
                        cmds.connectAttr(scale_bc+".output.outputG", skin_joint+".scaleY", force=True)
                        cmds.connectAttr(scale_bc+".output.outputB", skin_joint+".scaleZ", force=True)
                        cmds.setAttr(ik_joint+".segmentScaleCompensate", 1)
                        if "01_Ik_Jxt" in ik_joint:
                            if not self.n_joints == 2: # to avoid thumb cycle error when parenting All_Grp transform node
                                cmds.pointConstraint(finger_ctrl, ik_joint, maintainOffset=True, name=ik_joint+"_PoC")
                        if self.n_joints > 2:
                            if i > 0:
                                # fix ik scale
                                cmds.connectAttr(skin_joints[0]+".scaleX", ik_joints[i]+".scaleX", force=True)
                                cmds.connectAttr(skin_joints[0]+".scaleY", ik_joints[i]+".scaleY", force=True)
                # create a masterModuleGrp to be checked if this rig exists:
                ctrl_hooks = [side+self.number_name+"_00_SDK_Zero_0_Grp", side+self.number_name+"_01_SDK_Zero_0_Grp"]
                if self.n_joints >= 2:
                    if self.n_joints == 2:
                        scalable_hooks = [skin_joints[0], ik_base_joint, fk_base_joint, ik_handle_grp, dist_betweens[2], dist_betweens[3], dist_betweens[4]]
                    else:
                        scalable_hooks = [skin_joints[0], ik_handle_grp, dist_betweens[2], dist_betweens[3], dist_betweens[4]]
                else:
                    ctrl_hooks.append(self.ik_ctrl_zero)
                    scalable_hooks = [side+self.number_name+"_00_Jnt"]
                self.create_hook_setup(side, ctrl_hooks, scalable_hooks)
                if self.corrective:
                    cmds.parent(self.corrective_ctrls_grp, self.ctrl_hook_grp)
                self.scalable_grps.append(self.scalable_hook_grp)
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
                            "scalableGrpList": self.scalable_grps,
                            "ikCtrlZeroList": self.ik_ctrl_zeros,
                            "correctiveCtrlGrpList": self.corrective_ctrl_grps
                        }
