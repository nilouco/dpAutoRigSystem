#import libraries
import re
import time
import getpass
from maya import cmds



class Maker(object):
    def __init__(self, ar):
        self.ar = ar


    def create_raw_guide(self, module, *args):
        mod = self.ar.lib.initialize_library(module, self.ar.data.standard_folder)[0]
        return [mod, mod.build_raw_guide()]


    # .............................................................................. start here --- unused yet / or delete it
    #
    # TODO: it isn't used yet.
    #
    def set_new_guide(self, module, name, t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1), size=1, radius=2, end=1.3, mirror=None, flip=1, deformed=0, indSkin=0, annot=1, annot_pos=None, parent=None, progress=True):
        """ Creates a new standard guide, set the given values and returns a list with the imported module and the created guide.
        """
        if progress:
            self.ar.ui_manager.set_progress(self.ar.data.lang['m094_doing']+name)
            cmds.refresh()
        mod, guide = self.create_raw_guide(module)
        mod.set_guide_custom_name(name)
        cmds.setAttr(mod.radius_ctrl+".translateX", radius)
        cmds.setAttr(mod.cvEndJoint+".translateZ", end)
        cmds.setAttr(guide+".translateX", t[0])
        cmds.setAttr(guide+".translateY", t[1])
        cmds.setAttr(guide+".translateZ", t[2])
        cmds.setAttr(guide+".rotateX", r[0])
        cmds.setAttr(guide+".rotateY", r[1])
        cmds.setAttr(guide+".rotateZ", r[2])
        cmds.setAttr(guide+".scaleX", s[0])
        cmds.setAttr(guide+".scaleY", s[1])
        cmds.setAttr(guide+".scaleZ", s[2])
        cmds.setAttr(guide+".shapeSize", size)
        if mirror:
            mod.change_mirror(mirror)
            cmds.setAttr(guide+".flip", flip)
        if deformed:
            cmds.setAttr(guide+".deformedBy", deformed)
        if indSkin:
            cmds.setAttr(guide+".indirectSkin", indSkin)
        cmds.setAttr(guide+".displayAnnotation", annot)
        cmds.setAttr(guide+"_Ant.visibility", annot)
        if annot_pos:
            cmds.setAttr(mod.annotation+".translateX", annot_pos[0])
            cmds.setAttr(mod.annotation+".translateY", annot_pos[1])
            cmds.setAttr(mod.annotation+".translateZ", annot_pos[2])
        else:
            cmds.setAttr(mod.annotation+".translateX", 0)
            cmds.setAttr(mod.annotation+".translateY", radius)
            cmds.setAttr(mod.annotation+".translateZ", 0)
        if parent:
            cmds.parent(guide, parent, absolute=True)
        return [mod, guide]
    #
    #
    # .............................................................................. end here --- unused yet / or delete it


    def create_template(self, name=None, *args):
        self.ar.ui_manager.refresh_ui()
        nets = self.ar.utils.get_network_by_attr("dpGuideNet")
        nets.extend(self.ar.utils.get_network_by_attr("dpHeadDeformerNet") or [])
        if nets:
            self.ar.job.unpin_guide(force=True)
            guide_io = self.ar.config.get_instance("GuideIO", [self.ar.data.setup_folder])
            guides_data = guide_io.get_guide_data(nets)
            if not name:
                if self.ar.data.ui_state:
                    if self.ar.data.ui_state:
                        name = self.ar.ui_manager.ask_prompt_dialog("Template", self.ar.data.lang["m006_name"]).lower()
            if name:
                # export json file
                self.ar.pipeliner.save_json_file(guides_data, f"{self.ar.data.dp_auto_rig_path}/{self.ar.data.template_folder.replace('.', '/')}/{name}.json")
                print(self.ar.data.lang["i133_presetCreated"], name)
                self.ar.ui_manager.reload_ui()
        else:
            print(self.ar.data.lang["e000_guideNotFound"])


    def setup_duplicated_guide(self, selected_item, *args):
        """ This method will create a new module instance for a duplicated guide found.
            Returns the guide_base of the new module instance.
        """
        # Duplicating a module guide
        print(self.ar.data.lang['i067_duplicating'])
        self.ar.ui_manager.set_progress("dpAutoRigSystem", self.ar.data.lang['i067_duplicating'], max=3, add_one=False, add_number=False)
        # declaring variables
        segments_attr = "nJoints"
        custom_name_attr = "customName"
        mirror_axis_attr = "mirrorAxis"
        display_annotation_attr = "displayAnnotation"
        net_attr = "net"

        # unparenting
        parents = cmds.listRelatives(selected_item, parent=True)
        if parents:
            cmds.parent(selected_item, world=True)
            selected_item = selected_item[selected_item.rfind("|"):]

        # getting duplicated item values
        module_namespace_value = cmds.getAttr(selected_item+"."+self.ar.data.module_namespace_attr)
        module_instance_info_value = cmds.getAttr(selected_item+"."+self.ar.data.module_instance_info_attr)
        # generating naming values
        that_class_name = module_namespace_value.partition("__")[0]
        that_module_name = module_instance_info_value[:module_instance_info_value.rfind(that_class_name)-1]
        that_module_name = that_module_name[that_module_name.rfind(".")+1:]
        module_folder = module_instance_info_value[:module_instance_info_value.rfind(that_module_name)-1]
        module_folder = module_folder[module_folder.find(".")+1:]
        self.ar.ui_manager.set_progress(self.ar.data.lang['i067_duplicating'])
        # initializing a new module instance
        new_guide_instance, new_guide_name = self.create_raw_guide(that_module_name, self.ar.data.standard_folder)
        new_guide_namespace = cmds.getAttr(new_guide_name+"."+self.ar.data.module_namespace_attr)
                
        # getting a good attribute list
        to_set_attrs = cmds.listAttr(selected_item)
        current_attrs = to_set_attrs.copy()
        to_set_attrs = to_set_attrs[to_set_attrs.index(self.ar.data.guide_base_attr):]
        to_set_attrs.remove(self.ar.data.guide_base_attr)
        to_set_attrs.remove(self.ar.data.module_namespace_attr)
        to_set_attrs.remove(custom_name_attr)
        to_set_attrs.remove(mirror_axis_attr)
        # check for special attributes
        if segments_attr in current_attrs:
            to_set_attrs.remove(segments_attr)
            segments_value = cmds.getAttr(selected_item+'.'+segments_attr)
            if segments_value > 0:
                new_guide_instance.change_joint_number(segments_value)
        self.ar.ui_manager.set_progress(self.ar.data.lang['i067_duplicating'])
        if custom_name_attr in current_attrs:
            custom_name_value = cmds.getAttr(selected_item+'.'+custom_name_attr)
            if custom_name_value != "" and custom_name_value != None:
                new_guide_instance.set_guide_custom_name(custom_name_value)
        self.ar.ui_manager.set_progress(self.ar.data.lang['i067_duplicating'])
        if mirror_axis_attr in current_attrs:
            mirror_axis_value = cmds.getAttr(selected_item+'.'+mirror_axis_attr)
            if mirror_axis_value != "off":
                new_guide_instance.change_mirror(mirror_axis_value)
        if display_annotation_attr in current_attrs:
            to_set_attrs.remove(display_annotation_attr)
            new_guide_instance.display_annotation(cmds.getAttr(selected_item+'.'+display_annotation_attr))
        if net_attr in current_attrs:
            to_set_attrs.remove(net_attr)
        
        # TODO: change to unify style and type attributes        
        if "type" in current_attrs:
            typeValue = cmds.getAttr(selected_item+'.type')
            new_guide_instance.change_type(typeValue)
        if "style" in current_attrs:
            styleValue = cmds.getAttr(selected_item+'.style')
            new_guide_instance.changeStyle(styleValue)
        
        # get and set transformations
        children = cmds.listRelatives(selected_item, children=True, allDescendents=True, fullPath=True, type="transform")
        if children:
            for child in children:
                if not "|Guide_Base|Guide_Base" in child:
                    new_child = new_guide_namespace+":"+child[child.rfind("|")+1:]
                    for transform_attr in self.ar.data.transform_attrs:
                        try:
                            is_locked = cmds.getAttr(child+"."+transform_attr, lock=True)
                            cmds.setAttr(new_child+"."+transform_attr, lock=False)
                            cmds.setAttr(new_child+"."+transform_attr, cmds.getAttr(child+"."+transform_attr))
                            if is_locked:
                                cmds.setAttr(new_child+"."+transform_attr, lock=True)
                        except:
                            pass
        # set transformation for Guide_Base
        for transform_attr in self.ar.data.transform_attrs:
            cmds.setAttr(new_guide_name+"."+transform_attr, cmds.getAttr(selected_item+"."+transform_attr))
        
        # setting new guide attributes
        for to_set_attr in to_set_attrs:
            try:
                cmds.setAttr(new_guide_name+"."+to_set_attr, cmds.getAttr(selected_item+"."+to_set_attr))
            except:
                if cmds.getAttr(selected_item+"."+to_set_attr):
                    cmds.setAttr(new_guide_name+"."+to_set_attr, cmds.getAttr(selected_item+"."+to_set_attr), type="string")
        cmds.setAttr(new_guide_name+"_RadiusCtrl.translateX", cmds.getAttr(module_namespace_value+":"+self.ar.data.guide_base_name+"_RadiusCtrl.translateX"))
        
        # parenting correctly
        if parents:
            cmds.parent(new_guide_name, parents[0])

        cmds.delete(selected_item)
        print(self.ar.data.lang['r006_wellDone']+" "+new_guide_name)
        self.ar.ui_manager.set_progress(end_it=True)
        return new_guide_name
    

    def get_base_group(self, attr, item, olds=None):
        if not cmds.objExists(item):
            need_create_it = True
            if olds:
                if cmds.objExists(olds[1]):
                    attr = olds[0]
                    item = olds[1]
                    need_create_it = False
            if need_create_it:
                cmds.createNode("transform", name=item)
        if not attr in cmds.listAttr(self.all_grp):
            cmds.addAttr(self.all_grp, longName=attr, attributeType="message")
        if not cmds.listConnections(self.all_grp+"."+attr, destination=False, source=True):
            cmds.connectAttr(item+".message", self.all_grp+"."+attr, force=True)
        self.ar.custom_attr.add_attr(0, [item]) #dpID
        return item
    

    def get_base_controller(self, ctrl_type, attr, item, radius, degree=1):
        self.ctrl_was_created = False
        if not attr in cmds.listAttr(self.all_grp):
            cmds.addAttr(self.all_grp, longName=attr, attributeType="message")
        if not cmds.objExists(item):
            if (item != (self.ar.data.prefix+"Option_Ctrl")):
                item = self.ar.ctrls.create_controller(ctrl_type, item, r=radius, d=degree, dir="+X")
            else:
                item = self.ar.ctrls.create_character_ctrl(ctrl_type, item, r=(radius*0.2))
            cmds.setAttr(item+".rotateOrder", 3)
            cmds.connectAttr(item+".message", self.all_grp+"."+attr, force=True)
            self.ctrl_was_created = True
        return item
    

    def create_all_grp(self):
        if cmds.objExists(self.ar.data.master_name):
            # rename existing All_Grp node without connections as All_Grp_Old
            cmds.rename(self.ar.data.master_name, self.ar.data.master_name+"_Old")
        #Create Master Grp
        self.all_grp = cmds.createNode("transform", name=self.ar.data.prefix+self.ar.data.master_name)
        self.ar.custom_attr.add_attr(0, [self.all_grp]) #dpID
        # adding All_Grp attributes
        cmds.addAttr(self.all_grp, longName=self.ar.data.master_attr, attributeType="bool")
        cmds.addAttr(self.all_grp, longName="dpAutoRigSystem", dataType="string")
        cmds.addAttr(self.all_grp, longName="date", dataType="string")
        # system:
        cmds.addAttr(self.all_grp, longName="maya", dataType="string")
        cmds.addAttr(self.all_grp, longName="system", dataType="string")
        cmds.addAttr(self.all_grp, longName="language", dataType="string")
        cmds.addAttr(self.all_grp, longName="preset", dataType="string")
        # author:
        cmds.addAttr(self.all_grp, longName="author", dataType="string")
        # rig info to be updated:
        cmds.addAttr(self.all_grp, longName="geometryList", dataType="string")
        cmds.addAttr(self.all_grp, longName="controlList", dataType="string")
        cmds.addAttr(self.all_grp, longName="prefix", dataType="string")
        cmds.addAttr(self.all_grp, longName="name", dataType="string")
        # setting All_Grp data
        cmds.setAttr(self.all_grp+"."+self.ar.data.master_attr, True)
        cmds.setAttr(self.all_grp+".dpAutoRigSystem", self.ar.data.github_url, type="string")
        cmds.setAttr(self.all_grp+".date", str(time.asctime(time.localtime(time.time()))), type="string")
        cmds.setAttr(self.all_grp+".maya", cmds.about(version=True), type="string")
        cmds.setAttr(self.all_grp+".system", self.ar.data.version, type="string")
        cmds.setAttr(self.all_grp+".language", self.ar.data.lang["_preset"], type="string")
        cmds.setAttr(self.all_grp+".preset", self.ar.data.curve_preset["_preset"], type="string")
        cmds.setAttr(self.all_grp+".author", getpass.getuser(), type="string")
        cmds.setAttr(self.all_grp+".prefix", self.ar.data.prefix, type="string")
        cmds.setAttr(self.all_grp+".name", self.all_grp, type="string")
        # add date data log:
        cmds.addAttr(self.all_grp, longName="lastModification", dataType="string")
        # add pipeline data:
        cmds.addAttr(self.all_grp, longName="firstGuidesFile", dataType="string")
        cmds.addAttr(self.all_grp, longName="lastGuidesFile", dataType="string")
        cmds.addAttr(self.all_grp, longName="publishedFromFile", dataType="string")
        cmds.addAttr(self.all_grp, longName="assetName", dataType="string")
        cmds.addAttr(self.all_grp, longName="comment", dataType="string")
        cmds.addAttr(self.all_grp, longName="modelVersion", attributeType="long", defaultValue=0, minValue=0)
        # set data
        cmds.setAttr(self.all_grp+".firstGuidesFile", cmds.file(query=True, sceneName=True), type="string")
        cmds.setAttr(self.all_grp+".lastGuidesFile", cmds.file(query=True, sceneName=True), type="string")
        # module counts:
        for class_name in self.ar.data.lib[self.ar.data.standard_folder]["names"]:
            cmds.addAttr(self.all_grp, longName="dp"+class_name+"Count", attributeType="long", defaultValue=0)
        # set outliner color
        self.ar.ctrls.color_shape([self.all_grp], [1, 1, 1], outliner=True) #white


    def update_all_grp_attrs(self):
        cmds.setAttr(self.all_grp+".lastModification", str(time.asctime(time.localtime(time.time()))), type="string")
        # setting pipeline data
        if not cmds.objExists(self.all_grp+".lastGuidesFile"):
            cmds.addAttr(self.all_grp, longName="lastGuidesFile", dataType="string")
        cmds.setAttr(self.all_grp+".lastGuidesFile", cmds.file(query=True, sceneName=True), type="string")


    def set_outliner_color(self):
        self.ar.ctrls.color_shape([self.ctrls_grp], [0, 0.65, 1], outliner=True) #blue
        self.ar.ctrls.color_shape([self.data_grp], [1, 1, 0], outliner=True) #yellow
        self.ar.ctrls.color_shape([self.render_grp], [1, 0.45, 0], outliner=True) #orange


    def set_all_grp_hierarchy(self):
        # Arrange Hierarchy if using an original setup or preserve existing if integrating to another studio setup
        if self.all_grp == self.ar.data.prefix+self.ar.data.master_name:
            cmds.parent(self.ctrls_grp, self.data_grp, self.render_grp, self.proxy_grp, self.fx_grp, self.all_grp)
            cmds.parent(self.support_grp, self.static_grp, self.scalable_grp, self.blendshapes_grp, self.wip_grp, self.data_grp)


    def set_all_grp_attributes(self):
        if not cmds.listConnections(self.fx_grp+".visibility", destination=False, source=True):
            cmds.setAttr(self.fx_grp+".visibility", 0)
        to_lock_hide_attrs = [  self.all_grp,
                                self.support_grp,
                                self.ctrls_grp,
                                self.render_grp,
                                self.data_grp,
                                self.proxy_grp,
                                self.fx_grp,
                                self.static_grp,
                                self.ctrls_vis_grp]
        self.ar.ctrls.set_lock_hide(to_lock_hide_attrs, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])


    def set_parent_root_ctrl_pivot(self):
        self.root_pivot_ctrl_grp = self.ar.utils.create_zero_out([self.root_pivot_ctrl])[0]
        cmds.parent(self.root_pivot_ctrl_grp, self.root_ctrl)
        self.change_root_to_ctrls_vis_constraint()


    def set_ground_shapes(self):
        self.ar.ctrls.create_ground_direction_shape(self.global_ctrl, 2, 15, 1)
        self.ar.ctrls.create_ground_direction_shape(self.master_ctrl, 1, 11, 0)
        self.ar.ctrls.create_ground_direction_shape(self.root_ctrl, 1, 8, 0)


    def set_option_ctrl_rig_scale(self):
        cmds.makeIdentity(self.option_ctrl, apply=True)
        self.option_ctrl_grp = self.ar.utils.create_zero_out([self.option_ctrl], not_transform_io=False)[0]
        cmds.setAttr(self.option_ctrl_grp+".translateX", self.ar.ctrls.dpCheckLinearUnit(10))
        # use Option_Ctrl rigScale and rigScaleMultiplier attribute to Master_Ctrl
        self.rig_scale_md = cmds.createNode("multiplyDivide", name=self.ar.data.prefix+'RigScale_MD')
        self.ar.custom_attr.add_attr(0, [self.rig_scale_md]) #dpID
        cmds.addAttr(self.rig_scale_md, longName="dpRigScale", attributeType="bool", defaultValue=True)
        cmds.addAttr(self.option_ctrl, longName="dpRigScaleNode", attributeType="message")
        cmds.addAttr(self.option_ctrl, longName="rigScaleOutput", attributeType="float", defaultValue=1)
        cmds.connectAttr(self.rig_scale_md+".message", self.option_ctrl+".dpRigScaleNode", force=True)
        cmds.connectAttr(self.option_ctrl+".rigScale", self.rig_scale_md+".input1X", force=True)
        cmds.connectAttr(self.option_ctrl+".rigScaleMultiplier", self.rig_scale_md+".input2X", force=True)
        cmds.connectAttr(self.rig_scale_md+".outputX", self.option_ctrl+".rigScaleOutput", force=True)
        cmds.connectAttr(self.rig_scale_md+".outputX", self.master_ctrl+".scaleX", force=True)
        cmds.connectAttr(self.rig_scale_md+".outputX", self.master_ctrl+".scaleY", force=True)
        cmds.connectAttr(self.rig_scale_md+".outputX", self.master_ctrl+".scaleZ", force=True)
        self.ar.ctrls.set_lock_hide([self.master_ctrl], ['sx', 'sy', 'sz'])
        self.ar.ctrls.set_lock_hide([self.option_ctrl], ['rigScaleOutput'])
        self.ar.ctrls.set_non_keyable([self.option_ctrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        self.ar.ctrls.set_string_attr_from_items(self.option_ctrl, ['rigScaleMultiplier'])


    def mount_ground_ctrls_hierarchy(self):
        cmds.parent(self.root_ctrl, self.master_ctrl)
        cmds.parent(self.master_ctrl, self.global_ctrl)
        cmds.parent(self.global_ctrl, self.ctrls_grp)
        cmds.parent(self.option_ctrl_grp, self.root_ctrl)
        cmds.parent(self.ctrls_vis_grp, self.root_ctrl)


    def set_ground_ctrls_parent_tag(self):
        if "parentTag" in cmds.listAttr(self.global_ctrl):
            cmds.connectAttr(self.global_ctrl+".message", self.master_ctrl+".parentTag", force=True)
            cmds.connectAttr(self.master_ctrl+".message", self.root_ctrl+".parentTag", force=True)
            cmds.connectAttr(self.root_ctrl+".message", self.option_ctrl+".parentTag", force=True)
            cmds.connectAttr(self.root_ctrl+".message", self.root_pivot_ctrl+".parentTag", force=True)


    def set_ground_ctrls_lock_hide_attr(self):
        self.ar.ctrls.set_lock_hide([self.scalable_grp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])
        self.ar.ctrls.set_lock_hide([self.root_ctrl, self.global_ctrl], ['sx', 'sy', 'sz', 'v'])
        self.ar.ctrls.set_lock_hide([self.root_pivot_ctrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])


    def set_root_pivot_attr(self):
        for axis in self.ar.data.axes:
            cmds.connectAttr(self.root_pivot_ctrl+".translate"+axis, self.root_ctrl+".rotatePivot"+axis, force=True)
            cmds.connectAttr(self.root_pivot_ctrl+".translate"+axis, self.root_ctrl+".scalePivot"+axis, force=True)


    def set_base_joint(self):
        cmds.select(clear=True)
        self.base_root_jnt = self.ar.data.prefix+"BaseRoot_Jnt"
        self.base_root_jnt_grp = self.ar.data.prefix+"BaseRoot_Joint_Grp"
        if not cmds.objExists(self.base_root_jnt):
            self.base_root_jnt = cmds.createNode("joint", name=self.ar.data.prefix+"BaseRoot_Jnt")
            if not cmds.objExists(self.base_root_jnt_grp):
                self.base_root_jnt_grp = cmds.createNode("transform", name=self.ar.data.prefix+"BaseRoot_Joint_Grp")
            cmds.parent(self.base_root_jnt, self.base_root_jnt_grp)
            cmds.parent(self.base_root_jnt_grp, self.scalable_grp)
            cmds.parentConstraint(self.root_ctrl, self.base_root_jnt_grp, maintainOffset=True, name=self.base_root_jnt_grp+"_PaC")
            cmds.scaleConstraint(self.root_ctrl, self.base_root_jnt_grp, maintainOffset=True, name=self.base_root_jnt_grp+"_ScC")
            self.ar.custom_attr.add_attr(0, [self.base_root_jnt_grp], descendents=True) #dpID
            cmds.setAttr(self.base_root_jnt_grp+".visibility", 0)
            self.ar.ctrls.set_lock_hide([self.base_root_jnt, self.base_root_jnt_grp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])


    def create_base_rig_node(self):
        base_was_created = False
        self.all_grp = self.ar.utils.get_all_grp()
        if not self.all_grp:
            base_was_created = True
            self.create_all_grp()
        self.update_all_grp_attrs()

        # Get or create all the needed groups
        self.support_grp = self.get_base_group("supportGrp", self.ar.data.prefix+"Support_Grp", ["modelsGrp", self.ar.data.prefix+"Model_Grp"]) #just to make compatibility with old rigs
        self.ctrls_grp = self.get_base_group("ctrlsGrp", self.ar.data.prefix+"Ctrls_Grp")
        self.ctrls_vis_grp = self.get_base_group("ctrlsVisibilityGrp", self.ar.data.prefix+"Ctrls_Visibility_Grp")
        self.data_grp = self.get_base_group("dataGrp", self.ar.data.prefix+"Data_Grp")
        self.render_grp = self.get_base_group("renderGrp", self.ar.data.prefix+"Render_Grp")
        self.proxy_grp = self.get_base_group("proxyGrp", self.ar.data.prefix+"Proxy_Grp")
        self.fx_grp = self.get_base_group("fxGrp", self.ar.data.prefix+"FX_Grp")
        self.static_grp = self.get_base_group("staticGrp", self.ar.data.prefix+"Static_Grp")
        self.scalable_grp = self.get_base_group("scalableGrp", self.ar.data.prefix+"Scalable_Grp")
        self.blendshapes_grp = self.get_base_group("blendShapesGrp", self.ar.data.prefix+"BlendShapes_Grp")
        self.wip_grp = self.get_base_group("wipGrp", self.ar.data.prefix+"WIP_Grp")
        
        if base_was_created:
            self.set_outliner_color()
            self.set_all_grp_hierarchy()
        self.set_all_grp_attributes()

        # Controllers Setup
        self.master_ctrl = self.get_base_controller("id_004_Master", "masterCtrl", self.ar.data.prefix+"Master_Ctrl", self.ar.ctrls.dpCheckLinearUnit(10), degree=3)
        self.global_ctrl = self.get_base_controller("id_003_Global", "globalCtrl", self.ar.data.prefix+"Global_Ctrl", self.ar.ctrls.dpCheckLinearUnit(13))
        self.root_ctrl = self.get_base_controller("id_005_Root", "rootCtrl", self.ar.data.prefix+"Root_Ctrl", self.ar.ctrls.dpCheckLinearUnit(8))
        self.root_pivot_ctrl = self.get_base_controller("id_099_RootPivot", "rootPivotCtrl", self.ar.data.prefix+"Root_Pivot_Ctrl", self.ar.ctrls.dpCheckLinearUnit(1), degree=3)
        need_connect_root_pivot_attr = False
        if self.ctrl_was_created:
            need_connect_root_pivot_attr = True
            self.set_parent_root_ctrl_pivot()
            self.set_ground_shapes()
        self.option_ctrl = self.get_base_controller("id_006_Option", "optionCtrl", self.ar.data.prefix+"Option_Ctrl", self.ar.ctrls.dpCheckLinearUnit(16))
        if self.ctrl_was_created:
            self.set_option_ctrl_rig_scale()
            self.mount_ground_ctrls_hierarchy()
        else:
            self.rig_scale_md = self.ar.data.prefix+'RigScale_MD'
        if base_was_created:
            self.set_ground_ctrls_parent_tag()
            self.set_ground_ctrls_lock_hide_attr()
            if need_connect_root_pivot_attr:
                self.set_root_pivot_attr()
            cmds.setAttr(self.master_ctrl+".visibility", keyable=False)
            self.set_base_joint()
    

    def change_root_to_ctrls_vis_constraint(self, *args):
        """ Just recreate the Root_Ctrl output connections to a constraint, now using the ctrlsVisibilityGrp as source node instead.
            It keeps the dpAR compatibility to old rigs.
        """
        change_attrs = ["rotateOrder", "translate", "rotate", "scale", "parentMatrix[0]", "rotatePivot", "rotatePivotTranslate"]
        for attr in change_attrs:
            pacs = cmds.listConnections(self.root_ctrl+"."+attr, destination=True, source=False, plugs=True)
            if pacs:
                for pac in pacs:
                    cmds.connectAttr(self.ctrls_vis_grp+"."+attr, pac, force=True)


    def reorder_option_attributes(self, items, attrs, verbose=True, *args):
        """ Reorder Attributes of a given objectList following the desiredAttribute list.
            Useful for organize the Option_Ctrl attributes, for example.
        """
        if items and attrs:
            for item in items:
                reorder_attr = self.ar.config.get_instance("ReorderAttr", [self.ar.data.tools_folder])
                if reorder_attr:
                    if verbose and not self.ar.data.rebuilding:
                        self.ar.ui_manager.set_progress('Reordering: '+self.ar.data.lang['c110_start'], 'Reordering Attributes', len(attrs), add_one=False, add_number=False)
                    delta = 0
                    for i, attr in enumerate(attrs):
                        if verbose:
                            self.ar.ui_manager.set_progress('Reordering Attributes: '+item)
                        # get current user defined attributes:
                        current_attrs = cmds.listAttr(item, userDefined=True)
                        if attr in current_attrs:
                            for n in range(1, current_attrs.index(attr)+1-i+delta):
                                reorder_attr.move_attr(1, [item], [attr])
                        else:
                            delta += 1
                    if verbose and not self.ar.data.rebuilding:
                        self.ar.ui_manager.set_progress(end_it=True)
                    self.ar.ui_manager.close_ui('dpReorderAttrWindow')
    

    def before_start_rig_all(self):
        if not self.ar.data.rebuilding:
            print('\ndpAutoRigSystem Log: ' + self.ar.data.lang['i178_startRigging'] + '...\n')
        # Starting progress window
        self.ar.ui_manager.set_progress(self.ar.data.lang['i178_startRigging'], 'dpAutoRigSystem', add_one=False, add_number=False)
        self.ar.ui_manager.close_ui(self.ar.data.plus_info_win_name)
        self.ar.ui_manager.close_ui(self.ar.data.color_override_win_name)


    def refresh_before_build(self):
        # force refresh in order to avoid calculus error if creating Rig at the same time of guides:
        cmds.refresh()
        if not self.ar.data.rebuilding:
            self.ar.ui_manager.refresh_ui()


    def check_good_guide_version(self, guides_to_rig):
        # check guide versions to be sure we are building with the same dpAutoRigSystem version:
        for item in guides_to_rig:
            guide_version = cmds.getAttr(f"{item.guide_base}.dpARVersion")
            if not guide_version == self.ar.data.version:
                yes_text = self.ar.data.lang['i071_yes']
                update_guides_text = self.ar.data.lang['m186_updateGuides']
                not_text = self.ar.data.lang['i072_no']
                user_choose = cmds.confirmDialog(title=f"dpAutoRigSystem - v{self.ar.data.version}", message=self.ar.data.lang['i127_guideVersionDif'], button=[yes_text, update_guides_text, not_text], defaultButton=yes_text, cancelButton=not_text, dismissString=not_text)
                if user_choose == not_text:
                    return False
                elif user_choose == update_guides_text:
                    self.ar.config.get_instance("UpdateGuides", [self.ar.data.tools_folder]).build_tool()
                    return False
        return True


    def colorize_curves(self):
        # colorize all controller in yellow as a base if not find the pattern
        if self.ar.data.colorize_curve:
            ground_ctrls = [self.global_ctrl, self.root_ctrl, self.option_ctrl]
            left_pattern = re.compile(f"{self.ar.data.lang['p002_left']}_.*._Ctrl")
            right_pattern = re.compile(f"{self.ar.data.lang['p003_right']}_.*._Ctrl")
            for ctrl in self.ar.ctrls.get_controllers():
                shapes = cmds.listRelatives(ctrl, children=True, allDescendents=True, fullPath=True, type="shape")
                if shapes:
                    if not cmds.getAttr(shapes[0]+".overrideEnabled"):
                        if (left_pattern.match(ctrl)):
                            self.ar.ctrls.color_shape([ctrl], "red")
                        elif (right_pattern.match(ctrl)):
                            self.ar.ctrls.color_shape([ctrl], "blue")
                        elif (ctrl in ground_ctrls):
                            self.ar.ctrls.color_shape([ctrl], "black")
                        else:
                            self.ar.ctrls.color_shape([ctrl], "yellow")


    def get_mirror_names(self, item):
        mirror_names = [""]
        if self.hook[item.guide_base]['guideMirrorAxis'] != "off":
            mirror_names = self.hook[item.guide_base]['guideMirrorName']
        return mirror_names


    def organize_hierarchy(self):
        # verify if it's necessary organize the hierarchies for each module:
        for item in self.guides_to_rig:
            for s, side in enumerate(self.get_mirror_names(item)):
                # get hook groups info:
                self.static_hook_grp = cmds.listConnections(f"{item.guide_net}.{side}StaticHookGrp", destination=False, source=True)[0]
                self.scalable_hook_grp = cmds.listConnections(f"{item.guide_net}.{side}ScalableHookGrp", destination=False, source=True)[0]
                self.ctrl_hook_grp = cmds.listConnections(f"{item.guide_net}.{side}ControlHookGrp", destination=False, source=True)[0]
                # get father info:
                if self.hook[item.guide_base]['fatherGuide']:
                    # working with father mirror:
                    father_mirror_names = [""]
                    # get fatherName:
                    if self.hook[item.guide_base]['fatherMirrorAxis'] != "off":
                        father_mirror_names = self.hook[item.guide_base]['fatherMirrorName']
                    for f, side_father in enumerate(father_mirror_names):
                        father_name = f"{side_father}{self.ar.data.prefix}{self.hook[item.guide_base]['fatherInstance']}"
                        if self.hook[item.guide_base]['fatherCustomName']:
                            father_name = f"{side_father}{self.ar.data.prefix}{self.hook[item.guide_base]['fatherCustomName']}"
                        # get final rigged parent node from origined_from_data:
                        father_rigged_parent_node = self.origined_from_data[father_name+"_Guide_"+self.hook[item.guide_base]['fatherGuideLoc']]
                        if father_rigged_parent_node:
                            if len(father_mirror_names) != 1: # tell us 'the father has mirror'
                                if s == f:
                                    # parent them to the correct side of the father's mirror:
                                    if self.ctrl_hook_grp:
                                        cmds.parent(self.ctrl_hook_grp, father_rigged_parent_node)
                            else:
                                # parent them to the unique father:
                                if self.ctrl_hook_grp:
                                    cmds.parent(self.ctrl_hook_grp, father_rigged_parent_node)
                elif self.hook[item.guide_base]['parentNode']:
                    # parent module control to just a node in the scene:
                    cmds.parent(self.ctrl_hook_grp, self.hook[item.guide_base]['parentNode'])
                else:
                    # parent module control to default all_grp:
                    cmds.parent(self.ctrl_hook_grp, self.ctrls_vis_grp)
                # put static and scalable groups in dataGrp:
                cmds.parent(self.static_hook_grp, self.static_grp)
                cmds.parent(self.scalable_hook_grp, self.scalable_grp)
                # finish hookGrps:
                cmds.setAttr(f"{self.static_hook_grp}.staticHook", 0)
                cmds.setAttr(f"{self.scalable_hook_grp}.scalableHook", 0)
                cmds.setAttr(f"{self.ctrl_hook_grp}.ctrlHook", 0)
                cmds.lockNode(item.guide_net, lock=False)
                cmds.deleteAttr(f"{item.guide_net}.{side}StaticHookGrp")
                cmds.deleteAttr(f"{item.guide_net}.{side}ScalableHookGrp")
                cmds.deleteAttr(f"{item.guide_net}.{side}ControlHookGrp")
                cmds.lockNode(item.guide_net, lock=True)


    def set_option_ctrl_corrective(self, item):
        # display corrective controls by an Option_Ctrl attribute:
        if "correctiveCtrlGrpList" in item.composed.keys():
            if not f"{self.ar.data.lang['c124_corrective']}Ctrls" in cmds.listAttr(self.option_ctrl):
                cmds.addAttr(self.option_ctrl, longName=f"{self.ar.data.lang['c124_corrective']}Ctrls", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                cmds.setAttr(f"{self.option_ctrl}.{self.ar.data.lang['c124_corrective']}Ctrls", channelBox=True)
            for corrective_grp in item.composed['correctiveCtrlGrpList']:
                cmds.connectAttr(f"{self.option_ctrl}.{self.ar.data.lang['c124_corrective']}Ctrls", f"{corrective_grp}.visibility", force=True)

    
    def set_rigged_types(self):
        # actualise the number of rigged standard guides by type
        for class_name in self.ar.data.lib[self.ar.data.standard_folder]["names"]:
            cmds.setAttr(f"{self.all_grp}.dp{class_name}Count", len([n for n in self.ar.utils.get_network_by_attr("dpGuideNet") if f"{cmds.getAttr(n+'.moduleType')}" == class_name]))


    def set_parent_tag(self):
        guide_source_data = {}
        holder_ctrls = self.ar.ctrls.get_controllers("dpHolder")
        ctrls = self.ar.ctrls.get_controllers()
        ctrls.extend(holder_ctrls)
        for ctrl in ctrls:
            if "guide_source" in cmds.listAttr(ctrl):
                guide_source_data[cmds.getAttr(ctrl+".guide_source")] = ctrl
        # missing parentTag controllers:
        for p_tag_ctrl in [c for c in self.ar.ctrls.get_controllers("parentTag") if not cmds.listConnections(c+".parentTag", source=True, destination=False)]:
            if not p_tag_ctrl == self.global_ctrl:
                if "controlID" in cmds.listAttr(p_tag_ctrl):
                    if not cmds.getAttr(p_tag_ctrl+".controlID") == "id_092_Correctives":
                        if "guide_source" in cmds.listAttr(p_tag_ctrl):
                            guide_source = cmds.getAttr(p_tag_ctrl+".guide_source")
                            guide_base = guide_source.split(":")[0]+":Guide_Base"
                            parent_node = self.hook[guide_base]['parentNode']
                            father_guide = self.hook[guide_base]['fatherGuide']
                            if parent_node:
                                if not parent_node in guide_source_data.keys():
                                    parent_node = self.ar.utils.replace_item_suffix(parent_node, guide_source_data)
                                if not parent_node in guide_source_data.keys():
                                    continue
                                found_ctrl = guide_source_data[parent_node]
                                if found_ctrl in holder_ctrls: #holder
                                    guide_source = cmds.getAttr(found_ctrl+".guide_source")
                                    guide_base = guide_source.split(":")[0]+":Guide_Base"
                                    parent_node = self.hook[guide_base]['parentNode']
                                    father_guide = self.hook[guide_base]['fatherGuide']
                                    parent_node = self.ar.utils.replace_item_suffix(parent_node, guide_source_data)
                                    if not parent_node in guide_source_data.keys():
                                        continue
                                    found_ctrl = guide_source_data[parent_node]
                                if not self.hook[father_guide]['guideMirrorAxis'] == "off": #father guide has mirror
                                    mirror_names = self.hook[father_guide]['guideMirrorName']
                                    if p_tag_ctrl.startswith(mirror_names[0]):
                                        if not found_ctrl.startswith(mirror_names[0]):
                                            found_ctrl = mirror_names[0]+found_ctrl[2:]
                                    else:
                                        if not found_ctrl.startswith(mirror_names[1]):
                                            found_ctrl = mirror_names[1]+found_ctrl[2:]
                                if cmds.objExists(found_ctrl):
                                    cmds.connectAttr(found_ctrl+".message", p_tag_ctrl+".parentTag", force=True)
                            else:
                                cmds.connectAttr(self.root_ctrl+".message", p_tag_ctrl+".parentTag", force=True)


    def set_option_ctrl_attrs(self):
        # Add usefull attributes for the animators
        if self.ar.data.supplementary_attr:
            # defining attribute name strings:
            general_attr = self.ar.data.lang['c066_general']
            volume_variation_attr = self.ar.data.lang['c031_volumeVariation']
            spine_attr = self.ar.data.lang['m011_spine'].lower()
            limb_attr = self.ar.data.lang['m019_limb'].lower()
            arm_attr = self.ar.data.lang['m028_arm']
            leg_attr = self.ar.data.lang['m030_leg']
            front_attr = self.ar.data.lang['c056_front']
            back_attr = self.ar.data.lang['c057_back']
            left_attr = self.ar.data.lang['p002_left'].lower()
            right_attr = self.ar.data.lang['p003_right'].lower()
            tweaks_attr = self.ar.data.lang['m081_tweaks'].lower()
            facial_attr = self.ar.data.lang['c059_facial'].lower()
            
            option_ctrl_attrs = cmds.listAttr(self.option_ctrl)

            if not general_attr in option_ctrl_attrs:
                cmds.addAttr(self.option_ctrl, longName=general_attr, attributeType="enum", enumName="----------", keyable=True)
                cmds.setAttr(self.option_ctrl+"."+general_attr, lock=True)
            
            # Only create if a VolumeVariation attribute is found
            if not volume_variation_attr in option_ctrl_attrs:
                if cmds.listAttr(self.option_ctrl, string="*"+volume_variation_attr+"*"):
                    cmds.addAttr(self.option_ctrl, longName=volume_variation_attr, attributeType="enum", enumName="----------", keyable=True)
                    cmds.setAttr(self.option_ctrl+"."+volume_variation_attr, lock=True)
            
            # Only create if an IkFk attribute is found
            if not 'ikFkBlend' in option_ctrl_attrs:
                if cmds.listAttr(self.option_ctrl, string="*ikFk*"):
                    cmds.addAttr(self.option_ctrl, longName="ikFkBlend", attributeType="enum", enumName="----------", keyable=True)
                    cmds.setAttr(self.option_ctrl+".ikFkBlend", lock=True)
            
            if 'ikFkSnap' in option_ctrl_attrs:
                cmds.setAttr(self.option_ctrl+".ikFkSnap", keyable=False, channelBox=True)
            
            if not 'display' in option_ctrl_attrs:
                cmds.addAttr(self.option_ctrl, longName="display", attributeType="enum", enumName="----------", keyable=True)
                cmds.setAttr(self.option_ctrl+".display", lock=True)
            
            if not 'mesh' in option_ctrl_attrs:
                cmds.addAttr(self.option_ctrl, longName="mesh", min=0, max=1, defaultValue=1, attributeType="long", keyable=True)
                cmds.connectAttr(self.option_ctrl+".mesh", self.render_grp+".visibility", force=True)
            
            if not 'proxy' in option_ctrl_attrs:
                cmds.addAttr(self.option_ctrl, longName="proxy", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                cmds.connectAttr(self.option_ctrl+".proxy", self.proxy_grp+".visibility", force=True)
            
            if not 'controllers' in option_ctrl_attrs:
                cmds.addAttr(self.option_ctrl, longName="controllers", min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                cmds.connectAttr(self.option_ctrl+".controllers", self.ctrls_vis_grp+".visibility", force=True)
                cmds.setAttr(self.option_ctrl+".controllers", channelBox=True)

            if not 'rootPivot' in option_ctrl_attrs:
                cmds.addAttr(self.option_ctrl, longName="rootPivot", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                cmds.connectAttr(self.option_ctrl+".rootPivot", self.root_pivot_ctrl_grp+".visibility", force=True)
                cmds.setAttr(self.option_ctrl+".rootPivot", channelBox=True)

            # try to organize Option_Ctrl attributes:
            # get current user defined attributes:
            current_attrs = cmds.listAttr(self.option_ctrl, userDefined=True)
            # clean up "_ikFkBlend" atributes:
            if current_attrs:
                for current_attr in current_attrs:
                    if current_attr.endswith("_ikFkBlend"):
                        if not current_attr[:current_attr.find("_ikFkBlend")] in option_ctrl_attrs:
                            cmds.renameAttr(self.option_ctrl+"."+current_attr, current_attr[:current_attr.find("_ikFkBlend")])
            # clean up "VolumeVariation" attributes:
            if current_attrs:
                for current_attr in current_attrs:
                    if current_attr.endswith("_"+volume_variation_attr):
                        if not current_attr[:current_attr.find("_"+volume_variation_attr)] in option_ctrl_attrs:
                            cmds.renameAttr(self.option_ctrl+"."+current_attr, current_attr[:current_attr.find("_"+volume_variation_attr)])
                        
            # list desirable Option_Ctrl attributes order:
            desired_order_attrs = [general_attr, 'globalStretch', 'rigScale', 'rigScaleMultiplier', volume_variation_attr,
            spine_attr+'Active', spine_attr, spine_attr+'001Active', spine_attr+'001', spine_attr+'002Active', spine_attr+'002',
            limb_attr, limb_attr+'Min', limb_attr+'Manual', 'ikFkBlend', 'ikFkSnap', spine_attr+'Fk', spine_attr+'Fk1', spine_attr+'Fk2', spine_attr+'001Fk', spine_attr+'002Fk', 
            left_attr+spine_attr+'Fk', right_attr+spine_attr+'Fk', left_attr+spine_attr+'Fk1', right_attr+spine_attr+'Fk1', left_attr+spine_attr+'Fk2', right_attr+spine_attr+'Fk2',
            arm_attr+"Fk", leg_attr+"Fk", left_attr+arm_attr+"Fk", right_attr+arm_attr+"Fk", arm_attr.lower()+"Fk", leg_attr.lower()+"Fk", left_attr+arm_attr.lower()+"Fk", right_attr+arm_attr.lower()+"Fk",
            left_attr+leg_attr+"Fk", right_attr+leg_attr+"Fk", left_attr+leg_attr+front_attr+"Fk", right_attr+leg_attr+front_attr+"Fk", left_attr+leg_attr+back_attr+"Fk", right_attr+leg_attr+back_attr+"Fk",
            arm_attr+'Fk1', leg_attr+'Fk1', left_attr+arm_attr+'Fk1', right_attr+arm_attr+'Fk1', left_attr+leg_attr+'Fk1', right_attr+leg_attr+'Fk1',
            left_attr+leg_attr+front_attr+'Fk1', right_attr+leg_attr+front_attr+'Fk1', left_attr+leg_attr+back_attr+'Fk1', right_attr+leg_attr+back_attr+'Fk1',
            'tailFk', 'tailDyn', 'tail1Fk', 'tail1Dyn', 'tailFk1', 'tailDyn1', left_attr+'TailFk', left_attr+'TailFk1', right_attr+'TailFk', right_attr+'TailFk1', left_attr+'TailDyn', left_attr+'TailDyn1', right_attr+'TailDyn', right_attr+'TailDyn1',
            'hairFk', 'hairDyn', 'hair1Fk', 'hair1Dyn', 'hairFk1', 'hairDyn1', left_attr+'HairFk', left_attr+'HairFk1', right_attr+'HairFk', right_attr+'HairFk1', left_attr+'HairDyn', left_attr+'HairDyn1', right_attr+'HairDyn', right_attr+'HairDyn1',
            'dpAR_000Fk', 'dpAR_000Dyn', 'dpAR_001Fk', 'dpAR_001Dyn', 'dpAR_002Fk', 'dpAR_002Dyn', 
            'dpAR_000Fk1', 'dpAR_000Dyn1', left_attr+'dpAR_000Fk', left_attr+'dpAR_000Fk1', right_attr+'dpAR_000Fk', right_attr+'dpAR_000Fk1', left_attr+'dpAR_000Dyn', left_attr+'dpAR_000Dyn1', right_attr+'dpAR_000Dyn', right_attr+'dpAR_000Dyn1',
            'dpAR_001Fk1', 'dpAR_001Dyn1', left_attr+'dpAR_001Fk', left_attr+'dpAR_001Fk1', right_attr+'dpAR_001Fk', right_attr+'dpAR_001Fk1', left_attr+'dpAR_001Dyn', left_attr+'dpAR_001Dyn1', right_attr+'dpAR_001Dyn', right_attr+'dpAR_001Dyn1',
            'display', 'mesh', 'proxy', 'controllers', 'bends', 'extraBends', facial_attr, tweaks_attr, 'correctiveCtrls']
            # call method to reorder Option_Ctrl attributes:
            self.reorder_option_attributes([self.option_ctrl], desired_order_attrs)


    #maker
    def rig_all(self, *args):
        """ Create the RIG based in the Guide Modules in the scene.
            Most important function to automate the generating process.
        """
        detected_bug = False
        self.hook = self.ar.utils.get_hook()
        self.before_start_rig_all()
        self.refresh_before_build()
        self.guides_to_rig = self.ar.utils.get_guides_to_rig()
        if self.guides_to_rig:
            self.ar.ui_manager.set_progress(max=len(self.guides_to_rig), add_one=False, add_number=False)
            if not self.check_good_guide_version(self.guides_to_rig):
                return
            if self.ar.data.compose_all:
                self.create_base_rig_node()
            self.ar.utils.clear_guide_mirror_grp()
            for item in self.guides_to_rig:
                item.check_father_mirror()
                item.serialize_guide()
            for item in self.guides_to_rig: #it needs another loop to serialize guides parenting before rig them
                if item.custom_name:
                    self.ar.ui_manager.set_progress('Rigging: '+str(item.custom_name))
                else:
                    self.ar.ui_manager.set_progress('Rigging: '+str(item.guide_namespace))
                # TODO detected bug returning rig_me
                item.rig_me() #rig it :)
            # integrating modules together:
            if self.ar.data.compose_all:
                self.ar.ui_manager.set_progress('Rigging: '+self.ar.data.lang['i010_composeCB'])
                self.colorize_curves()
                self.origined_from_data = self.ar.utils.get_origined_from_data()
                self.organize_hierarchy()
                for item in self.guides_to_rig:
                    father = self.ar.config.get_father_instance(self.hook[item.guide_base]['fatherGuide'])
                    self.set_option_ctrl_corrective(item)
                    self.ar.composer.comp_rigged(item, father)
                self.set_rigged_types()
                self.set_parent_tag()
            self.set_option_ctrl_attrs()
            self.ar.config.get_instance("LimbSpaceSwitch", [self.ar.data.tools_folder]).build_tool()
            self.ar.config.get_instance("FingerHandPose", [self.ar.data.tools_folder]).build_tool()
            # show dialogBox if detected a bug:
            if detected_bug:
                print(f"\n\n{self.ar.data.lang['b000_bugGeneral']}")
                cmds.confirmDialog(title=self.ar.data.lang['i078_detectedBug'], message=self.ar.data.lang['b000_bugGeneral'], button=["OK"])
        self.ar.utils.clear_guide_mirror_grp()
        self.ar.filler.populate_joints()
        if not self.ar.data.rebuilding:
            self.ar.ui_manager.refresh_ui()
            self.ar.logger.logWin()
            self.ar.ui_manager.set_progress(end_it=True)
        cmds.select(clear=True)



class Composer(object):
    def __init__(self, ar):
        self.ar = ar


    def comp_rigged(self, item, father):
        self.to_ids = []
        if item.name == self.ar.data.foot_name:
            self.foot_limb(item, father)
        elif item.name == self.ar.data.limb_name:
            self.limb_options(item)
            self.limb_spine(item, father)
        elif item.name == self.ar.data.spine_name:
            self.spine_options(item)
        elif item.name == self.ar.data.head_name:
            self.head_options(item)
        elif item.name == self.ar.data.eye_name:
            self.eye_head(item, father)
            self.eye_color(item)
        elif item.name == self.ar.data.finger_name:
            self.finger_scalable(item)
            self.finger_limb(item, father)
        elif item.name == self.ar.data.single_name:
            self.single_single(item, father)
        elif item.name == self.ar.data.wheel_name:
            self.wheel_options(item)
            self.wheel_steering(item, father)
        elif item.name == self.ar.data.suspension_name:
            self.suspension_wheel(item, father)
        elif item.name == self.ar.data.nose_name:
            self.nose_options(item)
            self.nose_head(item, father)
        elif item.name == self.ar.data.chain_name:
            self.chain_options(item)
        if self.to_ids:
            self.ar.custom_attr.add_attr(0, list(set(self.to_ids)), descendents=True)


    def foot_limb(self, foot, limb):
        # footGuide parented in the extremGuide of the limbModule:
        if limb:
            if self.ar.maker.hook[foot.guide_base]['fatherModule'] == self.ar.data.limb_name and self.ar.maker.hook[foot.guide_base]['fatherGuideLoc'] == 'Extrem':
                for s, side in enumerate(self.ar.maker.get_mirror_names(foot)):
                    # getting foot data:
                    reverse_foot_ctrl = foot.composed['revFootCtrlList'][s]
                    reverse_foot_ctrl_grp = foot.composed['revFootCtrlGrpList'][s]
                    reverse_foot_ctrl_shape = foot.composed['revFootCtrlShapeList'][s]
                    to_limb_ik_handle_grp = foot.composed['toLimbIkHandleGrpList'][s]
                    parent_const = foot.composed['parentConstList'][s]
                    scale_const = foot.composed['scaleConstList'][s]
                    foot_jnt = foot.composed['footJntList'][s]
                    ball_reverse_feet = foot.composed['ballRFList'][s]
                    # getting limb data:
                    ik_ctrl = limb.composed['ikCtrlList'][s]
                    ik_handle_grp = limb.composed['ikHandleGrpList'][s]
                    ik_handle_consts = limb.composed['ikHandleConstList'][s]
                    ik_handle_grp_consts = limb.composed['ikHandleGrpConstList'][s]
                    ik_fk_blend_grp_to_reverse_foot = limb.composed['ikFkBlendGrpToRevFootList'][s]
                    latest_joint = limb.composed['extremJntList'][s]
                    ik_stretch_latest_loc = limb.composed['ikStretchExtremLoc'][s]
                    limb_type_name = limb.composed['limbTypeName']
                    world_ref = limb.composed['worldRefList'][s]
                    add_articulation = limb.composed['addArticJoint']
                    add_corrective = limb.composed['addCorrective']
                    ankle_articulations = limb.composed['ankleArticList'][s]
                    ankle_correctives = limb.composed['ankleCorrectiveList'][s]
                    # do task actions in order to compose the limb and foot:
                    cmds.cycleCheck(evaluation=False)
                    cmds.delete(ik_handle_consts, ik_handle_grp_consts, parent_const, scale_const) #there's an undesirable cycleCheck evaluation error here when we delete ik_handle_consts!
                    cmds.cycleCheck(evaluation=True)
                    cmds.parent(reverse_foot_ctrl_grp, ik_fk_blend_grp_to_reverse_foot, absolute=True)
                    cmds.parent(ik_handle_grp, to_limb_ik_handle_grp, absolute=True)
                    self.to_ids.extend(cmds.parentConstraint(latest_joint, foot_jnt, maintainOffset=True, name=foot_jnt+"_PaC"))
                    if limb_type_name == self.ar.data.leg_name:
                        cmds.connectAttr(latest_joint+".scaleX", foot_jnt+".scaleX", force=True)
                        cmds.connectAttr(latest_joint+".scaleY", foot_jnt+".scaleY", force=True)
                        cmds.connectAttr(latest_joint+".scaleZ", foot_jnt+".scaleZ", force=True)
                        if ik_stretch_latest_loc: # avoid issue parenting if quadruped
                            cmds.parent(ik_stretch_latest_loc, ball_reverse_feet, absolute=True)
                        if cmds.objExists(latest_joint+".dpAR_joint"):
                            cmds.deleteAttr(latest_joint+".dpAR_joint")
                        # reconnect correctly the interation for ankle and correctives
                        if add_articulation:
                            cmds.delete(ankle_articulations[1])
                            # workaround to avoid orientConstraint offset issue
                            foot_joint_father = cmds.listRelatives(foot_jnt, parent=True)[0]
                            cmds.delete(cmds.listRelatives(foot_jnt, children=True, type="parentConstraint")[0])
                            foot_joint_children = cmds.listRelatives(foot_jnt, children=True)
                            cmds.parent(foot_joint_children, world=True)
                            cmds.parent(foot_jnt, latest_joint, relative=True)
                            cmds.makeIdentity(foot_jnt, apply=True, translate=True, rotate=True, jointOrient=True, scale=False)
                            cmds.parent(foot_jnt, foot_joint_father)
                            cmds.parent(foot_joint_children, foot_jnt)
                            self.to_ids.extend(cmds.parentConstraint(latest_joint, foot_jnt, maintainOffset=True, name=foot_jnt+"_PaC"))
                        # extracting angle to avoid orientConstraint issue when uniform scaling
                        extract_angle_mm  = cmds.createNode("multMatrix", name=ankle_articulations[0]+"_ExtractAngle_MM")
                        extract_angle_dm  = cmds.createNode("decomposeMatrix", name=ankle_articulations[0]+"_ExtractAngle_DM")
                        extract_angle_qte = cmds.createNode("quatToEuler", name=ankle_articulations[0]+"_ExtractAngle_QtE")
                        extract_angle_md  = cmds.createNode("multiplyDivide", name=ankle_articulations[0]+"_ExtractAngle_MD")
                        orig_loc = cmds.spaceLocator(name=ankle_articulations[0]+"_ExtractAngle_Orig_Loc")[0]
                        action_loc = cmds.spaceLocator(name=ankle_articulations[0]+"_ExtractAngle_Action_Loc")[0]
                        cmds.matchTransform(orig_loc, action_loc, ankle_articulations[2], position=True, rotation=True)
                        cmds.parent(orig_loc, ankle_articulations[2])
                        cmds.parent(action_loc, foot_jnt)
                        cmds.setAttr(orig_loc+".visibility", 0)
                        cmds.setAttr(action_loc+".visibility", 0)
                        cmds.connectAttr(action_loc+".worldMatrix[0]", extract_angle_mm+".matrixIn[0]", force=True)
                        cmds.connectAttr(orig_loc+".worldInverseMatrix[0]", extract_angle_mm+".matrixIn[1]", force=True)
                        cmds.connectAttr(extract_angle_mm+".matrixSum", extract_angle_dm+".inputMatrix", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatX", extract_angle_qte+".inputQuatX", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatY", extract_angle_qte+".inputQuatY", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatZ", extract_angle_qte+".inputQuatZ", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatW", extract_angle_qte+".inputQuatW", force=True)
                        for axis in self.ar.data.axes:
                            cmds.setAttr(extract_angle_md+".input2"+axis, 0.5)
                            cmds.connectAttr(extract_angle_qte+".outputRotate"+axis, ankle_articulations[0]+".rotate"+axis, force=True)
                        self.to_ids.extend([extract_angle_mm, extract_angle_dm, extract_angle_qte, orig_loc, action_loc])
                        if add_corrective:
                            for net in ankle_correctives:
                                if net:
                                    if cmds.objExists(net):
                                        action_locators = cmds.listConnections(net+".actionLoc", destination=False, source=True)
                                        if action_locators:
                                            cmds.connectAttr(foot_jnt+".message", action_locators[0]+".inputNode", force=True)
                                            action_loc_grp = cmds.listRelatives(action_locators[0], parent=True, type="transform")[0]
                                            cmds.delete(action_loc_grp+"_PaC")
                                            self.to_ids.extend(cmds.parentConstraint(foot_jnt, action_loc_grp, maintainOffset=True, name=action_loc_grp+"_PaC"))
                    scalable_grp = foot.composed["scalableGrp"][s]
                    self.to_ids.extend(cmds.scaleConstraint(self.ar.maker.master_ctrl, scalable_grp, name=scalable_grp+"_ScC"))
                    # hide this controller shape
                    cmds.setAttr(reverse_foot_ctrl_shape+".visibility", 0)
                    # add attributes and connect from ik_ctrl to reverse_foot_ctrl:
                    for attr in cmds.listAttr(reverse_foot_ctrl, visible=True, scalar=True, userDefined=True):
                        if not cmds.objExists(ik_ctrl+'.'+attr):
                            current_value = cmds.getAttr(reverse_foot_ctrl+'.'+attr)
                            keyable_status = cmds.getAttr(reverse_foot_ctrl+'.'+attr, keyable=True)
                            channelbox_status = cmds.getAttr(reverse_foot_ctrl+'.'+attr, channelBox=True)
                            attr_min_value = cmds.addAttr(reverse_foot_ctrl+'.'+attr, query=True, minValue=True)
                            attr_max_value = cmds.addAttr(reverse_foot_ctrl+'.'+attr, query=True, maxValue=True)
                            cmds.addAttr(ik_ctrl, longName=attr, attributeType=cmds.getAttr(reverse_foot_ctrl+'.'+attr, type=True), keyable=keyable_status, defaultValue=cmds.addAttr(reverse_foot_ctrl+'.'+attr, query=True, defaultValue=True))
                            if not attr_min_value == None:
                                cmds.addAttr(ik_ctrl+'.'+attr, edit=True, minValue=attr_min_value)
                            if not attr_max_value == None:
                                cmds.addAttr(ik_ctrl+'.'+attr, edit=True, maxValue=attr_max_value)
                            cmds.setAttr(ik_ctrl+'.'+attr, current_value)
                            if not keyable_status:
                                cmds.setAttr(ik_ctrl+'.'+attr, channelBox=channelbox_status)
                            cmds.connectAttr(ik_ctrl+'.'+attr, reverse_foot_ctrl+'.'+attr, force=True)
                            if attr == "visIkFk":
                                if not cmds.objExists(world_ref):
                                    world_ref = world_ref.replace("_Ctrl", "_Grp")
                                if cmds.objExists(world_ref):
                                    for world_ref_attr in cmds.listAttr(world_ref, userDefined=True):
                                        if "Fk_ikFkBlendRevOutputX" in world_ref_attr:
                                            cmds.connectAttr(world_ref+"."+world_ref_attr, ik_ctrl+'.'+attr, force=True)
                    rev_foot_ctrl_old = cmds.rename(reverse_foot_ctrl, reverse_foot_ctrl+"_Old")
                    self.ar.custom_attr.remove_attr("dpControl", [rev_foot_ctrl_old])
                    self.ar.custom_attr.update_id([rev_foot_ctrl_old])


    def limb_options(self, limb):
        # world_ref of extremGuide from limbModule controlled by optionCtrl:
        # getting limb data:
        world_refs = limb.composed['worldRefList']
        world_ref_shapes = limb.composed['worldRefShapeList']
        limb_vv_attr = limb.composed['limbManualVolume']
        master_ctrl_refs = limb.composed['masterCtrlRefList']
        root_ctrl_refs = limb.composed['rootCtrlRefList']
        soft_ik_calibs = limb.composed['softIkCalibrateList']
        for w, world_ref in enumerate(world_refs):
            # do actions in order to make limb be controlled by optionCtrl:
            float_attrs = cmds.listAttr(world_ref, visible=True, scalar=True, keyable=True, userDefined=True)
            for f, float_attr in enumerate(float_attrs):
                if f != len(float_attrs):
                    if not cmds.objExists(self.ar.maker.option_ctrl+'.'+float_attr):
                        current_value = cmds.getAttr(world_ref+'.'+float_attr)
                        if float_attr == limb_vv_attr:
                            cmds.addAttr(self.ar.maker.option_ctrl, longName=float_attr, attributeType=cmds.getAttr(world_ref+"."+float_attr, type=True), defaultValue=current_value, keyable=True)
                            # TODO fix or remove Limb manual volume variation attribute
                            cmds.setAttr(self.ar.maker.option_ctrl+"."+float_attr, channelBox=False, keyable=False)
                        else:
                            cmds.addAttr(self.ar.maker.option_ctrl, longName=float_attr, attributeType=cmds.getAttr(world_ref+"."+float_attr, type=True), minValue=0, maxValue=1, defaultValue=current_value, keyable=True)
                    cmds.connectAttr(self.ar.maker.option_ctrl+'.'+float_attr, world_ref+'.'+float_attr, force=True)
            if not cmds.objExists(self.ar.maker.option_ctrl+'.'+float_attrs[len(float_attrs)-1]):
                cmds.addAttr(self.ar.maker.option_ctrl, longName=float_attrs[len(float_attrs)-1], attributeType=cmds.getAttr(world_ref+"."+float_attr, type=True), defaultValue=1, keyable=True)
                cmds.connectAttr(self.ar.maker.option_ctrl+'.'+float_attrs[len(float_attrs)-1], world_ref+'.'+float_attrs[len(float_attrs)-1], force=True)
            cmds.connectAttr(self.ar.maker.master_ctrl+".scaleX", world_ref+".scaleX", force=True)
            for bend_attr in ["bends", "extraBends"]:
                if cmds.objExists(self.ar.maker.option_ctrl+"."+bend_attr):
                    cmds.setAttr(self.ar.maker.option_ctrl+"."+bend_attr, keyable=False, channelBox=True)
            # connect Option_Ctrl RigScale_MD output to the radiusScale:
            if cmds.objExists(self.ar.maker.rig_scale_md+".dpRigScale") and cmds.getAttr(self.ar.maker.rig_scale_md+".dpRigScale") == True:
                cmds.connectAttr(self.ar.maker.rig_scale_md+".outputX", soft_ik_calibs[w]+".input2X", force=True)

            cmds.delete(world_ref_shapes[w])
            world_ref = cmds.rename(world_ref, world_ref.replace("_Ctrl", "_Grp"))
            self.to_ids.extend(cmds.parentConstraint(self.ar.maker.root_ctrl, world_ref, maintainOffset=True, name=world_ref+"_PaC"))

            # remove dpControl attribute
            self.ar.custom_attr.remove_attr("dpControl", [world_ref])
            self.to_ids.append(world_ref)

            # fix poleVector follow feature integrating with Master_Ctrl and Root_Ctrl:
            self.to_ids.extend(cmds.parentConstraint(self.ar.maker.master_ctrl, master_ctrl_refs[w], maintainOffset=True, name=master_ctrl_refs[w]+"_PaC"))
            self.to_ids.extend(cmds.parentConstraint(self.ar.maker.root_ctrl, root_ctrl_refs[w], maintainOffset=True, name=root_ctrl_refs[w]+"_PaC"))


    def limb_spine(self, limb, spine):
        if spine:
            # parenting correctly the ik_ctrl_zero to spineModule:
            for s, side in enumerate(self.ar.maker.get_mirror_names(limb)):
                scalable_grp = limb.composed["scalableGrp"][s]
                self.to_ids.extend(cmds.scaleConstraint(self.ar.maker.master_ctrl, scalable_grp, name=scalable_grp+"_ScC"))

                if self.ar.maker.hook[limb.guide_base]['fatherModule'] == self.ar.data.spine_name:
                    # getting limb data:
                    limb_type_name = limb.composed['limbTypeName']
                    ik_ctrl_zero = limb.composed['ikCtrlZeroList'][s]
                    ik_polevector_ctrl_zero = limb.composed['ikPoleVectorZeroList'][s]
                    limb_style = limb.composed['limbStyle']
                    ik_handle_grp = limb.composed['ikHandleGrpList'][s]
                    root_ctrl_refs = limb.composed['rootCtrlRefList']
                    # getting spine data:
                    tip_ctrl = spine.composed['tipList'][0]

                    cmds.parent(ik_ctrl_zero, self.ar.maker.ctrls_vis_grp, absolute=True)
                    # verifying what part will be used, the hips or chest:
                    if limb_type_name == self.ar.data.leg_name:
                        # do task actions in order to compose the limb of leg type to rootCtrl:
                        cmds.parent(ik_polevector_ctrl_zero, self.ar.maker.ctrls_vis_grp, absolute=True)
                    else:
                        # do task actions in order to compose the limb and spine (ik_ctrl):
                        self.to_ids.extend(cmds.parentConstraint(tip_ctrl, ik_handle_grp, mo=1, name=ik_handle_grp+"_PaC"))
                        # poleVector autoOrient for arm
                        cmds.delete(root_ctrl_refs[s]+"_PaC")
                        self.to_ids.extend(cmds.parentConstraint(tip_ctrl, root_ctrl_refs[s], maintainOffset=True, name=root_ctrl_refs[s]+"_PaC"))




    def spine_options(self, spine):
        # compose the volumeVariation and ikFkBlend attributes from Spine module to optionCtrl:
        for s, side in enumerate(self.ar.maker.get_mirror_names(spine)):
            # connect the optionCtrl volume_variation_attr to hips_a volume_variation_attr and hide it for each side of the mirror (if it exists):
            hips_a = spine.composed['hipsAList'][s]
            volume_variation_attr = spine.composed['volumeVariationAttrList'][s]
            active_vv_attrs = spine.composed['ActiveVolumeVariationAttrList'][s]
            master_scale_vv_attrs = spine.composed['MasterScaleVolumeVariationAttrList'][s]
            ik_fk_blend_attr = spine.composed['IkFkBlendAttrList'][s]
            cluster_grp = spine.composed["scalableGrp"][s]
            shape_vis_attrs = spine.composed["shapeVisAttrList"]
            self.to_ids.extend(cmds.scaleConstraint(self.ar.maker.master_ctrl, cluster_grp, name=cluster_grp+"_ScC"))
            cmds.addAttr(self.ar.maker.option_ctrl, longName=volume_variation_attr, attributeType="float", defaultValue=1, keyable=True)
            cmds.connectAttr(self.ar.maker.option_ctrl+'.'+volume_variation_attr, hips_a+'.'+volume_variation_attr)
            cmds.setAttr(hips_a+'.'+volume_variation_attr, keyable=False)
            cmds.addAttr(self.ar.maker.option_ctrl, longName=active_vv_attrs, attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=True)
            cmds.connectAttr(self.ar.maker.option_ctrl+'.'+active_vv_attrs, hips_a+'.'+active_vv_attrs)
            cmds.setAttr(hips_a+'.'+active_vv_attrs, keyable=False)
            cmds.connectAttr(self.ar.maker.master_ctrl+'.scaleX', hips_a+'.'+master_scale_vv_attrs)
            cmds.setAttr(hips_a+'.'+master_scale_vv_attrs, keyable=False)
            cmds.addAttr(self.ar.maker.option_ctrl, longName=ik_fk_blend_attr, attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
            cmds.connectAttr(self.ar.maker.option_ctrl+'.'+ik_fk_blend_attr, hips_a+'.'+ik_fk_blend_attr)
            cmds.setAttr(hips_a+'.'+ik_fk_blend_attr, keyable=False)
            if shape_vis_attrs:
                for shape_vis_attr in shape_vis_attrs:
                    if not cmds.objExists(self.ar.maker.option_ctrl+"."+shape_vis_attr):
                        cmds.addAttr(self.ar.maker.option_ctrl, longName=shape_vis_attr, attributeType="long", min=0, max=1, defaultValue=0, keyable=False)
                        cmds.setAttr(self.ar.maker.option_ctrl+'.'+shape_vis_attr, channelBox=True)
                        cmds.connectAttr(self.ar.maker.option_ctrl+'.'+shape_vis_attr, hips_a+'.'+shape_vis_attr)
                        cmds.setAttr(hips_a+'.'+shape_vis_attr, keyable=False)
            if self.ar.data.colorize_curve:
                self.ar.ctrls.color_shape(spine.composed['InnerCtrls'][s], "cyan")
                self.ar.ctrls.color_shape(spine.composed['OuterCtrls'][s], "yellow")


    def head_options(self, head):
        # compose the head orient from the masterCtrl and facial controllers to optionCtrl:
        self.facial_ctrl_grps = head.composed['facialCtrlGrpList']
        for s, side in enumerate(self.ar.maker.get_mirror_names(head)):
            # connect the masterCtrl to head group using a orientConstraint:
            world_ref = head.composed['worldRefList'][s]
            self.to_ids.extend(cmds.parentConstraint(self.ar.maker.root_ctrl, world_ref, maintainOffset=True, name=world_ref+"_PaC"))
            if self.ar.data.colorize_curve:
                if head.composed['controllers']:
                    self.ar.ctrls.color_shape(head.composed['controllers'][s], "yellow")
                if head.composed['InnerCtrls']:
                    self.ar.ctrls.color_shape(head.composed['InnerCtrls'][s], "cyan")
                if head.composed['lCtrls']:
                    self.ar.ctrls.color_shape(head.composed['lCtrls'][s], "red")
                if head.composed['rCtrls']:
                    self.ar.ctrls.color_shape(head.composed['rCtrls'][s], "blue")
        if self.facial_ctrl_grps:
            if not cmds.objExists(self.ar.maker.option_ctrl+"."+self.ar.data.lang['c059_facial'].lower()):
                cmds.addAttr(self.ar.maker.option_ctrl, longName=self.ar.data.lang['c059_facial'].lower(), min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                cmds.setAttr(self.ar.maker.option_ctrl+"."+self.ar.data.lang['c059_facial'].lower(), channelBox=True)
            for facial_ctrl_grp in self.facial_ctrl_grps:
                cmds.connectAttr(self.ar.maker.option_ctrl+"."+self.ar.data.lang['c059_facial'].lower(), facial_ctrl_grp+".visibility", force=True)


    def eye_head(self, eye, head):
        # compose the Eye with the Head setup:
        eye_ctrl = eye.composed['eyeCtrl']
        eye_grp = eye.composed['eyeGrp']
        up_loc_grp = eye.composed['upLocGrp']
        cmds.parent(eye_grp, self.ar.maker.ctrls_vis_grp, relative=False)
        # get head module:
        if self.ar.maker.hook[eye.guide_base]['fatherModule'] == self.ar.data.head_name:
            # getting head data:
            upper_ctrl  = head.composed['upperCtrlList'][0]
            head_pac = cmds.parentConstraint(self.ar.maker.root_ctrl, upper_ctrl, eye_grp, maintainOffset=True, name=eye_grp+"_PaC")[0]
            eye_rev_node = cmds.createNode('reverse', name=eye_grp+"_Rev")
            self.to_ids.extend([head_pac, eye_rev_node])
            cmds.connectAttr(eye_ctrl+'.'+self.ar.data.lang['c032_follow'], eye_rev_node+".inputX", force=True)
            cmds.connectAttr(eye_rev_node+".outputX", head_pac+"."+self.ar.maker.root_ctrl+"W0", force=True)
            cmds.connectAttr(eye_ctrl+'.'+self.ar.data.lang['c032_follow'], head_pac+"."+upper_ctrl+"W1", force=True)
            cmds.parent(up_loc_grp, upper_ctrl, relative=False)
            cmds.setAttr(up_loc_grp+".visibility", 0)
            # head drives eyeScaleGrp:
            for s, side in enumerate(self.ar.maker.get_mirror_names(eye)):
                eye_scale_grp = eye.composed['eyeScaleGrp'][s]
                self.to_ids.extend(cmds.parentConstraint(upper_ctrl, eye_scale_grp, maintainOffset=True, name=eye_scale_grp+"_PaC"))
    

    def eye_color(self, eye):
        # changing iris and pupil color override:
        if self.ar.data.colorize_curve:
            for s, side in enumerate(self.ar.maker.get_mirror_names(eye)):
                if eye.composed['hasIris']:
                    iris_ctrl = eye.composed['irisCtrl'][s]
                    self.ar.ctrls.color_shape([iris_ctrl], "cyan")
                if eye.composed['hasPupil']:
                    pupil_ctrl = eye.composed['pupilCtrl'][s]
                    self.ar.ctrls.color_shape([pupil_ctrl], "yellow")


    def finger_scalable(self, finger):
        for s, side in enumerate(self.ar.maker.get_mirror_names(finger)):
            ik_ctrl_zero = finger.composed['ikCtrlZeroList'][s]
            scalable_grp = finger.composed['scalableGrpList'][s]
            self.to_ids.extend(cmds.scaleConstraint(self.ar.maker.master_ctrl, scalable_grp, name=scalable_grp+"_ScC"))
            # correct ik_ctrl parent to root ctrl:
            cmds.parent(ik_ctrl_zero, self.ar.maker.ctrls_vis_grp, relative=True)


    def finger_limb(self, finger, limb):
        # compose the Finger module:
        if limb:
            for s, side in enumerate(self.ar.maker.get_mirror_names(finger)):
                scalable_grp = finger.composed['scalableGrpList'][s]
                # get limb guide data:
                if self.ar.maker.hook[finger.guide_base]['fatherModule'] == self.ar.data.limb_name and self.ar.maker.hook[finger.guide_base]['fatherGuideLoc'] == 'Extrem':
                    # getting limb type:
                    limb_type_name = limb.composed['limbTypeName']
                    if limb_type_name == self.ar.data.arm_name:
                        orig_froms = limb.composed['integrateOrigFromList'][s]
                        orig_from = orig_froms[-1]
                        self.to_ids.extend(cmds.parentConstraint(orig_from, scalable_grp, maintainOffset=True, name=scalable_grp+"_PaC"))


    def single_options(self, single):
        # connect Option_Ctrl display attribute to the visibility:
        if not cmds.objExists(self.ar.maker.option_ctrl+"."+self.ar.data.lang['m081_tweaks'].lower()):
            cmds.addAttr(self.ar.maker.option_ctrl, longName=self.ar.data.lang['m081_tweaks'].lower(), min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
            cmds.setAttr(self.ar.maker.option_ctrl+"."+self.ar.data.lang['m081_tweaks'].lower(), channelBox=True)
        for s, side in enumerate(self.ar.maker.get_mirror_names(single)):
            ctrl_grp = single.composed["ctrlGrpList"][s]
            cmds.connectAttr(self.ar.maker.option_ctrl+"."+self.ar.data.lang['m081_tweaks'].lower(), ctrl_grp+".visibility", force=True)


    def single_single(self, single, father):
        # compose the Single module with another Single as a father:
        # get father module:
        if self.ar.maker.hook[single.guide_base]['fatherModule'] == self.ar.data.single_name:
            for s, side in enumerate(self.ar.maker.get_mirror_names(single)):
                # getting child Single Static_Grp:
                static_grp = single.composed["staticGrpList"][s]
                # getting father Single mainJis (indirect skinning joint) data:
                try:
                    main_jis = father.composed['mainJisList'][s]
                except:
                    main_jis = father.composed['mainJisList'][0]
                # father's mainJis drives child's staticGrp:
                self.to_ids.extend(cmds.parentConstraint(main_jis, static_grp, maintainOffset=True, name=static_grp+"_PaC"))
                self.to_ids.extend(cmds.scaleConstraint(main_jis, static_grp, maintainOffset=True, name=static_grp+"_ScC"))


    def wheel_options(self, wheel):
        # compose the Wheel module with another Option_Ctrl:
        for s, side in enumerate(self.ar.maker.get_mirror_names(wheel)):
            wheel_ctrl = wheel.composed["wheelCtrlList"][s]
            # connect Option_Ctrl RigScale_MD output to the radiusScale:
            if cmds.objExists(self.ar.maker.rig_scale_md+".dpRigScale") and cmds.getAttr(self.ar.maker.rig_scale_md+".dpRigScale") == True:
                cmds.connectAttr(self.ar.maker.rig_scale_md+".outputX", wheel_ctrl+".radiusScale", force=True)
        

    def wheel_steering(self, wheel, steering):
        for s, side in enumerate(self.ar.maker.get_mirror_names(wheel)):
            wheel_ctrl = wheel.composed["wheelCtrlList"][s]
            # get steering module:
            if self.ar.maker.hook[wheel.guide_base]['fatherModule'] == self.ar.data.steering_name:
                # getting Steering data:
                try:
                    steering_ctrl = steering.composed['steeringCtrlList'][s]
                except:
                    steering_ctrl = steering.composed['steeringCtrlList'][0]
                # connect modules to be integrated:
                cmds.connectAttr(steering_ctrl+'.'+self.ar.data.lang['c070_steering'], wheel_ctrl+'.'+self.ar.data.lang['i037_to']+self.ar.data.lang['c070_steering'].capitalize(), force=True)
                # reparent wheel module:
                wheel_hook_ctrl_grp = wheel.composed['ctrlHookGrpList'][s]
                cmds.parent(wheel_hook_ctrl_grp, self.ar.maker.ctrls_vis_grp)


    def suspension_wheel(self, suspension, wheel):
        # compose the Suspension module with Wheel:
        for s, side in enumerate(self.ar.maker.get_mirror_names(suspension)):
            loaded_father_b = suspension.composed['fatherBList'][s]
            if loaded_father_b:
                suspension_b_ctrl_grp = suspension.composed['suspensionBCtrlGrpList'][s]
                # find the correct fatherB node in order to parent the B_Ctrl:
                if "__" in loaded_father_b and ":" in loaded_father_b: # means we need to parent to a rigged guide
                    # find fatherB module data:
                    father_b_namespace = loaded_father_b[:loaded_father_b.find(":")]
                    for hook_item in self.ar.maker.hook:
                        if self.ar.maker.hook[hook_item]['guideModuleNamespace'] == father_b_namespace:
                            # got wheel module data:
                            father_b_module_data = hook_item
                            father_b_mirror_axis = self.ar.maker.hook[father_b_module_data]['guideMirrorAxis']
                            father_b_guide_mirror_names = self.ar.maker.hook[father_b_module_data]['guideMirrorName']
                            father_b_custom_name = self.ar.maker.hook[father_b_module_data]['guideCustomName']
                            father_b_guide_instance = self.ar.maker.hook[father_b_module_data]['guideInstance']
                            # working with fatherB guide mirror:
                            self.father_b_mirror_names = [""]
                            if father_b_mirror_axis != "off":
                                self.father_b_mirror_names = father_b_guide_mirror_names
                            for b, fb_side_name in enumerate(self.father_b_mirror_names):
                                if father_b_custom_name:
                                    father_b = fb_side_name + self.ar.data.prefix + father_b_custom_name + "_" + loaded_father_b[loaded_father_b.rfind(":")+1:]
                                else:
                                    father_b = fb_side_name + self.ar.data.prefix + father_b_guide_instance + "_" + loaded_father_b[loaded_father_b.rfind(":")+1:]
                                father_b_rigged_node = self.ar.maker.origined_from_data[father_b]
                                if cmds.objExists(father_b_rigged_node):
                                    if len(self.father_b_mirror_names) != 1: #means fatherB has mirror
                                        if s == b:
                                            self.to_ids.extend(cmds.parentConstraint(father_b_rigged_node, suspension_b_ctrl_grp, maintainOffset=True, name=suspension_b_ctrl_grp+"_PaC"))
                                            self.to_ids.extend(cmds.scaleConstraint(father_b_rigged_node, suspension_b_ctrl_grp, maintainOffset=True, name=suspension_b_ctrl_grp+"_ScC"))
                                    else:
                                        self.to_ids.extend(cmds.parentConstraint(father_b_rigged_node, suspension_b_ctrl_grp, maintainOffset=True, name=suspension_b_ctrl_grp+"_PaC"))
                                        self.to_ids.extend(cmds.scaleConstraint(father_b_rigged_node, suspension_b_ctrl_grp, maintainOffset=True, name=suspension_b_ctrl_grp+"_ScC"))
                else: # probably we will parent to a control curve already generated and rigged before
                    if cmds.objExists(loaded_father_b):
                        self.to_ids.extend(cmds.parentConstraint(loaded_father_b, suspension_b_ctrl_grp, maintainOffset=True, name=suspension_b_ctrl_grp+"_PaC"))
                        self.to_ids.extend(cmds.scaleConstraint(loaded_father_b, suspension_b_ctrl_grp, maintainOffset=True, name=suspension_b_ctrl_grp+"_ScC"))
            if wheel:
                # get wheel module:
                if self.ar.maker.hook[suspension.guide_base]['fatherModule'] == self.ar.data.wheel_name:
                    # parent suspension control group to wheel Main_Ctrl
                    suspension_hook_ctrl_grp = suspension.composed['ctrlHookGrpList'][s]
                    wheel_main_ctrl = wheel.composed['mainCtrlList'][s]
                    self.to_ids.extend(cmds.parentConstraint(wheel_main_ctrl, suspension_hook_ctrl_grp, maintainOffset=True, name=suspension_hook_ctrl_grp+"_PaC"))
                    self.to_ids.extend(cmds.scaleConstraint(wheel_main_ctrl, suspension_hook_ctrl_grp, maintainOffset=True, name=suspension_hook_ctrl_grp+"_ScC"))


    def nose_options(self, nose):
        # compose the nose control colors:
        if self.ar.maker.hook[nose.guide_base]['guideMirrorAxis'] == "off":
            if self.ar.data.colorize_curve:
                self.ar.ctrls.color_shape(nose.composed['controllers'][0], "yellow")
                self.ar.ctrls.color_shape(nose.composed['lCtrls'][0], "red")
                self.ar.ctrls.color_shape(nose.composed['rCtrls'][0], "blue")
        
        
    def nose_head(self, nose, head):
        if self.ar.maker.hook[nose.guide_base]['fatherModule'] == self.ar.data.head_name:
            upper_ctrl = head.composed['upperCtrlList'][0]
            upper_jaw_ctrl = head.composed['upperJawCtrlList'][0]
            if not upper_jaw_ctrl == upper_ctrl:
                ctrl_grp = nose.composed['ctrlHookGrpList'][0]
                main_ctrl = nose.composed['mainCtrlList'][0]
                cmds.addAttr(main_ctrl, longName="spaceSwitch", attributeType="enum", en="Upper Jaw:Upper Head", keyable=True)
                rev_node = cmds.createNode("reverse", name="Nose_SpaceSwitch_Rev")
                pac = cmds.parentConstraint(upper_jaw_ctrl, upper_ctrl, ctrl_grp, maintainOffset=True, name=ctrl_grp+"_PaC")[0]
                cmds.connectAttr(main_ctrl+".spaceSwitch", pac+"."+upper_ctrl+"W1", force=True)
                cmds.connectAttr(main_ctrl+".spaceSwitch", rev_node+".inputX", force=True)
                cmds.connectAttr(rev_node+".outputX", pac+"."+upper_jaw_ctrl+"W0", force=True)
                self.to_ids.extend([pac, rev_node])


    def chain_options(self, chain):
        # world_ref of chain controlled by optionCtrl:
        world_refs = chain.composed['worldRefList']
        world_ref_shapes = chain.composed['worldRefShapeList']
        for w, world_ref in enumerate(world_refs):
            # do actions in order to make chain be controlled by optionCtrl:
            float_attrs = cmds.listAttr(world_ref, visible=True, scalar=True, keyable=True, userDefined=True)
            for f, float_attr in enumerate(float_attrs):
                if f != len(float_attrs):
                    if not cmds.objExists(self.ar.maker.option_ctrl+'.'+float_attr):
                        current_value = cmds.getAttr(world_ref+'.'+float_attr)
                        cmds.addAttr(self.ar.maker.option_ctrl, longName=float_attr, attributeType=cmds.getAttr(world_ref+"."+float_attr, type=True), minValue=0, maxValue=1, defaultValue=current_value, keyable=True)
                    cmds.connectAttr(self.ar.maker.option_ctrl+'.'+float_attr, world_ref+'.'+float_attr, force=True)
            if not cmds.objExists(self.ar.maker.option_ctrl+'.'+float_attrs[len(float_attrs)-1]):
                cmds.addAttr(self.ar.maker.option_ctrl, longName=float_attrs[len(float_attrs)-1], attributeType=cmds.getAttr(world_ref+"."+float_attr, type=True), defaultValue=1, keyable=True)
                cmds.connectAttr(self.ar.maker.option_ctrl+'.'+float_attrs[len(float_attrs)-1], world_ref+'.'+float_attrs[len(float_attrs)-1], force=True)
            cmds.connectAttr(self.ar.maker.master_ctrl+".scaleX", world_ref+".scaleX", force=True)
            cmds.delete(world_ref_shapes[w])
            world_ref = cmds.rename(world_ref, world_ref.replace("_Ctrl", "_Grp"))
            self.to_ids.extend(cmds.parentConstraint(self.ar.maker.root_ctrl, world_ref, maintainOffset=True, name=world_ref+"_PaC"))
            # remove dpControl attribute
            self.ar.custom_attr.remove_attr("dpControl", [world_ref])
