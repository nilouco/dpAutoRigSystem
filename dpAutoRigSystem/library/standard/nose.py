# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "Nose"
TITLE = "m078_nose"
DESCRIPTION = "m176_noseDesc"
WIKI = "03-‐-Guides#-nose"



class Nose(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.guide_left_nostril_loc = self.name_guide+"_cvLNostrilLoc"
        self.guide_right_nostril_loc = self.name_guide+"_cvRNostrilLoc"
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.create_guide_nose_side("Side", self.guide_left_side_loc, self.guide_right_side_loc)
        self.create_guide_nose_side("Nostril", self.guide_left_nostril_loc, self.guide_right_nostril_loc)
        self.add_node_to_guide_net([self.guide_top_loc, self.guide_middle_loc, self.guide_tip_loc, self.guide_left_side_loc, self.guide_right_side_loc, self.guide_left_nostril_loc, self.guide_bottom_loc, self.guide_end_loc], 
                                   ["cvTopLoc1", "guide_middle_loc", "guide_tip_loc", "guide_left_side_loc", "guide_right_side_loc", "guide_left_nostril_loc", "guide_bottom_loc", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", defaultValue=1, attributeType='long')
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="articulation", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="nostril", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=1, maxValue=3, attributeType='long')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_top_loc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_cvTopLoc1", r=0.3, d=1, guide=True)
        self.guide_middle_loc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_cvMiddleLoc", r=0.2, d=1, guide=True)
        self.guide_tip_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvTipLoc", r=0.1, d=1, guide=True)
        self.guide_left_side_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvLSideLoc", r=0.15, d=1, guide=True)
        self.guide_right_side_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvRSideLoc", r=0.15, d=1, guide=True)
        self.guide_left_nostril_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvLNostrilLoc", r=0.1, d=1, guide=True)
        self.guide_right_nostril_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvRNostrilLoc", r=0.1, d=1, guide=True)
        self.guide_bottom_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvBottomLoc", r=0.1, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_JointEnd", r=0.05, d=1, guide=True)
        # joints
        self.line_top1 = cmds.joint(name=self.name_guide+"_JGuideTop1", radius=0.001)
        self.line_middle = cmds.joint(name=self.name_guide+"_JGuideMiddle", radius=0.001)
        self.line_tip = cmds.joint(name=self.name_guide+"line_tip", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        cmds.select(self.line_middle)
        self.line_side = cmds.joint(name=self.name_guide+"line_side", radius=0.001)
        self.line_nostril = cmds.joint(name=self.name_guide+"line_nostril", radius=0.001)
        cmds.select(self.line_middle)
        self.line_bottom = cmds.joint(name=self.name_guide+"line_bottom", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_top1, self.line_middle, self.line_tip, self.line_end, self.line_side, self.line_nostril, self.line_bottom, self.guide_right_side_loc, self.guide_right_nostril_loc])
        cmds.setAttr(self.guide_top_loc+".rotateX", 60)
        cmds.setAttr(self.guide_middle_loc+".translateY", -0.6)
        cmds.setAttr(self.guide_middle_loc+".translateZ", 0.35)
        cmds.setAttr(self.guide_tip_loc+".translateY", -0.4)
        cmds.setAttr(self.guide_tip_loc+".translateZ", 0.55)
        cmds.setAttr(self.guide_end_loc+".translateZ", 0.3)
        cmds.setAttr(self.guide_left_side_loc+".translateX", 0.35)
        cmds.setAttr(self.guide_left_side_loc+".translateY", -0.55)
        cmds.setAttr(self.guide_left_side_loc+".translateZ", 0.45)
        cmds.setAttr(self.guide_left_nostril_loc+".translateX", 0.25)
        cmds.setAttr(self.guide_left_nostril_loc+".translateY", -0.625)
        cmds.setAttr(self.guide_left_nostril_loc+".translateZ", 0.625)
        cmds.setAttr(self.guide_bottom_loc+".translateY", -0.9)
        cmds.setAttr(self.guide_bottom_loc+".translateZ", 0.6)
        # parenting
        cmds.parent(self.line_top1, self.guide_top_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_middle_loc, self.guide_top_loc, relative=False)
        cmds.parent(self.guide_tip_loc, self.guide_bottom_loc, self.guide_middle_loc, relative=False)
        cmds.parent(self.guide_end_loc, self.guide_tip_loc, relative=True)
        cmds.parent(self.guide_left_side_loc, self.guide_right_side_loc, self.guide_middle_loc, relative=False)
        cmds.parent(self.guide_left_nostril_loc, self.guide_left_side_loc, relative=False)
        cmds.parent(self.guide_right_nostril_loc, self.guide_right_side_loc, relative=False)
        # edit
        self.ar.ctrls.directConnect(self.guide_top_loc, self.line_top1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_middle_loc, self.line_middle, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_tip_loc, self.line_tip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_left_side_loc, self.line_side, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_left_nostril_loc, self.line_nostril, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_bottom_loc, self.line_bottom, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def create_guide_nose_side(self, name, source, destination):
        side_t_md = cmds.createNode("multiplyDivide", name=self.name_guide+"_"+name+"_Translate_MD")
        side_r_md = cmds.createNode("multiplyDivide", name=self.name_guide+"_"+name+"_Rotate_MD")
        cmds.connectAttr(source+".translateX", side_t_md+".input1X", force=True)
        cmds.connectAttr(source+".translateY", side_t_md+".input1Y", force=True)
        cmds.connectAttr(source+".translateZ", side_t_md+".input1Z", force=True)
        cmds.connectAttr(source+".rotateX", side_r_md+".input1X", force=True)
        cmds.connectAttr(source+".rotateY", side_r_md+".input1Y", force=True)
        cmds.connectAttr(source+".rotateZ", side_r_md+".input1Z", force=True)
        cmds.connectAttr(side_t_md+".outputX", destination+".translateX", force=True)
        cmds.connectAttr(side_t_md+".outputY", destination+".translateY", force=True)
        cmds.connectAttr(side_t_md+".outputZ", destination+".translateZ", force=True)
        cmds.connectAttr(side_r_md+".outputX", destination+".rotateX", force=True)
        cmds.connectAttr(side_r_md+".outputY", destination+".rotateY", force=True)
        cmds.connectAttr(side_r_md+".outputZ", destination+".rotateZ", force=True)
        cmds.setAttr(side_t_md+".input2X", -1)
        cmds.setAttr(side_r_md+".input2Y", -1)
        cmds.setAttr(side_r_md+".input2Z", -1)

        
    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
        if joint_number and joint_number != self.current_joint_number:
            self.ar.opt.check_use_default_render_layer()
            if joint_number > self.current_joint_number:
                for n in range(self.current_joint_number+1, joint_number+1):
                    self.guide_top_loc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_cvTopLoc"+str(n), r=0.3, d=1, guide=True)
                    cmds.setAttr(self.guide_top_loc+".nJoint", n)
                    cmds.parent(self.guide_top_loc, self.name_guide+"_cvTopLoc"+str(n-1), relative=True)
                    dist = self.ar.utils.distanceBet(self.name_guide+"_cvTopLoc"+str(n-1), self.name_guide+"_cvMiddleLoc")[0]
                    cmds.setAttr(self.guide_top_loc+".translateZ", (0.5*dist))
                    self.line = cmds.joint(name=self.name_guide+"_JGuideTop"+str(n), radius=0.001)
                    cmds.setAttr(self.line+".template", 1)
                    cmds.parent(self.line, self.name_guide+"_JGuideTop"+str(n-1), relative=True)
                    cmds.parentConstraint(self.guide_top_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
                    cmds.scaleConstraint(self.guide_top_loc, self.line, maintainOffset=False, name=self.line+"_ScC")
                    self.add_node_to_guide_net([self.guide_top_loc], ["guide_top_loc"+str(n)])
            elif joint_number < self.current_joint_number:
                self.guide_top_loc = self.reduce_joint_number(joint_number, "guide_top_loc", "Top")
            cmds.setAttr(self.guide_base+".nJoints", joint_number)
            self.current_joint_number = joint_number
            self.create_mirror_preview()
        cmds.select(self.guide_base)
    

    def change_nostril(self, value, *args):
        """ Set the attribute value for nostril.
        """
        cmds.setAttr(self.guide_base+".nostril", value)
        cmds.setAttr(self.guide_left_nostril_loc+".visibility", value)
        cmds.setAttr(self.guide_right_nostril_loc+".visibility", value)
    

    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.ctrl_hook_grps, self.main_ctrls = [], []
            self.ctrls, self.left_ctrls, self.right_ctrls = [], [], []
            # check if need to add nostril:
            nostril = self.get_guide_attr("nostril")
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                ctrl_zero_grp = side+self.number_name+"_00_Ctrl_Zero_0_Grp"
                skin_joints = []
                centers, lefts, rights = [], [], []
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                head_def_value = cmds.getAttr(self.base+".deformedBy")
                # creating top nose controls and joints:
                for n in range(0, self.n_joints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide_top_loc = side+self.number_name+"_Guide_cvTopLoc"+str(n+1)
                    self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.number_name+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_%02d"%(n))
                    skin_joints.append(self.jnt)
                    # create a control:
                    nose_ctrl = self.ar.ctrls.cvControl("id_075_NoseTop", ctrl_name=side+self.number_name+"_%02d_Ctrl"%(n), r=self.radius, d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvTopLoc1", parentTag=self.get_parent_to_tag(centers))
                    centers.append(nose_ctrl)
                    # zeroOut controls:
                    ctrl_zero = self.ar.utils.zeroOut([nose_ctrl])[0]
                    # position and orientation of joint and control:
                    cmds.matchTransform(self.jnt, self.guide_top_loc, position=True, rotation=True)
                    cmds.matchTransform(ctrl_zero, self.guide_top_loc, position=True, rotation=True)
                    # hide visibility attribute:
                    cmds.setAttr(nose_ctrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if self.flip:
                            cmds.setAttr(ctrl_zero+".scaleX", -1)
                            cmds.setAttr(ctrl_zero+".scaleY", -1)
                            cmds.setAttr(ctrl_zero+".scaleZ", -1)
                    if n == 0:
                        self.main_ctrls.append(nose_ctrl)
                        self.ar.utils.originedFrom(objName=nose_ctrl, attrString=self.base+";"+self.guide_top_loc+";"+self.guide_radius)
                        ctrl_zero_grp = ctrl_zero
                    else:
                        self.ar.utils.originedFrom(objName=nose_ctrl, attrString=self.guide_top_loc)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        father_joint = side+self.number_name+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, father_joint, absolute=True)
                        # parent zeroCtrl Group to the before noseCtrl:
                        cmds.parent(ctrl_zero, side+self.number_name+"_%02d_Ctrl"%(n-1), absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(nose_ctrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    cmds.scaleConstraint(nose_ctrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                    # add articulationJoint:
                    if n == 1:
                        if self.articulation:
                            articulation_joints = self.ar.utils.articulationJoint(father_joint, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            self.ar.utils.setJointLabel(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_%02d_Jar"%(n))
                            cmds.setAttr(articulation_joints[0]+".segmentScaleCompensate", 0)
                            cmds.setAttr(articulation_joints[0]+".segmentScaleCompensate", 0)
                    cmds.select(self.jnt)
                
                # declaring guides:
                self.guide_middle_loc = side+self.number_name+"_Guide_cvMiddleLoc"
                self.guide_tip_loc = side+self.number_name+"_Guide_cvTipLoc"
                self.guide_left_side_loc = side+self.number_name+"_Guide_cvLSideLoc"
                self.guide_right_side_loc = side+self.number_name+"_Guide_cvRSideLoc"
                self.guide_left_nostril_loc = side+self.number_name+"_Guide_cvLNostrilLoc"
                self.guide_right_nostril_loc = side+self.number_name+"_Guide_cvRNostrilLoc"
                self.guide_bottom_loc = side+self.number_name+"_Guide_cvBottomLoc"
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                
                # generating naming:
                left_side_name = self.ar.data.lang['p002_left']
                right_side_name = self.ar.data.lang['p003_right']
                if self.flip:
                    left_side_name = self.ar.data.lang['c123_outer']
                    right_side_name = self.ar.data.lang['c122_inner']
                middle_joint_name = side+self.number_name+"_%02d_"%(n+1)+self.ar.data.lang['c029_middle']+"_Jnt"
                tip_joint_name = side+self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c120_tip']+"_Jnt"
                bottom_joint_name = side+self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c100_bottom']+"_Jnt"
                left_side_joint_name = side+self.number_name+"_%02d_"%(n+3)+left_side_name+"_"+self.ar.data.lang['c121_side']+"_Jnt"
                right_side_joint_name = side+self.number_name+"_%02d_"%(n+3)+right_side_name+"_"+self.ar.data.lang['c121_side']+"_Jnt"
                left_nostril_joint_name = side+self.number_name+"_%02d_"%(n+4)+left_side_name+"_"+self.ar.data.lang['m079_nostril']+"_Jnt"
                right_nostril_joint_name = side+self.number_name+"_%02d_"%(n+4)+right_side_name+"_"+self.ar.data.lang['m079_nostril']+"_Jnt"
                middle_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c029_middle']+"_Ctrl"
                tip_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c120_tip']+"_Ctrl"
                bottom_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c100_bottom']+"_Ctrl"
                left_side_ctrl_name = left_side_name+"_"+side+self.number_name+"_"+self.ar.data.lang['c121_side']+"_Ctrl"
                right_side_ctrl_name = right_side_name+"_"+side+self.number_name+"_"+self.ar.data.lang['c121_side']+"_Ctrl"
                left_nostril_ctrl_name = left_side_name+"_"+side+self.number_name+"_"+self.ar.data.lang['m079_nostril']+"_Ctrl"
                right_nostril_ctrl_name = right_side_name+"_"+side+self.number_name+"_"+self.ar.data.lang['m079_nostril']+"_Ctrl"
                
                # creating joints:
                middle_joint = cmds.joint(name=middle_joint_name, scaleCompensate=False)
                tip_joint = cmds.joint(name=tip_joint_name, scaleCompensate=False)
                cmds.select(middle_joint)
                bottom_joint = cmds.joint(name=bottom_joint_name, scaleCompensate=False)
                cmds.select(middle_joint)
                left_side_joint = cmds.joint(name=left_side_joint_name, scaleCompensate=False)
                if nostril:
                    left_nostril_joint = cmds.joint(name=left_nostril_joint_name, scaleCompensate=False)
                cmds.select(middle_joint)
                right_side_joint = cmds.joint(name=right_side_joint_name, scaleCompensate=False)
                if nostril:
                    right_nostril_joint = cmds.joint(name=right_nostril_joint_name, scaleCompensate=False)
                    dpar_joints = [middle_joint, tip_joint, left_side_joint, right_side_joint, left_nostril_joint, right_nostril_joint, bottom_joint]
                else:
                    dpar_joints = [middle_joint, tip_joint, left_side_joint, right_side_joint, bottom_joint]
                for dpar_joint in dpar_joints:
                    if cmds.objExists(dpar_joint):
                        cmds.addAttr(dpar_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.ar.utils.setJointLabel(middle_joint, s+self.joint_label_add, 18, self.number_name+"_%02d_"%(n+1)+self.ar.data.lang['c029_middle'])
                self.ar.utils.setJointLabel(tip_joint, s+self.joint_label_add, 18, self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c120_tip'])
                self.ar.utils.setJointLabel(bottom_joint, s+self.joint_label_add, 18, self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c100_bottom'])
                self.ar.utils.setJointLabel(left_side_joint, 1, 18, self.number_name+"_%02d_"%(n+3)+self.ar.data.lang['c121_side'])
                self.ar.utils.setJointLabel(right_side_joint, 2, 18, self.number_name+"_%02d_"%(n+3)+self.ar.data.lang['c121_side'])
                if nostril:
                    self.ar.utils.setJointLabel(left_nostril_joint, 1, 18, self.number_name+"_%02d_"%(n+4)+self.ar.data.lang['m079_nostril'])
                    self.ar.utils.setJointLabel(right_nostril_joint, 2, 18, self.number_name+"_%02d_"%(n+4)+self.ar.data.lang['m079_nostril'])
                
                # creating controls:
                middle_ctrl = self.ar.ctrls.cvControl("id_076_NoseMiddle", ctrl_name=middle_ctrl_name, r=(self.radius), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvMiddleLoc", parentTag=centers[-1])
                tip_ctrl = self.ar.ctrls.cvControl("id_077_NoseTip", ctrl_name=tip_ctrl_name, r=(self.radius * 0.3), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvTipLoc", parentTag=centers[-1])
                bottom_ctrl = self.ar.ctrls.cvControl("id_080_NoseBottom", ctrl_name=bottom_ctrl_name, r=(self.radius * 0.5), d=self.curve_degree, dir="-Y", headDef=head_def_value, guideSource=self.name_guide+"_cvBottomLoc", parentTag=centers[-1])
                left_side_ctrl = self.ar.ctrls.cvControl("id_078_NoseSide", ctrl_name=left_side_ctrl_name, r=(self.radius * 0.5), d=self.curve_degree, rot=(0, 0, -90), headDef=head_def_value, guideSource=self.name_guide+"_cvLSideLoc", parentTag=centers[-1])
                right_side_ctrl = self.ar.ctrls.cvControl("id_078_NoseSide", ctrl_name=right_side_ctrl_name, r=(self.radius * 0.5), d=self.curve_degree, rot=(0, 0, -90), headDef=head_def_value, guideSource=self.name_guide+"_cvRSideLoc", parentTag=centers[-1])
                if nostril:
                    left_nostril_ctrl = self.ar.ctrls.cvControl("id_079_Nostril", ctrl_name=left_nostril_ctrl_name, r=(self.radius * 0.2), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvLNostrilLoc", parentTag=left_side_ctrl)
                    right_nostril_ctrl = self.ar.ctrls.cvControl("id_079_Nostril", ctrl_name=right_nostril_ctrl_name, r=(self.radius * 0.2), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvRNostrilLoc", parentTag=right_side_ctrl)
                    lefts.append(left_nostril_ctrl)
                    rights.append(right_nostril_ctrl)
                centers.append(middle_ctrl)
                centers.append(tip_ctrl)
                centers.append(bottom_ctrl)
                self.ctrls.append(centers)
                lefts.append(left_side_ctrl)
                rights.append(right_side_ctrl)
                self.left_ctrls.append(lefts)
                self.right_ctrls.append(rights)
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                self.ar.utils.originedFrom(objName=middle_ctrl, attrString=self.guide_middle_loc)
                self.ar.utils.originedFrom(objName=tip_ctrl, attrString=self.guide_tip_loc)
                self.ar.utils.originedFrom(objName=bottom_ctrl, attrString=self.guide_bottom_loc)
                self.ar.utils.originedFrom(objName=left_side_ctrl, attrString=self.guide_left_side_loc)
                self.ar.utils.originedFrom(objName=right_side_ctrl, attrString=self.guide_right_side_loc)
                if nostril:
                    self.ar.utils.originedFrom(objName=left_nostril_ctrl, attrString=self.guide_left_nostril_loc)
                    self.ar.utils.originedFrom(objName=right_nostril_ctrl, attrString=self.guide_right_nostril_loc)

                # temporary parentConstraints:
                cmds.matchTransform(middle_ctrl, self.guide_middle_loc, position=True, rotation=True)
                cmds.matchTransform(tip_ctrl, self.guide_tip_loc, position=True, rotation=True)
                cmds.matchTransform(bottom_ctrl, self.guide_bottom_loc, position=True, rotation=True)
                cmds.matchTransform(left_side_ctrl, self.guide_left_side_loc, position=True, rotation=True)
                cmds.matchTransform(right_side_ctrl, self.guide_right_side_loc, position=True, rotation=True)
                if nostril:
                    cmds.matchTransform(left_nostril_ctrl, self.guide_left_nostril_loc, position=True, rotation=True)
                    cmds.matchTransform(right_nostril_ctrl, self.guide_right_nostril_loc, position=True, rotation=True)
                
                # fixing flip mirror:
                if s == 1:
                    if self.flip:
                        to_flip_ctrls = [middle_ctrl, bottom_ctrl, tip_ctrl, left_side_ctrl, right_side_ctrl]
                        if nostril:
                            to_flip_ctrls.append(left_nostril_ctrl)
                            to_flip_ctrls.append(right_nostril_ctrl)
                        for to_flip_ctrl in to_flip_ctrls:
                            cmds.setAttr(to_flip_ctrl+".scaleX", -1)
                            cmds.setAttr(to_flip_ctrl+".scaleY", -1)
                            cmds.setAttr(to_flip_ctrl+".scaleZ", -1)
                    else:
                        cmds.setAttr(right_side_ctrl+".scaleX", -1)
                        if nostril:
                            cmds.setAttr(right_nostril_ctrl+".scaleX", -1)

                # zeroOut controls:
                side_ctrl_zeros = self.ar.utils.zeroOut([left_side_ctrl, right_side_ctrl])
                if s == 0:
                    cmds.setAttr(side_ctrl_zeros[1]+".scaleX", -1)
                elif self.flip:
                    cmds.setAttr(side_ctrl_zeros[1]+".scaleX", 1)
                if nostril:
                    side_nostril_ctrl_zeros = self.ar.utils.zeroOut([left_nostril_ctrl, right_nostril_ctrl])
                    if s == 0:
                        cmds.setAttr(side_nostril_ctrl_zeros[1]+".scaleX", -1)
                    elif self.flip:
                        cmds.setAttr(side_nostril_ctrl_zeros[1]+".scaleX", 1)
                ctrl_zeros = self.ar.utils.zeroOut([middle_ctrl, tip_ctrl, bottom_ctrl])

                # make controls drive joints:
                cmds.parentConstraint(middle_ctrl, middle_joint, maintainOffset=False, name=middle_joint+"_PaC")
                cmds.scaleConstraint(middle_ctrl, middle_joint, maintainOffset=False, name=middle_joint+"_ScC")
                cmds.parentConstraint(tip_ctrl, tip_joint, maintainOffset=False, name=tip_joint+"_PaC")
                cmds.scaleConstraint(tip_ctrl, tip_joint, maintainOffset=False, name=tip_joint+"_ScC")
                cmds.parentConstraint(bottom_ctrl, bottom_joint, maintainOffset=False, name=bottom_joint+"_PaC")
                cmds.scaleConstraint(bottom_ctrl, bottom_joint, maintainOffset=False, name=bottom_joint+"_ScC")
                cmds.parentConstraint(left_side_ctrl, left_side_joint, maintainOffset=False, name=left_side_joint+"_PaC")
                cmds.scaleConstraint(left_side_ctrl, left_side_joint, maintainOffset=False, name=left_side_joint+"_ScC")
                cmds.parentConstraint(right_side_ctrl, right_side_joint, maintainOffset=False, name=right_side_joint+"_PaC")
                cmds.scaleConstraint(right_side_ctrl, right_side_joint, maintainOffset=False, name=right_side_joint+"_ScC")
                if nostril:
                    cmds.parentConstraint(left_nostril_ctrl, left_nostril_joint, maintainOffset=False, name=left_nostril_joint+"_PaC")
                    cmds.scaleConstraint(left_nostril_ctrl, left_nostril_joint, maintainOffset=False, name=left_nostril_joint+"_ScC")
                    cmds.parentConstraint(right_nostril_ctrl, right_nostril_joint, maintainOffset=False, name=right_nostril_joint+"_PaC")
                    cmds.scaleConstraint(right_nostril_ctrl, right_nostril_joint, maintainOffset=False, name=right_nostril_joint+"_ScC")

                # mount controls hierarchy:
                cmds.parent(ctrl_zeros[0], nose_ctrl, absolute=True) #middleCtrl
                cmds.parent(ctrl_zeros[1], ctrl_zeros[2], side_ctrl_zeros[0], side_ctrl_zeros[1], middle_ctrl, absolute=True) #tipCtrl, bottomCtrl, lSideCtrl, rSideCtrl
                if nostril:
                    cmds.parent(side_nostril_ctrl_zeros[0], left_side_ctrl, absolute=True) #lNostrilCtrl
                    cmds.parent(side_nostril_ctrl_zeros[1], right_side_ctrl, absolute=True) #rNostrilCtrl

                # create end joint:
                cmds.select(tip_joint)
                self.create_end_joint(side+self.number_name)

                # optimize control CV shapes:
                temp_tip_cluster = cmds.cluster(tip_ctrl)[1]
                cmds.parentConstraint(self.guide_end_loc, temp_tip_cluster, maintainOffset=False)
                cmds.delete([tip_ctrl], constructionHistory=True)

                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [ctrl_zero_grp], [skin_joints[0]])
                self.ctrl_hook_grps.append(self.ctrl_hook_grp)
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
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "controllers"     : self.ctrls,
                            "lCtrls"          : self.left_ctrls,
                            "rCtrls"          : self.right_ctrls,
                            "ctrlHookGrpList" : self.ctrl_hook_grps,
                            "mainCtrlList"    : self.main_ctrls
                        }
