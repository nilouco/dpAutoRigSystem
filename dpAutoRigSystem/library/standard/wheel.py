# Thanks to Andrew Christophersen
# Maya Wheel Rig with World Vectors video tutorial
# https://youtu.be/QpDc93br3dM


# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Wheel"
TITLE = "m156_wheel"
DESCRIPTION = "m157_wheelDesc"
WIKI = "03-‐-Guides#-wheel"



class Wheel(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.add_node_to_guide_net([self.guide_center_loc, self.guide_front_loc, self.guide_inside_loc, self.guide_outside_loc], 
                                   ["CenterLoc", "FrontLoc", "InsideLoc", "OutsideLoc"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="geo", dataType='string')
        cmds.addAttr(self.guide_base, longName="startFrame", attributeType='long', defaultValue=1)
        cmds.addAttr(self.guide_base, longName="showControls", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="steering", attributeType='bool')
        

    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_center_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_CenterLoc", r=0.6, d=1, rot=(90, 0, 90), guide=True)
        self.guide_front_loc = self.ar.ctrls.create_controller("id_059_AimLoc", ctrl_name=self.name_guide+"_FrontLoc", r=0.3, d=1, rot=(0, 0, 90))
        self.guide_inside_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_InsideLoc", r=0.2, d=1, guide=True)
        self.guide_outside_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_OutsideLoc", r=0.2, d=1, guide=True)
        # joints
        self.line_center = cmds.joint(name=self.name_guide+"_JGuideCenter", radius=0.001)
        self.line_front = cmds.joint(name=self.name_guide+"_JGuideFront", radius=0.001)
        self.line_inside = cmds.joint(name=self.name_guide+"_JGuideInside", radius=0.001)
        self.line_outside = cmds.joint(name=self.name_guide+"_JGuideOutside", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_center, self.line_front, self.line_inside, self.line_outside])
        front_loc_pos_pma = cmds.createNode("plusMinusAverage", name=self.guide_front_loc+"_Pos_PMA")
        inverse_radius_md = cmds.createNode("multiplyDivide", name=self.guide_base+"_Radius_Inv_MD")
        cmds.setAttr(self.guide_front_loc+".tx", 1.3)
        cmds.setAttr(self.guide_inside_loc+".tz", 0.3)
        cmds.setAttr(self.guide_outside_loc+".tz", -0.3)
        cmds.setAttr(front_loc_pos_pma+".input1D[0]", -0.5)
        cmds.setAttr(inverse_radius_md+".input2X", -1)
        # parenting
        cmds.parent(self.line_center, self.guide_center_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_front_loc, self.guide_inside_loc, self.guide_outside_loc, self.guide_center_loc)
        cmds.parent(self.line_inside, self.line_outside, self.line_center)
        # edit
        cmds.connectAttr(self.radius_ctrl+".translateX", front_loc_pos_pma+".input1D[1]")
        cmds.connectAttr(front_loc_pos_pma+".output1D", self.guide_front_loc+".tx")
        cmds.connectAttr(self.radius_ctrl+".translateX", inverse_radius_md+".input1X")
        cmds.connectAttr(inverse_radius_md+".outputX", self.guide_inside_loc+".translateY")
        cmds.connectAttr(inverse_radius_md+".outputX", self.guide_outside_loc+".translateY")
        cmds.transformLimits(self.guide_front_loc, translationX=(1, 1), enableTranslationX=(True, False))
        cmds.transformLimits(self.guide_inside_loc, tz=(0.01, 1), etz=(True, False))
        cmds.transformLimits(self.guide_outside_loc, tz=(-1, 0.01), etz=(False, True))
        self.ar.ctrls.color_shape([self.guide_front_loc], "blue")
        self.ar.ctrls.shape_size_setup(self.guide_front_loc)
        self.ar.ctrls.set_lock_hide([self.guide_inside_loc, self.guide_outside_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        self.ar.ctrls.set_lock_hide([self.guide_center_loc, self.guide_front_loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.parentConstraint(self.guide_center_loc, self.line_center, maintainOffset=False, name=self.line_center+"_PaC")
        cmds.parentConstraint(self.guide_front_loc, self.line_front, maintainOffset=False, name=self.line_front+"_PaC")
        cmds.parentConstraint(self.guide_inside_loc, self.line_inside, maintainOffset=False, name=self.guide_inside_loc+"_PaC")
        cmds.parentConstraint(self.guide_outside_loc, self.line_outside, maintainOffset=False, name=self.guide_outside_loc+"_PaC")
    
        
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.main_ctrls, self.wheel_ctrls, self.steering_grps, self.ctrl_hook_grps = [], [], [], []
            # run for all sides
            for s, side in enumerate(self.sides):
                # declare guides:
                self.base = side+self.number_name+'_Guide_Base'
                self.guide_center_loc = side+self.number_name+"_Guide_CenterLoc"
                self.guide_front_loc = side+self.number_name+"_Guide_FrontLoc"
                self.guide_inside_loc = side+self.number_name+"_Guide_InsideLoc"
                self.guide_outside_loc = side+self.number_name+"_Guide_OutsideLoc"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                
                # create a joint:
                cmds.select(clear=True)
                # center joint:
                center_joint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(center_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.ar.utils.set_joint_label(center_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['m156_wheel'])
                self.create_end_joint(side+self.number_name+"_"+self.ar.data.lang['m156_wheel'], self.guide_front_loc)
                # main joint:
                cmds.select(clear=True)
                main_joint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang['c058_main']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(main_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.ar.utils.set_joint_label(main_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c058_main'])
                self.create_end_joint(side+self.number_name+"_"+self.ar.data.lang['c058_main'], self.guide_front_loc)
                
                # create controls:
                wheel_ctrl = self.ar.ctrls.create_controller("id_060_WheelCenter", side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.name_guide+"_CenterLoc")
                # add clip shape on wheel shape and optimize control CV shapes:
                self.ar.ctrls.transfer_shape(delete_source = True, clear_dest_shapes=False, source_item=self.ar.ctrls.create_controller("Clip", side+self.number_name+"_"+self.ar.data.lang['m106_clip']+"_Ctrl", r=self.radius*0.2, d=self.curve_degree, rot = (0, 0, 0) ), destinations=[wheel_ctrl], keep_color=False)
                self.ar.ctrls.transfer_shape(delete_source = True, clear_dest_shapes=False, source_item=self.ar.ctrls.create_controller("Clip", side+self.number_name+"_"+self.ar.data.lang['m106_clip']+"_Ctrl", r=self.radius*0.2, d=self.curve_degree, rot = (0, 0, 90) ), destinations=[wheel_ctrl], keep_color=False)
                self.ar.ctrls.transfer_shape(delete_source = True, clear_dest_shapes=False, source_item=self.ar.ctrls.create_controller("Clip", side+self.number_name+"_"+self.ar.data.lang['m106_clip']+"_Ctrl", r=self.radius*0.2, d=self.curve_degree, rot = (0, 0, 180) ), destinations=[wheel_ctrl], keep_color=False)
                self.ar.ctrls.transfer_shape(delete_source = True, clear_dest_shapes=False, source_item=self.ar.ctrls.create_controller("Clip", side+self.number_name+"_"+self.ar.data.lang['m106_clip']+"_Ctrl", r=self.radius*0.2, d=self.curve_degree, rot = (0, 0, 270) ), destinations=[wheel_ctrl], keep_color=False)
                # optimize control CV shapes:
                cmds.setAttr(cmds.cluster(wheel_ctrl+"1Shape"+".cv[1:]")[1]+".translateY", self.radius*0.9)
                cmds.setAttr(cmds.cluster(wheel_ctrl+"2Shape"+".cv[1:]")[1]+".translateX", -self.radius*0.9)
                cmds.setAttr(cmds.cluster(wheel_ctrl+"3Shape"+".cv[1:]")[1]+".translateY", -self.radius*0.9)
                cmds.setAttr(cmds.cluster(wheel_ctrl+"4Shape"+".cv[1:]")[1]+".translateX", self.radius*0.9)
                cmds.delete(wheel_ctrl, constructionHistory=True)
                
                # create defaults controls shape
                main_ctrl = self.ar.ctrls.create_controller("id_061_WheelMain", side+self.number_name+"_"+self.ar.data.lang['c058_main']+"_Ctrl", r=self.radius*0.4, d=self.curve_degree, guide_source=self.name_guide+"_CenterLoc", parent_tag=wheel_ctrl)
                inside_ctrl = self.ar.ctrls.create_controller("id_062_WheelPivot", side+self.number_name+"_"+self.ar.data.lang['c011_revFoot_B'].capitalize()+"_Ctrl", r=self.radius*0.2, d=self.curve_degree, rot=(0, 90, 0), guide_source=self.name_guide+"_InsideLoc", parent_tag=main_ctrl)
                outside_ctrl = self.ar.ctrls.create_controller("id_062_WheelPivot", side+self.number_name+"_"+self.ar.data.lang['c010_revFoot_A'].capitalize()+"_Ctrl", r=self.radius*0.2, d=self.curve_degree, rot=(0, 90, 0), guide_source=self.name_guide+"_OutsideLoc", parent_tag=main_ctrl)
                self.main_ctrls.append(main_ctrl)
                self.wheel_ctrls.append(wheel_ctrl)

                # origined from attributes:
                self.ar.utils.set_origined_from_attr(main_ctrl, self.base+";"+self.guide_center_loc+";"+self.guide_front_loc+";"+self.guide_radius)
                self.ar.utils.set_origined_from_attr(inside_ctrl, self.guide_inside_loc)
                self.ar.utils.set_origined_from_attr(outside_ctrl, self.guide_outside_loc)
                
                # prepare group to receive steering wheel connection:
                to_steering_grp = cmds.group(inside_ctrl, name=side+self.number_name+"_"+self.ar.data.lang['c070_steering'].capitalize()+"_Grp")
                cmds.addAttr(to_steering_grp, longName=self.ar.data.lang['c070_steering'], attributeType='bool', keyable=True)
                cmds.addAttr(to_steering_grp, longName=self.ar.data.lang['c070_steering']+self.ar.data.lang['m151_invert'], attributeType='bool', keyable=True)
                cmds.setAttr(to_steering_grp+"."+self.ar.data.lang['c070_steering'], 1)
                self.steering_grps.append(to_steering_grp)
                
                # position and orientation of joint and control:
                cmds.matchTransform(center_joint, self.guide_center_loc, position=True, rotation=True)
                cmds.matchTransform(wheel_ctrl, self.guide_center_loc, position=True, rotation=True)
                cmds.matchTransform(main_ctrl, self.guide_center_loc, position=True, rotation=True)
                cmds.parentConstraint(main_ctrl, main_joint, maintainOffset=False, name=main_joint+"_PaC")
                cmds.scaleConstraint(main_ctrl, main_joint, maintainOffset=True, name=main_joint+"_ScC")
                if s == 1 and cmds.getAttr(self.guide_base+".flip") == 1:
                    cmds.move(self.radius, main_ctrl, moveY=True, relative=True, objectSpace=True, worldSpaceDistance=True)
                else:
                    cmds.move(-self.radius, main_ctrl, moveY=True, relative=True, objectSpace=True, worldSpaceDistance=True)
                cmds.matchTransform(to_steering_grp, self.guide_inside_loc, position=True, rotation=True)
                cmds.matchTransform(outside_ctrl, self.guide_outside_loc, position=True, rotation=True)
                
                # create_zero_out controls:
                zeros = self.ar.utils.create_zero_out([main_ctrl, wheel_ctrl, to_steering_grp, outside_ctrl])
                wheel_auto_grp = self.ar.utils.create_zero_out([wheel_ctrl])
                wheel_auto_grp = cmds.rename(wheel_auto_grp, side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Auto_Grp")
                
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        for zero_grp in zeros:
                            cmds.setAttr(zero_grp+".scaleX", -1)
                            cmds.setAttr(zero_grp+".scaleY", -1)
                            cmds.setAttr(zero_grp+".scaleZ", -1)
                
                cmds.addAttr(wheel_ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                cmds.setAttr(wheel_ctrl+".scaleCompensate", 1, channelBox=True)
                cmds.connectAttr(wheel_ctrl+".scaleCompensate", center_joint+".segmentScaleCompensate", force=True)
                cmds.addAttr(main_ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                cmds.setAttr(main_ctrl+".scaleCompensate", 1, channelBox=True)
                cmds.connectAttr(main_ctrl+".scaleCompensate", main_joint+".segmentScaleCompensate", force=True)
                # hide visibility attributes:
                self.ar.ctrls.set_lock_hide([main_ctrl, inside_ctrl, outside_ctrl], ['v'])
                self.ar.ctrls.set_lock_hide([wheel_ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v', 'ro'])
                
                # grouping:
                cmds.parentConstraint(wheel_ctrl, center_joint, maintainOffset=False, name=center_joint+"_PaC")
                cmds.scaleConstraint(wheel_ctrl, center_joint, maintainOffset=True, name=center_joint+"_ScC")
                cmds.parent(zeros[1], main_ctrl, absolute=True)
                cmds.parent(zeros[0], outside_ctrl, absolute=True)
                cmds.parent(zeros[3], inside_ctrl, absolute=True)
                
                # add attributes:
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c047_autoRotate'], attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c068_startFrame'], attributeType="long", defaultValue=1, keyable=False)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c067_radius'], attributeType="float", min=0.01, defaultValue=self.radius, keyable=True)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c069_radiusScale'], attributeType="float", defaultValue=1, keyable=False)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c021_showControls'], attributeType="long", min=0, max=1, defaultValue=1, keyable=True)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c070_steering'], attributeType="short", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['i037_to']+self.ar.data.lang['c070_steering'].capitalize(), attributeType="float", defaultValue=0, keyable=False)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c070_steering']+self.ar.data.lang['c053_invert'].capitalize(), attributeType="long", min=0, max=1, defaultValue=1, keyable=False)
                cmds.addAttr(wheel_ctrl, longName=self.ar.data.lang['c093_tryKeepUndo'], attributeType="long", min=0, max=1, defaultValue=1, keyable=False)
                
                # get stored values by user:
                start_frame_value = cmds.getAttr(self.guide_base+".startFrame")
                steering_value = cmds.getAttr(self.guide_base+".steering")
                show_ctrls_value = cmds.getAttr(self.guide_base+".showControls")
                cmds.setAttr(wheel_ctrl+"."+self.ar.data.lang['c068_startFrame'], start_frame_value, channelBox=True)
                cmds.setAttr(wheel_ctrl+"."+self.ar.data.lang['c070_steering'], steering_value, channelBox=True)
                cmds.setAttr(wheel_ctrl+"."+self.ar.data.lang['c021_showControls'], show_ctrls_value, channelBox=True)
                cmds.setAttr(wheel_ctrl+"."+self.ar.data.lang['c070_steering']+self.ar.data.lang['c053_invert'].capitalize(), 1, channelBox=True)
                self.ar.ctrls.set_default_value(wheel_ctrl, self.ar.data.lang['c070_steering']+self.ar.data.lang['c053_invert'].capitalize(), 1)
                cmds.setAttr(wheel_ctrl+"."+self.ar.data.lang['c093_tryKeepUndo'], 1, channelBox=True)
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.setAttr(wheel_ctrl+"."+self.ar.data.lang['c070_steering']+self.ar.data.lang['c053_invert'].capitalize(), 0)
                        self.ar.ctrls.set_default_value(wheel_ctrl, self.ar.data.lang['c070_steering']+self.ar.data.lang['c053_invert'].capitalize(), 0)
                # set default values:
                self.ar.ctrls.set_default_value(wheel_ctrl, self.ar.data.lang['c068_startFrame'], start_frame_value)
                self.ar.ctrls.set_default_value(wheel_ctrl, self.ar.data.lang['c070_steering'], steering_value)
                self.ar.ctrls.set_default_value(wheel_ctrl, self.ar.data.lang['c021_showControls'], show_ctrls_value)
                self.ar.ctrls.set_default_value(wheel_ctrl, self.ar.data.lang['c093_tryKeepUndo'], 1)
                
                # automatic rotation wheel setup:
                recept_steering_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_"+self.ar.data.lang['c070_steering'].capitalize()+"_MD")
                inverse_steering_md = cmds.createNode('multiplyDivide', name=side+self.number_name+"_"+self.ar.data.lang['c070_steering'].capitalize()+"_Inv_MD")
                inverse_steering_cnd = cmds.createNode('condition', name=side+self.number_name+"_"+self.ar.data.lang['c070_steering'].capitalize()+"_Inv_Cnd")
                cmds.setAttr(inverse_steering_cnd+".colorIfTrueR", 1)
                cmds.setAttr(inverse_steering_cnd+".colorIfFalseR", -1)
                cmds.connectAttr(wheel_ctrl+"."+self.ar.data.lang['i037_to']+self.ar.data.lang['c070_steering'].capitalize(), recept_steering_md+".input1X", force=True)
                cmds.connectAttr(wheel_ctrl+"."+self.ar.data.lang['c070_steering'], recept_steering_md+".input2X", force=True)
                cmds.connectAttr(recept_steering_md+".outputX", inverse_steering_md+".input1X", force=True)
                cmds.connectAttr(inverse_steering_cnd+".outColorR", inverse_steering_md+".input2X", force=True)
                cmds.connectAttr(wheel_ctrl+"."+self.ar.data.lang['c070_steering']+self.ar.data.lang['c053_invert'].capitalize(), inverse_steering_cnd+".firstTerm", force=True)
                cmds.connectAttr(inverse_steering_md+".outputX", to_steering_grp+".rotateY", force=True)
                # create locators (frontLoc to get direction and oldLoc to store wheel old position):
                front_loc = cmds.spaceLocator(name=side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Front_Loc")[0]
                old_loc = cmds.spaceLocator(name=side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Old_Loc")[0]
                cmds.matchTransform(front_loc, self.guide_front_loc, position=True, rotation=True)
                cmds.parent(front_loc, main_ctrl)
                cmds.matchTransform(old_loc, self.guide_center_loc, position=True, rotation=True)
                cmds.setAttr(front_loc+".visibility", 0, lock=True)
                cmds.setAttr(old_loc+".visibility", 0, lock=True)
                # this wheel auto group locator could be replaced by a decomposeMatrix to get the translation in world space of the Wheel_Auto_Ctrl_Grp instead:
                wheel_auto_grp_loc = cmds.spaceLocator(name=side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Auto_Loc")[0]
                cmds.pointConstraint(wheel_auto_grp, wheel_auto_grp_loc, maintainOffset=False, name=wheel_auto_grp_loc+"_PoC")
                cmds.setAttr(wheel_auto_grp_loc+".visibility", 0, lock=True)
                exp_text =  "if ("+wheel_ctrl+"."+self.ar.data.lang['c047_autoRotate']+" == 1) {"+\
                            "\nif ("+wheel_ctrl+"."+self.ar.data.lang['c093_tryKeepUndo']+" == 1) { undoInfo -stateWithoutFlush 0; };"+\
                            "\nfloat $radius = "+wheel_ctrl+"."+self.ar.data.lang['c067_radius']+" * "+wheel_ctrl+"."+self.ar.data.lang['c069_radiusScale']+\
                            ";\nvector $moveVectorOld = `xform -q -ws -t \""+old_loc+\
                            "\"`;\nvector $moveVector = << "+wheel_auto_grp_loc+".translateX, "+wheel_auto_grp_loc+".translateY, "+wheel_auto_grp_loc+".translateZ >>;"+\
                            "\nvector $dirVector = `xform -q -ws -t \""+front_loc+\
                            "\"`;\nvector $wheelVector = ($dirVector - $moveVector);"+\
                            "\nvector $motionVector = ($moveVector - $moveVectorOld);"+\
                            "\nfloat $distance = mag($motionVector);"+\
                            "\n$dot = dotProduct($motionVector, $wheelVector, 1);\n"+\
                            wheel_auto_grp+".rotateZ = "+wheel_auto_grp+".rotateZ - 360 / (6.283*$radius) * ($dot*$distance);"+\
                            "\nxform -t ($moveVector.x) ($moveVector.y) ($moveVector.z) "+old_loc+\
                            ";\nif (frame == "+wheel_ctrl+"."+self.ar.data.lang['c068_startFrame']+") { "+wheel_auto_grp+".rotateZ = 0; };"+\
                            "\nif ("+wheel_ctrl+"."+self.ar.data.lang['c093_tryKeepUndo']+" == 1) { undoInfo -stateWithoutFlush 1; };};"
                # expression:
                exp_node = cmds.expression(name=side+self.number_name+"_"+self.ar.data.lang['m156_wheel']+"_Exp", object=front_loc, string=exp_text)
                self.ar.ctrls.set_lock_hide([front_loc, wheel_auto_grp_loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                
                # deformers:
                loaded_geo = cmds.getAttr(self.guide_base+".geo")
                
                # geometry holder:
                geo_holder = cmds.polyCube(name=side+self.number_name+"_"+self.ar.data.lang['c046_holder']+"_Geo", constructionHistory=False)[0]
                cmds.matchTransform(geo_holder, self.guide_center_loc, position=True, rotation=True)
                cmds.setAttr(geo_holder+".visibility", 0, lock=True)
                
                # skinning:
                skincluster_node = cmds.skinCluster(center_joint, geo_holder, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=side+self.number_name+"_"+self.ar.data.lang['c046_holder']+"_SC")[0]
                bindpose_node = cmds.listConnections(skincluster_node+".bindPose", destination=False, source=True)
                cmds.rename(bindpose_node, side+self.number_name+"_"+self.ar.data.lang['c046_holder']+"_BP")
                if loaded_geo:
                    if cmds.objExists(loaded_geo):
                        base_name = self.ar.utils.extract_suffix(loaded_geo)
                        skincluster_name = base_name+"_SC"
                        if "|" in skincluster_name:
                            skincluster_name = skincluster_name[skincluster_name.rfind("|")+1:]
                        try:
                            cmds.skinCluster(center_joint, loaded_geo, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skincluster_name)
                        except:
                            for item in cmds.listRelatives(loaded_geo, children=True, allDescendents=True) or []:
                                item_type = cmds.objectType(item)
                                if item_type == "mesh" or item_type == "nurbsSurface":
                                    try:
                                        skincluster_name = self.ar.utils.extract_suffix(item)+"_SC"
                                        cmds.skinCluster(center_joint, item, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skincluster_name)
                                    except:
                                        pass
                
                # lattice:
                lattice_items = cmds.lattice(geo_holder, divisions=(6, 6, 6), outsideLattice=2, outsideFalloffDistance=1, position=(0, 0, 0), scale=(self.radius*2, self.radius*2, self.radius*2), name=side+self.number_name+"_FFD") #[deformer, lattice, base]
                cmds.scale(self.radius*2, self.radius*2, self.radius*2, lattice_items[2])
                # clusters:
                upper_clusters = cmds.cluster(lattice_items[1]+".pt[0:5][4:5][0:5]", relative=True, name=side+self.number_name+"_"+self.ar.data.lang['c044_upper']+"_Cls") #[deform, handle]
                middle_clusters = cmds.cluster(lattice_items[1]+".pt[0:5][2:3][0:5]", relative=True, name=side+self.number_name+"_"+self.ar.data.lang['m033_middle']+"_Cls") #[deform, handle]
                lower_clusters = cmds.cluster(lattice_items[1]+".pt[0:5][0:1][0:5]", relative=True, name=side+self.number_name+"_"+self.ar.data.lang['c045_lower']+"_Cls") #[deform, handle]                
                cluster_grps = self.ar.utils.create_zero_out([upper_clusters[1], middle_clusters[1], lower_clusters[1]])
                cluster_grp = cmds.group(cluster_grps, name=side+self.number_name+"_Clusters_Grp")
                
                # deform controls:
                upper_def_ctrl = self.ar.ctrls.create_controller("id_063_WheelDeform", side+self.number_name+"_"+self.ar.data.lang['c044_upper']+"_Ctrl", r=self.radius*0.5, d=self.curve_degree, guide_source=self.name_guide+"_CenterLoc", parent_tag=wheel_ctrl)
                middle_def_ctrl = self.ar.ctrls.create_controller("id_064_WheelMiddle", side+self.number_name+"_"+self.ar.data.lang['m033_middle']+"_Ctrl", r=self.radius*0.5, d=self.curve_degree, guide_source=self.name_guide+"_CenterLoc", parent_tag=wheel_ctrl)
                lower_def_ctrl = self.ar.ctrls.create_controller("id_063_WheelDeform", side+self.number_name+"_"+self.ar.data.lang['c045_lower']+"_Ctrl", r=self.radius*0.5, d=self.curve_degree, rot=(0, 0, 180), guide_source=self.name_guide+"_CenterLoc", parent_tag=wheel_ctrl)
                def_ctrl_grps = self.ar.utils.create_zero_out([upper_def_ctrl, middle_def_ctrl, lower_def_ctrl])
                def_ctrl_grp = cmds.group(def_ctrl_grps, name=side+self.number_name+"_Ctrl_Grp")
                
                # positions:
                cmds.matchTransform(def_ctrl_grps[0], upper_clusters[1], position=True, rotation=True)
                cmds.matchTransform(def_ctrl_grps[1], middle_clusters[1], position=True, rotation=True)
                cmds.matchTransform(def_ctrl_grps[2], lower_clusters[1], position=True, rotation=True)
                if s == 1: #fix right side controllers upper/lower flipping - workaround
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        self.ar.utils.unlock_attr([self.guide_center_loc])
                        cmds.parent(self.guide_center_loc, world=True)
                cmds.matchTransform(lattice_items[1], self.guide_center_loc, position=True, rotation=True)
                cmds.matchTransform(lattice_items[2], self.guide_center_loc, position=True, rotation=True)
                cmds.matchTransform(cluster_grp, self.guide_center_loc, position=True, rotation=True)
                cmds.matchTransform(def_ctrl_grp, self.guide_center_loc, position=True, rotation=True)
                outside_dist = cmds.getAttr(self.guide_outside_loc+".tz")
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.parent(self.guide_center_loc, self.guide_base)
                        outside_dist = -outside_dist
                cmds.move(outside_dist, def_ctrl_grp, moveZ=True, relative=True, objectSpace=True, worldSpaceDistance=True)
                self.ar.ctrls.direct_connect(upper_def_ctrl, upper_clusters[1])
                self.ar.ctrls.direct_connect(middle_def_ctrl, middle_clusters[1])
                self.ar.ctrls.direct_connect(lower_def_ctrl, lower_clusters[1])
                # grouping deformers:
                if loaded_geo:
                    if cmds.objExists(loaded_geo):
                        cmds.lattice(lattice_items[0], edit=True, geometry=loaded_geo)
                def_grp = cmds.group(lattice_items[1], lattice_items[2], cluster_grp, name=side+self.number_name+"_Deform_Grp")
                cmds.parentConstraint(main_ctrl, def_grp, maintainOffset=True, name=def_grp+"_PaC")
                cmds.scaleConstraint(main_ctrl, def_grp, maintainOffset=True, name=def_grp+"_ScC")
                cmds.parent(def_ctrl_grp, main_ctrl)
                cmds.connectAttr(wheel_ctrl+"."+self.ar.data.lang['c021_showControls'], def_ctrl_grp+".visibility", force=True)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [zeros[2]], [center_joint, main_joint, def_grp], [old_loc, wheel_auto_grp_loc, geo_holder])
                self.ctrl_hook_grps.append(self.ctrl_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.add_attr_to_items([to_steering_grp, cluster_grp, def_ctrl_grp, def_grp, lattice_items[1], lattice_items[2], geo_holder], self.ar.utils.ignore_transform_io_attr)
                
                self.to_ids.extend([recept_steering_md, inverse_steering_md, inverse_steering_cnd, exp_node, geo_holder, skincluster_node, side+self.number_name+"_"+self.ar.data.lang['c046_holder']+"_BP"])
                for ids in [lattice_items, upper_clusters, middle_clusters, lower_clusters]:
                    self.to_ids.extend(ids)
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
                            "mainCtrlList"    : self.main_ctrls,
                            "wheelCtrlList"   : self.wheel_ctrls,
                            "steeringGrpList" : self.steering_grps,
                            "ctrlHookGrpList" : self.ctrl_hook_grps,
                        }


###
#
# Wheel Auto Rotation Expression:
#
# if (Wheel_Ctrl.autoRotate == 1) {
# if (Wheel_Ctrl.tryKeepUndo == 1) { undoInfo -stateWithoutFlush 0; };
# float $radius = Wheel_Ctrl.radius * Wheel_Ctrl.radiusScale;
# vector $moveVectorOld = `xform -q -ws -t "Wheel_Old_Loc"`;
# vector $moveVector = << L_BackWheel_Wheel_Auto_Loc.translateX, L_BackWheel_Wheel_Auto_Loc.translateY, L_BackWheel_Wheel_Auto_Loc.translateZ >>;
# vector $dirVector = `xform -q -ws -t "Wheel_Front_Loc"`;
# vector $wheelVector = ($dirVector - $moveVector);
# vector $motionVector = ($moveVector - $moveVectorOld);
# float $distance = mag($motionVector);
# $dot = dotProduct($motionVector, $wheelVector, 1);
# L_BackWheel_Wheel_Auto_Grp.rotateZ = L_BackWheel_Wheel_Auto_Grp.rotateZ - 360 / (6.283*$radius) * ($dot*$distance);
# xform -t ($moveVector.x) ($moveVector.y) ($moveVector.z) Wheel_Old_Loc;
# if (frame == Wheel_Ctrl.startFrame) { L_BackWheel_Wheel_Auto_Grp.rotateZ = 0; };
# if (Wheel_Ctrl.tryKeepUndo == 1) { undoInfo -stateWithoutFlush 1; };};
#
###