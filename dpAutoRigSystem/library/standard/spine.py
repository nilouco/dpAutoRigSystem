# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "Spine"
TITLE = "m011_spine"
DESCRIPTION = "m012_spineDesc"
WIKI = "03-‐-Guides#-spine"



class Spine(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        # declare variable
        self.guide_loc = None
        self.current_joint_number = 3
        # list of returned data:
        self.hips_a_items = []
        self.tips = []
        self.vv_attributes = []
        self.vv_active_attributes = []
        self.vv_master_scale_attributes = []
        self.ikfk_blend_attributes = []
        self.inner_ctrls = []
        self.outer_ctrls = []
        self.ribbon_joints = []
        self.cluster_grp = []
        self.shape_vis_attributes = []
    

    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.change_joint_number(3)
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc], 
                                   ["JointLoc1", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", attributeType='long', defaultValue=1)
        cmds.addAttr(self.guide_base, longName="style", attributeType='enum', enumName=self.ar.data.lang['m042_default']+':'+self.ar.data.lang['m026_biped'])


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_JointLoc1", r=0.5, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        # setup
        cmds.setAttr(self.line+".template", 1)
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        # parenting
        cmds.parent(self.line, self.guide_loc, self.guide_base)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".rx", -90)
        cmds.setAttr(self.guide_base+".ry", -90)
        cmds.setAttr(self.radius_ctrl+".tx", 4)

        
        
    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number >= 3:
            self.ar.opt.check_use_default_render_layer()
            self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
            if joint_number != self.current_joint_number:
                self.guide_end_loc = self.name_guide+"_JointEnd"
                if self.current_joint_number > 1:
                    # delete current point constraints:
                    for n in range(2, self.current_joint_number):
                        cmds.delete(self.name_guide+"_PaC"+str(n))
                # verify if the nJoints is greather or less than the current
                if joint_number > self.current_joint_number:
                    # add the new cvLocators:
                    for n in range(self.current_joint_number+1, joint_number+1):
                        # create another N create_curve_locator:
                        self.guide_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                        self.line = cmds.joint(name=self.name_guide+"_JGuide"+str(n), radius=0.001)
                        # set its nJoint value as n:
                        cmds.setAttr(self.line+".template", 1)
                        cmds.setAttr(self.guide_loc+".nJoint", n)
                        # parent its group to the first cvJointLocator:
                        self.guide_loc_grp = cmds.group(self.guide_loc, name=self.guide_loc+"_Grp")
                        cmds.parent(self.guide_loc_grp, self.name_guide+"_JointLoc"+str(n-1), relative=True)
                        cmds.parent(self.line, self.name_guide+"_JGuide"+str(n-1), relative=True)
                        cmds.setAttr(self.guide_loc_grp+".translateZ", 2)
                        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
                        if n > 2:
                            cmds.parent(self.guide_loc_grp, self.name_guide+"_JointLoc1", absolute=True)
                        self.add_node_to_guide_net([self.guide_loc], ["JointLoc"+str(n)])
                elif joint_number < self.current_joint_number:
                    # re-parent cvEndJoint:
                    self.guide_loc = self.name_guide+"_JointLoc" + str(joint_number)
                    cmds.parent(self.guide_end_loc, world=True)
                    # delete difference of nJoints:
                    for n in range(joint_number, self.current_joint_number):
                        # re-parent the children guides:
                        guide_bellow_children = self.ar.utils.get_guide_children(self.name_guide+"_JointLoc"+str(n+1)+"_Grp")
                        if guide_bellow_children:
                            for guide_child in guide_bellow_children:
                                cmds.parent(guide_child, self.guide_loc)
                        cmds.delete(self.name_guide+"_JointLoc"+str(n+1)+"_Grp")
                        self.remove_attr_from_guide_net(["JointLoc"+str(n+1)])
                    cmds.delete(self.name_guide+"_JGuide"+str(joint_number+1))
                # re-parent cvEndJoint:
                cmds.parent(self.guide_end_loc, self.guide_loc)
                cmds.setAttr(self.guide_end_loc+".tz", 1.3)
                cmds.setAttr(self.guide_end_loc+".visibility", 0)
                # re-create parentConstraints:
                if joint_number > 1:
                    for n in range(2, joint_number):
                        pac = cmds.parentConstraint(self.name_guide+"_JointLoc1", self.guide_end_loc, self.name_guide+"_JointLoc"+str(n)+"_Grp", name=self.name_guide+"_PaC"+str(n), maintainOffset=True)[0]
                        n_parent_value = (n-1) / float(joint_number-1)
                        cmds.setAttr(pac+".Guide_JointLoc1W0", 1-n_parent_value)
                        cmds.setAttr(pac+".Guide_JointEndW1", n_parent_value)
                        self.ar.ctrls.set_lock_hide([self.name_guide+"_JointLoc"+ str(n)], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                # actualise the nJoints in the main:
                cmds.setAttr(self.guide_base+".nJoints", joint_number)
                self.current_joint_number = joint_number
                # re-create the preview mirror:
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.change_joint_number(3)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            style = cmds.getAttr(self.guide_base+".style")
            # naming main controls:
            hips_name  = self.ar.data.lang['c100_bottom']
            chest_name = self.ar.data.lang['c099_top']
            base_name = self.ar.data.lang['c106_base']
            end_name = self.ar.data.lang['c120_tip']
            if style == 1: #biped
                hips_name  = self.ar.data.lang['c027_hips']
                chest_name = self.ar.data.lang['c028_chest']
            # run for all sides
            for s, side in enumerate(self.sides):
                attr_name_lower = self.ar.utils.get_attr_name_lower(side, self.number_name)
                self.base = side+self.number_name+'_Guide_Base'
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                # create controls:
                self.hips_a_ctrl = self.ar.ctrls.create_controller("id_041_SpineHipsA", ctrl_name=side+self.number_name+"_"+hips_name+"A_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc1")
                self.chest_a_ctrl = self.ar.ctrls.create_controller("id_044_SpineChestA", ctrl_name=side+self.number_name+"_"+chest_name+"A_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc"+str(self.n_joints))
                # create start and end Fk controls:
                self.hips_fk_ctrl = self.ar.ctrls.create_controller("id_067_SpineFk", ctrl_name=side+self.number_name+"_"+hips_name+"A_Fk_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", guide_source=self.name_guide+"_JointLoc1")
                self.chest_fk_ctrl = self.ar.ctrls.create_controller("id_067_SpineFk", ctrl_name=side+self.number_name+"_"+chest_name+"A_Fk_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", guide_source=self.name_guide+"_JointLoc"+str(self.n_joints))
                # optimize controls CV shapes:
                temp_hips_a_cluster = cmds.cluster(self.hips_a_ctrl)[1]
                cmds.setAttr(temp_hips_a_cluster+".scaleY", 0.25)
                cmds.delete(self.hips_a_ctrl, constructionHistory=True)
                temp_chest_a_cluster = cmds.cluster(self.chest_a_ctrl)[1]
                cmds.setAttr(temp_chest_a_cluster+".scaleY", 0.4)
                cmds.delete(self.chest_a_ctrl, constructionHistory=True)
                hips_fk_ctrl_cv_pos = -0.4*self.radius
                if style == 1: #biped
                    hips_fk_ctrl_cv_pos = 0.4*self.radius
                cmds.move(0, hips_fk_ctrl_cv_pos, 0, self.hips_fk_ctrl+"0Shape.cv[0:5]", relative=True, worldSpace=True, worldSpaceDistance=True)
                
                self.hips_b_ctrl = self.ar.ctrls.create_controller("id_042_SpineHipsB", side+self.number_name+"_"+hips_name+"B_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guide_source=self.name_guide+"_Base")
                self.chest_b_ctrl = self.ar.ctrls.create_controller("id_045_SpineChestB", side+self.number_name+"_"+chest_name+"B_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guide_source=self.name_guide+"_JointLoc"+str(self.n_joints))
                cmds.addAttr(self.hips_a_ctrl, longName=attr_name_lower+'_'+self.ar.data.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hips_a_ctrl, longName=attr_name_lower+'Active_'+self.ar.data.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hips_a_ctrl, longName=attr_name_lower+'_masterScale_'+self.ar.data.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hips_a_ctrl, longName=attr_name_lower+'Fk_ikFkBlend', attributeType="float", min=0, max=1, defaultValue=1, keyable=True)
                self.hips_a_items.append(self.hips_a_ctrl)
                self.vv_attributes.append(attr_name_lower+'_'+self.ar.data.lang['c031_volumeVariation'])
                self.vv_active_attributes.append(attr_name_lower+'Active_'+self.ar.data.lang['c031_volumeVariation'])
                self.vv_master_scale_attributes.append(attr_name_lower+'_masterScale_'+self.ar.data.lang['c031_volumeVariation'])
                self.ikfk_blend_attributes.append(attr_name_lower+'Fk_ikFkBlend')
                
                # base and end controls:
                self.base_ctrl = self.ar.ctrls.create_controller("id_089_SpineBase", side+self.number_name+"_"+base_name+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, dir="+X", guide_source=self.name_guide+"_JointLoc1")
                self.tip_ctrl = self.ar.ctrls.create_controller("id_090_SpineTip", side+self.number_name+"_"+end_name+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, dir="+X", guide_source=self.name_guide+"_JointLoc"+str(self.n_joints))
                self.tips.append(self.tip_ctrl)
                # optimize control CV shapes:
                temp_base_cluster = cmds.cluster(self.base_ctrl)[1]
                temp_tip_cluster = cmds.cluster(self.tip_ctrl)[1]
                if style == 0: #default
                    cmds.setAttr(temp_base_cluster+".translateY", 0.2*self.radius)
                    cmds.setAttr(temp_tip_cluster+".translateY", -0.2*self.radius)
                else:
                    cmds.setAttr(temp_base_cluster+".translateY", -0.2*self.radius)
                    cmds.setAttr(temp_tip_cluster+".translateY", 0.2*self.radius)
                cmds.delete([self.base_ctrl, self.tip_ctrl], constructionHistory=True)
                # shape visibility
                cmds.addAttr(self.hips_a_ctrl, longName=attr_name_lower+end_name+self.ar.data.lang['c126_display'], attributeType="long", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(self.hips_a_ctrl, longName=attr_name_lower+base_name+self.ar.data.lang['c126_display'], attributeType="long", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.connectAttr(self.hips_a_ctrl+"."+attr_name_lower+end_name+self.ar.data.lang['c126_display'], cmds.listRelatives(self.tip_ctrl, children=True, type="shape")[0]+".visibility", force=True)
                cmds.connectAttr(self.hips_a_ctrl+"."+attr_name_lower+base_name+self.ar.data.lang['c126_display'], cmds.listRelatives(self.base_ctrl, children=True, type="shape")[0]+".visibility", force=True)
                self.shape_vis_attributes.append(attr_name_lower+end_name+self.ar.data.lang['c126_display'])
                self.shape_vis_attributes.append(attr_name_lower+base_name+self.ar.data.lang['c126_display'])

                # Setup axis order
                if self.rigType == "quadruped" or style == 2: #quadruped
                    cmds.setAttr(self.hips_a_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.hips_b_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chest_a_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chest_b_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.hips_fk_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chest_fk_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.base_ctrl + ".rotateOrder", 1)
                    cmds.setAttr(self.tip_ctrl + ".rotateOrder", 1)
                    cmds.rotate(90, 0, 0, self.hips_a_ctrl, self.hips_b_ctrl, self.chest_a_ctrl, self.chest_b_ctrl, self.hips_fk_ctrl, self.chest_fk_ctrl, self.base_ctrl, self.tip_ctrl)
                    cmds.makeIdentity(self.hips_a_ctrl, self.hips_b_ctrl, self.chest_a_ctrl, self.chest_b_ctrl, self.hips_fk_ctrl, self.chest_fk_ctrl, self.base_ctrl, self.tip_ctrl, apply=True, rotate=True)
                else:
                    cmds.setAttr(self.hips_a_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.hips_b_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chest_a_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chest_b_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.hips_fk_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chest_fk_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.base_ctrl + ".rotateOrder", 3)
                    cmds.setAttr(self.tip_ctrl + ".rotateOrder", 3)
                
                # Keep a list of ctrls we want to colorize a certain way
                self.inner_ctrls.append([self.hips_b_ctrl, self.chest_b_ctrl])
                self.outer_ctrls.append([self.hips_a_ctrl, self.chest_a_ctrl, self.hips_fk_ctrl, self.chest_fk_ctrl])
                
                # organize hierarchy:
                cmds.parent(self.hips_b_ctrl, self.hips_a_ctrl)
                cmds.parent(self.chest_b_ctrl, self.chest_a_ctrl)
                cmds.parent(self.hips_fk_ctrl, self.hips_a_ctrl)
                cmds.parent(self.chest_fk_ctrl, self.chest_a_ctrl)
                cmds.parent(self.base_ctrl, self.hips_b_ctrl, relative=True)
                cmds.parent(self.tip_ctrl, self.chest_b_ctrl, relative=True)
                if style == 0: #default
                    cmds.rotate(-90, 0, 0, self.hips_a_ctrl, self.chest_a_ctrl)
                    cmds.makeIdentity(self.hips_a_ctrl, self.chest_a_ctrl, apply=True, rotate=True)
                # position of controls:
                guide_bottom_loc = side+self.number_name+"_Guide_JointLoc1"
                guide_top_loc = side+self.number_name+"_Guide_JointLoc"+str(self.n_joints)
                # snap controls to guideLocators:
                cmds.matchTransform(self.hips_a_ctrl, guide_bottom_loc, position=True, rotation=True)
                cmds.matchTransform(self.chest_a_ctrl, guide_top_loc, position=True, rotation=True)
                
                # change axis orientation for biped style
                if style == 1: #biped
                    cmds.rotate(0, 0, 0, self.hips_a_ctrl, self.chest_a_ctrl)
                    cmds.makeIdentity(self.hips_a_ctrl, self.chest_a_ctrl, apply=True, rotate=True)
                cmds.parent(self.chest_a_ctrl, self.hips_a_ctrl)
                
                # create_zero_out transformations:
                hips_a_ctrl_zero, chest_a_zero, chest_b_grp, hips_fk_ctrl_zero, chest_fk_ctrl_zero = self.ar.utils.create_zero_out([self.hips_a_ctrl, self.chest_a_ctrl, self.chest_b_ctrl, self.hips_fk_ctrl, self.chest_fk_ctrl])
                chest_b_grp = cmds.rename(chest_b_grp, chest_b_grp.replace("Zero", "Grp"))
                chest_b_zero = self.ar.utils.create_zero_out([chest_b_grp])[0]
                base_ctrl_zero = self.ar.utils.create_zero_out([self.base_ctrl])[0]
                tip_ctrl_zero = self.ar.utils.create_zero_out([self.tip_ctrl])[0]
                self.ar.ctrls.set_lock_hide([self.hips_a_ctrl, self.hips_b_ctrl, self.chest_a_ctrl, self.chest_b_ctrl, self.hips_fk_ctrl, self.chest_fk_ctrl], ['v'], l=False)
                # modify the pivots of chest controls:
                up_pivot_pos = cmds.xform(side+self.number_name+"_Guide_JointLoc"+str(self.n_joints-1), query=True, worldSpace=True, translation=True)
                cmds.move(up_pivot_pos[0], up_pivot_pos[1], up_pivot_pos[2], self.chest_a_ctrl+".scalePivot", self.chest_a_ctrl+".rotatePivot")
                
                # add originedFrom attributes to hipsA, hipsB and chestB:
                self.ar.utils.set_origined_from_attr(self.hips_a_ctrl, self.base+";"+self.guide_radius)
                self.ar.utils.set_origined_from_attr(self.base_ctrl, guide_bottom_loc)
                self.ar.utils.set_origined_from_attr(self.tip_ctrl, guide_top_loc)

                # create base and end joints:
                cmds.select(clear=True)
                base_joint = cmds.joint(name=side+self.number_name+"_00_"+self.ar.data.lang['c106_base']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(base_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                tip_joint = cmds.joint(name=side+self.number_name+"_"+str(self.n_joints+1).zfill(2)+"_"+self.ar.data.lang['c120_tip']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(tip_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.ar.utils.set_joint_label(base_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c106_base'])
                self.ar.utils.set_joint_label(tip_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c120_tip'])
                # Base and end controllers:
                cmds.parentConstraint(self.base_ctrl, base_joint, maintainOffset=False, name=base_joint+"_PaC")
                cmds.scaleConstraint(self.base_ctrl, base_joint, maintainOffset=True, name=base_joint+"_ScC")
                cmds.parentConstraint(self.tip_ctrl, tip_joint, maintainOffset=False, name=tip_joint+"_PaC")
                cmds.scaleConstraint(self.tip_ctrl, tip_joint, maintainOffset=True, name=tip_joint+"_ScC")

                # create a simple spine ribbon:
                ribbons = self.ar.ctrls.create_simple_ribbon(name=side+self.number_name, total_joints=(self.n_joints-1), joint_label_number=(s+self.joint_label_add), joint_label_name=self.number_name)
                ribbon_nurbs_plane = ribbons[0]
                ribbon_nurbs_plane_shape = ribbons[1]
                ribbon_joints_grps = ribbons[2]
                self.ribbon_joints = ribbons[3]
                # position of ribbon nurbs plane:
                cmds.setAttr(ribbon_nurbs_plane+".tz", -4)
                cmds.move(0, 0, 0, ribbon_nurbs_plane+".scalePivot", ribbon_nurbs_plane+".rotatePivot")
                cmds.rotate(90, 90, 0, ribbon_nurbs_plane)
                cmds.makeIdentity(ribbon_nurbs_plane, apply=True, translate=True, rotate=True)
                down_loc_pos = cmds.xform(side+self.number_name+"_Guide_JointLoc1", query=True, worldSpace=True, translation=True)
                upLocPos = cmds.xform(side+self.number_name+"_Guide_JointLoc"+str(self.n_joints), query=True, worldSpace=True, translation=True)
                cmds.move(down_loc_pos[0], down_loc_pos[1], down_loc_pos[2], ribbon_nurbs_plane)
                # create up and down clusters:
                down_clusters = cmds.cluster(ribbon_nurbs_plane+".cv[0:3][0:1]", name=side+self.number_name+'_Down_Cls')
                up_clusters = cmds.cluster(ribbon_nurbs_plane+".cv[0:3]["+str(self.n_joints)+":"+str(self.n_joints+1)+"]", name=side+self.number_name+'_Up_Cls')
                down_cluster = down_clusters[1]
                up_cluster = up_clusters[1]
                self.to_ids.extend([down_clusters[0], up_clusters[0]])
                # get positions of joints from ribbon nurbs plane:
                start_ribbon_joint_pos = cmds.xform(side+self.number_name+"_01_Jnt", query=True, worldSpace=True, translation=True)
                end_ribbon_joint_pos = cmds.xform(side+self.number_name+"_%02d_Jnt"%(self.n_joints), query=True, worldSpace=True, translation=True)
                # move pivots of clusters to start and end positions:
                cmds.move(start_ribbon_joint_pos[0], start_ribbon_joint_pos[1], start_ribbon_joint_pos[2], down_cluster+".scalePivot", down_cluster+".rotatePivot")
                cmds.move(end_ribbon_joint_pos[0], end_ribbon_joint_pos[1], end_ribbon_joint_pos[2], up_cluster+".scalePivot", up_cluster+".rotatePivot")
                # snap clusters to guideLocators:
                cmds.matchTransform(down_cluster, guide_bottom_loc, position=True, rotation=True)
                cmds.matchTransform(up_cluster, guide_top_loc, position=True, rotation=True)
                # rotate clusters to compensate guide:
                up_cluster_rot = cmds.xform(up_cluster, query=True, worldSpace=True, rotation=True)
                down_cluster_rot = cmds.xform(down_cluster, query=True, worldSpace=True, rotation=True)
                cmds.xform(up_cluster, worldSpace=True, rotation=(up_cluster_rot[0]+90, up_cluster_rot[1], up_cluster_rot[2]))
                cmds.xform(down_cluster, worldSpace=True, rotation=(down_cluster_rot[0]+90, down_cluster_rot[1], down_cluster_rot[2]))
                # scaleY of the clusters in order to avoid great extremity deforms:
                ribbon_height = self.ar.utils.create_dist_between(side+self.number_name+"_Guide_JointLoc"+str(self.n_joints), side+self.number_name+"_Guide_JointLoc1", keep=False)[0]
                cmds.setAttr(up_cluster+".sy", ribbon_height / 10)
                cmds.setAttr(down_cluster+".sy", ribbon_height / 10)
                # parent clusters in controls (up and down):
                cmds.parentConstraint(self.hips_b_ctrl, down_cluster, maintainOffset=True, name=down_cluster+"_PaC")
                cmds.parentConstraint(self.chest_b_ctrl, up_cluster, maintainOffset=True, name=up_cluster+"_PaC")
                # organize a group of clusters:
                spine_clusters_grp = cmds.group(name=side+self.number_name+"_Clusters_Grp", empty=True)
                cmds.parent(down_cluster, up_cluster, spine_clusters_grp, relative=True)
                # make ribbon joints groups scalable:
                middle_scale_y_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_MiddleScaleY_MD")
                cmds.setAttr(middle_scale_y_md+".operation", 2)
                cmds.setAttr(middle_scale_y_md+".input1X", 1)
                size_ctrls = [self.hips_b_ctrl]
                size_grps = []
                for r, ribbon_joint_grp in enumerate(ribbon_joints_grps):
                    size_grps.append(cmds.group(ribbon_joint_grp, name=ribbon_joint_grp.replace("_Grp", "_Size_Grp")))
                    scale_grp = cmds.group(size_grps[-1], name=ribbon_joint_grp.replace("_Grp", "_Scale_Grp"))
                    cmds.scaleConstraint(spine_clusters_grp, scale_grp, maintainOffset=True, name=scale_grp+"_ScC")
                    if ((r > 0) and (r < (len(ribbon_joints_grps) - 1))):
                        self.ar.utils.add_attr_to_items([scale_grp], self.ar.utils.ignore_transform_io_attr)
                        self.ar.ctrls.direct_connect(scale_grp, ribbon_joint_grp, ['sx', 'sy', 'sz'])
                        cmds.connectAttr(middle_scale_y_md+".outputX", self.ribbon_joints[r]+".scaleY", force=True)
                        cmds.connectAttr(scale_grp+".scaleY", middle_scale_y_md+".input2X", force=True)
                        size_ctrls.append(side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(r)+"_Ctrl")
                size_ctrls.append(self.chest_b_ctrl)
                # calculate the distance to volumeVariation:
                arc_len_shape = cmds.createNode('arcLengthDimension', name=side+self.number_name+"_Rbn_ArcLenShape")
                arc_len_father = cmds.listRelatives(arc_len_shape, parent=True)[0]
                arcLen = cmds.rename(arc_len_father, side+self.number_name+"_Rbn_ArcLen")
                arc_len_shape = cmds.listRelatives(arcLen, children=True, shapes=True)[0]
                cmds.setAttr(arcLen+'.visibility', 0)
                # connect nurbsPlaneShape to arcLength node:
                cmds.connectAttr(ribbon_nurbs_plane_shape+'.worldSpace[0]', arc_len_shape+'.nurbsGeometry')
                cmds.setAttr(arc_len_shape+'.vParamValue', 1)
                # avoid undesired squash if rotateZ the nurbsPlane:
                cmds.setAttr(arc_len_shape+'.uParamValue', 0.5)
                arc_len_value = cmds.getAttr(arc_len_shape+'.arcLengthInV')
                # create a multiplyDivide to output the squashStretch values:
                ribbon_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Rbn_MD")
                cmds.connectAttr(arc_len_shape+'.arcLengthInV', ribbon_md+'.input2X')
                cmds.setAttr(ribbon_md+'.input1X', arc_len_value)
                cmds.setAttr(ribbon_md+'.operation', 2)
                # create a blendColor, a condition and a multiplyDivide in order to get the correct result value of volumeVariation:
                ribbon_bc = cmds.createNode('blendColors', name=side+self.number_name+"_Rbn_BC")
                cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'_'+self.ar.data.lang['c031_volumeVariation'], ribbon_bc+'.blender')
                ribbon_cnd = cmds.createNode('condition', name=side+self.number_name+'_Rbn_Cond')
                cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Active_'+self.ar.data.lang['c031_volumeVariation'], ribbon_cnd+'.firstTerm')
                cmds.connectAttr(ribbon_bc+'.outputR', ribbon_cnd+'.colorIfTrueR')
                cmds.connectAttr(ribbon_md+'.outputX', ribbon_bc+'.color1R')
                ribbon_vv_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Rbn_VV_MD")
                cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'_masterScale_'+self.ar.data.lang['c031_volumeVariation'], ribbon_vv_md+'.input2X')
                cmds.connectAttr(ribbon_vv_md+'.outputX', ribbon_cnd+'.colorIfFalseR')
                cmds.setAttr(ribbon_vv_md+'.operation', 2)
                cmds.setAttr(ribbon_bc+'.color2R', 1)
                cmds.setAttr(ribbon_cnd+".secondTerm", 1)
                # middle ribbon setup:
                for n in range(1, self.n_joints - 1):
                    if style == 0: #default
                        middle_ctrl = self.ar.ctrls.create_controller("id_043_SpineMiddle", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc"+str(n+1))
                        middle_fk_ctrl = self.ar.ctrls.create_controller("id_067_SpineFk", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc"+str(n+1))
                        cmds.setAttr(middle_ctrl+".rotateOrder", 4)
                        cmds.setAttr(middle_fk_ctrl+".rotateOrder", 4)
                        cmds.rotate(0, 0, 90, middle_ctrl, middle_fk_ctrl)
                        cmds.makeIdentity(middle_ctrl, middle_fk_ctrl, apply=True, rotate=True)
                    else: #biped or quadruped
                        middle_ctrl = self.ar.ctrls.create_controller("id_043_SpineMiddle", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guide_source=self.name_guide+"_JointLoc"+str(n+1))
                        middle_fk_ctrl = self.ar.ctrls.create_controller("id_067_SpineFk", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guide_source=self.name_guide+"_JointLoc"+str(n+1))
                        cmds.setAttr(middle_ctrl+".rotateOrder", 3)
                        cmds.setAttr(middle_fk_ctrl+".rotateOrder", 3)
                    self.inner_ctrls[s].append(middle_ctrl)
                    self.outer_ctrls[s].append(middle_fk_ctrl)
                    self.ar.ctrls.set_lock_hide([middle_ctrl, middle_fk_ctrl], ['sx', 'sy', 'sz'])
                    cmds.setAttr(middle_ctrl+'.visibility', keyable=False)
                    cmds.setAttr(middle_fk_ctrl+'.visibility', keyable=False)
                    cmds.parent(middle_ctrl, self.hips_a_ctrl)
                    guide_middle_loc = side+self.number_name+"_Guide_JointLoc"+str(n + 1)
                    cmds.matchTransform(middle_ctrl, guide_middle_loc, position=True, rotation=True)
                    cmds.matchTransform(middle_fk_ctrl, guide_middle_loc, position=True, rotation=True)
                    if style == 1: #biped
                        cmds.rotate(0, 0, 0, middle_ctrl, middle_fk_ctrl)
                    if self.rigType == "quadruped": #quadruped
                        cmds.rotate(90, 0, 0, middle_ctrl, middle_fk_ctrl)
                        cmds.makeIdentity(middle_ctrl, middle_fk_ctrl, apply=True, rotate=True)
                    middle_ctrl_grp = self.ar.utils.create_zero_out([middle_ctrl])[0]
                    middle_ctrl_grp = cmds.rename(middle_ctrl_grp, middle_ctrl_grp.replace("Zero", "Grp"))
                    middle_ctrl_zero = self.ar.utils.create_zero_out([middle_ctrl_grp])[0]
                    middle_fk_ctrl_zero = self.ar.utils.create_zero_out([middle_fk_ctrl])[0]
                    middle_clusters = cmds.cluster(ribbon_nurbs_plane+".cv[0:3]["+str(n+1)+"]", name=side+self.number_name+'_Middle_Cls')
                    middle_cluster = middle_clusters[1]
                    self.to_ids.append(middle_clusters[0])
                    middleLocPos = cmds.xform(side+self.number_name+"_Guide_JointLoc"+str(n), query=True, worldSpace=True, translation=True)
                    cmds.matchTransform(middle_cluster, guide_middle_loc, position=True, rotation=True)
                    middle_cluster_rot = cmds.xform(middle_cluster, query=True, worldSpace=True, rotation=True)
                    cmds.xform(middle_cluster, worldSpace=True, rotation=(middle_cluster_rot[0]+90, middle_cluster_rot[1], middle_cluster_rot[2]))
                    cmds.parentConstraint(middle_ctrl, middle_cluster, maintainOffset=True, name=middle_cluster+"_PaC")
                    # parenting constraints like guide locators:
                    pac = cmds.parentConstraint(self.hips_b_ctrl, self.chest_b_ctrl, middle_ctrl_zero, name=middle_ctrl+"_PaC", maintainOffset=True)[0]
                    n_parent_value = (n) / float(self.n_joints-1)
                    cmds.setAttr(pac+"."+self.hips_b_ctrl+"W0", 1-n_parent_value)
                    cmds.setAttr(pac+"."+self.chest_b_ctrl+"W1", n_parent_value)
                    cmds.parent(middle_cluster, spine_clusters_grp, relative=True)
                    # add originedFrom attribute to this middle ctrl:
                    middle_orig_grp = cmds.group(empty=True, name=side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_OrigFrom_Grp")
                    self.ar.utils.set_origined_from_attr(middle_orig_grp, guide_middle_loc)
                    cmds.parentConstraint(self.ribbon_joints[n], middle_orig_grp, maintainOffset=False, name=middle_orig_grp+"_PaC")
                    cmds.parent(middle_orig_grp, self.hips_a_ctrl)
                    # apply volumeVariation to joints in the middle ribbon setup:
                    cmds.connectAttr(ribbon_cnd+'.outColorR', self.ribbon_joints[n]+'.scaleX')
                    cmds.connectAttr(ribbon_cnd+'.outColorR', self.ribbon_joints[n]+'.scaleZ')
                    # create intensity attribute to drive joint with more force in horizontal:
                    cmds.addAttr(middle_ctrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                    cmds.addAttr(middle_fk_ctrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                    father_joint = cmds.listRelatives(self.ribbon_joints[n], allParents=True)[0]
                    int_rev = cmds.createNode("reverse", name=side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_"+self.ar.data.lang['c049_intensity'].capitalize()+"_Rev")
                    middle_int_bc = cmds.createNode("blendColors", name=side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_"+self.ar.data.lang['c049_intensity'].capitalize()+"_BC")
                    self.to_ids.extend([int_rev, middle_int_bc])
                    middle_int_pac = cmds.parentConstraint(middle_ctrl, father_joint, self.ribbon_joints[n], maintainOffset=True, name=self.ribbon_joints[n]+"_"+self.ar.data.lang['c049_intensity'].capitalize()+"_PaC")[0]
                    cmds.connectAttr(middle_fk_ctrl+"."+self.ar.data.lang['c049_intensity'], middle_int_bc+".color1R", force=True)
                    cmds.connectAttr(middle_ctrl+"."+self.ar.data.lang['c049_intensity'], middle_int_bc+".color2R", force=True)
                    cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Fk_ikFkBlend', middle_int_bc+".blender", force=True)
                    cmds.connectAttr(middle_int_bc+".outputR", middle_int_pac+"."+middle_ctrl+"W0", force=True)
                    cmds.connectAttr(middle_ctrl+"."+self.ar.data.lang['c049_intensity'], int_rev+".inputX", force=True)
                    cmds.connectAttr(int_rev+".outputX", middle_int_pac+"."+father_joint+"W1", force=True)
                    # fk middle control hierarchy:
                    if n == 1: #first middle
                        cmds.parent(middle_fk_ctrl_zero, self.hips_fk_ctrl)
                    else:
                        cmds.parent(middle_fk_ctrl_zero, side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n-1)+"_Fk_Ctrl")
                    # build fk setup:
                    middle_ctrl_grp_pac = cmds.parentConstraint(middle_ctrl_zero, middle_fk_ctrl, middle_ctrl_grp, maintainOffset=True, name=middle_ctrl_grp+"_IkFkBlend_PaC")[0]
                    if n == 1:
                        ikfk_blend_rev = cmds.createNode('reverse', name=side+self.number_name+"_IkFkBlend_Rev")
                        self.to_ids.append(ikfk_blend_rev)
                        cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Fk_ikFkBlend', ikfk_blend_rev+".inputX", force=True)
                    # connecting ikFkBlend using the reverse node:
                    cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Fk_ikFkBlend', middle_ctrl_grp_pac+"."+middle_fk_ctrl+"W1", force=True)
                    cmds.connectAttr(ikfk_blend_rev+'.outputX', middle_ctrl_grp_pac+"."+middle_ctrl_zero+"W0", force=True)
                    # ikFkBlend visibility:
                    cmds.connectAttr(ikfk_blend_rev+'.outputX', middle_ctrl_zero+".visibility", force=True)
                
                # finishing ikFkBlend:
                chest_a_ctrl_shape = cmds.listRelatives(self.chest_a_ctrl, children=True, type="shape")[0]
                chest_b_ctrl_shape = cmds.listRelatives(self.chest_b_ctrl, children=True, type="shape")[0]
                cmds.parent(chest_fk_ctrl_zero, middle_fk_ctrl)
                chest_ctrl_grp_pac = cmds.parentConstraint(chest_b_zero, self.chest_fk_ctrl, chest_b_grp, maintainOffset=True, name=chest_b_grp+"_IkFkBlend_PaC")[0]
                cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Fk_ikFkBlend', chest_ctrl_grp_pac+"."+self.chest_fk_ctrl+"W1", force=True)
                cmds.connectAttr(ikfk_blend_rev+'.outputX', chest_ctrl_grp_pac+"."+chest_b_zero+"W0", force=True)
                cmds.connectAttr(ikfk_blend_rev+'.outputX', chest_a_ctrl_shape+".visibility", force=True)
                cmds.connectAttr(ikfk_blend_rev+'.outputX', chest_b_ctrl_shape+".visibility", force=True)
                cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Fk_ikFkBlend', hips_fk_ctrl_zero+".visibility", force=True)
                cmds.connectAttr(self.hips_a_ctrl+'.'+attr_name_lower+'Fk_ikFkBlend', chest_fk_ctrl_zero+".visibility", force=True)
                
                # parent tag
                self.add_parent_tag_info()

                # adding size feature:
                for a, b in zip(size_ctrls, size_grps):
                    self.connect_size_axes(a, b)

                # update spine volume variation setup
                cmds.setAttr(ribbon_vv_md+'.input1X', cmds.getAttr(ribbon_md+'.outputX')) #currentVV
                # organize groups:
                self.create_hook_setup(side, [hips_a_ctrl_zero], [spine_clusters_grp], [side+self.number_name+"_Rbn_RibbonJoint_Grp", arcLen, base_joint, tip_joint])
                self.cluster_grp.append(self.scalable_hook_grp)
                # lockHide scale of up and down controls:
                self.ar.ctrls.set_lock_hide([self.hips_a_ctrl, self.hips_b_ctrl, self.chest_a_ctrl, self.chest_b_ctrl, self.hips_fk_ctrl, self.chest_fk_ctrl], ['sx', 'sy', 'sz'])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.add_attr_to_items([middle_orig_grp], self.ar.utils.ignore_transform_io_attr)
                self.to_ids.extend([middle_scale_y_md, arcLen, ribbon_md, ribbon_bc, ribbon_cnd, ribbon_vv_md])
                self.ar.custom_attr.add_attr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID


    def add_parent_tag_info(self):
        """ Set the parentTag connections for existing controllers.
        """
        for i in range(2, len(self.inner_ctrls[0])-1):
            cmds.connectAttr(self.inner_ctrls[0][i+1]+".message", self.inner_ctrls[0][i]+".parentTag", force=True) #middles
        for j in range(4, len(self.outer_ctrls[0])-1):
            cmds.connectAttr(self.outer_ctrls[0][j+1]+".message", self.outer_ctrls[0][j]+".parentTag", force=True) #fks
        cmds.connectAttr(self.inner_ctrls[0][2]+".message", self.hips_b_ctrl+".parentTag", force=True)
        cmds.connectAttr(self.hips_b_ctrl+".message", self.hips_a_ctrl+".parentTag", force=True)
        cmds.connectAttr(self.hips_b_ctrl+".message", self.base_ctrl+".parentTag", force=True)
        cmds.connectAttr(self.outer_ctrls[0][4]+".message", self.hips_fk_ctrl+".parentTag", force=True)
        cmds.connectAttr(self.chest_fk_ctrl+".message", self.outer_ctrls[0][-1]+".parentTag", force=True)
        cmds.connectAttr(self.chest_b_ctrl+".message", self.inner_ctrls[0][-1]+".parentTag", force=True)
        cmds.connectAttr(self.tip_ctrl+".message", self.chest_fk_ctrl+".parentTag", force=True)
        cmds.connectAttr(self.chest_b_ctrl+".message", self.tip_ctrl+".parentTag", force=True)
        cmds.connectAttr(self.chest_a_ctrl+".message", self.chest_b_ctrl+".parentTag", force=True)


    def connect_size_axes(self, from_node, to_node):
        """ Just connect sizeXYZ to scaleXYZ of given nodes.
        """
        for axis in self.ar.data.axes:
            if not cmds.objExists(from_node+".size"+axis):
                cmds.addAttr(from_node, longName="size"+axis, attributeType="float", defaultValue=1, keyable=True)
            cmds.connectAttr(from_node+".size"+axis, to_node+".scale"+axis, force=True)


    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "hipsAList": self.hips_a_items,
                            "tipList": self.tips,
                            "volumeVariationAttrList": self.vv_attributes,
                            "ActiveVolumeVariationAttrList": self.vv_active_attributes,
                            "MasterScaleVolumeVariationAttrList": self.vv_master_scale_attributes,
                            "IkFkBlendAttrList": self.ikfk_blend_attributes,
                            "InnerCtrls": self.inner_ctrls,
                            "OuterCtrls": self.outer_ctrls,
                            "jointList": self.ribbon_joints,
                            "scalableGrp": self.cluster_grp,
                            "shapeVisAttrList": self.shape_vis_attributes
                        }
