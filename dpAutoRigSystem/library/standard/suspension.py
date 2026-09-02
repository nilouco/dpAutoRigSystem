# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Suspension"
TITLE = "m153_suspension"
DESCRIPTION = "m154_suspensionDesc"
WIKI = "03-‐-Guides#-suspension"



class Suspension(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.add_node_to_guide_net([self.guide_a_loc, self.guide_b_loc], 
                                   ["JointLocA", "JointLocB"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="fatherB", dataType='string')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_a_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_JointLocA", r=0.3, d=1, guide=True)
        self.guide_b_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_JointLocB", r=0.3, d=1, guide=True)
        # joints
        self.line_a = cmds.joint(name=self.name_guide+"_line_a", radius=0.001)
        self.line_b = cmds.joint(name=self.name_guide+"_line_b", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_a, self.line_b])
        cmds.setAttr(self.guide_b_loc+".tz", 3)
        cmds.setAttr(self.guide_b_loc+".rotateX", 180)
        # parenting
        cmds.parent(self.line_a, self.guide_a_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_b_loc, self.guide_a_loc)
        # edit
        cmds.parentConstraint(self.guide_a_loc, self.line_a, maintainOffset=False, name=self.line_a+"_PaC")
        cmds.parentConstraint(self.guide_b_loc, self.line_b, maintainOffset=False, name=self.line_b+"_PaC")
        cmds.scaleConstraint(self.guide_a_loc, self.line_a, maintainOffset=False, name=self.line_a+"_ScC")
        cmds.scaleConstraint(self.guide_b_loc, self.line_b, maintainOffset=False, name=self.line_b+"_ScC")
        cmds.transformLimits(self.guide_b_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_b_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
    
    def load_father_b(self, *args):
        """ Loads the selected node to fatherBTextField in selectedModuleLayout.
        """
        selection = cmds.ls(selection=True)
        if selection:
            if cmds.objExists(selection[0]):
                cmds.setAttr(self.guide_base+".fatherB", selection[0], type='string')
                if self.ar.data.ui_state:
                    cmds.textField('edit_guide_fatherb_tf', edit=True, text=selection[0])
    
    
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.suspension_b_ctrl_grps, self.father_b_items, self.ctrl_hook_grps = [], [], []
            # run for all sides
            for s, side in enumerate(self.sides):
                # declare guide:
                self.base = side+self.number_name+'_Guide_Base'
                self.guide_a_loc = side+self.number_name+"_Guide_JointLocA"
                self.guide_b_loc = side+self.number_name+"_Guide_JointLocB"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                self.locators_grp = cmds.group(name=side+self.number_name+"_Loc_Grp", empty=True)
                # calculate distance between guide and end:
                self.dist = self.ar.utils.create_dist_between(self.guide_a_loc, self.guide_b_loc)[0] * 0.2
                self.joints, self.main_ctrls, self.zeros, self.controllers, self.aim_locs, self.up_locs = [], [], [], [], [], []
                for p, letter in enumerate(["A", "B"]):
                    # create joints:
                    cmds.select(clear=True)
                    jnt = cmds.joint(name=side+self.number_name+"_"+letter+"_1_Jnt", scaleCompensate=False)
                    cmds.addAttr(jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.create_end_joint(side+self.number_name+"_"+letter, jnt, tz=self.dist)
                    # joint labelling:
                    self.ar.utils.set_joint_label(jnt, s+self.joint_label_add, 18, self.number_name+"_"+letter)
                    self.joints.append(jnt)
                    
                    # create a control:
                    main_ctrl = self.ar.ctrls.create_controller("id_055_SuspensionMain", side+self.number_name+"_"+self.ar.data.lang["c058_main"]+"_"+letter+"_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc"+letter)
                    ctrl = self.ar.ctrls.create_controller("id_056_SuspensionAB", side+self.number_name+"_"+letter+"_Ctrl", r=self.radius*0.5, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc"+letter, parent_tag=main_ctrl)
                    upLocCtrl = self.ar.ctrls.create_controller("id_057_SuspensionUpLoc", side+self.number_name+"_"+letter+"_UpLoc_Ctrl", r=self.radius*0.1, d=self.curve_degree, guide_source=self.name_guide+"_JointLoc"+letter, parent_tag=ctrl)
                    self.ar.ctrls.set_lock_hide([ctrl], ['tx', 'ty', 'tz', 'v'])
                    self.ar.ctrls.set_lock_hide([upLocCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
                    # position and orientation of joint and control:
                    cmds.parent(ctrl, upLocCtrl, main_ctrl)
                    cmds.parentConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_PaC")
                    cmds.scaleConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_ScC")
                    self.controllers.append(ctrl)
                    # create_zero_out controls:
                    ctrl_zeros = self.ar.utils.create_zero_out([main_ctrl, ctrl, upLocCtrl])
                    self.main_ctrls.append(ctrl_zeros[0])
                    self.zeros.append(ctrl_zeros[1])
                    cmds.setAttr(ctrl_zeros[2]+".translateX", self.dist)
                    # origined from data:
                    if p == 0:
                        self.ar.utils.set_origined_from_attr(main_ctrl, self.base+";"+self.guide_a_loc+";"+self.guide_radius)
                        cmds.matchTransform(ctrl_zeros[0], self.guide_a_loc, position=True, rotation=True)
                    else:
                        self.ar.utils.set_origined_from_attr(main_ctrl, self.guide_b_loc)
                        cmds.matchTransform(ctrl_zeros[0], self.guide_b_loc, position=True, rotation=True)
                        # integrating data:
                        self.suspension_b_ctrl_grps.append(ctrl_zeros[0])
                    # hide visibility attribute:
                    cmds.setAttr(main_ctrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 1:
                            cmds.setAttr(ctrl_zeros[0]+".scaleX", -1)
                            cmds.setAttr(ctrl_zeros[0]+".scaleY", -1)
                            cmds.setAttr(ctrl_zeros[0]+".scaleZ", -1)
                    cmds.addAttr(ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                    cmds.setAttr(ctrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(ctrl+".scaleCompensate", jnt+".segmentScaleCompensate", force=True)
                    
                    # working with aim setup:
                    cmds.addAttr(ctrl, longName=self.ar.data.lang['c118_active'], attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                    aim_loc = cmds.spaceLocator(name=side+self.number_name+"_"+letter+"_Aim_Loc")[0]
                    up_loc = cmds.spaceLocator(name=side+self.number_name+"_"+letter+"_Up_Loc")[0]
                    loc_grp = cmds.group(aim_loc, up_loc, name=side+self.number_name+"_"+letter+"_Loc_Grp")
                    cmds.parent(loc_grp, self.locators_grp, relative=True)
                    cmds.matchTransform(loc_grp, ctrl, position=True, rotation=True)
                    cmds.parentConstraint(upLocCtrl, up_loc, maintainOffset=False, name=up_loc+"_PaC")
                    cmds.parentConstraint(main_ctrl, loc_grp, maintainOffset=True, name=loc_grp+"_PaC")
                    cmds.setAttr(loc_grp+".visibility", 0)
                    self.aim_locs.append(aim_loc)
                    self.up_locs.append(up_loc)

                # aim constraints:
                # B to A:
                aic_a = cmds.aimConstraint(self.aim_locs[1], self.zeros[0], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.up_locs[0], maintainOffset=True, name=self.zeros[0]+"_AiC")[0]
                cmds.connectAttr(self.controllers[0]+"."+self.ar.data.lang['c118_active'], aic_a+"."+self.aim_locs[1]+"W0", force=True)
                # A to B:
                aic_b = cmds.aimConstraint(self.aim_locs[0], self.zeros[1], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.up_locs[1], maintainOffset=True, name=self.zeros[1]+"_AiC")[0]
                cmds.connectAttr(self.controllers[1]+"."+self.ar.data.lang['c118_active'], aic_b+"."+self.aim_locs[0]+"W0", force=True)
                
                # integrating data:
                self.loaded_father_b = cmds.getAttr(self.guide_base+".fatherB")
                if self.loaded_father_b:
                    self.father_b_items.append(self.loaded_father_b)
                else:
                    self.father_b_items.append(None)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, self.main_ctrls, self.joints, [self.locators_grp])
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
                            "suspensionBCtrlGrpList" : self.suspension_b_ctrl_grps,
                            "fatherBList" : self.father_b_items,
                            "ctrlHookGrpList" : self.ctrl_hook_grps
                        }
