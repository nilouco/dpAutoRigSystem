#!/usr/bin/python
# -*- coding: utf-8 -*-

###################################################################
#
#    dpAutoRig Python script
#
#    author:  Danilo Pinheiro
#
#    contact: nilouco@gmail.com
#             nilouco.blogspot.com
#
#    date:
#        v 1.0 _ 2010-09-18 - start working based in dpAutoRig.mel v1.3
#        v 2.0 _ 2011-08-03 - first version created
#        v 2.0 _ 2011-10-09 - first version released for Maya 2011, 2012
#        v 2.1 _ 2012-03-27 - Mac version updated, thanks to Roger Santos
#        v 2.2 _ 2012-06-01 - Maya 2013, fixed: limb stretch calcul, (des)active poleVector, leg poleVector parent,
#                                               ikFkBlend attr for many instances, control size by guide scale,
#                                               mirror control shape, module count, dontDelete locators
#        v 2.3 _ 2012-08-27 - new icons by Leandro Wagner, fixed: thumb, spine scale by James do Carmo
#		 v 2.4 _ 2013-02-01 - fixed: doNotSkin ribbon nurbsSurface, find masterGrp, orient head from masterCtrl,
#                                    print messages (, at the end), centered pivot of chestB_Ctrl (spine),
#                                    clavicle pivot position, correct controls mirror based in dpLimb style,
#                                    quadruped front legs using ikSpring solver, find environment path,
#                                    loading decomposeMatrix node in order to create mirror, headFollow
#                             implemented: new feature for dpLimb with bend ribbons by James do Carmo
#        v 2.5 _ 2014-06-05 - fixed: name convension for controls "_Ctrl", joint scaleCompensate as False,
#                                    displayAnnotation option for poleVector controls, head scalable,
#                                    redefined clavicle/hips control, render_Grp, ikStretch/reverseFoot integration
#                             implemented: dpLimb extremLocToParent control (working for ik/Fk), global_Ctrl,
#                                          dpFoot footRoll and sideRoll attributes, footMiddleCtrl translate and scale,
#                                          Proxy_Grp, FX_Grp, Jaw autoTranslate, StickyLips, EyeLookAt, Finger Ik setup,
#                                          Add Hand Follow, Target Mirror
#                             changed: all names to UpperCamelCase (PascalCase)
#       v 2.6 _ 2015-06-08 - fixed: dpTargetMirror with locked transform, arm stretchale, integrated reverseFootCtrl_Old renaming,
#                                   R_Leg_IkFkBlendGrpToRevFoot_Grp_ParentConstraint offset without stretch, addBend and forearm,
#                                   fkLine flip mirror, biped ear, quadruped legs, limb start stretch value
#                            implemented: findPath to Linux OS on dpUtils, eyeScale, sideLips, ballSpin and ballTurn, limb fkIsolated,
#                                         ikFkSnap (thanks to Renaud Lessard), head translation, finger ikStretch, limb volume variation,
#                                         eyeLookAt activation with baseCtrl, limb extra bends, shapeSize
#                            changed: only one limb corner joint, unlocked fk translation,
#       v 3.0 _ 2015-09-30 - GitHub OpenSource by Sébastien Bourgoing and Renaud Lessard from Squeeze Studio Animation, thanks!
#                            All updates will be publish in GitHub:
#                            https://github.com/nilouco/dpAutoRigSystem
#
#
###################################################################



# importing libraries:
try:
    import maya.cmds as cmds
    import pymel.core as pymel
    import json
    import os
    import sys
    import re
    import time
    import getpass
    from functools import partial
    import Modules.Library.dpUtils as utils
    import Modules.Library.dpControls as ctrls
    import Modules.dpBaseClass as Base
    import Modules.dpLayoutClass as Layout
    import Extras.dpUpdateRigInfo as rigInfo
    reload(utils)
    reload(ctrls)
    reload(rigInfo)
    reload(Base)
    reload(Layout)
except Exception as e:
    print "Error: importing python modules!!!\n",
    print e

# declaring member variables
DPAR_VERSION = "3.05.3"
ENGLISH = "English"
MODULES = "Modules"
SCRIPTS = "Scripts"
EXTRAS = "Extras"
BASE_NAME = "dpAR_"
EYE = "Eye"
HEAD = "Head"
SPINE = "Spine"
LIMB = "Limb"
FOOT = "Foot"
FINGER = "Finger"
ARM = "Arm"
LEG = "Leg"
SINGLE = "Single"
GUIDE_BASE_NAME = "Guide_Base"
GUIDE_BASE_ATTR = "guideBase"
MODULE_NAMESPACE_ATTR = "moduleNamespace"
MODULE_INSTANCE_INFO_ATTR = "moduleInstanceInfo"



