# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "FkLine"
TITLE = "m001_fkLine"
DESCRIPTION = "m002_fkLineDesc"
WIKI = "03-‐-Guides#-fk-line"



class FkLine(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.current_joint_number = 1
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc], 
                                   ["JointLoc1", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", defaultValue=1, attributeType='long')
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="articulation", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="mainControls", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="nMain", minValue=1, defaultValue=1, attributeType='long')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=0, maxValue=3, attributeType='long')
        cmds.addAttr(self.guide_base, longName="reorient", attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_loc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line, self.line_end])
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        # parenting
        cmds.parent(self.line, self.guide_base, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        cmds.parent(self.guide_loc, self.guide_base)
        # edit
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.parentConstraint(self.guide_end_loc, self.line_end, maintainOffset=False, name=self.line_end+"_PaC")
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        # get the number of joints entered by user:
        joint_number = self.parse_inputted_joint_number(inputted)
        # start analisys the difference between values:
        if joint_number and joint_number != self.current_joint_number:
            self.ar.opt.check_use_default_render_layer()
            # get the number of joints existing:
            self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
            # unparent temporarely the Ends:
            self.guide_end_loc = self.name_guide+"_JointEnd"
            self.line_end = self.name_guide+"_JGuideEnd"
            cmds.parent(self.guide_end_loc, self.line_end, world=True)
            # verify if the nJoints is greather or less than the current
            if joint_number > self.current_joint_number:
                for n in range(self.current_joint_number+1, joint_number+1):
                    # create another N cvJointLoc:
                    self.guide_loc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                    self.increment_joint_number(n)
                    self.add_node_to_guide_net([self.guide_loc], ["JointLoc"+str(n)])
            elif joint_number < self.current_joint_number:
                self.line = self.name_guide+"_JGuide"+str(joint_number)
                self.guide_loc = self.reduce_joint_number(joint_number)
            self.re_parent_guide_end()
            cmds.setAttr(self.guide_base+".nJoints", joint_number)
            self.current_joint_number = joint_number
            self.change_main_ctrls_number(0)
            # re-create the preview mirror:
            self.create_mirror_preview()
        cmds.select(self.guide_base)


    def get_joint_locs(self):
        """ Get the list of jointLocators from the guideBase.
        """
        if cmds.objExists(self.guide_base):
            children = cmds.listRelatives(self.guide_base, allDescendents=True, type="transform")
            up_vector = self.ar.utils.createLocatorInItemPosition(self.guide_radius)  # using locator to avoid cycle error
            locs = []
            for child in children:
                # Check if the child is a joint locator, with nJoint attribute
                if cmds.attributeQuery("nJoint", node=child, exists=True):
                    locs.append(child)
            return locs, up_vector


    def aim_to_target(self, node, target, up_object):
        """ Aim the target towards the node object using the up_object(RadiusCtrl) for orientation.
        """ 
        # If it's JointEnd, unlock translateX and translateY attributes to allow unparenting to world with no translation issues.
        # The JointEnd will be unlocked after pressing the reorient button only.
        if target == self.guide_end_loc:
            cmds.setAttr(target + ".translateX", lock=False, keyable=True)
            cmds.setAttr(target + ".translateY", lock=False, keyable=True)
        father_loc = cmds.listRelatives(target, parent=True, type="transform")[0]
        cmds.parent(target, world=True)
        # Aim Constraint without maintain offset
        cmds.delete(cmds.aimConstraint(target, node, aimVector=(0, 0, 1), upVector=(0, 1, 0), worldUpType="objectrotation", worldUpVector=(0, 1, 0), worldUpObject=up_object, maintainOffset=False))
        # Get back to the original parent
        cmds.parent(target, father_loc)


    def re_orient_fkline(self, locs, up_vector):
        """ Reorient the FK line based on the locs and up_vector.
        """ 
        if locs:
            for joint_loc in locs:
                # jointLocPos = createLocatorInPosition(joint_loc)
                father = cmds.listRelatives(joint_loc, parent=True)[0]
                # Check if the father is not the guideBase
                if not father == self.guide_base:
                    self.aim_to_target(father, joint_loc, up_vector)
                # If the father is the guideBase, align the jointLoc1 to the guideBase
                if father == self.guide_base:
                    child = cmds.listRelatives(joint_loc, children=True, type="transform")[0]
                    temp_pos_loc = self.ar.utils.createLocatorInItemPosition(child)
                    # Aim guideBase and joint_loc to child
                    self.aim_to_target(self.guide_base, child, up_vector)
                    # Parenting nJoint to world and reset joint_loc position
                    cmds.parent(child, world=True)
                    for axis in self.ar.data.axes:
                        cmds.setAttr(joint_loc + ".translate" + axis, 0)
                        cmds.setAttr(joint_loc + ".rotate" + axis, 0)
                    cmds.parent(child, joint_loc)
                    # Delete the temporary locators
                    cmds.delete(up_vector)
                    cmds.delete(temp_pos_loc)
                cmds.select(self.guide_base)


    def run_re_orient_guide(self, *args):
        """ reorient dpFkLine button. 
            Each guide will point to the next guide using Radius_Ctrl position as a Object Rotation Up Vector.
        """
        # re-declaring guides names:
        self.guide_radius = self.name_guide + "_Base_RadiusCtrl"
        self.guide_end_loc = self.name_guide + "_JointEnd"
        # Check if the guideBase exists:
        if cmds.attributeQuery("guideBase", node=self.guide_base, exists=True):
            # Get the locs and up_vector:
            locs, up_vector = self.get_joint_locs()
            # Reorient the FK line:
            self.re_orient_fkline(locs, up_vector)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                ctrl_zero_grp = side+self.number_name+"_00_Ctrl_Zero_0_Grp"
                skin_joints = []
                fk_ctrls = []
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.n_joints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.number_name+"_Guide_JointLoc"+str(n+1)
                    self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                    self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    jnt = cmds.joint(name=side+self.number_name+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    self.ar.utils.setJointLabel(jnt, s+self.joint_label_add, 18, self.number_name+"_%02d"%(n))
                    skin_joints.append(jnt)
                    # create a control:
                    ctrl = self.ar.ctrls.cvControl("id_007_FkLine", side+self.number_name+"_%02d_Ctrl"%(n), r=self.radius, d=self.curve_degree, headDef=cmds.getAttr(self.base+".deformedBy"), guideSource=self.name_guide+"_JointLoc"+str(n+1), parentTag=self.get_parent_to_tag(fk_ctrls))
                    fk_ctrls.append(ctrl)
                    # zeroOut controls:
                    ctrl_zero = self.ar.utils.zeroOut([ctrl])[0]
                    # position and orientation of joint and control:
                    cmds.matchTransform(jnt, self.guide, position=True, rotation=True)
                    cmds.matchTransform(ctrl_zero, self.guide, position=True, rotation=True)
                    # hide visibility attribute:
                    cmds.setAttr(ctrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 1:
                            cmds.setAttr(ctrl_zero+".scaleX", -1)
                            cmds.setAttr(ctrl_zero+".scaleY", -1)
                            cmds.setAttr(ctrl_zero+".scaleZ", -1)
                    cmds.addAttr(ctrl, longName='scaleCompensate', attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=False)
                    cmds.setAttr(ctrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(ctrl+".scaleCompensate", jnt+".segmentScaleCompensate", force=True)
                    if n == 0:
                        self.ar.utils.originedFrom(objName=ctrl, attrString=self.base+";"+self.guide+";"+self.guide_radius)
                        ctrl_zero_grp = ctrl_zero
                    elif n == self.n_joints-1:
                        self.ar.utils.originedFrom(objName=ctrl, attrString=self.guide+";"+self.guide_end_loc)
                    else:
                        self.ar.utils.originedFrom(objName=ctrl, attrString=self.guide)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        father_joint = side+self.number_name+"_%02d_Jnt"%(n-1)
                        cmds.parent(jnt, father_joint, absolute=True)
                        # parent zeroCtrl Group to the before jntCtrl:
                        cmds.parent(ctrl_zero, side+self.number_name+"_%02d_Ctrl"%(n-1), absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_PaC")
                    cmds.scaleConstraint(ctrl, jnt, maintainOffset=True, name=jnt+"_ScC")
                    # add articulationJoint:
                    if n > 0:
                        if self.articulation:
                            articulation_joints = self.ar.utils.articulationJoint(father_joint, jnt) #could call to create corrective joints. See parameters to implement it, please.
                            self.ar.utils.setJointLabel(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_%02d_Jar"%(n))
                    cmds.select(jnt)
                    # end chain:
                    if n == self.n_joints-1:
                        self.create_end_joint(side+self.number_name)
                # work with main fk controllers
                if cmds.getAttr(self.base+".mainControls"):
                    self.add_fk_main_ctrls(side, fk_ctrls)
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [ctrl_zero_grp], [skin_joints[0]])
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
    