# importing libraries:
from maya import cmds
from maya import mel
from . import base
from ..tool import correction_manager
from importlib import reload



class BaseStandard(base.BaseLibrary):
    def __init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI, *args):
        """ Initialize the rigging standard module class.
        """
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
            reload(correction_manager)
        self.get_namespace_for_it()
        self.correction_manager = correction_manager.CorrectionManager(self.ar)
        self.correction_manager.ui = False
        self.raw = True
        self.serialized = False
        self.sides = [""]
        self.guide_net = None
        

    def get_namespace_for_it(self, number_name=None):
        self.number_name = number_name
        if not self.number_name:
            self.number_name = self.ar.data.base_name+str(self.ar.utils.findLastNumber())
        self.rigType = "biped"
        # defining namespace:
        self.guide_namespace = self.name+"__"+self.number_name
        cmds.namespace(setNamespace=":")
        self.name_guide = self.guide_namespace+":Guide"
        self.guide_base = self.name_guide+"_Base"
        self.radius_ctrl = self.guide_base+"_RadiusCtrl"
        self.annotation = self.guide_base+"_Ant"


    def build_raw_guide(self, number_name=None, *args):
        self.get_namespace_for_it(number_name)
        if not cmds.namespace(exists=self.guide_namespace):
            cmds.namespace(add=self.guide_namespace)
            self.create_guide()
        self.load_raw_guide()
        return self.guide_base
    

    def load_raw_guide(self, number_name=None):
        if number_name:
            self.number_name = number_name
        if self.ar.data.ui_state:
            self.create_module_layout()
        self.set_guide_attr('moduleInstanceInfo', self, True)
        self.guide_net = self.ar.utils.getNodeByMessage("net", self.guide_base)
        if self.guide_net:
            self.raw = cmds.getAttr(self.guide_net+".rawGuide")

    
    def create_module_layout(self):
        """ Create the Module Layout, so it will exists in the right as a new options to editModules.
        """
        layout_name = ""
        if "customName" in cmds.listAttr(self.guide_base):
            layout_name = cmds.getAttr(self.guide_base+".customName")
        if not layout_name:
            layout_name = self.number_name
        self.module_layout_name = self.ar.data.lang[self.title]+" - "+layout_name
        if self.ar.data.ui_state:
            if cmds.columnLayout("rig_guides_inst_cl", query=True, exists=True):
                cmds.frameLayout(f"{self.number_name}_fl", label=self.module_layout_name, collapsable=True, collapse=False, parent="rig_guides_inst_cl")
                cmds.columnLayout(f"{self.number_name}_top_cl", adjustableColumn=True, parent=f"{self.number_name}_fl")
            # rig_guides_inst_cl -> here we have just the column layouts to be populated by modules.
            self.ar.guide_ui.basic_module_layout(self)            

    
    def create_guide_base(self):
        """ Create the node elements to Guide module in the scene, like guides, attributes, etc...
        """
        self.ar.opt.check_use_default_render_layer()
        # create guide base (main guide node):
        self.guide_base, self.radius_ctrl = self.ar.ctrls.create_guide_base_loc(self.guide_base, r=2)
        self.add_guide_base_attr()
        self.create_guide_annotation()
        # setup worldSize
        self.ar.ctrls.get_dpar_temp_grp()
        self.create_world_size()
        # prepare guide to serialization
        self.create_guide_network()
        self.ar.data.guide_instances.append(self)
        if self.ar.data.ui_state:
            self.ar.ui_manager.update_guide_footer()


    def add_guide_base_attr(self):
        # add attributes to be read when rigging module:
        for bool_attr in ['guideBase', 'mirrorEnable', 'displayAnnotation']:
            cmds.addAttr(self.guide_base, longName=bool_attr, attributeType='bool')
            cmds.setAttr(self.guide_base+"."+bool_attr, 1)
        for str_attr in ['moduleType', 'moduleNamespace', 'customName', 'mirrorAxis', 'mirrorName', 'mirrorNameList', 'hookNode', 'moduleInstanceInfo', 'guideObjectInfo', 'rigType', 'dpARVersion']:
            cmds.addAttr(self.guide_base, longName=str_attr, dataType='string')
        cmds.setAttr(self.guide_base+".moduleType", self.name, type='string')
        cmds.setAttr(self.guide_base+".moduleNamespace", self.guide_base[:self.guide_base.rfind(":")], type='string')
        cmds.setAttr(self.guide_base+".mirrorAxis", "off", type='string')
        cmds.setAttr(self.guide_base+".mirrorName", self.ar.data.lang['p002_left']+' --> '+self.ar.data.lang['p003_right'], type='string')
        cmds.setAttr(self.guide_base+".hookNode", "_Grp", type='string')
        cmds.setAttr(self.guide_base+".moduleInstanceInfo", self, type='string')
        cmds.setAttr(self.guide_base+".guideObjectInfo", self.ar.config.get_instance(self.name, [self.ar.data.standard_folder], "imported"), type='string')
        cmds.setAttr(self.guide_base+".rigType", self.rigType, type='string')
        cmds.setAttr(self.guide_base+".dpARVersion", self.ar.data.version, type='string')
        for float_attr in ['shapeSize', 'worldSize']:
            cmds.addAttr(self.guide_base, longName=float_attr, attributeType='float', defaultValue=1)
            cmds.setAttr(self.guide_base+"."+float_attr, keyable=True)
        for int_short_attr in ['degree']:
            cmds.addAttr(self.guide_base, longName=int_short_attr, attributeType='short')
        cmds.setAttr(self.guide_base+".degree", self.ar.data.degree_option)
        for int_long_attr in ['guideColorIndex']:
            cmds.addAttr(self.guide_base, longName=int_long_attr, attributeType='long')
        for c, guide_color_attr in enumerate(['guideColorR', 'guideColorG', 'guideColorB']):
            cmds.addAttr(self.guide_base, longName=guide_color_attr, attributeType='float')
            cmds.setAttr(self.guide_base+"."+guide_color_attr, self.ar.ctrls.colors[0][c])


    def create_guide_annotation(self):
        # create annotation to this module:
        self.annotation = cmds.annotate(self.guide_base, tx=self.guide_base, point=(0,2,0))
        self.annotation = cmds.listRelatives(self.annotation, parent=True)[0]
        self.annotation = cmds.rename(self.annotation, self.guide_base+"_Ant")
        cmds.parent(self.annotation, self.guide_base)
        cmds.setAttr(self.annotation+'.text', self.guide_base[self.guide_base.find("__")+2:self.guide_base.rfind(":")], type='string')
        cmds.setAttr(self.annotation+'.template', 1)
        cmds.connectAttr(self.radius_ctrl+".translateX", self.annotation+".translateY", force=True)
    
    
    def check_guide_integrity(self):
        """ This function verify the integrity of the current module guide checking if there's an active guideBase attribute.
            Returns True if Ok and False if Fail.
        """
        # conditionals to be elegible as a rigged guide module:
        if cmds.objExists(self.guide_base):
            if 'guideBase' in cmds.listAttr(self.guide_base):
                if cmds.getAttr(self.guide_base+'.guideBase') == 1:
                    return True
                else:
                    try:
                        self.delete_guide()
                        mel.eval('warning \"'+ self.ar.data.lang['e000_guideNotFound'] +' - '+ self.guide_base +'\";')
                    except:
                        pass
                    return False
    
    
    def delete_guide(self, *args):
        """ Delete the Guide, ModuleLayout and Namespace.
        """
        for item in [self.guide_base[:self.guide_base.find(":")]+"_MirrorGrp",
                     self.guide_base+"_WorldSize_Ref"]:
            if cmds.objExists(item):
                cmds.delete(item)
        # delete the guide module:
        self.ar.utils.clearNodeGrp(self.guide_base, 'guideBase', unparent=True)
        # remove the namespaces:
        if self.guide_namespace in cmds.namespaceInfo(listOnlyNamespaces=True):
            cmds.namespace(moveNamespace=(self.guide_namespace, ':'), force=True)
            cmds.namespace(removeNamespace=self.guide_namespace, force=True)
        if not self.ar.data.rebuilding:
            self.ar.ui_manager.refresh_ui(clear_selection=True)
    

    def duplicate_guide(self, *args):
        """ This module will just do a simple duplicate from Maya because we have a scriptJob to do the setup creation of a new guide instance.
        """
        cmds.duplicate(self.guide_base)

    
    def set_guide_custom_name(self, check_text=None, pad=1, *args):
        """ Edit the number_name to set the user custom name from module UI.
        """
        if self.check_guide_integrity():
            if check_text:
                inputted_text = check_text
            else:
                try:
                    # get the entered text:
                    inputted_text = cmds.textField("edit_guide_custom_name_tf", query=True, text=True)
                except:
                    inputted_text = ""
            inputted_text = inputted_text.replace(" ", "_")
            # call utils to return the normalized text:
            self.custom_name = self.ar.utils.normalizeText(inputted_text, prefixMax=30)
            # check if there is another rigged module using the same customName:
            if self.custom_name == "":
                try:
                    cmds.textField("edit_guide_custom_name_tf", edit=True, text="")
                except:
                    pass
                cmds.setAttr(self.guide_base+".customName", "", type='string')
                self.number_name = self.guide_namespace.split("__")[-1]
            else:
                base_name = self.custom_name
                suffix_numbers = self.ar.utils.getSuffixNumberList(self.custom_name)
                if suffix_numbers[1]:
                    base_name = suffix_numbers[1]
                dpar_names = []
                nets = self.ar.utils.getNetworkNodeByAttr("dpGuideNet")
                for net in nets:
                    if base_name == self.ar.utils.getSuffixNumberList(cmds.getAttr(net+".guideName"))[1]:
                        dpar_names.append(cmds.getAttr(net+".guideName"))
                if dpar_names:
                    if self.custom_name in dpar_names:
                        for n in range(1, len(dpar_names)+2):
                            if not base_name+str(n).zfill(pad) in dpar_names:
                                self.custom_name = base_name+str(n).zfill(pad)
                                break
                # edit the prefixTextField with the normalText:
                try:
                    cmds.textField("edit_guide_custom_name_tf", edit=True, text=self.custom_name)
                    cmds.frameLayout("edit_guide_fl", edit=True, label=self.ar.data.lang[self.title]+" - "+self.custom_name)
                except:
                    pass
                cmds.setAttr(self.guide_base+".customName", self.custom_name, type='string')
                cmds.setAttr(self.annotation+".text", self.custom_name, type='string')
                if self.guide_net:
                    cmds.setAttr(self.guide_net+".guideName", self.custom_name, type='string')
                # set number_name:
                self.number_name = self.custom_name
                

    def setup_corrective_net(self, ctrl, first_node, second_node, net_name, axis, axis_order, input_end_value, is_leg=None, legs=None):
        """ Create the correction manager network node and returns it.
            legs = [
                        0 = rename,
                        1 = axis,
                        2 = axis_order
                        3 = inputValue,
                    ]
        """
        if not cmds.objExists(ctrl+"."+self.ar.data.lang['c124_corrective']):
            cmds.addAttr(ctrl, longName=self.ar.data.lang['c124_corrective'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
        # corrective network node
        net = self.correction_manager.create_correction_manager_setup([first_node, second_node], name=net_name, correct_type=self.correction_manager.angle_name, to_rivet=False, from_ui=False)
        cmds.connectAttr(ctrl+"."+self.ar.data.lang['c124_corrective'], net+".corrective", force=True)
        cmds.setAttr(net+".axis", axis)
        cmds.setAttr(net+".axisOrder", axis_order)
        if is_leg:
            cmds.setAttr(net+".axis", legs[1])
            cmds.setAttr(net+".axisOrder", legs[2])
        net_input_value = cmds.getAttr(net+".inputValue")
        if net_input_value+input_end_value == 0:
            input_end_value += 1
        cmds.setAttr(net+".inputStart", net_input_value) #offset default position
        cmds.setAttr(net+".inputEnd", net_input_value+input_end_value)
        if is_leg:
            if net_input_value+legs[3] == 0:
                legs[3] += 1
            cmds.setAttr(net+".inputEnd", net_input_value+legs[3])
            net = self.correction_manager.change_name(legs[0])+"_Net"
        return net


    def setup_corrective_controllers(self, corrective_joints, s, label_name, corrective_nets, calibrate_presets, inverts, mirrors=None):
        """ Create corrective joint controllers.
        """
        if corrective_joints:
            l = 0
            s_default = s
            mirror_prefixes = [self.ar.data.lang['p002_left'], self.ar.data.lang['p003_right']]
            for i, jcr in enumerate(corrective_joints):
                if not i == 0: #exclude jar in the index 0
                    # logic to mirror calibration setup for left and right sides of a centered module like neck/head
                    m = i
                    if mirrors:
                        if mirrors[i]:
                            s += 1
                            if l == 0:
                                old_jcr = jcr
                                jcr = cmds.rename(jcr, mirror_prefixes[l]+"_"+jcr)
                            else:
                                jcr = cmds.rename(jcr, mirror_prefixes[l]+"_"+old_jcr)
                                m -= 1
                            corrective_joints[i] = jcr
                            l += 1
                        else:
                            m = i
                            s = s_default
                    else:
                        s = s_default
                    # add joint label, create controller, zeroOut
                    self.ar.utils.setJointLabel(jcr, s+self.joint_label_add, 18, label_name+"_"+str(m))
                    jcr_ctrl, jcr_grp = self.ar.ctrls.create_corrective_joint_ctrl(corrective_joints[i], corrective_nets[i], radius=self.radius*0.2)
                    cmds.parent(jcr_grp, self.corrective_ctrls_grp)
                    # preset calibration
                    for calibrate_attr in calibrate_presets[i].keys():
                        if "calibrateT" in calibrate_attr:
                            cmds.setAttr(jcr_ctrl+"."+calibrate_attr, calibrate_presets[i][calibrate_attr]*self.radius)
                        else:
                            cmds.setAttr(jcr_ctrl+"."+calibrate_attr, calibrate_presets[i][calibrate_attr])
                    if inverts:
                        invert_attrs = inverts[i]
                        if invert_attrs:
                            for invert_attr in invert_attrs:
                                cmds.setAttr(jcr_ctrl+"."+invert_attr, 1)
                                cmds.addAttr(jcr_ctrl+"."+invert_attr, edit=True, defaultValue=1)


    def change_main_ctrls_number(self, inputted_number, *args):
        """ Edit the number of main controllers in the guide.
        """
        self.ar.opt.check_use_default_render_layer()
        # get the number of main controllers entered by user:
        if inputted_number == 0:
            if self.ar.data.ui_state and cmds.intField("edit_guide_main_ctrl_if", query=True, exists=True):
                main_number = cmds.intField("edit_guide_main_ctrl_if", query=True, value=True)
            else:
                return
        else:
            main_number = inputted_number
        # limit range
        if main_number >= self.current_joint_number:
            main_number = self.current_joint_number - 1
            if main_number == 0:
                main_number = 1
                if cmds.checkBox("edit_guide_main_ctrl_cb", query=True, exists=True):
                    cmds.checkBox("edit_guide_main_ctrl_cb", edit=True, editable=False)
            if cmds.intField("edit_guide_main_ctrl_if", query=True, exists=True):
                cmds.intField("edit_guide_main_ctrl_if", edit=True, value=main_number)
        cmds.setAttr(self.guide_base+".nMain", main_number)


    def changeStyle(self, style, *args):
        """ Change the style to be applyed custom actions to be more animator friendly.
            We will optimise: control world orientation
        """
        if style == self.ar.data.lang['m042_default'] or style == 0:
            cmds.setAttr(self.guide_base+".style", 0)
        elif style == self.ar.data.lang['m026_biped'] or style == 1:
            cmds.setAttr(self.guide_base+".style", 1)
        elif style == self.ar.data.lang['m037_quadruped'] or style == 2:
            cmds.setAttr(self.guide_base+".style", 2)


    def set_main_ctrls(self, value, *args):
        """ Just store the main controllers checkBox value and enable the int field.
        """
        cmds.setAttr(self.guide_base+".mainControls", value)
        self.ar.guide_ui.enable_main_ctrls(self, value)


    def add_fk_main_ctrls(self, side, controllers):
        """ Implement the fk main controllers.
        """
        main_ctrls = []
        # getting and calculating values
        total_to_add_main = 1
        self.n_main = cmds.getAttr(self.base+".nMain")
        if self.n_main > 1:
            total_to_add_main = int(self.n_joints/self.n_main)
        # run throgh the chain
        for m in range(0, self.n_main):
            start = m*total_to_add_main
            end = (m+1)*total_to_add_main
            if m == self.n_main-1:
                end = self.n_joints
            for n in range(start, end):
                current_ctrl = controllers[n]
                current_ctrl_zero = cmds.listRelatives(current_ctrl, parent=True)[0]
                if n == start:
                    # create a main controller
                    main_ctrl = self.ar.ctrls.create_controller("id_096_FkLineMain", side+self.number_name+"_%02d_Main_Fk_Ctrl"%(n), r=self.radius*1.2, d=self.curve_degree, guide_source=self.name_guide+"_Base", parent_tag=self.get_parent_to_tag(main_ctrls))
                    main_ctrls.append(main_ctrl)
                    self.ar.ctrls.color_shape([main_ctrl], "cyan")
                    cmds.addAttr(main_ctrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                    # position
                    cmds.parent(main_ctrl, current_ctrl_zero)
                    cmds.makeIdentity(main_ctrl, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(current_ctrl, main_ctrl)
                    # intensity utilities
                    r_intensity_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_R_Main_MD")
                    self.to_ids.append(r_intensity_md)
                    for axis in self.ar.data.axes:
                        cmds.connectAttr(main_ctrl+".rotate"+axis, r_intensity_md+".input1"+axis, force=True)
                        cmds.connectAttr(main_ctrl+"."+self.ar.data.lang['c049_intensity'], r_intensity_md+".input2"+axis, force=True)
                else:
                    # offseting sub controllers
                    offset_grp = cmds.group(name=current_ctrl+"_Offset_Grp", empty=True)
                    cmds.parent(offset_grp, current_ctrl_zero)
                    cmds.makeIdentity(offset_grp, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(current_ctrl, offset_grp)
                    for axis in self.ar.data.axes:
                        cmds.connectAttr(r_intensity_md+".output"+axis, offset_grp+".rotate"+axis, force=True)
                # display sub controllers shapes
                self.ar.ctrls.set_sub_ctrl_display(main_ctrl, current_ctrl, 0)
    

    def get_mirror_sides(self):
        """ Processes the mirror information for the current guide.
            Defines self.sides to be used by the module.
        """
        # analisys the mirror module:
        self.mirror_axis = cmds.getAttr(self.guide_base+".mirrorAxis")
        if self.mirror_axis != 'off':
            # get rigs names:
            self.mirror_names = cmds.getAttr(self.guide_base+".mirrorName")
            # get first and last letters to use as side initials (prefix):
            self.sides = [self.mirror_names[0]+'_', self.mirror_names[len(self.mirror_names)-1]+'_']
            for s, side in enumerate(self.sides):
                duplicated = cmds.duplicate(self.guide_base, name=side+self.number_name+'_Guide_Base')[0]
                for item in cmds.listRelatives(duplicated, allDescendents=True):
                    cmds.rename(item, side+self.number_name+"_"+item)
                self.mirror_grp = cmds.group(name="Guide_Base_Grp", empty=True)
                cmds.parent(side+self.number_name+'_Guide_Base', self.mirror_grp, absolute=True)
                # re-rename grp:
                cmds.rename(self.mirror_grp, side+self.number_name+'_'+self.mirror_grp)
                # do a group mirror with negative scaling:
                if s == 1:
                    without_flip = False
                    if cmds.objExists(self.guide_base+".flip"):
                        if cmds.getAttr(self.guide_base+".flip") == 0:
                            without_flip = True
                    if without_flip:
                        for axis in self.mirror_axis:
                            got_value = cmds.getAttr(side+self.number_name+"_Guide_Base.translate"+axis)
                            fliped_value = got_value*(-2)
                            cmds.setAttr(side+self.number_name+'_'+self.mirror_grp+'.translate'+axis, fliped_value)
                    else:
                        for axis in self.mirror_axis:
                            cmds.setAttr(side+self.number_name+'_'+self.mirror_grp+'.scale'+axis, -1)
            # joint labelling:
            self.joint_label_add = 1
        else: # if not mirror:
            duplicated = cmds.duplicate(self.guide_base, name=self.number_name+'_Guide_Base')[0]
            for item in cmds.listRelatives(duplicated, allDescendents=True):
                cmds.rename(item, self.number_name+"_"+item)
            self.mirror_grp = cmds.group(self.number_name+'_Guide_Base', name="Guide_Base_Grp", relative=True)
            # re-rename grp:
            cmds.rename(self.mirror_grp, self.number_name+'_'+self.mirror_grp)
            # joint labelling:
            self.joint_label_add = 0
        # store the number of this guide by module type
        self.dpar_count = self.ar.utils.findModuleLastNumber(self.name, "moduleType", True)


    def rig_me(self, *args):
        """ The fun part of the module, just read the values from editModuleLayout and create the rig for this guide.
        """
        self.ar.utils.close_ui(self.ar.data.plus_info_win_name)
        self.ar.utils.close_ui(self.ar.data.color_override_win_name)
        if self.check_guide_integrity():
            self.to_ids = []
            self.oldUnitConversionList = cmds.ls(selection=False, type="unitConversion")
            if self.ar.data.ui_state:
                self.ar.guide_ui.clear_selected_module_layout()

            # unPinGuides before Rig them:
            self.ar.job.unpin_guide([self.guide_base], force=True)
            
            # RIG:
            self.ar.opt.check_use_default_render_layer()
            
            # get the radius value to controls:
            self.radius = 1
            if cmds.objExists(self.radius_ctrl):
                self.radius = self.ar.utils.getCtrlRadius(self.radius_ctrl)
                
            # get curve degree:
            self.curve_degree = cmds.getAttr(self.guide_base+".degree")
            
            # unparent all guide modules child:
            children = cmds.listRelatives(self.guide_base, allDescendents=True, type='transform')
            if children:
                for child in children:
                    if "guideBase" in cmds.listAttr(child) and cmds.getAttr(child+".guideBase") == 1:
                        cmds.parent(child, world=True)
            
            # just edit customName and prefix:
            if self.custom_name != "" and self.custom_name != " " and self.custom_name != "_" and self.custom_name != None:
                names = [n for n in cmds.ls(selection=False, type="transform") if "dpAR_name" in cmds.listAttr(n)]
                for item in names:
                   if self.custom_name == cmds.getAttr(item+".dpAR_name"):
                       self.custom_name = self.custom_name + "1"
                self.number_name = self.custom_name

            if self.ar.data.prefix:
                self.number_name = self.ar.data.prefix + self.number_name
            cmds.select(clear=True)
            self.get_mirror_sides()
            self.articulation = self.get_guide_attr('articulation')
            self.corrective = self.get_guide_attr('corrective')
            self.flip = self.get_guide_attr('flip')
            self.rigType = self.get_guide_attr('rigType')
    

    def create_hook_setup(self, side, controllers, scalableList=None, staticList=None, *args):
        """ Generate the hook setup to find lists of controllers, scalable and static groups.
            Add message attributes to map hooked groups for the rigged module.
        """
        # create a masterModuleGrp to be checked if this rig exists:
        self.ctrl_hook_grp = cmds.group(controllers, name=side+self.number_name+"_Control_Grp")
        self.scalable_hook_grp = cmds.group(empty=True, name=side+self.number_name+"_Scalable_Grp")
        self.static_hook_grp = cmds.group(self.ctrl_hook_grp, self.scalable_hook_grp, name=side+self.number_name+"_Static_Grp")
        if staticList:
            cmds.parent(staticList, self.static_hook_grp)
        if scalableList:
            cmds.parent(scalableList, self.scalable_hook_grp)
        self.ar.custom_attr.add_attr(0, [self.ctrl_hook_grp, self.scalable_hook_grp, self.static_hook_grp]) #dpID
        # add hook attributes to be read when rigging composed modules:
        self.ar.utils.addHook(objName=self.ctrl_hook_grp, hookType='ctrlHook')
        self.ar.utils.addHook(objName=self.scalable_hook_grp, hookType='scalableHook')
        self.ar.utils.addHook(objName=self.static_hook_grp, hookType='staticHook')
        cmds.lockNode(self.guide_net, lock=False)
        # add module type counter value
        if not 'dpAR_count' in cmds.listAttr(self.guide_net):
            cmds.addAttr(self.guide_net, longName='dpAR_count', attributeType='long', keyable=False)
            cmds.setAttr(self.guide_net+'.dpAR_count', self.dpar_count)
        # message attributes
        cmds.addAttr(self.guide_net, longName=side+"ControlHookGrp", attributeType="message")
        cmds.addAttr(self.guide_net, longName=side+"StaticHookGrp", attributeType="message")
        cmds.addAttr(self.guide_net, longName=side+"ScalableHookGrp", attributeType="message")
        cmds.connectAttr(self.ctrl_hook_grp+".message", self.guide_net+"."+side+"ControlHookGrp", force=True)
        cmds.connectAttr(self.scalable_hook_grp+".message", self.guide_net+"."+side+"ScalableHookGrp", force=True)
        cmds.connectAttr(self.static_hook_grp+".message", self.guide_net+"."+side+"StaticHookGrp", force=True)
        cmds.setAttr(self.scalable_hook_grp+".visibility", self.ar.data.display_joint)
        cmds.setAttr(self.static_hook_grp+".visibility", self.ar.data.display_joint)
        cmds.lockNode(self.guide_net, lock=True)

    
    def composing_info(self):
        """ This method just create this dictionary in order to build information of module integration.
        """
        self.composed = {}
    

    def create_guide_network(self, number=None):
        """ Create a network for the current guide and store on it the nodes used in this module by message.
        """
        if number:
            guide_number = number
        else:
            guide_number = self.ar.utils.findLastNumber()
        self.guide_net = cmds.createNode("network", name="dpGuide_"+guide_number+"_Net")
        self.ar.custom_attr.add_attr(0, [self.guide_net])[0] #dpID
        for base_attr in ["dpNetwork", "dpGuideNet", "rawGuide"]:
            cmds.addAttr(self.guide_net, longName=base_attr, attributeType="bool")
            cmds.setAttr(self.guide_net+"."+base_attr, 1)
        cmds.addAttr(self.guide_net, longName="moduleType", dataType="string")
        cmds.addAttr(self.guide_net, longName="guideName", dataType="string")
        cmds.addAttr(self.guide_net, longName="guideNumber", dataType="string")
        cmds.addAttr(self.guide_net, longName="beforeData", dataType="string")
        cmds.addAttr(self.guide_net, longName="afterData", dataType="string")
        cmds.addAttr(self.guide_net, longName="linkedNode", attributeType="message")
        cmds.setAttr(self.guide_net+".moduleType", self.name, type="string")
        cmds.setAttr(self.guide_net+".guideName", self.number_name, type="string")
        cmds.setAttr(self.guide_net+".guideNumber", guide_number, type="string")
        if not "net" in cmds.listAttr(self.guide_base):
            cmds.addAttr(self.guide_base, longName="net", attributeType="message")
        cmds.lockNode(self.guide_net, lock=False)
        cmds.connectAttr(self.guide_net+".message", self.guide_base+".net", force=True)
        cmds.connectAttr(self.guide_base+".message", self.guide_net+".linkedNode", force=True)
        self.add_node_to_guide_net([self.guide_base, self.radius_ctrl, self.annotation], ["main", "radiusCtrl", "annotation"])

    
    def add_node_to_guide_net(self, nodes, message_attrs):
        """ Include the given node list to the respective given attribute list as message connection in the network.
        """
        for node, message_attr in zip(nodes, message_attrs):
            if not message_attr in cmds.listAttr(self.guide_net):
                self.lock_node_status = cmds.lockNode(self.guide_net, query=True, lock=True)[0]
                cmds.lockNode(self.guide_net, lock=False)
                cmds.addAttr(self.guide_net, longName=message_attr, attributeType="message")
            cmds.connectAttr(node+".message", self.guide_net+"."+message_attr, force=True)
            self.add_attr_to_before_data(message_attr)


    def remove_attr_from_guide_net(self, attributes):
        """ Remove the given attribute list from the network node.
        """
        for attr in attributes:
            cmds.deleteAttr(self.guide_net+"."+attr)
            befores = self.get_befores()
            if attr in befores:
                befores.remove(attr)
                self.set_befores(befores)
    

    def add_attr_to_before_data(self, attr):
        """ Just read the current before attribute string, add the new give attribute to it and set the guide network attibute with this new info.
            Returns the updated before data string.
        """
        before = cmds.getAttr(self.guide_net+".beforeData") or ""
        before = f"{before}{attr};"
        cmds.setAttr(self.guide_net+".beforeData", before, type="string")
        if self.lock_node_status:
            cmds.lockNode(self.guide_net, lock=True)
        return before


    def get_befores(self):
        """ Just return a list with the splited items from the guide network beforeData string attribute.
        """
        before = cmds.getAttr(self.guide_net+".beforeData")
        if before:
            return list(filter(None, before.split(";")))


    def set_befores(self, befores):
        """ Receives a list and set it as beforeData string attribute in the guide network.
        """
        cmds.setAttr(self.guide_net+".beforeData", (";").join(befores)+";", type="string")


    def get_node_data(self, node):
        """ Get and return all transformation data for the transform, also the userDefined attributes and them values.
            Returns a dictionary with this info.
        """
        attributes = cmds.listAttr(node, keyable=True)
        user_defined_attributes = cmds.listAttr(node, unlocked=True, userDefined=True)
        if attributes:
            attr_data = {}
            fathers = cmds.listRelatives(node, parent=True)
            if fathers:
                attr_data["FatherNode"] = fathers[0]
                if "guideBase" in cmds.listAttr(node) and cmds.getAttr(node+".guideBase") == 1:
                    if not "__" in fathers[0]: #not a rawGuide
                        if "guide_source" in cmds.listAttr(fathers[0]):
                            attr_data["FatherNode"] = cmds.getAttr(fathers[0]+".guide_source")
                    cmds.parent(node, world=True) #to export guide base transformation in worldSpace
            else:
                attr_data["FatherNode"] = None
            if user_defined_attributes:
                attributes.extend(user_defined_attributes)
            attributes = list(set(attributes))
            attributes.sort()
            for attr in attributes:
                if cmds.getAttr(node+"."+attr, type=True) == "message":
                    connections = cmds.listConnections(node+"."+attr, source=True, destination=False)
                    if connections:
                        attr_data[attr] = connections[0]
                else:
                    attr_data[attr] = cmds.getAttr(node+"."+attr)
            if "guideBase" in cmds.listAttr(node) and cmds.getAttr(node+".guideBase") == 1:
                if fathers:
                    cmds.parent(node, fathers[0])
            return attr_data


    def serialize_guide(self, build_it=True):
        """ Work in the guide info to store it as a json dictionary in order to be able to rebuild it in the future.
        """
        self.ar.job.unpin_guide(force=True)
        if cmds.objExists(self.guide_base):
            self.custom_name = cmds.getAttr(self.guide_base+".customName") or ""
        if not self.serialized:
            after_data, guide_data = {}, {}
            befores = self.get_befores()
            if befores:
                if build_it:
                    self.raw = False
                    cmds.setAttr(self.guide_net+".rawGuide", 0)
                after_data["GuideNumber"] = cmds.getAttr(self.guide_net+".guideNumber")
                after_data["ModuleType"] = self.name
                after_data["RawGuide"] = self.raw
                after_data["BeforeData"] = befores
                for before_attr in befores:
                    node_name = cmds.listConnections(self.guide_net+"."+before_attr, source=True, destination=False) or None
                    if node_name:
                        if cmds.objExists(node_name[0]):
                            guide_data[node_name[0]] = self.get_node_data(node_name[0])
                            if build_it:
                                cmds.lockNode(self.guide_net, lock=False)
                                cmds.deleteAttr(self.guide_net+"."+before_attr)
                                cmds.lockNode(self.guide_net, lock=True)
                after_data["GuideData"] = guide_data
                cmds.setAttr(self.guide_net+".afterData", after_data, type="string")
                if build_it:
                    cmds.lockNode(self.guide_net, lock=True) #to avoid deleting this network node
                    self.serialized = True
        else: #update linked node to avoid cleanup this network if it's broken
            cmds.lockNode(self.guide_net, lock=False)
            option_ctrl = self.ar.utils.getNodeByMessage("optionCtrl")
            if option_ctrl:
                cmds.connectAttr(option_ctrl+".message", self.guide_net+".linkedNode", force=True)
            else:
                cmds.connectAttr(self.static_hook_grp+".message", self.guide_net+".linkedNode", force=True)
            cmds.lockNode(self.guide_net, lock=True)
    

    def rename_unit_conversion(self, unit_conversions=None):
        """ Rename just the new unitConverson created after the beginning of the module building.
        """
        if not unit_conversions:
            unit_conversions = cmds.ls(selection=False, type="unitConversion")
        if unit_conversions:
            if self.oldUnitConversionList:
                unit_conversions = list(set(unit_conversions)-set(self.oldUnitConversionList))
            if unit_conversions:
                self.ar.utils.nodeRenamingTreatment(unit_conversions)


    def create_world_size(self):
        """ Create a null transform and use it as worldSize reference setup to scale the main by offsetTransformMatrix.
        """
        world_size_ref = cmds.createNode("transform", name=self.guide_namespace+":Guide_Base_WorldSize_Ref")
        for attr in self.ar.data.axes:
            cmds.connectAttr(self.guide_base+".worldSize", world_size_ref+".scale"+attr)
        cmds.connectAttr(world_size_ref+".worldMatrix[0]", self.guide_base+".offsetParentMatrix", force=True)
        cmds.setAttr(world_size_ref+".visibility", False)
        cmds.setAttr(world_size_ref+".template", 1)
        cmds.parent(world_size_ref, self.ar.data.temp_grp)


    def get_parent_to_tag(self, items, return_item=None):
        """ Return the latest item from given list or the second given param.
        """
        if items:
            return items[-1]
        return return_item


    def display_annotation(self, value, *args):
        """ Get the current display setting from interface to show or hide the Annotation for this module.
        """
        if self.check_guide_integrity():
            self.annotation = self.guide_base+"_Ant"
            cmds.setAttr(self.annotation+'.visibility', value)
            cmds.setAttr(self.guide_base+'.displayAnnotation', value)


    def parse_inputted_joint_number(self, inputted):
        """ Check if we need to get the entered by UI.
            Returns None if there isn't UI.
        """
        if inputted == 0:
            if self.ar.data.ui_state:
                return cmds.intField("edit_guide_n_joints_if", query=True, value=True)
            else:
                return None
        else:
            return inputted


    def increment_joint_number(self, n):
        # set its nJoint value as n:
        cmds.setAttr(self.guide_loc+".nJoint", n)
        # parent it to the lastGuide:
        cmds.parent(self.guide_loc, self.name_guide+"_JointLoc"+str(n-1), relative=True)
        cmds.setAttr(self.guide_loc+".translateZ", 2)
        # create a joint to use like an arrowLine:
        self.line = cmds.joint(name=self.name_guide+"_JGuide"+str(n), radius=0.001)
        cmds.setAttr(self.line+".template", 1)
        #Prevent a intermidiate node to be added
        cmds.parent(self.line, self.name_guide+"_JGuide"+str(n-1), relative=True)
        #Do not maintain offset and ensure cv will be at the same place than the joint
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.scaleConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_ScC")


    def reduce_joint_number(self, joint_number, name='JointLoc', extra="", add=1, number=1):
        # re-define cvEndJoint:
        joint_loc = self.name_guide+"_"+name+str(joint_number)
        # re-parent the children guides:
        children = self.ar.utils.getGuideChildrenList(joint_loc)
        if children:
            for child in children:
                cmds.parent(child, joint_loc)
        # delete difference of nJoints:
        cmds.delete(self.name_guide+"_"+name+str(joint_number+add))
        cmds.delete(self.name_guide+"_JGuide"+extra+str(joint_number+add))
        for j in range(joint_number+number, self.current_joint_number+add):
            self.remove_attr_from_guide_net([name+str(j)])
        return joint_loc


    def re_parent_guide_end(self):
        # re-parent cvEndJoint:
        temp = cmds.listRelatives(self.guide_end_loc, parent=True)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        #Ensure to remove temp parent from the unparenting done on the end joint
        if temp:
            cmds.delete(temp)
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        temp = cmds.listRelatives(self.line_end, parent=True)
        cmds.parent(self.line_end, self.line, relative=True)
        if temp:
            cmds.delete(temp)


    def check_father_mirror(self, *args):
        """ Check all fathers and verify if there are mirror applied to father.
            Then, stop mirror for this guide or continue creating its mirror.
            Return "stopIt" if there's a father guide mirror.
        """
        self.father_flip_exists = None
        if self.check_guide_integrity():
            mirroredGuideFather = self.ar.utils.mirroredGuideFather(self.guide_base)
            if mirroredGuideFather:
                cmds.setAttr(self.guide_base+".mirrorEnable", 0)
                # get initial values from father guide base:
                fatherMirror = cmds.getAttr(mirroredGuideFather+".mirrorAxis")
                fatherMirrorName = cmds.getAttr(mirroredGuideFather+".mirrorName")
                # set values to guide base:
                cmds.setAttr(self.guide_base+".mirrorAxis", fatherMirror, type='string')
                cmds.setAttr(self.guide_base+".mirrorName", fatherMirrorName, type='string')
                # set layout as theses values:
                try:
                    cmds.optionMenu('edit_mirror_om', edit=True, value=fatherMirror, enable=False)
                    cmds.optionMenu('edit_mirror_name_om', edit=True, value=fatherMirrorName, enable=False)
                except:
                    pass
                # update flip attribute info from fatherGuide:
                self.father_flip_exists = cmds.objExists(mirroredGuideFather+".flip")
                if self.father_flip_exists:
                    fatherFlip = cmds.getAttr(mirroredGuideFather+".flip")
                    if cmds.objExists(self.guide_base+".flip"):
                        cmds.setAttr(self.guide_base+".flip", fatherFlip)
                self.create_mirror_preview()
                # returns a string 'stopIt' if there is mirrored father guide:
                return "stopIt"


    def create_mirror_preview(self):
        """ Just create the mirror preview nodes.
            It runs recursively.
        """
        selection = cmds.ls(selection=True)
        # re-declaring guideMirror and previewMirror groups:
        preview_mirror_grp = self.guide_base[:self.guide_base.find(":")]+'_MirrorGrp'
        if cmds.objExists(preview_mirror_grp):
            cmds.delete(preview_mirror_grp)
        # get children, verifying if there are children guides:
        guide_children = self.ar.utils.getGuideChildrenList(self.guide_base)
        self.mirror_axis = cmds.getAttr(self.guide_base+".mirrorAxis")
        if self.mirror_axis != 'off':
            if not cmds.objExists(self.ar.data.guide_mirror_grp):
                hidden = not self.ar.data.display_temp_grp #invert to apply
                self.ar.data.guide_mirror_grp = cmds.createNode('transform', name=self.ar.data.guide_mirror_grp)
                cmds.addAttr(self.ar.data.guide_mirror_grp, longName="selectionChanges", defaultValue=0, attributeType="byte")
                cmds.setAttr(self.ar.data.guide_mirror_grp+".template", 1)
                cmds.setAttr(self.ar.data.guide_mirror_grp+".hiddenInOutliner", hidden)
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
                    cmds.setAttr(self.ar.data.guide_mirror_grp+"."+attr, lock=True, keyable=False)
            
            if not cmds.objExists(preview_mirror_grp):
                if guide_children:
                    guide_father_names = []
                    for guide_child in guide_children:
                        guide_father_names.append(cmds.listRelatives(guide_child, parent=True))
                        # unparent this child guide in order to make the mirror and after return it to the parent:
                        cmds.parent(guide_child, world=True)
                        # set child guide as not mirrorable:
                        cmds.setAttr(guide_child+".mirrorEnable", 0)
                        # set values to guide base:
                        cmds.setAttr(guide_child+".mirrorAxis", self.mirror_axis, type='string')
                        cmds.setAttr(guide_child+".mirrorName", cmds.getAttr(self.guide_base+".mirrorName"), type='string') #fatherMirrorName
                        for instance in self.ar.data.guide_instances:
                            if cmds.objExists(instance.guide_base):
                                if cmds.getAttr(instance.guide_base+".moduleInstanceInfo") == cmds.getAttr(guide_child+".moduleInstanceInfo"):
                                    instance.create_mirror_preview()
                
                # duplicating the moduleGuide
                duplicated = cmds.duplicate(self.guide_base, returnRootsOnly=True)[0]
                # renaming  and reShaping all its children nodes:
                for dup in cmds.listRelatives(duplicated, allDescendents=True, fullPath=True) or []:
                    if cmds.objExists(dup):
                        if "_RadiusCtrl" in dup or "_Ant" in dup:
                            cmds.delete(dup)
                        else:
                            if cmds.objectType(dup) == 'transform' or cmds.objectType(dup) == 'joint':
                                # rename duplicated node:
                                dup_renamed = cmds.rename(dup, self.guide_base[:self.guide_base.find(":")]+'_'+dup[dup.rfind("|")+1:]+'_Mirror')
                                original_guide = self.guide_base[:self.guide_base.find(":")+1]+dup[dup.rfind("|")+1:]
                                # unlock and unhide all attributes and connect original guide node transformations to the mirror guide node:
                                for attr in self.ar.data.transform_attrs:
                                    cmds.setAttr(dup_renamed+"."+attr, lock=False, keyable=True)
                                    cmds.connectAttr(original_guide+'.'+attr, dup_renamed+'.'+attr, force=True)
                                
                                # rebuild the shape as a nurbsSphere:
                                if cmds.objectType(dup_renamed) == 'transform':
                                    # make this previewMirrorGuide as not skinable from dpAR_UI:
                                    self.ar.utils.addCustomAttr([dup_renamed], self.ar.skin.ignoreSkinningAttr)
                                    children_shapes = cmds.listRelatives(dup_renamed, shapes=True, children=True)
                                    if children_shapes:
                                        cmds.delete(children_shapes)
                                        new_sphere = cmds.sphere(name=dup_renamed+"Sphere", radius=0.1, constructionHistory=True)
                                        cmds.parent(cmds.listRelatives(new_sphere, shapes=True, children=True)[0], dup_renamed, shape=True, relative=True) #newSphereShape
                                        cmds.delete(new_sphere[0]) #transform
                                        sz_md = cmds.createNode("multiplyDivide", name=dup_renamed+"_MD")
                                        sz_clp = cmds.createNode("clamp", name=dup_renamed+"_Clp")
                                        cmds.connectAttr(self.guide_base+".shapeSize", sz_md+".input1X", force=True)
                                        cmds.connectAttr(sz_md+".outputX", sz_clp+".inputR", force=True)
                                        cmds.connectAttr(sz_clp+".outputR", new_sphere[1]+".radius", force=True)
                                        cmds.setAttr(sz_md+".input2X", 0.1)
                                        cmds.setAttr(sz_clp+".minR", 0.001)
                                        cmds.setAttr(sz_clp+".maxR", 1000)
                                        cmds.rename(new_sphere[1], dup_renamed+"_MNS")
                            elif cmds.objectType(dup) != 'nurbsCurve':
                                cmds.delete(dup)
                
                # renaming the previewMirrorGuide:
                preview_mirror_guide = cmds.rename(duplicated, self.guide_base.replace(":", "_")+'_Mirror')
                cmds.deleteAttr(preview_mirror_guide+".guideBase")
                cmds.delete(cmds.listRelatives(preview_mirror_guide, shapes=True, type="nurbsCurve"))
                self.ar.utils.unlockAttr([preview_mirror_guide])
                
                # clean up old module attributes in order to avoid numbering issue:
                if cmds.objExists(preview_mirror_guide+".customName"):
                    custom_name_mirror = "_Mirror"
                    current_custom_name = cmds.getAttr(preview_mirror_guide+".customName")
                    if current_custom_name:
                        custom_name_mirror = current_custom_name+"_Mirror"
                    cmds.setAttr(preview_mirror_guide+".customName", custom_name_mirror, type="string")
                
                # create a decomposeMatrix node in order to get the worldSpace transformations (like using xform):
                preview_mirror_dm = cmds.createNode('decomposeMatrix', name=preview_mirror_guide+"_dm")
                cmds.connectAttr(self.guide_base+'.worldMatrix', preview_mirror_dm+'.inputMatrix', force=True)
                
                # connect original guide base decomposeMatrix node output transformations to the mirror guide base node:
                for axis in self.ar.data.axes:
                    cmds.connectAttr(preview_mirror_dm+'.outputTranslate'+axis, preview_mirror_guide+'.translate'+axis, force=True)
                    cmds.connectAttr(preview_mirror_dm+'.outputRotate'+axis, preview_mirror_guide+'.rotate'+axis, force=True)
                    cmds.connectAttr(preview_mirror_dm+'.outputScale'+axis, preview_mirror_guide+'.scale'+axis, force=True)
                
                # analysis if there were children guides for this guide in order to re-parent them:
                if guide_children:
                    for p, guide_child in enumerate(guide_children):
                        # re-parent this child guide to the correct guideFatherName:
                        cmds.parent(guide_child, guide_father_names[p])
                
                # create previewMirror group:
                preview_mirror_grp = cmds.createNode('transform', name=preview_mirror_grp)
                cmds.parent(preview_mirror_guide, preview_mirror_grp, absolute=True)
                # parent the previewMirror group to the guideMirror group:
                cmds.parent(preview_mirror_grp, self.ar.data.guide_mirror_grp, relative=True)
                
                # add attributes to be read as mirror guide when re-creating this module:
                cmds.addAttr(preview_mirror_grp, longName='guideBaseMirror', attributeType='bool')
                cmds.setAttr(preview_mirror_grp+".guideBaseMirror", 1)
            
            # reset all scale values to 1:
            cmds.setAttr(preview_mirror_grp+'.scaleX', 1)
            cmds.setAttr(preview_mirror_grp+'.scaleY', 1)
            cmds.setAttr(preview_mirror_grp+'.scaleZ', 1)
            # set a negative value to the scale mirror axis:
            for axis in self.mirror_axis:
                cmds.setAttr(preview_mirror_grp+'.scale'+axis, -1)
        cmds.select(selection)


    def change_mirror(self, item, *args):
        """ This function receives the mirror menu item and set it as a string in the guide base (main).
            Also, call the builder of the preview mirror (for the viewport).
        """
        if self.check_guide_integrity():
            # check if the father guide is in X=0 in order to permit mirror:
            if not self.check_father_mirror(): #stopMirrorOperation
                # loading Maya matrix node (for mirror porpuses)
                loaded_matrix_plugin = self.ar.utils.checkLoadedPlugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
                if loaded_matrix_plugin:
                    self.mirror_axis = item
                    cmds.setAttr(self.guide_base+".mirrorAxis", self.mirror_axis, type='string')
                    self.create_mirror_preview()
    
    
    def change_mirror_name(self, item, *args):
        """ This function receives the mirror menu name item and set it as a string in the guide base (main).
        """
        if self.check_guide_integrity():
            cmds.setAttr(self.guide_base+".mirrorName", item, type='string')


    def change_deformed_by(self, item, *args):
        """ This function receives the deformedBy menu name item and set it as a integer value in the guide base (main).
        """
        if self.check_guide_integrity():
            cmds.setAttr(self.guide_base+".deformedBy", int(item[0]))


    def change_articulation(self, value, *args):
        """ Set the attribute value for articulation.
        """
        cmds.setAttr(self.guide_base+".articulation", value)
        if self.ar.data.ui_state and 'corrective' in cmds.listAttr(self.guide_base):
            self.ar.guide_ui.change_corrective(self, value)


    def change_radius_size(self, value, *args):
        """ Set the attribute value for the viewport radius size.
        """
        cmds.setAttr(self.radius_ctrl+".translateX", value)


    def create_end_joint(self, name, match_node=None, tx=None, ty=None, tz=None):
        if not match_node:
            match_node = self.guide_end_loc
        end_joint = cmds.joint(name=name+"_"+self.ar.data.joint_end_attr, scaleCompensate=False, radius=0.5)
        self.ar.utils.addJointEndAttr([end_joint])
        cmds.matchTransform(end_joint, match_node, position=True, rotation=True)
        for attr, value in zip(['tx', 'ty', 'tz'], [tx, ty, tz]):
            if value:
                cmds.setAttr(f"{end_joint}.{attr}", value)
        return end_joint


    # Getters:
    #
    def get_guide_attr(self, attr):
        if attr in cmds.listAttr(self.guide_base):
            return cmds.getAttr(self.guide_base+"."+attr)
    
    
    # Setters:
    #
    def set_guide_attr(self, attr, value, is_string=False, *args):
        """ Set guide_base attribute value.
        """
        if is_string:
            cmds.setAttr(f"{self.guide_base}.{attr}", value, type='string')
        else:
            cmds.setAttr(f"{self.guide_base}.{attr}", value)