class DP_AutoRig_UI:
    
    ###################### Start: UI
    
    def __init__(self):
        """ Start the window, menus and main layout for dpAutoRig UI.
        """

        try:
            # store all UI elements in a dictionary:
            self.allUIs = {}
            self.iDeleteJobId = 0
            self.iSelChangeJobId = 0
            # creating User Interface (UI) Window:
            self.deleteExistWindow()
            dpAR_winWidth  = 305
            dpAR_winHeight = 605
            self.allUIs["dpAutoRigWin"] = cmds.window('dpAutoRigWindow', title='dpAutoRig System - v'+str(DPAR_VERSION)+' - UI', iconName='dpAutoRig', widthHeight=(dpAR_winWidth, dpAR_winHeight), menuBar=True, sizeable=True, minimizeButton=True, maximizeButton=False)
            
            # creating menus:
            # language menu:
            cmds.menu('languageMenu', label='Language')
            cmds.radioMenuItemCollection('languageRadioMenuCollection')
            # create a language list:
            self.langList = self.language()
            # create menuItems from language list:
            if self.langList:
                # verify if there is a optionVar of last language choose by user in the maya system:
                lastLangExists = cmds.optionVar( exists='dpAutoRigLastLanguage' )
                if not lastLangExists:
                    # if not exists a last language, set it to English if it exists, or to the first language in the list:
                    if ENGLISH in self.langList:
                        cmds.optionVar( stringValue=('dpAutoRigLastLanguage', ENGLISH) )
                    else:
                        cmds.optionVar( stringValue=('dpAutoRigLastLanguage', self.langList[0]) )
                # get its value puting in a variable lastLang:
                self.lastLang = cmds.optionVar( query='dpAutoRigLastLanguage' )
                # if the last language in the system was different of json files, set it to English or to the first language in the list also:
                if not self.lastLang in self.langList:
                    if ENGLISH in self.langList:
                        self.lastLang = ENGLISH
                    else:
                        self.lastLang = self.langList[0]
                # create menuItems with the command to set the last language variable, delete languageUI and call mainUI() again when changed:
                for idiom in self.langList:
                    cmds.menuItem( idiom+"_MI", label=idiom, radioButton=False, collection='languageRadioMenuCollection', command='import maya.cmds as cmds; cmds.optionVar(remove=\"dpAutoRigLastLanguage\"); cmds.optionVar(stringValue=(\"dpAutoRigLastLanguage\", \"'+idiom+'\")); cmds.deleteUI(\"languageTabLayout\"); autoRigUI.mainUI()')
                # load the last language from optionVar value:
                cmds.menuItem( self.lastLang+"_MI", edit=True, radioButton=True, collection='languageRadioMenuCollection' )
            else:
                print "Error: Cannot load the json language files!\n",
                return
            
            # option menu:
            cmds.menu( 'optionMenu', label='Window' )
            cmds.menuItem( 'reloadUI_MI', label='Reload UI', command=self.jobReloadUI )
            cmds.menuItem( 'quit_MI', label='Quit', command=self.deleteExistWindow )
            # help menu:
            cmds.menu( 'helpMenu', label='Help', helpMenu=True )
            cmds.menuItem( 'about_MI"', label='About', command=partial(self.info, 'm015_about', 'i006_aboutDesc', None, 'center', 305, 250) )
            cmds.menuItem( 'author_MI', label='Author', command=partial(self.info, 'm016_author', 'i007_authorDesc', None, 'center', 305, 250) )
            cmds.menuItem( 'idiom_MI', label='Idioms', command=partial(self.info, 'm009_idioms', 'i012_idiomsDesc', None, 'center', 305, 250) )
            cmds.menuItem( 'help_MI', label='Help...', command=self.help )
            
            # create the main layout:
            self.allUIs["mainLayout"] = cmds.formLayout('mainLayout')
            # here we will populate with layout from mainUI based in the choose language.
            
            # call mainUI in order to populate the main layout:
            self.mainUI()
        
        except Exception as e:
            print "Error: dpAutoRig UI window !!!\n"
            print "Exception:", e
            print self.langDic[self.langName]['i008_errorUI'],
            return
        

        # call UI window: Also ensure that when thedock controler X button it it, the window is killed and the dock control too
        self.iUIKilledId = cmds.scriptJob(uid=[self.allUIs["dpAutoRigWin"], self.jobWinClose])
        self.pDockCtrl = cmds.dockControl( 'dpAutoRigSystem', area="left", content=self.allUIs["dpAutoRigWin"], vcc=self.jobDockVisChange)
        print self.pDockCtrl

    def deleteExistWindow(self, *args):
        """ Check if there are the dpAutoRigWindow and dpAutoRigSystem_Control to deleteUI.
        """
        if cmds.window('dpAutoRigWindow', query=True, exists=True):
            cmds.deleteUI('dpAutoRigWindow', window=True)
        if cmds.dockControl('dpAutoRigSystem', exists=True):
            cmds.deleteUI('dpAutoRigSystem', control=True)
    
    
    def language(self):
        """ Find all json language file in the languagePath and get idiom used for each "language module".
            Create a dictionary with dictionaries of all languages found.
            Return a list with the name of the languages found.
        """
        # declare the resulted list:
        self.langList = []
        self.langDic = {}
        # find path where 'dpAutoRig.py' is been executed:
        path = utils.findPath("dpAutoRig.py")
        langDir = "Languages/"
        langPath = path + "/" + langDir
        # list all files in the language directory:
        allFileList = os.listdir(langPath)
        for file in allFileList:
            # verify if there is the extension ".json"
            if ".json" in file:
                # get the name of the languafe from the file name:
                langName = file.partition(".json")[0]
                # clear the old variable content and open the json file as read:
                content = None
                fileDictionary = open(langPath + file, "r")
                try:
                    # read the json file content and store it in a dictionary:
                    content = json.loads(fileDictionary.read())
                    self.langDic[langName] = content
                    self.langList.append(langName)
                except:
                    print "Error: json Language file corrupted:", file,
                # close the json file:
                fileDictionary.close()
        return self.langList
    
    
    def mainUI(self):
        """ Create the layouts inside of the mainLayout. Here will be the entire User Interface.
        """
        # get current language choose UI from menu:
        for idiom in self.langList:
            if cmds.menuItem( idiom+"_MI", query=True, radioButton=True ):
                self.langName = idiom
                break
        
        # creating tabs - languageTabLayout:
        self.allUIs["languageTabLayout"] = cmds.tabLayout('languageTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=self.allUIs["mainLayout"])
        cmds.formLayout( self.allUIs["mainLayout"], edit=True, attachForm=((self.allUIs["languageTabLayout"], 'top', 0), (self.allUIs["languageTabLayout"], 'left', 0), (self.allUIs["languageTabLayout"], 'bottom', 0), (self.allUIs["languageTabLayout"], 'right', 0)) )
        
        # --
        
        # interface of Rigging tab - formLayout:
        self.allUIs["riggingTabLayout"] = cmds.formLayout('riggingTabLayout', numberOfDivisions=100, parent=self.allUIs["languageTabLayout"])
        
        #colTopLefA - columnLayout:
        self.allUIs["colTopLeftA"] = cmds.columnLayout('colTopLeftA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["i000_guides"] = cmds.text(self.langDic[self.langName]['i000_guides'], font="boldLabelFont", width=150, align='center', parent=self.allUIs["colTopLeftA"])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colTopRightA - columnLayout:
        self.allUIs["colTopRightA"] = cmds.columnLayout('colTopRightA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["i001_modules"] = cmds.text(self.langDic[self.langName]['i001_modules'], font="boldLabelFont", width=150, align='center', parent=self.allUIs["colTopRightA"])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colMiddleLeftA - scrollLayout - guidesLayout:
        self.allUIs["colMiddleLeftA"] = cmds.scrollLayout("colMiddleLeftA", width=150, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["guidesLayoutA"] = cmds.columnLayout("guidesLayoutA", adjustableColumn=True, width=122, rowSpacing=3, parent=self.allUIs["colMiddleLeftA"])
        # here will be populated by guides of modules and scripts...
        self.allUIs["i030_standard"] = cmds.text(self.langDic[self.langName]['i030_standard'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.guideModuleList = self.startGuideModules(MODULES, "start", "guidesLayoutA")
        cmds.separator(style='doubleDash', height=10, parent=self.allUIs["guidesLayoutA"])
        self.allUIs["i031_integrated"] = cmds.text(self.langDic[self.langName]['i031_integrated'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.startGuideModules(SCRIPTS, "start", "guidesLayoutA")
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colMiddleRightA - scrollLayout - modulesLayout:
        self.allUIs["colMiddleRightA"] = cmds.scrollLayout("colMiddleRightA", width=150, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=200, parent=self.allUIs["colMiddleRightA"])
        # here will be populated by created instances of modules...
        # after footerA we will call the function to populate here, because it edits the footerAText
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #editSelectedModuleLayoutA - frameLayout:
        self.allUIs["editSelectedModuleLayoutA"] = cmds.frameLayout('editSelectedModuleLayoutA', label=self.langDic[self.langName]['i011_selectedModule'], collapsable=True, collapse=False, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["selectedModuleLayout"] = cmds.columnLayout('selectedModuleLayout', adjustableColumn=True, parent=self.allUIs["editSelectedModuleLayoutA"])
        
        #optionsA - frameLayout:
        self.allUIs["optionsA"] = cmds.frameLayout('optionsA', label=self.langDic[self.langName]['i002_options'], collapsable=True, collapse=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigOptionsLayout"] = cmds.columnLayout('rigOptionsLayout', adjustableColumn=True, columnOffset=('left', 5), parent=self.allUIs["optionsA"])
        self.allUIs["prefixLayout"] = cmds.rowColumnLayout('prefixLayout', numberOfColumns=2, columnWidth=[(1, 40), (2, 100)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["prefixTextField"] = cmds.textField('prefixTextField', text="", parent= self.allUIs["prefixLayout"], changeCommand=self.setPrefix)
        self.allUIs["prefixText"] = cmds.text('prefixText', align='left', label=self.langDic[self.langName]['i003_prefix'], parent=self.allUIs["prefixLayout"])
        cmds.setParent(self.allUIs["rigOptionsLayout"])
        self.allUIs["hideJointsCB"] = cmds.checkBox('hideJointsCB', label=self.langDic[self.langName]['i009_hideJointsCB'], align='left', v=0, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["integrateCB"] = cmds.checkBox('integrateCB', label=self.langDic[self.langName]['i010_integrateCB'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["defaultRenderLayerCB"] = cmds.checkBox('defaultRenderLayerCB', label=self.langDic[self.langName]['i004_defaultRL'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["colorizeCtrlCB"] = cmds.checkBox('colorizeCtrlCB', label=self.langDic[self.langName]['i065_colorizeCtrl'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["addAttrCB"] = cmds.checkBox('addAttrCB', label=self.langDic[self.langName]['i066_addAttr'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])

        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #footerA - columnLayout:
        self.allUIs["footerA"] = cmds.columnLayout('footerA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigAllButton"] = cmds.button(label=self.langDic[self.langName]['i020_rigAll'], annotation=self.langDic[self.langName]['i021_rigAllDesc'], backgroundColor=(0.6, 1.0, 0.6), command=self.rigAll, parent=self.allUIs["footerA"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerA"])
        # this text will be actualized by the number of module instances created in the scene...
        self.allUIs["footerAText"] = cmds.text('footerAText', align='center', label="# "+self.langDic[self.langName]['i005_footerA'], parent=self.allUIs["footerA"])
        cmds.setParent( self.allUIs["languageTabLayout"] )
        
        # call the function in order to populate the colMiddleRightA (modulesLayout)
        self.populateCreatedGuideModules()
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["riggingTabLayout"], edit=True,
                        attachForm=[(self.allUIs["colTopLeftA"], 'top', 5), (self.allUIs["colTopLeftA"], 'left', 5), (self.allUIs["colTopRightA"], 'top', 5), (self.allUIs["colTopRightA"], 'right', 5), (self.allUIs["colMiddleLeftA"], 'left', 5), (self.allUIs["colMiddleRightA"], 'right', 5), (self.allUIs["optionsA"], 'left', 5), (self.allUIs["optionsA"], 'right', 5), (self.allUIs["editSelectedModuleLayoutA"], 'left', 5), (self.allUIs["editSelectedModuleLayoutA"], 'right', 5), (self.allUIs["footerA"], 'left', 5), (self.allUIs["footerA"], 'bottom', 5), (self.allUIs["footerA"], 'right', 5)],
                        attachControl=[(self.allUIs["colMiddleLeftA"], 'top', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colTopRightA"], 'left', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colMiddleLeftA"], 'bottom', 5, self.allUIs["editSelectedModuleLayoutA"]), (self.allUIs["colMiddleRightA"], 'top', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colMiddleRightA"], 'bottom', 5, self.allUIs["editSelectedModuleLayoutA"]), (self.allUIs["colMiddleRightA"], 'left', 5, self.allUIs["colMiddleLeftA"]), (self.allUIs["editSelectedModuleLayoutA"], 'bottom', 5, self.allUIs["optionsA"]), (self.allUIs["optionsA"], 'bottom', 5, self.allUIs["footerA"])],
                        #attachPosition=[(self.allUIs["colTopLeftA"], 'right', 5, 50), (self.allUIs["colTopRightA"], 'left', 0, 50)],
                        attachNone=[(self.allUIs["footerA"], 'top')]
                        )
        
        # create the job of selected guide module and when new scene is created:
        self.iDeleteJobId = cmds.scriptJob(event=('deleteAll', self.jobReloadUI), parent='dpAutoRigWindow', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
        self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)
        
        # --
        
        # interface of Skinning tab:
        self.allUIs["skinningTabLayout"] = cmds.formLayout('skinningTabLayout', numberOfDivisions=100, parent=self.allUIs["languageTabLayout"])
        
        #colSkinLeftA - columnLayout:
        self.allUIs["colSkinLeftA"] = cmds.columnLayout('colSkinLeftA', adjustableColumn=True, width=190, parent=self.allUIs["skinningTabLayout"])
        # radio buttons:
        self.allUIs["jntCollection"] = cmds.radioCollection('jntCollection', parent=self.allUIs["colSkinLeftA"])
        allJoints   = cmds.radioButton( label=self.langDic[self.langName]['i022_listAllJnts'], annotation="allJoints", onCommand=self.populateJoints )
        dpARJoints  = cmds.radioButton( label=self.langDic[self.langName]['i023_listdpARJnts'], annotation="dpARJoints", onCommand=self.populateJoints )
        self.allUIs["jointsDisplay"] = cmds.rowColumnLayout('jointsDisplay', numberOfColumns=2, columnWidth=[(1, 40), (2, 100)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["colSkinLeftA"])
        self.allUIs["_JntCB"] = cmds.checkBox('_JntCB', label="_Jnt", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["_JisCB"] = cmds.checkBox('_JisCB', label="_Jis", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["jntTextScrollLayout"] = cmds.textScrollList( 'jntTextScrollLayout', width=30, allowMultiSelection=True, selectCommand=self.atualizeSkinFooter, parent=self.allUIs["skinningTabLayout"] )
        cmds.radioCollection( self.allUIs["jntCollection"], edit=True, select=dpARJoints )
        cmds.setParent(self.allUIs["skinningTabLayout"])
        
        #colSkinRightA - columnLayout:
        self.allUIs["colSkinRightA"] = cmds.columnLayout('colSkinRightA', adjustableColumn=True, width=190, parent=self.allUIs["skinningTabLayout"])
        self.allUIs["geomCollection"] = cmds.radioCollection('geomCollection', parent=self.allUIs["colSkinRightA"])
        allGeoms   = cmds.radioButton( label=self.langDic[self.langName]['i026_listAllJnts'], annotation="allGeoms", onCommand=self.populateGeoms )
        selGeoms   = cmds.radioButton( label=self.langDic[self.langName]['i027_listSelJnts'], annotation="selGeoms", onCommand=self.populateGeoms )
        self.allUIs["modelsTextScrollLayout"] = cmds.textScrollList( 'modelsTextScrollLayout', width=30, allowMultiSelection=True, selectCommand=self.atualizeSkinFooter, parent=self.allUIs["skinningTabLayout"] )
        self.allUIs["geoLongName"] = cmds.checkBox('geoLongName', label=self.langDic[self.langName]['i073_displayLongName'], align='left', value=1, changeCommand=self.populateGeoms, parent=self.allUIs["colSkinRightA"])
        cmds.radioCollection( self.allUIs["geomCollection"], edit=True, select=allGeoms )
        cmds.setParent(self.allUIs["skinningTabLayout"])
        
        #footerB - columnLayout:
        self.allUIs["footerB"] = cmds.columnLayout('footerB', adjustableColumn=True, parent=self.allUIs["skinningTabLayout"])
        cmds.separator(style='none', height=3, parent=self.allUIs["footerB"])
        self.allUIs["skinButton"] = cmds.button("skinButton", label=self.langDic[self.langName]['i028_skinButton'], backgroundColor=(0.5, 0.8, 0.8), command=partial(self.skinFromUI), parent=self.allUIs["footerB"])
        self.allUIs["footerAddRem"] = cmds.paneLayout("footerAddRem", cn="vertical2", st=2.0, parent=self.allUIs["footerB"])
        self.allUIs["addSkinButton"] = cmds.button("addSkinButton", label=self.langDic[self.langName]['i063_skinAddBtn'], backgroundColor=(0.7, 0.9, 0.9), command=partial(self.skinFromUI, "Add"), parent=self.allUIs["footerAddRem"])
        self.allUIs["removeSkinButton"] = cmds.button("removeSkinButton", label=self.langDic[self.langName]['i064_skinRemBtn'], backgroundColor=(0.1, 0.3, 0.3), command=partial(self.skinFromUI, "Remove"), parent=self.allUIs["footerAddRem"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerB"])
        # this text will be actualized by the number of joints and geometries in the textScrollLists for skinning:
        self.allUIs["footerBText"] = cmds.text('footerBText', align='center', label="0 "+self.langDic[self.langName]['i025_joints']+" 0 "+self.langDic[self.langName]['i024_geometries'], parent=self.allUIs["footerB"])
        cmds.setParent( self.allUIs["languageTabLayout"] )
        
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["skinningTabLayout"], edit=True,
                        attachForm=[(self.allUIs["colSkinLeftA"], 'top', 5), (self.allUIs["colSkinLeftA"], 'left', 5), (self.allUIs["colSkinRightA"], 'top', 5), (self.allUIs["colSkinRightA"], 'right', 5), (self.allUIs["footerB"], 'left', 5), (self.allUIs["footerB"], 'bottom', 5), (self.allUIs["footerB"], 'right', 5), (self.allUIs["modelsTextScrollLayout"], 'right', 5), (self.allUIs["jntTextScrollLayout"], 'left', 5)],
                        attachControl=[(self.allUIs["colSkinRightA"], 'left', 5, self.allUIs["colSkinLeftA"]), (self.allUIs["modelsTextScrollLayout"], 'bottom', 5, self.allUIs["footerB"]), (self.allUIs["modelsTextScrollLayout"], 'top', 5, self.allUIs["colSkinRightA"]), (self.allUIs["modelsTextScrollLayout"], 'left', 5, self.allUIs["colSkinLeftA"]), (self.allUIs["jntTextScrollLayout"], 'bottom', 5, self.allUIs["footerB"]), (self.allUIs["jntTextScrollLayout"], 'top', 5, self.allUIs["colSkinLeftA"]), (self.allUIs["jntTextScrollLayout"], 'right', 5, self.allUIs["colSkinRightA"])],
                        attachPosition=[(self.allUIs["colSkinLeftA"], 'right', 5, 50), (self.allUIs["colSkinRightA"], 'left', 5, 50), (self.allUIs["jntTextScrollLayout"], 'right', 3, 50), (self.allUIs["modelsTextScrollLayout"], 'left', 3, 50)],
                        attachNone=[(self.allUIs["footerB"], 'top')]
                        )
        
        # populate the joint and geometries lists:
        self.populateJoints()
        self.populateGeoms()
        
        # --
        
        # interface of Extra tab - formLayout:
        self.allUIs["extraTabLayout"] = cmds.formLayout('extraTabLayout', numberOfDivisions=100, parent=self.allUIs["languageTabLayout"])
        # extraMainLayout - scrollLayout:
        self.allUIs["extraMainLayout"] = cmds.scrollLayout("extraMainLayout", parent=self.allUIs["extraTabLayout"])
        self.allUIs["extraLayout"] = cmds.columnLayout("extraLayout", adjustableColumn=True, rowSpacing=3, parent=self.allUIs["extraMainLayout"])
        self.extraModuleList = self.startGuideModules(EXTRAS, "start", "extraLayout")
        
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["extraTabLayout"], edit=True,
                        attachForm=[(self.allUIs["extraMainLayout"], 'top', 20), (self.allUIs["extraMainLayout"], 'left', 5), (self.allUIs["extraMainLayout"], 'right', 5), (self.allUIs["extraMainLayout"], 'bottom', 5)]
                        )
        
        # --
        
        # call tabLayouts:
        cmds.tabLayout( self.allUIs["languageTabLayout"], edit=True, tabLabel=((self.allUIs["riggingTabLayout"], 'Rigging'), (self.allUIs["skinningTabLayout"], 'Skinning'), (self.allUIs["extraTabLayout"], 'Extra')) )
        cmds.select(clear=True)

    
    def jobReloadUI(self, *args):
        """ This scriptJob active when we got one new scene in order to reload the UI.
        """
        import maya.cmds as cmds
        cmds.select(clear=True)
        import dpAutoRig as autoRig
        reload( autoRig )
        autoRigUI = autoRig.DP_AutoRig_UI()
        cmds.dockControl(self.pDockCtrl, r=True, edit=True) #Force focus on the tool when it's open

    def jobWinClose(self, *args):
        #This job will ensure that the dock control is killed correctly
        if (not cmds.dockControl(self.pDockCtrl, vis=True, query=True)):
            if cmds.dockControl('dpAutoRigSystem', exists=True):
                cmds.deleteUI('dpAutoRigSystem', control=True)

    def jobDockVisChange(self, *args):
        #Force focus
        cmds.dockControl(self.pDockCtrl, r=True, edit=True) #Force focus on the tool when it's open
    
    def jobSelectedGuide(self):
        """ This scriptJob read if the selected item in the scene is a guideModule and reload the UI.
        """
        # run the UI part:
        selectedGuideNodeList = []
        selectedList = []

        # get selected items:
        selectedList = cmds.ls(selection=True, long=True)
        if selectedList:
            updatedGuideNodeList = []
            needUpdateSelect = False
            for selectedItem in selectedList:
                if cmds.objExists(selectedItem+"."+GUIDE_BASE_ATTR) and cmds.getAttr(selectedItem+"."+GUIDE_BASE_ATTR) == 1:
                    if not ":" in selectedItem[selectedItem.rfind("|"):]:
                        newGuide = self.setupDuplicatedGuide(selectedItem)
                        updatedGuideNodeList.append(newGuide)
                        needUpdateSelect = True
                    else:
                        selectedGuideNodeList.append(selectedItem)
            if needUpdateSelect:
                self.jobReloadUI(self)
                cmds.select(updatedGuideNodeList)

        # re-create module layout:
        if selectedGuideNodeList:
            for moduleInstance in self.moduleInstancesList:
                cmds.button(moduleInstance.selectButton, edit=True, label=" ", backgroundColor=(0.5, 0.5, 0.5))
                for selectedGuide in selectedGuideNodeList:
                    selectedGuideInfo = cmds.getAttr(selectedGuide+"."+MODULE_INSTANCE_INFO_ATTR)
                    if selectedGuideInfo == str(moduleInstance):
                        moduleInstance.reCreateEditSelectedModuleLayout(bSelect=False)
        # delete module layout:
        else:
            try:
                cmds.frameLayout('editSelectedModuleLayoutA', edit=True, label=self.langDic[self.langName]['i011_selectedModule'])
                cmds.deleteUI("selectedColumn")
                for moduleInstance in self.moduleInstancesList:
                    cmds.button(moduleInstance.selectButton, edit=True, label=" ", backgroundColor=(0.5, 0.5, 0.5))
            except:
                pass

        # re-select items:
        #if selectedList:
        #    cmds.select(selectedList)
        # call reload the geometries in skin UI:
        self.reloadPopulatedGeoms()
    
    
    def setupDuplicatedGuide(self, selectedItem, *args):
        """ This method will create a new module instance for a duplicated guide found.
            Returns a guideBase for a new module instance.
        """
        # Duplicating a module guide
        print self.langDic[self.langName]['i067_duplicating']

        # declaring variables
        transformAttrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        nSegmentsAttr = "nJoints"
        customNameAttr = "customName"
        mirroirAxisAttr = "mirrorAxis"

        # unparenting
        parentList = cmds.listRelatives(selectedItem, parent=True)
        if parentList:
            cmds.parent(selectedItem, world=True)
            selectedItem = selectedItem[selectedItem.rfind("|"):]

        # getting duplicated item values
        moduleNamespaceValue = cmds.getAttr(selectedItem+"."+MODULE_NAMESPACE_ATTR)
        moduleInstanceInfoValue = cmds.getAttr(selectedItem+"."+MODULE_INSTANCE_INFO_ATTR)
        # generating naming values
        origGuideName = moduleNamespaceValue+":"+GUIDE_BASE_NAME
        thatClassName = moduleNamespaceValue.partition("__")[0]
        thatModuleName = moduleInstanceInfoValue[:moduleInstanceInfoValue.rfind(thatClassName)-1]
        thatModuleName = thatModuleName[thatModuleName.rfind(".")+1:]
        moduleDir = moduleInstanceInfoValue[:moduleInstanceInfoValue.rfind(thatModuleName)-1]
        moduleDir = moduleDir[moduleDir.rfind(".")+1:]

        # initializing a new module instance
        newGuideInstance = eval('self.initGuide("'+thatModuleName+'", "'+moduleDir+'")')
        newGuideName = cmds.ls(selection=True)[0]
        newGuideNamespace = cmds.getAttr(newGuideName+"."+MODULE_NAMESPACE_ATTR)
        # getting a good attribute list
        toSetAttrList = cmds.listAttr(selectedItem)
        guideBaseAttrIdx = toSetAttrList.index(GUIDE_BASE_ATTR)
        toSetAttrList = toSetAttrList[guideBaseAttrIdx:]
        toSetAttrList.remove(GUIDE_BASE_ATTR)
        toSetAttrList.remove(MODULE_NAMESPACE_ATTR)
        toSetAttrList.remove(customNameAttr)
        toSetAttrList.remove(mirroirAxisAttr)
        
        # check for special attributes
        if cmds.objExists(selectedItem+"."+nSegmentsAttr):
            toSetAttrList.remove(nSegmentsAttr)
            nJointsValue = cmds.getAttr(selectedItem+'.'+nSegmentsAttr)
            if nJointsValue > 1:
                eval('self.guide.'+thatClassName+'.changeJointNumber(newGuideInstance, '+str(nJointsValue)+')')
        if cmds.objExists(selectedItem+"."+customNameAttr):
            customNameValue = cmds.getAttr(selectedItem+'.'+customNameAttr)
            if customNameValue != "" and customNameValue != None:
                eval('self.guide.'+thatClassName+'.editUserName(newGuideInstance, checkText="'+customNameValue+'")')
        if cmds.objExists(selectedItem+"."+mirroirAxisAttr):
            mirroirAxisValue = cmds.getAttr(selectedItem+'.'+mirroirAxisAttr)
            if mirroirAxisValue != "off":
                eval('self.guide.'+thatClassName+'.changeMirror(newGuideInstance, "'+mirroirAxisValue+'")')

        # get and set transformations
        childrenList = cmds.listRelatives(selectedItem, children=True, allDescendents=True, fullPath=True, type="transform")
        if childrenList:
            for child in childrenList:
                newChild = newGuideNamespace+":"+child[child.rfind("|")+1:]
                for transfAttr in transformAttrList:
                    try:
                        cmds.setAttr(newChild+"."+transfAttr, cmds.getAttr(child+"."+transfAttr))
                    except:
                        pass
        # set transformation for Guide_Base
        for transfAttr in transformAttrList:
            cmds.setAttr(newGuideName+"."+transfAttr, cmds.getAttr(selectedItem+"."+transfAttr))
        # setting new guide attributes
        for toSetAttr in toSetAttrList:
            try:
                cmds.setAttr(newGuideName+"."+toSetAttr, cmds.getAttr(selectedItem+"."+toSetAttr))
            except:
                cmds.setAttr(newGuideName+"."+toSetAttr, cmds.getAttr(selectedItem+"."+toSetAttr), type="string")

        # parenting correctly
        if parentList:
            cmds.parent(newGuideName, parentList[0])

        cmds.delete(selectedItem)
        return newGuideName


    def populateJoints(self, *args):
        """ This function is responsable to list all joints or only dpAR joints in the interface in order to use in skinning.
        """
        # get current jointType (all or just dpAutoRig joints):
        jntSelectedRadioButton = cmds.radioCollection(self.allUIs["jntCollection"], query=True, select=True)
        chooseJnt = cmds.radioButton(jntSelectedRadioButton, query=True, annotation=True)
        
        # list joints to be populated:
        jointList = []
        allJointList = cmds.ls(selection=False, type="joint")
        if chooseJnt == "allJoints":
            jointList = allJointList
            cmds.checkBox(self.allUIs["_JntCB"], edit=True, enable=False)
            cmds.checkBox(self.allUIs["_JisCB"], edit=True, enable=False)
        elif chooseJnt == "dpARJoints":
            cmds.checkBox(self.allUIs["_JntCB"], edit=True, enable=True)
            cmds.checkBox(self.allUIs["_JisCB"], edit=True, enable=True)
            displayJnt = cmds.checkBox(self.allUIs["_JntCB"], query=True, value=True)
            displayJis = cmds.checkBox(self.allUIs["_JisCB"], query=True, value=True)
            for jointNode in allJointList:
                if cmds.objExists(jointNode+'.'+BASE_NAME+'joint'):
                    if displayJnt:
                        if "_Jnt" in jointNode:
                            jointList.append(jointNode)
                    if displayJis:
                        if "_Jis" in jointNode:
                            jointList.append(jointNode)
        
        # populate the list:
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, removeAll=True)
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, append=jointList)
        # atualize of footerB text:
        self.atualizeSkinFooter()
    
    
    def populateGeoms(self, *args):
        """ This function is responsable to list all geometries or only selected geometries in the interface in order to use in skinning.
        """
        # get current geomType (all or just selected):
        geomSelectedRadioButton = cmds.radioCollection(self.allUIs["geomCollection"], query=True, select=True)
        chooseGeom = cmds.radioButton(geomSelectedRadioButton, query=True, annotation=True)
        
        # get user preference as long or short name:
        displayGeoLongName = cmds.checkBox(self.allUIs["geoLongName"], query=True, value=True)
        
        # list geometries to be populated:
        geomList, shortNameList, sameNameList = [], [], []
        
        currentSelectedList = cmds.ls(selection=True, long=True)
        geomTypeList = ["mesh", "nurbsSurface", "subdiv"]
        for geomType in geomTypeList:
            allGeomList = cmds.ls(selection=False, type=geomType, long=True)
            if allGeomList:
                for meshName in allGeomList:
                    if cmds.getAttr(meshName+".intermediateObject") == 0:
                        transformNameList = cmds.listRelatives(meshName, parent=True, fullPath=True, type="transform")
                        if transformNameList:
                            # do not add ribbon nurbs plane to the list:
                            if not cmds.objExists(transformNameList[0]+".doNotSkinIt"):
                                if not transformNameList[0] in geomList:
                                    if chooseGeom == "allGeoms":
                                        geomList.append(transformNameList[0])
                                        cmds.checkBox(self.allUIs["geoLongName"], edit=True, value=True, enable=False)
                                    elif chooseGeom == "selGeoms":
                                        cmds.checkBox(self.allUIs["geoLongName"], edit=True, enable=True)
                                        if transformNameList[0] in currentSelectedList or meshName in currentSelectedList:
                                            if displayGeoLongName:
                                                geomList.append(transformNameList[0])
                                            else:
                                                shortName = transformNameList[0][transformNameList[0].rfind("|")+1:]
                                                geomList.append(shortName)

        # check if we have same short name:
        if geomList:
            for g, geo in enumerate(geomList):
                if geo in geomList[:g]:
                    sameNameList.append(geo)
        if sameNameList:
            geomList.insert(0, "*")
            geomList.append(" ")
            geomList.append("-------")
            geomList.append(self.langDic[self.langName]['i074_attention'])
            geomList.append(self.langDic[self.langName]['i075_moreOne'])
            geomList.append(self.langDic[self.langName]['i076_sameName'])
            for sameName in sameNameList:
                geomList.append(sameName)
        
        
        # populate the list:
        cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, removeAll=True)
        if sameNameList:
            cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, lineFont=[(len(geomList)-len(sameNameList)-2, 'boldLabelFont'), (len(geomList)-len(sameNameList)-1, 'obliqueLabelFont'), (len(geomList)-len(sameNameList), 'obliqueLabelFont')], append=geomList)
        else:
            cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, append=geomList)
        # atualize of footerB text:
        self.atualizeSkinFooter()
    
    
    def reloadPopulatedGeoms(self, *args):
        """ This function reloads the list all selected geometries in the interface in order to use in skinning if necessary.
        """
        # store current selected items in the geometry list to skin:
        geomSelectedList = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, selectItem=True)
        # populate again the list of geometries:
        self.populateGeoms()
        # re-select the old selected items in the list if possible:
        if geomSelectedList:
            try:
                cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, selectItem=geomSelectedList)
            except:
                pass
    
    
    def atualizeSkinFooter(self, *args):
        """ Edit the label of skin footer text.
        """
        try:
            # get the number of selected items for each textScrollLayout:
            nSelectedJoints = cmds.textScrollList( self.allUIs["jntTextScrollLayout"], query=True, numberOfSelectedItems=True)
            nSelectedGeoms  = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, numberOfSelectedItems=True)
            
            # verify if there are not any selected items:
            if nSelectedJoints == 0:
                nJointItems = cmds.textScrollList( self.allUIs["jntTextScrollLayout"], query=True, numberOfItems=True)
                if nJointItems != 0:
                    nSelectedJoints = nJointItems
            if nSelectedGeoms == 0:
                nGeomItems = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, numberOfItems=True)
                if nGeomItems != 0:
                    nSelectedGeoms = nGeomItems
            
            # edit the footerB text:
            if nSelectedJoints != 0 and nSelectedGeoms != 0:
                cmds.text(self.allUIs["footerBText"], edit=True, label=str(nSelectedJoints)+" "+self.langDic[self.langName]['i025_joints']+" "+str(nSelectedGeoms)+" "+self.langDic[self.langName]['i024_geometries'])
            else:
                cmds.text(self.allUIs["footerBText"], edit=True, label=self.langDic[self.langName]['i029_skinNothing'])
        except:
            pass
    
    
    # Start working with Guide Modules:
    def startGuideModules(self, guideDir, action, layout, checkModuleList=None):
        """ Find and return the modules in the directory 'Modules'.
            Returns a list with the found modules.
        """
        # find path where 'dpAutoRig.py' is been executed:
        path = utils.findPath("dpAutoRig.py")
        print "dpAutoRigPath: "+path
        # list all guide modules:
        guideModuleList = utils.findAllModules(path, guideDir)
        print guideDir+" : "+str(guideModuleList)
        if guideModuleList:
            # change guide module list for alphabetic order:
            guideModuleList.sort()
            if action == "start":
                # create guide buttons:
                for guideModule in guideModuleList:
                    self.createGuideButton(guideModule, guideDir, layout)
            elif action == "check":
                notFoundModuleList = []
                # verify the list if exists all elements in the folder:
                if checkModuleList:
                    for checkModule in checkModuleList:
                        if not checkModule in guideModuleList:
                            notFoundModuleList.append(checkModule)
                return notFoundModuleList
        return guideModuleList
    
    
    def createGuideButton(self, guideModule, guideDir, layout):
        """ Create a guideButton for guideModule in the respective colMiddleLeftA guidesLayout.
        """
        # especific import command for guides storing theses guides modules in a variable:
        #guide = __import__("dpAutoRigSystem."+guideDir+"."+guideModule, {}, {}, [guideModule])
        basePath = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")

        # Sandbox the module import process so a single guide cannot crash the whole Autorig.
        # https://github.com/SqueezeStudioAnimation/dpAutoRigSystem/issues/28
        try:
            guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
            reload(guide)
        except Exception, e:
            print "ERROR loading extension {0}: {1}".format(guideModule, e)
            return

        # getting data from guide module:
        title = self.langDic[self.langName][guide.TITLE]
        description = self.langDic[self.langName][guide.DESCRIPTION]
        icon = guide.ICON
        # find path where 'dpAutoRig.py' is been executed to get the icon:
        path = utils.findPath("dpAutoRig.py")
        iconDir = path+icon
        # creating a basic layout for guide buttons:
        cmds.rowLayout( numberOfColumns=3, columnWidth3=(15, 30, 55), height=30, adjustableColumn=3, columnAlign=(1, 'left'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent=self.allUIs[layout] )
        cmds.button(label='?', height=30, backgroundColor=(0.8, 0.8, 0.8), command=partial(self.info, guide.TITLE, guide.DESCRIPTION, None, 'center', 305, 250))
        cmds.image(i=iconDir)

        if guideDir == MODULES:
            '''
            We need to passe the rigType parameters because the cmds.button command will send a False parameter that
            will be stock in the rigType if we don't pass the parameter
            http://stackoverflow.com/questions/24616757/maya-python-cmds-button-with-ui-passing-variables-and-calling-a-function
            '''
            cmds.button(label=title, height=30, command=partial(self.initGuide, guideModule, guideDir, Base.RigType.biped) )
        elif guideDir == SCRIPTS:
            cmds.button(label=title, height=30, command=partial(self.execScriptedGuide, guideModule, guideDir) )
        elif guideDir == EXTRAS:
            cmds.button(label=title, height=30, width=200, command=partial(self.initExtraModule, guideModule, guideDir) )

        cmds.setParent('..')
    
    #@utils.profiler
    def initGuide(self, guideModule, guideDir, rigType=Base.RigType.biped, *args):
        """ Create a guideModuleReference (instance) of a further guideModule that will be rigged (installed).
            Returns the guide instance initialised.
        """
        # creating unique namespace:
        cmds.namespace(setNamespace=":")
        # list all namespaces:
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        # check if there is "__" (double undersore) in the namespaces:
        for i in range(len(namespaceList)):
            if namespaceList[i].find("__") != -1:
                # if yes, get the name after the "__":
                namespaceList[i] = namespaceList[i].partition("__")[2]
        # send this result to findLastNumber in order to get the next moduleName +1:
        newSuffix = utils.findLastNumber(namespaceList, BASE_NAME) + 1
        # generate the current moduleName added the next new suffix:
        userSpecName = BASE_NAME + str(newSuffix)
        # especific import command for guides storing theses guides modules in a variable:
        basePath = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        self.guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(self.guide)
        # get the CLASS_NAME from guideModule:
        guideClass = getattr(self.guide, self.guide.CLASS_NAME)
        # initialize this guideModule as an guide Instance:
        guideInstance = guideClass(self, self.langDic, self.langName, userSpecName, rigType)
        self.moduleInstancesList.append(guideInstance)
        # edit the footer A text:
        self.allGuidesList.append([guideModule, userSpecName])
        self.modulesToBeRiggedList = utils.getModulesToBeRigged(self.moduleInstancesList)
        cmds.text(self.allUIs["footerAText"], edit=True, label=str(len(self.modulesToBeRiggedList)) +" "+ self.langDic[self.langName]['i005_footerA'])

        return guideInstance
    
    
    def initExtraModule(self, guideModule, guideDir, *args):
        """ Create a guideModuleReference (instance) of a further guideModule that will be rigged (installed).
            Returns the guide instance initialised.
        """
        # especific import command for guides storing theses guides modules in a variable:
        basePath = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        self.guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(self.guide)
        # get the CLASS_NAME from extraModule:
        guideClass = getattr(self.guide, self.guide.CLASS_NAME)
        # initialize this extraModule as an Instance:
        dpUIinst = self
        guideInstance = guideClass(dpUIinst, self.langDic, self.langName)
        return guideInstance
        
        
    def execScriptedGuide(self, guideModule, guideDir, *args):
        """ Create a instance of a scripted guide that will create several guideModules in order to integrate them.
        """
        # import this scripted module:
        basePath = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(guide)
        # get the CLASS_NAME from guideModule:
        startScriptFunction = getattr(guide, guide.CLASS_NAME)
        # execute this scriptedGuideModule:
        startScriptFunction(self)
    
    
    def populateCreatedGuideModules(self, *args):
        """ Read all guide modules loaded in the scene and re-create the elements in the moduleLayout.
        """
        # create a new list in order to store all created guide modules in the scene and its userSpecNames:
        self.allGuidesList = []
        self.moduleInstancesList = []
        # list all namespaces:
        cmds.namespace(setNamespace=":")
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        # find path where 'dpAutoRig.py' is been executed:
        path = utils.findPath("dpAutoRig.py")
        guideDir = MODULES
        # find all module names:
        moduleNameInfo = utils.findAllModuleNames(path, guideDir)
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
                    curGuideName = validModuleNames[index]+"__"+userSpecName+":"+GUIDE_BASE_NAME
                    if cmds.objExists(curGuideName):
                        self.allGuidesList.append([validModules[index], userSpecName, curGuideName])
                        
        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.allGuidesList:
            # clear current layout before reload modules:
            cmds.deleteUI(self.allUIs["modulesLayoutA"])
            self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=200, parent=self.allUIs["colMiddleRightA"])
            # load again the modules:
            guideFolder = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")+"."+MODULES
            # this list will be used to rig all modules pressing the RIG button:
            for module in self.allGuidesList:
                mod = __import__(guideFolder+"."+module[0], {}, {}, [module[0]])
                reload(mod)
                # identify the guide modules and add to the moduleInstancesList:
                moduleClass = getattr(mod, mod.CLASS_NAME)
                dpUIinst = self
                if cmds.attributeQuery("rigType", node=module[2], ex=True):
                    curRigType = cmds.getAttr(module[2] + ".rigType")
                    moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, module[1], curRigType)
                else:
                    if cmds.attributeQuery("Style", node=module[2], ex=True):
                        iStyle = cmds.getAttr(module[2] + ".Style")
                        if (iStyle == 0 or iStyle == 1):
                            moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, module[1], Base.RigType.biped)
                        else:
                            moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, module[1], Base.RigType.quadruped)
                    else:
                        moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, module[1], Base.RigType.default)
                self.moduleInstancesList.append(moduleInst)
        # edit the footer A text:
        self.modulesToBeRiggedList = utils.getModulesToBeRigged(self.moduleInstancesList)
        cmds.text(self.allUIs["footerAText"], edit=True, label=str(len(self.modulesToBeRiggedList)) +" "+ self.langDic[self.langName]['i005_footerA'])
    
    
    def setPrefix(self, *args):
        """ Get the text entered in the textField and change it to normal.
        """
        # get the entered text:
        enteredText = cmds.textField(self.allUIs["prefixTextField"], query=True, text=True)
        # call utils to return the normalized text:
        prefixName = utils.normalizeText(enteredText, prefixMax=10)

        # edit the prefixTextField with the prefixName:
        if len(prefixName) != 0:
            cmds.textField(self.allUIs["prefixTextField"], edit=True, text=prefixName+"_")


    def info(self, title, description, text, align, width, height, *args):
        """ Create a window showing the text info with the description about any module.
        """
        # declaring variables:
        self.info_title       = title
        self.info_description = description
        self.info_text        = text
        self.info_winWidth    = width
        self.info_winHeight   = height
        self.info_align       = align
        # creating Info Window:
        if cmds.window('dpInfoWindow', query=True, exists=True):
            cmds.deleteUI('dpInfoWindow', window=True)
        dpInfoWin = cmds.window('dpInfoWindow', title='dpAutoRig - v'+DPAR_VERSION+' - '+self.langDic[self.langName]['i013_info']+' - '+self.langDic[self.langName][self.info_title], iconName='dpInfo', widthHeight=(self.info_winWidth, self.info_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        infoLayout = cmds.scrollLayout('dpInfoWindow')
        if self.info_description:
            infoDesc = cmds.text(self.langDic[self.langName][self.info_description], align=self.info_align, parent=infoLayout)
        if self.info_text:
            infoText = cmds.text(self.info_text, align=self.info_align, parent=infoLayout)
        # call Info Window:
        cmds.showWindow(dpInfoWin)
    
    
    def help(self, *args):
        """ Start browser with the help instructions and tutorials about dpAutoRig v2.
        """
        os.popen('start http://nilouco.blogspot.com')
    
    
    def logWin(self, *args):
        """ Just create a window with all information log and print the principal result.
        """
        # create the logText:
        logText = self.langDic[self.langName]['i014_logStart'] + '\n'
        logText += str( time.asctime( time.localtime(time.time()) ) ) + '\n\n'
        # get the number of riggedModules:
        nRiggedModule = len(self.riggedModuleDic)
        # pass for rigged module to add informations in logText:
        if nRiggedModule > 0:
            if nRiggedModule == 1:
                logText += str(nRiggedModule).zfill(3) + ' ' + self.langDic[self.langName]['i015_success'] + ':\n\n'
                print('\ndpAutoRigSystem Log: ' + str(nRiggedModule).zfill(3) + ' ' + self.langDic[self.langName]['i015_success'] + ', thanks!\n'),
            else:
                logText += str(nRiggedModule).zfill(3) + ' ' + self.langDic[self.langName]['i016_success'] + ':\n\n'
                print('\ndpAutoRigSystem Log: ' + str(nRiggedModule).zfill(3) + ' ' + self.langDic[self.langName]['i016_success'] + ', thanks!\n'),
            riggedGuideModuleList = []
            for riggedGuideModule in self.riggedModuleDic:
                riggedGuideModuleList.append(riggedGuideModule)
            riggedGuideModuleList.sort()
            for riggedGuideModule in riggedGuideModuleList:
                moduleCustomName= self.riggedModuleDic[riggedGuideModule]
                if moduleCustomName == None:
                    logText += riggedGuideModule + '\n'
                else:
                    logText += riggedGuideModule + " as " + moduleCustomName + '\n'
        else:
            logText += self.langDic[self.langName]['i017_nothing'] + '\n'
        logText += '\n' + self.langDic[self.langName]['i018_thanks']
        
        # creating a info window to show the log:
        self.info( 'i019_log', None, logText, 'center', 250, (150+(nRiggedModule*13)) )
        
    
    ###################### End: UI
    
    
    ###################### Start: Rigging Modules Instances

    '''
    Pymel
    Generic function to create base group
    '''
    def getBaseGrp(self, sAttrName, sGrpName):
        nGrpNode = None
        try:
            nGrpNode = self.masterGrp.getAttr(sAttrName)
        except pymel.MayaAttributeError:
            try:
                nGrpNode = pymel.PyNode(sGrpName)
            except pymel.MayaNodeError:
                nGrpNode = pymel.createNode("transform", name=sGrpName)
            finally:
                #Since there is no connection between the master and the node found, create the connection
                self.masterGrp.addAttr(sAttrName, attributeType='message')
                nGrpNode.message.connect(self.masterGrp.attr(sAttrName))

        return nGrpNode

    '''
    Pymel
    Generic function to create base controller
    '''
    def getBaseCtrl(self, sAttrName, sCtrlName, fRadius, iDegree = 1, iSection = 8):
        nCtrl = None
        self.ctrlCreated = False
        try:
            nCtrl= self.masterGrp.getAttr(sAttrName)
        except pymel.MayaAttributeError:
            try:
                nCtrl = pymel.PyNode(self.prefix + sCtrlName)
            except pymel.MayaNodeError:
                if (sCtrlName != (self.prefix + "Option_Ctrl")):
                    nCtrl = pymel.circle(n=sCtrlName, nr=(0, 1, 0), d=iDegree, s=iSection, r=fRadius, ch=False)[0]
                else:
                    nCtrl = pymel.PyNode(ctrls.cvCharacter(sCtrlName, r=0.2))
                self.ctrlCreated = True
            finally:
                #Since there is no connection between the master and the node found, create the connection
                self.masterGrp.addAttr(sAttrName, attributeType='message')
                nCtrl.message.connect(self.masterGrp.attr(sAttrName))

        return nCtrl

    '''
    Pymel
    ensure that the main group and Ctrl of the rig exist in the scene or else create them
    '''
    def createBaseRigNode(self):
        sAllGrp = "All_Grp"
        # create master hierarchy:
        allTransformList = pymel.ls(self.prefix + "*", selection=False, type="transform")
        #Get all the masterGrp obj and ensure it not referenced
        self.masterGrp = [n for n in allTransformList if n.hasAttr("masterGrp") and not pymel.referenceQuery(n, isNodeReferenced=True)]
        localTime = str( time.asctime( time.localtime(time.time()) ) )
        if self.masterGrp:
            # Take the first one in the list, in almost all case, it will be fine.
            # If not, the user need to clean it's scene for the moment
            self.masterGrp = self.masterGrp[0]
        else:
            #Create Master Grp
            self.masterGrp = pymel.createNode("transform", name=self.prefix+sAllGrp)
            self.masterGrp.addAttr("masterGrp", at="bool")
            self.masterGrp.setDynamicAttr('masterGrp', True)
            self.masterGrp.setDynamicAttr("date", localTime)

        # add data log:
        # system:
        self.masterGrp.setDynamicAttr("system", "dpAutoRig_"+DPAR_VERSION)
        # date:
        self.masterGrp.setDynamicAttr("lastModification", localTime)
        # author:
        self.masterGrp.setDynamicAttr("author", getpass.getuser())
        # module counts:
        for guideType in self.guideModuleList:
            self.masterGrp.setDynamicAttr(guideType+"Count", 0)

        #Get or create all the needed group
        self.modelsGrp      = self.getBaseGrp("modelsGrp", self.prefix+"Model_Grp")
        self.ctrlsGrp       = self.getBaseGrp("ctrlsGrp", self.prefix+"Ctrls_Grp")
        self.ctrlsVisGrp    = self.getBaseGrp("ctrlsVisibilityGrp", self.prefix+"Ctrls_Visibility_Grp")
        self.dataGrp        = self.getBaseGrp("dataGrp", self.prefix+"Data_Grp")
        self.renderGrp      = self.getBaseGrp("renderGrp", self.prefix+"Render_Grp")
        self.proxyGrp       = self.getBaseGrp("proxyGrp", self.prefix+"Proxy_Grp")
        self.fxGrp          = self.getBaseGrp("fxGrp", self.prefix+"FX_Grp")
        self.staticGrp      = self.getBaseGrp("staticGrp", self.prefix+"Static_Grp")
        self.scalableGrp    = self.getBaseGrp("scalableGrp", self.prefix+"Scalable_Grp")

        #Arrange Hierarchy
        pymel.parent(self.modelsGrp, self.ctrlsGrp, self.dataGrp, self.renderGrp, self.proxyGrp, self.fxGrp, self.masterGrp)
        pymel.parent(self.staticGrp, self.scalableGrp, self.dataGrp)
        pymel.select(None)

        #Hide Models and FX groups
        pymel.setAttr(self.modelsGrp.visibility, 0)
        pymel.setAttr(self.fxGrp.visibility, 0)

        #Function not in pymel for the moment
        aToLock = [self.masterGrp.__melobject__(),
                   self.modelsGrp.__melobject__(),
                   self.ctrlsGrp.__melobject__(),
                   self.renderGrp.__melobject__(),
                   self.dataGrp.__melobject__(),
                   self.proxyGrp.__melobject__(),
                   self.fxGrp.__melobject__(),
                   self.staticGrp.__melobject__(),
                   self.ctrlsVisGrp.__melobject__()]
        ctrls.setLockHide(aToLock, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        #Control Setup
        fMasterRadius = ctrls.dpCheckLinearUnit(10)
        self.masterCtrl = self.getBaseCtrl("masterCtrl", self.prefix+"Master_Ctrl", fMasterRadius, iDegree=3)
        if (self.ctrlCreated):
            self.masterCtrl.setDynamicAttr("masterCtrl", True)
            self.masterCtrl.setDynamicAttr("geometryList", "")
            self.masterCtrl.setDynamicAttr("controlList", "")
            self.masterCtrl.rotateOrder.set(3)

        self.globalCtrl = self.getBaseCtrl("globalCtrl", self.prefix+"Global_Ctrl", ctrls.dpCheckLinearUnit(16), iSection=4)
        if (self.ctrlCreated):
            self.globalCtrl.rotateY.set(45)
            pymel.makeIdentity(self.globalCtrl, a=True)
            self.globalCtrl.rotateOrder.set(3)

        self.rootCtrl   = self.getBaseCtrl("rootCtrl", self.prefix+"Root_Ctrl", ctrls.dpCheckLinearUnit(8))
        if (self.ctrlCreated):
            self.rootCtrl.rotateOrder.set(3)

        self.optionCtrl = self.getBaseCtrl("optionCtrl", self.prefix+"Option_Ctrl", ctrls.dpCheckLinearUnit(16))
        if (self.ctrlCreated):
            pymel.makeIdentity(self.optionCtrl, apply=True)
            self.optionCtrlGrp = pymel.PyNode(utils.zeroOut([self.optionCtrl.__melobject__()])[0])
            self.optionCtrlGrp.translateX.set(fMasterRadius)
            # use Option_Ctrl rigScale and rigScaleMultiplier attribute to Master_Ctrl
            self.rigScaleMD = pymel.createNode("multiplyDivide", name=self.prefix+'RigScale_MD')
            pymel.connectAttr(self.optionCtrl.rigScale, self.rigScaleMD.input1X, force=True)
            pymel.connectAttr(self.optionCtrl.rigScaleMultiplier, self.rigScaleMD.input2X, force=True)
            pymel.connectAttr(self.rigScaleMD.outputX, self.masterCtrl.scaleX, force=True)
            pymel.connectAttr(self.rigScaleMD.outputX, self.masterCtrl.scaleY, force=True)
            pymel.connectAttr(self.rigScaleMD.outputX, self.masterCtrl.scaleZ, force=True)
            ctrls.setLockHide([self.masterCtrl.__melobject__()], ['sx', 'sy', 'sz'])
        else:
            self.optionCtrlGrp = self.optionCtrl.getParent()

        pymel.parent(self.rootCtrl, self.masterCtrl)
        pymel.parent(self.masterCtrl, self.globalCtrl)
        pymel.parent(self.globalCtrl, self.ctrlsGrp)
        pymel.parent(self.optionCtrlGrp, self.rootCtrl)
        pymel.parent(self.ctrlsVisGrp, self.rootCtrl)

        '''
        Not needed in maya 2016. Scale Constraint seem to react differently with the scale compensate
        Release node MAYA-45759 http://download.autodesk.com/us/support/files/maya_2016/Maya%202016%20Release%20Notes_enu.htm
        '''
        if (int(cmds.about(version=True)[:4]) < 2016):
            pymel.scaleConstraint(self.masterCtrl, self.scalableGrp, name=self.scalableGrp.name()+"_ScaleConstraint")
        # set lock and hide attributes (cmds function):
        ctrls.setLockHide([self.scalableGrp.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])
        ctrls.setLockHide([self.rootCtrl.__melobject__(), self.globalCtrl.__melobject__()], ['sx', 'sy', 'sz', 'v'])

        self.masterCtrl.visibility.setKeyable(False)
        pymel.select(None)

        #Base joint
        try:
            self.baseRootJnt = pymel.PyNode(self.prefix+"BaseRoot_Jnt")
            self.baseRootJntGrp = pymel.PyNode(self.prefix+"BaseRoot_Joint_Grp")
        except pymel.MayaNodeError:
            self.baseRootJnt = pymel.createNode("joint", name=self.prefix+"BaseRoot_Jnt")
            self.baseRootJntGrp = pymel.createNode("transform", name=self.prefix+"BaseRoot_Joint_Grp")
            pymel.parent(self.baseRootJnt, self.baseRootJntGrp)
            pymel.parent(self.baseRootJntGrp, self.scalableGrp)
            pymel.parentConstraint(self.rootCtrl, self.baseRootJntGrp, maintainOffset=True, name=self.baseRootJntGrp+"_ParentConstraint")
            pymel.scaleConstraint(self.rootCtrl, self.baseRootJntGrp, maintainOffset=True, name=self.baseRootJntGrp+"_ScaleConstraint")
            self.baseRootJntGrp.visibility.set(False)
            ctrls.setLockHide([self.baseRootJnt.__melobject__(), self.baseRootJntGrp.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

        #Ensure object returned are cmds supported
        self.masterGrp = self.masterGrp.__melobject__()
        self.modelsGrp = self.modelsGrp.__melobject__()
        self.ctrlsGrp = self.ctrlsGrp.__melobject__()
        self.ctrlsVisGrp = self.ctrlsVisGrp.__melobject__()
        self.dataGrp = self.dataGrp.__melobject__()
        self.renderGrp = self.renderGrp.__melobject__()
        self.proxyGrp = self.proxyGrp.__melobject__()
        self.fxGrp = self.fxGrp.__melobject__()
        self.staticGrp = self.staticGrp.__melobject__()
        self.scalableGrp = self.scalableGrp.__melobject__()
        self.masterCtrl = self.masterCtrl.__melobject__()
        self.rootCtrl = self.rootCtrl.__melobject__()
        self.globalCtrl = self.globalCtrl.__melobject__()
        self.optionCtrl = self.optionCtrl.__melobject__()
        self.optionCtrlGrp = self.optionCtrlGrp.__melobject__()
        self.baseRootJnt = self.baseRootJnt.__melobject__()
        self.baseRootJntGrp = self.baseRootJntGrp.__melobject__()


    def rigAll(self, integrate=None, *args):
        """ Create the RIG based in the Guide Modules in the scene.
            Most important function to automatizate the proccess.
        """
        # get a list of modules to be rigged and re-declare the riggedModuleDic to store for log in the end:
        self.modulesToBeRiggedList = utils.getModulesToBeRigged(self.moduleInstancesList)
        self.riggedModuleDic = {}
        
        # declare a list to store all integrating information:
        self.integratedTaskDic = {}
        
        # verify if there are instances of modules (guides) to rig in the scene:
        if self.modulesToBeRiggedList:
            
            # clear all duplicated names in order to run without find same names if they exists:
            if cmds.objExists("dpAR_GuideMirror_Grp"):
                cmds.delete("dpAR_GuideMirror_Grp")
            
            # regenerate mirror information for all guides:
            for guideModule in self.modulesToBeRiggedList:
                guideModule.checkFatherMirror()
            
            # store hierarchy from guides:
            self.hookDic = utils.hook()
            
            # get prefix:
            self.prefix = cmds.textField("prefixTextField", query=True, text=True)
            if self.prefix != "" and self.prefix != " " and self.prefix != "_" and self.prefix != None:
                if self.prefix[len(self.prefix)-1] != "_":
                    self.prefix = self.prefix + "_"

            #Check if we need to colorize the ctrls
            #Check integrate option
            bColorize = False
            try:
                bColorize = cmds.checkBox(self.allUIs["colorizeCtrlCB"], query=True, value=True)
                integrate = cmds.checkBox(self.allUIs["integrateCB"], query=True, value=True)
                bAddAttr = cmds.checkBox(self.allUIs["addAttrCB"], query=True, value=True)
            except:
                pass

            if integrate == 1:
                self.createBaseRigNode()
            # run RIG function for each guideModule:
            for guideModule in self.modulesToBeRiggedList:
                # create the rig for this guideModule:
                guideModuleCustomName = cmds.getAttr(guideModule.moduleGrp+'.customName')
                guideModule.rigModule()
                # get rigged module name:
                self.riggedModuleDic[guideModule.moduleGrp.split(":")[0]] = guideModuleCustomName
                # get integrated information:
                if guideModule.integratedActionsDic:
                    self.integratedTaskDic[guideModule.moduleGrp] = guideModule.integratedActionsDic["module"]
            
            if integrate == 1:
                # get all parent info from rigged modules:
                self.originedFromDic = utils.getOriginedFromDic()
                
                # verify if is necessary organize the hierarchies for each module:
                for guideModule in self.modulesToBeRiggedList:                
                    # get guideModule info:
                    self.itemGuideModule         = self.hookDic[guideModule.moduleGrp]['guideModuleName']
                    self.itemGuideInstance       = self.hookDic[guideModule.moduleGrp]['guideInstance']
                    self.itemGuideCustomName     = self.hookDic[guideModule.moduleGrp]['guideCustomName']
                    self.itemGuideMirrorAxis     = self.hookDic[guideModule.moduleGrp]['guideMirrorAxis']
                    self.itemGuideMirrorNameList = self.hookDic[guideModule.moduleGrp]['guideMirrorName']
                    
                    # working with item guide mirror:
                    self.itemMirrorNameList = [""]
                    
                    # get itemGuideName:
                    if self.itemGuideMirrorAxis != "off":
                        self.itemMirrorNameList = self.itemGuideMirrorNameList
                    
                    for s, sideName in enumerate(self.itemMirrorNameList):
                        
                        if self.itemGuideCustomName:
                            self.itemGuideName = sideName + self.prefix + self.itemGuideCustomName
                        else:
                            self.itemGuideName = sideName + self.prefix + self.itemGuideInstance
                        
                        # get hook groups info:
                        self.itemRiggedGrp = self.itemGuideName + "_Grp"
                        self.staticHookGrp = self.itemRiggedGrp
                        self.ctrlHookGrp = ""
                        self.scalableHookGrp = ""
                        self.rootHookGrp = ""
                        riggedChildList = cmds.listRelatives(self.itemRiggedGrp, children=True, type='transform')
                        if riggedChildList:
                            for child in riggedChildList:
                                if cmds.objExists(child+".ctrlHook") and cmds.getAttr(child+".ctrlHook") == 1:
                                    self.ctrlHookGrp = child
                                elif cmds.objExists(child+".scalableHook") and cmds.getAttr(child+".scalableHook") == 1:
                                    self.scalableHookGrp = child
                                elif cmds.objExists(child+".staticHook") and cmds.getAttr(child+".staticHook") == 1:
                                    self.staticHookGrp = child
                                elif cmds.objExists(child+".rootHook") and cmds.getAttr(child+".rootHook") == 1:
                                    self.rootHookGrp = child
                        
                        # get guideModule hierarchy data:
                        self.fatherGuide  = self.hookDic[guideModule.moduleGrp]['fatherGuide']
                        self.parentNode   = self.hookDic[guideModule.moduleGrp]['parentNode']
                        
                        # get father info:
                        if self.fatherGuide:
                            self.fatherModule              = self.hookDic[guideModule.moduleGrp]['fatherModule']
                            self.fatherInstance            = self.hookDic[guideModule.moduleGrp]['fatherInstance']
                            self.fatherNode                = self.hookDic[guideModule.moduleGrp]['fatherNode']
                            self.fatherGuideLoc            = self.hookDic[guideModule.moduleGrp]['fatherGuideLoc']
                            self.fatherCustomName          = self.hookDic[guideModule.moduleGrp]['fatherCustomName']
                            self.fatherMirrorAxis          = self.hookDic[guideModule.moduleGrp]['fatherMirrorAxis']
                            self.fatherGuideMirrorNameList = self.hookDic[guideModule.moduleGrp]['fatherMirrorName']
                            
                            # working with father mirror:
                            self.fatherMirrorNameList = [""]
                            
                            # get fatherName:
                            if self.fatherMirrorAxis != "off":
                                self.fatherMirrorNameList = self.fatherGuideMirrorNameList
                            
                            for f, sideFatherName in enumerate(self.fatherMirrorNameList):
                                
                                if self.fatherCustomName:
                                    self.fatherName = sideFatherName + self.prefix + self.fatherCustomName
                                else:
                                    self.fatherName = sideFatherName + self.prefix + self.fatherInstance
                                
                                # get final rigged parent node from originedFromDic:
                                self.fatherRiggedParentNode = self.originedFromDic[self.fatherName+"_Guide_"+self.fatherGuideLoc]
                                if len(self.fatherMirrorNameList) > 1: # tell us 'the father has mirror'
                                    if s == f:
                                        # parent them to the correct side of the father's mirror:
                                        if self.ctrlHookGrp:
                                            cmds.parent(self.ctrlHookGrp, self.fatherRiggedParentNode)
                                            # make ctrlHookGrp inactive:
                                            cmds.setAttr(self.ctrlHookGrp+".ctrlHook", 0)

                                else:
                                    # parent them to the unique father:
                                    if self.ctrlHookGrp:
                                        cmds.parent(self.ctrlHookGrp, self.fatherRiggedParentNode)
                                        # make ctrlHookGrp inactive:
                                        cmds.setAttr(self.ctrlHookGrp+".ctrlHook", 0)
                        
                        elif self.parentNode:
                            # parent module control to just a node in the scene:
                            cmds.parent(self.ctrlHookGrp, self.parentNode)
                            # make ctrlHookGrp inactive:
                            cmds.setAttr(self.ctrlHookGrp+".ctrlHook", 0)
                        else:
                            # parent module control to default masterGrp:
                            cmds.parent(self.ctrlHookGrp, self.ctrlsVisGrp)
                            # make ctrlHookGrp inactive:
                            cmds.setAttr(self.ctrlHookGrp+".ctrlHook", 0)
                        
                        if self.rootHookGrp:
                            # parent module rootHook to rootCtrl:
                            cmds.parent(self.rootHookGrp, self.ctrlsVisGrp)
                            # make rootHookGrp inactive:
                            cmds.setAttr(self.rootHookGrp+".rootHook", 0)
                        
                        # put static and scalable groups in dataGrp:
                        if self.staticHookGrp:
                            cmds.parent(self.staticHookGrp, self.staticGrp)
                            # make staticHookGrp inative:
                            cmds.setAttr(self.staticHookGrp+".staticHook", 0)
                        if self.scalableHookGrp:
                            cmds.parent(self.scalableHookGrp, self.scalableGrp)
                            # make scalableHookGrp inative:
                            cmds.setAttr(self.scalableHookGrp+".scalableHook", 0)
                
                # prepare to show a dialog box if find a bug:
                self.detectedBug = False
                self.bugMessage = self.langDic[self.langName]['b000_BugGeneral']
                
                # integrating modules together:
                # working with specific cases:
                if self.integratedTaskDic:
                    defaultAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
                    for moduleDic in self.integratedTaskDic:
                        moduleType = moduleDic[:moduleDic.find("__")]
						
                        # footGuide parented in the extremGuide of the limbModule:
                        if moduleType == FOOT:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                            if fatherModule == LIMB and fatherGuideLoc == 'Extrem':
                                self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                                self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                                # working with item guide mirror:
                                self.itemMirrorNameList = [""]
                                # get itemGuideName:
                                if self.itemGuideMirrorAxis != "off":
                                    self.itemMirrorNameList = self.itemGuideMirrorNameList
                                for s, sideName in enumerate(self.itemMirrorNameList):
                                    # getting foot data:
                                    revFootCtrl       = self.integratedTaskDic[moduleDic]['revFootCtrlList'][s]
                                    revFootCtrlZero   = self.integratedTaskDic[moduleDic]['revFootCtrlZeroList'][s]
                                    revFootCtrlShape  = self.integratedTaskDic[moduleDic]['revFootCtrlShapeList'][s]
                                    toLimbIkHandleGrp = self.integratedTaskDic[moduleDic]['toLimbIkHandleGrpList'][s]
                                    parentConst       = self.integratedTaskDic[moduleDic]['parentConstList'][s]
                                    scaleConst        = self.integratedTaskDic[moduleDic]['scaleConstList'][s]
                                    footJnt           = self.integratedTaskDic[moduleDic]['footJntList'][s]
                                    ballRFList        = self.integratedTaskDic[moduleDic]['ballRFList'][s]
                                    middleFootCtrl    = self.integratedTaskDic[moduleDic]['middleFootCtrlList'][s]
                                    # getting limb data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    ikCtrl                = self.integratedTaskDic[fatherGuide]['ikCtrlList'][s]
                                    ikHandleGrp           = self.integratedTaskDic[fatherGuide]['ikHandleGrpList'][s]
                                    ikHandlePointConst    = self.integratedTaskDic[fatherGuide]['ikHandlePointConstList'][s]
                                    ikFkBlendGrpToRevFoot = self.integratedTaskDic[fatherGuide]['ikFkBlendGrpToRevFootList'][s]
                                    extremJnt             = self.integratedTaskDic[fatherGuide]['extremJntList'][s]
                                    parentConstToRFOffset = self.integratedTaskDic[fatherGuide]['parentConstToRFOffsetList'][s]
                                    ikStretchExtremLoc    = self.integratedTaskDic[fatherGuide]['ikStretchExtremLoc'][s]
                                    limbType              = self.integratedTaskDic[fatherGuide]['limbType']
                                    ikFkNetworkList       = self.integratedTaskDic[fatherGuide]['ikFkNetworkList']
                                    worldRefList          = self.integratedTaskDic[fatherGuide]['worldRefList'][s]
                                    # do task actions in order to integrate the limb and foot:
                                    cmds.delete(ikHandlePointConst, parentConst, scaleConst)
                                    cmds.parent(revFootCtrlZero, ikFkBlendGrpToRevFoot, absolute=True)
                                    cmds.parent(ikHandleGrp, toLimbIkHandleGrp, absolute=True)
                                    #Delete the old constraint (two line before) and recreate them on the extrem joint on the limb
                                    cmds.parentConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_ParentConstraint")[0]
                                    #cmds.scaleConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_ScaleConstraint")[0]
                                    if limbType == LEG:
                                        cmds.connectAttr(extremJnt+".scaleX", footJnt+".scaleX", force=True)
                                        cmds.connectAttr(extremJnt+".scaleY", footJnt+".scaleY", force=True)
                                        cmds.connectAttr(extremJnt+".scaleZ", footJnt+".scaleZ", force=True)
                                        cmds.parent(ikStretchExtremLoc, ballRFList, absolute=True)
                                        if cmds.objExists(extremJnt+".dpAR_joint"):
                                            cmds.deleteAttr(extremJnt+".dpAR_joint")
                                    if (int(cmds.about(version=True)[:4]) < 2016): #HACK negative scale --> Autodesk fixed this problem in Maya 2016 !
                                        # organize to avoid offset error in the parentConstraint with negative scale:
                                        if cmds.getAttr(parentConstToRFOffset+".mustCorrectOffset") == 1:
                                            for f in range(1,3):
                                                cmds.setAttr(parentConstToRFOffset+".target["+str(f)+"].targetOffsetRotateX", cmds.getAttr(parentConstToRFOffset+".fixOffsetX"))
                                                cmds.setAttr(parentConstToRFOffset+".target["+str(f)+"].targetOffsetRotateY", cmds.getAttr(parentConstToRFOffset+".fixOffsetY"))
                                                cmds.setAttr(parentConstToRFOffset+".target["+str(f)+"].targetOffsetRotateZ", cmds.getAttr(parentConstToRFOffset+".fixOffsetZ"))
                                    #Maya 2016 --> Scale constraint behavior
                                    # is fixed and a single master scale constraint doesn't work anymore
                                    if (int(cmds.about(version=True)[:4]) >= 2016):
                                        scalableGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                        cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScaleConstraint")


                                    # hide this control shape
                                    cmds.setAttr(revFootCtrlShape+".visibility", 0)
                                    # add float attributes and connect from ikCtrl to revFootCtrl:
                                    floatAttrList = cmds.listAttr(revFootCtrl, visible=True, scalar=True, keyable=True)
                                    for floatAttr in floatAttrList:
                                        if not floatAttr in defaultAttrList and not cmds.objExists(ikCtrl+'.'+floatAttr):
                                            cmds.addAttr(ikCtrl, longName=floatAttr, attributeType='float', keyable=True)
                                            cmds.connectAttr(ikCtrl+'.'+floatAttr, revFootCtrl+'.'+floatAttr, force=True)
                                    if ikFkNetworkList:
                                        lastIndex = len(cmds.listConnections(ikFkNetworkList[s]+".otherCtrls"))
                                        cmds.connectAttr(middleFootCtrl+'.message', ikFkNetworkList[s]+'.otherCtrls['+str(lastIndex+5)+']')
                                    cmds.rename(revFootCtrl, revFootCtrl+"_Old")
                        
                        # worldRef of extremGuide from limbModule controlled by optionCtrl:
                        if moduleType == LIMB:
                            # getting limb data:
                            worldRefList      = self.integratedTaskDic[moduleDic]['worldRefList']
                            worldRefShapeList = self.integratedTaskDic[moduleDic]['worldRefShapeList']
                            ikFkNetworkList   = self.integratedTaskDic[moduleDic]['ikFkNetworkList']
                            ikCtrlList        = self.integratedTaskDic[moduleDic]['ikCtrlList']
                            lvvAttr           = self.integratedTaskDic[moduleDic]['limbManualVolume']
                            for w, worldRef in enumerate(worldRefList):
                                # do actions in order to make limb be controlled by optionCtrl:
                                floatAttrList = cmds.listAttr(worldRef, visible=True, scalar=True, keyable=True)
                                for f, floatAttr in enumerate(floatAttrList):
                                    if f < len(floatAttrList):
                                        if not floatAttr in defaultAttrList:
                                            if not cmds.objExists(self.optionCtrl+'.'+floatAttr):
                                                currentValue = cmds.getAttr(worldRef+'.'+floatAttr)
                                                if floatAttr == lvvAttr:
                                                    cmds.addAttr(self.optionCtrl, longName=floatAttr, attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), defaultValue=currentValue, keyable=True)
                                                else:
                                                    cmds.addAttr(self.optionCtrl, longName=floatAttr, attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), minValue=0, maxValue=1, defaultValue=currentValue, keyable=True)
                                            cmds.connectAttr(self.optionCtrl+'.'+floatAttr, worldRef+'.'+floatAttr, force=True)
                                if not floatAttrList[len(floatAttrList)-1] in defaultAttrList and not cmds.objExists(self.optionCtrl+'.'+floatAttrList[len(floatAttrList)-1]):
                                    cmds.addAttr(self.optionCtrl, longName=floatAttrList[len(floatAttrList)-1], attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), defaultValue=1, keyable=True)
                                    cmds.connectAttr(self.optionCtrl+'.'+floatAttrList[len(floatAttrList)-1], worldRef+'.'+floatAttrList[len(floatAttrList)-1], force=True)
                                cmds.connectAttr(self.masterCtrl+".scaleX", worldRef+".scaleX", force=True)

                                # update ikFkNetwork:
                                if ikFkNetworkList:
                                    netIndex = 1
                                    optionCtrlAttrList = cmds.listAttr(self.optionCtrl, visible=True, scalar=True, keyable=True)
                                    for optAttr in optionCtrlAttrList:
                                        if "_IkFkBlend" in optAttr:
                                            cmds.connectAttr(self.optionCtrl+'.'+optAttr, ikFkNetworkList[w]+'.attState', force=True)
                                    limbAttrList = cmds.listAttr(ikCtrlList[w], visible=True, scalar=True, keyable=True)
                                    for limbAttr in limbAttrList:
                                        if not limbAttr in defaultAttrList and "_" in limbAttr:
                                            cmds.connectAttr(ikCtrlList[w]+'.'+limbAttr, ikFkNetworkList[w]+'.footRollAtts['+str(netIndex)+']', force=True)
                                            netIndex = netIndex + 1

                                cmds.setAttr(worldRefShapeList[w]+'.visibility', 0)
                                cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True)
                            
                            # parenting correctly the ikCtrlZero to spineModule:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']

                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList

                            for s, sideName in enumerate(self.itemMirrorNameList):
                                #Maya 2016 --> Scale constraint behavior
                                # is fixed and a single master scale constraint doesn't work anymore
                                if (int(cmds.about(version=True)[:4]) >= 2016):
                                    scalableGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                    cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScaleConstraint")

                                if fatherModule == SPINE:
                                    # getting limb data:
                                    limbType             = self.integratedTaskDic[moduleDic]['limbType']
                                    ikCtrlZero           = self.integratedTaskDic[moduleDic]['ikCtrlZeroList'][s]
                                    ikPoleVectorCtrlZero = self.integratedTaskDic[moduleDic]['ikPoleVectorZeroList'][s]
                                    limbStyle            = self.integratedTaskDic[moduleDic]['limbStyle']
                                    limbIsolateFkConst   = self.integratedTaskDic[moduleDic]['fkIsolateConst'][s]
                                    ikHandleGrp          = self.integratedTaskDic[moduleDic]['ikHandleGrpList'][s]
                                    
                                    # getting spine data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    hipsA  = self.integratedTaskDic[fatherGuide]['hipsAList'][0]
                                    chestA = self.integratedTaskDic[fatherGuide]['chestAList'][0]

                                    def setupFollowSpine(mainParent):
                                        #Ensure that the arm will follow the Chest_A Ctrl instead of the world
                                        targetList = cmds.parentConstraint(limbIsolateFkConst, q=True, tl=True)
                                        weightList = cmds.parentConstraint(limbIsolateFkConst, q=True, wal=True)
                                        #Need to sort the list to ensure that the resulat are in the same
                                        #order in Maya 2014 and Maya 2016...
                                        tempList = cmds.listConnections(limbIsolateFkConst + "." + weightList[1])
                                        tempList.sort()
                                        revNode = tempList[0]
                                        if not cmds.objectType(revNode) == 'reverse':
                                            for tmp in tempList:
                                                if cmds.objectType(tmp) == 'reverse':
                                                    revNode = tmp
                                        fkZeroNode = cmds.listConnections(limbIsolateFkConst + ".constraintRotateZ")[0]
                                        fkCtrl = fkZeroNode.replace("_Zero", "")
                                        nodeToConst = utils.zeroOut([fkCtrl])[0]
                                        nodeToConst = cmds.rename(nodeToConst, fkZeroNode + "_spaceSwitch")
                                        mainCtrl = cmds.listConnections(revNode + ".inputX")[0]
                                        mainNull = sideName + mainParent +"_null"  #Ensure the name is set to prevent unbound variable problem with inner function
                                        #Replace the old constraint with a new one that will switch with the chest ctrl
                                        cmds.delete(limbIsolateFkConst, icn=False, cn=True)
                                        #cmds.parentConstraint(targetList[1], limbIsolateFkConst, rm=True)
                                        if (not cmds.objExists(mainNull)):
                                            mainNull = cmds.group(empty=True, name=mainNull)
                                            cmds.parent(mainNull, mainParent, relative=False)
                                            m4Fk = cmds.xform(fkCtrl, ws=True, m=True, q=True)
                                            cmds.xform(mainNull, ws=True, m=m4Fk)
                                        newFkConst = cmds.parentConstraint(targetList[0], mainNull, nodeToConst, skipTranslate=["x", "y", "z"], maintainOffset=True)[0]
                                        cmds.connectAttr(mainCtrl + "." + self.langDic[self.langName]['c_Follow'], newFkConst + "." + targetList[0]+"W0", force=True)
                                        if (cmds.objExists(revNode)):
                                            cmds.connectAttr(revNode + ".outputX", newFkConst + "." + mainNull+"W1", force=True)
                                        else:
                                            revNode = cmds.createNode('reverse', name=sideName+fkCtrl+"_FkIsolate_Rev")
                                            cmds.connectAttr(mainCtrl+'.'+self.langDic[self.langName]['c_Follow'], revNode+".inputX", force=True)
                                            cmds.connectAttr(revNode + ".outputX", newFkConst + "." + mainNull+"W1", force=True)

                                    # verifying what part will be used, the hips or chest:
                                    if limbType == self.langDic[self.langName]['m030_leg']:
                                        # do task actions in order to integrate the limb of leg type to rootCtrl:
                                        cmds.parent(ikCtrlZero, self.ctrlsVisGrp, absolute=True)
                                        cmds.parent(ikPoleVectorCtrlZero, self.ctrlsVisGrp, absolute=True)
                                        #Ensure that the arm will follow the Chest_A Ctrl instead of the world
                                        setupFollowSpine(hipsA)

                                    elif fatherGuideLoc == "JointLoc1":
                                        # do task actions in order to integrate the limb and spine (ikCtrl):
                                        cmds.parent(ikCtrlZero, self.ctrlsVisGrp, absolute=True)
                                        #Ensure that the arm will follow the Chest_A Ctrl instead of the world
                                        setupFollowSpine(hipsA)

                                    else:
                                        # do task actions in order to integrate the limb and spine (ikCtrl):
                                        cmds.parent(ikCtrlZero, self.ctrlsVisGrp, absolute=True)
                                        cmds.parentConstraint(chestA, ikHandleGrp, mo=1)
                                        #Ensure that the arm will follow the Chest_A Ctrl instead of the world
                                        setupFollowSpine(chestA)

                                    # verify if is quadruped
                                    if limbStyle == self.langDic[self.langName]['m037_quadruped'] or limbStyle == self.langDic[self.langName]['m043_quadSpring']:
                                        if fatherGuideLoc != "JointLoc1":
                                            # get extra info from limb module data:
                                            quadFrontLeg = self.integratedTaskDic[moduleDic]['quadFrontLegList'][s]
                                            ikCtrl       = self.integratedTaskDic[moduleDic]['ikCtrlList'][s]
                                            # if quadruped, create a parent contraint from chestA to front leg:
                                            quadChestParentConst = cmds.parentConstraint(self.rootCtrl, chestA, quadFrontLeg, maintainOffset=True, name=quadFrontLeg+"_ParentConstraint")[0]
                                            revNode = cmds.createNode('reverse', name=quadFrontLeg+"_Rev")
                                            cmds.addAttr(ikCtrl, longName="followChestA", attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                                            cmds.connectAttr(ikCtrl+".followChestA", quadChestParentConst+"."+chestA+"W1", force=True)
                                            cmds.connectAttr(ikCtrl+".followChestA", revNode+".inputX", force=True)
                                            cmds.connectAttr(revNode+".outputX", quadChestParentConst+"."+self.rootCtrl+"W0", force=True)
                            
                            # fixing ikSpringSolver parenting for quadrupeds:
                            # getting limb data:
                            fixIkSpringSolverGrp = self.integratedTaskDic[moduleDic]['fixIkSpringSolverGrpList']
                            if fixIkSpringSolverGrp:
                                cmds.parent(fixIkSpringSolverGrp, self.scalableGrp, absolute=True)
                                if (int(cmds.about(version=True)[:4]) >= 2016):
                                    for nFix in fixIkSpringSolverGrp:
                                        cmds.scaleConstraint(self.masterCtrl, nFix, name=nFix+"_ScaleConstraint")
                            
                        # integrate the volumeVariation attribute from Spine module to optionCtrl:
                        if moduleType == SPINE:
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                # connect the optionCtrl vvAttr to hipsA vvAttr and hide it for each side of the mirror (if it exists):
                                hipsA  = self.integratedTaskDic[moduleDic]['hipsAList'][s]
                                vvAttr = self.integratedTaskDic[moduleDic]['volumeVariationAttrList'][s]
                                actVVAttr = self.integratedTaskDic[moduleDic]['ActiveVolumeVariationAttrList'][s]
                                mScaleVVAttr = self.integratedTaskDic[moduleDic]['MasterScaleVolumeVariationAttrList'][s]
                                #Maya 2016 --> Scale constraint behavior
                                # is fixed and a single master scale constraint doesn't work anymore
                                if (int(cmds.about(version=True)[:4]) >= 2016):
                                    clusterGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                    cmds.scaleConstraint(self.masterCtrl, clusterGrp, name=clusterGrp+"_ScaleConstraint")
                                cmds.addAttr(self.optionCtrl, longName=vvAttr, attributeType="float", defaultValue=1, keyable=True)
                                cmds.connectAttr(self.optionCtrl+'.'+vvAttr, hipsA+'.'+vvAttr)
                                cmds.setAttr(hipsA+'.'+vvAttr, keyable=False)
                                cmds.addAttr(self.optionCtrl, longName=actVVAttr, attributeType="bool", defaultValue=True, keyable=True)
                                cmds.connectAttr(self.optionCtrl+'.'+actVVAttr, hipsA+'.'+actVVAttr)
                                cmds.setAttr(hipsA+'.'+actVVAttr, keyable=False)
                                cmds.connectAttr(self.masterCtrl+'.scaleX', hipsA+'.'+mScaleVVAttr)
                                cmds.setAttr(hipsA+'.'+mScaleVVAttr, keyable=False)
                                if bColorize:
                                    ctrls.colorShape(self.integratedTaskDic[moduleDic]['FkCtrls'][s], "cyan")
                                    ctrls.colorShape(self.integratedTaskDic[moduleDic]['IkCtrls'][s], "yellow")
                        
                        # integrate the head orient from the masterCtrl:
                        if moduleType == HEAD:
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                # connect the masterCtrl to head group using a orientConstraint:
                                worldRef = self.integratedTaskDic[moduleDic]['worldRefList'][s]
                                cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_ParentConstraint")
                                if bColorize:
                                    ctrls.colorShape(self.integratedTaskDic[moduleDic]['ctrls'][s], "yellow")
                                    ctrls.colorShape(self.integratedTaskDic[moduleDic]['lCtrls'][s], "red")
                                    ctrls.colorShape(self.integratedTaskDic[moduleDic]['rCtrls'][s], "blue")
                        
                        # integrate the Eye with the Head setup:
                        if moduleType == EYE:
                            eyeCtrl = self.integratedTaskDic[moduleDic]['eyeCtrl']
                            eyeGrp = self.integratedTaskDic[moduleDic]['eyeGrp']
                            upLocGrp = self.integratedTaskDic[moduleDic]['upLocGrp']
                            cmds.parent(eyeGrp, self.ctrlsVisGrp, relative=False)
                            # get father module:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                            if fatherModule == HEAD:
                                # getting head data:
                                fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                headCtrl  = self.integratedTaskDic[fatherGuide]['headCtrlList'][0]
                                headParentConst = cmds.parentConstraint(self.rootCtrl, headCtrl, eyeGrp, maintainOffset=True, name=eyeGrp+"_ParentConstraint")[0]
                                eyeRevNode = cmds.createNode('reverse', name=eyeGrp+"_Rev")
                                cmds.connectAttr(eyeCtrl+'.'+self.langDic[self.langName]['c_Follow'], eyeRevNode+".inputX", force=True)
                                cmds.connectAttr(eyeRevNode+".outputX", headParentConst+"."+self.rootCtrl+"W0", force=True)
                                cmds.connectAttr(eyeCtrl+'.'+self.langDic[self.langName]['c_Follow'], headParentConst+"."+headCtrl+"W1", force=True)
                                cmds.parent(upLocGrp, headCtrl, relative=False)
                                cmds.setAttr(upLocGrp+".visibility", 0)
                                # head drives eyeScaleGrp:
                                self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                                self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                                # working with item guide mirror:
                                self.itemMirrorNameList = [""]
                                # get itemGuideName:
                                if self.itemGuideMirrorAxis != "off":
                                    self.itemMirrorNameList = self.itemGuideMirrorNameList
                                for s, sideName in enumerate(self.itemMirrorNameList):
                                    eyeScaleGrp = self.integratedTaskDic[moduleDic]['eyeScaleGrp'][s]
                                    cmds.parentConstraint(headCtrl, eyeScaleGrp, maintainOffset=True)
                            # changing iris and pupil color override:
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                if self.integratedTaskDic[moduleDic]['hasIris']:
                                    irisCtrl = self.integratedTaskDic[moduleDic]['irisCtrl'][s]
                                    ctrls.colorShape([irisCtrl], "cyan")
                                if self.integratedTaskDic[moduleDic]['hasPupil']:
                                    pupilCtrl = self.integratedTaskDic[moduleDic]['pupilCtrl'][s]
                                    ctrls.colorShape([pupilCtrl], "black")
                        
                        # integrate the Finger module:
                        if moduleType == FINGER:
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                ikCtrlZero = self.integratedTaskDic[moduleDic]['ikCtrlZeroList'][s]
                                scalableGrp = self.integratedTaskDic[moduleDic]['scalableGrpList'][s]

                                '''
                                Not needed in maya 2016. Scale Constraint seem to react differently with the scale compensate
                                Release node MAYA-45759 http://download.autodesk.com/us/support/files/maya_2016/Maya%202016%20Release%20Notes_enu.htm
                                '''
                                if (int(cmds.about(version=True)[:4]) >= 2016):
                                    cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScaleConstraint")

                                # correct ikCtrl parent to root ctrl:
                                cmds.parent(ikCtrlZero, self.ctrlsVisGrp, relative=True)
                                # get father guide data:
                                fatherModule   = self.hookDic[moduleDic]['fatherModule']
                                fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                                if fatherModule == LIMB and fatherGuideLoc == 'Extrem':
                                    # getting limb type:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    limbType = self.integratedTaskDic[fatherGuide]['limbType']
                                    if limbType == ARM:
                                        origFromList = self.integratedTaskDic[fatherGuide]['integrateOrigFromList'][s]
                                        origFrom = origFromList[-1]
                                        cmds.parentConstraint(origFrom, scalableGrp, maintainOffset=True)
                
                        # integrate the Single module with another Single as a father:
                        if moduleType == SINGLE:
                            # connect Option_Ctrl display attribute to the visibility:
                            if not cmds.objExists(self.optionCtrl+".display"+self.langDic[self.langName]['m081_tweaks']):
                                cmds.addAttr(self.optionCtrl, longName="display"+self.langDic[self.langName]['m081_tweaks'], min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                                cmds.setAttr(self.optionCtrl+".display"+self.langDic[self.langName]['m081_tweaks'], channelBox=True)
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                ctrlGrp = self.integratedTaskDic[moduleDic]["ctrlGrpList"][s]
                                cmds.connectAttr(self.optionCtrl+".display"+self.langDic[self.langName]['m081_tweaks'], ctrlGrp+".visibility", force=True)
                            # get father module:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            if fatherModule == SINGLE:
                                for s, sideName in enumerate(self.itemMirrorNameList):
                                    # getting child Single Static_Grp:
                                    staticGrp = self.integratedTaskDic[moduleDic]["staticGrpList"][s]
                                    # getting father Single mainJis (indirect skinning joint) data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    try:
                                        mainJis = self.integratedTaskDic[fatherGuide]['mainJisList'][s]
                                    except:
                                        mainJis = self.integratedTaskDic[fatherGuide]['mainJisList'][0]
                                    # father's mainJis drives child's staticGrp:
                                    cmds.parentConstraint(mainJis, staticGrp, maintainOffset=True)
                                    cmds.scaleConstraint(mainJis, staticGrp, maintainOffset=True)
                            # check Single mirror indirectSkin bug in Maya2018:
                            if not self.detectedBug:
                                self.detectedBug = self.integratedTaskDic[moduleDic]["detectedBug"]
                                self.bugMessage = self.langDic[self.langName]['b001_BugSingleIndirectSkinMaya2018']
                
                
                # atualise the number of rigged guides by type
                for guideType in self.guideModuleList:
                    typeCounter = 0
                    newTranformList = cmds.ls(selection=False, type="transform")
                    for transf in newTranformList:
                        if cmds.objExists(transf+'.dpAR_type'):
                            dpARType = ( 'dp'+(cmds.getAttr(transf+'.dpAR_type')) )
                            if ( dpARType == guideType ):
                                typeCounter = typeCounter + 1
                    if ( typeCounter > cmds.getAttr(self.masterGrp+'.'+guideType+'Count') ):
                        cmds.setAttr(self.masterGrp+'.'+guideType+'Count', typeCounter)
        
            #Actualise all controls (Master_Ctrl.controlList) for this rig:
            rigInfo.UpdateRigInfo.updateRigInfoLists()

            #Colorize all controller in yellow as a base (Pymel)
            if (bColorize):
                aBCtrl = [pymel.PyNode(self.globalCtrl), pymel.PyNode(self.rootCtrl), pymel.PyNode(self.optionCtrl)]
                aAllCtrls = pymel.ls("*_Ctrl")
                lPattern = re.compile(self.langDic[self.langName]['p002_left'] + '_.*._Ctrl')
                rPattern = re.compile(self.langDic[self.langName]['p003_right'] + '_.*._Ctrl')
                for pCtrl in aAllCtrls:
                    if not pCtrl.getShape().overrideEnabled.get():
                        if (lPattern.match(pCtrl.name())):
                            ctrls.colorShape([pCtrl.__melobject__()], "red")
                        elif (rPattern.match(pCtrl.name())):
                            ctrls.colorShape([pCtrl.__melobject__()], "blue")
                        elif (pCtrl in aBCtrl):
                            ctrls.colorShape([pCtrl.__melobject__()], "black")
                        else:
                            ctrls.colorShape([pCtrl.__melobject__()], "yellow")

            #Add usefull attributes for the animators
            if (bAddAttr):
                pOptCtrl = pymel.PyNode(self.optionCtrl)
                pRenderGrp = pymel.PyNode(self.renderGrp)
                pCtrlVisGrp = pymel.PyNode(self.ctrlsVisGrp)
                pProxyGrp = pymel.PyNode(self.proxyGrp)

                if not pymel.hasAttr(pOptCtrl, "display"):
                    pymel.addAttr(pOptCtrl, ln="display", at="enum", enumName="----------", keyable=True)

                if not pymel.hasAttr(pOptCtrl, "displayMesh"):
                    pymel.addAttr(pOptCtrl, ln="displayMesh", min=0, max=1, defaultValue=1, attributeType="long", keyable=True)
                    pymel.connectAttr(pOptCtrl.displayMesh, pRenderGrp.visibility, force=True)

                if not pymel.hasAttr(pOptCtrl, "displayProxy"):
                    pymel.addAttr(pOptCtrl, ln="displayProxy", min=0, max=1, defaultValue=0, attributeType="long", keyable=True)
                    pymel.connectAttr(pOptCtrl.displayProxy, pProxyGrp.visibility, force=True)

                if not pymel.hasAttr(pOptCtrl, "displayCtrl"):
                    pymel.addAttr(pOptCtrl, ln="displayCtrl", min=0, max=1, defaultValue=1, attributeType="long", keyable=True)
                    pymel.connectAttr(pOptCtrl.displayCtrl, pCtrlVisGrp.visibility, force=True)

                if not pymel.hasAttr(pOptCtrl, "General"):
                    pymel.addAttr(pOptCtrl, ln="General", at="enum", enumName="----------", keyable=True)

                #Only create if a IkFk attribute is found
                if not pymel.hasAttr(pOptCtrl, "ikFkBlend"):
                    if (pOptCtrl.listAttr(string="*IkFk*")):
                        pymel.addAttr(pOptCtrl, ln="ikFkBlend", at="enum", enumName="----------", keyable=True)
                        
            #Try add hand follow (space switch attribute) on bipeds:
            self.initExtraModule("dpAddHandFollow", EXTRAS)
            
            # show dialogBox if detected a bug:
            if self.detectedBug:
                print "\n\n"
                print self.bugMessage
                cmds.confirmDialog(title=self.langDic[self.langName]['i078_detectedBug'], message=self.bugMessage, button=['OK'])

        # re-declaring guideMirror and previewMirror groups:
        self.guideMirrorGrp = 'dpAR_GuideMirror_Grp'
        if cmds.objExists(self.guideMirrorGrp):
            cmds.delete(self.guideMirrorGrp)
        
        # reload the jointSkinList:
        self.populateJoints()
        
        # select the MasterCtrl:
        try:
            cmds.select(self.masterCtrl)
        except:
            pass
        
        # call log window:
        self.logWin()
        
    
    ###################### End: Rigging Modules Instances.
    
    
    ###################### Start: Skinning.
    
    def validateGeoList(self, geoList, *args):
        """ Check if the geometry list from UI is good to be skinned, because we can get issue if the display long name is not used.
        """
        if geoList:
            for i, item in enumerate(geoList):
                if item in geoList[:i]:
                    self.info('i038_canceled', 'e003_moreThanOneGeo', item, 'center', 205, 270)
                    return False
        return True
    
    def skinFromUI(self, *args):
        """ Skin the geometries using the joints, reading from UI the selected items of the textScrollLists or getting all items if nothing selected.
        """
        # get joints to be skinned:
        uiJointSkinList = cmds.textScrollList( self.allUIs["jntTextScrollLayout"], query=True, selectItem=True)
        if not uiJointSkinList:
            uiJointSkinList = cmds.textScrollList( self.allUIs["jntTextScrollLayout"], query=True, allItems=True)
        
        # check if all items in jointSkinList exists, then if not, show dialog box to skinWithoutNotExisting or Cancel
        jointSkinList, jointNotExistingList = [], []
        for item in uiJointSkinList:
            if cmds.objExists(item):
                jointSkinList.append(item)
            else:
                jointNotExistingList.append(item)
        if jointNotExistingList:
            notExistingJointMessage = self.langDic[self.langName]['i069_notSkinJoint'] +"\n\n"+ ", ".join(str(jntNotExitst) for jntNotExitst in jointNotExistingList) +"\n\n"+ self.langDic[self.langName]['i070_continueSkin']
            btYes = self.langDic[self.langName]['i071_yes']
            btNo = self.langDic[self.langName]['i072_no']
            confirmSkinning = cmds.confirmDialog(title='Confirm Skinning', message=notExistingJointMessage, button=[btYes,btNo], defaultButton=btYes, cancelButton=btNo, dismissString=btNo)
            if confirmSkinning == btNo:
                jointSkinList = None
        
        # get geometries to be skinned:
        geomSkinList = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, selectItem=True)
        if not geomSkinList:
            geomSkinList = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, allItems=True)
        
        # check if we have repeated listed geometries in case of the user choose to not display long names:
        if self.validateGeoList(geomSkinList):
            if jointSkinList and geomSkinList:
                for geomSkin in geomSkinList:
                    if (args[0] == "Add"):
                        cmds.skinCluster(geomSkin, edit=True, ai=jointSkinList, toSelectedBones=True, removeUnusedInfluence=False, lockWeights=True, wt=0.0)
                    elif (args[0] == "Remove"):
                        cmds.skinCluster(geomSkin, edit=True, ri=jointSkinList, toSelectedBones=True)
                    else:
                        baseName = geomSkin
                        meshSuffixList = ["_Mesh", "_mesh", "_Geo", "_geo", "_Tgt", "_tgt"]
                        for meshSuffix in meshSuffixList:
                            if meshSuffix in geomSkin:
                                baseName = geomSkin[:geomSkin.rfind(meshSuffix)]
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)
                print self.langDic[self.langName]['i077_skinned'] + ', '.join(geomSkinList),
        else:
            print self.langDic[self.langName]['i029_skinNothing'],

    ###################### End: Skinning.
