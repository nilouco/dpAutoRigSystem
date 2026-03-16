#import libraries
import os
from maya import cmds
from functools import partial
from importlib import reload


class UI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self):
        """ Start the main UI, menus and layouts for dpAutoRigSystem through workspaceControl.
        """
        if cmds.workspaceControl(self.ar.data.workspace_control_name, query=True, exists=True):
            cmds.workspaceControl(self.ar.data.workspace_control_name, edit=True, close=True)
        labelText = "dpAutoRigSystem"
        labelText += " - "+self.ar.dpARVersion
        if self.ar.dev:
            labelText += " ~ dev"
        uiCallScript = "import dpAutoRigSystem; from dpAutoRigSystem import dpAutoRig; ar = dpAutoRig.Start("+str(self.ar.dev)+", intro=False); ar.main_ui.show_ui();"
        cmds.workspaceControl(
                                self.ar.data.workspace_control_name, 
                                retain=False,
                                floating=False,
                                minimumWidth=400,
                                initialWidth=400,
                                minimumHeight=515,
                                initialHeight=715,
                                widthProperty="preferred",
                                visible=True,
                                loadImmediately=True,
                                label=labelText,
                                uiScript=uiCallScript
                                )
    
    
    def show_ui(self):
        """ Call mainUI method and the following instructions to check optionVars, refresh UI elements, start the scriptJobs and close loading window.
        """
        startSelList = cmds.ls(selection=True)

        self.main_ui()
        self.ar.ui_manager.set_ui_state(True)
        self.ar.lib.fill_library()
        
        #
        #
        # WIP:
        #
        self.ar.ui_manager.refresh_ui()


        self.ar.autoCheckOptionVar("dpAutoRigAutoCheckUpdate", "dpAutoRigLastDateAutoCheckUpdate", "update")
        self.ar.autoCheckOptionVar("dpAutoRigAgreeTermsCond", "dpAutoRigLastDateAgreeTermsCond", "terms")
        
        #self.ar.refreshMainUI()



