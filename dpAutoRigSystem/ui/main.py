#import libraries
from maya import cmds
from functools import partial


class UI(object):
    def __init__(self, dpUIinst):
        self.ar = dpUIinst
    
    
    def create_ui(self):
        """ Start the main UI, menus and layouts for dpAutoRigSystem through workspaceControl.
        """
        if cmds.workspaceControl("dpAutoRigSystemWC", query=True, exists=True):
            cmds.workspaceControl("dpAutoRigSystemWC", edit=True, close=True)
        self.labelText = "dpAutoRigSystem"
        self.labelText += " - "+self.ar.dpARVersion
        if self.ar.dev:
            self.labelText += " ~ dev"
        uiCallScript = "import dpAutoRigSystem; from dpAutoRigSystem import dpAutoRig; ar = dpAutoRig.Start("+str(self.ar.dev)+"); ar.main_ui.show_ui();"
        cmds.workspaceControl("dpAutoRigSystemWC", 
                            retain=False,
                            floating=False,
                            minimumWidth=400,
                            initialWidth=400,
                            minimumHeight=515,
                            initialHeight=715,
                            widthProperty="preferred",
                            visible=True,
                            loadImmediately=True,
                            label=self.labelText,
                            uiScript=uiCallScript)
    
    
    def show_ui(self):
        """ Call mainUI method and the following instructions to check optionVars, refresh UI elements, start the scriptJobs and close loading window.
        """
        startSelList = cmds.ls(selection=True)
        self.main_ui()
        self.ar.autoCheckOptionVar("dpAutoRigAutoCheckUpdate", "dpAutoRigLastDateAutoCheckUpdate", "update")
        self.ar.autoCheckOptionVar("dpAutoRigAgreeTermsCond", "dpAutoRigLastDateAgreeTermsCond", "terms")
        self.ar.refreshMainUI()
#        self.ar.startScriptJobs()
#        self.ar.utils.closeUI("dpar_load_win")
#        cmds.select(startSelList)
#        print("dpAutoRigSystem "+self.ar.lang['i346_loadedSuccess'])


    def menu_change(self, name, item, *args):
        if name == "language":
            self.reload_ui(self.ar.data.language_option_var, item)
        elif name == "controller_preset":
            self.reload_ui(self.ar.data.controller_option_var, item)
        elif name == "validator_preset":
            
            # TODO
            # TODO add pipeline validators to the first element in the list
            print("validator here hhehehe presetssss", name, item)
            self.ar.setValidatorPreset()
            print("done test")
            #


    def create_option_menu(self, name, parent_layout, items, option_var, menu_label=''):
        menu_name = f"{name}_option_menu"
        cmds.optionMenu(menu_name, label=menu_label, changeCommand=self.ar.changeOptionDegree, parent=parent_layout)
        if option_var:
            last_item = self.ar.opt.check_last_option_var(option_var, items[0], items)
            self.ar.data.degree_option = int(last_item[0])
        for deg_opt in items:
            cmds.menuItem(label=deg_opt, parent=menu_name)
        cmds.optionMenu(menu_name, edit=True, value=last_item)


    def create_radio_menu(self, name, parent_menu, folder, default, option_var=None):
        menu_name = f"{name}_menu"
        collection_name = f"{name}_rbc"
        cmds.menuItem(menu_name, label=name.capitalize().replace("_", " "), parent=parent_menu, subMenu=True)
        cmds.radioMenuItemCollection(collection_name)
        
        #founds, lang_data = self.ar.getJsonFileInfo(folder)
        founds, content = self.ar.config.get_json_file_content(folder)
        print("founds =", founds)
        if founds:
            for item in founds:
                cmds.menuItem(f"{item}_mi", label=item, radioButton=False, collection=collection_name, command=partial(self.menu_change, name, item), parent=menu_name)
            last_item = founds[0]
            if option_var:
                last_item = self.ar.opt.check_last_option_var(option_var, default, founds)
            cmds.menuItem(f"{last_item}_mi", edit=True, radioButton=True, collection=collection_name)
        # else:
        #     print("Error: Cannot load json language files!\n")
        #     return
        return founds, content


    def create_settings_menu(self):
        cmds.menu('settings_menu', label='Settings', parent='main_menu_bar')
        self.create_radio_menu("language", "settings_menu", self.ar.data.language_folder, self.ar.data.language_default, self.ar.data.language_option_var)
        self.ar.ctrlPresetList, self.ar.ctrlPresetDic = self.create_radio_menu("controller_preset", "settings_menu", self.ar.data.curves_presets_folder, self.ar.data.controller_default, self.ar.data.controller_option_var)
        self.ar.validatorPresetList, self.ar.validatorPresetDic = self.create_radio_menu("validator_preset", "settings_menu", self.ar.data.validator_presets_folder, self.ar.data.validator_default, self.ar.data.validator_option_var)
        self.ar.ctrlPreset = self.ar.ctrlPresetDic[self.ar.ctrlPresetList[0]]
        


        # if self.ar.pipeliner.pipeData['presetsPath']:
        #     self.loadPipelineValidatorPresets()


    def create_create_menu(self):
        # create menu:
        cmds.menu('create_menu', label='Create', parent='main_menu_bar')
        cmds.menuItem('translator_mi', label='Translator', command=self.ar.translator, parent='create_menu')
        cmds.menuItem('pipeliner_mi', label='Pipeliner', command=self.ar.config.open_pipeliner, parent='create_menu')
        
        cmds.menuItem('create_control_preset_mi', label='Controllers Preset', command=partial(self.ar.config.create_preset, "controls", self.ar.data.curves_presets_folder, True), parent='create_menu')
        cmds.menuItem('create_validator_preset_mi', label='Validator Preset', command=partial(self.ar.config.create_preset, "validator", self.ar.data.validator_presets_folder, False), parent='create_menu')



    def create_window_menu(self):
        # window menu:
        cmds.menu('window_menu', label='Window', parent='main_menu_bar')
        cmds.menuItem('dev_mode_mi', label='Dev mode', checkBox=self.ar.dev, command=self.reload_dev_mode_ui, parent='window_menu')
        cmds.menuItem('reload_ui_mi', label='Reload UI', command=self.reload_ui, parent='window_menu')
        cmds.menuItem('quit_mi', label='Quit', command=self.deleteExistWindow, parent='window_menu')



    def create_help_menu(self):
        # help menu:
        cmds.menu('help_menu', label='Help', helpMenu=True, parent='main_menu_bar')
        cmds.menuItem('about_mi"', label='About', command=partial(self.ar.logger.infoWin, 'm015_about', 'i006_aboutDesc', self.ar.dpARVersion, 'center', 305, 250), parent='help_menu')
        cmds.menuItem('author_mi', label='Author', command=partial(self.ar.logger.infoWin, 'm016_author', 'i007_authorDesc', None, 'center', 305, 250), parent='help_menu')
        cmds.menuItem('collaborators_mi', label='Collaborators', command=partial(self.ar.logger.infoWin, 'i165_collaborators', 'i166_collabDesc', "\n\n"+self.ar.lang['_collaborators'], 'center', 305, 250), parent='help_menu')
        cmds.menuItem('donate_mi', label='Donate', command=partial(self.ar.donateWin), parent='help_menu')
        cmds.menuItem('idiom_mi', label='Idioms', command=partial(self.ar.logger.infoWin, 'm009_idioms', 'i012_idiomsDesc', None, 'center', 305, 250), parent='help_menu')
        cmds.menuItem('terms_mi', label='Terms and Conditions', command=self.ar.checkTermsAndCond, parent='help_menu')
        cmds.menuItem('update_mi', label='Update', command=partial(self.ar.checkForUpdate, True), parent='help_menu')
        cmds.menuItem('help_mi', label='Wiki...', command=partial(self.ar.utils.visitWebSite, self.ar.data.wiki_url), parent='help_menu')


    def create_dev_menu(self):
        cmds.menu('dev_menu', label='Dev', parent='main_menu_bar')
        cmds.menuItem('verbose_mi', label='Verbose', checkBox=self.ar.verbose, command=self.change_verbose)


    def create_menu(self):
        cmds.menuBarLayout("main_menu_bar", parent="dpAutoRigSystemWC")
        self.create_settings_menu()
        self.create_create_menu()
        self.create_window_menu()
        self.create_help_menu()
        if self.ar.dev:
            self.create_dev_menu()
            


    def create_rigging_layout(self):
        
        cmds.formLayout('rigging_tab', numberOfDivisions=100, parent='main_tab')
        #colTopLefA - columnLayout:
        cmds.columnLayout('rig_header_cl', adjustableColumn=True, height=20, parent='rigging_tab')
        cmds.text('guides_txt', label=self.ar.lang['i000_guides'], font="boldLabelFont", width=150, align='center', parent='rig_header_cl')
