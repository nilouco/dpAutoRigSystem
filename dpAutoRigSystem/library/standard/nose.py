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
        self.cvLNostrilLoc = self.name_guide+"_cvLNostrilLoc"
        self.cvRNostrilLoc = self.name_guide+"_cvRNostrilLoc"
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.create_guide_nose_side("Side", self.cvLSideLoc, self.cvRSideLoc)
        self.create_guide_nose_side("Nostril", self.cvLNostrilLoc, self.cvRNostrilLoc)
        self.add_node_to_guide_net([self.cvTopLoc, self.cvMiddleLoc, self.cvTipLoc, self.cvLSideLoc, self.cvRSideLoc, self.cvLNostrilLoc, self.cvBottomLoc, self.guide_end_loc], 
                                   ["cvTopLoc1", "cvMiddleLoc", "cvTipLoc", "cvLSideLoc", "cvRSideLoc", "cvLNostrilLoc", "cvBottomLoc", "JointEnd"])


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
        self.cvTopLoc      = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_cvTopLoc1", r=0.3, d=1, guide=True)
        self.cvMiddleLoc   = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_cvMiddleLoc", r=0.2, d=1, guide=True)
        self.cvTipLoc      = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvTipLoc", r=0.1, d=1, guide=True)
        self.cvLSideLoc    = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvLSideLoc", r=0.15, d=1, guide=True)
        self.cvRSideLoc    = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvRSideLoc", r=0.15, d=1, guide=True)
        self.cvLNostrilLoc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvLNostrilLoc", r=0.1, d=1, guide=True)
        self.cvRNostrilLoc = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvRNostrilLoc", r=0.1, d=1, guide=True)
        self.cvBottomLoc   = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_cvBottomLoc", r=0.1, d=1, guide=True)
        self.guide_end_loc    = self.ar.ctrls.cvLocator(ctrl_name=self.name_guide+"_JointEnd", r=0.05, d=1, guide=True)
        # joints
        self.jGuideTop1   = cmds.joint(name=self.name_guide+"_JGuideTop1", radius=0.001)
        self.jGuideMiddle = cmds.joint(name=self.name_guide+"_JGuideMiddle", radius=0.001)
        self.jGuideTip    = cmds.joint(name=self.name_guide+"jGuideTip", radius=0.001)
        self.line_end    = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        cmds.select(self.jGuideMiddle)
        self.jGuideSide    = cmds.joint(name=self.name_guide+"jGuideSide", radius=0.001)
        self.jGuideNostril = cmds.joint(name=self.name_guide+"jGuideNostril", radius=0.001)
        cmds.select(self.jGuideMiddle)
        self.jGuideBottom = cmds.joint(name=self.name_guide+"jGuideBottom", radius=0.001)
        # setup
        self.ar.utils.set_template([self.jGuideTop1, self.jGuideMiddle, self.jGuideTip, self.line_end, self.jGuideSide, self.jGuideNostril, self.jGuideBottom, self.cvRSideLoc, self.cvRNostrilLoc])
        cmds.setAttr(self.cvTopLoc+".rotateX", 60)
        cmds.setAttr(self.cvMiddleLoc+".translateY", -0.6)
        cmds.setAttr(self.cvMiddleLoc+".translateZ", 0.35)
        cmds.setAttr(self.cvTipLoc+".translateY", -0.4)
        cmds.setAttr(self.cvTipLoc+".translateZ", 0.55)
        cmds.setAttr(self.guide_end_loc+".translateZ", 0.3)
        cmds.setAttr(self.cvLSideLoc+".translateX", 0.35)
        cmds.setAttr(self.cvLSideLoc+".translateY", -0.55)
        cmds.setAttr(self.cvLSideLoc+".translateZ", 0.45)
        cmds.setAttr(self.cvLNostrilLoc+".translateX", 0.25)
        cmds.setAttr(self.cvLNostrilLoc+".translateY", -0.625)
        cmds.setAttr(self.cvLNostrilLoc+".translateZ", 0.625)
        cmds.setAttr(self.cvBottomLoc+".translateY", -0.9)
        cmds.setAttr(self.cvBottomLoc+".translateZ", 0.6)
        # parenting
        cmds.parent(self.jGuideTop1, self.cvTopLoc, self.guide_base, relative=True)
        cmds.parent(self.cvMiddleLoc, self.cvTopLoc, relative=False)
        cmds.parent(self.cvTipLoc, self.cvBottomLoc, self.cvMiddleLoc, relative=False)
        cmds.parent(self.guide_end_loc, self.cvTipLoc, relative=True)
        cmds.parent(self.cvLSideLoc, self.cvRSideLoc, self.cvMiddleLoc, relative=False)
        cmds.parent(self.cvLNostrilLoc, self.cvLSideLoc, relative=False)
        cmds.parent(self.cvRNostrilLoc, self.cvRSideLoc, relative=False)
        # edit
        self.ar.ctrls.directConnect(self.cvTopLoc, self.jGuideTop1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.cvMiddleLoc, self.jGuideMiddle, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.cvTipLoc, self.jGuideTip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.cvLSideLoc, self.jGuideSide, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.cvLNostrilLoc, self.jGuideNostril, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.cvBottomLoc, self.jGuideBottom, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
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
                    self.cvTopLoc = self.ar.ctrls.cvJointLoc(ctrl_name=self.name_guide+"_cvTopLoc"+str(n), r=0.3, d=1, guide=True)
                    cmds.setAttr(self.cvTopLoc+".nJoint", n)
                    cmds.parent(self.cvTopLoc, self.name_guide+"_cvTopLoc"+str(n-1), relative=True)
                    dist = self.ar.utils.distanceBet(self.name_guide+"_cvTopLoc"+str(n-1), self.name_guide+"_cvMiddleLoc")[0]
                    cmds.setAttr(self.cvTopLoc+".translateZ", (0.5*dist))
                    self.line = cmds.joint(name=self.name_guide+"_JGuideTop"+str(n), radius=0.001)
                    cmds.setAttr(self.line+".template", 1)
                    cmds.parent(self.line, self.name_guide+"_JGuideTop"+str(n-1), relative=True)
                    cmds.parentConstraint(self.cvTopLoc, self.line, maintainOffset=False, name=self.line+"_PaC")
                    cmds.scaleConstraint(self.cvTopLoc, self.line, maintainOffset=False, name=self.line+"_ScC")
                    self.add_node_to_guide_net([self.cvTopLoc], ["cvTopLoc"+str(n)])
            elif joint_number < self.current_joint_number:
                self.cvTopLoc = self.reduce_joint_number(joint_number, "cvTopLoc", "Top")
            cmds.setAttr(self.guide_base+".nJoints", joint_number)
            self.current_joint_number = joint_number
            self.create_mirror_preview()
        cmds.select(self.guide_base)
    

    def changeNostril(self, *args):
        """ Set the attribute value for nostril.
        """
        nostrilValue = cmds.checkBox(self.nostrilCB, query=True, value=True)
        cmds.setAttr(self.guide_base+".nostril", nostrilValue)
        cmds.setAttr(self.cvLNostrilLoc+".visibility", nostrilValue)
        cmds.setAttr(self.cvRNostrilLoc+".visibility", nostrilValue)
    

    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.ctrlHookGrpList, self.mainCtrlList = [], []
            self.aCtrls, self.aLCtrls, self.aRCtrls = [], [], []
            # check if need to add nostril:
            self.nostril = self.get_guide_attr("nostril")
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                ctrl_zero_grp = side+self.number_name+"_00_Ctrl_Zero_0_Grp"
                skin_joints = []
                self.centerList, self.leftList, self.rightList = [], [], []
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                head_def_value = cmds.getAttr(self.base+".deformedBy")
                # creating top nose controls and joints:
                for n in range(0, self.n_joints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.cvTopLoc = side+self.number_name+"_Guide_cvTopLoc"+str(n+1)
                    self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.number_name+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_%02d"%(n))
                    skin_joints.append(self.jnt)
                    # create a control:
                    self.noseCtrl = self.ar.ctrls.cvControl("id_075_NoseTop", ctrl_name=side+self.number_name+"_%02d_Ctrl"%(n), r=self.radius, d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvTopLoc1", parentTag=self.get_parent_to_tag(self.centerList))
                    self.centerList.append(self.noseCtrl)
                    # zeroOut controls:
                    ctrl_zero = self.ar.utils.zeroOut([self.noseCtrl])[0]
                    # position and orientation of joint and control:
                    cmds.matchTransform(self.jnt, self.cvTopLoc, position=True, rotation=True)
                    cmds.matchTransform(ctrl_zero, self.cvTopLoc, position=True, rotation=True)
                    # hide visibility attribute:
                    cmds.setAttr(self.noseCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if self.flip:
                            cmds.setAttr(ctrl_zero+".scaleX", -1)
                            cmds.setAttr(ctrl_zero+".scaleY", -1)
                            cmds.setAttr(ctrl_zero+".scaleZ", -1)
                    if n == 0:
                        self.mainCtrlList.append(self.noseCtrl)
                        self.ar.utils.originedFrom(objName=self.noseCtrl, attrString=self.base+";"+self.cvTopLoc+";"+self.guide_radius)
                        ctrl_zero_grp = ctrl_zero
                    else:
                        self.ar.utils.originedFrom(objName=self.noseCtrl, attrString=self.cvTopLoc)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        father_joint = side+self.number_name+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, father_joint, absolute=True)
                        # parent zeroCtrl Group to the before noseCtrl:
                        cmds.parent(ctrl_zero, side+self.number_name+"_%02d_Ctrl"%(n-1), absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(self.noseCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    cmds.scaleConstraint(self.noseCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                    # add articulationJoint:
                    if n == 1:
                        if self.articulation:
                            articulation_joints = self.ar.utils.articulationJoint(father_joint, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            self.ar.utils.setJointLabel(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_%02d_Jar"%(n))
                            cmds.setAttr(articulation_joints[0]+".segmentScaleCompensate", 0)
                            cmds.setAttr(articulation_joints[0]+".segmentScaleCompensate", 0)
                    cmds.select(self.jnt)
                
                # declaring guides:
                self.cvMiddleLoc   = side+self.number_name+"_Guide_cvMiddleLoc"
                self.cvTipLoc      = side+self.number_name+"_Guide_cvTipLoc"
                self.cvLSideLoc    = side+self.number_name+"_Guide_cvLSideLoc"
                self.cvRSideLoc    = side+self.number_name+"_Guide_cvRSideLoc"
                self.cvLNostrilLoc = side+self.number_name+"_Guide_cvLNostrilLoc"
                self.cvRNostrilLoc = side+self.number_name+"_Guide_cvRNostrilLoc"
                self.cvBottomLoc   = side+self.number_name+"_Guide_cvBottomLoc"
                self.guide_end_loc    = side+self.number_name+"_Guide_JointEnd"
                
                # generating naming:
                leftSideName  = self.ar.data.lang['p002_left']
                rightSideName = self.ar.data.lang['p003_right']
                if self.flip:
                    leftSideName = self.ar.data.lang['c123_outer']
                    rightSideName = self.ar.data.lang['c122_inner']
                middleJntName    = side+self.number_name+"_%02d_"%(n+1)+self.ar.data.lang['c029_middle']+"_Jnt"
                tipJntName       = side+self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c120_tip']+"_Jnt"
                bottomJntName    = side+self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c100_bottom']+"_Jnt"
                lSideJntName     = side+self.number_name+"_%02d_"%(n+3)+leftSideName+"_"+self.ar.data.lang['c121_side']+"_Jnt"
                rSideJntName     = side+self.number_name+"_%02d_"%(n+3)+rightSideName+"_"+self.ar.data.lang['c121_side']+"_Jnt"
                lNostrilJntName  = side+self.number_name+"_%02d_"%(n+4)+leftSideName+"_"+self.ar.data.lang['m079_nostril']+"_Jnt"
                rNostrilJntName  = side+self.number_name+"_%02d_"%(n+4)+rightSideName+"_"+self.ar.data.lang['m079_nostril']+"_Jnt"
                middleCtrlName   = side+self.number_name+"_"+self.ar.data.lang['c029_middle']+"_Ctrl"
                tipCtrlName      = side+self.number_name+"_"+self.ar.data.lang['c120_tip']+"_Ctrl"
                bottomCtrlName   = side+self.number_name+"_"+self.ar.data.lang['c100_bottom']+"_Ctrl"
                lSideCtrlName    = leftSideName+"_"+side+self.number_name+"_"+self.ar.data.lang['c121_side']+"_Ctrl"
                rSideCtrlName    = rightSideName+"_"+side+self.number_name+"_"+self.ar.data.lang['c121_side']+"_Ctrl"
                lNostrilCtrlName = leftSideName+"_"+side+self.number_name+"_"+self.ar.data.lang['m079_nostril']+"_Ctrl"
                rNostrilCtrlName = rightSideName+"_"+side+self.number_name+"_"+self.ar.data.lang['m079_nostril']+"_Ctrl"
                
                # creating joints:
                self.middleJnt = cmds.joint(name=middleJntName, scaleCompensate=False)
                self.tipJnt = cmds.joint(name=tipJntName, scaleCompensate=False)
                cmds.select(self.middleJnt)
                self.bottomJnt = cmds.joint(name=bottomJntName, scaleCompensate=False)
                cmds.select(self.middleJnt)
                self.lSideJnt = cmds.joint(name=lSideJntName, scaleCompensate=False)
                if self.nostril:
                    self.lNostrilJnt = cmds.joint(name=lNostrilJntName, scaleCompensate=False)
                cmds.select(self.middleJnt)
                self.rSideJnt = cmds.joint(name=rSideJntName, scaleCompensate=False)
                if self.nostril:
                    self.rNostrilJnt = cmds.joint(name=rNostrilJntName, scaleCompensate=False)
                    dpARJointList = [self.middleJnt, self.tipJnt, self.lSideJnt, self.rSideJnt, self.lNostrilJnt, self.rNostrilJnt, self.bottomJnt]
                else:
                    dpARJointList = [self.middleJnt, self.tipJnt, self.lSideJnt, self.rSideJnt, self.bottomJnt]
                for dpARJoint in dpARJointList:
                    if cmds.objExists(dpARJoint):
                        cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.ar.utils.setJointLabel(self.middleJnt, s+self.joint_label_add, 18, self.number_name+"_%02d_"%(n+1)+self.ar.data.lang['c029_middle'])
                self.ar.utils.setJointLabel(self.tipJnt, s+self.joint_label_add, 18, self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c120_tip'])
                self.ar.utils.setJointLabel(self.bottomJnt, s+self.joint_label_add, 18, self.number_name+"_%02d_"%(n+2)+self.ar.data.lang['c100_bottom'])
                self.ar.utils.setJointLabel(self.lSideJnt, 1, 18, self.number_name+"_%02d_"%(n+3)+self.ar.data.lang['c121_side'])
                self.ar.utils.setJointLabel(self.rSideJnt, 2, 18, self.number_name+"_%02d_"%(n+3)+self.ar.data.lang['c121_side'])
                if self.nostril:
                    self.ar.utils.setJointLabel(self.lNostrilJnt, 1, 18, self.number_name+"_%02d_"%(n+4)+self.ar.data.lang['m079_nostril'])
                    self.ar.utils.setJointLabel(self.rNostrilJnt, 2, 18, self.number_name+"_%02d_"%(n+4)+self.ar.data.lang['m079_nostril'])
                
                # creating controls:
                self.middleCtrl = self.ar.ctrls.cvControl("id_076_NoseMiddle", ctrl_name=middleCtrlName, r=(self.radius), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvMiddleLoc", parentTag=self.centerList[-1])
                self.tipCtrl = self.ar.ctrls.cvControl("id_077_NoseTip", ctrl_name=tipCtrlName, r=(self.radius * 0.3), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvTipLoc", parentTag=self.centerList[-1])
                self.bottomCtrl = self.ar.ctrls.cvControl("id_080_NoseBottom", ctrl_name=bottomCtrlName, r=(self.radius * 0.5), d=self.curve_degree, dir="-Y", headDef=head_def_value, guideSource=self.name_guide+"_cvBottomLoc", parentTag=self.centerList[-1])
                self.lSideCtrl = self.ar.ctrls.cvControl("id_078_NoseSide", ctrl_name=lSideCtrlName, r=(self.radius * 0.5), d=self.curve_degree, rot=(0, 0, -90), headDef=head_def_value, guideSource=self.name_guide+"_cvLSideLoc", parentTag=self.centerList[-1])
                self.rSideCtrl = self.ar.ctrls.cvControl("id_078_NoseSide", ctrl_name=rSideCtrlName, r=(self.radius * 0.5), d=self.curve_degree, rot=(0, 0, -90), headDef=head_def_value, guideSource=self.name_guide+"_cvRSideLoc", parentTag=self.centerList[-1])
                if self.nostril:
                    self.lNostrilCtrl = self.ar.ctrls.cvControl("id_079_Nostril", ctrl_name=lNostrilCtrlName, r=(self.radius * 0.2), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvLNostrilLoc", parentTag=self.lSideCtrl)
                    self.rNostrilCtrl = self.ar.ctrls.cvControl("id_079_Nostril", ctrl_name=rNostrilCtrlName, r=(self.radius * 0.2), d=self.curve_degree, headDef=head_def_value, guideSource=self.name_guide+"_cvRNostrilLoc", parentTag=self.rSideCtrl)
                    self.leftList.append(self.lNostrilCtrl)
                    self.rightList.append(self.rNostrilCtrl)
                self.centerList.append(self.middleCtrl)
                self.centerList.append(self.tipCtrl)
                self.centerList.append(self.bottomCtrl)
                self.aCtrls.append(self.centerList)
                self.leftList.append(self.lSideCtrl)
                self.rightList.append(self.rSideCtrl)
                self.aLCtrls.append(self.leftList)
                self.aRCtrls.append(self.rightList)
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                self.ar.utils.originedFrom(objName=self.middleCtrl, attrString=self.cvMiddleLoc)
                self.ar.utils.originedFrom(objName=self.tipCtrl, attrString=self.cvTipLoc)
                self.ar.utils.originedFrom(objName=self.bottomCtrl, attrString=self.cvBottomLoc)
                self.ar.utils.originedFrom(objName=self.lSideCtrl, attrString=self.cvLSideLoc)
                self.ar.utils.originedFrom(objName=self.rSideCtrl, attrString=self.cvRSideLoc)
                if self.nostril:
                    self.ar.utils.originedFrom(objName=self.lNostrilCtrl, attrString=self.cvLNostrilLoc)
                    self.ar.utils.originedFrom(objName=self.rNostrilCtrl, attrString=self.cvRNostrilLoc)

                # temporary parentConstraints:
                cmds.matchTransform(self.middleCtrl, self.cvMiddleLoc, position=True, rotation=True)
                cmds.matchTransform(self.tipCtrl, self.cvTipLoc, position=True, rotation=True)
                cmds.matchTransform(self.bottomCtrl, self.cvBottomLoc, position=True, rotation=True)
                cmds.matchTransform(self.lSideCtrl, self.cvLSideLoc, position=True, rotation=True)
                cmds.matchTransform(self.rSideCtrl, self.cvRSideLoc, position=True, rotation=True)
                if self.nostril:
                    cmds.matchTransform(self.lNostrilCtrl, self.cvLNostrilLoc, position=True, rotation=True)
                    cmds.matchTransform(self.rNostrilCtrl, self.cvRNostrilLoc, position=True, rotation=True)
                
                # fixing flip mirror:
                if s == 1:
                    if self.flip:
                        ctrlToFlipList = [self.middleCtrl, self.bottomCtrl, self.tipCtrl, self.lSideCtrl, self.rSideCtrl]
                        if self.nostril:
                            ctrlToFlipList.append(self.lNostrilCtrl)
                            ctrlToFlipList.append(self.rNostrilCtrl)
                        for ctrlToFlip in ctrlToFlipList:
                            cmds.setAttr(ctrlToFlip+".scaleX", -1)
                            cmds.setAttr(ctrlToFlip+".scaleY", -1)
                            cmds.setAttr(ctrlToFlip+".scaleZ", -1)
                    else:
                        cmds.setAttr(self.rSideCtrl+".scaleX", -1)
                        if self.nostril:
                            cmds.setAttr(self.rNostrilCtrl+".scaleX", -1)

                # zeroOut controls:
                self.zeroSideCtrlList = self.ar.utils.zeroOut([self.lSideCtrl, self.rSideCtrl])
                if s == 0:
                    cmds.setAttr(self.zeroSideCtrlList[1]+".scaleX", -1)
                elif self.flip:
                    cmds.setAttr(self.zeroSideCtrlList[1]+".scaleX", 1)
                if self.nostril:
                    self.zeroNostrilCtrlList = self.ar.utils.zeroOut([self.lNostrilCtrl, self.rNostrilCtrl])
                    if s == 0:
                        cmds.setAttr(self.zeroNostrilCtrlList[1]+".scaleX", -1)
                    elif self.flip:
                        cmds.setAttr(self.zeroNostrilCtrlList[1]+".scaleX", 1)
                self.zeroCtrlList = self.ar.utils.zeroOut([self.middleCtrl,  self.tipCtrl, self.bottomCtrl])

                # make controls drive joints:
                cmds.parentConstraint(self.middleCtrl, self.middleJnt, maintainOffset=False, name=self.middleJnt+"_PaC")
                cmds.scaleConstraint(self.middleCtrl, self.middleJnt, maintainOffset=False, name=self.middleJnt+"_ScC")
                cmds.parentConstraint(self.tipCtrl, self.tipJnt, maintainOffset=False, name=self.tipJnt+"_PaC")
                cmds.scaleConstraint(self.tipCtrl, self.tipJnt, maintainOffset=False, name=self.tipJnt+"_ScC")
                cmds.parentConstraint(self.bottomCtrl, self.bottomJnt, maintainOffset=False, name=self.bottomJnt+"_PaC")
                cmds.scaleConstraint(self.bottomCtrl, self.bottomJnt, maintainOffset=False, name=self.bottomJnt+"_ScC")
                cmds.parentConstraint(self.lSideCtrl, self.lSideJnt, maintainOffset=False, name=self.lSideJnt+"_PaC")
                cmds.scaleConstraint(self.lSideCtrl, self.lSideJnt, maintainOffset=False, name=self.lSideJnt+"_ScC")
                cmds.parentConstraint(self.rSideCtrl, self.rSideJnt, maintainOffset=False, name=self.rSideJnt+"_PaC")
                cmds.scaleConstraint(self.rSideCtrl, self.rSideJnt, maintainOffset=False, name=self.rSideJnt+"_ScC")
                if self.nostril:
                    cmds.parentConstraint(self.lNostrilCtrl, self.lNostrilJnt, maintainOffset=False, name=self.lNostrilJnt+"_PaC")
                    cmds.scaleConstraint(self.lNostrilCtrl, self.lNostrilJnt, maintainOffset=False, name=self.lNostrilJnt+"_ScC")
                    cmds.parentConstraint(self.rNostrilCtrl, self.rNostrilJnt, maintainOffset=False, name=self.rNostrilJnt+"_PaC")
                    cmds.scaleConstraint(self.rNostrilCtrl, self.rNostrilJnt, maintainOffset=False, name=self.rNostrilJnt+"_ScC")

                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[0], self.noseCtrl, absolute=True) #middleCtrl
                cmds.parent(self.zeroCtrlList[1], self.zeroCtrlList[2], self.zeroSideCtrlList[0], self.zeroSideCtrlList[1], self.middleCtrl, absolute=True) #tipCtrl, bottomCtrl, lSideCtrl, rSideCtrl
                if self.nostril:
                    cmds.parent(self.zeroNostrilCtrlList[0], self.lSideCtrl, absolute=True) #lNostrilCtrl
                    cmds.parent(self.zeroNostrilCtrlList[1], self.rSideCtrl, absolute=True) #rNostrilCtrl

                # create end joint:
                cmds.select(self.tipJnt)
                self.create_end_joint(side+self.number_name)

                # optimize control CV shapes:
                tempTipCluster = cmds.cluster(self.tipCtrl)[1]
                cmds.parentConstraint(self.guide_end_loc, tempTipCluster, maintainOffset=False)
                cmds.delete([self.tipCtrl], constructionHistory=True)

                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [ctrl_zero_grp], [skin_joints[0]])
                self.ctrlHookGrpList.append(self.ctrl_hook_grp)
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
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "controllers"     : self.aCtrls,
                            "lCtrls"          : self.aLCtrls,
                            "rCtrls"          : self.aRCtrls,
                            "ctrlHookGrpList" : self.ctrlHookGrpList,
                            "mainCtrlList"    : self.mainCtrlList
                        }
