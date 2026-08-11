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
        

    def get_namespace_for_it(self, userGuideName=None):
        self.userGuideName = userGuideName
        if not self.userGuideName:
            self.userGuideName = self.ar.data.base_name+str(self.ar.utils.findLastNumber())
        self.rigType = "biped"
        # defining namespace:
        self.guide_namespace = self.name+"__"+self.userGuideName
        # defining guideNamespace:
        cmds.namespace(setNamespace=":")
        self.name_guide = self.guide_namespace+":Guide"
        self.guide_base = self.name_guide+"_Base"
        self.radius_ctrl = self.guide_base+"_RadiusCtrl"
        self.annotation = self.guide_base+"_Ant"


    def build_raw_guide(self, userGuideName=None, *args):
        #
        #
        #self.number = number
        #
        # WIP TODO: get new userGuideName by findLastNumber in utils
        #

        self.get_namespace_for_it(userGuideName)
        # starting module:
        if not cmds.namespace(exists=self.guide_namespace):
            cmds.namespace(add=self.guide_namespace)
            # create GUIDE for this module:
            self.create_guide()
        
        self.load_raw_guide()
        return self.guide_base
    

    def load_raw_guide(self, userGuideName=None):
        if userGuideName:
            self.userGuideName = userGuideName
        if self.ar.data.ui_state:
            # create the Module layout in the mainUI - modulesLayoutA:        
            self.create_module_layout()
        # update module instance info:
        self.update_module_instance_info()
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
            layout_name = self.userGuideName
        self.module_layout_name = self.ar.data.lang[self.title]+" - "+layout_name
        if cmds.columnLayout("rig_guides_inst_cl", query=True, exists=True):
            self.module_fl = cmds.frameLayout(self.module_layout_name+"_fl" , label=self.module_layout_name, collapsable=True, collapse=False, parent="rig_guides_inst_cl")
            self.top_cl = cmds.columnLayout(self.module_layout_name+"_top_cl", adjustableColumn=True, parent=self.module_fl)
        # rig_guides_inst_cl -> here we have just the column layouts to be populated by modules.
    
    
    def create_guide_base(self):
        """ Create the node elements to Guide module in the scene, like guides, attributes, etc...
        """
        self.ar.opt.check_use_default_render_layer()
        # create guide base (main guide node):
        self.guide_base, self.radius_ctrl = self.ar.ctrls.cvBaseGuide(self.guide_base, r=2)
        self.add_guide_base_attr()
        self.create_guide_annotation()
        # setup worldSize
        self.ar.ctrls.getDPARTempGrp()
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
            cmds.setAttr(self.guide_base+"."+guide_color_attr, self.ar.ctrls.colorList[0][c])


    def create_guide_annotation(self):
        # create annotation to this module:
        self.annotation = cmds.annotate(self.guide_base, tx=self.guide_base, point=(0,2,0))
        self.annotation = cmds.listRelatives(self.annotation, parent=True)[0]
        self.annotation = cmds.rename(self.annotation, self.guide_base+"_Ant")
        cmds.parent(self.annotation, self.guide_base)
        cmds.setAttr(self.annotation+'.text', self.guide_base[self.guide_base.find("__")+2:self.guide_base.rfind(":")], type='string')
        cmds.setAttr(self.annotation+'.template', 1)
        cmds.connectAttr(self.radius_ctrl+".translateX", self.annotation+".translateY", force=True)

    
    def update_module_instance_info(self):
        """ Just update modeuleInstanceInfo attribute in the guideNode transform.
        """
        cmds.setAttr(self.guide_base+".moduleInstanceInfo", self, type='string')
    
    
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
        """ Edit the userGuideName to set the user custom name from module UI.
        """
        # verify integrity of the guideModule:
        if self.check_guide_integrity():
            if check_text:
                inputted_text = check_text
            else:
                try:
                    # get the entered text:
                    inputted_text = cmds.textField(self.userName, query=True, text=True)
                except:
                    inputted_text = ""
            inputted_text = inputted_text.replace(" ", "_")
            # call utils to return the normalized text:
            self.custom_name = self.ar.utils.normalizeText(inputted_text, prefixMax=30)
            # check if there is another rigged module using the same customName:
            if self.custom_name == "":
                try:
                    cmds.textField(self.userName, edit=True, text="")
                except:
                    pass
                cmds.setAttr(self.guide_base+".customName", "", type='string')
                self.userGuideName = self.guide_namespace.split("__")[-1]
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
                    cmds.textField(self.userName, edit=True, text=self.custom_name)
                    cmds.frameLayout(self.module_fl, edit=True, label=self.ar.data.lang[self.title]+" - "+self.custom_name)
                except:
                    pass
                cmds.setAttr(self.guide_base+".customName", self.custom_name, type='string')
                cmds.setAttr(self.annotation+".text", self.custom_name, type='string')
                if self.guide_net:
                    cmds.setAttr(self.guide_net+".guideName", self.custom_name, type='string')
                # set userGuideName:
                self.userGuideName = self.custom_name
                

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
        net = self.correction_manager.createCorrectionManager([first_node, second_node], name=net_name, correctType=self.correction_manager.angleName, toRivet=False, from_ui=False)
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
            net = self.correction_manager.changeName(legs[0])+"_Net"
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
                    jcr_ctrl, jcr_grp = self.ar.ctrls.createCorrectiveJointCtrl(corrective_joints[i], corrective_nets[i], radius=self.radius*0.2)
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
            if self.ar.data.ui_state:
                main_number = cmds.intField(self.nMainCtrlIF, query=True, value=True)
            else:
                return
        else:
            main_number = inputted_number
        # limit range
        if main_number >= self.currentNJoints:
            main_number = self.currentNJoints - 1
            if main_number == 0:
                main_number = 1
                cmds.checkBox(self.mainCtrlsCB, edit=True, editable=False)
            cmds.intField(self.nMainCtrlIF, edit=True, value=main_number)
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


    def enable_main_ctrls(self, value):
        """ Just enable or disable the main controllers int field UI.
        """
        cmds.intField(self.nMainCtrlIF, edit=True, editable=value)
        cmds.checkBox(self.mainCtrlsCB, edit=True, editable=True)


    def set_main_ctrls(self, value, *args):
        """ Just store the main controllers checkBox value and enable the int field.
        """
        cmds.setAttr(self.guide_base+".mainControls", value)
        self.enable_main_ctrls(value)


    def add_fk_main_ctrls(self, side, ctrlList):
        """ Implement the fk main controllers.
        """
        main_ctrls = []
        # getting and calculating values
        total_to_add_main = 1
        self.n_main = cmds.getAttr(self.base+".nMain")
        if self.n_main > 1:
            total_to_add_main = int(self.nJoints/self.n_main)
        # run throgh the chain
        for m in range(0, self.n_main):
            start = m*total_to_add_main
            end = (m+1)*total_to_add_main
            if m == self.n_main-1:
                end = self.nJoints
            for n in range(start, end):
                current_ctrl = ctrlList[n]
                current_ctrl_zero = cmds.listRelatives(current_ctrl, parent=True)[0]
                if n == start:
                    # create a main controller
                    main_ctrl = self.ar.ctrls.cvControl("id_096_FkLineMain", side+self.userGuideName+"_%02d_Main_Fk_Ctrl"%(n), r=self.radius*1.2, d=self.curve_degree, guideSource=self.name_guide+"_Base", parentTag=self.get_parent_to_tag(main_ctrls))
                    main_ctrls.append(main_ctrl)
                    self.ar.ctrls.colorShape([main_ctrl], "cyan")
                    cmds.addAttr(main_ctrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                    # position
                    cmds.parent(main_ctrl, current_ctrl_zero)
                    cmds.makeIdentity(main_ctrl, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(current_ctrl, main_ctrl)
                    # intensity utilities
                    r_intensity_md = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_R_Main_MD")
                    self.to_ids.append(r_intensity_md)
                    for axis in self.ar.data.axis:
                        cmds.connectAttr(main_ctrl+".rotate"+axis, r_intensity_md+".input1"+axis, force=True)
                        cmds.connectAttr(main_ctrl+"."+self.ar.data.lang['c049_intensity'], r_intensity_md+".input2"+axis, force=True)
                else:
                    # offseting sub controllers
                    offset_grp = cmds.group(name=current_ctrl+"_Offset_Grp", empty=True)
                    cmds.parent(offset_grp, current_ctrl_zero)
                    cmds.makeIdentity(offset_grp, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(current_ctrl, offset_grp)
                    for axis in self.ar.data.axis:
                        cmds.connectAttr(r_intensity_md+".output"+axis, offset_grp+".rotate"+axis, force=True)
                # display sub controllers shapes
                self.ar.ctrls.setSubControlDisplay(main_ctrl, current_ctrl, 0)
    

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
                duplicated = cmds.duplicate(self.guide_base, name=side+self.userGuideName+'_Guide_Base')[0]
                for item in cmds.listRelatives(duplicated, allDescendents=True):
                    cmds.rename(item, side+self.userGuideName+"_"+item)
                self.mirror_grp = cmds.group(name="Guide_Base_Grp", empty=True)
                cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirror_grp, absolute=True)
                # re-rename grp:
                cmds.rename(self.mirror_grp, side+self.userGuideName+'_'+self.mirror_grp)
                # do a group mirror with negative scaling:
                if s == 1:
                    without_flip = False
                    if cmds.objExists(self.guide_base+".flip"):
                        if cmds.getAttr(self.guide_base+".flip") == 0:
                            without_flip = True
                    if without_flip:
                        for axis in self.mirror_axis:
                            got_value = cmds.getAttr(side+self.userGuideName+"_Guide_Base.translate"+axis)
                            fliped_value = got_value*(-2)
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirror_grp+'.translate'+axis, fliped_value)
                    else:
                        for axis in self.mirror_axis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirror_grp+'.scale'+axis, -1)
            # joint labelling:
            self.joint_label_add = 1
        else: # if not mirror:
            duplicated = cmds.duplicate(self.guide_base, name=self.userGuideName+'_Guide_Base')[0]
            for item in cmds.listRelatives(duplicated, allDescendents=True):
                cmds.rename(item, self.userGuideName+"_"+item)
            self.mirror_grp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
            # re-rename grp:
            cmds.rename(self.mirror_grp, self.userGuideName+'_'+self.mirror_grp)
            # joint labelling:
            self.joint_label_add = 0
        # store the number of this guide by module type
        self.dpar_count = self.ar.utils.findModuleLastNumber(self.name, "moduleType", True)


    def rig_me(self, *args):
        """ The fun part of the module, just read the values from editModuleLayout and create the rig for this guide.
        """
        self.ar.utils.close_ui(self.ar.data.plus_info_win_name)
        self.ar.utils.close_ui(self.ar.data.color_override_win_name)
        # verify integrity of the guideModule:
        if self.check_guide_integrity():
            self.to_ids = []
            self.oldUnitConversionList = cmds.ls(selection=False, type="unitConversion")
            try:
                # clear selected module layout:
                self.clearSelectedModuleLayout()
            except:
                pass

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
                self.userGuideName = self.custom_name

            if self.ar.data.prefix:
                self.userGuideName = self.ar.data.prefix + self.userGuideName
            cmds.select(clear=True)
            self.get_mirror_sides()
            self.articulation = self.get_guide_attr("articulation")
            self.corrective = self.get_guide_attr("corrective")
            self.flip = self.get_guide_attr("flip")
    

    def create_hook_setup(self, side, ctrlList, scalableList=None, staticList=None, *args):
        """ Generate the hook setup to find lists of controllers, scalable and static groups.
            Add message attributes to map hooked groups for the rigged module.
        """
        # create a masterModuleGrp to be checked if this rig exists:
        self.ctrl_hook_grp = cmds.group(ctrlList, name=side+self.userGuideName+"_Control_Grp")
        self.scalable_hook_grp = cmds.group(empty=True, name=side+self.userGuideName+"_Scalable_Grp")
        self.static_hook_grp = cmds.group(self.ctrl_hook_grp, self.scalable_hook_grp, name=side+self.userGuideName+"_Static_Grp")
        if staticList:
            cmds.parent(staticList, self.static_hook_grp)
        if scalableList:
            cmds.parent(scalableList, self.scalable_hook_grp)
        self.ar.custom_attr.addAttr(0, [self.ctrl_hook_grp, self.scalable_hook_grp, self.static_hook_grp]) #dpID
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
        self.ar.custom_attr.addAttr(0, [self.guide_net])[0] #dpID
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
        cmds.setAttr(self.guide_net+".guideName", self.userGuideName, type="string")
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
                        if "guideSource" in cmds.listAttr(fathers[0]):
                            attr_data["FatherNode"] = cmds.getAttr(fathers[0]+".guideSource")
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
        for attr in self.ar.data.axis:
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


    # Getters:
    #
    def get_guide_attr(self, attr):
        if attr in cmds.listAttr(self.guide_base):
            return cmds.getAttr(self.guide_base+"."+attr)
    
    
    # Setters:
    #
    def set_articulation(self, value):
        self.articulation = value
        cmds.setAttr(self.guide_base+".articulation", value)
    