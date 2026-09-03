# importing libraries:
from maya import cmds
from maya import mel
from ..base import standard
from importlib import reload


# global variables to this module:    
CLASS_NAME = "Chain"
TITLE = "m178_chain"
DESCRIPTION = "m179_chainDesc"
WIKI = "03-‐-Guides#-chain"



class Chain(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(standard)
        self.world_refs = []
        self.world_ref_shapes = []
        self.current_joint_number = 5
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.change_joint_number(5)
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc], 
                                   ["JointLoc1", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", defaultValue=1, attributeType='long')
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="dynamic", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="mainControls", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="nMain", minValue=1, defaultValue=1, attributeType='long')
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
        cmds.parent(self.line, self.guide_base, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        cmds.parent(self.guide_loc, self.guide_base)
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.parentConstraint(self.guide_end_loc, self.line_end, maintainOffset=False, name=self.line_end+"_PaC")
        # edit
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])

    
    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number >= 5: #min for chain
            self.ar.opt.check_use_default_render_layer()
            self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
            if joint_number != self.current_joint_number:
                self.guide_end_loc = self.name_guide+"_JointEnd"
                self.line_end = self.name_guide+"_JGuideEnd"
                cmds.parent(self.guide_end_loc, self.line_end, world=True)
                if joint_number > self.current_joint_number:
                    for n in range(self.current_joint_number+1, joint_number+1):
                        self.guide_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                        self.increment_joint_number(n)
                        self.add_node_to_guide_net([self.guide_loc], ["JointLoc"+str(n)])
                elif joint_number < self.current_joint_number:
                    self.line = self.name_guide+"_JGuide"+str(joint_number)
                    self.guide_loc = self.reduce_joint_number(joint_number)
                self.re_parent_guide_end()
                cmds.setAttr(self.guide_base+".nJoints", joint_number)
                self.current_joint_number = joint_number
                self.change_main_ctrls_number(0)
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.change_joint_number(5)


    def setup_aim_locators(self, side, to_up_parent, ik_numb, ik_fake_ctrl, to_fake_parent, has_fake=True):
        """ Creates the up and fake locators to use in the aimConstraint.
            Return them as a list.
        """
        fake_loc = None
        # up locator:
        up_loc = cmds.spaceLocator(name=side+self.number_name+"_%02d_Up_Loc"%ik_numb)[0]
        cmds.matchTransform(up_loc, to_up_parent, position=True, rotation=True)
        cmds.parent(up_loc, to_up_parent, relative=False)
        cmds.setAttr(up_loc+".translateY", 2*self.radius)
        cmds.setAttr(up_loc+".visibility", 0)    
        if has_fake:
            # fake aim locator:
            fake_loc = cmds.spaceLocator(name=side+self.number_name+"_%02d_Fake_Loc"%ik_numb)[0]
            cmds.matchTransform(fake_loc, ik_fake_ctrl, position=True, rotation=True)
            cmds.parent(fake_loc, to_fake_parent, relative=False)
            cmds.setAttr(fake_loc+".visibility", 0)
        return [up_loc, fake_loc]
    

    def setup_aim_constraint(self, ik_ctrl, ik_to_aim_ctrl, up_loc, fake_loc, ik_ctrl_zero, z_dir=1, auto_orient=True):
        """ Creates an aim constraint to extrem ik controls use auto_orient attributes.
        """
        # look at aim constraint:
        aic = cmds.aimConstraint(ik_to_aim_ctrl, fake_loc, ik_ctrl_zero, worldUpType="object", worldUpObject=up_loc, aimVector=(0, 0, z_dir), upVector=(0, 1, 0), maintainOffset=True, name=ik_ctrl_zero+"_AiC")[0]
        if auto_orient:
            cmds.connectAttr(ik_ctrl+"."+self.ar.data.lang['c033_autoOrient'], aic+"."+ik_to_aim_ctrl+"W0", force=True)
            rev = cmds.createNode("reverse", name=ik_ctrl_zero+"_Aim_Rev")
            cmds.connectAttr(ik_ctrl+"."+self.ar.data.lang['c033_autoOrient'], rev+".inputX", force=True)
            cmds.connectAttr(rev+".outputX", aic+"."+fake_loc+"W1", force=True)
            self.to_ids.append(rev)


    def clear_rename_joint_chain(self, joints, from_name, to_name, clear=True):
        """ Clean up joint chain and rename it as well.
            Return the renamed list.
        """
        result = []
        for item in reversed(joints):
            if cmds.objectType(item) == "joint":
                if self.ar.data.joint_end_attr in cmds.listAttr(item):
                    result.append(cmds.rename(item, item[item.rfind("|")+1:].replace("_"+self.ar.data.joint_end_attr, to_name+"_"+self.ar.data.joint_end_attr)))
                    continue
                elif "_Jax" in item:
                    if clear:
                        cmds.delete(item)
                    continue
                if not to_name in item[item.rfind("|")+1:]:
                    result.append(cmds.rename(item, item[item.rfind("|")+1:].replace(from_name, to_name)))
            else:
                if clear:
                    cmds.delete(item)
        return list(reversed(result))


    def create_dynamic_chain(self, dyn_name, world_ref, rebuild_curve_spans=20):
        """ This is like a patch to add a dynamic setup to the Chain.
        """
        dyn_name_lower = dyn_name[0].lower()+dyn_name[1:]
        if dyn_name_lower[1] == "_":
            dyn_name_lower = dyn_name[0].lower()+dyn_name[2:]
        # curve
        main_crv = cmds.duplicate(self.ik_spline_items[2], name=dyn_name+"_Main_Crv")[0]
        cmds.delete(main_crv+"ShapeOrig")
        cmds.rebuildCurve(main_crv, constructionHistory=False, replaceOriginal=True, rebuildType=False, endKnots=True, keepRange=False, keepControlPoints=False, keepEndPoints=True, keepTangents=False, spans=rebuild_curve_spans, degree=3, tolerance=0.01)
        cmds.skinCluster(self.skin_joints, main_crv, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=dyn_name+"_Main_Crv_SC")

        # dynamic joints
        first_dyn_jnt = dyn_name+"_00_Dyn_Jnt"
        dyn_joints = cmds.duplicate(dyn_name+"_00_Fk_Jxt", name=first_dyn_jnt, fullPath=True)
        new_skin_joints = cmds.duplicate(dyn_name+"_00_Jnt", name=dyn_name+"_00_Jnt_First", fullPath=True)
        skin_joints = cmds.ls(self.skin_joints[0], long=True)
        skin_joints.extend(sorted(cmds.listRelatives(self.skin_joints[0], children=True, allDescendents=True, fullPath=True, type="joint")))
        dyn_joints = self.clear_rename_joint_chain(dyn_joints, "_Fk", "_Dyn")
        dyn_joints.insert(0, first_dyn_jnt)
        self.skin_joints = self.clear_rename_joint_chain(skin_joints, "_Jn", "_IkFk_Jx", False)
        self.ar.utils.add_joint_end_attr([self.skin_joints[-1]])
        cmds.rename(self.skin_joints[-1], dyn_name+"_IkFk_"+self.ar.data.joint_end_attr)
        self.ar.utils.remove_user_defined_attr(self.skin_joints[:-1])
        new_skin_joints = self.clear_rename_joint_chain(new_skin_joints, "", "")
        cmds.rename(dyn_name+"_00_Jnt_First", dyn_name+"_00_Jnt")
        new_skin_joints = [dyn_name+"_00_Jnt"]
        new_skin_joints.extend(sorted(cmds.listRelatives(dyn_name+"_00_Jnt", children=True, allDescendents=True)))
        self.ar.utils.clear_joint_label(self.skin_joints)
        cmds.setAttr(self.skin_joints[0]+".visibility", 0)
        
        # setup new blend joints
        self.ar.utils.create_joint_blend(self.skin_joints[:-1], dyn_joints[:-1], new_skin_joints[:-1], "Dyn_ikFkBlend", dyn_name_lower, world_ref, False)
        dyn_stretch_bc = cmds.createNode("blendColors", name=dyn_name+"_DynStretch_BC")
        self.to_ids.append(dyn_stretch_bc)
        cmds.connectAttr(dyn_joints[0]+".scaleX", dyn_stretch_bc+".color1R", force=True)
        cmds.connectAttr(dyn_joints[0]+".scaleY", dyn_stretch_bc+".color1G", force=True)
        cmds.connectAttr(dyn_joints[0]+".scaleZ", dyn_stretch_bc+".color1B", force=True)
        cmds.connectAttr(self.skin_joints[0]+".scaleX", dyn_stretch_bc+".color2R", force=True)
        cmds.connectAttr(self.skin_joints[0]+".scaleY", dyn_stretch_bc+".color2G", force=True)
        cmds.connectAttr(self.skin_joints[0]+".scaleZ", dyn_stretch_bc+".color2B", force=True)
        cmds.connectAttr(world_ref+"."+dyn_name_lower+"Dyn_ikFkBlend", dyn_stretch_bc+".blender", force=True)
        for j, jnt in enumerate(new_skin_joints[:-1]):
            cmds.connectAttr(dyn_stretch_bc+".outputR", new_skin_joints[j]+".scaleX", force=True)
            cmds.connectAttr(dyn_stretch_bc+".outputG", new_skin_joints[j]+".scaleY", force=True)
            cmds.connectAttr(dyn_stretch_bc+".outputB", new_skin_joints[j]+".scaleZ", force=True)

        # hairSystem
        mel.eval("DynCreateHairMenu MayaWindow|mainHairMenu; HairAssignHairSystemMenu MayaWindow|mainHairMenu|hairAssignHairSystemItem;")
        cmds.select(main_crv+"Shape")
        dp_hair_system_node = None
        transforms = cmds.ls(selection=False, type="transform")
        if transforms:
            for transform in transforms:
                if 'dpHairSystem' in cmds.listAttr(transform):
                    dp_hair_system_node = transform
                    break
        if not dp_hair_system_node:
            mel.eval("assignNewHairSystem;")
            # rename nodes
            if cmds.objExists("hairSystem1"):
                cmds.rename("hairSystem1", "dpHairSystem")
            dp_hair_system_node = "dpHairSystemShape"
            cmds.addAttr(dp_hair_system_node, longName="dpHairSystem", attributeType="bool", defaultValue=1)
            if cmds.objExists("nucleus1"):
                cmds.rename("nucleus1", "dpNucleus")
                cmds.addAttr(dp_hair_system_node, longName="dpNucleus", attributeType="bool", defaultValue=1)
            if cmds.objExists("hairSystem1OutputCurves"):
                cmds.rename("hairSystem1OutputCurves", "dpHairSystemOutputCurves")
            # parent nodes
            fx_grp = self.ar.utils.get_node_by_message("fxGrp")
            if fx_grp:
                cmds.parent("dpNucleus", "dpHairSystem", "dpHairSystemOutputCurves", fx_grp)
                self.ar.ctrls.color_shape([fx_grp], [0.9, 0.6, 1], outliner=True)
            if cmds.objExists("hairSystem1Follicles"):
                cmds.delete("hairSystem1Follicles")
        else:
            mel.eval('assignHairSystem '+dp_hair_system_node+';')
            if cmds.objExists("dpHairSystemFollicles"):
                cmds.delete("dpHairSystemFollicles")
        cmds.rename(cmds.listRelatives(cmds.listRelatives(self.ik_static_grp, children=True, allDescendents=True, type="follicle")[0], parent=True)[0], dyn_name+"_Dyn_Fol")
        dyn_crv = cmds.rename("dpHairSystemOutputCurves|curve1", dyn_name+"_Dyn_Crv")
        # ikHandle
        ik_spline_items = cmds.ikHandle(startJoint=first_dyn_jnt, endEffector=dyn_joints[-2], name=dyn_name+"_Dyn_IkH", solver="ikSplineSolver", parentCurve=False, curve=dyn_crv, createCurve=False) #[Handle, Effector]
        ik_spline_items[1] = cmds.rename(ik_spline_items[1], dyn_name+"_Dyn_Eff")
        cmds.parent(ik_spline_items[0], self.ik_static_grp)
        cmds.select(clear=True)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                attr_name_lower = self.ar.naming.get_attr_name_lower(side, self.number_name)
                self.base = side+self.number_name+'_Guide_Base'
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                self.skin_joints, ik_joints, fk_joints = [], [], []
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                head_def_value = cmds.getAttr(self.base+".deformedBy")
                
                # creating joint chains:
                chain_data = {}
                suffixes = ['_Jnt', '_Ik_Jxt', '_Fk_Jxt']
                end_suffixes = ['_'+self.ar.data.joint_end_attr, '_Ik_'+self.ar.data.joint_end_attr, '_Fk_'+self.ar.data.joint_end_attr]
                for t, suffix in enumerate(suffixes):
                    wips = []
                    cmds.select(clear=True)
                    for n in range(0, self.n_joints):
                        wips.append(cmds.joint(name=side+self.number_name+"_%02d"%n+suffix))
                    joint_end = cmds.joint(name=side+self.number_name+end_suffixes[t], radius=0.5)
                    self.ar.utils.add_joint_end_attr([joint_end])
                    wips.append(joint_end)
                    chain_data[suffix] = wips
                # getting jointLists:
                self.skin_joints = chain_data[suffixes[0]]
                ik_joints = chain_data[suffixes[1]]
                fk_joints = chain_data[suffixes[2]]
                
                # hide not skin joints in order to be more Rigger friendly when working the Skinning:
                cmds.setAttr(ik_joints[0]+".visibility", 0)
                cmds.setAttr(fk_joints[0]+".visibility", 0)

                for o, skin_joint in enumerate(self.skin_joints):
                    if o < len(self.skin_joints) - 1:
                        cmds.addAttr(skin_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                        self.ar.naming.set_joint_label(skin_joint, s+self.joint_label_add, 18, self.number_name+"_%02d"%o)

                fk_ctrls, fk_zeros, orig_from_items = [], [], []
                for n in range(0, self.n_joints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.number_name+"_Guide_JointLoc"+str(n+1)
                    
                    # create a Fk control:
                    fk_ctrl = self.ar.ctrls.create_controller("id_082_ChainFk", side+self.number_name+"_%02d_Fk_Ctrl"%n, r=self.radius, d=self.curve_degree, head_def=head_def_value, guide_source=self.name_guide+"_JointLoc"+str(n+1), parent_tag=self.get_parent_to_tag(fk_ctrls))
                    fk_ctrls.append(fk_ctrl)
                    # position and orientation of joint and control:
                    cmds.matchTransform(fk_joints[n], self.guide, position=True, rotation=True)
                    cmds.matchTransform(fk_ctrl, self.guide, position=True, rotation=True)
                    # create_zero_out controls:
                    
                    fk_zeros.append(self.ar.utils.create_zero_out([fk_ctrl])[0]) #zeroOutCtrlGrp
                    # hide visibility attribute:
                    cmds.setAttr(fk_ctrl+'.visibility', keyable=False)

                    # creating the originedFrom attributes (in order to permit composed parents in the future):
                    orig_grp = cmds.group(empty=True, name=side+self.number_name+"_%02d_OrigFrom_Grp"%n)
                    orig_from_items.append(orig_grp)
                    if n == 0:
                        self.ar.utils.set_origined_from_attr(orig_grp, self.guide[self.guide.find("__") + 1:].replace(":", "_")+";"+self.guide_end_loc+";"+self.guide_radius)
                    elif n == (self.n_joints-1):
                        self.ar.utils.set_origined_from_attr(orig_grp, self.guide[self.guide.find("__") + 1:].replace(":", "_")+";"+self.base)
                    else:
                        self.ar.utils.set_origined_from_attr(orig_grp, self.guide[self.guide.find("__") + 1:].replace(":", "_"))
                    self.to_ids.extend(cmds.parentConstraint(self.skin_joints[n], orig_grp, maintainOffset=False, name=orig_grp+"_PaC"))
                    
                    if n > 0:
                        cmds.parent(fk_zeros[n], fk_ctrls[n - 1])
                        cmds.parent(orig_grp, orig_from_items[n - 1])

                # add extrem_toParent_Ctrl
                if n == (self.n_joints-1):
                    to_parent_extrem_ctrl = self.ar.ctrls.create_controller("id_083_ChainToParent", ctrl_name=side+self.number_name+"_ToParent_Ctrl", r=(self.radius * 0.1), d=self.curve_degree, head_def=head_def_value, guide_source=self.name_guide+"_JointEnd", parent_tag=fk_ctrls[-1])
                    cmds.addAttr(to_parent_extrem_ctrl, longName="stretchable", minValue=0, maxValue=1, attributeType="float", defaultValue=1, keyable=True)
                    cmds.addAttr(to_parent_extrem_ctrl, longName=self.ar.data.lang['c031_volumeVariation'], attributeType="float", minValue=0, defaultValue=1, keyable=True)
                    cmds.addAttr(to_parent_extrem_ctrl, longName="min"+self.ar.data.lang['c031_volumeVariation'], attributeType="float", minValue=0, defaultValue=0.01, maxValue=1, keyable=True)
                    cmds.addAttr(to_parent_extrem_ctrl, longName=self.ar.data.lang['c118_active']+self.ar.data.lang['c031_volumeVariation'], attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                    cmds.parent(to_parent_extrem_ctrl, orig_grp)
                    cmds.setAttr(to_parent_extrem_ctrl+".translateZ", self.radius)
                    if s == 1:
                        if self.flip:
                            cmds.setAttr(to_parent_extrem_ctrl+".translateZ", -self.radius)
                    self.ar.utils.create_zero_out([to_parent_extrem_ctrl])
                    self.ar.ctrls.set_lock_hide([to_parent_extrem_ctrl], ['v'])

                # invert scale for right side before:
                if s == 1:
                    if self.flip:
                        # fix flipping issue for FK right side:
                        for f in range(1, len(fk_ctrls)):
                            cmds.setAttr(fk_zeros[0]+".scaleX", -1)
                            cmds.setAttr(fk_zeros[0]+".scaleY", -1)
                            cmds.setAttr(fk_zeros[0]+".scaleZ", -1)
                            attributes = ["tx", "ty", "tz", "rx", "ry", "rz"]
                            for attr in attributes:
                                attr_value = cmds.getAttr(fk_zeros[f]+"."+attr)
                                cmds.setAttr(fk_zeros[f]+"."+attr, -1*attr_value)
                
                # working with position, orientation of joints and make an orientConstraint for Fk controls:
                for n in range(0, self.n_joints):
                    cmds.matchTransform(self.skin_joints[n], side+self.number_name+"_Guide_JointLoc"+str(n+1), position=True, rotation=True)
                    cmds.matchTransform(ik_joints[n], side+self.number_name+"_Guide_JointLoc"+str(n+1), position=True, rotation=True)
                    # freezeTransformations (rotates):
                    cmds.makeIdentity(self.skin_joints[n], ik_joints[n], fk_joints[n], apply=True, rotate=True)
                    # fk control leads fk joint:
                    cmds.parentConstraint(fk_ctrls[n], fk_joints[n], maintainOffset=True, name=side+self.number_name+"_%02d_Fk_PaC"%n)
                    if n == self.n_joints-1:
                        cmds.connectAttr(fk_ctrls[n]+".scaleX", fk_joints[n]+".scaleX", force=True)
                        cmds.connectAttr(fk_ctrls[n]+".scaleY", fk_joints[n]+".scaleY", force=True)
                        cmds.connectAttr(fk_ctrls[n]+".scaleZ", fk_joints[n]+".scaleZ", force=True)
                    else:
                        self.ar.ctrls.set_lock_hide([fk_ctrls[n]], ['sx', 'sy', 'sz'])

                if self.mirror_axis == "Z":
                    cmds.setAttr(ik_joints[0]+".rotateZ", 180)
                # puting endJoints in the correct position:
                cmds.matchTransform(self.skin_joints[-1], self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(ik_joints[-1], self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(fk_joints[-1], self.guide_end_loc, position=True, rotation=True)
                
                # creating a group reference to recept the attributes:
                world_ref = self.ar.ctrls.create_controller("id_084_ChainWorldRef", side+self.number_name+"_WorldRef_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", head_def=head_def_value, guide_source=self.name_guide+"_Base")
                if not cmds.objExists(world_ref+'.globalStretch'):
                    cmds.addAttr(world_ref, longName='globalStretch', attributeType='float', minValue=0, maxValue=1, defaultValue=1, keyable=True)
                self.world_refs.append(world_ref)
                self.world_ref_shapes.append(cmds.listRelatives(world_ref, children=True, type='nurbsCurve')[0])

                # create constraint in order to blend ikFk:
                self.ar.utils.create_joint_blend(ik_joints, fk_joints, self.skin_joints, "Fk_ikFkBlend", attr_name_lower, world_ref)

                # ik spline:
                self.ik_spline_items = cmds.ikHandle(startJoint=ik_joints[0], endEffector=ik_joints[-2], name=side+self.number_name+"_IkH", solver="ikSplineSolver", parentCurve=False, numSpans=4) #[Handle, Effector, Curve]
                self.ik_spline_items[1] = cmds.rename(self.ik_spline_items[1], side+self.number_name+"_Eff")
                self.ik_spline_items[2] = cmds.rename(self.ik_spline_items[2], side+self.number_name+"_IkC")
                ik_spline_handle = self.ik_spline_items[0]
                ik_spline_curve = self.ik_spline_items[2]
                # ik clusters:
                ik_clusters = []
                for p, i in zip(["0:1", "2", "3", "4", "5:6"], range(0,5)):
                    clusters = cmds.cluster(ik_spline_curve+".cv["+p+"]", name=side+self.number_name+"_Ik_"+str(i)+"_Cls") #[Deform, Handle]
                    self.to_ids.append(clusters[0]) #Deformer
                    ik_clusters.append(clusters[1]) #Handle
                # ik cluster positions:
                cmds.xform(ik_clusters[0], worldSpace=True, rotatePivot=cmds.xform(ik_joints[0], query=True, worldSpace=True, rotatePivot=True)) #firstIkJointPos
                cmds.xform(ik_clusters[-1], worldSpace=True, rotatePivot=cmds.xform(ik_joints[-2], query=True, worldSpace=True, rotatePivot=True)) #endIkJointPos
                # ik cluster group:
                ik_cluster_grp = cmds.group(ik_clusters, name=side+self.number_name+"_Ik_Cluster_Grp")
                option_ctrl = self.ar.utils.get_node_by_message("optionCtrl")
                if option_ctrl:
                    for axis in ['X', 'Y', 'Z']:
                        cmds.connectAttr(option_ctrl+".rigScaleOutput", ik_cluster_grp+".scale"+axis)

                # ik controls:
                ik_ctrls, ik_ctrl_zeros = [], []
                ik_ctrl_grp = cmds.group(name=side+self.number_name+"_Ik_Ctrl_Grp", empty=True)
                for c, cluster_node in enumerate(ik_clusters):
                    if c == 0: #first
                        ik_ctrl_main = self.ar.ctrls.create_controller("id_086_ChainIkMain", ctrl_name=side+self.number_name+"_Ik_Main_Ctrl", r=self.radius, d=self.curve_degree, head_def=head_def_value, guide_source=self.name_guide+"_Base")
                        cmds.matchTransform(ik_ctrl_main, cluster_node, position=True, rotation=True)
                        ik_ctrl_main_zero = self.ar.utils.create_zero_out([ik_ctrl_main])[0]
                        cmds.parent(ik_ctrl_main_zero, ik_ctrl_grp)
                        
                        # orienting controls
                        if s == 1:
                            cmds.parent(self.base, world=True)
                        cmds.setAttr(ik_ctrl_main_zero+".rotateX", cmds.getAttr(self.base+".rotateX"))
                        cmds.setAttr(ik_ctrl_main_zero+".rotateY", cmds.getAttr(self.base+".rotateY"))
                        cmds.setAttr(ik_ctrl_main_zero+".rotateZ", cmds.getAttr(self.base+".rotateZ"))
                        self.fix_mirror_flipping(ik_ctrl_main_zero, s, -1)

                        # loading Maya matrix node
                        loaded_quaternion_plugin = self.ar.config.check_loaded_plugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
                        loaded_matrix_plugin = self.ar.config.check_loaded_plugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
                        if loaded_quaternion_plugin and loaded_matrix_plugin:
                            # setup extract rotateZ from ikCtrlMain using worldSpace matrix by quaternion:
                            ik_main_loc = cmds.spaceLocator(name=side+self.number_name+"_Ik_Main_Loc")[0]
                            ik_main_loc_grp = cmds.group(ik_main_loc, name=side+self.number_name+"_Ik_MainLoc_Grp")
                            # need to keep ik_main_loc_grp at the world without any transformation to use it to extract ikMainCtrl rotateZ properly:
                            cmds.setAttr(ik_main_loc_grp+".inheritsTransform", 0)
                            cmds.setAttr(ik_main_loc_grp+".visibility", 0)
                            cmds.delete(cmds.parentConstraint(ik_ctrl_main, ik_main_loc_grp, maintainOffset=False, skipTranslate=("x", "y", "z")))
                            self.ar.ctrls.set_lock_hide([ik_main_loc_grp], ['rx', 'ry', 'rz'], l=True, k=True)
                            cmds.parentConstraint(ik_ctrl_main, ik_main_loc, maintainOffset=False, skipTranslate=("x", "y", "z"), name=ik_main_loc+"_PaC")
                            main_twist_matrix_md = self.ar.math.create_twist_bone_matrix(ik_main_loc_grp, ik_main_loc, "ikCtrlMain_TwistMatrix")
                            cmds.setAttr(main_twist_matrix_md+".input1Z", 1)
                            if s == 1:
                                cmds.setAttr(main_twist_matrix_md+".input1Z", -1)
                            # connect output of rotate in Z to ikSplineHandle roll attribute:
                            cmds.connectAttr(main_twist_matrix_md+".outputZ", ik_spline_handle+".roll", force=True)

                    ik_ctrl = self.ar.ctrls.create_controller("id_085_ChainIk", ctrl_name=side+self.number_name+"_Ik_"+str(c)+"_Ctrl", r=self.radius, d=self.curve_degree, head_def=head_def_value, guide_source=self.name_guide+"_JointLoc"+str(c), parent_tag=self.get_parent_to_tag(ik_ctrls, ik_ctrl_main))
                    ik_ctrls.append(ik_ctrl)
                    cmds.matchTransform(ik_ctrl, cluster_node, position=True, rotation=True)
                    ik_ctrl_zero = self.ar.utils.create_zero_out([ik_ctrl])[0]
                    ik_ctrl_zeros.append(ik_ctrl_zero)
                    cmds.parent(ik_ctrl_zero, ik_ctrl_main)
                    cmds.rotate(0, 0, 0, ik_ctrl_zero)
                    cmds.parentConstraint(ik_ctrl, cluster_node, maintainOffset=True, name=cluster_node+"_PaC")
                    self.fix_mirror_flipping(ik_ctrl_zero, s, 1)

                    if c == 4: #last
                        cmds.addAttr(ik_ctrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.ar.ctrls.set_lock_hide([ik_ctrl], ["sx", "sy", "sz", "v"])
                        # last ik control:
                        ik_ctrl_last = self.ar.ctrls.create_controller("id_087_ChainIkLast", ctrl_name=side+self.number_name+"_Ik_"+self.ar.data.lang['c125_last']+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, head_def=head_def_value, guide_source=self.name_guide+"_JointEnd", parent_tag=ik_ctrls[-1])
                        self.ar.ctrls.color_shape([ik_ctrl_last], 'cyan')
                        cmds.matchTransform(ik_ctrl_last, ik_ctrl, position=True, rotation=True)
                        ik_ctrl_last_zero = self.ar.utils.create_zero_out([ik_ctrl_last])[0]
                        cmds.parent(ik_ctrl_last_zero, ik_ctrl_main)
                        self.ar.ctrls.set_lock_hide([ik_ctrl_last], ["v"])
                        cmds.orientConstraint(ik_ctrl_last, ik_joints[-2], maintainOffset=True, name=ik_joints[-2]+"_OrC")
                        cmds.connectAttr(ik_ctrl_last+".scaleX", ik_joints[-2]+".scaleX", force=True)
                        cmds.connectAttr(ik_ctrl_last+".scaleY", ik_joints[-2]+".scaleY", force=True)
                        cmds.connectAttr(ik_ctrl_last+".scaleZ", ik_joints[-2]+".scaleZ", force=True)
                        self.fix_mirror_flipping(ik_ctrl_last_zero, s, -1, "X")
                        self.fix_mirror_flipping(ik_ctrl_last_zero, s, -1, "Y")
                        self.fix_mirror_flipping(ik_ctrl_last_zero, s, 1, "Z")
                        if self.mirror_axis == "Y":
                            self.fix_mirror_flipping(ik_ctrl_last_zero, s, -1, "Z")
                        cmds.parent(ik_ctrl_zero, ik_ctrl_last)
                    elif not c == 0:
                        if c == 2:
                            self.ar.ctrls.set_lock_hide([ik_ctrl], ["rx", "ry", "sx", "sy", "sz", "v", "ro"])
                        else:
                            self.ar.ctrls.set_lock_hide([ik_ctrl], ["rx", "ry", "rz", "sx", "sy", "sz", "v", "ro"])
                    else: #first
                        cmds.addAttr(ik_ctrl, longName=self.ar.data.lang['c033_autoOrient'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                        self.ar.ctrls.set_lock_hide([ik_ctrl], ["sx", "sy", "sz", "v"])
                        # first ik control:
                        ik_ctrl_first = self.ar.ctrls.create_controller("id_087_ChainIkLast", ctrl_name=side+self.number_name+"_Ik_"+self.ar.data.lang['c114_first']+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, head_def=head_def_value, guide_source=self.name_guide+"_Base", parent_tag=ik_ctrl_main)
                        self.ar.ctrls.color_shape([ik_ctrl_first], 'cyan')
                        cmds.matchTransform(ik_ctrl_first, ik_ctrl, position=True, rotation=True)
                        ik_ctrl_first_zero = self.ar.utils.create_zero_out([ik_ctrl_first])[0]
                        cmds.parent(ik_ctrl_first_zero, ik_ctrl_main)
                        self.ar.ctrls.set_lock_hide([ik_ctrl_first], ["v"])
                        cmds.connectAttr(ik_ctrl_first+".scaleX", ik_joints[0]+".scaleX", force=True)
                        cmds.connectAttr(ik_ctrl_first+".scaleY", ik_joints[0]+".scaleY", force=True)
                        cmds.connectAttr(ik_ctrl_first+".scaleZ", ik_joints[0]+".scaleZ", force=True)
                        self.fix_mirror_flipping(ik_ctrl_first_zero, s, -1, "X")
                        self.fix_mirror_flipping(ik_ctrl_first_zero, s, -1, "Y")
                        self.fix_mirror_flipping(ik_ctrl_first_zero, s, 1, "Z")
                        if self.mirror_axis == "Y":
                            self.fix_mirror_flipping(ik_ctrl_first_zero, s, -1, "Z")
                        cmds.parent(ik_ctrl_zero, ik_ctrl_first)
                cmds.connectAttr(ik_ctrl_first+".message", ik_ctrls[0]+".parentTag", force=True)
                
                # ik controls position:
                cmds.pointConstraint(ik_ctrl_first, ik_ctrls[2], ik_ctrl_zeros[1], maintainOffset=True, name=ik_ctrl_zeros[1]+"_PoC")
                cmds.pointConstraint(ik_ctrl_first, ik_ctrl_last, ik_ctrl_zeros[2], maintainOffset=True, name=ik_ctrl_zeros[2]+"_PoC")
                cmds.pointConstraint(ik_ctrls[2], ik_ctrl_last, ik_ctrl_zeros[3], maintainOffset=True, name=ik_ctrl_zeros[3]+"_PoC")
                
                # ik controls orientation:
                first_up_loc, first_fake_loc = self.setup_aim_locators(side, ik_ctrl_first, 0, ik_ctrls[1], ik_ctrl_first)
                last_up_loc, last_fake_loc = self.setup_aim_locators(side, ik_ctrl_last, 4, ik_ctrls[-2], ik_ctrl_last)
                mid_up_loc, mid_fake_loc = self.setup_aim_locators(side, ik_ctrls[2], 13, ik_ctrls[2], ik_ctrls[2], False)
                last_mid_loc = cmds.duplicate(last_fake_loc, name=last_fake_loc.replace("Fake", "Middle"))[0]
                cmds.setAttr(last_mid_loc+".translateZ", 0)
                if s == 0:
                    self.setup_aim_constraint(ik_ctrls[0], ik_ctrls[1], first_up_loc, first_fake_loc, ik_ctrl_zeros[0], 1)
                    self.setup_aim_constraint(ik_ctrls[-1], ik_ctrls[-2], last_up_loc, last_fake_loc, ik_ctrl_zeros[-1], -1)
                    self.setup_aim_constraint(ik_ctrls[1], ik_ctrls[2], mid_up_loc, mid_fake_loc, ik_ctrl_zeros[1], 1, False)
                    self.setup_aim_constraint(ik_ctrls[3], ik_ctrls[2], mid_up_loc, mid_fake_loc, ik_ctrl_zeros[3], -1, False)
                    cmds.aimConstraint(last_mid_loc, ik_ctrl_zeros[2], worldUpType="object", worldUpObject=last_up_loc, aimVector=(0, 0, 1), upVector=(0, 1, 0), maintainOffset=True, name=ik_ctrl_zeros[2]+"_AiC")
                else:
                    self.setup_aim_constraint(ik_ctrls[0], ik_ctrls[1], first_up_loc, first_fake_loc, ik_ctrl_zeros[0], -1)
                    self.setup_aim_constraint(ik_ctrls[-1], ik_ctrls[-2], last_up_loc, last_fake_loc, ik_ctrl_zeros[-1], -1)
                    self.setup_aim_constraint(ik_ctrls[1], ik_ctrls[2], mid_up_loc, mid_fake_loc, ik_ctrl_zeros[1], -1, False)
                    self.setup_aim_constraint(ik_ctrls[3], ik_ctrls[2], mid_up_loc, mid_fake_loc, ik_ctrl_zeros[3], 1, False)
                    cmds.aimConstraint(last_mid_loc, ik_ctrl_zeros[2], worldUpType="object", worldUpObject=last_up_loc, aimVector=(0, 0, -1), upVector=(0, 1, 0), maintainOffset=True, name=ik_ctrl_zeros[2]+"_AiC")
                
                self.ik_static_grp = cmds.group(self.ik_spline_items[0], self.ik_spline_items[2], name=side+self.number_name+"_IkH_Grp")

                # ik stretch:
                curve_info_node = cmds.arclen(self.ik_spline_items[2], constructionHistory=True)
                curve_info_node = cmds.rename(curve_info_node, side+self.number_name+"_Ik_CurveInfo")
                # create stretch nodes:
                ik_normalize_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_Normalize_MD")
                global_stretch_bc = cmds.createNode("blendColors", name=side+self.number_name+"_GlobalStretch_BC")
                stretchable_bc = cmds.createNode("blendColors", name=side+self.number_name+"_Stretchable_BC")
                stretch_bc = cmds.createNode("blendColors", name=side+self.number_name+"_Stretch_BC")
                ik_stretch_rev = cmds.createNode("reverse", name=side+self.number_name+"_Stretch_Rev")
                # get and set stretch attribute values:
                cmds.setAttr(ik_normalize_md+".operation", 2)
                cmds.setAttr(ik_normalize_md+".input2X", cmds.getAttr(curve_info_node+".arcLength")) #initialDistance
                # connect stretch attributes:
                cmds.connectAttr(curve_info_node+".arcLength", ik_normalize_md+".input1X", force=True)
                cmds.connectAttr(ik_normalize_md+".outputX", global_stretch_bc+".color1.color1R", force=True)
                cmds.connectAttr(global_stretch_bc+".output.outputR", stretchable_bc+".color1.color1R", force=True)
                cmds.connectAttr(stretchable_bc+".output.outputR", stretch_bc+".color1.color1R", force=True)
                cmds.connectAttr(to_parent_extrem_ctrl+".stretchable", stretchable_bc+".blender", force=True)
                cmds.connectAttr(ik_stretch_rev+".outputX", stretch_bc+".blender", force=True)
                # work with world_ref node:
                if cmds.objExists(world_ref):
                    cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlend", ik_stretch_rev+".inputX", force=True)
                    cmds.connectAttr(world_ref+".globalStretch", global_stretch_bc+".blender", force=True)
                    cmds.connectAttr(world_ref+".scaleX", global_stretch_bc+".color2.color2R", force=True)
                    cmds.connectAttr(world_ref+".scaleX", stretchable_bc+".color2.color2R", force=True)
                    cmds.connectAttr(world_ref+".scaleX", stretch_bc+".color2.color2R", force=True)
                # output stretch values to joint scale:
                for j in range(0, len(ik_joints)-2):
                    cmds.connectAttr(stretch_bc+".output.outputR", ik_joints[j]+".scaleX", force=True)
                    cmds.connectAttr(stretch_bc+".output.outputR", ik_joints[j]+".scaleY", force=True)
                    cmds.connectAttr(stretch_bc+".output.outputR", ik_joints[j]+".scaleZ", force=True)
                    cmds.connectAttr(stretch_bc+".output.outputR", self.skin_joints[j]+".scaleZ", force=True)

                # volumeVariation:
                vv_bc = cmds.createNode('blendColors', name=side+self.number_name+"_VV_BC")
                vv_cond = cmds.createNode('condition', name=side+self.number_name+'_VV_Cond')
                vv_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_VV_MD")
                vv_scale_compensate_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_VV_ScaleCompensate_MD")
                vv_clp = cmds.createNode('clamp', name=side+self.number_name+"_VV_Clp")
                cmds.setAttr(vv_clp+".maxR", 1000)
                cmds.connectAttr(to_parent_extrem_ctrl+'.'+self.ar.data.lang['c031_volumeVariation'], vv_bc+'.blender', force=True)
                cmds.connectAttr(to_parent_extrem_ctrl+"."+self.ar.data.lang['c118_active']+self.ar.data.lang['c031_volumeVariation'], vv_cond+'.firstTerm', force=True)
                cmds.connectAttr(to_parent_extrem_ctrl+".min"+self.ar.data.lang['c031_volumeVariation'], vv_clp+'.min.minR', force=True)
                cmds.connectAttr(vv_bc+'.outputR', vv_clp+'.input.inputR', force=True)
                cmds.connectAttr(vv_clp+'.output.outputR', vv_cond+'.colorIfTrueR', force=True)
                cmds.connectAttr(vv_scale_compensate_md+".outputX", vv_bc+'.color1R', force=True)
                cmds.connectAttr(vv_md+".outputX", vv_scale_compensate_md+'.input1X', force=True)
                cmds.connectAttr(world_ref+".scaleX", vv_md+'.input1X', force=True)
                cmds.connectAttr(world_ref+".scaleX", vv_cond+'.colorIfFalseR', force=True)
                cmds.connectAttr(world_ref+".scaleX", vv_scale_compensate_md+'.input2X', force=True)
                cmds.connectAttr(world_ref+".scaleX", vv_bc+'.color2.color2R', force=True)
                cmds.connectAttr(stretch_bc+".output.outputR", vv_md+'.input2X', force=True)
                cmds.setAttr(vv_md+'.operation', 2)
                cmds.setAttr(vv_cond+".secondTerm", 1)
                #output volumeVariation values to joint scale axis:
                for j in range(0, len(self.skin_joints)-2):
                    cmds.connectAttr(vv_cond+".outColorR", self.skin_joints[j]+".scaleX", force=True)
                    cmds.connectAttr(vv_cond+".outColorR", self.skin_joints[j]+".scaleY", force=True)

                # connecting visibilities:
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlend", fk_zeros[0] + ".visibility", force=True)
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlendRevOutputX", ik_ctrl_grp+".visibility", force=True)
                self.ar.ctrls.set_lock_hide(fk_ctrls, ['v'], l=False)
                self.ar.ctrls.set_lock_hide(ik_ctrls, ['v'], l=False)
                
                # last controls drive scale of last joints:
                fk_last_scale_compensate_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_LastScale_Fk_MD")
                ik_last_scale_compensate_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_LastScale_Ik_MD")
                last_scale_bc = cmds.createNode("blendColors", name=side+self.number_name+"_LastScale_BC")
                cmds.connectAttr(world_ref+"."+attr_name_lower+"Fk_ikFkBlend", last_scale_bc+".blender", force=True)
                cmds.connectAttr(fk_joints[-2]+".scaleX", fk_last_scale_compensate_md+'.input1X', force=True)
                cmds.connectAttr(fk_joints[-2]+".scaleY", fk_last_scale_compensate_md+'.input1Y', force=True)
                cmds.connectAttr(fk_joints[-2]+".scaleZ", fk_last_scale_compensate_md+'.input1Z', force=True)
                cmds.connectAttr(ik_joints[-2]+".scaleX", ik_last_scale_compensate_md+'.input1X', force=True)
                cmds.connectAttr(ik_joints[-2]+".scaleY", ik_last_scale_compensate_md+'.input1Y', force=True)
                cmds.connectAttr(ik_joints[-2]+".scaleZ", ik_last_scale_compensate_md+'.input1Z', force=True)
                cmds.connectAttr(world_ref+".scaleX", fk_last_scale_compensate_md+'.input2X', force=True)
                cmds.connectAttr(world_ref+".scaleX", fk_last_scale_compensate_md+'.input2Y', force=True)
                cmds.connectAttr(world_ref+".scaleX", fk_last_scale_compensate_md+'.input2Z', force=True)
                cmds.connectAttr(world_ref+".scaleX", ik_last_scale_compensate_md+'.input2X', force=True)
                cmds.connectAttr(world_ref+".scaleX", ik_last_scale_compensate_md+'.input2Y', force=True)
                cmds.connectAttr(world_ref+".scaleX", ik_last_scale_compensate_md+'.input2Z', force=True)
                cmds.connectAttr(fk_last_scale_compensate_md+".outputX", last_scale_bc+'.color1R', force=True)
                cmds.connectAttr(fk_last_scale_compensate_md+".outputY", last_scale_bc+'.color1G', force=True)
                cmds.connectAttr(fk_last_scale_compensate_md+".outputZ", last_scale_bc+'.color1B', force=True)
                cmds.connectAttr(ik_last_scale_compensate_md+".outputX", last_scale_bc+'.color2R', force=True)
                cmds.connectAttr(ik_last_scale_compensate_md+".outputY", last_scale_bc+'.color2G', force=True)
                cmds.connectAttr(ik_last_scale_compensate_md+".outputZ", last_scale_bc+'.color2B', force=True)
                cmds.connectAttr(last_scale_bc+".outputR", self.skin_joints[-2]+'.scaleX', force=True)
                cmds.connectAttr(last_scale_bc+".outputG", self.skin_joints[-2]+'.scaleY', force=True)
                cmds.connectAttr(last_scale_bc+".outputB", self.skin_joints[-2]+'.scaleZ', force=True)

                # work with main fk controllers
                if cmds.getAttr(self.base+".mainControls"):
                    self.add_fk_main_ctrls(side, fk_ctrls)
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [fk_zeros[0], ik_ctrl_grp, orig_from_items[0], world_ref], [self.skin_joints[0], ik_joints[0], fk_joints[0], ik_cluster_grp], [self.ik_static_grp, ik_main_loc_grp])
                # dynamic
                if self.get_guide_attr("dynamic"):
                    self.create_dynamic_chain(side+self.number_name, world_ref)
                    cmds.xform(self.ctrl_hook_grp, pivots=cmds.xform(ik_ctrl_main, worldSpace=True, rotatePivot=True, query=True))
                # delete duplicated group for side (mirror):
                cmds.delete(self.base, side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.add_attr_to_items(orig_from_items, self.ar.utils.ignore_transform_io_attr)
                self.ar.utils.add_attr_to_items([ik_cluster_grp, ik_ctrl_grp, ik_main_loc_grp, self.ik_static_grp], self.ar.utils.ignore_transform_io_attr)
                self.to_ids.extend([curve_info_node, ik_normalize_md, global_stretch_bc, stretchable_bc, stretch_bc, ik_stretch_rev, vv_bc, vv_cond, vv_md, vv_scale_compensate_md, vv_clp, fk_last_scale_compensate_md, ik_last_scale_compensate_md, last_scale_bc])
                self.ar.custom_attr.add_attr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID


    def fix_mirror_flipping(self, item, s, value=-1, axis=None):
        """ Just flip the controller to fix the mirror issue.
        """
        if s == 1:
            if self.flip:
                if not axis:
                    if self.mirror_axis == "X":
                        cmds.setAttr(item+".scaleZ", value)
                    elif self.mirror_axis == "Y":
                        cmds.setAttr(item+".scaleZ", -value)
                    elif self.mirror_axis == "Z":
                        cmds.setAttr(item+".scaleZ", value)
                else:
                    cmds.setAttr(item+".scale"+axis, value)


    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "worldRefList": self.world_refs,
                            "worldRefShapeList": self.world_ref_shapes,
                        }
