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
        #self.ar.autoCheckOptionVar("dpAutoRigAutoCheckUpdate", "dpAutoRigLastDateAutoCheckUpdate", "update")
        #self.ar.autoCheckOptionVar("dpAutoRigAgreeTermsCond", "dpAutoRigLastDateAgreeTermsCond", "terms")
        #self.refresh_main_ui()
        #self.ar.startScriptJobs()
        #self.ar.utils.closeUI("dpARLoadWin")
        #cmds.select(startSelList)
        #print("dpAutoRigSystem "+self.ar.lang['i346_loadedSuccess'])


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




    def create_radio_menu(self, name, parent_menu, folder, default, option_var=None):
        menu_name = f"{name}_menu"
        collection_name = f"{name}_rbc"
        cmds.menuItem(menu_name, label=name.capitalize().replace("_", " "), parent=parent_menu, subMenu=True)
        cmds.radioMenuItemCollection(collection_name)
        
        #founds, lang_data = self.ar.getJsonFileInfo(folder)
        founds = self.ar.config.get_json_file_content(folder)[0]
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

    def create_menus(self):
        cmds.menuBarLayout("main_menu_bar", parent="dpAutoRigSystemWC")
        # settings menu:
        cmds.menu('settings_menu', label='Settings', parent='main_menu_bar')
        self.create_radio_menu("language", "settings_menu", self.ar.data.language_folder, self.ar.data.language_default, self.ar.data.language_option_var)
        self.create_radio_menu("controller_preset", "settings_menu", self.ar.data.curves_presets_folder, self.ar.data.controller_default, self.ar.data.controller_option_var)
        self.create_radio_menu("validator_preset", "settings_menu", self.ar.data.validator_presets_folder, self.ar.data.validator_default, self.ar.data.validator_option_var)
        
        # if self.ar.pipeliner.pipeData['presetsPath']:
        #     self.loadPipelineValidatorPresets()

        # create menu:
        cmds.menu('create_menu', label='Create', parent='main_menu_bar')
        cmds.menuItem('translator_mi', label='Translator', command=self.ar.translator, parent='create_menu')
        cmds.menuItem('pipeliner_mi', label='Pipeliner', command=self.ar.config.open_pipeliner, parent='create_menu')
        
        cmds.menuItem('create_control_preset_mi', label='Controllers Preset', command=partial(self.ar.config.create_preset, "controls", self.ar.data.curves_presets_folder, True), parent='create_menu')
        cmds.menuItem('create_validator_preset_mi', label='Validator Preset', command=partial(self.ar.config.create_preset, "validator", self.ar.data.validator_presets_folder, False), parent='create_menu')
        # window menu:
        cmds.menu('window_menu', label='Window', parent='main_menu_bar')
        cmds.menuItem('dev_mode_mi', label='Dev mode', checkBox=self.ar.dev, command=self.reload_dev_mode_ui, parent='window_menu')
        cmds.menuItem('reload_ui_mi', label='Reload UI', command=self.reload_ui, parent='window_menu')
        cmds.menuItem('quit_mi', label='Quit', command=self.deleteExistWindow, parent='window_menu')
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
        if self.ar.dev:
            cmds.menu('dev_menu', label='Dev', parent='main_menu_bar')
            cmds.menuItem('verbose_mi', label='Verbose', checkBox=self.ar.verbose, command=self.change_verbose)




    def main_ui(self):
        """ Create the layouts inside of the mainLayout. Here will be the entire User Interface.
        """
        self.create_menus()

        return
        # TODO: remove the allUIs dict:
        self.allUIs = {}



        self.langName = self.ar.getCurrentMenuValue(self.langList)
        self.presetName = self.ar.getCurrentMenuValue(self.presetList)
        # optimize dictionaries
        self.lang = self.langDic[self.langName]
        self.ctrlPreset = self.presetDic[self.presetName]
        
        # -- Initialize some objects here:

        # self.ctrls = dpControls.ControlClass(self.ar)
        # self.publisher = dpPublisher.Publisher(self.ar)
        # self.customAttr = dpCustomAttr.CustomAttr(self.ar, False)
        # self.skin = dpSkinning.Skinning(self.ar)
        # self.logger = dpLogger.Logger(self.ar)

        # create menu:
        # self.allUIs["createMenu"] = cmds.menu('createMenu', label='Create')
        # cmds.menuItem('translator_MI', label='Translator', command=self.translator)
        # cmds.menuItem('pipeliner_MI', label='Pipeliner', command=partial(self.ar.pipeliner.mainUI, self))
        # cmds.menuItem('createControlPreset_MI', label='Controllers Preset', command=partial(self.createPreset, "controls", self.ar.curvesPresetsFolder, True))
        # cmds.menuItem('createValidatorPreset_MI', label='Validator Preset', command=partial(self.createPreset, "validator", self.ar.validatorPresetsFolder, False))
        # window menu:
        # self.allUIs["windowMenu"] = cmds.menu('windowMenu', label='Window')
        # cmds.menuItem('devMode_MI', label='Dev mode', checkBox=self.dev, command=self.reloadDevModeUI)
        # cmds.menuItem('reloadUI_MI', label='Reload UI', command=self.reloadMainUI)
        # cmds.menuItem('quit_MI', label='Quit', command=self.deleteExistWindow)
        # help menu:
        self.allUIs["helpMenu"] = cmds.menu('helpMenu', label='Help', helpMenu=True)
        cmds.menuItem('about_MI"', label='About', command=partial(self.logger.infoWin, 'm015_about', 'i006_aboutDesc', self.ar.dpARVersion, 'center', 305, 250))
        cmds.menuItem('author_MI', label='Author', command=partial(self.logger.infoWin, 'm016_author', 'i007_authorDesc', None, 'center', 305, 250))
        cmds.menuItem('collaborators_MI', label='Collaborators', command=partial(self.logger.infoWin, 'i165_collaborators', 'i166_collabDesc', "\n\n"+self.langDic[self.englishName]['_collaborators'], 'center', 305, 250))
        cmds.menuItem('donate_MI', label='Donate', command=partial(self.donateWin))
        cmds.menuItem('idiom_MI', label='Idioms', command=partial(self.logger.infoWin, 'm009_idioms', 'i012_idiomsDesc', None, 'center', 305, 250))
        cmds.menuItem('terms_MI', label='Terms and Conditions', command=self.checkTermsAndCond)
        cmds.menuItem('update_MI', label='Update', command=partial(self.checkForUpdate, True))
        cmds.menuItem('help_MI', label='Wiki...', command=partial(self.utils.visitWebSite, self.wikiURL))
        if self.dev:
            self.allUIs["devMenu"] = cmds.menu('devMenu', label='Dev')
            cmds.menuItem('verbose_MI', label='Verbose', checkBox=self.verbose, command=self.changeVerbose)
        # -- Layout
        
        # create the main layout:
        self.allUIs["mainLayout"] = cmds.formLayout('mainLayout')        
        # creating tabs - mainTabLayout:
        self.allUIs["mainTabLayout"] = cmds.tabLayout('mainTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=self.allUIs["mainLayout"])
        cmds.formLayout( self.allUIs["mainLayout"], edit=True, attachForm=((self.allUIs["mainTabLayout"], 'top', 0), (self.allUIs["mainTabLayout"], 'left', 0), (self.allUIs["mainTabLayout"], 'bottom', 0), (self.allUIs["mainTabLayout"], 'right', 0)) )
        
        # -- Rigging tag
        
        self.allUIs["riggingTabLayout"] = cmds.formLayout('riggingTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        #colTopLefA - columnLayout:
        self.allUIs["colTopLeftA"] = cmds.columnLayout('colTopLeftA', adjustableColumn=True, height=20, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["i000_guides"] = cmds.text(self.lang['i000_guides'], font="boldLabelFont", width=150, align='center', parent=self.allUIs["colTopLeftA"])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        #colTopRightA - columnLayout:
        self.allUIs["colTopRightA"] = cmds.rowColumnLayout('colTopRightA', numberOfColumns=2, adjustableColumn=1, columnWidth=(120, 50), parent=self.allUIs["riggingTabLayout"])
        self.allUIs["i001_modules"] = cmds.text(self.lang['i001_modules'], font="boldLabelFont", width=150, align='center', parent=self.allUIs["colTopRightA"])
        self.allUIs["triCollapseGuidesITB"] = cmds.iconTextButton("triCollapseGuidesITB", image=self.triDownIcon, annotation=self.lang['i348_triangleIconAnn'], command=partial(self.collapseAllFL, "triCollapseGuidesITB", 0), width=17, height=17, style='iconOnly', align='right', parent=self.allUIs["colTopRightA"])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        #colMiddleLeftA - scrollLayout - guidesLayout:
        self.allUIs["colMiddleLeftA"] = cmds.scrollLayout("colMiddleLeftA", width=160, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["guidesLayoutA"] = cmds.columnLayout("guidesLayoutA", adjustableColumn=True, width=140, rowSpacing=3, parent=self.allUIs["colMiddleLeftA"])
        # here will be populated by guides of modules and scripts...
        self.allUIs["i030_standard"] = cmds.text(self.lang['i030_standard'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.guideModuleList = self.startGuideModules(self.standardFolder, "start", "guidesLayoutA")
        cmds.separator(style='doubleDash', height=10, parent=self.allUIs["guidesLayoutA"])
        self.allUIs["i031_integrated"] = cmds.text(self.lang['i031_integrated'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.startGuideModules(self.integratedFolder, "start", "guidesLayoutA")
        cmds.setParent(self.allUIs["riggingTabLayout"])
        #colMiddleRightA - scrollLayout - modulesLayout:
        self.allUIs["colMiddleRightA"] = cmds.scrollLayout("colMiddleRightA", width=120, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=120, parent=self.allUIs["colMiddleRightA"])
        # here will be populated by created instances of modules...
        # after footerRigging we will call the function to populate here, because it edits the footerRiggingText
        cmds.setParent(self.allUIs["riggingTabLayout"])
        #editSelectedModuleLayoutA - frameLayout:
        self.allUIs["editSelectedModuleLayoutA"] = cmds.frameLayout('editSelectedModuleLayoutA', label=self.lang['i011_editSelected']+" "+self.lang['i143_module'], collapsable=True, collapse=self.collapseEditSelModFL, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["selectedModuleLayout"] = cmds.columnLayout('selectedModuleLayout', adjustableColumn=True, parent=self.allUIs["editSelectedModuleLayoutA"])
        #optionsMainFL - frameLayout:
        self.allUIs["optionsMainFL"] = cmds.frameLayout('optionsMainFL', label=self.lang['i002_options'], collapsable=True, collapse=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigOptionsLayout"] = cmds.columnLayout('rigOptionsLayout', adjustableColumn=True, columnOffset=('left', 5), parent=self.allUIs["optionsMainFL"])
        self.allUIs["prefixLayout"] = cmds.rowColumnLayout('prefixLayout', numberOfColumns=2, columnWidth=[(1, 40), (2, 200)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["prefixTextField"] = cmds.textField('prefixTextField', text="", parent= self.allUIs["prefixLayout"], changeCommand=self.setPrefix)
        self.allUIs["prefixText"] = cmds.text('prefixText', align='left', label=self.lang['i003_prefix'], parent=self.allUIs["prefixLayout"])
        cmds.setParent(self.allUIs["rigOptionsLayout"])
        self.allUIs["displayJointsCB"] = cmds.checkBox('displayJointsCB', label=self.lang['i009_displayJointsCB'], align='left', value=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["hideGuideGrpCB"] = cmds.checkBox('hideGuideGrpCB', label=self.lang['i183_hideGuideGrp'], align='left', value=1, changeCommand=self.displayGuideGrp, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["integrateCB"] = cmds.checkBox('integrateCB', label=self.lang['i010_integrateCB'], align='left', value=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["defaultRenderLayerCB"] = cmds.checkBox('defaultRenderLayerCB', label=self.lang['i004_defaultRL'], align='left', value=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["colorizeCtrlCB"] = cmds.checkBox('colorizeCtrlCB', label=self.lang['i065_colorizeCtrl'], align='left', value=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["addAttrCB"] = cmds.checkBox('addAttrCB', label=self.lang['i066_addAttr'], align='left', value=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["degreeLayout"] = cmds.rowColumnLayout('degreeLayout', numberOfColumns=2, columnWidth=[(1, 100), (2, 250)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["rigOptionsLayout"])
        # option Degree:
        self.degreeOptionMenu = cmds.optionMenu("degreeOptionMenu", label='', changeCommand=self.changeOptionDegree, parent=self.allUIs["degreeLayout"])
        self.degreeOptionMenuItemList = ['0 - Preset', '1 - Linear', '3 - Cubic']
        # verify if there is an optionVar of last choosen by user in Maya system:
        lastDegreeOption = self.ar.checkLastOptionVar("dpAutoRigLastDegreeOption", "0 - Preset", self.degreeOptionMenuItemList)
        for degOpt in self.degreeOptionMenuItemList:
            cmds.menuItem(label=degOpt, parent=self.degreeOptionMenu)
        cmds.optionMenu(self.degreeOptionMenu, edit=True, value=lastDegreeOption)
        cmds.text(self.lang['i128_optionDegree'], parent=self.allUIs["degreeLayout"])
        self.degreeOption = int(lastDegreeOption[0])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        #footerRigging - columnLayout:
        self.allUIs["footerRigging"] = cmds.columnLayout('footerRigging', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigAllButton"] = cmds.button(label=self.lang['i020_rigAll'], annotation=self.lang['i021_rigAllDesc'], backgroundColor=(0.6, 1.0, 0.6), command=self.rigAll, parent=self.allUIs["footerRigging"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerRigging"])
        # this text will be actualized by the number of module instances created in the scene...
        self.allUIs["footerRiggingText"] = cmds.text('footerRiggingText', align='center', label="# "+self.lang['i005_footerRigging'], parent=self.allUIs["footerRigging"])
        cmds.setParent( self.allUIs["mainTabLayout"] )
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["riggingTabLayout"], edit=True,
                        attachForm=[(self.allUIs["colTopLeftA"], 'top', 7), (self.allUIs["colTopLeftA"], 'left', 5), (self.allUIs["colTopRightA"], 'top', 5), (self.allUIs["colTopRightA"], 'right', 5), (self.allUIs["colMiddleLeftA"], 'left', 5), (self.allUIs["colMiddleRightA"], 'right', 5), (self.allUIs["optionsMainFL"], 'left', 5), (self.allUIs["optionsMainFL"], 'right', 5), (self.allUIs["editSelectedModuleLayoutA"], 'left', 5), (self.allUIs["editSelectedModuleLayoutA"], 'right', 5), (self.allUIs["footerRigging"], 'left', 5), (self.allUIs["footerRigging"], 'bottom', 5), (self.allUIs["footerRigging"], 'right', 5)],
                        attachControl=[(self.allUIs["colMiddleLeftA"], 'top', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colTopRightA"], 'left', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colMiddleLeftA"], 'bottom', 5, self.allUIs["editSelectedModuleLayoutA"]), (self.allUIs["colMiddleRightA"], 'top', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colMiddleRightA"], 'bottom', 5, self.allUIs["editSelectedModuleLayoutA"]), (self.allUIs["colMiddleRightA"], 'left', 5, self.allUIs["colMiddleLeftA"]), (self.allUIs["editSelectedModuleLayoutA"], 'bottom', 5, self.allUIs["optionsMainFL"]), (self.allUIs["optionsMainFL"], 'bottom', 5, self.allUIs["footerRigging"])],
                        #attachPosition=[(self.allUIs["colTopLeftA"], 'right', 5, 50), (self.allUIs["colTopRightA"], 'left', 0, 50)],
                        attachNone=[(self.allUIs["footerRigging"], 'top')]
                        )
        
        # -- Skinning tab
        
        self.allUIs["skinningTabLayout"] = cmds.formLayout('skinningTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        self.allUIs["skinMainLayout"] = cmds.scrollLayout('skinMainLayout', parent=self.allUIs["skinningTabLayout"])
        self.allUIs["skinLayout"] = cmds.columnLayout('skinLayout', adjustableColumn=True, rowSpacing=10, parent=self.allUIs['skinMainLayout'])
        self.allUIs["skinCreateFL"] = cmds.frameLayout('skinCreateFL', label=self.lang['i158_create']+" SkinCluster", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["skinLayout"])
        self.allUIs["skinLists2Layout"] = cmds.paneLayout("skinLists2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["skinCreateFL"])
        #colSkinLeftA - columnLayout:
        self.allUIs["colSkinLeftA"] = cmds.columnLayout('colSkinLeftA', adjustableColumn=True, width=170, parent=self.allUIs["skinLists2Layout"])
        # radio buttons:
        self.allUIs["jntCollection"] = cmds.radioCollection('jntCollection', parent=self.allUIs["colSkinLeftA"])
        cmds.radioButton(label=self.lang['i022_listAllJnts'], annotation="allJoints", onCommand=self.populateJoints) #all joints
        dpARJoints = cmds.radioButton(label=self.lang['i023_listdpARJnts'], annotation="dpARJoints", onCommand=self.populateJoints)
        self.allUIs["jointsDisplay"] = cmds.rowColumnLayout('jointsDisplay', numberOfColumns=3, columnWidth=[(1, 45), (2, 45), (3, 45)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 10), (3, 'left', 10)], parent=self.allUIs["colSkinLeftA"])
        self.allUIs["_JntCB"] = cmds.checkBox('_JntCB', label="Jnt", annotation="Skinned Joints", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["_JarCB"] = cmds.checkBox('_JarCB', label="Jar", annotation="Skinned Articulation Joints", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["_JadCB"] = cmds.checkBox('_JadCB', label="Jad", annotation="Skinned Additional Joints", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["_JcrCB"] = cmds.checkBox('_JcrCB', label="Jcr", annotation="Skinned Corrective Joints", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["_JisCB"] = cmds.checkBox('_JisCB', label="Jis", annotation="Indirect Skinning Joints", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["jointNameTF"] = cmds.textField('jointNameTF', width=30, changeCommand=self.populateJoints, parent=self.allUIs["colSkinLeftA"])
        self.allUIs["jntTextScrollLayout"] = cmds.textScrollList( 'jntTextScrollLayout', width=30, height=500, allowMultiSelection=True, selectCommand=self.actualizeSkinFooter, parent=self.allUIs["colSkinLeftA"] )
        cmds.radioCollection(self.allUIs["jntCollection"], edit=True, select=dpARJoints)
        cmds.setParent(self.allUIs["skinCreateFL"])
        #colSkinRightA - columnLayout:
        self.allUIs["colSkinRightA"] = cmds.columnLayout('colSkinRightA', adjustableColumn=True, width=170, parent=self.allUIs["skinLists2Layout"])
        self.allUIs["geomCollection"] = cmds.radioCollection('geomCollection', parent=self.allUIs["colSkinRightA"])
        cmds.radioButton(label=self.lang['i026_listAllJnts'], annotation="allGeoms", onCommand=self.populateGeoms) #all geometries
        selGeoms = cmds.radioButton(label=self.lang['i027_listSelJnts'], annotation="selGeoms", onCommand=self.populateGeoms)
        self.allUIs["geoLongName"] = cmds.checkBox('geoLongName', label=self.lang['i073_displayLongName'], align='left', value=1, changeCommand=self.populateGeoms, parent=self.allUIs["colSkinRightA"])
        self.allUIs["displaySkinLogWin"] = cmds.checkBox('displaySkinLogWin', label=self.lang['i286_displaySkinLog'], align='left', value=1, parent=self.allUIs["colSkinRightA"])
        cmds.separator(style="none", height=2, parent=self.allUIs["colSkinRightA"])
        self.allUIs["geoNameTF"] = cmds.textField('geoNameTF', width=30, changeCommand=self.populateGeoms, parent=self.allUIs["colSkinRightA"])
        self.allUIs["modelsTextScrollLayout"] = cmds.textScrollList( 'modelsTextScrollLayout', width=30, height=500, allowMultiSelection=True, selectCommand=self.actualizeSkinFooter, parent=self.allUIs["colSkinRightA"] )
        cmds.radioCollection(self.allUIs["geomCollection"], edit=True, select=selGeoms)
        cmds.setParent(self.allUIs["skinCreateFL"])
        #footerB - columnLayout:
        self.allUIs["footerB"] = cmds.columnLayout('footerB', adjustableColumn=True, parent=self.allUIs["skinCreateFL"])
        cmds.separator(style='none', height=3, parent=self.allUIs["footerB"])
        self.allUIs["skinButton"] = cmds.button("skinButton", label=self.lang['i028_skinButton'], backgroundColor=(0.5, 0.8, 0.8), command=partial(self.skin.skinFromUI), parent=self.allUIs["footerB"])
        self.allUIs["footerRiggingddRem"] = cmds.paneLayout("footerRiggingddRem", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["footerB"])
        self.allUIs["addSkinButton"] = cmds.button("addSkinButton", label=self.lang['i063_skinAddBtn'], backgroundColor=(0.7, 0.9, 0.9), command=partial(self.skin.skinFromUI, "Add"), parent=self.allUIs["footerRiggingddRem"])
        self.allUIs["removeSkinButton"] = cmds.button("removeSkinButton", label=self.lang['i064_skinRemBtn'], backgroundColor=(0.1, 0.3, 0.3), command=partial(self.skin.skinFromUI, "Remove"), parent=self.allUIs["footerRiggingddRem"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerB"])
        # this text will be actualized by the number of joints and geometries in the textScrollLists for skinning:
        self.allUIs["footerBText"] = cmds.text('footerBText', align='center', label="0 "+self.lang['i025_joints']+" 0 "+self.lang['i024_geometries'], parent=self.allUIs["footerB"])
        #skinCopy - layout
        self.allUIs["skinCopyFL"] = cmds.frameLayout('skinCopyFL', label=self.lang['i287_copy']+" Skinning", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["skinLayout"])
        self.allUIs['skinCopyRowLayout'] = cmds.rowLayout('skinCopyRowLayout', numberOfColumns=3, columnWidth3=(90, 90, 150), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent=self.allUIs["skinCopyFL"])
        self.allUIs["skinSurfAssociationCollection"] = cmds.radioCollection('skinSurfAssociationCollection', parent=self.allUIs["skinCopyRowLayout"])
        closestPoint = cmds.radioButton(label="closestPoint", annotation="closestPoint")
        cmds.radioButton(label="uvSpace", annotation="uvSpace") #uvSpace
        self.allUIs["skinCopy2Layout"] = cmds.paneLayout("skinCopy2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["skinCopyRowLayout"])
        self.allUIs["skinCopyOneSourceBT"] = cmds.button("skinCopyOneSourceBT", label=self.lang['i290_oneSource'], backgroundColor=(0.4, 0.8, 0.9), command=partial(self.skin.copySkinFromOneSource, None, True), annotation=self.lang['i288_copySkinDesc'], parent=self.allUIs["skinCopy2Layout"])
        self.allUIs["skinCopyMultiSourceBT"] = cmds.button("skinCopyMultiSourceBT", label=self.lang['i146_same']+" "+self.lang['m222_name'], backgroundColor=(0.5, 0.8, 0.9), command=partial(self.skin.copySkinSameName, None, True), annotation=self.lang['i289_sameNameSkinDesc'], parent=self.allUIs["skinCopy2Layout"])
        cmds.radioCollection(self.allUIs["skinSurfAssociationCollection"], edit=True, select=closestPoint)
        cmds.setParent( self.allUIs["mainTabLayout"] )
        #skinWeightsIO - layout
        self.allUIs["skinWeightsIOFL"] = cmds.frameLayout('skinWeightsIOFL', label="SkinCluster weights IO", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["skinLayout"])
        self.allUIs["skinWeightsIOLayout"] = cmds.paneLayout("skinWeightsIOLayout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["skinWeightsIOFL"])
        self.allUIs["skinWeightsExportBT"] = cmds.button("skinWeightsExportBT", label=self.lang['i164_export'], backgroundColor=(0.4, 0.8, 0.9), command=partial(self.skin.ioSkinWeightsByUI, True), annotation=self.lang['i266_selected'], parent=self.allUIs["skinWeightsIOLayout"])
        self.allUIs["skinWeightsImportBT"] = cmds.button("skinWeightsImportBT", label=self.lang['i196_import'], backgroundColor=(0.5, 0.8, 0.9), command=partial(self.skin.ioSkinWeightsByUI, False), annotation=self.lang['i266_selected'], parent=self.allUIs["skinWeightsIOLayout"])
        cmds.setParent( self.allUIs["mainTabLayout"] )
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["skinningTabLayout"], edit=True,
                        attachForm=[(self.allUIs["skinMainLayout"], 'top', 20), (self.allUIs["skinMainLayout"], 'left', 5), (self.allUIs["skinMainLayout"], 'right', 5), (self.allUIs["skinMainLayout"], 'bottom', 5)]
                        )
        
        # -- Controllers tab

        self.allUIs["controllerTabLayout"] = cmds.formLayout('controllerTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        self.allUIs["controllerMainLayout"] = cmds.scrollLayout('controllerMainLayout', parent=self.allUIs["controllerTabLayout"])
        self.allUIs["controllerLayout"] = cmds.columnLayout('controllerLayout', adjustableColumn=True, rowSpacing=10, parent=self.allUIs['controllerMainLayout'])
        # colorControl - frameLayout:
        self.allUIs["colorControlFL"] = cmds.frameLayout('colorControlFL', label=self.lang['m047_colorOver'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controllerLayout"])
        self.allUIs["colorTabLayout"] = cmds.tabLayout('colorTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=self.allUIs["colorControlFL"])
        # Index layout:
        self.allUIs["colorIndexLayout"] = cmds.gridLayout('colorIndexLayout', numberOfColumns=16, cellWidthHeight=(20, 20), parent=self.allUIs["colorTabLayout"])
        # creating buttons
        for colorIndex, colorValues in enumerate(self.ctrls.getColorList()):
            cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.ctrls.colorShape, color=colorIndex), parent=self.allUIs["colorIndexLayout"])
        # RGB layout:
        self.allUIs["colorRGBLayout"] = cmds.columnLayout('colorRGBLayout', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent=self.allUIs["colorTabLayout"])
        cmds.separator(height=10, style='none', parent=self.allUIs["colorRGBLayout"])
        self.allUIs["colorRGBSlider"] = cmds.colorSliderGrp('colorRGBSlider', label='Color', columnAlign3=('right', 'left', 'left'), columnWidth3=(30, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=partial(self.ctrls.setColorRGBByUI, slider='colorRGBSlider'), parent=self.allUIs["colorRGBLayout"])
        cmds.button("removeOverrideColorBT", label=self.lang['i046_remove'], command=self.ctrls.removeColor, parent=self.allUIs["colorRGBLayout"])
        # Outliner layout:
        self.allUIs["colorOutlinerLayout"] = cmds.columnLayout('colorOutlinerLayout', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent=self.allUIs["colorTabLayout"])
        cmds.separator(height=10, style='none', parent=self.allUIs["colorOutlinerLayout"])
        self.allUIs["colorOutlinerSlider"] = cmds.colorSliderGrp('colorOutlinerSlider', label='Outliner', columnAlign3=('right', 'left', 'left'), columnWidth3=(45, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=partial(self.ctrls.setColorOutlinerByUI, slider='colorOutlinerSlider'), parent=self.allUIs["colorOutlinerLayout"])
        cmds.button("removeOutlinerColorBT", label=self.lang['i046_remove'], command=self.ctrls.removeColor, parent=self.allUIs["colorOutlinerLayout"])
        # renaming tabLayouts:
        cmds.tabLayout(self.allUIs["colorTabLayout"], edit=True, tabLabel=((self.allUIs["colorIndexLayout"], "Index"), (self.allUIs["colorRGBLayout"], "RGB"), (self.allUIs["colorOutlinerLayout"], "Outliner")))
        # setupController - frameLayout:
        self.allUIs["defaultValuesControlFL"] = cmds.frameLayout('defaultValuesControlFL', label=self.lang['i270_defaultValues'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controllerLayout"])
        self.allUIs["defaultValuesControl3Layout"] = cmds.paneLayout("defaultValuesControl3Layout", configuration="vertical3", separatorThickness=2.0, parent=self.allUIs["defaultValuesControlFL"])
        self.allUIs["resetToDefaultValuesButton"] = cmds.button("resetToDefaultValuesButton", label=self.lang['i271_reset'], backgroundColor=(1.0, 0.9, 0.6), height=30, command=partial(self.ctrls.setupDefaultValues, True), parent=self.allUIs["defaultValuesControl3Layout"])
        self.allUIs["setDefaultValuesButton"] = cmds.button("setDefaultValuesButton", label=self.lang['i272_set'], backgroundColor=(1.0, 0.8, 0.5), height=30, command=partial(self.ctrls.setupDefaultValues, False), parent=self.allUIs["defaultValuesControl3Layout"])
        self.allUIs["setupDefaultValuesButton"] = cmds.button("setupDefaultValuesButton", label=self.lang['i274_editor'], backgroundColor=(1.0, 0.6, 0.4), height=30, command=self.ctrls.defaultValueEditor, parent=self.allUIs["defaultValuesControl3Layout"])
        # createController - frameLayout:
        self.allUIs["createControllerLayout"] = cmds.frameLayout('createControllerLayout', label=self.lang['i114_createControl'], collapsable=True, collapse=False, marginWidth=10, marginHeight=10, parent=self.allUIs["controllerLayout"])
        self.allUIs["optionsControllerFL"] = cmds.frameLayout('optionsControllerFL', label=self.lang['i002_options'], collapsable=True, collapse=True, marginWidth=10, parent=self.allUIs["createControllerLayout"])
        self.allUIs["controllerOptionsLayout"] = cmds.columnLayout('controllerOptionsLayout', adjustableColumn=True, width=50, rowSpacing=5, parent=self.allUIs["optionsControllerFL"])
        self.allUIs["controlNameTFG"] = cmds.textFieldGrp('controlNameTFG', text="", label=self.lang['i101_customName'], columnAlign2=("right", "left"), adjustableColumn2=2, columnAttach=((1, "right", 5), (2, "left", 5)), parent=self.allUIs["controllerOptionsLayout"])
        self.allUIs["controlActionRBG"] = cmds.radioButtonGrp("controlActionRBG", label=self.lang['i109_action'], labelArray3=[self.lang['i108_newController'], self.lang['i107_addShape'], self.lang['i102_replaceShape']], vertical=True, numberOfRadioButtons=3, parent=self.allUIs["controllerOptionsLayout"])
        cmds.radioButtonGrp(self.allUIs["controlActionRBG"], edit=True, select=1) #new controller
        self.allUIs["degreeRBG"] = cmds.radioButtonGrp("degreeRBG", label=self.lang['i103_degree'], labelArray2=[self.lang['i104_linear'], self.lang['i105_cubic']], vertical=True, numberOfRadioButtons=2, parent=self.allUIs["controllerOptionsLayout"])
        cmds.radioButtonGrp(self.allUIs["degreeRBG"], edit=True, select=1) #linear
        self.allUIs["controlSizeFSG"] = cmds.floatSliderGrp("controlSizeFSG", label=self.lang['i115_size'], field=True, minValue=0.01, maxValue=10.0, fieldMinValue=0, fieldMaxValue=100.0, precision=2, value=1.0, parent=self.allUIs["controllerOptionsLayout"])
        self.allUIs["directionOMG"] = cmds.optionMenuGrp("directionOMG", label=self.lang['i106_direction'], parent=self.allUIs["controllerOptionsLayout"])
        cmds.menuItem(label='-X')
        cmds.menuItem(label='+X')
        cmds.menuItem(label='-Y')
        cmds.menuItem(label='+Y')
        cmds.menuItem(label='-Z')
        cmds.menuItem(label='+Z')
        cmds.optionMenuGrp(self.allUIs["directionOMG"], edit=True, value='+Y')
        # curveShapes - frameLayout:
        self.allUIs["controlShapesLayout"] = cmds.frameLayout('controlShapesLayout', label=self.lang['i100_curveShapes'], collapsable=True, collapse=True, parent=self.allUIs["createControllerLayout"])
        self.allUIs["controlModuleLayout"] = cmds.gridLayout('controlModuleLayout', numberOfColumns=7, cellWidthHeight=(48, 50), backgroundColor=(0.3, 0.3, 0.3), parent=self.allUIs['controlShapesLayout'])
        # here we populate the control module layout with the items from Controllers folder:
        self.startGuideModules(self.curvesSimpleFolder, "start", "controlModuleLayout")
        self.allUIs["combinedControlShapesLayout"] = cmds.frameLayout('combinedControlShapesLayout', label=self.lang['i118_combinedShapes'], collapsable=True, collapse=True, parent=self.allUIs["createControllerLayout"])
        self.allUIs["combinedControlModuleLayout"] = cmds.gridLayout('combinedControlModuleLayout', numberOfColumns=7, cellWidthHeight=(48, 50), backgroundColor=(0.3, 0.3, 0.3), parent=self.allUIs['combinedControlShapesLayout'])
        # here we populate the control module layout with the items from Controllers folder:
        self.startGuideModules(self.curvesCombinedFolder, "start", "combinedControlModuleLayout")
        # editSeletedController - frameLayout:
        self.allUIs["editSelectedControllerFL"] = cmds.frameLayout('editSelectedControllerFL', label=self.lang['i011_editSelected']+" "+self.lang['i111_controller'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent=self.allUIs["controllerLayout"])
        self.allUIs["editSelectedController3Layout"] = cmds.paneLayout("editSelectedController3Layout", configuration="vertical3", separatorThickness=2.0, parent=self.allUIs["editSelectedControllerFL"])
        self.allUIs["addShapeButton"] = cmds.button("addShapeButton", label=self.lang['i113_addShapes'], backgroundColor=(1.0, 0.6, 0.7), command=partial(self.ctrls.transferShape, False, False), parent=self.allUIs["editSelectedController3Layout"])
        self.allUIs["copyShapeButton"] = cmds.button("copyShapeButton", label=self.lang['i112_copyShapes'], backgroundColor=(1.0, 0.6, 0.5), command=partial(self.ctrls.transferShape, False, True), parent=self.allUIs["editSelectedController3Layout"])
        self.allUIs["replaceShapeButton"] = cmds.button("replaceShapeButton", label=self.lang['i110_transferShapes'], backgroundColor=(1.0, 0.6, 0.3), command=partial(self.ctrls.transferShape, True, True), parent=self.allUIs["editSelectedController3Layout"])
        self.allUIs["editSelection2Layout"] = cmds.paneLayout("editSelection2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["editSelectedControllerFL"])
        self.allUIs["resetCurveButton"] = cmds.button("resetCurveButton", label=self.lang['i121_resetCurve'], backgroundColor=(1.0, 0.7, 0.3), height=30, command=partial(self.ctrls.resetCurve), parent=self.allUIs["editSelection2Layout"])
        self.allUIs["changeDegreeButton"] = cmds.button("changeDegreeButton", label=self.lang['i120_changeDegree'], backgroundColor=(1.0, 0.8, 0.4), height=30, command=partial(self.ctrls.resetCurve, True), parent=self.allUIs["editSelection2Layout"])
        self.allUIs["zeroOutGrpButton"] = cmds.button("zeroOutGrpButton", label=self.lang['i116_zeroOut'], backgroundColor=(0.8, 0.8, 0.8), height=30, command=self.utils.zeroOut, parent=self.allUIs["editSelectedControllerFL"])
        self.allUIs["selectAllControls"] = cmds.button("selectAllControls", label=self.lang['i291_selectAllControls'], backgroundColor=(0.9, 1.0, 0.6), height=30, command=partial(self.ctrls.selectAllControls), parent=self.allUIs["editSelectedControllerFL"])
        # calibrationControls - frameLayout:
        self.allUIs["calibrationFL"] = cmds.frameLayout('calibrationFL', label=self.lang['i193_calibration'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent=self.allUIs["controllerLayout"])
        self.allUIs["calibration2Layout"] = cmds.paneLayout("calibration2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["calibrationFL"])
        self.allUIs["transferCalibrationButton"] = cmds.button("transferCalibrationButton", label=self.lang['i194_transfer'], backgroundColor=(0.5, 1.0, 1.0), height=30, command=self.ctrls.transferCalibration, parent=self.allUIs["calibration2Layout"])
        self.allUIs["importCalibrationButton"] = cmds.button("importCalibrationButton", label=self.lang['i196_import'], backgroundColor=(0.5, 0.8, 1.0), height=30, command=self.ctrls.importCalibration, parent=self.allUIs["calibration2Layout"])
        # mirror calibration - layout:
        self.allUIs["mirrorCalibrationFL"] = cmds.frameLayout('mirrorCalibrationFL', label=self.lang['m010_mirror']+" "+self.lang['i193_calibration'], collapsable=True, collapse=True, marginHeight=10, marginWidth=10, parent=self.allUIs["calibrationFL"])
        self.allUIs["mirrorCalibrationLayout"] = cmds.rowColumnLayout('mirrorCalibrationLayout', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="mirrorCalibrationFL" )
        self.allUIs["prefixT"] = cmds.text("prefixT", label=self.lang['i144_prefix'], parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["fromPrefixT"] = cmds.text("fromPrefixT", label=self.lang['i036_from'], parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["fromPrefixTF"] = cmds.textField('fromPrefixTF', text=self.lang['p002_left']+"_", parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["toPrefixT"] = cmds.text("toPrefixT", label=self.lang['i037_to'], parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["toPrefixTF"] = cmds.textField('toPrefixTF', text=self.lang['p003_right']+"_", parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["mirrorCalibrationButton"] = cmds.button("mirrorCalibrationButton", label=self.lang['m010_mirror'], backgroundColor=(0.5, 0.7, 1.0), height=30, width=70, command=self.ctrls.mirrorCalibration, parent=self.allUIs["mirrorCalibrationLayout"])
        # ControlShapeIO - frameLayout:
        self.allUIs["shapeIOFL"] = cmds.frameLayout('shapeIOFL', label=self.lang['m067_shape']+" "+self.lang['i199_io'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controllerLayout"])
        self.allUIs["shapeIO4Layout"] = cmds.paneLayout("shapeIO4Layout", configuration="vertical4", separatorThickness=2.0, parent=self.allUIs["shapeIOFL"])
        self.allUIs["exportShapeButton"] = cmds.button("exportShapeButton", label=self.lang['i164_export'], backgroundColor=(1.0, 0.8, 0.8), height=30, command=self.ctrls.exportShape, parent=self.allUIs["shapeIO4Layout"])
        self.allUIs["importShapeButton"] = cmds.button("importShapeButton", label=self.lang['i196_import'], backgroundColor=(1.0, 0.9, 0.9), height=30, command=self.ctrls.importShape, parent=self.allUIs["shapeIO4Layout"])
        # mirror control shape - layout:
        self.allUIs["mirrorShapeFL"] = cmds.frameLayout('mirrorShapeFL', label=self.lang['m010_mirror']+" "+self.lang['m067_shape'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["shapeIOFL"])
        self.allUIs["mirrorShapeLayout"] = cmds.rowColumnLayout('mirrorShapeLayout', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="mirrorShapeFL" )
        self.allUIs["axisShapeMenu"] = cmds.optionMenu("axisShapeMenu", label='', parent=self.allUIs["mirrorShapeLayout"])
        mirrorShapeMenuItemList = ['X', 'Y', 'Z']
        for axis in mirrorShapeMenuItemList:
            cmds.menuItem(label=axis, parent=self.allUIs["axisShapeMenu"])
        self.allUIs["fromPrefixShapeT"] = cmds.text("fromPrefixShapeT", label=self.lang['i036_from'], parent=self.allUIs["mirrorShapeLayout"])
        self.allUIs["fromPrefixShapeTF"] = cmds.textField('fromPrefixShapeTF', text=self.lang['p002_left']+"_", parent=self.allUIs["mirrorShapeLayout"])
        self.allUIs["toPrefixShapeT"] = cmds.text("toPrefixShapeT", label=self.lang['i037_to'], parent=self.allUIs["mirrorShapeLayout"])
        self.allUIs["toPrefixShapeTF"] = cmds.textField('toPrefixShapeTF', text=self.lang['p003_right']+"_", parent=self.allUIs["mirrorShapeLayout"])
        self.allUIs["mirrorShapeButton"] = cmds.button("mirrorShapeButton", label=self.lang['m010_mirror'], backgroundColor=(1.0, 0.5, 0.5), height=30, width=70, command=self.ctrls.resetMirrorShape, parent=self.allUIs["mirrorShapeLayout"])
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["controllerTabLayout"], edit=True,
                        attachForm=[(self.allUIs["controllerMainLayout"], 'top', 20), (self.allUIs["controllerMainLayout"], 'left', 5), (self.allUIs["controllerMainLayout"], 'right', 5), (self.allUIs["controllerMainLayout"], 'bottom', 5)]
                        )
        
        # --Tools tab
        
        self.allUIs["toolsTabLayout"] = cmds.formLayout('toolsTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        self.allUIs["toolsMainLayout"] = cmds.scrollLayout("toolsMainLayout", parent=self.allUIs["toolsTabLayout"])
        self.allUIs["toolsLayout"] = cmds.columnLayout("toolsLayout", adjustableColumn=True, rowSpacing=3, parent=self.allUIs["toolsMainLayout"])
        self.startGuideModules(self.toolsFolder, "start", "toolsLayout")
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["toolsTabLayout"], edit=True,
                        attachForm=[(self.allUIs["toolsMainLayout"], 'top', 20), (self.allUIs["toolsMainLayout"], 'left', 5), (self.allUIs["toolsMainLayout"], 'right', 5), (self.allUIs["toolsMainLayout"], 'bottom', 5)]
                        )
        
        # -- Validator tab
        
        self.allUIs["validatorTabLayout"] = cmds.formLayout('validatorTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        self.allUIs["validatorMainLayout"] = cmds.scrollLayout("validatorMainLayout", parent=self.allUIs["validatorTabLayout"])
        self.allUIs["validatorLayout"] = cmds.columnLayout("validatorLayout", adjustableColumn=True, rowSpacing=3, parent=self.allUIs["validatorMainLayout"])
        self.allUIs["validatorCheckInLayout"] = cmds.frameLayout('validatorCheckInLayout', label=self.lang['i208_checkin'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
        # check-in
        self.startGuideModules(self.checkInFolder, "start", "validatorCheckInLayout")
        cmds.separator(style="none", parent=self.allUIs["validatorCheckInLayout"])
        self.allUIs["selectAllCheckinCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i208_checkin'], value=False, changeCommand=partial(self.changeActiveAllModules, self.checkInInstanceList), parent=self.allUIs["validatorCheckInLayout"])
        self.allUIs["selectedCheckInPL"] = cmds.paneLayout("selectedCheckInPL", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorCheckInLayout"])
        self.allUIs["verifyAllSelectCheckinBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkInInstanceList, True, True), parent=self.allUIs["selectedCheckInPL"])
        self.allUIs["fixAllSelectCheckinBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkInInstanceList, False, True), parent=self.allUIs["selectedCheckInPL"])
        cmds.separator(height=30, parent=self.allUIs["validatorLayout"])
        # check-out
        self.allUIs["validatorCheckOutLayout"] = cmds.frameLayout('validatorCheckOutLayout', label=self.lang['i209_checkout'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
        self.startGuideModules(self.checkOutFolder, "start", "validatorCheckOutLayout")
        cmds.separator(style="none", parent=self.allUIs["validatorCheckOutLayout"])
        self.allUIs["selectAllCheckoutCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i209_checkout'], value=True, changeCommand=partial(self.changeActiveAllModules, self.checkOutInstanceList), parent=self.allUIs["validatorCheckOutLayout"])
        self.allUIs["selectedCheckOutPL"] = cmds.paneLayout("selectedCheckOutPL", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorCheckOutLayout"])
        self.allUIs["verifyAllSelectCheckoutBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkOutInstanceList, True, True), parent=self.allUIs["selectedCheckOutPL"])
        self.allUIs["fixAllSelectCheckoutBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkOutInstanceList, False, True), parent=self.allUIs["selectedCheckOutPL"])
        # pipeline check-addons
        if self.ar.pipeliner.pipeData['addOnsPath']:
            if self.getValidatorsAddOns():
                cmds.separator(height=30, parent=self.allUIs["validatorLayout"])
                self.allUIs["validatorAddOnsLayout"] = cmds.frameLayout('validatorAddOnsLayout', label=self.lang['i212_addOns'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
                self.startGuideModules("", "start", "validatorAddOnsLayout", path=self.ar.pipeliner.pipeData['addOnsPath'])
                cmds.separator(style="none", parent=self.allUIs["validatorAddOnsLayout"])
                self.allUIs["selectAllAddonCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i212_addOns'], value=True, changeCommand=partial(self.changeActiveAllModules, self.checkAddOnsInstanceList), parent=self.allUIs["validatorAddOnsLayout"])
                self.allUIs["selectedCheckAddOnsPL"] = cmds.paneLayout("selectedCheckAddOnsPL", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorAddOnsLayout"])
                self.allUIs["verifyAllSelectAddonBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkAddOnsInstanceList, True, True), parent=self.allUIs["selectedCheckAddOnsPL"])
                self.allUIs["fixAllSelectAddonBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkAddOnsInstanceList, False, True), parent=self.allUIs["selectedCheckAddOnsPL"])
        # pipeline check-finishing
        if self.ar.pipeliner.pipeData['finishingPath']:
            if self.getValidatorsAddOns("finishingPath"):
                cmds.separator(height=30, parent=self.allUIs["validatorLayout"])
                self.allUIs["validatorFinishingLayout"] = cmds.frameLayout('validatorFinishingLayout', label=self.lang['i354_finishing'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
                self.startGuideModules("", "start", "validatorFinishingLayout", path=self.ar.pipeliner.pipeData['finishingPath'])
                cmds.separator(style="none", parent=self.allUIs["validatorFinishingLayout"])
                self.allUIs["selectAllFinishingCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i354_finishing'], value=True, changeCommand=partial(self.changeActiveAllModules, self.checkFinishingInstanceList), parent=self.allUIs["validatorFinishingLayout"])
                self.allUIs["selectedCheckFinishingPL"] = cmds.paneLayout("selectedCheckFinishingPL", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorFinishingLayout"])
                self.allUIs["verifyAllSelectFinishingBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkFinishingInstanceList, True, True), parent=self.allUIs["selectedCheckFinishingPL"])
                self.allUIs["fixAllSelectFinishingBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkFinishingInstanceList, False, True), parent=self.allUIs["selectedCheckFinishingPL"])
        # publisher
        self.allUIs["footerPublish"] = cmds.columnLayout('footerPublish', adjustableColumn=True, parent=self.allUIs["validatorTabLayout"])
        cmds.separator(style='none', height=3, parent=self.allUIs["footerPublish"])
        self.allUIs["publisherButton"] = cmds.button("publisherButton", label=self.lang['m046_publisher'], backgroundColor=(0.75, 0.75, 0.75), height=40, command=self.publisher.mainUI, parent=self.allUIs["footerPublish"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerPublish"])
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["validatorTabLayout"], edit=True,
                        attachForm=[(self.allUIs["validatorMainLayout"], 'top', 20), (self.allUIs["validatorMainLayout"], 'left', 5), (self.allUIs["validatorMainLayout"], 'right', 5), (self.allUIs["validatorMainLayout"], 'bottom', 60), (self.allUIs["footerPublish"], 'left', 5), (self.allUIs["footerPublish"], 'right', 5), (self.allUIs["footerPublish"], 'bottom', 5)],
                        attachNone=[(self.allUIs["footerPublish"], 'top')]
                        )
        self.ar.setValidatorPreset()

        # -- Rebuilder tab

        self.allUIs["rebuilderTabLayout"] = cmds.formLayout('rebuilderTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        # project pipeline asset
        self.allUIs["assetMainLayout"] = cmds.columnLayout('assetMainLayout', adjustableColumn=False, parent=self.allUIs["rebuilderTabLayout"])
        self.allUIs["assetLayout"] = cmds.frameLayout('assetLayout', label=self.lang['i303_asset'], collapsable=True, collapse=False, width=370, parent=self.allUIs["assetMainLayout"])
        self.allUIs["mayaProjectText"] = cmds.textFieldGrp("mayaProjectText", label="Maya "+self.lang['i301_project']+":", text=self.ar.pipeliner.pipeData['mayaProject'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent=self.allUIs["assetLayout"])
        self.allUIs["pipelineText"] = cmds.textFieldGrp("pipelineText", label="Pipeline:", text=self.ar.pipeliner.pipeData['projectPath'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent=self.allUIs["assetLayout"])
        self.allUIs["assetText"] = cmds.textFieldGrp("assetText", label=self.lang['i303_asset']+":", text=self.ar.pipeliner.pipeData['assetName'], editable=False, adjustableColumn=2, columnWidth=[(1, 80), (2, 120)], parent=self.allUIs["assetLayout"])
        # asset buttons
        self.allUIs["assetButtonsLayout"] = cmds.rowColumnLayout("assetButtonsLayout", numberOfColumns=5, columnAlign=[(1, "left"), (2, "left"), (3, "left"), (4, "left"), (5, "left")], columnAttach=[(1, "left", 10), (2, "left", 10), (3, "left", 10), (4, "left", 10), (5, "left", 10)], parent=self.allUIs["assetLayout"])
        self.allUIs['saveVersionAssetBT'] = cmds.button("saveVersionAssetBT", label=self.lang['i222_save']+" "+self.lang['m205_version'], command=self.ar.pipeliner.saveVersion, parent=self.allUIs["assetButtonsLayout"])
        self.allUIs['loadAssetBT'] = cmds.button("loadAssetBT", label=self.lang['i187_load'], command=self.ar.pipeliner.loadAsset, parent=self.allUIs["assetButtonsLayout"])
        self.allUIs['newAssetBT'] = cmds.button("newAssetBT", label=self.lang['i304_new'], command=self.ar.pipeliner.createNewAssetUI, parent=self.allUIs["assetButtonsLayout"])
        self.allUIs['openAssetFolderBT'] = cmds.button("openAssetFolderBT", label=self.lang['c108_open']+" "+self.lang['i298_folder'], command=partial(self.packager.openFolder, self.ar.pipeliner.pipeData['projectPath']), parent=self.allUIs["assetButtonsLayout"])
        self.allUIs['replaceDPDataBT'] = cmds.button("replaceDPDataBT", label=self.lang['m219_replace']+" "+self.dpData, command=partial(self.ar.pipeliner.loadAsset, mode=1), parent=self.allUIs["assetButtonsLayout"])
        cmds.separator(style='in', height=20, width=370, parent=self.allUIs["assetMainLayout"])
        # processes
        self.allUIs["processesLayout"] = cmds.rowColumnLayout('processesLayout', adjustableColumn=1, numberOfColumns=2, columnAlign=[(1, "left"), (2, "right")], columnWidth=[(1, 360), (2, 17)], columnAttach=[(1, "both", 10), (2, "right", 10)], parent=self.allUIs["rebuilderTabLayout"])
        cmds.text('processesIOT', label=self.lang['i292_processes'].upper()+" IO", font="boldLabelFont", parent=self.allUIs["processesLayout"])
        self.allUIs["triCollapseRebuilderITB"] = cmds.iconTextButton("triCollapseRebuilderITB", image=self.triDownIcon, annotation=self.lang['i348_triangleIconAnn'], command=partial(self.collapseAllFL, "triCollapseRebuilderITB", 1), width=17, height=17, style='iconOnly', align='right', parent=self.allUIs["processesLayout"])
        self.allUIs["rebuilderMainLayout"] = cmds.scrollLayout("rebuilderMainLayout", parent=self.allUIs["rebuilderTabLayout"])
        self.allUIs["rebuilderLayout"] = cmds.columnLayout("rebuilderLayout", adjustableColumn=True, rowSpacing=3, parent=self.allUIs["rebuilderMainLayout"])
        self.startGuideModules(self.rebuilderFolder, "start", "rebuilderLayout")
        cmds.separator(style='none', parent=self.allUIs["rebuilderLayout"])
        self.allUIs["rebuilderStartLayout"] = cmds.frameLayout('rebuilderStartLayout', label=self.lang['c110_start'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent=self.allUIs["rebuilderLayout"])
        self.startGuideModules(self.startFolder, "start", "rebuilderStartLayout")
        self.allUIs["rebuilderSourceLayout"] = cmds.frameLayout('rebuilderSourceLayout', label=self.lang['i331_source'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent=self.allUIs["rebuilderLayout"])
        self.startGuideModules(self.sourceFolder, "start", "rebuilderSourceLayout")
        self.allUIs["rebuilderSetupLayout"] = cmds.frameLayout('rebuilderSetupLayout', label=self.lang['i332_setup'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent=self.allUIs["rebuilderLayout"])
        self.startGuideModules(self.setupFolder, "start", "rebuilderSetupLayout")
        self.allUIs["rebuilderDeformingLayout"] = cmds.frameLayout('rebuilderDeformingLayout', label=self.lang['i333_deforming'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent=self.allUIs["rebuilderLayout"])
        self.startGuideModules(self.deformingFolder, "start", "rebuilderDeformingLayout")
        self.allUIs["rebuilderCustomLayout"] = cmds.frameLayout('rebuilderCustomLayout', label=self.lang['i334_custom'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, width=360, parent=self.allUIs["rebuilderLayout"])
        self.startGuideModules(self.customFolder, "start", "rebuilderCustomLayout")
        cmds.separator(style='none', parent=self.allUIs["rebuilderLayout"])
        self.rebuilderFLList = ["rebuilderStartLayout", "rebuilderSourceLayout", "rebuilderSetupLayout", "rebuilderDeformingLayout", "rebuilderCustomLayout"]
        self.collapseAllFL("triCollapseRebuilderITB", 1) #close all = hack to start opened to get the right width then collapse them
        # rebuilder
        self.allUIs["footerRebuilder"] = cmds.columnLayout('footerRebuilder', adjustableColumn=False, parent=self.allUIs["rebuilderTabLayout"])
        cmds.separator(style='in', height=20, width=370, parent=self.allUIs["footerRebuilder"])
        self.allUIs["selectAllProcessCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i292_processes'].lower(), value=True, changeCommand=partial(self.changeActiveAllModules, self.rebuilderInstanceList), parent=self.allUIs["footerRebuilder"])
        cmds.separator(style='none', height=10, parent=self.allUIs["footerRebuilder"])
        self.allUIs["selectedRebuildersPL"] = cmds.paneLayout("selectedRebuildersPL", configuration="vertical2", separatorThickness=7.0, width=370, parent=self.allUIs["footerRebuilder"])
        self.allUIs["splitDataSelectProcessBT"] = cmds.button("splitDataSelectProcessBT", label=self.lang['r002_splitData'].upper(), command=partial(self.runSelectedActions, self.rebuilderInstanceList, True, True, actionType="r000_rebuilder"), parent=self.allUIs["selectedRebuildersPL"])
        self.allUIs["rebuildSelectProcessBT"] = cmds.button("rebuildSelectProcessBT", label=self.lang['r001_rebuild'].upper(), command=partial(self.runSelectedActions, self.rebuilderInstanceList, False, True, actionType="r000_rebuilder"), parent=self.allUIs["selectedRebuildersPL"])
        cmds.separator(style='none', height=10, parent=self.allUIs["footerRebuilder"])
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["rebuilderTabLayout"], edit=True,
                        attachForm=[(self.allUIs["rebuilderMainLayout"], 'left', 5), (self.allUIs["rebuilderMainLayout"], 'right', 5), (self.allUIs["rebuilderMainLayout"], 'bottom', 80), 
                                    (self.allUIs["assetMainLayout"], 'left', 5), (self.allUIs["assetMainLayout"], 'right', 5), (self.allUIs["assetMainLayout"], 'top', 15),
                                    (self.allUIs["footerRebuilder"], 'left', 5), (self.allUIs["footerRebuilder"], 'right', 5), (self.allUIs["footerRebuilder"], 'bottom', 5)],
                        attachControl=[(self.allUIs["rebuilderMainLayout"], 'top', 10, self.allUIs["processesLayout"]), (self.allUIs["processesLayout"], 'top', 10, self.allUIs["assetMainLayout"])],
                        attachNone=[(self.allUIs["footerRebuilder"], 'top')]
                        )
        
        # --
        # call tabLayouts:
        cmds.tabLayout(self.allUIs["mainTabLayout"], edit=True, tabLabel=((self.allUIs["riggingTabLayout"], 'Rigging'), (self.allUIs["skinningTabLayout"], 'Skinning'), (self.allUIs["controllerTabLayout"], self.lang['i342_controllers']), (self.allUIs["toolsTabLayout"], self.lang['i343_tools']), (self.allUIs["validatorTabLayout"], self.lang['v000_validator']), (self.allUIs["rebuilderTabLayout"], self.lang['r000_rebuilder'])))
        self.selList = cmds.ls(selection=True)



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

    
    def refresh_main_ui(self, savedScene=False, resetButtons=True, clearSel=False, *args):
        """ Read guides, joints, geometries and refresh the UI without reload the script creating a new instance.
            Useful to rebuilding process when creating a new scene
        """
        if savedScene:
            self.selList = cmds.ls(selection=True)
            self.rebuilding = False
        self.populateCreatedGuideModules()
        self.checkImportedGuides()
        self.checkGuideNets()
        self.populateJoints()
        self.populateGeoms()
        if not self.rebuilding:
            if resetButtons:
                self.resetAllButtonColors()
            self.ar.pipeliner.refreshAssetData()
            for rebuildInstance in self.rebuilderInstanceList:
                rebuildInstance.updateActionButtons(color=False)
        try:
            self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=False, compressUndo=True)
        except:
            self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=False, killWithScene=False, compressUndo=True)
        if savedScene:
            cmds.select(clear=True)
            if self.selList:
                cmds.select(self.selList)
        if clearSel:
            cmds.select(clear=True)
        self.rebuilding = False


    def startScriptJobs(self, *args):
        """ Create scriptJobs to read:
            - NewSceneOpened
            - SceneSaved
            - deleteAll = new scene (disable to don't reset the asset context when running a new scene for the first module)
            - SelectionChanged
            - WorkspaceChanged = not documented
        """
        cmds.scriptJob(event=('SceneOpened', partial(self.refresh_main_ui, clearSel=True)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        #cmds.scriptJob(event=('deleteAll', self.refresh_main_ui), parent='dpAutoRigSystemWC', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
        cmds.scriptJob(event=('NewSceneOpened', self.refresh_main_ui), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('SceneSaved', partial(self.refresh_main_ui, savedScene=True, resetButtons=False)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('workspaceChanged', self.ar.pipeliner.refreshAssetData), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=False, compressUndo=True, force=True)
        self.ctrls.startCorrectiveEditMode()
        self.jobSelectedGuide()


    def deleteExistWindow(self, *args):
        """ Check if there are the dpAutoRigWindow and a control element to delete the UI.
        """
        if cmds.workspaceControl("dpAutoRigSystemWC", query=True, exists=True):
            cmds.workspaceControl("dpAutoRigSystemWC", edit=True, close=True)
            #cmds.deleteUI("dpAutoRigSystemWC", control=True)
        winNameList = ["dpARLoadWin", "dpInfoWindow", "dpNewAssetWindow", "dpReplaceDPDataWindow", "dpSelectAssetWindow", "dpSaveVersionWindow", self.ar.data.plus_info_win_name, self.ar.data.color_override_win_name]
        for winName in winNameList:
            self.ar.utils.closeUI(winName)