#        cmds.setParent('rigging_tab')
        #colTopRightA - columnLayout:
        cmds.rowColumnLayout('rig_header_rcl', numberOfColumns=2, adjustableColumn=1, columnWidth=(120, 50), parent='rigging_tab')
        cmds.text('modules_txt', label=self.ar.lang['i001_modules'], font="boldLabelFont", width=150, align='center', parent='rig_header_rcl')
        cmds.iconTextButton("tri_collapse_guides_itb", image=self.ar.data.icon['triDown'], annotation=self.ar.lang['i348_triangleIconAnn'], command=partial(self.ar.collapseAllFL, "tri_collapse_guides_itb", 0), width=17, height=17, style='iconOnly', align='right', parent='rig_header_rcl')
#        cmds.setParent('rigging_tab')
        #colMiddleLeftA - scrollLayout - guidesLayout:
        cmds.scrollLayout("rig_guides_start_sl", width=160, parent='rigging_tab')
        cmds.columnLayout("rig_guides_start_cl", adjustableColumn=True, width=140, rowSpacing=3, parent='rig_guides_start_sl')
        
        # it will be populated here by guides of modules and scripts...
        cmds.text('standard_txt', label=self.ar.lang['i030_standard'], font="obliqueLabelFont", align='left', parent='rig_guides_start_cl')
        self.ar.guideModuleList = self.ar.startGuideModules(self.ar.data.standard_folder, "start", "rig_guides_start_cl")
        #print("self.ar.guideModuleList = ",self.ar.guideModuleList)
        
        cmds.separator(style='doubleDash', height=10, parent='rig_guides_start_cl')
        cmds.text('integrated_txt', label=self.ar.lang['i031_integrated'], font="obliqueLabelFont", align='left', parent='rig_guides_start_cl')
        self.ar.startGuideModules(self.ar.data.integrated_folder, "start", "rig_guides_start_cl")

#        cmds.setParent('rigging_tab')
        #colMiddleRightA - scrollLayout - modulesLayout:
        cmds.scrollLayout("rig_guides_inst_sl", width=120, parent='rigging_tab')
        cmds.columnLayout("rig_guides_inst_cl", adjustableColumn=True, width=120, parent='rig_guides_inst_sl')
        # here will be populated by created instances of modules...
        # after footerRigging we will call the function to populate here, because it edits the footerRiggingText