#        self.ar.startScriptJobs()
#        self.ar.utils.closeUI("dpar_load_win")
#        cmds.select(startSelList)
#        print("dpAutoRigSystem "+self.ar.data.lang['i346_loadedSuccess'])





    def main_ui(self):
        """ Create the layouts inside of the mainLayout. Here will be the entire User Interface.
        """
        self.create_menu()
        self.create_layout()
        cmds.tabLayout('main_tab', edit=True, tabLabel=(
                                                        ('rigging_tab', 'Rigging'),
                                                        ('skinning_tab', 'Skinning'),
                                                        ('controllers_tab', self.ar.data.lang['i342_controllers']),
                                                        ("tools_tab", self.ar.data.lang['i343_tools']),
                                                        ("validator_tab", self.ar.data.lang['v000_validator']),
                                                        ("rebuilder_tab", self.ar.data.lang['r000_rebuilder']))
                                                        )


    def create_menu(self):
        cmds.menuBarLayout("main_menu_bar", parent=self.ar.data.workspace_control_name)
        self.create_settings_menu()
        self.create_the_create_menu()
        self.create_window_menu()
        self.create_help_menu()
        self.create_dev_menu()


    def create_settings_menu(self):
        cmds.menu('settings_menu', label='Settings', parent='main_menu_bar')
        self.create_radio_menu("language", "settings_menu", self.ar.data.lang["_preset"], self.ar.data.lang_preset_data, self.ar.data.language_option_var)
        self.create_radio_menu("validator_preset", "settings_menu", self.ar.data.validator_preset["_preset"], self.ar.data.validator_preset_data, self.ar.data.validator_option_var, refresh=True)
        self.create_radio_menu("curve_preset", "settings_menu", self.ar.data.curve_preset["_preset"], self.ar.data.curve_preset_data, self.ar.data.curve_option_var, refresh=True)
        self.create_radio_menu("curve_degree", "settings_menu", self.ar.data.degree, {d:0 for d in self.ar.data.degrees}, self.ar.data.degree_option_var, degree=True)
        
        #
        #
        # WIP
        # TODO: save options by optionVars:
        #
        # Options
        cmds.menuItem("options_mi", label=self.ar.data.lang['i002_options'], subMenu=True, parent="settings_menu")
        
        cmds.menuItem("opt_colorize_curve_mi", label=self.ar.data.lang['i065_colorizeCtrl'], checkBox=self.ar.data.colorize_curve, command=self.ar.opt.set_colorize_curve, parent="options_mi")
        cmds.menuItem("opt_add_supplementary_attr_mi", label=self.ar.data.lang['i066_addAttr'], checkBox=self.ar.data.add_supplementary_attr, command=self.ar.opt.set_add_supplementary_attr, parent="options_mi")
        cmds.menuItem("opt_display_joint_mi", label=self.ar.data.lang['i009_displayJointsCB'], checkBox=self.ar.data.display_joint, command=self.ar.opt.set_display_joint, parent="options_mi")
        cmds.menuItem("opt_display_temp_grp_mi", label=self.ar.data.lang['i183_hideGuideGrp'], checkBox=self.ar.data.display_temp_grp, command=self.ar.opt.set_display_temp_grp, parent="options_mi")
        cmds.menuItem("opt_integrate_module_mi", label=self.ar.data.lang['i010_integrateCB'], checkBox=self.ar.data.integrate_module, command=self.ar.opt.set_integrate_module, parent="options_mi")
        cmds.menuItem("opt_default_render_layer_mi", label=self.ar.data.lang['i004_defaultRL'], checkBox=self.ar.data.use_default_render_layer, command=self.ar.opt.set_use_default_render_layer, parent="options_mi")


        cmds.menuItem("opt_prefix_mi", label=f"{self.ar.data.lang['i272_set']} {self.ar.data.lang['i144_prefix']}", command=self.ar.opt.set_prefix, parent="settings_menu")
        





    def create_the_create_menu(self):
        # create menu:
        cmds.menu('create_menu', label='Create', parent='main_menu_bar')
        cmds.menuItem('translator_mi', label='Translator', command=self.ar.translator, parent='create_menu')
        cmds.menuItem('pipeliner_mi', label='Pipeliner', command=self.ar.config.open_pipeliner, parent='create_menu')
        cmds.menuItem('create_curve_preset_mi', label='Curve Preset', command=partial(self.ar.config.create_preset, "curve", self.ar.data.curve_preset_folder, True), parent='create_menu')
        cmds.menuItem('create_validator_preset_mi', label='Validator Preset', command=partial(self.ar.config.create_preset, "validator", self.ar.data.validator_preset_folder, False), parent='create_menu')


    def create_window_menu(self):
        # window menu:
        cmds.menu('window_menu', label='Window', parent='main_menu_bar')
        cmds.menuItem('dev_mode_mi', label='Dev mode', checkBox=self.ar.dev, command=self.ar.ui_manager.reload_dev_mode_ui, parent='window_menu')
        cmds.menuItem('reload_ui_mi', label='Reload UI', command=self.ar.ui_manager.reload_ui, parent='window_menu')
        cmds.menuItem('quit_mi', label='Quit', command=self.ar.ui_manager.delete_exist_window, parent='window_menu')


    def create_help_menu(self):
        # help menu:
        cmds.menu('help_menu', label='Help', helpMenu=True, parent='main_menu_bar')
        cmds.menuItem('about_mi"', label='About', command=partial(self.ar.logger.infoWin, 'm015_about', 'i006_aboutDesc', self.ar.dpARVersion, 'center', 305, 250), parent='help_menu')
        cmds.menuItem('author_mi', label='Author', command=partial(self.ar.logger.infoWin, 'm016_author', 'i007_authorDesc', None, 'center', 305, 250), parent='help_menu')
        cmds.menuItem('collaborators_mi', label='Collaborators', command=partial(self.ar.logger.infoWin, 'i165_collaborators', 'i166_collabDesc', "\n\n"+self.ar.data.lang['_collaborators'], 'center', 305, 250), parent='help_menu')
        cmds.menuItem('donate_mi', label='Donate', command=partial(self.ar.donateWin), parent='help_menu')
        cmds.menuItem('idiom_mi', label='Idioms', command=partial(self.ar.logger.infoWin, 'm009_idioms', 'i012_idiomsDesc', None, 'center', 305, 250), parent='help_menu')
        cmds.menuItem('terms_mi', label='Terms and Conditions', command=self.ar.checkTermsAndCond, parent='help_menu')
        cmds.menuItem('update_mi', label='Update', command=partial(self.ar.checkForUpdate, True), parent='help_menu')
        cmds.menuItem('help_mi', label='Wiki...', command=partial(self.ar.utils.visitWebSite, self.ar.data.wiki_url), parent='help_menu')


    def create_dev_menu(self):
        cmds.menu('dev_menu', label='Dev', visible=self.ar.dev, parent='main_menu_bar')
        cmds.menuItem('verbose_mi', label='Verbose', checkBox=self.ar.data.verbose, command=self.ar.opt.set_verbose)


    def create_radio_menu(self, name, parent_menu, current, data, option_var=None, degree=False, refresh=False):
        menu_name = f"{name}_menu"
        collection_name = f"{name}_rbc"
        cmds.menuItem(menu_name, label=name.capitalize().replace("_", " "), parent=parent_menu, subMenu=True)
        cmds.radioMenuItemCollection(collection_name)
        for item in data.keys():
            if degree:
                cmds.menuItem(f"{item}_mi", label=item, radioButton=False, collection=collection_name, command=partial(self.ar.opt.change_degree, item), parent=menu_name)
            elif refresh:
                cmds.menuItem(f"{item}_mi", label=item, radioButton=False, collection=collection_name, command=self.ar.ui_manager.refresh_ui, parent=menu_name)
            else:
                cmds.menuItem(f"{item}_mi", label=item, radioButton=False, collection=collection_name, command=partial(self.ar.ui_manager.reload_ui, option_var, item), parent=menu_name)
        cmds.menuItem(f"{current}_mi", edit=True, radioButton=True, collection=collection_name)


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
            

    def create_rigging_layout(self):
        cmds.formLayout('rigging_tab', numberOfDivisions=100, parent='main_tab')
        # top left
        cmds.columnLayout('rig_header_cl', adjustableColumn=True, height=20, parent='rigging_tab')
        cmds.text('rig_guides_txt', label=self.ar.data.lang['i000_guides'], font="boldLabelFont", width=150, align='center', parent='rig_header_cl')
        # top right
        cmds.rowColumnLayout('rig_header_rcl', numberOfColumns=2, adjustableColumn=1, columnWidth=(120, 50), parent='rigging_tab')
        cmds.text('rig_modules_txt', label=self.ar.data.lang['i001_modules'], font="boldLabelFont", width=150, align='center', parent='rig_header_rcl')
        cmds.iconTextButton("rig_tri_collapse_guides_itb", image=self.ar.data.icon['triDown'], annotation=self.ar.data.lang['i348_triangleIconAnn'], command=partial(self.ar.ui_manager.collapse_all_fl, "rig_tri_collapse_guides_itb", 0), width=17, height=17, style='iconOnly', align='right', parent='rig_header_rcl')
        # middle left
        cmds.scrollLayout("rig_guides_start_sl", width=160, parent='rigging_tab')
        cmds.text('rig_standard_txt', label=self.ar.data.lang['i030_standard'], font="obliqueLabelFont", align='left', parent='rig_guides_start_sl')
        cmds.columnLayout("rig_guides_standard_cl", adjustableColumn=True, width=140, rowSpacing=3, parent='rig_guides_start_sl')
        # -> rig_guides_standard_cl it will be populated here by guides of standard library...
        cmds.separator(style='doubleDash', height=10, width=140, parent='rig_guides_start_sl')
        cmds.text('rig_integrated_txt', label=self.ar.data.lang['i031_integrated'], font="obliqueLabelFont", align='left', parent='rig_guides_start_sl')
        cmds.columnLayout("rig_guides_integrated_cl", adjustableColumn=True, width=140, rowSpacing=3, parent='rig_guides_start_sl')
        # -> rig_guides_integrated_cl it will be populated here by guides of integrated templates...
        # middle right
        cmds.scrollLayout("rig_guides_inst_sl", width=120, parent='rigging_tab')
        cmds.columnLayout("rig_guides_inst_cl", adjustableColumn=True, width=120, parent='rig_guides_inst_sl')
        # -> rig_guides_inst_cl it will be populated here by created instances of modules...
        # edit selected module layout
        cmds.frameLayout('rig_edit_selected_module_fl', label=self.ar.data.lang['i011_editSelected']+" "+self.ar.data.lang['i143_module'], collapsable=True, collapse=self.ar.data.collapse_edit_sel_mod, parent='rigging_tab')
        cmds.columnLayout('rig_selected_module_cl', adjustableColumn=True, parent='rig_edit_selected_module_fl')
        # footer
        cmds.columnLayout('rig_footer_cl', adjustableColumn=True, parent='rigging_tab')
        cmds.text("rig_prefix_txt", label="", font="boldLabelFont", height=25, visible=False, parent="rig_footer_cl")
        cmds.button('rig_all_bt', label=self.ar.data.lang['i020_rigAll'], annotation=self.ar.data.lang['i021_rigAllDesc'], backgroundColor=(0.6, 1.0, 0.6), command=self.ar.rigAll, parent='rig_footer_cl')
        cmds.separator(style='none', height=5, parent='rig_footer_cl')
        # this text will be actualized by the number of module instances created in the scene...
        cmds.text('rig_footer_txt', label="# "+self.ar.data.lang['i005_footerRigging'], align='center', parent='rig_footer_cl')
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout('rigging_tab', edit=True,
                        attachForm=[
                                    ('rig_header_cl', 'top', 7),
                                    ('rig_header_cl', 'left', 5),
                                    ('rig_header_rcl', 'top', 5),
                                    ('rig_header_rcl', 'right', 5),
                                    ('rig_guides_start_sl', 'left', 5),
                                    ('rig_guides_inst_sl', 'right', 5),
                                    ('rig_edit_selected_module_fl', 'left', 5),
                                    ('rig_edit_selected_module_fl', 'right', 5),
                                    ('rig_footer_cl', 'left', 5),
                                    ('rig_footer_cl', 'bottom', 5),
                                    ('rig_footer_cl', 'right', 5)
                                    ],
                        attachControl=[ 
                                        ('rig_guides_start_sl', 'top', 5, 'rig_header_cl'),
                                        ('rig_header_rcl', 'left', 5, 'rig_header_cl'),
                                        ('rig_guides_start_sl', 'bottom', 5, 'rig_edit_selected_module_fl'),
                                        ('rig_guides_inst_sl', 'top', 5, 'rig_header_cl'),
                                        ('rig_guides_inst_sl', 'bottom', 5, 'rig_edit_selected_module_fl'),
                                        ('rig_guides_inst_sl', 'left', 5, 'rig_guides_start_sl'),
                                        ('rig_edit_selected_module_fl', 'bottom', 5, 'rig_footer_cl')
                                        ],
                        attachNone=[('rig_footer_cl', 'top')]
                        )


    def create_skinning_layout(self):
        cmds.formLayout('skinning_tab', numberOfDivisions=100, parent='main_tab')
        cmds.scrollLayout('skin_main_sl', parent='skinning_tab')
        cmds.columnLayout('skin_main_cl', adjustableColumn=True, rowSpacing=10, parent='skin_main_sl')
        cmds.frameLayout('skin_create_fl', label=self.ar.data.lang['i158_create']+" SkinCluster", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='skin_main_cl')
        cmds.paneLayout("skin_create_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_create_fl')
        # left
        cmds.columnLayout('skin_joint_cl', adjustableColumn=True, width=170, parent='skin_create_v2_pl')
        cmds.radioCollection('skin_joint_rc', parent='skin_joint_cl')
        cmds.radioButton('skin_all_joint_rb', label=self.ar.data.lang['i022_listAllJnts'], annotation="allJoints", onCommand=self.ar.populateJoints, parent='skin_joint_cl') #all joints
        cmds.radioButton('skin_dpar_joint_rb', label=self.ar.data.lang['i023_listdpARJnts'], annotation="dpARJoints", onCommand=self.ar.populateJoints, parent='skin_joint_cl')
        cmds.rowColumnLayout('skin_joint_display_rcl', numberOfColumns=3, columnWidth=[(1, 45), (2, 45), (3, 45)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 10), (3, 'left', 10)], parent='skin_joint_cl')
        cmds.checkBox('skin_jnt_cb', label="Jnt", annotation="Skinned Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jar_cb', label="Jar", annotation="Skinned Articulation Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jad_cb', label="Jad", annotation="Skinned Additional Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jcr_cb', label="Jcr", annotation="Skinned Corrective Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.checkBox('skin_jis_cb', label="Jis", annotation="Indirect Skinning Joints", align='left', value=1, changeCommand=self.ar.populateJoints, parent='skin_joint_display_rcl')
        cmds.textField('skin_joint_name_tf', width=30, changeCommand=self.ar.populateJoints, parent='skin_joint_cl')
        cmds.separator(style="none", height=3, parent='skin_joint_cl')
        cmds.textScrollList('skin_joint_tsl', width=30, height=500, allowMultiSelection=True, selectCommand=self.ar.actualizeSkinFooter, parent='skin_joint_cl')
        # -> skin_joint_tsl it'll be populated by joints...
        cmds.radioCollection('skin_joint_rc', edit=True, select="skin_dpar_joint_rb")
        # right
        cmds.columnLayout('skin_geo_cl', adjustableColumn=True, width=170, parent='skin_create_v2_pl')
        cmds.radioCollection('skin_geo_rc', parent='skin_geo_cl')
        cmds.radioButton('skin_all_geo_rb', label=self.ar.data.lang['i026_listAllJnts'], annotation="allGeoms", onCommand=self.ar.populateGeoms, parent='skin_geo_cl') #all geometries
        cmds.radioButton('skin_selected_geo_rb', label=self.ar.data.lang['i027_listSelJnts'], annotation="selGeoms", onCommand=self.ar.populateGeoms, parent='skin_geo_cl')
        cmds.checkBox('skin_geo_long_name_cb', label=self.ar.data.lang['i073_displayLongName'], align='left', value=1, changeCommand=self.ar.populateGeoms, parent='skin_geo_cl')
        cmds.checkBox('skin_log_win_cb', label=self.ar.data.lang['i286_displaySkinLog'], align='left', value=1, parent='skin_geo_cl')
        cmds.separator(style="none", height=2, parent='skin_geo_cl')
        cmds.textField('skin_geo_name_tf', width=30, changeCommand=self.ar.populateGeoms, parent='skin_geo_cl')
        cmds.separator(style="none", height=3, parent='skin_geo_cl')
        cmds.textScrollList('skin_geo_tcl', width=30, height=500, allowMultiSelection=True, selectCommand=self.ar.actualizeSkinFooter, parent='skin_geo_cl' )
        # -> skin_geo_tcl it'll be populated by geometries...
        cmds.radioCollection('skin_geo_rc', edit=True, select="skin_selected_geo_rb")
        # footer
        cmds.columnLayout('skin_footer_cl', adjustableColumn=True, parent='skin_create_fl')
        cmds.separator(style='none', height=3, parent='skin_footer_cl')
        cmds.button("skin_create_bt", label=self.ar.data.lang['i028_skinButton'], backgroundColor=(0.5, 0.8, 0.8), command=partial(self.ar.skin.skinFromUI), parent='skin_footer_cl')
        cmds.paneLayout("skin_add_remove_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_footer_cl')
        cmds.button("skin_add_bt", label=self.ar.data.lang['i063_skinAddBtn'], backgroundColor=(0.7, 0.9, 0.9), command=partial(self.ar.skin.skinFromUI, "Add"), parent='skin_add_remove_v2_pl')
        cmds.button("skin_remove_bt", label=self.ar.data.lang['i064_skinRemBtn'], backgroundColor=(0.1, 0.3, 0.3), command=partial(self.ar.skin.skinFromUI, "Remove"), parent='skin_add_remove_v2_pl')
        cmds.separator(style='none', height=5, parent='skin_footer_cl')
        # this text will be actualized by the number of joints and geometries in the textScrollLists for skinning:
        cmds.text('skin_footer_txt', align='center', label="0 "+self.ar.data.lang['i025_joints']+" 0 "+self.ar.data.lang['i024_geometries'], parent='skin_footer_cl')
        # skin copy
        cmds.frameLayout('skin_copy_fl', label=self.ar.data.lang['i287_copy']+" Skinning", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='skin_main_cl')
        cmds.rowLayout('skin_copy_rl', numberOfColumns=3, columnWidth3=(90, 90, 150), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent='skin_copy_fl')
        cmds.radioCollection('skin_surface_association_rc', parent='skin_copy_rl')
        cmds.radioButton('skin_closest_point_rb', label="closestPoint", annotation="closestPoint", parent='skin_copy_rl')
        cmds.radioButton('skin_uvspace_rb', label="uvSpace", annotation="uvSpace", parent='skin_copy_rl') #uvSpace
        cmds.paneLayout("skin_copy_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_copy_rl')
        cmds.button("skin_copy_one_source_bt", label=self.ar.data.lang['i290_oneSource'], backgroundColor=(0.4, 0.8, 0.9), command=partial(self.ar.skin.copySkinFromOneSource, None, True), annotation=self.ar.data.lang['i288_copySkinDesc'], parent='skin_copy_v2_pl')
        cmds.button("skin_copy_multi_source_bt", label=self.ar.data.lang['i146_same']+" "+self.ar.data.lang['m222_name'], backgroundColor=(0.5, 0.8, 0.9), command=partial(self.ar.skin.copySkinSameName, None, True), annotation=self.ar.data.lang['i289_sameNameSkinDesc'], parent='skin_copy_v2_pl')
        cmds.radioCollection('skin_surface_association_rc', edit=True, select="skin_closest_point_rb")
        # skin weights IO
        cmds.frameLayout('skin_weights_io_fl', label="SkinCluster weights IO", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='skin_main_cl')
        cmds.paneLayout("skin_weights_io_v2_pl", configuration="vertical2", separatorThickness=2.0, parent='skin_weights_io_fl')
        cmds.button("skin_weights_export_bt", label=self.ar.data.lang['i164_export'], backgroundColor=(0.4, 0.8, 0.9), command=partial(self.ar.skin.ioSkinWeightsByUI, True), annotation=self.ar.data.lang['i266_selected'], parent='skin_weights_io_v2_pl')
        cmds.button("skin_weights_import_bt", label=self.ar.data.lang['i196_import'], backgroundColor=(0.5, 0.8, 0.9), command=partial(self.ar.skin.ioSkinWeightsByUI, False), annotation=self.ar.data.lang['i266_selected'], parent='skin_weights_io_v2_pl')
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
        # controller color
        cmds.frameLayout('ctr_color_fl', label=self.ar.data.lang['m047_colorOver'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.tabLayout('ctr_color_tab', innerMarginWidth=5, innerMarginHeight=5, parent='ctr_color_fl')
        # color index
        cmds.gridLayout('ctr_color_index_gl', numberOfColumns=16, cellWidthHeight=(20, 20), parent='ctr_color_tab')
        # creating color buttons
        for colorIndex, colorValues in enumerate(self.ar.ctrls.getColorList()):
            cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.ar.ctrls.colorShape, color=colorIndex), parent='ctr_color_index_gl')
        # RGB layout:
        cmds.columnLayout('ctr_color_rgb_cl', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent='ctr_color_tab')
        cmds.separator(height=10, style='none', parent='ctr_color_rgb_cl')
        cmds.colorSliderGrp('ctr_color_rgb_csg', label='Color', columnAlign3=('right', 'left', 'left'), columnWidth3=(30, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=partial(self.ar.ctrls.setColorRGBByUI, slider='colorRGBSlider'), parent='ctr_color_rgb_cl')
        cmds.button("ctr_remove_override_color_bt", label=self.ar.data.lang['i046_remove'], command=self.ar.ctrls.removeColor, parent='ctr_color_rgb_cl')
        # outliner layout:
        cmds.columnLayout('ctr_color_outliner_cl', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent='ctr_color_tab')
        cmds.separator(height=10, style='none', parent='ctr_color_outliner_cl')
        cmds.colorSliderGrp('ctr_color_outliner_csg', label='Outliner', columnAlign3=('right', 'left', 'left'), columnWidth3=(45, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=partial(self.ar.ctrls.setColorOutlinerByUI, slider='colorOutlinerSlider'), parent='ctr_color_outliner_cl')
        cmds.button("ctr_remove_outliner_color_bt", label=self.ar.data.lang['i046_remove'], command=self.ar.ctrls.removeColor, parent='ctr_color_outliner_cl')
        # renaming color tabLayouts:
        cmds.tabLayout('ctr_color_tab', edit=True, tabLabel=(('ctr_color_index_gl', "Index"), ('ctr_color_rgb_cl', "RGB"), ('ctr_color_outliner_cl', "Outliner")))
        # setup controller
        cmds.frameLayout('ctr_default_value_fl', label=self.ar.data.lang['i270_defaultValues'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_default_value_v3_pl", configuration="vertical3", separatorThickness=2.0, parent='ctr_default_value_fl')
        cmds.button("ctr_reset_to_default_value_bt", label=self.ar.data.lang['i271_reset'], backgroundColor=(1.0, 0.9, 0.6), height=30, command=partial(self.ar.ctrls.setupDefaultValues, True), parent='ctr_default_value_v3_pl')
        cmds.button("ctr_set_default_value_bt", label=self.ar.data.lang['i272_set'], backgroundColor=(1.0, 0.8, 0.5), height=30, command=partial(self.ar.ctrls.setupDefaultValues, False), parent='ctr_default_value_v3_pl')
        cmds.button("ctr_setup_default_value_bt", label=self.ar.data.lang['i274_editor'], backgroundColor=(1.0, 0.6, 0.4), height=30, command=self.ar.ctrls.defaultValueEditor, parent='ctr_default_value_v3_pl')
        # create dontroller
        cmds.frameLayout('ctr_create_fl', label=self.ar.data.lang['i114_createControl'], collapsable=True, collapse=False, marginWidth=10, marginHeight=10, parent='ctr_main_cl')
        cmds.frameLayout('ctr_create_options_fl', label=self.ar.data.lang['i002_options'], collapsable=True, collapse=True, marginWidth=10, parent='ctr_create_fl')
        cmds.columnLayout('ctr_create_options_cl', adjustableColumn=True, width=50, rowSpacing=5, parent='ctr_create_options_fl')
        cmds.textFieldGrp('ctr_name_tfg', text="", label=self.ar.data.lang['i101_customName'], columnAlign2=("right", "left"), adjustableColumn2=2, columnAttach=((1, "right", 5), (2, "left", 5)), parent='ctr_create_options_cl')
        cmds.radioButtonGrp("ctr_action_rgb", label=self.ar.data.lang['i109_action'], labelArray3=[self.ar.data.lang['i108_newController'], self.ar.data.lang['i107_addShape'], self.ar.data.lang['i102_replaceShape']], vertical=True, numberOfRadioButtons=3, parent='ctr_create_options_cl')
        cmds.radioButtonGrp('ctr_action_rgb', edit=True, select=1) #new controller
        cmds.radioButtonGrp("ctr_degree_rgb", label=self.ar.data.lang['i103_degree'], labelArray2=[self.ar.data.lang['i104_linear'], self.ar.data.lang['i105_cubic']], vertical=True, numberOfRadioButtons=2, parent='ctr_create_options_cl')
        cmds.radioButtonGrp('ctr_degree_rgb', edit=True, select=1) #linear
        cmds.floatSliderGrp("ctr_size_fsg", label=self.ar.data.lang['i115_size'], field=True, minValue=0.01, maxValue=10.0, fieldMinValue=0, fieldMaxValue=100.0, precision=2, value=1.0, parent='ctr_create_options_cl')
        cmds.optionMenuGrp("ctr_direction_omg", label=self.ar.data.lang['i106_direction'], parent='ctr_create_options_cl')
        cmds.menuItem('ctr_direction_X_neg_mi', label='-X')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_X_pos_mi', label='+X')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Y_neg_mi', label='-Y')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Y_pos_mi', label='+Y')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Z_neg_mi', label='-Z')#, parent='ctr_direction_omg')
        cmds.menuItem('ctr_direction_Z_pos_mi', label='+Z')#, parent='ctr_direction_omg')
        cmds.optionMenuGrp('ctr_direction_omg', edit=True, value='+Y')
        # curve shapes
        cmds.frameLayout('ctr_shapes_fl', label=self.ar.data.lang['i100_curveShapes'], collapsable=True, collapse=True, parent='ctr_create_fl')
        cmds.gridLayout('ctr_simple_module_gl', numberOfColumns=8, cellWidthHeight=(40, 50), backgroundColor=(0.3, 0.3, 0.3), parent='ctr_shapes_fl')
        # -> ctr_simple_module_gl here we'll populate the control module layout with the items from Controllers folder:
        cmds.frameLayout('ctr_combined_shapes_fl', label=self.ar.data.lang['i118_combinedShapes'], collapsable=True, collapse=True, parent='ctr_create_fl')
        cmds.gridLayout('ctr_combined_module_gl', numberOfColumns=8, cellWidthHeight=(40, 50), backgroundColor=(0.3, 0.3, 0.3), parent='ctr_combined_shapes_fl')
        # -> ctr_combined_module_gl here we'll populate the control module layout with the items from Controllers folder:
        # edit seleted controller
        cmds.frameLayout('ctr_edit_selected_fl', label=self.ar.data.lang['i011_editSelected']+" "+self.ar.data.lang['i111_controller'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_edit_selected_v3_pl", configuration="vertical3", separatorThickness=2.0, parent="ctr_edit_selected_fl")
        cmds.button("ctr_add_shape_bt", label=self.ar.data.lang['i113_addShapes'], backgroundColor=(1.0, 0.6, 0.7), command=partial(self.ar.ctrls.transferShape, False, False), parent="ctr_edit_selected_v3_pl")
        cmds.button("ctr_copy_shape_bt", label=self.ar.data.lang['i112_copyShapes'], backgroundColor=(1.0, 0.6, 0.5), command=partial(self.ar.ctrls.transferShape, False, True), parent="ctr_edit_selected_v3_pl")
        cmds.button("ctr_replace_shape_bt", label=self.ar.data.lang['i110_transferShapes'], backgroundColor=(1.0, 0.6, 0.3), command=partial(self.ar.ctrls.transferShape, True, True), parent="ctr_edit_selected_v3_pl")
        cmds.paneLayout("ctr_edit_selected_v2_pl", configuration="vertical2", separatorThickness=2.0, parent="ctr_edit_selected_fl")
        cmds.button("ctr_reset_curve_bt", label=self.ar.data.lang['i121_resetCurve'], backgroundColor=(1.0, 0.7, 0.3), height=30, command=partial(self.ar.ctrls.resetCurve), parent="ctr_edit_selected_v2_pl")
        cmds.button("ctr_change_degree_bt", label=self.ar.data.lang['i120_changeDegree'], backgroundColor=(1.0, 0.8, 0.4), height=30, command=partial(self.ar.ctrls.resetCurve, True), parent="ctr_edit_selected_v2_pl")
        cmds.button("ctr_zero_out_grp_bt", label=self.ar.data.lang['i116_zeroOut'], backgroundColor=(0.8, 0.8, 0.8), height=30, command=self.ar.utils.zeroOut, parent="ctr_edit_selected_fl")
        cmds.button("ctr_select_all_bt", label=self.ar.data.lang['i291_selectAllControls'], backgroundColor=(0.9, 1.0, 0.6), height=30, command=partial(self.ar.ctrls.selectAllControls), parent="ctr_edit_selected_fl")
        # calibration controllers
        cmds.frameLayout('ctr_calibration_fl', label=self.ar.data.lang['i193_calibration'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_calibration_v2_pl", configuration="vertical2", separatorThickness=2.0, parent="ctr_calibration_fl")
        cmds.button("ctr_transfer_calibration_bt", label=self.ar.data.lang['i194_transfer'], backgroundColor=(0.5, 1.0, 1.0), height=30, command=self.ar.ctrls.transferCalibration, parent="ctr_calibration_v2_pl")
        cmds.button("ctr_import_calibration_bt", label=self.ar.data.lang['i196_import'], backgroundColor=(0.5, 0.8, 1.0), height=30, command=self.ar.ctrls.importCalibration, parent="ctr_calibration_v2_pl")
        # mirror calibration
        cmds.frameLayout('ctr_mirror_calibration_fl', label=self.ar.data.lang['m010_mirror']+" "+self.ar.data.lang['i193_calibration'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent="ctr_calibration_fl")
        cmds.rowColumnLayout('ctr_mirror_calibration_rcl', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="ctr_calibration_fl")
        cmds.text("ctr_mirror_calibration_prefix_txt", label=self.ar.data.lang['i144_prefix'], parent="ctr_mirror_calibration_rcl")
        cmds.text("ctr_mirror_calibration_from_prefix_txt", label=self.ar.data.lang['i036_from'], parent="ctr_mirror_calibration_rcl")
        cmds.textField('ctr_mirror_calibration_from_prefix_tf', text=self.ar.data.lang['p002_left']+"_", parent="ctr_mirror_calibration_rcl")
        cmds.text("ctr_mirror_calibration_to_prefix_txt", label=self.ar.data.lang['i037_to'], parent="ctr_mirror_calibration_rcl")
        cmds.textField('ctr_mirror_calibration_to_prefix_tf', text=self.ar.data.lang['p003_right']+"_", parent="ctr_mirror_calibration_rcl")
        cmds.button("ctr_mirror_calibration_bt", label=self.ar.data.lang['m010_mirror'], backgroundColor=(0.5, 0.7, 1.0), height=30, width=70, command=self.ar.ctrls.mirrorCalibration, parent="ctr_mirror_calibration_rcl")
        # control shape IO
        cmds.frameLayout('ctr_shape_io_fl', label=self.ar.data.lang['m067_shape']+" "+self.ar.data.lang['i199_io'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent='ctr_main_cl')
        cmds.paneLayout("ctr_shape_io_v4_pl", configuration="vertical4", separatorThickness=2.0, parent="ctr_shape_io_fl")
        cmds.button("ctr_shape_io_export_bt", label=self.ar.data.lang['i164_export'], backgroundColor=(1.0, 0.8, 0.8), height=30, command=self.ar.ctrls.exportShape, parent="ctr_shape_io_v4_pl")
        cmds.button("ctr_shape_io_import_bt", label=self.ar.data.lang['i196_import'], backgroundColor=(1.0, 0.9, 0.9), height=30, command=self.ar.ctrls.importShape, parent="ctr_shape_io_v4_pl")
        # mirror control shape
        cmds.frameLayout('ctr_mirror_shape_fl', label=self.ar.data.lang['m010_mirror']+" "+self.ar.data.lang['m067_shape'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent="ctr_shape_io_fl")
        cmds.rowColumnLayout('ctr_mirror_shape_rcl', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="ctr_shape_io_fl")
        cmds.optionMenu("ctr_mirror_shape_axis_om", label='', parent="ctr_mirror_shape_rcl")
        for x in self.ar.data.axis:
            cmds.menuItem('ctr_mirror_axis_'+x+'_mi', label=x, parent="ctr_mirror_shape_axis_om")
        cmds.text("ctr_mirror_shape_from_prefix_txt", label=self.ar.data.lang['i036_from'], parent="ctr_mirror_shape_rcl")
        cmds.textField('ctr_mirror_shape_from_prefix_tf', text=self.ar.data.lang['p002_left']+"_", parent="ctr_mirror_shape_rcl")
        cmds.text("ctr_mirror_shape_to_prefix_txt", label=self.ar.data.lang['i037_to'], parent="ctr_mirror_shape_rcl")
        cmds.textField('ctr_mirror_shape_to_prefix_tf', text=self.ar.data.lang['p003_right']+"_", parent="ctr_mirror_shape_rcl")
        cmds.button("ctr_mirror_shape_bt", label=self.ar.data.lang['m010_mirror'], backgroundColor=(1.0, 0.5, 0.5), height=30, width=70, command=self.ar.ctrls.resetMirrorShape, parent="ctr_mirror_shape_rcl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout('controllers_tab', edit=True,
                        attachForm=[('ctr_main_sl', 'top', 20), ('ctr_main_sl', 'left', 5), ('ctr_main_sl', 'right', 5), ('ctr_main_sl', 'bottom', 5)]
                        )


    def create_tools_layout(self):
        cmds.formLayout('tools_tab', numberOfDivisions=100, parent="main_tab")
        cmds.scrollLayout("tools_sl", parent="tools_tab")
        cmds.columnLayout("tools_module_cl", adjustableColumn=True, rowSpacing=3, parent="tools_sl")
        # -> tools_module_cl it will be filled further...
        cmds.formLayout("tools_tab", edit=True,
                        attachForm=[("tools_sl", 'top', 20), ("tools_sl", 'left', 5), ("tools_sl", 'right', 5), ("tools_sl", 'bottom', 5)]
                        )


    def create_validator_layout(self):
        cmds.formLayout('validator_tab', numberOfDivisions=100, parent="main_tab")
        cmds.scrollLayout("validator_sl", parent="validator_tab")
        cmds.columnLayout("validator_cl", adjustableColumn=True, rowSpacing=3, parent="validator_sl")
        # validators
        self.create_check_layout("i208_checkin", self.ar.data.checkin_instances, "validator_cl")
        self.create_check_layout("i209_checkout", self.ar.data.checkout_instances, "validator_cl")
        self.create_check_layout("i212_addOns", self.ar.data.checkaddon_instances, "validator_cl", False)
        self.create_check_layout("i354_finishing", self.ar.data.checkfinishing_instances, "validator_cl", False)
        # publisher
        cmds.columnLayout('validator_footer_cl', adjustableColumn=True, parent="validator_tab")
        cmds.separator(style='none', height=3, parent="validator_footer_cl")
        cmds.button("validator_publisher_bt", label=self.ar.data.lang['m046_publisher'], backgroundColor=(0.75, 0.75, 0.75), height=40, command=self.ar.publisher.mainUI, parent="validator_footer_cl")
        cmds.separator(style='none', height=5, parent="validator_footer_cl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout("validator_tab", edit=True,
                        attachForm=[("validator_sl", 'top', 20), ("validator_sl", 'left', 5), ("validator_sl", 'right', 5), ("validator_sl", 'bottom', 60), ("validator_footer_cl", 'left', 5), ("validator_footer_cl", 'right', 5), ("validator_footer_cl", 'bottom', 5)],
                        attachNone=[("validator_footer_cl", 'top')]
                        )


    def create_rebuilder_layout(self):
        cmds.formLayout("rebuilder_tab", numberOfDivisions=100, parent="main_tab")
        # project pipeline asset
        cmds.columnLayout('asset_main_cl', adjustableColumn=False, parent="rebuilder_tab")
        cmds.frameLayout('asset_fl', label=self.ar.data.lang['i303_asset'], collapsable=True, collapse=False, width=370, parent="asset_main_cl")
        cmds.textFieldGrp("asset_maya_project_tfg", label="Maya "+self.ar.data.lang['i301_project']+":", text=self.ar.pipeliner.pipeData['mayaProject'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent="asset_fl")
        cmds.textFieldGrp("asset_pipeline_tfg", label="Pipeline:", text=self.ar.pipeliner.pipeData['projectPath'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent="asset_fl")
        cmds.textFieldGrp("asset_name_tfg", label=self.ar.data.lang['i303_asset']+":", text=self.ar.pipeliner.pipeData['assetName'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent="asset_fl")
        # asset buttons
        cmds.rowColumnLayout("asset_buttons_rcl", numberOfColumns=5, columnAlign=[(1, "left"), (2, "left"), (3, "left"), (4, "left"), (5, "left")], columnAttach=[(1, "left", 10), (2, "left", 10), (3, "left", 10), (4, "left", 10), (5, "left", 10)], parent="asset_fl")
        cmds.button("asset_save_version_bt", label=self.ar.data.lang['i222_save']+" "+self.ar.data.lang['m205_version'], command=self.ar.pipeliner.saveVersion, parent="asset_buttons_rcl")
        cmds.button("asset_load_bt", label=self.ar.data.lang['i187_load'], command=self.ar.pipeliner.loadAsset, parent="asset_buttons_rcl")
        cmds.button("asset_new_bt", label=self.ar.data.lang['i304_new'], command=self.ar.pipeliner.createNewAssetUI, parent="asset_buttons_rcl")
        cmds.button("asset_open_folder_bt", label=self.ar.data.lang['c108_open']+" "+self.ar.data.lang['i298_folder'], command=partial(self.ar.packager.openFolder, self.ar.pipeliner.pipeData['projectPath']), parent="asset_buttons_rcl")
        cmds.button("asset_replace_data_bt", label=self.ar.data.lang['m219_replace']+" "+self.ar.data.dp_data, command=partial(self.ar.pipeliner.loadAsset, mode=1), parent="asset_buttons_rcl")
        cmds.separator(style='in', height=20, width=370, parent="asset_main_cl")
        # processes
        cmds.rowColumnLayout('processes_rcl', adjustableColumn=1, numberOfColumns=2, columnAlign=[(1, "left"), (2, "right")], columnWidth=[(1, 360), (2, 17)], columnAttach=[(1, "both", 10), (2, "right", 10)], parent="rebuilder_tab")
        cmds.text('processes_io_txt', label=self.ar.data.lang['i292_processes'].upper()+" IO", font="boldLabelFont", parent="processes_rcl")
        cmds.iconTextButton("rebuilder_tri_collapse_itb", image=self.ar.data.icon['triRight'], annotation=self.ar.data.lang['i348_triangleIconAnn'], command=partial(self.ar.ui_manager.collapse_all_fl, "rebuilder_tri_collapse_itb", 1), width=17, height=17, style='iconOnly', align='right', parent="processes_rcl")
        cmds.scrollLayout("rebuilder_main_sl", parent="rebuilder_tab")
        cmds.columnLayout("rebuilder_cl", adjustableColumn=True, rowSpacing=3, parent="rebuilder_main_sl")
        # -> rebuilder_cl it will be filled futher...
        cmds.separator(style='none', parent="rebuilder_cl")
        # -> these formLayouts will be filled futher...
        cmds.frameLayout('rebuilder_start_fl', label=self.ar.data.lang['c110_start'].upper(), collapsable=True, collapse=True, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        cmds.frameLayout('rebuilder_source_fl', label=self.ar.data.lang['i331_source'].upper(), collapsable=True, collapse=True, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        cmds.frameLayout('rebuilder_setup_fl', label=self.ar.data.lang['i332_setup'].upper(), collapsable=True, collapse=True, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        cmds.frameLayout('rebuilder_deforming_fl', label=self.ar.data.lang['i333_deforming'].upper(), collapsable=True, collapse=True, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        cmds.frameLayout('rebuilder_custom_fl', label=self.ar.data.lang['i334_custom'].upper(), collapsable=True, collapse=True, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent="rebuilder_cl")
        cmds.separator(style='none', parent="rebuilder_cl")
        # rebuilder
        cmds.columnLayout('rebuilder_footer_cl', adjustableColumn=False, parent="rebuilder_tab")
        cmds.separator(style='in', height=20, width=370, parent="rebuilder_footer_cl")
        cmds.checkBox("rebuilder_select_all_cb", label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all']+" "+self.ar.data.lang['i292_processes'].lower(), value=True, changeCommand=partial(self.ar.changeActiveAllModules, self.ar.data.rebuilder_instances), parent="rebuilder_footer_cl")
        cmds.separator(style='none', height=10, parent="rebuilder_footer_cl")
        cmds.paneLayout("rebuilder_selected_pl", configuration="vertical2", separatorThickness=7.0, width=370, parent="rebuilder_footer_cl")
        cmds.button("rebuilder_split_data_bt", label=self.ar.data.lang['r002_splitData'].upper(), command=partial(self.ar.runSelectedActions, self.ar.data.rebuilder_instances, True, True, actionType="r000_rebuilder"), parent="rebuilder_selected_pl")
        cmds.button("rebuilder_rebuild_bt", label=self.ar.data.lang['r001_rebuild'].upper(), command=partial(self.ar.runSelectedActions, self.ar.data.rebuilder_instances, False, True, actionType="r000_rebuilder"), parent="rebuilder_selected_pl")
        cmds.separator(style='none', height=10, parent="rebuilder_footer_cl")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout("rebuilder_tab", edit=True,
                        attachForm=[("rebuilder_main_sl", 'left', 5), ("rebuilder_main_sl", 'right', 5), ("rebuilder_main_sl", 'bottom', 80), 
                                    ("asset_main_cl", 'left', 5), ("asset_main_cl", 'right', 5), ("asset_main_cl", 'top', 15),
                                    ("rebuilder_footer_cl", 'left', 5), ("rebuilder_footer_cl", 'right', 5), ("rebuilder_footer_cl", 'bottom', 5)],
                        attachControl=[("rebuilder_main_sl", 'top', 10, "processes_rcl"), ("processes_rcl", 'top', 10, "asset_main_cl")],
                        attachNone=[("rebuilder_footer_cl", 'top')]
                        )


    def create_check_layout(self, name, instances, layout, visible=True):
        cmds.frameLayout(name+"_fl", label=self.ar.data.lang[name].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, visible=visible, parent=layout)
        cmds.columnLayout(name+"_module_cl", adjustableColumn=True, parent=name+"_fl") #rowSpacing=3
        # it'll be filled further...
        cmds.separator(style="none", parent=name+"_fl")
        cmds.checkBox(name+"_select_all_cb", label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all']+" "+self.ar.data.lang[name], value=False, changeCommand=partial(self.ar.changeActiveAllModules, instances), parent=name+"_fl")
        cmds.paneLayout(name+"_select_v2_pl", configuration="vertical2", separatorThickness=7.0, parent=name+"_fl")
        cmds.button(name+"_veryfy_all_bt", label=self.ar.data.lang['i210_verify'].upper(), command=partial(self.ar.runSelectedActions, instances, True, True), parent=name+"_select_v2_pl")
        cmds.button(name+"_fix_all_bt", label=self.ar.data.lang['c052_fix'].upper(), command=partial(self.ar.runSelectedActions, instances, False, True), parent=name+"_select_v2_pl")
        cmds.separator(height=30, parent=name+"_fl")


            

    


    

    
    # def refresh_main_ui(self, savedScene=False, resetButtons=True, clearSel=False, *args):
    #     """ Read guides, joints, geometries and refresh the UI without reload the script creating a new instance.
    #         Useful to rebuilding process when creating a new scene
    #     """
    #     if savedScene:
    #         self.selList = cmds.ls(selection=True)
    #         self.rebuilding = False
    #     self.ar.fill_created_guides()
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


    




# WIP

class Fill(object):
    def __init__(self, ar):
        self.ar = ar
        self.validator_folders = [self.ar.data.checkin_folder, 
                                  self.ar.data.checkout_folder]
        self.rebuilder_folders = [ self.ar.data.rebuilder_folder,
                                   self.ar.data.start_folder,
                                   self.ar.data.source_folder,
                                   self.ar.data.setup_folder,
                                   self.ar.data.deforming_folder,
                                   self.ar.data.custom_folder]


    def start_library(self):
        self.start_modules()
        self.load_pipeline_validator()
        self.set_validator_preset()


    def start_modules(self):
        # rigging
        self.ar.startGuideModules(self.ar.data.standard_folder, "start")
        self.ar.startGuideModules(self.ar.data.integrated_folder, "start")
        # controllers
        self.ar.startGuideModules(self.ar.data.curve_simple_folder, "start")
        self.ar.startGuideModules(self.ar.data.curve_combined_folder, "start")
        # tools
        self.ar.startGuideModules(self.ar.data.tools_folder, "start")
        # validators
        self.ar.startGuideModules(self.ar.data.checkin_folder, "start")
        self.ar.startGuideModules(self.ar.data.checkout_folder, "start")
        if self.ar.pipeliner.pipeData['addOnsPath'] and self.ar.config.get_validator_addons():
            self.ar.startGuideModules("", "start", path=self.ar.pipeliner.pipeData['addOnsPath'])
            self.ar.data.checkaddon_folder = self.ar.pipeliner.pipeData['addOnsPath']
        if self.ar.pipeliner.pipeData['finishingPath'] and self.ar.config.get_validator_addons("finishingPath"):
            self.ar.startGuideModules("", "start", path=self.ar.pipeliner.pipeData['finishingPath'])
            self.ar.data.checkfinishing_folder = self.ar.pipeliner.pipeData['finishingPath']
        # rebuilders
        self.ar.startGuideModules(self.ar.data.start_folder, "start")
        self.ar.startGuideModules(self.ar.data.source_folder, "start")
        self.ar.startGuideModules(self.ar.data.setup_folder, "start")
        self.ar.startGuideModules(self.ar.data.deforming_folder, "start")
        self.ar.startGuideModules(self.ar.data.custom_folder, "start")


    def load_pipeline_validator(self):
        """ Load the Validator's presets from the pipeline path.
        """
        if self.ar.pipeliner.pipeData['presetsPath']:
            if os.path.exists(self.ar.pipeliner.pipeData['presetsPath']):
                studio_preset, studio_preset_data = self.ar.config.get_json_file_content(self.ar.pipeliner.pipeData['presetsPath']+"/", True)
                if studio_preset:
                    self.ar.data.validator_preset = studio_preset_data[studio_preset[0]]
                    self.ar.data.validator_preset_data.update(studio_preset_data)
                    cmds.menuItem(f"{self.ar.data.validator_preset['_preset']}_mi", label=self.ar.data.validator_preset["_preset"], radioButton=False, collection="validator_preset_rbc", parent="validator_preset_menu")
                    cmds.menuItem(f"{self.ar.data.validator_preset['_preset']}_mi", edit=True, radioButton=True, collection="validator_preset_rbc")

    
    def set_validator_preset(self):
        check_instances = self.ar.data.lib[self.ar.data.checkin_folder]["instances"] + self.ar.data.lib[self.ar.data.checkout_folder]["instances"]
        if self.ar.data.checkaddon_folder in self.ar.data.lib.keys():
            check_instances = check_instances + self.ar.data.lib[self.ar.data.checkaddon_folder]["instances"]
        if self.ar.data.checkfinishing_folder in self.ar.data.lib.keys():
            check_instances = check_instances + self.ar.data.lib[self.ar.data.checkfinishing_folder]["instances"]
        if check_instances:
            for validator_name in self.ar.data.validator_preset:
                for validator_instance in check_instances:
                    if validator_name == validator_instance.name:
                        validator_instance.changeActive(self.ar.data.validator_preset_data[self.ar.data.validator_preset["_preset"]][validator_instance.name])
    
    
    def fill_library(self):
        # rigging
        for item in self.ar.data.lib[self.ar.data.standard_folder]["instances"]:
            self.populate_library(item, self.ar.data.standard_folder, "rig_guides_standard_cl")
        for item in self.ar.data.lib[self.ar.data.integrated_folder]["instances"]:
            self.populate_library(item, self.ar.data.integrated_folder, "rig_guides_integrated_cl")
        # controllers
        for item in self.ar.data.lib[self.ar.data.curve_simple_folder]["instances"]:
            self.populate_library(item, self.ar.data.curve_simple_folder, "ctr_simple_module_gl")
        for item in self.ar.data.lib[self.ar.data.curve_combined_folder]["instances"]:
            self.populate_library(item, self.ar.data.curve_combined_folder, "ctr_combined_module_gl")
        # tools
        for item in self.ar.data.lib[self.ar.data.tools_folder]["instances"]:
            self.populate_library(item, self.ar.data.tools_folder, "tools_module_cl")
        # validators
        for item in self.ar.data.lib[self.ar.data.checkin_folder]["instances"]:
            self.populate_library(item, self.ar.data.checkin_folder, "i208_checkin_module_cl")
        for item in self.ar.data.lib[self.ar.data.checkout_folder]["instances"]:
            self.populate_library(item, self.ar.data.checkout_folder, "i209_checkout_module_cl")
        if self.ar.data.checkaddon_folder:
            for item in self.ar.data.lib[self.ar.data.checkaddon_folder]["instances"]:
                cmds.frameLayout('i212_addOns_fl', edit=True, visible=True)
                self.populate_library(item, "", "i212_addOns_module_cl")
        if self.ar.data.checkfinishing_folder:
            for item in self.ar.data.lib[self.ar.data.checkfinishing_folder]["instances"]:
                cmds.frameLayout('i354_finishing_fl', edit=True, visible=True)
                self.populate_library(item, "", "i354_finishing_module_cl")
        # rebuilders
        for item in self.ar.data.lib[self.ar.data.start_folder]["instances"]:
            self.populate_library(item, self.ar.data.start_folder, "rebuilder_start_fl", 6)
        for item in self.ar.data.lib[self.ar.data.source_folder]["instances"]:
            self.populate_library(item, self.ar.data.source_folder, "rebuilder_source_fl", 6)
        for item in self.ar.data.lib[self.ar.data.setup_folder]["instances"]:
            self.populate_library(item, self.ar.data.setup_folder, "rebuilder_setup_fl", 6)
        for item in self.ar.data.lib[self.ar.data.deforming_folder]["instances"]:
            self.populate_library(item, self.ar.data.deforming_folder, "rebuilder_deforming_fl", 6)
        for item in self.ar.data.lib[self.ar.data.custom_folder]["instances"]:
            self.populate_library(item, self.ar.data.custom_folder, "rebuilder_custom_fl", 6)


    def populate_library(self, item, folder, layout, columns=5):
        if cmds.layout(layout, query=True, exists=True):
            icon_name = self.ar.ui_manager.get_icon_name(item)
            if folder == self.ar.data.curve_simple_folder or folder == self.ar.data.curve_combined_folder:
                cmds.iconTextButton(image=self.ar.data.icon[icon_name], label=item.name, annotation=item.name, height=32, width=32, command=partial(item.cvMain, True), parent=layout)
                return
#            module_layout = cmds.rowLayout(item.title+"_rl", numberOfColumns=columns, columnWidth3=(32, 55, 17), height=32, adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 0), (3, 'both', 2), (4, 'both', 2), (5, 'left', 2)], parent=layout)
            module_layout = cmds.rowLayout(numberOfColumns=columns, columnWidth3=(32, 55, 17), height=32, adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 0), (3, 'both', 2), (4, 'both', 2), (5, 'left', 2)], parent=layout)
            cmds.image(item.title+"_img", image=self.ar.data.icon[icon_name], width=32, parent=module_layout)
            if folder == self.ar.data.standard_folder:
                cmds.button(item.title+'_bt', label=self.ar.data.lang[item.title], height=32, command=item.build_raw_guide, parent=module_layout)
            elif folder == self.ar.data.integrated_folder:
                cmds.button(item.title+'_bt', label=self.ar.data.lang[item.title], height=32, command=item.build_template, parent=module_layout)
            elif folder == self.ar.data.tools_folder:
                cmds.button(item.title+'_bt', label=self.ar.data.lang[item.title], height=32, width=200, command=item.build_tool, parent=module_layout)
            else:
                item.actionCB = cmds.checkBox(label=self.ar.data.lang[item.title], value=item.active, changeCommand=item.changeActive, parent=module_layout)
                item.firstBT = cmds.button(label=item.firstBTLabel, width=45, command=partial(item.runAction, True), backgroundColor=(0.5, 0.5, 0.5), enable=item.firstBTEnable, parent=module_layout)
                item.secondBT = cmds.button(label=item.secondBTLabel.capitalize(), width=45, command=partial(item.runAction, False), backgroundColor=(0.5, 0.5, 0.5), enable=item.secondBTEnable, parent=module_layout)
                if folder == "" or folder in self.validator_folders:
                    if item.customName:
                        cmds.checkBox(item.actionCB, edit=True, label=item.customName)
                        item.title = item.customName
                if folder in self.rebuilder_folders:
                    item.deleteDataITB = cmds.iconTextButton(image=self.ar.data.icon['xDelete'], height=30, width=30, style='iconOnly', command=item.deleteData, enable=item.deleteDataBTEnable, annotation=self.ar.data.lang['r058_deleteDataAnn'], parent=module_layout)
                    item.updateActionButtons(color=False)
            cmds.iconTextButton(item.title+"_itb", image=self.ar.data.icon['info'], height=30, width=30, style='iconOnly', command=partial(self.ar.logger.infoWin, item.title, item.description, None, 'center', 305, 250, wiki=item.wiki), parent=module_layout)





class Manager(object):
    def __init__(self, ar):
        print("init manager")
        self.ar = ar


    def reload_ui(self, opt_var=None, item=None, *args):
        """ This method will set the given optionVar and reload the dpAutoRigSystem UI.
        """
        if opt_var and item:
            self.ar.opt.set_option_var(opt_var, item)
        cmds.evalDeferred("ar = dpAutoRig.Start("+str(self.ar.dev)+", intro=False); ar.ui();", lowestPriority=True)

    
    def reload_dev_mode_ui(self, *args):
        """ Reload the system code as development mode.
        """
        value = True
        if cmds.menuItem('dev_mode_mi', query=True, exists=True):
            value = cmds.menuItem('dev_mode_mi', query=True, checkBox=True)
        if value:
            cmds.evalDeferred("from importlib import reload; reload(dpAutoRigSystem); ar = dpAutoRig.Start(dev=True, intro=False); ar.ui();", lowestPriority=True)
        else:
            cmds.evalDeferred("ar = dpAutoRig.Start(); ar.ui();", lowestPriority=True)


    def refresh_ui(self, savedScene=False, resetButtons=True, clearSel=False):
        """ Read guides, joints, geometries and refresh the UI without reload the script creating a new instance.
            Useful to rebuilding process when creating a new scene
        """
        
        #
        # WIP
        #
        #
        # TODO: delete main frame layout and call the loadUI again?
        #       or just clear filled layouts and fill them again?
        #
        # TODO: check all validators active checkboxes?
        #

#            def refreshMainUI(self, savedScene=False, resetButtons=True, clearSel=False, *args):

        if savedScene:
            self.selList = cmds.ls(selection=True)
            self.ar.data.rebuilding = False
        #clear layouts
        self.clear_guide_layout()
        self.fill_created_guides()

#        self.checkImportedGuides()
#        self.checkGuideNets()
#        self.populateJoints()
#        self.populateGeoms()
#        if not self.ar.data.rebuilding:
#            if resetButtons:
#                self.resetAllButtonColors()
#            self.pipeliner.refreshAssetData()
#            for rebuildInstance in self.rebuilderInstanceList:
#                rebuildInstance.updateActionButtons(color=False)
#        try:
#            self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=False, compressUndo=True)
#        except:
#            self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=False, killWithScene=False, compressUndo=True)
#        if savedScene:
#            cmds.select(clear=True)
#            if self.selList:
#                cmds.select(self.selList)
#        if clearSel:
#            cmds.select(clear=True)
#        self.ar.data.rebuilding = False


    def clear_guide_layout(self):
        if self.ar.data.ui_state:

            print("cleared layout here....")
            
            cmds.frameLayout('rig_edit_selected_module_fl', edit=True, label=self.ar.data.lang['i011_editSelected'], collapsable=True, collapse=False, parent='rigging_tab')
            if cmds.columnLayout("rig_guides_inst_cl", query=True, exists=True):
                cmds.deleteUI('rig_guides_inst_cl')
            if cmds.columnLayout("rig_selected_module_cl", query=True, exists=True):
                cmds.deleteUI('rig_selected_module_cl')
            cmds.columnLayout('rig_guides_inst_cl', adjustableColumn=True, width=200, parent='rig_guides_inst_sl')
            cmds.columnLayout('rig_selected_module_cl', adjustableColumn=True, parent='rig_edit_selected_module_fl')


    def fill_created_guides(self, *args):
        """ Read all guide modules loaded in the scene and re-create the elements in the module_layout.
        """
        
        print("entered here 000000 -----------------------------------", self.ar.data.created_guides)
        print("lib =", self.ar.data.lib)

        # create a new list in order to store all created guide modules in the scene and its userSpecNames:
        self.ar.data.created_guides = []
        self.ar.data.standard_instances = []
        # list all namespaces:
        cmds.namespace(setNamespace=":")
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        # find path where 'dpAutoRig.py' is been executed:
        path = self.ar.data.dp_auto_rig_path
        guideDir = self.ar.data.standard_folder
        # find all module names:
        moduleNameInfo = self.ar.utils.findAllModuleNames(path, guideDir)
        validModules = moduleNameInfo[0]
        validModuleNames = moduleNameInfo[1]
        
        # check if there is "__" (double undersore) in the namespaces:
        for n in namespaceList:
            divString = n.partition("__")
            if divString[1] != "":
                module = divString[0]
                userSpecName = divString[2]
                if module in validModuleNames:
                    index = validModuleNames.index(module)
                    # check if there is this module guide base in the scene:
                    curGuideName = validModuleNames[index]+"__"+userSpecName+":"+self.ar.data.guide_base_name
                    if cmds.objExists(curGuideName):
                        self.ar.data.created_guides.append([validModules[index], userSpecName, curGuideName])
                    else:
                        cmds.namespace(moveNamespace=(n, ':'), force=True)
                        cmds.namespace(removeNamespace=n, deleteNamespaceContent=True, force=True)

#        self.clearGuideLayout()
        print("self.ar.data.created_guides ====", self.ar.data.created_guides)

        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.ar.data.created_guides:
            sortedAllGuidesList = sorted(self.ar.data.created_guides, key=lambda userSpecName: userSpecName[1])
            # load again the modules:
            guideFolder = self.ar.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")+"."+self.ar.data.standard_folder.replace("/", ".")
            
            print("guideFolder =", guideFolder)
            
            # this list will be used to rig all modules pressing the RIG button:
            for module in sortedAllGuidesList:
                mod = __import__(guideFolder+"."+module[0], {}, {}, [module[0]])
                
                print("mod =", mod)
                #print("mod.name", mod.name)
                
                if self.ar.dev:
                    reload(mod)
                # identify the guide modules and add to the moduleInstancesList:
                moduleClass = getattr(mod, mod.CLASS_NAME)
                
                print("moduleClass =", moduleClass)
                
                if "rigType" in cmds.listAttr(module[2]):
                    curRigType = cmds.getAttr(module[2]+".rigType")
                    moduleInst = moduleClass(self.ar)#, module[1], curRigType)
                else:
                    if "Style" in cmds.listAttr(module[2]):
                        iStyle = cmds.getAttr(module[2]+".Style")
                        if (iStyle == 0 or iStyle == 1):
                            moduleInst = moduleClass(self.ar, module[1], self.ar.data.rig_type_biped)
                        else:
                            moduleInst = moduleClass(self.ar, module[1], self.ar.data.rig_type_quadruped)
                    else:
                        moduleInst = moduleClass(self.ar, module[1], self.ar.data.rig_type_default)
                
                print("moduleInst =", moduleInst)
                
                self.ar.data.standard_instances.append(moduleInst)
                print("moduleInst.userGuideName before =", moduleInst.userGuideName)
                #moduleInst.userGuideName = module[1]
                moduleInst.get_namespace_for_it(module[1])
                print("moduleInst.userGuideName after =", moduleInst.userGuideName)

                #print("self.ar.data.standard_instances = ", self.ar.data.standard_instances)
                if self.ar.data.ui_state:
                    moduleInst.load_raw_guide(moduleInst.userGuideName)


                # reload pinGuide scriptJob:
                self.ar.ctrls.startPinGuide(module[2])
        
        # edit the footer A text:
        if self.ar.data.ui_state:
            self.modulesToBeRiggedList = self.ar.utils.getModulesToBeRigged(self.ar.data.standard_instances)
            print("modulesToBeRiggedList XXXX = ", self.modulesToBeRiggedList)
            # for guide in self.ar.data.standard_instances:
            #     #print("guide =", cmds.getAttr(guide.moduleGrp+".moduleNamespace"))
                
            #     #guide.load_raw_guide(cmds.getAttr(guide.moduleGrp+".moduleNamespace"))

            #     guideNet = self.ar.utils.getNodeByMessage("net", guide.moduleGrp)
            #     if guideNet:
            #         if cmds.getAttr(self.guideNet+".rawGuide"):
            #             userGuideName = cmds.getAttr(self.guideNet+".guideNumber")
            #             print("guide.userGuideName zzzzzzz =", userGuideName)
            #             #guide.load_raw_guide(guide)
            cmds.text('rig_footer_txt', edit=True, label=str(len(self.modulesToBeRiggedList))+" "+self.ar.data.lang['i005_footerRigging'])



    def delete_exist_window(self, *args):
        """ Check if there are the dpAutoRigWindow and a control element to delete the UI.
        """
        if cmds.workspaceControl(self.ar.data.workspace_control_name, query=True, exists=True):
            cmds.workspaceControl(self.ar.data.workspace_control_name, edit=True, close=True)
            #cmds.deleteUI("dpAutoRigSystemWC", control=True)
        win_names = [
                        "dpARLoadWin", 
                        "dpInfoWindow", 
                        "dpNewAssetWindow", 
                        "dpReplaceDPDataWindow", 
                        "dpSelectAssetWindow", 
                        "dpSaveVersionWindow", 
                        self.ar.data.plus_info_win_name, 
                        self.ar.data.color_override_win_name
                       ]
        for win_name in win_names:
            self.ar.utils.closeUI(win_name)
        self.set_ui_state(False)

    
    def set_ui_state(self, value):
        self.ar.data.ui_state = value


    def collapse_all_fl(self, iconTB="rig_tri_collapse_guides_itb", layout=0, *args):
        """ Edit the current module frame layout collapse and icon.
            Layout number:
            0 = guide module frame layouts
            1 = rebuilder processes frame layouts
        """
        collapse_value = True
        icon = self.ar.data.icon['triRight']
        if layout == 0: #guide modules
            modules = self.ar.data.standard_instances
            if self.ar.data.modules_collapse_status:
                collapse_value = False
                icon = self.ar.data.icon['triDown']
            self.ar.data.modules_collapse_status = collapse_value
        else: #rebuilder processes
            modules = self.ar.data.rebuilder_layouts
            if self.ar.data.rebuilders_collapse_status:
                collapse_value = False
                icon = self.ar.data.icon['triDown']
            self.ar.data.rebuilders_collapse_status = collapse_value
        if modules:
            for item in modules:
                if layout == 0:
                    cmds.frameLayout(item.moduleFrameLayout, edit=True, collapse=collapse_value)
                else:
                    cmds.frameLayout(item, edit=True, collapse=collapse_value)
        cmds.iconTextButton(iconTB, edit=True, image=icon)


    def get_icon_name(self, item, alternative="addOn"):
        icon_name = "AR"
        if hasattr(item, "name"):
            icon_name = item.name[0].lower()+item.name[1:]
        if not icon_name in self.ar.data.icon.keys():
            icon_name = alternative
        return icon_name
