# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Single"
TITLE = "m073_single"
DESCRIPTION = "m074_singleDesc"
WIKI = "03-‐-Guides#-single"



class Single(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        # returned data from the dictionary
        self.main_jis_items = []
        self.static_grps = []
        self.ctrl_grps = []
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc], ["JointLoc1", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="indirectSkin", attributeType='bool')
        cmds.addAttr(self.guide_base, longName='holder', attributeType='bool')
        cmds.addAttr(self.guide_base, longName='sdkLocator', attributeType='bool')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=0, maxValue=3, attributeType='long')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line, self.line_end])
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        # parenting
        cmds.parent(self.line, self.guide_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.parentConstraint(self.guide_end_loc, self.line_end, maintainOffset=False, name=self.line_end+"_PaC")
        cmds.scaleConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_ScC")
        cmds.scaleConstraint(self.guide_end_loc, self.line_end, maintainOffset=False, name=self.line_end+"_ScC")
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])

    
    def change_indirectskin(self, value, *args):
        """ Set the attribute value for indirectSkin.
        """
        cmds.setAttr(self.guide_base+".indirectSkin", value)
        if value == 0:
            cmds.setAttr(self.guide_base+".holder", 0)
            cmds.setAttr(self.guide_base+".sdkLocator", 0)
        if self.ar.data.ui_state:
            self.ar.guide_ui.change_indirectskin_ui(value)

    
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                cmds.select(clear=True)
                # declare guide:
                self.guide = side+self.number_name+"_Guide_JointLoc1"
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                # create a joint:
                jnt = cmds.joint(name=side+self.number_name+"_Jnt", scaleCompensate=False)
                cmds.addAttr(jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.ar.utils.set_joint_label(jnt, s+self.joint_label_add, 18, self.number_name)
                # create a control:
                if not self.get_guide_attr('indirectSkin'):
                    if self.curve_degree == 0:
                        self.curve_degree = 1
                # work with curve shape and rotation cases:
                indirectskin_rot = (0, 0, 0)
                if self.ar.data.lang['c058_main'] in self.number_name:
                    ctrl_type_id = "id_054_SingleMain"
                    if len(self.sides) > 1:
                        if self.ar.data.lang['c041_eyebrow'] in self.number_name:
                            indirectskin_rot = (0, 0, -90)
                        else:
                            indirectskin_rot = (0, 0, 90)
                else:
                    ctrl_type_id = "id_029_SingleIndSkin"
                    if self.ar.data.lang['c045_lower'] in self.number_name:
                        indirectskin_rot=(0, 0, 180)
                    elif self.ar.data.lang['c043_corner'] in self.number_name:
                        if "00" in self.number_name:
                            indirectskin_rot=(0, 0, 90)
                        else:
                            indirectskin_rot=(0, 0, -90)
                single_ctrl = self.ar.ctrls.create_controller(ctrl_type_id, side+self.number_name+"_Ctrl", r=self.radius, d=self.curve_degree, rot=indirectskin_rot, head_def=cmds.getAttr(self.base+".deformedBy"), guide_source=self.name_guide+"_JointLoc1")
                self.ar.utils.set_origined_from_attr(single_ctrl, self.base+";"+self.guide+";"+self.guide_end_loc+";"+self.guide_radius)
                # position and orientation of joint and control:
                cmds.matchTransform(jnt, self.guide, position=True, rotation=True)
                cmds.matchTransform(single_ctrl, self.guide, position=True, rotation=True)
                # create_zero_out controls:
                single_ctrl_zero = self.ar.utils.create_zero_out([single_ctrl], offset=True)[0]
                # hide visibility attribute:
                cmds.setAttr(single_ctrl+'.visibility', keyable=False)
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.setAttr(single_ctrl_zero+".scaleX", -1)
                        cmds.setAttr(single_ctrl_zero+".scaleY", -1)
                        cmds.setAttr(single_ctrl_zero+".scaleZ", -1)
                if not self.get_guide_attr('indirectSkin'):
                    cmds.addAttr(single_ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                    cmds.setAttr(single_ctrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(single_ctrl+".scaleCompensate", jnt+".segmentScaleCompensate", force=True)
                if self.get_guide_attr('indirectSkin'):
                    # create fatherJoints in order to create_zero_out the skinning joint:
                    cmds.select(clear=True)
                    jxt_name = jnt.replace("_Jnt", "_Jxt")
                    jxt = cmds.duplicate(jnt, name=jxt_name)[0]
                    self.ar.utils.clear_dpar_attr([jxt])
                    cmds.makeIdentity(jnt, apply=True, jointOrient=False)
                    cmds.parent(jnt, jxt)
                    for attr in self.ar.data.transform_attrs[:-1]:
                        cmds.connectAttr(single_ctrl+'.'+attr, jnt+'.'+attr, force=True)
                    # fix mirror issue: Maya 2026 release bug
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 1:
                            inv_md = cmds.createNode("multiplyDivide", name=jxt_name.replace("_Jxt", "_Inv_MD"))
                            for axis in self.ar.data.axes:
                                cmds.setAttr(inv_md+".input2"+axis, -1)
                                cmds.connectAttr(single_ctrl+'.translate'+axis, inv_md+'.input1'+axis, force=True)
                                cmds.connectAttr(inv_md+'.output'+axis, jnt+'.translate'+axis, force=True)
                    if self.get_guide_attr('holder'):
                        cmds.delete(single_ctrl+"0Shape", shape=True)
                        single_ctrl = cmds.rename(single_ctrl, single_ctrl+"_"+self.ar.data.lang['c046_holder']+"_Grp")
                        self.ar.utils.remove_user_defined_attr(single_ctrl, True)
                        self.ar.utils.add_attr_to_items([single_ctrl], "dpHolder")
                        self.ar.ctrls.set_lock_hide([single_ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
                        jnt = cmds.rename(jnt, jnt.replace("_Jnt", "_"+self.ar.data.lang['c046_holder']+"_Jis"))
                        self.ar.ctrls.set_lock_hide([jnt], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'], True, True)
                    else:
                        if self.get_guide_attr('sdkLocator'):
                            if not self.ar.data.lang['c058_main'] in self.number_name:
                                # this one will be used to receive inputs from sdk locator:
                                sdk_jis_name = jnt.replace("_Jnt", "_SDK_Jis")
                                sdk_jis = cmds.duplicate(jnt, name=sdk_jis_name)[0]
                                # sdk locator:
                                sdk_loc = cmds.spaceLocator(name=sdk_jis.replace("_Jis", "_Loc"))[0]
                                sdk_loc_grp = cmds.group(sdk_loc, name=sdk_loc+"_Grp")
                                cmds.matchTransform(sdk_loc_grp, single_ctrl, position=True, rotation=True)
                                cmds.parent(sdk_loc_grp, single_ctrl, relative=True)
                                sdk_loc_md = cmds.createNode("multiplyDivide", name=sdk_loc+"_MD")
                                self.to_ids.append(sdk_loc_md)
                                cmds.addAttr(sdk_loc, longName="intensityX", attributeType="float", defaultValue=-1, keyable=False)
                                cmds.addAttr(sdk_loc, longName="intensityY", attributeType="float", defaultValue=-1, keyable=False)
                                cmds.addAttr(sdk_loc, longName="intensityZ", attributeType="float", defaultValue=-1, keyable=False)
                                cmds.connectAttr(sdk_loc+".translateX", sdk_loc_md+".input1X", force=True)
                                cmds.connectAttr(sdk_loc+".translateY", sdk_loc_md+".input1Y", force=True)
                                cmds.connectAttr(sdk_loc+".translateZ", sdk_loc_md+".input1Z", force=True)
                                cmds.connectAttr(sdk_loc+".intensityX", sdk_loc_md+".input2X", force=True)
                                cmds.connectAttr(sdk_loc+".intensityY", sdk_loc_md+".input2Y", force=True)
                                cmds.connectAttr(sdk_loc+".intensityZ", sdk_loc_md+".input2Z", force=True)
                                cmds.connectAttr(sdk_loc_md+".outputX", sdk_loc_grp+".translateX", force=True)
                                cmds.connectAttr(sdk_loc_md+".outputY", sdk_loc_grp+".translateY", force=True)
                                cmds.connectAttr(sdk_loc_md+".outputZ", sdk_loc_grp+".translateZ", force=True)
                                cmds.addAttr(single_ctrl, longName="displayLocator", attributeType="bool", keyable=False)
                                cmds.setAttr(single_ctrl+".displayLocator", 0, channelBox=True)
                                cmds.connectAttr(single_ctrl+".displayLocator", sdk_loc+".visibility", force=True)
                                cmds.setAttr(sdk_loc+".visibility", lock=True)
                                for attr in self.ar.data.transform_attrs[:-1]:
                                    cmds.connectAttr(sdk_loc+'.'+attr, sdk_jis+'.'+attr)
                                cmds.setAttr(sdk_loc_grp+".rotateX", 0)
                                cmds.setAttr(sdk_loc_grp+".rotateY", 0)
                                cmds.setAttr(sdk_loc_grp+".rotateZ", 0)
                        # rename indirectSkinning joint from Jnt to Jis:
                        jnt = cmds.rename(jnt, jnt.replace("_Jnt", "_Jis"))
                else: # like a fkLine
                    # create parentConstraint from ctrl to jnt:
                    cmds.parentConstraint(single_ctrl, jnt, maintainOffset=False, name=jnt+"_PaC")
                    # create scaleConstraint from ctrl to jnt:
                    cmds.scaleConstraint(single_ctrl, jnt, maintainOffset=True, name=jnt+"_ScC")
                # create end joint:
                cmds.select(jnt)
                self.create_end_joint(side+self.number_name)
                self.main_jis_items.append(jnt)
                # create a masterModuleGrp to be checked if this rig exists:
                if self.get_guide_attr('indirectSkin'):
                    self.create_hook_setup(side, [side+self.number_name+"_Ctrl_Zero_0_Grp"], staticList=[side+self.number_name+"_Jxt"])
                else:
                    self.create_hook_setup(side, [side+self.number_name+"_Ctrl_Zero_0_Grp"], [side+self.number_name+"_Jnt"])
                self.static_grps.append(self.static_hook_grp)
                self.ctrl_grps.append(self.ctrl_hook_grp)
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
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "mainJisList"   : self.main_jis_items,
                            "staticGrpList" : self.static_grps,
                            "ctrlGrpList"   : self.ctrl_grps,
                        }