#        cmds.setParent('rigging_tab')

        #editSelectedModuleLayoutA - frameLayout:
        cmds.frameLayout('edit_selected_module_fl', label=self.ar.lang['i011_editSelected']+" "+self.ar.lang['i143_module'], collapsable=True, collapse=self.ar.data.collapse_edit_sel_mod, parent='rigging_tab')
        cmds.columnLayout('selected_module_layout', adjustableColumn=True, parent='edit_selected_module_fl')
        
        #optionsMainFL - frameLayout:
        cmds.frameLayout('rig_options_fl', label=self.ar.lang['i002_options'], collapsable=True, collapse=True, parent='rigging_tab')
        self.rig_options_layout = cmds.columnLayout('rig_options_layout', adjustableColumn=True, columnOffset=('left', 5), parent='rig_options_fl')
        cmds.rowColumnLayout('rig_prefix_rcl', numberOfColumns=2, columnWidth=[(1, 40), (2, 200)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent='rig_options_layout')
        cmds.textField('rig_prefix_tf', text="", parent= 'rig_prefix_rcl', changeCommand=self.ar.setPrefix)
        cmds.text('rig_prefix_txt', align='left', label=self.ar.lang['i003_prefix'], parent='rig_prefix_rcl')
#        cmds.setParent('rig_options_layout')
        cmds.checkBox('rig_display_joints_cb', label=self.ar.lang['i009_displayJointsCB'], align='left', value=1, parent='rig_options_layout')
        cmds.checkBox('rig_hide_guide_grp_cb', label=self.ar.lang['i183_hideGuideGrp'], align='left', value=1, changeCommand=self.ar.displayGuideGrp, parent='rig_options_layout')
        cmds.checkBox('rig_integrate_cb', label=self.ar.lang['i010_integrateCB'], align='left', value=1, parent='rig_options_layout')
        cmds.checkBox('rig_default_render_layer_cb', label=self.ar.lang['i004_defaultRL'], align='left', value=1, parent='rig_options_layout')
        cmds.checkBox('rig_colorize_ctrl_cb', label=self.ar.lang['i065_colorizeCtrl'], align='left', value=1, parent='rig_options_layout')
        cmds.checkBox('rig_add_attr_cb', label=self.ar.lang['i066_addAttr'], align='left', value=1, parent='rig_options_layout')
        cmds.rowColumnLayout('rig_degree_rcl', numberOfColumns=2, columnWidth=[(1, 100), (2, 250)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent='rig_options_layout')
        
        # option Degree:
        self.create_option_menu('rig_degree', 'rig_degree_rcl', ['0 - Preset', '1 - Linear', '3 - Cubic'], self.ar.data.degree_option_var)
        cmds.text('option_degree_txt', label=self.ar.lang['i128_optionDegree'], parent='rig_degree_rcl')

#        cmds.setParent('rigging_tab')
        #footerRigging - columnLayout:
        cmds.columnLayout('rig_footer_cl', adjustableColumn=True, parent='rigging_tab')
        cmds.button('rig_all_bt', label=self.ar.lang['i020_rigAll'], annotation=self.ar.lang['i021_rigAllDesc'], backgroundColor=(0.6, 1.0, 0.6), command=self.ar.rigAll, parent='rig_footer_cl')
        cmds.separator(style='none', height=5, parent='rig_footer_cl')
        # this text will be actualized by the number of module instances created in the scene...
        cmds.text('rig_footer_txt', label="# "+self.ar.lang['i005_footerRigging'], align='center', parent='rig_footer_cl')
#        cmds.setParent(self.main_layout)
        # edit formLayout in order to get a good scalable window:
        
        cmds.formLayout('rigging_tab', edit=True,
                        attachForm=[
                                    ('rig_header_cl', 'top', 7),
                                    ('rig_header_cl', 'left', 5),
                                    ('rig_header_rcl', 'top', 5),
                                    ('rig_header_rcl', 'right', 5),
                                    ('rig_guides_start_sl', 'left', 5),
                                    ('rig_guides_inst_sl', 'right', 5),
                                    ('rig_options_fl', 'left', 5),
                                    ('rig_options_fl', 'right', 5),
                                    ('edit_selected_module_fl', 'left', 5),
                                    ('edit_selected_module_fl', 'right', 5),
                                    ('rig_footer_cl', 'left', 5),
                                    ('rig_footer_cl', 'bottom', 5),
                                    ('rig_footer_cl', 'right', 5)
                                    ],
                        attachControl=[ 
                                        ('rig_guides_start_sl', 'top', 5, 'rig_header_cl'),
                                        ('rig_header_rcl', 'left', 5, 'rig_header_cl'),
                                        ('rig_guides_start_sl', 'bottom', 5, 'edit_selected_module_fl'),
                                        ('rig_guides_inst_sl', 'top', 5, 'rig_header_cl'),
                                        ('rig_guides_inst_sl', 'bottom', 5, 'edit_selected_module_fl'),
                                        ('rig_guides_inst_sl', 'left', 5, 'rig_guides_start_sl'),
                                        ('edit_selected_module_fl', 'bottom', 5, 'rig_options_fl'),
                                        ('rig_options_fl', 'bottom', 5, 'rig_footer_cl')
                                        ],
                        #attachPosition=[('rig_header_cl', 'right', 5, 50), ('rig_header_rcl', 'left', 0, 50)],
                        attachNone=[('rig_footer_cl', 'top')]
                        )




    def create_skinning_layout(self):
        cmds.formLayout('skinning_tab', numberOfDivisions=100, parent='main_tab')
        cmds.scrollLayout('skin_main_sl', parent='skinning_tab')
        cmds.columnLayout('skin_main_cl', adjustableColumn=True, rowSpacing=10, parent='skin_main_sl')
        cmds.frameLayout('skin_create_fl', label=self.ar.lang['i158_create']+" SkinCluster", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='skin_main_cl')
        cmds.paneLayout("skin_create_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_create_fl')
        #colSkinLeftA - columnLayout:
        cmds.columnLayout('skin_joint_cl', adjustableColumn=True, width=170, parent='skin_create_v2_pl')
        # radio buttons:
        cmds.radioCollection('skin_joint_rc', parent='skin_joint_cl')
        cmds.radioButton('skin_all_joint_rb', label=self.ar.lang['i022_listAllJnts'], annotation="allJoints", onCommand=self.ar.populateJoints, parent='skin_joint_cl') #all joints
        dpARJoints = cmds.radioButton('skin_dpar_joint_rb', label=self.ar.lang['i023_listdpARJnts'], annotation="dpARJoints", onCommand=self.ar.populateJoints, parent='skin_joint_cl')
        cmds.rowColumnLayout('skin_joint_display_rcl', numberOfColumns=3, columnWidth=[(1, 45), (2, 45), (3, 45)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 10), (3, 'left', 10)], parent='skin_joint_cl')
        cmds.checkBox('skin_jnt_cb', label="Jnt", annotation="Skinned Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jar_cb', label="Jar", annotation="Skinned Articulation Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jad_cb', label="Jad", annotation="Skinned Additional Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jcr_cb', label="Jcr", annotation="Skinned Corrective Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jis_cb', label="Jis", annotation="Indirect Skinning Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.textField('skin_joint_name_tf', width=30, changeCommand=self.ar.populateJoints, parent='skin_joint_cl')
        cmds.textScrollList('skin_joint_tsl', width=30, height=500, allowMultiSelection=True, selectCommand=self.ar.actualizeSkinFooter, parent='skin_joint_cl')
        cmds.radioCollection('skin_joint_rc', edit=True, select=dpARJoints)
#        cmds.setParent('skin_create_fl')
        #colSkinRightA - columnLayout:
        cmds.columnLayout('skin_geo_cl', adjustableColumn=True, width=170, parent='skin_create_v2_pl')
        cmds.radioCollection('skin_geo_rc', parent='skin_geo_cl')
        cmds.radioButton('skin_all_geo_rb', label=self.ar.lang['i026_listAllJnts'], annotation="allGeoms", onCommand=self.ar.populateGeoms, parent='skin_geo_cl') #all geometries
        selGeoms = cmds.radioButton('skin_selected_geo_rb', label=self.ar.lang['i027_listSelJnts'], annotation="selGeoms", onCommand=self.ar.populateGeoms, parent='skin_geo_cl')
        cmds.checkBox('skin_geo_long_name_cb', label=self.ar.lang['i073_displayLongName'], align='left', value=1, changeCommand=self.ar.populateGeoms, parent='skin_geo_cl')
        cmds.checkBox('skin_log_win_cb', label=self.ar.lang['i286_displaySkinLog'], align='left', value=1, parent='skin_geo_cl')
        cmds.separator(style="none", height=2, parent='skin_geo_cl')
        cmds.textField('skin_geo_name_tf', width=30, changeCommand=self.ar.populateGeoms, parent='skin_geo_cl')
        cmds.textScrollList('skin_geo_tcl', width=30, height=500, allowMultiSelection=True, selectCommand=self.ar.actualizeSkinFooter, parent='skin_geo_cl' )
        cmds.radioCollection('skin_geo_rc', edit=True, select=selGeoms)
#        cmds.setParent('skin_create_fl')
        #footerB - columnLayout:
        cmds.columnLayout('skin_footer_cl', adjustableColumn=True, parent='skin_create_fl')
        cmds.separator(style='none', height=3, parent='skin_footer_cl')
        cmds.button("skin_create_bt", label=self.ar.lang['i028_skinButton'], backgroundColor=(0.5, 0.8, 0.8), command=partial(self.ar.skin.skinFromUI), parent='skin_footer_cl')
        cmds.paneLayout("skin_add_remove_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_footer_cl')
        cmds.button("skin_add_bt", label=self.ar.lang['i063_skinAddBtn'], backgroundColor=(0.7, 0.9, 0.9), command=partial(self.ar.skin.skinFromUI, "Add"), parent='skin_add_remove_v2_pl')
        cmds.button("skin_remove_bt", label=self.ar.lang['i064_skinRemBtn'], backgroundColor=(0.1, 0.3, 0.3), command=partial(self.ar.skin.skinFromUI, "Remove"), parent='skin_add_remove_v2_pl')
        cmds.separator(style='none', height=5, parent='skin_footer_cl')
        # this text will be actualized by the number of joints and geometries in the textScrollLists for skinning:
        cmds.text('skin_footer_txt', align='center', label="0 "+self.ar.lang['i025_joints']+" 0 "+self.ar.lang['i024_geometries'], parent='skin_footer_cl')
        #skinCopy - layout
        cmds.frameLayout('skin_copy_fl', label=self.ar.lang['i287_copy']+" Skinning", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='skin_main_cl')
        cmds.rowLayout('skin_copy_rl', numberOfColumns=3, columnWidth3=(90, 90, 150), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent='skin_copy_fl')
        cmds.radioCollection('skin_surface_association_rc', parent='skin_copy_rl')
        closestPoint = cmds.radioButton('skin_closest_point_rb', label="closestPoint", annotation="closestPoint", parent='skin_copy_rl')
        cmds.radioButton('skin_uvspace_rb', label="uvSpace", annotation="uvSpace", parent='skin_copy_rl') #uvSpace
        cmds.paneLayout("skin_copy_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_copy_rl')
        cmds.button("skin_copy_one_source_bt", label=self.ar.lang['i290_oneSource'], backgroundColor=(0.4, 0.8, 0.9), command=partial(self.ar.skin.copySkinFromOneSource, None, True), annotation=self.ar.lang['i288_copySkinDesc'], parent='skin_copy_v2_pl')
        cmds.button("skin_copy_multi_source_bt", label=self.ar.lang['i146_same']+" "+self.ar.lang['m222_name'], backgroundColor=(0.5, 0.8, 0.9), command=partial(self.ar.skin.copySkinSameName, None, True), annotation=self.ar.lang['i289_sameNameSkinDesc'], parent='skin_copy_v2_pl')
        cmds.radioCollection('skin_surface_association_rc', edit=True, select=closestPoint)
#        cmds.setParent( self.main_layout )
        #skinWeightsIO - layout
        cmds.frameLayout('skin_weights_io_fl', label="SkinCluster weights IO", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='skin_main_cl')
        cmds.paneLayout("skin_weights_io_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_weights_io_fl')
        cmds.button("skin_weights_export_bt", label=self.ar.lang['i164_export'], backgroundColor=(0.4, 0.8, 0.9), command=partial(self.ar.skin.ioSkinWeightsByUI, True), annotation=self.ar.lang['i266_selected'], parent='skin_weights_io_v2_pl')
        cmds.button("skin_weights_import_bt", label=self.ar.lang['i196_import'], backgroundColor=(0.5, 0.8, 0.9), command=partial(self.ar.skin.ioSkinWeightsByUI, False), annotation=self.ar.lang['i266_selected'], parent='skin_weights_io_v2_pl')
#        cmds.setParent( self.main_layout )
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout('skinning_tab', edit=True,
                        attachForm=[('skin_main_sl', 'top', 20),
                                    ('skin_main_sl', 'left', 5),
                                    ('skin_main_sl', 'right', 5),
                                    ('skin_main_sl', 'bottom', 5)
                                    ]
                        )
        

    def create_controllers_layout(self):
        cmds.formLayout('controllers_tab', numberOfDivisions=100, parent='main_tab')
        cmds.scrollLayout('ctr_main_sl', parent='controllers_tab')
        cmds.columnLayout('ctr_main_cl', adjustableColumn=True, rowSpacing=10, parent='ctr_main_sl')
        # colorControl - frameLayout:
        cmds.frameLayout('ctr_color_fl', label=self.ar.lang['m047_colorOver'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.tabLayout('ctr_color_tab', innerMarginWidth=5, innerMarginHeight=5, parent='ctr_color_fl')
        # Index layout:
        cmds.gridLayout('ctr_color_index_gl', numberOfColumns=16, cellWidthHeight=(20, 20), parent='ctr_color_tab')
        # creating buttons
        for colorIndex, colorValues in enumerate(self.ar.ctrls.getColorList()):
            cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.ar.ctrls.colorShape, color=colorIndex), parent='ctr_color_index_gl')
        # RGB layout:
        cmds.columnLayout('ctr_color_rgb_cl', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent='ctr_color_tab')
        cmds.separator(height=10, style='none', parent='ctr_color_rgb_cl')
        cmds.colorSliderGrp('ctr_color_rgb_csg', label='Color', columnAlign3=('right', 'left', 'left'), columnWidth3=(30, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=partial(self.ar.ctrls.setColorRGBByUI, slider='colorRGBSlider'), parent='ctr_color_rgb_cl')
        cmds.button("ctr_remove_override_color_bt", label=self.ar.lang['i046_remove'], command=self.ar.ctrls.removeColor, parent='ctr_color_rgb_cl')
        # Outliner layout:
        cmds.columnLayout('ctr_color_outliner_cl', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent='ctr_color_tab')
        cmds.separator(height=10, style='none', parent='ctr_color_outliner_cl')
        cmds.colorSliderGrp('ctr_color_outliner_csg', label='Outliner', columnAlign3=('right', 'left', 'left'), columnWidth3=(45, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=partial(self.ar.ctrls.setColorOutlinerByUI, slider='colorOutlinerSlider'), parent='ctr_color_outliner_cl')
        cmds.button("ctr_remove_outliner_color_bt", label=self.ar.lang['i046_remove'], command=self.ar.ctrls.removeColor, parent='ctr_color_outliner_cl')
        # renaming tabLayouts:
        cmds.tabLayout('ctr_color_tab', edit=True, tabLabel=(('ctr_color_index_gl', "Index"), ('ctr_color_rgb_cl', "RGB"), ('ctr_color_outliner_cl', "Outliner")))
        # setupController - frameLayout:
        cmds.frameLayout('ctr_default_value_fl', label=self.ar.lang['i270_defaultValues'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_default_value_v3_pl", configuration="vertical3", separatorThickness=2.0, parent='ctr_default_value_fl')
        cmds.button("ctr_reset_to_default_value_bt", label=self.ar.lang['i271_reset'], backgroundColor=(1.0, 0.9, 0.6), height=30, command=partial(self.ar.ctrls.setupDefaultValues, True), parent='ctr_default_value_v3_pl')
        cmds.button("ctr_set_default_value_bt", label=self.ar.lang['i272_set'], backgroundColor=(1.0, 0.8, 0.5), height=30, command=partial(self.ar.ctrls.setupDefaultValues, False), parent='ctr_default_value_v3_pl')
        cmds.button("ctr_setup_default_value_bt", label=self.ar.lang['i274_editor'], backgroundColor=(1.0, 0.6, 0.4), height=30, command=self.ar.ctrls.defaultValueEditor, parent='ctr_default_value_v3_pl')
        # createController - frameLayout:
        cmds.frameLayout('ctr_create_fl', label=self.ar.lang['i114_createControl'], collapsable=True, collapse=False, marginWidth=10, marginHeight=10, parent='ctr_main_cl')
        cmds.frameLayout('ctr_create_options_fl', label=self.ar.lang['i002_options'], collapsable=True, collapse=True, marginWidth=10, parent='ctr_create_fl')
        cmds.columnLayout('ctr_create_options_cl', adjustableColumn=True, width=50, rowSpacing=5, parent='ctr_create_options_fl')
        cmds.textFieldGrp('ctr_name_tfg', text="", label=self.ar.lang['i101_customName'], columnAlign2=("right", "left"), adjustableColumn2=2, columnAttach=((1, "right", 5), (2, "left", 5)), parent='ctr_create_options_cl')
        cmds.radioButtonGrp("ctr_action_rgb", label=self.ar.lang['i109_action'], labelArray3=[self.ar.lang['i108_newController'], self.ar.lang['i107_addShape'], self.ar.lang['i102_replaceShape']], vertical=True, numberOfRadioButtons=3, parent='ctr_create_options_cl')
        cmds.radioButtonGrp('ctr_action_rgb', edit=True, select=1) #new controller
        cmds.radioButtonGrp("ctr_degree_rgb", label=self.ar.lang['i103_degree'], labelArray2=[self.ar.lang['i104_linear'], self.ar.lang['i105_cubic']], vertical=True, numberOfRadioButtons=2, parent='ctr_create_options_cl')
        cmds.radioButtonGrp('ctr_degree_rgb', edit=True, select=1) #linear
        cmds.floatSliderGrp("ctr_size_fsg", label=self.ar.lang['i115_size'], field=True, minValue=0.01, maxValue=10.0, fieldMinValue=0, fieldMaxValue=100.0, precision=2, value=1.0, parent='ctr_create_options_cl')
        cmds.optionMenuGrp("ctr_direction_omg", label=self.ar.lang['i106_direction'], parent='ctr_create_options_cl')
        cmds.menuItem('ctr_direction_X_neg_mi', label='-X')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_X_pos_mi', label='+X')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Y_neg_mi', label='-Y')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Y_pos_mi', label='+Y')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Z_neg_mi', label='-Z')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Z_pos_mi', label='+Z')#, parent='ctr_direction_omg')
        cmds.optionMenuGrp('ctr_direction_omg', edit=True, value='+Y')
        # curveShapes - frameLayout:
        cmds.frameLayout('ctr_shapes_fl', label=self.ar.lang['i100_curveShapes'], collapsable=True, collapse=True, parent='ctr_create_fl')
        cmds.gridLayout('ctr_module_gl', numberOfColumns=7, cellWidthHeight=(48, 50), backgroundColor=(0.3, 0.3, 0.3), parent='ctr_shapes_fl')
        # here we populate the control module layout with the items from Controllers folder:
        self.ar.startGuideModules(self.ar.data.curves_simple_folder, "start", "ctr_module_gl")
        cmds.frameLayout('ctr_combined_shapes_fl', label=self.ar.lang['i118_combinedShapes'], collapsable=True, collapse=True, parent='ctr_create_fl')
        cmds.gridLayout('ctr_combined_module_gl', numberOfColumns=7, cellWidthHeight=(48, 50), backgroundColor=(0.3, 0.3, 0.3), parent='ctr_combined_shapes_fl')
        # here we populate the control module layout with the items from Controllers folder:
        self.ar.startGuideModules(self.ar.data.curves_combined_folder, "start", "ctr_combined_module_gl")
        # editSeletedController - frameLayout:
        cmds.frameLayout('ctr_edit_selected_fl', label=self.ar.lang['i011_editSelected']+" "+self.ar.lang['i111_controller'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_edit_selected_v3_pl", configuration="vertical3", separatorThickness=2.0, parent="ctr_edit_selected_fl")
        cmds.button("ctr_add_shape_bt", label=self.ar.lang['i113_addShapes'], backgroundColor=(1.0, 0.6, 0.7), command=partial(self.ar.ctrls.transferShape, False, False), parent="ctr_edit_selected_v3_pl")
        cmds.button("ctr_copy_shape_bt", label=self.ar.lang['i112_copyShapes'], backgroundColor=(1.0, 0.6, 0.5), command=partial(self.ar.ctrls.transferShape, False, True), parent="ctr_edit_selected_v3_pl")
        cmds.button("ctr_replace_shape_bt", label=self.ar.lang['i110_transferShapes'], backgroundColor=(1.0, 0.6, 0.3), command=partial(self.ar.ctrls.transferShape, True, True), parent="ctr_edit_selected_v3_pl")
        cmds.paneLayout("ctr_edit_selected_v2_pl", configuration="vertical2", separatorThickness=2.0, parent="ctr_edit_selected_fl")
        cmds.button("ctr_reset_curve_bt", label=self.ar.lang['i121_resetCurve'], backgroundColor=(1.0, 0.7, 0.3), height=30, command=partial(self.ar.ctrls.resetCurve), parent="ctr_edit_selected_v2_pl")
        cmds.button("ctr_change_degree_bt", label=self.ar.lang['i120_changeDegree'], backgroundColor=(1.0, 0.8, 0.4), height=30, command=partial(self.ar.ctrls.resetCurve, True), parent="ctr_edit_selected_v2_pl")
        cmds.button("ctr_zero_out_grp_bt", label=self.ar.lang['i116_zeroOut'], backgroundColor=(0.8, 0.8, 0.8), height=30, command=self.ar.utils.zeroOut, parent="ctr_edit_selected_fl")
        cmds.button("ctr_select_all_bt", label=self.ar.lang['i291_selectAllControls'], backgroundColor=(0.9, 1.0, 0.6), height=30, command=partial(self.ar.ctrls.selectAllControls), parent="ctr_edit_selected_fl")
        # calibrationControls - frameLayout:
        cmds.frameLayout('ctr_calibration_fl', label=self.ar.lang['i193_calibration'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_calibration_v2_pl", configuration="vertical2", separatorThickness=2.0, parent="ctr_calibration_fl")
        cmds.button("ctr_transfer_calibration_bt", label=self.ar.lang['i194_transfer'], backgroundColor=(0.5, 1.0, 1.0), height=30, command=self.ar.ctrls.transferCalibration, parent="ctr_calibration_v2_pl")
        cmds.button("ctr_import_calibration_bt", label=self.ar.lang['i196_import'], backgroundColor=(0.5, 0.8, 1.0), height=30, command=self.ar.ctrls.importCalibration, parent="ctr_calibration_v2_pl")
        # mirror calibration - layout:
        cmds.frameLayout('ctr_mirror_calibration_fl', label=self.ar.lang['m010_mirror']+" "+self.ar.lang['i193_calibration'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent="ctr_calibration_fl")
        cmds.rowColumnLayout('ctr_mirror_calibration_rcl', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="ctr_calibration_fl")
        cmds.text("ctr_mirror_calibration_prefix_txt", label=self.ar.lang['i144_prefix'], parent="ctr_mirror_calibration_rcl")
        cmds.text("ctr_mirror_calibration_from_prefix_txt", label=self.ar.lang['i036_from'], parent="ctr_mirror_calibration_rcl")
        cmds.textField('ctr_mirror_calibration_from_prefix_tf', text=self.ar.lang['p002_left']+"_", parent="ctr_mirror_calibration_rcl")
        cmds.text("ctr_mirror_calibration_to_prefix_txt", label=self.ar.lang['i037_to'], parent="ctr_mirror_calibration_rcl")
        cmds.textField('ctr_mirror_calibration_to_prefix_tf', text=self.ar.lang['p003_right']+"_", parent="ctr_mirror_calibration_rcl")
        cmds.button("ctr_mirror_calibration_bt", label=self.ar.lang['m010_mirror'], backgroundColor=(0.5, 0.7, 1.0), height=30, width=70, command=self.ar.ctrls.mirrorCalibration, parent="ctr_mirror_calibration_rcl")
        # ControlShapeIO - frameLayout:
        cmds.frameLayout('ctr_shape_io_fl', label=self.ar.lang['m067_shape']+" "+self.ar.lang['i199_io'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_shape_io_v4_pl", configuration="vertical4", separatorThickness=2.0, parent="ctr_shape_io_fl")
        cmds.button("ctr_shape_io_export_bt", label=self.ar.lang['i164_export'], backgroundColor=(1.0, 0.8, 0.8), height=30, command=self.ar.ctrls.exportShape, parent="ctr_shape_io_v4_pl")
        cmds.button("ctr_shape_io_import_bt", label=self.ar.lang['i196_import'], backgroundColor=(1.0, 0.9, 0.9), height=30, command=self.ar.ctrls.importShape, parent="ctr_shape_io_v4_pl")
        # mirror control shape - layout:
        cmds.frameLayout('ctr_mirror_shape_fl', label=self.ar.lang['m010_mirror']+" "+self.ar.lang['m067_shape'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent="ctr_shape_io_fl")
        cmds.rowColumnLayout('ctr_mirror_shape_rcl', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="ctr_shape_io_fl")
        cmds.optionMenu("ctr_mirror_shape_axis_om", label='', parent="ctr_mirror_shape_rcl")
        for x in self.ar.data.axis:
            cmds.menuItem('ctr_mirror_axis_'+x+'_mi', label=x, parent="ctr_mirror_shape_axis_om")
        cmds.text("ctr_mirror_shape_from_prefix_txt", label=self.ar.lang['i036_from'], parent="ctr_mirror_shape_rcl")
        cmds.textField('ctr_mirror_shape_from_prefix_tf', text=self.ar.lang['p002_left']+"_", parent="ctr_mirror_shape_rcl")
        cmds.text("ctr_mirror_shape_to_prefix_txt", label=self.ar.lang['i037_to'], parent="ctr_mirror_shape_rcl")
        cmds.textField('ctr_mirror_shape_to_prefix_tf', text=self.ar.lang['p003_right']+"_", parent="ctr_mirror_shape_rcl")
        cmds.button("ctr_mirror_shape_bt", label=self.ar.lang['m010_mirror'], backgroundColor=(1.0, 0.5, 0.5), height=30, width=70, command=self.ar.ctrls.resetMirrorShape, parent="ctr_mirror_shape_rcl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout('controllers_tab', edit=True,
                        attachForm=[('ctr_main_sl', 'top', 20), ('ctr_main_sl', 'left', 5), ('ctr_main_sl', 'right', 5), ('ctr_main_sl', 'bottom', 5)]
                        )


    def create_tools_layout(self):
        cmds.formLayout('tools_tab', numberOfDivisions=100, parent="main_tab")
        cmds.scrollLayout("tools_sl", parent="tools_tab")
        cmds.columnLayout("tools_cl", adjustableColumn=True, rowSpacing=3, parent="tools_sl")
        self.ar.startGuideModules(self.ar.data.tools_folder, "start", "tools_cl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout("tools_tab", edit=True,
                        attachForm=[("tools_sl", 'top', 20), ("tools_sl", 'left', 5), ("tools_sl", 'right', 5), ("tools_sl", 'bottom', 5)]
                        )


    def create_validator_layout(self):
        cmds.formLayout('validator_tab', numberOfDivisions=100, parent="main_tab")
        cmds.scrollLayout("validator_sl", parent="validator_tab")
        cmds.columnLayout("validator_cl", adjustableColumn=True, rowSpacing=3, parent="validator_sl")
        
        self.create_check_layout("i208_checkin", self.ar.data.checkin_folder, self.ar.data.checkin_instances, "validator_cl")
        self.create_check_layout("i209_checkout", self.ar.data.checkout_folder, self.ar.data.checkout_instances, "validator_cl")
        if self.ar.pipeliner.pipeData['addOnsPath']:
            if self.ar.getValidatorsAddOns():
                cmds.separator(height=30, parent="validator_cl")
                self.create_check_layout("i212_addOns", "", self.ar.data.checkaddon_instances, "validator_cl", self.ar.pipeliner.pipeData['addOnsPath'])
        if self.ar.pipeliner.pipeData['finishingPath']:
            if self.ar.getValidatorsAddOns("finishingPath"):
                cmds.separator(height=30, parent="validator_cl")
                self.create_check_layout("i354_finishing", "", self.ar.data.checkfinishing_instances, "validator_cl", self.ar.pipeliner.pipeData['finishingPath'])
        # publisher
        cmds.columnLayout('validator_footer_cl', adjustableColumn=True, parent="validator_tab")
        cmds.separator(style='none', height=3, parent="validator_footer_cl")
        cmds.button("validator_publisher_bt", label=self.ar.lang['m046_publisher'], backgroundColor=(0.75, 0.75, 0.75), height=40, command=self.ar.publisher.mainUI, parent="validator_footer_cl")
        cmds.separator(style='none', height=5, parent="validator_footer_cl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout("validator_tab", edit=True,
                        attachForm=[("validator_sl", 'top', 20), ("validator_sl", 'left', 5), ("validator_sl", 'right', 5), ("validator_sl", 'bottom', 60), ("validator_footer_cl", 'left', 5), ("validator_footer_cl", 'right', 5), ("validator_footer_cl", 'bottom', 5)],
                        attachNone=[("validator_footer_cl", 'top')]
                        )
        self.ar.setValidatorPreset()


    def create_rebuilder_layout(self):
        
        # divide method to?
        # asset
        # processes
        # rebuilder?

        cmds.formLayout("rebuilder_tab", numberOfDivisions=100, parent="main_tab")
        # project pipeline asset
        cmds.columnLayout('asset_main_cl', adjustableColumn=False, parent="rebuilder_tab")
        cmds.frameLayout('asset_fl', label=self.ar.lang['i303_asset'], collapsable=True, collapse=False, width=370, parent="asset_main_cl")
        cmds.textFieldGrp("asset_maya_project_tfg", label="Maya "+self.ar.lang['i301_project']+":", text=self.ar.pipeliner.pipeData['mayaProject'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent="asset_fl")
        cmds.textFieldGrp("asset_pipeline_tfg", label="Pipeline:", text=self.ar.pipeliner.pipeData['projectPath'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent="asset_fl")
        cmds.textFieldGrp("asset_name_tfg", label=self.ar.lang['i303_asset']+":", text=self.ar.pipeliner.pipeData['assetName'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent="asset_fl")
        # asset buttons
        cmds.rowColumnLayout("asset_buttons_rcl", numberOfColumns=5, columnAlign=[(1, "left"), (2, "left"), (3, "left"), (4, "left"), (5, "left")], columnAttach=[(1, "left", 10), (2, "left", 10), (3, "left", 10), (4, "left", 10), (5, "left", 10)], parent="asset_fl")
        cmds.button("asset_save_version_bt", label=self.ar.lang['i222_save']+" "+self.ar.lang['m205_version'], command=self.ar.pipeliner.saveVersion, parent="asset_buttons_rcl")
        cmds.button("asset_load_bt", label=self.ar.lang['i187_load'], command=self.ar.pipeliner.loadAsset, parent="asset_buttons_rcl")
        cmds.button("asset_new_bt", label=self.ar.lang['i304_new'], command=self.ar.pipeliner.createNewAssetUI, parent="asset_buttons_rcl")
        cmds.button("asset_open_folder_bt", label=self.ar.lang['c108_open']+" "+self.ar.lang['i298_folder'], command=partial(self.ar.packager.openFolder, self.ar.pipeliner.pipeData['projectPath']), parent="asset_buttons_rcl")
        cmds.button("asset_replace_data_bt", label=self.ar.lang['m219_replace']+" "+self.ar.data.dp_data, command=partial(self.ar.pipeliner.loadAsset, mode=1), parent="asset_buttons_rcl")
        cmds.separator(style='in', height=20, width=370, parent="asset_main_cl")
        # processes
        cmds.rowColumnLayout('processes_rcl', adjustableColumn=1, numberOfColumns=2, columnAlign=[(1, "left"), (2, "right")], columnWidth=[(1, 360), (2, 17)], columnAttach=[(1, "both", 10), (2, "right", 10)], parent="rebuilder_tab")
        cmds.text('processes_io_txt', label=self.ar.lang['i292_processes'].upper()+" IO", font="boldLabelFont", parent="processes_rcl")
        cmds.iconTextButton("rebuilder_tri_collapse_itb", image=self.ar.data.icon['triDown'], annotation=self.ar.lang['i348_triangleIconAnn'], command=partial(self.ar.collapseAllFL, "rebuilder_tri_collapse_itb", 1), width=17, height=17, style='iconOnly', align='right', parent="processes_rcl")
        cmds.scrollLayout("rebuilder_main_sl", parent="rebuilder_tab")
        cmds.columnLayout("rebuilder_cl", adjustableColumn=True, rowSpacing=3, parent="rebuilder_main_sl")
        self.ar.startGuideModules(self.ar.data.rebuilder_folder, "start", "rebuilder_cl")
        cmds.separator(style='none', parent="rebuilder_cl")
        cmds.frameLayout('rebuilder_start_fl', label=self.ar.lang['c110_start'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        self.ar.startGuideModules(self.ar.data.start_folder, "start", "rebuilder_start_fl")
        cmds.frameLayout('rebuilder_source_fl', label=self.ar.lang['i331_source'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        self.ar.startGuideModules(self.ar.data.source_folder, "start", "rebuilder_source_fl")
        cmds.frameLayout('rebuilder_setup_fl', label=self.ar.lang['i332_setup'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        self.ar.startGuideModules(self.ar.data.setup_folder, "start", "rebuilder_setup_fl")
        cmds.frameLayout('rebuilder_deforming_fl', label=self.ar.lang['i333_deforming'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        self.ar.startGuideModules(self.ar.data.deforming_folder, "start", "rebuilder_deforming_fl")
        cmds.frameLayout('rebuilder_custom_fl', label=self.ar.lang['i334_custom'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        self.ar.startGuideModules(self.ar.data.custom_folder, "start", "rebuilder_custom_fl")
        cmds.separator(style='none', parent="rebuilder_cl")
        self.ar.collapseAllFL("rebuilder_tri_collapse_itb", 1) #close all = hack to start opened to get the right width then collapse them
        # rebuilder
        cmds.columnLayout('rebuilder_footer_cl', adjustableColumn=False, parent="rebuilder_tab")
        cmds.separator(style='in', height=20, width=370, parent="rebuilder_footer_cl")
        cmds.checkBox("rebuilder_select_all_cb", label=self.ar.lang['m004_select']+" "+self.ar.lang['i211_all']+" "+self.ar.lang['i292_processes'].lower(), value=True, changeCommand=partial(self.ar.changeActiveAllModules, self.ar.data.rebuilder_instances), parent="rebuilder_footer_cl")
        cmds.separator(style='none', height=10, parent="rebuilder_footer_cl")
        cmds.paneLayout("rebuilder_selected_pl", configuration="vertical2", separatorThickness=7.0, width=370, parent="rebuilder_footer_cl")
        cmds.button("rebuilder_split_data_bt", label=self.ar.lang['r002_splitData'].upper(), command=partial(self.ar.runSelectedActions, self.ar.data.rebuilder_instances, True, True, actionType="r000_rebuilder"), parent="rebuilder_selected_pl")
        cmds.button("rebuilder_rebuild_bt", label=self.ar.lang['r001_rebuild'].upper(), command=partial(self.ar.runSelectedActions, self.ar.data.rebuilder_instances, False, True, actionType="r000_rebuilder"), parent="rebuilder_selected_pl")
        cmds.separator(style='none', height=10, parent="rebuilder_footer_cl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout("rebuilder_tab", edit=True,
                        attachForm=[("rebuilder_main_sl", 'left', 5), ("rebuilder_main_sl", 'right', 5), ("rebuilder_main_sl", 'bottom', 80), 
                                    ("asset_main_cl", 'left', 5), ("asset_main_cl", 'right', 5), ("asset_main_cl", 'top', 15),
                                    ("rebuilder_footer_cl", 'left', 5), ("rebuilder_footer_cl", 'right', 5), ("rebuilder_footer_cl", 'bottom', 5)],
                        attachControl=[("rebuilder_main_sl", 'top', 10, "processes_rcl"), ("processes_rcl", 'top', 10, "asset_main_cl")],
                        attachNone=[("rebuilder_footer_cl", 'top')]
                        )




    def create_layout(self):
        cmds.formLayout('main_layout')#, parent='dpAutoRigSystemWC')
        cmds.tabLayout('main_tab', innerMarginWidth=5, innerMarginHeight=5, parent='main_layout')
        cmds.formLayout('main_layout', edit=True, attachForm=(('main_tab', 'top', 0), ('main_tab', 'left', 0), ('main_tab', 'bottom', 0), ('main_tab', 'right', 0)))
        
        self.create_rigging_layout()
        self.create_skinning_layout()
        self.create_controllers_layout()
        self.create_tools_layout()
        self.create_validator_layout()
        self.create_rebuilder_layout()





    def main_ui(self):
        """ Create the layouts inside of the mainLayout. Here will be the entire User Interface.
        """
        self.create_menu()
        self.create_layout()
        
        # TODO: by Configuration?
        #self.start_guides()




 #       self.langName = self.ar.getCurrentMenuValue(self.langList)
 #       self.presetName = self.ar.getCurrentMenuValue(self.presetList)
        # optimize dictionaries
 #       self.ar.lang = self.langDic[self.langName]
 #       self.ctrlPreset = self.presetDic[self.presetName]
        
        # -- Initialize some objects here:

        # -- Layout
        
        cmds.tabLayout('main_tab', edit=True, tabLabel=(('rigging_tab', 'Rigging'), ('skinning_tab', 'Skinning'), ('controllers_tab', self.ar.lang['i342_controllers']), ("tools_tab", self.ar.lang['i343_tools']), ("validator_tab", self.ar.lang['v000_validator']), ("rebuilder_tab", self.ar.lang['r000_rebuilder'])))



    def create_check_layout(self, name, folder, instances, layout, path=None):
        cmds.frameLayout(name+"_fl", label=self.ar.lang[name].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=layout)
        self.ar.startGuideModules(folder, "start", name+"_fl", path=path)
        cmds.separator(style="none", parent=name+"_fl")
        cmds.checkBox(name+"_select_all_cb", label=self.ar.lang['m004_select']+" "+self.ar.lang['i211_all']+" "+self.ar.lang[name], value=False, changeCommand=partial(self.ar.changeActiveAllModules, instances), parent=name+"_fl")
        cmds.paneLayout(name+"_select_v2_pl", configuration="vertical2", separatorThickness=7.0, parent=name+"_fl")
        cmds.button(name+"_veryfy_all_bt", label=self.ar.lang['i210_verify'].upper(), command=partial(self.ar.runSelectedActions, instances, True, True), parent=name+"_select_v2_pl")
        cmds.button(name+"_fix_all_bt", label=self.ar.lang['c052_fix'].upper(), command=partial(self.ar.runSelectedActions, instances, False, True), parent=name+"_select_v2_pl")
        cmds.separator(height=30, parent=layout)




    def reload_ui(self, opt_var=None, item=None, *args):
        """ This method will set the given optionVar and reload the dpAutoRigSystem UI.
        """
        if opt_var and item:
            self.ar.opt.set_option_var(opt_var, item)
        cmds.evalDeferred("ar = dpAutoRig.Start("+str(self.ar.dev)+"); ar.ui();", lowestPriority=True)
    

    def reload_dev_mode_ui(self, *args):
        """ Reload the system code as development mode.
        """
        value = cmds.menuItem('dev_mode_mi', query=True, checkBox=True)
        if value:
            cmds.evalDeferred("from importlib import reload; reload(dpAutoRigSystem); ar = dpAutoRig.Start(True); ar.ui();", lowestPriority=True)
        else:
            cmds.evalDeferred("ar = dpAutoRig.Start(); ar.ui();", lowestPriority=True)


    def change_verbose(self, *args):
        """ Set the dev verbose variable.
        """
        self.ar.verbose = cmds.menuItem('verbose_mi', query=True, checkBox=True)
        print("Verbose =", self.ar.verbose)

    
    # def refresh_main_ui(self, savedScene=False, resetButtons=True, clearSel=False, *args):
    #     """ Read guides, joints, geometries and refresh the UI without reload the script creating a new instance.
    #         Useful to rebuilding process when creating a new scene
    #     """
    #     if savedScene:
    #         self.selList = cmds.ls(selection=True)
    #         self.rebuilding = False
    #     self.ar.populateCreatedGuideModules()
    #     self.ar.checkImportedGuides()
    #     self.ar.checkGuideNets()
    #     self.ar.populateJoints()
    #     self.ar.populateGeoms()
    #     if not self.rebuilding:
    #         if resetButtons:
    #             self.ar.resetAllButtonColors()
    #         self.ar.pipeliner.refreshAssetData()
    #         for rebuildInstance in self.rebuilderInstanceList:
    #             rebuildInstance.updateActionButtons(color=False)
    #     try:
    #         self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=False, compressUndo=True)
    #     except:
    #         self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=False, killWithScene=False, compressUndo=True)
    #     if savedScene:
    #         cmds.select(clear=True)
    #         if self.selList:
    #             cmds.select(self.selList)
    #     if clearSel:
    #         cmds.select(clear=True)
    #     self.rebuilding = False


    # def startScriptJobs(self, *args):
    #     """ Create scriptJobs to read:
    #         - NewSceneOpened
    #         - SceneSaved
    #         - deleteAll = new scene (disable to don't reset the asset context when running a new scene for the first module)
    #         - SelectionChanged
    #         - WorkspaceChanged = not documented
    #     """
    #     cmds.scriptJob(event=('SceneOpened', partial(self.refresh_main_ui, clearSel=True)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
    #     #cmds.scriptJob(event=('deleteAll', self.refresh_main_ui), parent='dpAutoRigSystemWC', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
    #     cmds.scriptJob(event=('NewSceneOpened', self.refresh_main_ui), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
    #     cmds.scriptJob(event=('SceneSaved', partial(self.refresh_main_ui, savedScene=True, resetButtons=False)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
    #     cmds.scriptJob(event=('workspaceChanged', self.ar.pipeliner.refreshAssetData), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
    #     self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=False, compressUndo=True, force=True)
    #     self.ar.ctrls.startCorrectiveEditMode()
    #     self.jobSelectedGuide()


    def deleteExistWindow(self, *args):
        """ Check if there are the dpAutoRigWindow and a control element to delete the UI.
        """
        if cmds.workspaceControl("dpAutoRigSystemWC", query=True, exists=True):
            cmds.workspaceControl("dpAutoRigSystemWC", edit=True, close=True)
            #cmds.deleteUI("dpAutoRigSystemWC", control=True)
        winNameList = ["dpARLoadWin", "dpInfoWindow", "dpNewAssetWindow", "dpReplaceDPDataWindow", "dpSelectAssetWindow", "dpSaveVersionWindow", self.ar.data.plus_info_win_name, self.ar.data.color_override_win_name]
        for winName in winNameList:
            self.ar.utils.closeUI(winName)