#!/usr/bin/python
# -*- coding: utf-8 -*-

###################################################################
#
#    dpAutoRigSystem Python script
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


# current version:
DPAR_VERSION = "3.09.24"
DPAR_UPDATELOG = "Improved: Limb auto clavicle pointing to\ncorner joint (elbow/knee)."



###################### Start: Loading.

import maya.cmds as cmds
import sys
import os
import random

def clearDPARLoadingWindow():
    if cmds.window('dpARLoadWin', query=True, exists=True):
        cmds.deleteUI('dpARLoadWin', window=True)

def dpARLoadingWindow():
    """ Just create a Loading window in order to show we are working to user when calling dpAutoRigSystem.
    """
    loadingString = "Loading dpAutoRigSystem v%s ... " %DPAR_VERSION
    print loadingString,
    path = os.path.dirname(__file__)
    randImage = random.randint(0,7)
    clearDPARLoadingWindow()
    cmds.window('dpARLoadWin', title='dpAutoRigSystem', iconName='dpAutoRig', widthHeight=(285, 203), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
    cmds.columnLayout('dpARLoadLayout')
    cmds.image('loadingImage', image=(path+"/Icons/dp_loading_0%i.png" %randImage), backgroundColor=(0.8, 0.8, 0.8), parent='dpARLoadLayout')
    cmds.text('versionText', label=loadingString, parent='dpARLoadLayout')
    cmds.showWindow('dpARLoadWin')

if not "pymel" in sys.modules:
    dpARLoadingWindow()

###################### End: Loading.



# importing libraries:
try:
    import maya.mel as mel
    import pymel.core as pymel
    import json
    import re
    import time
    import getpass
    import urllib
    import shutil
    import zipfile
    import StringIO
    import datetime
    import platform
    from functools import partial
    import Modules.Library.dpUtils as utils
    import Modules.Library.dpControls as dpControls
    import Modules.dpBaseClass as Base
    import Modules.dpLayoutClass as Layout
    import Extras.dpUpdateRigInfo as rigInfo
    import Extras.dpReorderAttr as dpReorderAttr
    import Languages.Translator.dpTranslator as dpTranslator
    reload(utils)
    reload(dpControls)
    reload(rigInfo)
    reload(Base)
    reload(Layout)
except Exception as e:
    print "Error: importing python modules!!!\n",
    print e
    try:
        clearDPARLoadingWindow()
        self.jobWinClose()
    except:
        pass

# declaring member variables
ENGLISH = "English"
MODULES = "Modules"
SCRIPTS = "Scripts"
CONTROLS = "Controls"
COMBINED = "Controls/Combined"
PRESETS = "Controls/Presets"
EXTRAS = "Extras"
LANGUAGES = "Languages"
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
WHEEL = "Wheel"
STEERING = "Steering"
SUSPENSION = "Suspension"
GUIDE_BASE_NAME = "Guide_Base"
GUIDE_BASE_ATTR = "guideBase"
MODULE_NAMESPACE_ATTR = "moduleNamespace"
MODULE_INSTANCE_INFO_ATTR = "moduleInstanceInfo"
INFO_ICON = "dp_info.png"
DPAR_SITE = "https://nilouco.blogspot.com"
DPAR_RAWURL = "https://raw.githubusercontent.com/nilouco/dpAutoRigSystem/master/dpAutoRigSystem/dpAutoRig.py"
DPAR_GITHUB = "https://github.com/nilouco/dpAutoRigSystem"
DPAR_MASTERURL = "https://github.com/nilouco/dpAutoRigSystem/zipball/master/"
DPAR_WHATSCHANGED = "https://github.com/nilouco/dpAutoRigSystem/commits/master"
SSL_MACOS = "https://medium.com/@katopz/how-to-upgrade-openssl-8d005554401"
DONATE = "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=nilouco%40gmail.com&item_name=Support+dpAutoRigSystem+and+Tutorials+by+Danilo+Pinheiro+%28nilouco%29&currency_code="


class DP_AutoRig_UI:
    
    ###################### Start: UI
    
    def __init__(self):
        """ Start the window, menus and main layout for dpAutoRig UI.
        """
        self.dpARVersion = DPAR_VERSION
        self.loadedPath = False
        self.loadedModules = False
        self.loadedScripts = False
        self.loadedControls = False
        self.loadedCombined = False
        self.loadedExtras = False
        self.controlInstanceList = []
        self.degreeOption = 0
        
        
        try:
            # store all UI elements in a dictionary:
            self.allUIs = {}
            self.iDeleteJobId = 0
            self.iSelChangeJobId = 0
            # creating User Interface (UI) Window:
            self.deleteExistWindow()
            dpAR_winWidth  = 305
            dpAR_winHeight = 605
            self.allUIs["dpAutoRigWin"] = cmds.window('dpAutoRigWindow', title='dpAutoRigSystem - v'+str(DPAR_VERSION)+' - UI', iconName='dpAutoRig', widthHeight=(dpAR_winWidth, dpAR_winHeight), menuBar=True, sizeable=True, minimizeButton=True, maximizeButton=False)
            
            # creating menus:
            self.allUIs["settingsMenu"] = cmds.menu('settingsMenu', label='Settings')
            # language menu:
            self.allUIs["languageMenu"] = cmds.menuItem('languageMenu', label='Language', parent='settingsMenu', subMenu=True)
            cmds.radioMenuItemCollection('languageRadioMenuCollection')
            # create a language list:
            self.langList, self.langDic = self.getJsonFileInfo(LANGUAGES)
            # create menuItems from language list:
            if self.langList:
                # verify if there is a optionVar of last choosen by user in Maya system:
                lastLang = self.checkLastOptionVar("dpAutoRigLastLanguage", ENGLISH, self.langList)
                # create menuItems with the command to set the last language variable, delete languageUI and call mainUI() again when changed:
                for idiom in self.langList:
                    cmds.menuItem(idiom+"_MI", label=idiom, radioButton=False, collection='languageRadioMenuCollection', command='import maya.cmds as cmds; cmds.optionVar(remove=\"dpAutoRigLastLanguage\"); cmds.optionVar(stringValue=(\"dpAutoRigLastLanguage\", \"'+idiom+'\")); cmds.evalDeferred(\"import sys; sys.modules[\'dpAutoRigSystem.dpAutoRig\'].DP_AutoRig_UI()\", lowestPriority=True)')
                # load the last language from optionVar value:
                cmds.menuItem(lastLang+"_MI", edit=True, radioButton=True, collection='languageRadioMenuCollection')
            else:
                print "Error: Cannot load json language files!\n",
                return
            
            # preset menu:
            self.allUIs["presetMenu"] = cmds.menuItem('presetMenu', label='Controls Preset', parent='settingsMenu', subMenu=True)
            cmds.radioMenuItemCollection('presetRadioMenuCollection')
            # create a preset list:
            self.presetList, self.presetDic = self.getJsonFileInfo(PRESETS)
            # create menuItems from preset list:
            if self.presetList:
                # verify if there is a optionVar of last choosen by user in Maya system:
                lastPreset = self.checkLastOptionVar("dpAutoRigLastPreset", "Default", self.presetList)
                # create menuItems with the command to set the last preset variable, delete languageUI and call mainUI() again when changed:
                for preset in self.presetList:
                    cmds.menuItem( preset+"_MI", label=preset, radioButton=False, collection='presetRadioMenuCollection', command='import maya.cmds as cmds; cmds.optionVar(remove=\"dpAutoRigLastPreset\"); cmds.optionVar(stringValue=(\"dpAutoRigLastPreset\", \"'+preset+'\")); cmds.evalDeferred(\"import sys; sys.modules[\'dpAutoRigSystem.dpAutoRig\'].DP_AutoRig_UI()\", lowestPriority=True)')
                # load the last preset from optionVar value:
                cmds.menuItem(lastPreset+"_MI", edit=True, radioButton=True, collection='presetRadioMenuCollection', parent='presetMenu')
            else:
                print "Error: Cannot load json preset files!\n",
                return
            
            # create menu:
            self.allUIs["createMenu"] = cmds.menu('createMenu', label='Create')
            cmds.menuItem('translator_MI', label='Translator', command=self.translator)
            cmds.menuItem('preset_MI', label='Preset', command=self.createPreset)
            # window menu:
            self.allUIs["windowMenu"] = cmds.menu( 'windowMenu', label='Window')
            cmds.menuItem('reloadUI_MI', label='Reload UI', command=self.jobReloadUI)
            cmds.menuItem('quit_MI', label='Quit', command=self.deleteExistWindow)
            # help menu:
            self.allUIs["helpMenu"] = cmds.menu( 'helpMenu', label='Help', helpMenu=True)
            cmds.menuItem('about_MI"', label='About', command=partial(self.info, 'm015_about', 'i006_aboutDesc', None, 'center', 305, 250))
            cmds.menuItem('author_MI', label='Author', command=partial(self.info, 'm016_author', 'i007_authorDesc', None, 'center', 305, 250))
            cmds.menuItem('collaborators_MI', label='Collaborators', command=partial(self.info, 'i165_collaborators', 'i166_collabDesc', "\n\n"+self.langDic[ENGLISH]['_collaborators'], 'center', 305, 250))
            cmds.menuItem('donate_MI', label='Donate', command=partial(self.donateWin))
            cmds.menuItem('idiom_MI', label='Idioms', command=partial(self.info, 'm009_idioms', 'i012_idiomsDesc', None, 'center', 305, 250))
            cmds.menuItem('update_MI', label='Update', command=partial(self.checkForUpdate, True))
            cmds.menuItem('help_MI', label='Help...', command=partial(utils.visitWebSite, DPAR_SITE))
            
            # create the main layout:
            self.allUIs["mainLayout"] = cmds.formLayout('mainLayout')
            # here we will populate with layout from mainUI based in the choose language.
            
            # call mainUI in order to populate the main layout:
            self.mainUI()
            
            # check if we need to automatically check for update:
            self.autoCheckUpdate()
        
        except Exception as e:
            print "Error: dpAutoRig UI window !!!\n"
            print "Exception:", e
            print self.langDic[self.langName]['i008_errorUI'],
            clearDPARLoadingWindow()
            return
        

        # call UI window: Also ensure that when thedock controler X button it it, the window is killed and the dock control too
        self.iUIKilledId = cmds.scriptJob(uiDeleted=[self.allUIs["dpAutoRigWin"], self.jobWinClose])
        self.pDockCtrl = cmds.dockControl('dpAutoRigSystem', area="left", content=self.allUIs["dpAutoRigWin"], visibleChangeCommand=self.jobDockVisChange)

        #print self.pDockCtrl
        clearDPARLoadingWindow()
        

    def deleteExistWindow(self, *args):
        """ Check if there are the dpAutoRigWindow and dpAutoRigSystem_Control to deleteUI.
        """
        if cmds.window('dpAutoRigWindow', query=True, exists=True):
            cmds.deleteUI('dpAutoRigWindow', window=True)
        if cmds.dockControl('dpAutoRigSystem', query=True, exists=True):
            cmds.deleteUI('dpAutoRigSystem', control=True)
    
    
    def getJsonFileInfo(self, dir):
        """ Find all json files in the given path and get coctemt used for each file.
            Create a dictionary with dictionaries of all file found.
            Return a list with the name of the found files.
        """
        # declare the resulted list:
        resultList = []
        resultDic = {}
        # find path where 'dpAutoRig.py' is been executed:
        path = os.path.dirname(__file__)
        # hack in order to avoid "\\" from os.sep, them we need to use the replace string method:
        jsonPath = os.path.join(path, dir, "").replace("\\", "/")
        # list all files in this directory:
        allFileList = os.listdir(jsonPath)
        for file in allFileList:
            # verify if there is the extension ".json"
            if file.endswith(".json"):
                # get the name of the type from the file name:
                typeName = file.partition(".json")[0]
                # clear the old variable content and open the json file as read:
                content = None
                fileDictionary = open(jsonPath + file, "r")
                try:
                    # read the json file content and store it in a dictionary:
                    content = json.loads(fileDictionary.read())
                    resultDic[typeName] = content
                    resultList.append(typeName)
                except:
                    print "Error: json file corrupted:", file,
                # close the json file:
                fileDictionary.close()
        return resultList, resultDic
    
    
    def checkLastOptionVar(self, optionVarName, preferableName, typeList):
        """ Verify if there's a optionVar with this name or create it with the preferable given value.
            Returns the lastValue found.
        """
        lastValueExists = cmds.optionVar(exists=optionVarName)
        if not lastValueExists:
            # if not exists a last optionVar, set it to preferableName if it exists, or to the first value in the list:
            if preferableName in typeList:
                cmds.optionVar( stringValue=(optionVarName, preferableName) )
            else:
                cmds.optionVar( stringValue=(optionVarName, typeList[0]) )
        # get its value puting in a variable to return it:
        resultValue = cmds.optionVar( query=optionVarName )
        # if the last value in the system was different of json files, set it to preferableName or to the first value in the list also:
        if not resultValue in typeList:
            if preferableName in typeList:
                resultValue = preferableName
            else:
                resultValue = resultValue[0]
        return resultValue
    
    
    def getCurrentMenuValue(self, itemList, *args):
        for item in itemList:
            if cmds.menuItem( item+"_MI", query=True, radioButton=True ):
                return item
    
    
    def changeOptionDegree(self, degreeOption, *args):
        """ Set optionVar to choosen menu item.
        """
        cmds.optionVar(stringValue=('dpAutoRigLastDegreeOption', degreeOption))
        self.degreeOption = int(degreeOption[0])
    
    
    def mainUI(self):
        """ Create the layouts inside of the mainLayout. Here will be the entire User Interface.
        """
        # get current language choose UI from menu:
        self.langName = self.getCurrentMenuValue(self.langList)
        # get current preset choose UI from menu:
        self.presetName = self.getCurrentMenuValue(self.presetList)            
        
        # initialize dpControls:
        self.ctrls = dpControls.ControlClass(self, self.presetDic, self.presetName)
        
        # --
        
        # creating tabs - mainTabLayout:
        self.allUIs["mainTabLayout"] = cmds.tabLayout('mainTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=self.allUIs["mainLayout"])
        cmds.formLayout( self.allUIs["mainLayout"], edit=True, attachForm=((self.allUIs["mainTabLayout"], 'top', 0), (self.allUIs["mainTabLayout"], 'left', 0), (self.allUIs["mainTabLayout"], 'bottom', 0), (self.allUIs["mainTabLayout"], 'right', 0)) )
        
        # --
        
        # interface of Rigging tab - formLayout:
        self.allUIs["riggingTabLayout"] = cmds.formLayout('riggingTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        
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
        self.allUIs["degreeLayout"] = cmds.rowColumnLayout('degreeLayout', numberOfColumns=2, columnWidth=[(1, 100), (2, 250)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["rigOptionsLayout"])
        # option Degree:
        self.degreeOptionMenu = cmds.optionMenu("degreeOptionMenu", label='', changeCommand=self.changeOptionDegree, parent=self.allUIs["degreeLayout"])
        self.degreeOptionMenuItemList = ['0 - Preset', '1 - Linear', '3 - Cubic']
        # verify if there is a optionVar of last choosen by user in Maya system:
        lastDegreeOption = self.checkLastOptionVar("dpAutoRigLastDegreeOption", "0 - Preset", self.degreeOptionMenuItemList)
        for degreeOption in self.degreeOptionMenuItemList:
            cmds.menuItem(label=degreeOption, parent=self.degreeOptionMenu)
        cmds.optionMenu(self.degreeOptionMenu, edit=True, value=lastDegreeOption)
        cmds.text(self.langDic[self.langName]['i128_optionDegree'], parent=self.allUIs["degreeLayout"])
        self.degreeOption = int(lastDegreeOption[0])

        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #footerA - columnLayout:
        self.allUIs["footerA"] = cmds.columnLayout('footerA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigAllButton"] = cmds.button(label=self.langDic[self.langName]['i020_rigAll'], annotation=self.langDic[self.langName]['i021_rigAllDesc'], backgroundColor=(0.6, 1.0, 0.6), command=self.rigAll, parent=self.allUIs["footerA"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerA"])
        # this text will be actualized by the number of module instances created in the scene...
        self.allUIs["footerAText"] = cmds.text('footerAText', align='center', label="# "+self.langDic[self.langName]['i005_footerA'], parent=self.allUIs["footerA"])
        cmds.setParent( self.allUIs["mainTabLayout"] )
        
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
        self.allUIs["skinningTabLayout"] = cmds.formLayout('skinningTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        
        #colSkinLeftA - columnLayout:
        self.allUIs["colSkinLeftA"] = cmds.columnLayout('colSkinLeftA', adjustableColumn=True, width=190, parent=self.allUIs["skinningTabLayout"])
        # radio buttons:
        self.allUIs["jntCollection"] = cmds.radioCollection('jntCollection', parent=self.allUIs["colSkinLeftA"])
        allJoints   = cmds.radioButton( label=self.langDic[self.langName]['i022_listAllJnts'], annotation="allJoints", onCommand=self.populateJoints )
        dpARJoints  = cmds.radioButton( label=self.langDic[self.langName]['i023_listdpARJnts'], annotation="dpARJoints", onCommand=self.populateJoints )
        self.allUIs["jointsDisplay"] = cmds.rowColumnLayout('jointsDisplay', numberOfColumns=2, columnWidth=[(1, 40), (2, 100)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["colSkinLeftA"])
        self.allUIs["_JntCB"] = cmds.checkBox('_JntCB', label="_Jnt", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["_JisCB"] = cmds.checkBox('_JisCB', label="_Jis", align='left', value=1, changeCommand=self.populateJoints, parent=self.allUIs["jointsDisplay"])
        self.allUIs["jointNameTF"] = cmds.textField('jointNameTF', width=30, changeCommand=self.populateJoints, parent=self.allUIs["colSkinLeftA"])
        self.allUIs["jntTextScrollLayout"] = cmds.textScrollList( 'jntTextScrollLayout', width=30, allowMultiSelection=True, selectCommand=self.atualizeSkinFooter, parent=self.allUIs["skinningTabLayout"] )
        cmds.radioCollection( self.allUIs["jntCollection"], edit=True, select=dpARJoints )
        cmds.setParent(self.allUIs["skinningTabLayout"])
        
        #colSkinRightA - columnLayout:
        self.allUIs["colSkinRightA"] = cmds.columnLayout('colSkinRightA', adjustableColumn=True, width=190, parent=self.allUIs["skinningTabLayout"])
        self.allUIs["geomCollection"] = cmds.radioCollection('geomCollection', parent=self.allUIs["colSkinRightA"])
        allGeoms   = cmds.radioButton( label=self.langDic[self.langName]['i026_listAllJnts'], annotation="allGeoms", onCommand=self.populateGeoms )
        selGeoms   = cmds.radioButton( label=self.langDic[self.langName]['i027_listSelJnts'], annotation="selGeoms", onCommand=self.populateGeoms )
        self.allUIs["geoLongName"] = cmds.checkBox('geoLongName', label=self.langDic[self.langName]['i073_displayLongName'], align='left', value=1, changeCommand=self.populateGeoms, parent=self.allUIs["colSkinRightA"])
        self.allUIs["geoNameTF"] = cmds.textField('geoNameTF', width=30, changeCommand=self.populateGeoms, parent=self.allUIs["colSkinRightA"])
        self.allUIs["modelsTextScrollLayout"] = cmds.textScrollList( 'modelsTextScrollLayout', width=30, allowMultiSelection=True, selectCommand=self.atualizeSkinFooter, parent=self.allUIs["skinningTabLayout"] )
        cmds.radioCollection( self.allUIs["geomCollection"], edit=True, select=allGeoms )
        cmds.setParent(self.allUIs["skinningTabLayout"])
        
        #footerB - columnLayout:
        self.allUIs["footerB"] = cmds.columnLayout('footerB', adjustableColumn=True, parent=self.allUIs["skinningTabLayout"])
        cmds.separator(style='none', height=3, parent=self.allUIs["footerB"])
        self.allUIs["skinButton"] = cmds.button("skinButton", label=self.langDic[self.langName]['i028_skinButton'], backgroundColor=(0.5, 0.8, 0.8), command=partial(self.skinFromUI), parent=self.allUIs["footerB"])
        self.allUIs["footerAddRem"] = cmds.paneLayout("footerAddRem", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["footerB"])
        self.allUIs["addSkinButton"] = cmds.button("addSkinButton", label=self.langDic[self.langName]['i063_skinAddBtn'], backgroundColor=(0.7, 0.9, 0.9), command=partial(self.skinFromUI, "Add"), parent=self.allUIs["footerAddRem"])
        self.allUIs["removeSkinButton"] = cmds.button("removeSkinButton", label=self.langDic[self.langName]['i064_skinRemBtn'], backgroundColor=(0.1, 0.3, 0.3), command=partial(self.skinFromUI, "Remove"), parent=self.allUIs["footerAddRem"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerB"])
        # this text will be actualized by the number of joints and geometries in the textScrollLists for skinning:
        self.allUIs["footerBText"] = cmds.text('footerBText', align='center', label="0 "+self.langDic[self.langName]['i025_joints']+" 0 "+self.langDic[self.langName]['i024_geometries'], parent=self.allUIs["footerB"])
        cmds.setParent( self.allUIs["mainTabLayout"] )
        
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
        
        # interface of Control tab - formLayout:
        self.allUIs["controlTabLayout"] = cmds.formLayout('controlTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        # controlMainLayout - scrollLayout:
        self.allUIs["controlMainLayout"] = cmds.scrollLayout('controlMainLayout', parent=self.allUIs["controlTabLayout"])
        self.allUIs["controlLayout"] = cmds.columnLayout('controlLayout', adjustableColumn=True, rowSpacing=10, parent=self.allUIs['controlMainLayout'])
        
        # createControl - frameLayout:
        self.allUIs["createControlLayout"] = cmds.frameLayout('createControlLayout', label=self.langDic[self.langName]['i114_createControl'], collapsable=True, collapse=False, marginWidth=10, marginHeight=10, parent=self.allUIs["controlLayout"])
        self.allUIs["optionsB"] = cmds.frameLayout('optionsB', label=self.langDic[self.langName]['i002_options'], collapsable=True, collapse=False, marginWidth=10, parent=self.allUIs["createControlLayout"])
        self.allUIs["controlOptionsLayout"] = cmds.columnLayout('controlOptionsLayout', adjustableColumn=True, width=50, rowSpacing=5, parent=self.allUIs["optionsB"])
        self.allUIs["controlNameTFG"] = cmds.textFieldGrp('controlNameTFG', text="", label=self.langDic[self.langName]['i101_customName'], columnAlign2=("right", "left"), adjustableColumn2=2, columnAttach=((1, "right", 5), (2, "left", 5)), parent=self.allUIs["controlOptionsLayout"])
        self.allUIs["controlActionRBG"] = cmds.radioButtonGrp("controlActionRBG", label=self.langDic[self.langName]['i109_action'], labelArray3=[self.langDic[self.langName]['i108_newControl'], self.langDic[self.langName]['i107_addShape'], self.langDic[self.langName]['i102_replaceShape']], vertical=True, numberOfRadioButtons=3, parent=self.allUIs["controlOptionsLayout"])
        cmds.radioButtonGrp(self.allUIs["controlActionRBG"], edit=True, select=1) #new control
        self.allUIs["degreeRBG"] = cmds.radioButtonGrp("degreeRBG", label=self.langDic[self.langName]['i103_degree'], labelArray2=[self.langDic[self.langName]['i104_linear'], self.langDic[self.langName]['i105_cubic']], vertical=True, numberOfRadioButtons=2, parent=self.allUIs["controlOptionsLayout"])
        cmds.radioButtonGrp(self.allUIs["degreeRBG"], edit=True, select=1) #linear
        self.allUIs["controlSizeFSG"] = cmds.floatSliderGrp("controlSizeFSG", label=self.langDic[self.langName]['i115_size'], field=True, minValue=0.01, maxValue=10.0, fieldMinValue=0, fieldMaxValue=1000.0, precision=2, value=1.0, parent=self.allUIs["controlOptionsLayout"])
        self.allUIs["directionOMG"] = cmds.optionMenuGrp("directionOMG", label=self.langDic[self.langName]['i106_direction'], parent=self.allUIs["controlOptionsLayout"])
        cmds.menuItem(label='-X')
        cmds.menuItem(label='+X')
        cmds.menuItem(label='-Y')
        cmds.menuItem(label='+Y')
        cmds.menuItem(label='-Z')
        cmds.menuItem(label='+Z')
        cmds.optionMenuGrp(self.allUIs["directionOMG"], edit=True, value='+Y')
        
        # curveShapes - frameLayout:
        self.allUIs["controlShapesLayout"] = cmds.frameLayout('controlShapesLayout', label=self.langDic[self.langName]['i100_curveShapes'], collapsable=True, collapse=False, parent=self.allUIs["createControlLayout"])
        self.allUIs["controlModuleLayout"] = cmds.gridLayout('controlModuleLayout', numberOfColumns=7, cellWidthHeight=(50, 50), backgroundColor=(0.3, 0.3, 0.3), parent=self.allUIs['controlShapesLayout'])
        # here we populate the control module layout with the items from Controls folder:
        self.controlModuleList = self.startGuideModules(CONTROLS, "start", "controlModuleLayout")
        
        self.allUIs["combinedControlShapesLayout"] = cmds.frameLayout('combinedControlShapesLayout', label=self.langDic[self.langName]['i118_combinedShapes'], collapsable=True, collapse=False, parent=self.allUIs["createControlLayout"])
        self.allUIs["combinedControlModuleLayout"] = cmds.gridLayout('combinedControlModuleLayout', numberOfColumns=7, cellWidthHeight=(50, 50), backgroundColor=(0.3, 0.3, 0.3), parent=self.allUIs['combinedControlShapesLayout'])
        # here we populate the control module layout with the items from Controls folder:
        self.combinedControlModuleList = self.startGuideModules(COMBINED, "start", "combinedControlModuleLayout")
        
        # editSeletedControls - frameLayout:
        self.allUIs["editSelectionFL"] = cmds.frameLayout('editSelectionFL', label=self.langDic[self.langName]['i111_editSelection'], collapsable=True, collapse=False, marginHeight=10, parent=self.allUIs["controlLayout"])
        self.allUIs["editSelection3Layout"] = cmds.paneLayout("editSelection3Layout", configuration="vertical3", separatorThickness=2.0, parent=self.allUIs["editSelectionFL"])
        self.allUIs["addShapeButton"] = cmds.button("addShapeButton", label=self.langDic[self.langName]['i113_addShapes'], backgroundColor=(1.0, 0.6, 0.7), command=partial(self.ctrls.transferShape, False, False), parent=self.allUIs["editSelection3Layout"])
        self.allUIs["copyShapeButton"] = cmds.button("copyShapeButton", label=self.langDic[self.langName]['i112_copyShapes'], backgroundColor=(1.0, 0.6, 0.5), command=partial(self.ctrls.transferShape, False, True), parent=self.allUIs["editSelection3Layout"])
        self.allUIs["replaceShapeButton"] = cmds.button("replaceShapeButton", label=self.langDic[self.langName]['i110_transferShapes'], backgroundColor=(1.0, 0.6, 0.3), command=partial(self.ctrls.transferShape, True, True), parent=self.allUIs["editSelection3Layout"])
        self.allUIs["editSelection2Layout"] = cmds.paneLayout("editSelection2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["editSelectionFL"])
        self.allUIs["resetCurveButton"] = cmds.button("resetCurveButton", label=self.langDic[self.langName]['i121_resetCurve'], backgroundColor=(1.0, 0.7, 0.3), height=30, command=partial(self.ctrls.resetCurve), parent=self.allUIs["editSelection2Layout"])
        self.allUIs["changeDegreeButton"] = cmds.button("changeDegreeButton", label=self.langDic[self.langName]['i120_changeDegree'], backgroundColor=(1.0, 0.8, 0.4), height=30, command=partial(self.ctrls.resetCurve, True), parent=self.allUIs["editSelection2Layout"])
        self.allUIs["zeroOutGrpButton"] = cmds.button("zeroOutGrpButton", label=self.langDic[self.langName]['i116_zeroOut'], backgroundColor=(0.8, 0.8, 0.8), height=30, command=utils.zeroOut, parent=self.allUIs["editSelectionFL"])
        
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["controlTabLayout"], edit=True,
                        attachForm=[(self.allUIs["controlMainLayout"], 'top', 20), (self.allUIs["controlMainLayout"], 'left', 5), (self.allUIs["controlMainLayout"], 'right', 5), (self.allUIs["controlMainLayout"], 'bottom', 5)]
                        )
        
        # --
        
        # interface of Extra tab - formLayout:
        self.allUIs["extraTabLayout"] = cmds.formLayout('extraTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
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
        cmds.tabLayout( self.allUIs["mainTabLayout"], edit=True, tabLabel=((self.allUIs["riggingTabLayout"], 'Rigging'), (self.allUIs["skinningTabLayout"], 'Skinning'), (self.allUIs["controlTabLayout"], 'Control'), (self.allUIs["extraTabLayout"], 'Extra')) )
        cmds.select(clear=True)

    
    def jobReloadUI(self, *args):
        """ This scriptJob active when we got one new scene in order to reload the UI.
        """
        import maya.cmds as cmds
        cmds.select(clear=True)
        cmds.evalDeferred("import sys; sys.modules['dpAutoRigSystem.dpAutoRig'].DP_AutoRig_UI()", lowestPriority=True)
    
    
    def jobWinClose(self, *args):
        #This job will ensure that the dock control is killed correctly
        if self.pDockCtrl:
            if cmds.objExists(self.pDockCtrl):
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
                self.jobReloadUI()
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
    
    
    def createJsonFile(self, newString, fileDir, fileNameID, *args):
        """ Load given string as a json dictionary and save it as a json file with the fileNameID in the fileDir.
            Returns the loaded json dictionary.
        """
        # json file:
        resultDic = json.loads(newString)
        # find path where 'dpAutoRig.py' is been executed:
        path = os.path.dirname(__file__)
        # hack in order to avoid "\\" from os.sep, them we need to use the replace string method:
        jsonPath = os.path.join(path, fileDir, "").replace("\\", "/")
        jsonFileName = jsonPath+resultDic[fileNameID]+'.json'
        # write json file in the HD:
        with open(jsonFileName, 'w') as jsonFile:
            json.dump(resultDic, jsonFile, indent=4, sort_keys=True)
        return resultDic
    
    
    def translator(self, *args):
        """ call language translator.
        """
        self.translatorInst = dpTranslator.Translator(self, self.langDic, self.langName)
        self.translatorInst.dpTranslatorMain()
        
        
    def createPreset(self, *args):
        """ Just call ctrls create preset and set it as userDefined preset.
        """
        newPresetString = self.ctrls.dpCreatePreset()
        if newPresetString:
            # create json file:
            resultDic = self.createJsonFile(newPresetString, PRESETS, '_preset')
            # set this new preset as userDefined preset:
            self.presetName = resultDic['_preset']
            cmds.optionVar(remove="dpAutoRigLastPreset")
            cmds.optionVar(stringValue=("dpAutoRigLastPreset", self.presetName))
            # show preset creation result window:
            self.info('i129_createPreset', 'i133_presetCreated', '\n'+self.presetName+'\n\n'+self.langDic[self.langName]['i134_rememberPublish']+'\n\n'+self.langDic[self.langName]['i018_thanks'], 'center', 205, 270)
            # close and reload dpAR UI in order to avoide Maya crash
            self.jobReloadUI()
            
    
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
        mirrorAxisAttr = "mirrorAxis"
        dispAnnotAttr = "displayAnnotation"

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
        
        # reset radius as original
        origRadius = cmds.getAttr(moduleNamespaceValue+":"+GUIDE_BASE_NAME+"_RadiusCtrl.translateX")
        cmds.setAttr(newGuideName+"_RadiusCtrl.translateX", origRadius)
        
        # getting a good attribute list
        toSetAttrList = cmds.listAttr(selectedItem)
        guideBaseAttrIdx = toSetAttrList.index(GUIDE_BASE_ATTR)
        toSetAttrList = toSetAttrList[guideBaseAttrIdx:]
        toSetAttrList.remove(GUIDE_BASE_ATTR)
        toSetAttrList.remove(MODULE_NAMESPACE_ATTR)
        toSetAttrList.remove(customNameAttr)
        toSetAttrList.remove(mirrorAxisAttr)
        
        # check for special attributes
        if cmds.objExists(selectedItem+"."+nSegmentsAttr):
            toSetAttrList.remove(nSegmentsAttr)
            nJointsValue = cmds.getAttr(selectedItem+'.'+nSegmentsAttr)
            if nJointsValue > 1:
                newGuideInstance.changeJointNumber(nJointsValue)
        if cmds.objExists(selectedItem+"."+customNameAttr):
            customNameValue = cmds.getAttr(selectedItem+'.'+customNameAttr)
            if customNameValue != "" and customNameValue != None:
                newGuideInstance.editUserName(customNameValue)
        if cmds.objExists(selectedItem+"."+mirrorAxisAttr):
            mirroirAxisValue = cmds.getAttr(selectedItem+'.'+mirrorAxisAttr)
            if mirroirAxisValue != "off":
                newGuideInstance.changeMirror(mirroirAxisValue)
        if cmds.objExists(selectedItem+"."+dispAnnotAttr):
            toSetAttrList.remove(dispAnnotAttr)
            currentDisplayAnnotValue = cmds.getAttr(selectedItem+'.'+dispAnnotAttr)
            newGuideInstance.displayAnnotation(currentDisplayAnnotValue)
        
        # get and set transformations
        childrenList = cmds.listRelatives(selectedItem, children=True, allDescendents=True, fullPath=True, type="transform")
        if childrenList:
            for child in childrenList:
                if not "|Guide_Base|Guide_Base" in child:
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
                if cmds.getAttr(selectedItem+"."+toSetAttr):
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
        jointList, sortedJointList = [], []
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
        
        # sort joints by name filter:
        jointName = cmds.textField(self.allUIs["jointNameTF"], query=True, text=True)
        if jointList:
            if jointName:
                sortedJointList = utils.filterName(jointName, jointList, " ")
            else:
                sortedJointList = jointList
        
        # populate the list:
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, removeAll=True)
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, append=sortedJointList)
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
        geomList, shortNameList, sameNameList, sortedGeoList = [], [], [], []
        
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
        
        # sort geometries by name filter:
        geoName = cmds.textField(self.allUIs["geoNameTF"], query=True, text=True)
        if geomList:
            if geoName:
                sortedGeoList = utils.filterName(geoName, geomList, " ")
            else:
                sortedGeoList = geomList
        
        # populate the list:
        cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, removeAll=True)
        if sameNameList:
            cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, lineFont=[(len(sortedGeoList)-len(sameNameList)-2, 'boldLabelFont'), (len(sortedGeoList)-len(sameNameList)-1, 'obliqueLabelFont'), (len(sortedGeoList)-len(sameNameList), 'obliqueLabelFont')], append=sortedGeoList)
        else:
            cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, append=sortedGeoList)
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
    
    
    def checkForUpdate(self, verbose=True, *args):
        """ Check if there's an update for this current script version.
            Output the result in a window.
        """
        print "\n", self.langDic[self.langName]['i084_checkUpdate']
        
        # compare current version with GitHub master
        rawResult = utils.checkRawURLForUpdate(DPAR_VERSION, DPAR_RAWURL)
        
        # call Update Window about rawRsult:
        if rawResult[0] == 0:
            if verbose:
                self.updateWin(rawResult, 'i085_updated')
        elif rawResult[0] == 1:
            self.updateWin(rawResult, 'i086_newVersion')
        elif rawResult[0] == 2:
            if verbose:
                self.updateWin(rawResult, 'i087_rawURLFail')
        elif rawResult[0] == 3:
            if verbose:
                self.updateWin(rawResult, 'i088_internetFail')
        elif rawResult[0] == 4:
            if verbose:
                self.updateWin(rawResult, 'e008_failCheckUpdate')
    
    
    # Start working with Guide Modules:
    def startGuideModules(self, guideDir, action, layout, checkModuleList=None):
        """ Find and return the modules in the directory 'Modules'.
            Returns a list with the found modules.
        """
        # find path where 'dpAutoRig.py' is been executed:
        path = utils.findPath("dpAutoRig.py")
        if not self.loadedPath:
            print "dpAutoRigPath: "+path
            self.loadedPath = True
        # list all guide modules:
        guideModuleList = utils.findAllModules(path, guideDir)
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
            # avoid print again the same message:
            if guideDir == MODULES and not self.loadedModules:
                print guideDir+" : "+str(guideModuleList)
                self.loadedModules = True
            if guideDir == SCRIPTS and not self.loadedScripts:
                print guideDir+" : "+str(guideModuleList)
                self.loadedScripts = True
            if guideDir == CONTROLS and not self.loadedControls:
                print guideDir+" : "+str(guideModuleList)
                self.loadedControls = True
            if guideDir == COMBINED and not self.loadedCombined:
                print guideDir+" : "+str(guideModuleList)
                self.loadedCombined = True
            if guideDir == EXTRAS and not self.loadedExtras:
                print guideDir+" : "+str(guideModuleList)
                self.loadedExtras = True
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
            guideDir = guideDir.replace("/", ".")
            guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
            reload(guide)
        except Exception as e:
            print e
            errorString = self.langDic[self.langName]['e017_loadingExtension']+" "+guideModule+" : "+e
            mel.eval('warning \"'+errorString+'\";')
            return

        # getting data from guide module:
        title = self.langDic[self.langName][guide.TITLE]
        description = self.langDic[self.langName][guide.DESCRIPTION]
        icon = guide.ICON
        # find path where 'dpAutoRig.py' is been executed to get the icon:
        path = utils.findPath("dpAutoRig.py")
        iconDir = path+icon
        iconInfo = path+"/Icons/"+INFO_ICON
        guideName = guide.CLASS_NAME
        
        # creating a basic layout for guide buttons:
        if guideDir == CONTROLS or guideDir == COMBINED.replace("/", "."):
            controlInstance = self.initControlModule(guideModule, guideDir)
            cmds.iconTextButton(image=iconDir, label=guideName, annotation=guideName, height=32, width=32, command=partial(self.installControlModule, controlInstance, True), parent=self.allUIs[layout])
            self.controlInstanceList.append(controlInstance)
        else:
            moduleLayout = cmds.rowLayout(numberOfColumns=3, columnWidth3=(32, 55, 17), height=32, adjustableColumn=2, columnAlign=(1, 'left'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent=self.allUIs[layout])
            cmds.image(i=iconDir, width=32, parent=moduleLayout)

            if guideDir == MODULES:
                '''
                We need to passe the rigType parameters because the cmds.button command will send a False parameter that
                will be stock in the rigType if we don't pass the parameter
                https://stackoverflow.com/questions/24616757/maya-python-cmds-button-with-ui-passing-variables-and-calling-a-function
                '''
                cmds.button(label=title, height=32, command=partial(self.initGuide, guideModule, guideDir, Base.RigType.biped), parent=moduleLayout)
            elif guideDir == SCRIPTS:
                cmds.button(label=title, height=32, command=partial(self.execScriptedGuide, guideModule, guideDir), parent=moduleLayout)
            elif guideDir == EXTRAS:
                cmds.button(label=title, height=32, width=200, command=partial(self.initExtraModule, guideModule, guideDir), parent=moduleLayout)
            
            cmds.iconTextButton(i=iconInfo, height=30, width=17, style='iconOnly', command=partial(self.info, guide.TITLE, guide.DESCRIPTION, None, 'center', 305, 250), parent=moduleLayout)
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
        guideInstance = guideClass(self, self.langDic, self.langName, self.presetDic, self.presetName, userSpecName, rigType)
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
        guideInstance = guideClass(self, self.langDic, self.langName, self.presetDic, self.presetName)
        return guideInstance
    
    
    def initControlModule(self, guideModule, guideDir, *args):
        """ Call initExtraModule because it's the same code.
        """
        guideInstance = self.initExtraModule(guideModule, guideDir)
        return guideInstance
    
    
    def installControlModule(self, controlInstance, useUI, *args):
        """  Start the creation of this Control module using the UI info.
        """
        controlInstance.cvMain(useUI)
    
    
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
                    moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, self.presetDic, self.presetName, module[1], curRigType)
                else:
                    if cmds.attributeQuery("Style", node=module[2], ex=True):
                        iStyle = cmds.getAttr(module[2] + ".Style")
                        if (iStyle == 0 or iStyle == 1):
                            moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, self.presetDic, self.presetName, module[1], Base.RigType.biped)
                        else:
                            moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, self.presetDic, self.presetName, module[1], Base.RigType.quadruped)
                    else:
                        moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, self.presetDic, self.presetName, module[1], Base.RigType.default)
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
        infoColumnLayout = cmds.columnLayout('infoColumnLayout', adjustableColumn=True, columnOffset=['both', 20], parent=dpInfoWin)
        cmds.separator(style='none', height=10, parent=infoColumnLayout)
        infoLayout = cmds.scrollLayout('infoLayout', parent=infoColumnLayout)
        if self.info_description:
            infoDesc = cmds.text(self.langDic[self.langName][self.info_description], align=self.info_align, parent=infoLayout)
        if self.info_text:
            infoText = cmds.text(self.info_text, align=self.info_align, parent=infoLayout)
        # call Info Window:
        cmds.showWindow(dpInfoWin)
    
    
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
    
    
    def donateWin(self, *args):
        """ Simple window with links to donate in order to support this free and openSource code via PayPal.
        """
        # declaring variables:
        self.donate_title       = 'dpAutoRig - v'+DPAR_VERSION+' - '+self.langDic[self.langName]['i167_donate']
        self.donate_description = self.langDic[self.langName]['i168_donateDesc']
        self.donate_winWidth    = 305
        self.donate_winHeight   = 300
        self.donate_align       = "center"
        # creating Donate Window:
        if cmds.window('dpDonateWindow', query=True, exists=True):
            cmds.deleteUI('dpDonateWindow', window=True)
        dpDonateWin = cmds.window('dpDonateWindow', title=self.donate_title, iconName='dpInfo', widthHeight=(self.donate_winWidth, self.donate_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        donateColumnLayout = cmds.columnLayout('donateColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpDonateWin)
        cmds.separator(style='none', height=10, parent=donateColumnLayout)
        infoDesc = cmds.text(self.donate_description, align=self.donate_align, parent=donateColumnLayout)
        cmds.separator(style='none', height=10, parent=donateColumnLayout)
        brPaypalButton = cmds.button('brlPaypalButton', label=self.langDic[self.langName]['i167_donate']+" - R$ - Real", align=self.donate_align, command=partial(utils.visitWebSite, DONATE+"BRL"), parent=donateColumnLayout)
        #usdPaypalButton = cmds.button('usdPaypalButton', label=self.langDic[self.langName]['i167_donate']+" - USD - Dollar", align=self.donate_align, command=partial(utils.visitWebSite, DONATE+"USD"), parent=donateColumnLayout)
        # call Donate Window:
        cmds.showWindow(dpDonateWin)
    
    
    def updateWin(self, rawResult, text, *args):
        """ Create a window showing the text info with the description about any module.
        """
        # declaring variables:
        self.update_checkedNumber = rawResult[0]
        self.update_remoteVersion = rawResult[1]
        self.update_remoteLog     = rawResult[2]
        self.update_text          = text
        self.update_winWidth      = 305
        self.update_winHeight     = 300
        # creating Update Window:
        if cmds.window('dpUpdateWindow', query=True, exists=True):
            cmds.deleteUI('dpUpdateWindow', window=True)
        dpUpdateWin = cmds.window('dpUpdateWindow', title='dpAutoRigSystem - '+self.langDic[self.langName]['i089_update'], iconName='dpInfo', widthHeight=(self.update_winWidth, self.update_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        updateLayout = cmds.columnLayout('updateLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpUpdateWin)
        if self.update_text:
            updateDesc = cmds.text("\n"+self.langDic[self.langName][self.update_text], align="center", parent=updateLayout)
            cmds.text("\n"+DPAR_VERSION+self.langDic[self.langName]['i090_currentVersion'], align="left", parent=updateLayout)
        if self.update_remoteVersion:
            cmds.text(self.update_remoteVersion+self.langDic[self.langName]['i091_onlineVersion'], align="left", parent=updateLayout)
            cmds.separator(height=30)
            if self.update_remoteLog:
                remoteLog = self.update_remoteLog.replace("\\n", "\n")
                cmds.text(self.langDic[self.langName]['i171_updateLog']+":\n", align="center", parent=updateLayout)
                cmds.text(remoteLog, align="left", parent=updateLayout)
                cmds.separator(height=30)
            whatsChangedButton = cmds.button('whatsChangedButton', label=self.langDic[self.langName]['i117_whatsChanged'], align="center", command=partial(utils.visitWebSite, DPAR_WHATSCHANGED), parent=updateLayout)
            visiteGitHubButton = cmds.button('visiteGitHubButton', label=self.langDic[self.langName]['i093_gotoWebSite'], align="center", command=partial(utils.visitWebSite, DPAR_GITHUB), parent=updateLayout)
            if (int(cmds.about(version=True)[:4]) < 2019) and platform.system() == "Darwin": #Maya 2018 or older on macOS
                upgradeSSLmacOSButton = cmds.button('upgradeSSLmacOSButton', label=self.langDic[self.langName]['i164_sslMacOS'], align="center", backgroundColor=(0.8, 0.4, 0.4), command=partial(utils.visitWebSite, SSL_MACOS), parent=updateLayout)
            downloadButton = cmds.button('downloadButton', label=self.langDic[self.langName]['i094_downloadUpdate'], align="center", command=partial(self.downloadUpdate, DPAR_MASTERURL, "zip"), parent=updateLayout)
            installButton = cmds.button('installButton', label=self.langDic[self.langName]['i095_installUpdate'], align="center", command=partial(self.installUpdate, DPAR_MASTERURL, self.update_remoteVersion), parent=updateLayout)
        # automatically check for updates:
        cmds.separator(height=30)
        self.autoCheckUpdateCB = cmds.checkBox('autoCheckUpdateCB', label=self.langDic[self.langName]['i092_autoCheckUpdate'], align="left", value=self.userDefAutoCheckUpdate, changeCommand=self.setAutoCheckUpdatePref, parent=updateLayout)
        cmds.separator(height=30)
        # call Update Window:
        cmds.showWindow(dpUpdateWin)
        print self.langDic[self.langName][self.update_text]
    
    
    def downloadUpdate(self, url, ext, *args):
        """ Download file from given url adrees and ask user to choose folder and file name to save
        """
        extFilter = "*."+ext
        downloadFolder = cmds.fileDialog2(fileFilter=extFilter, dialogStyle=2)
        if downloadFolder:
            cmds.progressWindow(title='Download Update', progress=50, status='Downloading...', isInterruptable=False)
            try:
                urllib.urlretrieve(url, downloadFolder[0])
                self.info('i094_downloadUpdate', 'i096_downloaded', downloadFolder[0]+'\n\n'+self.langDic[self.langName]['i018_thanks'], 'center', 205, 270)
                # closes dpUpdateWindow:
                if cmds.window('dpUpdateWindow', query=True, exists=True):
                    cmds.deleteUI('dpUpdateWindow', window=True)
            except:
                self.info('i094_downloadUpdate', 'e009_failDownloadUpdate', downloadFolder[0]+'\n\n'+self.langDic[self.langName]['i097_sorry'], 'center', 205, 270)
            cmds.progressWindow(endProgress=True)
    
    
    def keepJsonFilesWhenUpdate(self, currentDir, tempUpdateDir, *args):
        """ Check in given folder if we have custom json files and keep then when we install a new update.
            It will just check if there are user created json files, and copy them to temporary extracted update folder.
            So when the install overwrite all files, they will be copied (restored) again.
        """
        newUpdateList = []
        # list all new json files:
        for newRoot, newDirectories, newFiles in os.walk(tempUpdateDir):
            for newItem in newFiles:
                if newItem.endswith('.json'):
                    newUpdateList.append(newItem)
        
        # check if some current json file is a custom file created by user to copy it to new update directory in order to avoid overwrite it:
        for currentRoot, currentDirectories, currentFiles in os.walk(currentDir):
            for currentItem in currentFiles:
                if currentItem.endswith('.json'):
                    if not currentItem in newUpdateList:
                        # found custom file, then copy it to keep when install the new update
                        shutil.copy2(os.path.join(currentRoot, currentItem), tempUpdateDir)
    
    
    def installUpdate(self, url, newVersion, *args):
        """ Install the last version from the given url address to download file
        """
        btContinue = self.langDic[self.langName]['i174_continue']
        btCancel = self.langDic[self.langName]['i132_cancel']
        confirmAutoInstall = cmds.confirmDialog(title=self.langDic[self.langName]['i098_installing'], message=self.langDic[self.langName]['i172_updateManual'], button=[btContinue, btCancel], defaultButton=btContinue, cancelButton=btCancel, dismissString=btCancel)
        if confirmAutoInstall == btContinue:
            print self.langDic[self.langName]['i098_installing']
            # declaring variables:
            dpAR_Folder = "dpAutoRigSystem"
            dpAR_DestFolder = utils.findPath("dpAutoRig.py")
            
            # progress window:
            installAmount = 0
            cmds.progressWindow(title=self.langDic[self.langName]['i098_installing'], progress=installAmount, status='Installing: 0%', isInterruptable=False)
            maxInstall = 100
            
            try:
                # get remote file from url:
                remoteSource = urllib.urlopen(url)
                
                installAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + `installAmount`))
                
                # read the downloaded Zip file stored in the RAM memory:
                dpAR_Zip = zipfile.ZipFile(StringIO.StringIO(remoteSource.read()))
                
                installAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + `installAmount`))
                
                # list Zip file contents in order to extract them in a temporarlly folder:
                zipNameList = dpAR_Zip.namelist()
                for fileName in zipNameList:
                    if dpAR_Folder in fileName:
                        dpAR_Zip.extract(fileName, dpAR_DestFolder)
                dpAR_Zip.close()
                
                installAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + `installAmount`))
                
                # declare temporary folder:
                dpAR_TempDir = dpAR_DestFolder+"/"+zipNameList[0]+dpAR_Folder
                
                # store custom presets in order to avoid overwrite them when installing the update:
                self.keepJsonFilesWhenUpdate(dpAR_DestFolder+"/"+LANGUAGES, dpAR_TempDir+"/"+LANGUAGES)
                self.keepJsonFilesWhenUpdate(dpAR_DestFolder+"/"+PRESETS, dpAR_TempDir+"/"+PRESETS)
                
                # pass in all files to copy them (doing the simple installation):
                for sourceDir, dirList, fileList in os.walk(dpAR_TempDir):       
                    # declare destination directory:
                    destDir = sourceDir.replace(dpAR_TempDir, dpAR_DestFolder, 1).replace("\\", "/")
                    
                    installAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + `installAmount`))
                    
                    # make sure we have all folders needed, otherwise, create them in the destination directory:
                    if not os.path.exists(destDir):
                        os.makedirs(destDir)
                    
                    for dpAR_File in fileList:
                        sourceFile = os.path.join(sourceDir, dpAR_File).replace("\\", "/")
                        destFile = os.path.join(destDir, dpAR_File).replace("\\", "/")
                        # if the file exists (we expect that yes) then delete it:
                        if os.path.exists(destFile):
                            try:
                                os.remove(destFile)
                            except PermissionError as exc:
                                # use a brute force to delete without permission:
                                os.chmod(destFile, stat.S_IWUSR)
                                os.remove(destFile)
                        # copy the dpAR_File:
                        shutil.copy2(sourceFile, destDir)
                        
                        installAmount += 1
                        cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + `installAmount`))
                
                # delete the temporary folder used to download and install the update:
                folderToDelete = dpAR_DestFolder+"/"+zipNameList[0]
                shutil.rmtree(folderToDelete)
                
                # report finished update installation:
                self.info('i095_installUpdate', 'i099_installed', '\n\n'+newVersion+'\n\n'+self.langDic[self.langName]['i173_reloadScript']+'\n\n'+self.langDic[self.langName]['i018_thanks'], 'center', 205, 270)
                # closes dpUpdateWindow:
                if cmds.window('dpUpdateWindow', query=True, exists=True):
                    cmds.deleteUI('dpUpdateWindow', window=True)
                # quit UI in order to force user to refresh dpAutoRigSystem creating a new instance:
                self.deleteExistWindow()
            except:
                # report fail update installation:
                self.info('i095_installUpdate', 'e010_failInstallUpdate', '\n\n'+newVersion+'\n\n'+self.langDic[self.langName]['i097_sorry'], 'center', 205, 270)
            cmds.progressWindow(endProgress=True)
        else:
            print self.langDic[self.langName]['i038_canceled']
    
    
    def setAutoCheckUpdatePref(self, currentValue, *args):
        """ Set the optionVar for auto check update preference as stored userDefAutoCheckUpdate read variable.
        """
        cmds.optionVar(intValue=('dpAutoRigAutoCheckUpdate', int(currentValue)))
    
    
    def autoCheckUpdate(self, *args):
        """ Store user choose about automatically check for update in an optionVar.
            If active, try to check for update once a day.
        """
        firstTimeOpenDPAR = False
        # verify if there is an optionVar of last autoCheckUpdate checkBox choose value by user in the maya system:
        autoCheckUpdateExists = cmds.optionVar(exists='dpAutoRigAutoCheckUpdate')
        if not autoCheckUpdateExists:
            cmds.optionVar(intValue=('dpAutoRigAutoCheckUpdate', 1))
            firstTimeOpenDPAR = True
        
        # get its value puting in a variable userDefAutoCheckUpdate:
        self.userDefAutoCheckUpdate = cmds.optionVar(query='dpAutoRigAutoCheckUpdate')
        if self.userDefAutoCheckUpdate == 1:
            # verify if there is an optionVar for store the date of the lastest autoCheckUpdate ran in order to avoid many hits in the GitHub server:
            todayDate = str(datetime.datetime.now().date())
            lastAutoCheckUpdateExists = cmds.optionVar(exists='dpAutoRigLastDateAutoCheckUpdate')
            if not lastAutoCheckUpdateExists:
                cmds.optionVar(stringValue=('dpAutoRigLastDateAutoCheckUpdate', todayDate))
            # get its value puting in a variable userDefAutoCheckUpdate:
            lastDateAutoCheckUpdate = cmds.optionVar(query='dpAutoRigLastDateAutoCheckUpdate')
            if not lastDateAutoCheckUpdate == todayDate:
                # then check for update:
                self.checkForUpdate(verbose=False)
                cmds.optionVar(stringValue=('dpAutoRigLastDateAutoCheckUpdate', todayDate))
        
        # force checkForUpdate if it's the first time openning the dpAutoRigSystem in this computer:
        if firstTimeOpenDPAR:
            self.checkForUpdate(verbose=True)
        
        
    
    
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
    def getBaseCtrl(self, sCtrlType, sAttrName, sCtrlName, fRadius, iDegree = 1, iSection = 8):
        nCtrl = None
        self.ctrlCreated = False
        try:
            nCtrl= self.masterGrp.getAttr(sAttrName)
        except pymel.MayaAttributeError:
            try:
                nCtrl = pymel.PyNode(self.prefix + sCtrlName)
            except pymel.MayaNodeError:
                if (sCtrlName != (self.prefix + "Option_Ctrl")):
                    nCtrl = pymel.PyNode(self.ctrls.cvControl(sCtrlType, sCtrlName, r=fRadius, d=iDegree, dir="+X"))
                else:
                    nCtrl = pymel.PyNode(self.ctrls.cvCharacter(sCtrlType, sCtrlName, r=(fRadius*0.2)))
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
            # system:
            self.masterGrp.setDynamicAttr("maya", cmds.about(version=True))
            self.masterGrp.setDynamicAttr("system", "dpAutoRig_"+DPAR_VERSION)
            self.masterGrp.setDynamicAttr("language", self.langName)
            self.masterGrp.setDynamicAttr("preset", self.presetName)
            # author:
            self.masterGrp.setDynamicAttr("author", getpass.getuser())
            # rig info to be updated:
            self.masterGrp.setDynamicAttr("geometryList", "")
            self.masterGrp.setDynamicAttr("controlList", "")

        # add date data log:
        self.masterGrp.setDynamicAttr("lastModification", localTime)
        
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
        self.blendShapesGrp = self.getBaseGrp("blendShapesGrp", self.prefix+"BlendShapes_Grp")
        self.wipGrp         = self.getBaseGrp("wipGrp", self.prefix+"WIP_Grp")

        #Arrange Hierarchy if using an original setup or preserve existing if integrating to another studio setup
        if self.masterGrp.__melobject__() == sAllGrp:
            pymel.parent(self.modelsGrp, self.ctrlsGrp, self.dataGrp, self.renderGrp, self.proxyGrp, self.fxGrp, self.masterGrp)
            pymel.parent(self.staticGrp, self.scalableGrp, self.blendShapesGrp, self.wipGrp, self.dataGrp)
        pymel.select(None)

        #Hide Models and FX groups
        try:
            pymel.setAttr(self.modelsGrp.visibility, 0)
            pymel.setAttr(self.fxGrp.visibility, 0)
        except:
            pass

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
        self.ctrls.setLockHide(aToLock, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        #Control Setup
        fMasterRadius = self.ctrls.dpCheckLinearUnit(10)
        self.masterCtrl = self.getBaseCtrl("id_004_Master", "masterCtrl", self.prefix+"Master_Ctrl", fMasterRadius, iDegree=3)
        if (self.ctrlCreated):
#            self.masterCtrl.setDynamicAttr("masterCtrl", True)
            self.masterCtrl.rotateOrder.set(3)

        self.globalCtrl = self.getBaseCtrl("id_003_Global", "globalCtrl", self.prefix+"Global_Ctrl", self.ctrls.dpCheckLinearUnit(13), iSection=4)
        if (self.ctrlCreated):
            self.globalCtrl.rotateOrder.set(3)

        self.rootCtrl   = self.getBaseCtrl("id_005_Root", "rootCtrl", self.prefix+"Root_Ctrl", self.ctrls.dpCheckLinearUnit(8))
        if (self.ctrlCreated):
            self.rootCtrl.rotateOrder.set(3)

        self.optionCtrl = self.getBaseCtrl("id_006_Option", "optionCtrl", self.prefix+"Option_Ctrl", self.ctrls.dpCheckLinearUnit(16))
        if (self.ctrlCreated):
            pymel.makeIdentity(self.optionCtrl, apply=True)
            self.optionCtrlGrp = pymel.PyNode(utils.zeroOut([self.optionCtrl.__melobject__()])[0])
            self.optionCtrlGrp.translateX.set(fMasterRadius)
            # use Option_Ctrl rigScale and rigScaleMultiplier attribute to Master_Ctrl
            self.rigScaleMD = pymel.createNode("multiplyDivide", name=self.prefix+'RigScale_MD')
            self.rigScaleMD.addAttr("dpRigScale", at="bool")
            self.rigScaleMD.setDynamicAttr('dpRigScale', True)
            pymel.connectAttr(self.optionCtrl.rigScale, self.rigScaleMD.input1X, force=True)
            pymel.connectAttr(self.optionCtrl.rigScaleMultiplier, self.rigScaleMD.input2X, force=True)
            pymel.connectAttr(self.rigScaleMD.outputX, self.masterCtrl.scaleX, force=True)
            pymel.connectAttr(self.rigScaleMD.outputX, self.masterCtrl.scaleY, force=True)
            pymel.connectAttr(self.rigScaleMD.outputX, self.masterCtrl.scaleZ, force=True)
            # comment to avoid double transformation for tweaks using indirect skinning:
            #pymel.connectAttr(self.rigScaleMD.outputX, self.scalableGrp.scaleX, force=True)
            #pymel.connectAttr(self.rigScaleMD.outputX, self.scalableGrp.scaleY, force=True)
            #pymel.connectAttr(self.rigScaleMD.outputX, self.scalableGrp.scaleZ, force=True)
            self.ctrls.setLockHide([self.masterCtrl.__melobject__()], ['sx', 'sy', 'sz'])
            self.ctrls.setNonKeyable([self.optionCtrl.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        else:
            self.optionCtrlGrp = self.optionCtrl.getParent()
            self.rigScaleMD = self.prefix+'RigScale_MD'

        pymel.parent(self.rootCtrl, self.masterCtrl)
        pymel.parent(self.masterCtrl, self.globalCtrl)
        pymel.parent(self.globalCtrl, self.ctrlsGrp)
        pymel.parent(self.optionCtrlGrp, self.rootCtrl)
        pymel.parent(self.ctrlsVisGrp, self.rootCtrl)

        # set lock and hide attributes (cmds function):
        self.ctrls.setLockHide([self.scalableGrp.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])
        self.ctrls.setLockHide([self.rootCtrl.__melobject__(), self.globalCtrl.__melobject__()], ['sx', 'sy', 'sz', 'v'])

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
            self.ctrls.setLockHide([self.baseRootJnt.__melobject__(), self.baseRootJntGrp.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

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
        
        
    def reorderAttributes(self, objList, attrList, *args):
        """ Reorder Attributes of a given objectList following the desiredAttribute list.
            Useful for organize the Option_Ctrl attributes, for example.
        """
        if objList and attrList:
            for obj in objList:
                # load dpReorderAttribute:
                dpRAttr = dpReorderAttr.ReorderAttr(self, self.langDic, self.langName, False)
                # Reordering Option_Ctrl attributos progress window
                progressAmount = 0
                cmds.progressWindow(title='Reordering Attributes', progress=progressAmount, status='Reordering: 0%', isInterruptable=False)
                nbDesAttr = len(attrList)
                delta = 0
                for i, desAttr in enumerate(attrList):
                    # update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=nbDesAttr, progress=progressAmount, status=('Reordering: ' + `progressAmount` + ' '+ obj + ' attributes'))
                    # get current user defined attributes:
                    currentAttrList = cmds.listAttr(obj, userDefined=True)
                    if desAttr in currentAttrList:
                        cAttrIndex = currentAttrList.index(desAttr)
                        maxRange = cAttrIndex+1-i+delta
                        for n in range(1, maxRange):
                            dpRAttr.dpMoveAttr(1, [obj], [desAttr])
                    else:
                        delta = delta+1
                cmds.progressWindow(endProgress=True)
                dpRAttr.dpCloseReorderAttrUI()


    def rigAll(self, integrate=None, *args):
        """ Create the RIG based in the Guide Modules in the scene.
            Most important function to automate the proccess.
        """
        print('\ndpAutoRigSystem Log: ' + self.langDic[self.langName]['i178_startRigging'] + '...\n'),
        # force refresh in order to avoid calculus error is creating Rig at the same time of guides:
        cmds.refresh()
        
        # get a list of modules to be rigged and re-declare the riggedModuleDic to store for log in the end:
        self.modulesToBeRiggedList = utils.getModulesToBeRigged(self.moduleInstancesList)
        self.riggedModuleDic = {}
        
        # declare a list to store all integrating information:
        self.integratedTaskDic = {}
        
        # verify if there are instances of modules (guides) to rig in the scene:
        if self.modulesToBeRiggedList:
            
            # check guide versions to be sure we are building with the same dpAutoRigSystem version:
            for guideModule in self.modulesToBeRiggedList:
                guideVersion = cmds.getAttr(guideModule.moduleGrp+'.dpARVersion')
                if not guideVersion == DPAR_VERSION:
                    btYes = self.langDic[self.langName]['i071_yes']
                    btNo = self.langDic[self.langName]['i072_no']
                    userChoose = cmds.confirmDialog(title='dpAutoRigSystem - v'+DPAR_VERSION, message=self.langDic[self.langName]['i127_guideVersionDif'], button=[btYes, btNo], defaultButton=btYes, cancelButton=btNo, dismissString=btNo)
                    if userChoose == btNo:
                        return
                    else:
                        break
            
            # Starting progress window
            rigProgressAmount = 0
            cmds.progressWindow(title='dpAutoRigSystem', progress=rigProgressAmount, status='Rigging : 0%', isInterruptable=False)
            maxProcess = len(self.modulesToBeRiggedList)
            
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

            #Check if we need to colorize the self.ctrls
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
                
                # Update progress window
                rigProgressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=rigProgressAmount, status=('Rigging : ' + `rigProgressAmount` + ' '+str(guideModuleCustomName)))
                
                # Rig it :)
                guideModule.rigModule()
                # get rigged module name:
                self.riggedModuleDic[guideModule.moduleGrp.split(":")[0]] = guideModuleCustomName
                # get integrated information:
                if guideModule.integratedActionsDic:
                    self.integratedTaskDic[guideModule.moduleGrp] = guideModule.integratedActionsDic["module"]
            
            if integrate == 1:
                # Update progress window
                rigProgressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=rigProgressAmount, status=('Rigging : ' + `rigProgressAmount` + ' '+self.langDic[self.langName]['i010_integrateCB']))
                
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
                if self.integratedTaskDic:
                    # working with specific cases:
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
                                    revFootCtrlGrp   = self.integratedTaskDic[moduleDic]['revFootCtrlGrpList'][s]
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
                                    limbTypeName          = self.integratedTaskDic[fatherGuide]['limbTypeName']
                                    ikFkNetworkList       = self.integratedTaskDic[fatherGuide]['ikFkNetworkList']
                                    worldRefList          = self.integratedTaskDic[fatherGuide]['worldRefList'][s]
                                    # do task actions in order to integrate the limb and foot:
                                    cmds.cycleCheck(evaluation=False)
                                    cmds.delete(ikHandlePointConst, parentConst, scaleConst) #there's an undesirable cycleCheck evaluation error here when we delete ikHandlePointConst!
                                    cmds.cycleCheck(evaluation=True)
                                    cmds.parent(revFootCtrlGrp, ikFkBlendGrpToRevFoot, absolute=True)
                                    cmds.parent(ikHandleGrp, toLimbIkHandleGrp, absolute=True)
                                    #Delete the old constraint (two line before) and recreate them on the extrem joint on the limb
                                    cmds.parentConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_ParentConstraint")[0]
                                    #cmds.scaleConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_ScaleConstraint")[0]
                                    if limbTypeName == LEG:
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
                                    floatAttrList = cmds.listAttr(revFootCtrl, visible=True, scalar=True, keyable=True, userDefined=True)
                                    for floatAttr in floatAttrList:
                                        if not cmds.objExists(ikCtrl+'.'+floatAttr):
                                            cmds.addAttr(ikCtrl, longName=floatAttr, attributeType='float', keyable=True)
                                            cmds.connectAttr(ikCtrl+'.'+floatAttr, revFootCtrl+'.'+floatAttr, force=True)
                                    intAttrList = cmds.listAttr(revFootCtrl, visible=True, scalar=True, keyable=False, userDefined=True)
                                    for intAttr in intAttrList:
                                        if not cmds.objExists(ikCtrl+'.'+intAttr):
                                            cmds.addAttr(ikCtrl, longName=intAttr, attributeType='long', min=0, max=1, defaultValue=1)
                                            cmds.setAttr(ikCtrl+"."+intAttr, keyable=False, channelBox=True)
                                            cmds.connectAttr(ikCtrl+'.'+intAttr, revFootCtrl+'.'+intAttr, force=True)
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
                                floatAttrList = cmds.listAttr(worldRef, visible=True, scalar=True, keyable=True, userDefined=True)
                                for f, floatAttr in enumerate(floatAttrList):
                                    if f < len(floatAttrList):
                                        if not cmds.objExists(self.optionCtrl+'.'+floatAttr):
                                            currentValue = cmds.getAttr(worldRef+'.'+floatAttr)
                                            if floatAttr == lvvAttr:
                                                cmds.addAttr(self.optionCtrl, longName=floatAttr, attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), defaultValue=currentValue, keyable=True)
                                            else:
                                                cmds.addAttr(self.optionCtrl, longName=floatAttr, attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), minValue=0, maxValue=1, defaultValue=currentValue, keyable=True)
                                        cmds.connectAttr(self.optionCtrl+'.'+floatAttr, worldRef+'.'+floatAttr, force=True)
                                if not cmds.objExists(self.optionCtrl+'.'+floatAttrList[len(floatAttrList)-1]):
                                    cmds.addAttr(self.optionCtrl, longName=floatAttrList[len(floatAttrList)-1], attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), defaultValue=1, keyable=True)
                                    cmds.connectAttr(self.optionCtrl+'.'+floatAttrList[len(floatAttrList)-1], worldRef+'.'+floatAttrList[len(floatAttrList)-1], force=True)
                                cmds.connectAttr(self.masterCtrl+".scaleX", worldRef+".scaleX", force=True)
                                bendAttrList = ["bends", "extraBends"]
                                for bendAttr in bendAttrList:
                                    if cmds.objExists(self.optionCtrl+"."+bendAttr):
                                        cmds.setAttr(self.optionCtrl+"."+bendAttr, keyable=False, channelBox=True)
                                
                                # update ikFkNetwork:
                                if ikFkNetworkList:
                                    netIndex = 1
                                    optionCtrlAttrList = cmds.listAttr(self.optionCtrl, visible=True, scalar=True, keyable=True)
                                    for optAttr in optionCtrlAttrList:
                                        if "_IkFkBlend" in optAttr:
                                            cmds.connectAttr(self.optionCtrl+'.'+optAttr, ikFkNetworkList[w]+'.attState', force=True)
                                    limbAttrList = cmds.listAttr(ikCtrlList[w], visible=True, scalar=True, keyable=True, userDefined=True)
                                    for limbAttr in limbAttrList:
                                        if "_" in limbAttr:
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
                                    limbTypeName         = self.integratedTaskDic[moduleDic]['limbTypeName']
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
                                        targetList = cmds.parentConstraint(limbIsolateFkConst, query=True, targetList=True)
                                        weightList = cmds.parentConstraint(limbIsolateFkConst, query=True, weightAliasList=True)
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
                                        fkCtrl = fkZeroNode.replace("_Zero_Grp", "")
                                        nodeToConst = utils.zeroOut([fkCtrl])[0]
                                        nodeToConst = cmds.rename(nodeToConst, fkCtrl + "_SpaceSwitch_Grp")
                                        mainCtrl = cmds.listConnections(revNode + ".inputX")[0]
                                        mainNull = sideName + mainParent +"_Null"  #Ensure the name is set to prevent unbound variable problem with inner function
                                        #Replace the old constraint with a new one that will switch with the chest ctrl
                                        cmds.delete(limbIsolateFkConst, inputConnectionsAndNodes=False, constraints=True)
                                        #cmds.parentConstraint(targetList[1], limbIsolateFkConst, rm=True)
                                        if (not cmds.objExists(mainNull)):
                                            mainNull = cmds.group(empty=True, name=mainNull)
                                            cmds.parent(mainNull, mainParent, relative=False)
                                            m4Fk = cmds.xform(fkCtrl, worldSpace=True, matrix=True, query=True)
                                            cmds.xform(mainNull, worldSpace=True, matrix=m4Fk)
                                        newFkConst = cmds.parentConstraint(targetList[0], mainNull, nodeToConst, skipTranslate=["x", "y", "z"], maintainOffset=True, name=nodeToConst+"_ParentConstraint")[0]
                                        cmds.connectAttr(mainCtrl + "." + self.langDic[self.langName]['c032_follow'], newFkConst + "." + targetList[0]+"W0", force=True)
                                        if (cmds.objExists(revNode)):
                                            cmds.connectAttr(revNode + ".outputX", newFkConst + "." + mainNull+"W1", force=True)
                                        else:
                                            revNode = cmds.createNode('reverse', name=sideName+fkCtrl+"_FkIsolate_Rev")
                                            cmds.connectAttr(mainCtrl+'.'+self.langDic[self.langName]['c032_follow'], revNode+".inputX", force=True)
                                            cmds.connectAttr(revNode + ".outputX", newFkConst + "." + mainNull+"W1", force=True)

                                    # verifying what part will be used, the hips or chest:
                                    if limbTypeName == LEG:
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
                            
                        # integrate the volumeVariation and ikFkBlend attributes from Spine module to optionCtrl:
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
                                ikFkBlendAttr = self.integratedTaskDic[moduleDic]['IkFkBlendAttrList'][s]
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
                                cmds.addAttr(self.optionCtrl, longName=ikFkBlendAttr, attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                                cmds.connectAttr(self.optionCtrl+'.'+ikFkBlendAttr, hipsA+'.'+ikFkBlendAttr)
                                cmds.setAttr(hipsA+'.'+ikFkBlendAttr, keyable=False)
                                if bColorize:
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['InnerCtrls'][s], "cyan")
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['OuterCtrls'][s], "yellow")
                        
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
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['ctrlList'][s], "yellow")
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['lCtrls'][s], "red")
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['rCtrls'][s], "blue")
                        
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
                                cmds.connectAttr(eyeCtrl+'.'+self.langDic[self.langName]['c032_follow'], eyeRevNode+".inputX", force=True)
                                cmds.connectAttr(eyeRevNode+".outputX", headParentConst+"."+self.rootCtrl+"W0", force=True)
                                cmds.connectAttr(eyeCtrl+'.'+self.langDic[self.langName]['c032_follow'], headParentConst+"."+headCtrl+"W1", force=True)
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
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            self.itemGuideMirrorAxis = self.hookDic[moduleDic]['guideMirrorAxis']
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                if self.integratedTaskDic[moduleDic]['hasIris']:
                                    irisCtrl = self.integratedTaskDic[moduleDic]['irisCtrl'][s]
                                    self.ctrls.colorShape([irisCtrl], "cyan")
                                if self.integratedTaskDic[moduleDic]['hasPupil']:
                                    pupilCtrl = self.integratedTaskDic[moduleDic]['pupilCtrl'][s]
                                    self.ctrls.colorShape([pupilCtrl], "black")
                        
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
                                Release node MAYA-45759 https://download.autodesk.com/us/support/files/maya_2016/Maya%202016%20Release%20Notes_enu.htm
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
                                    limbTypeName = self.integratedTaskDic[fatherGuide]['limbTypeName']
                                    if limbTypeName == ARM:
                                        origFromList = self.integratedTaskDic[fatherGuide]['integrateOrigFromList'][s]
                                        origFrom = origFromList[-1]
                                        cmds.parentConstraint(origFrom, scalableGrp, maintainOffset=True)
                
                        # integrate the Single module with another Single as a father:
                        if moduleType == SINGLE:
                            # connect Option_Ctrl display attribute to the visibility:
                            if not cmds.objExists(self.optionCtrl+"."+self.langDic[self.langName]['m081_tweaks']):
                                cmds.addAttr(self.optionCtrl, longName=self.langDic[self.langName]['m081_tweaks'], min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                                cmds.setAttr(self.optionCtrl+"."+self.langDic[self.langName]['m081_tweaks'], channelBox=True)
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                ctrlGrp = self.integratedTaskDic[moduleDic]["ctrlGrpList"][s]
                                cmds.connectAttr(self.optionCtrl+"."+self.langDic[self.langName]['m081_tweaks'], ctrlGrp+".visibility", force=True)
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
                                    
                        # integrate the Wheel module with another Option_Ctrl:
                        if moduleType == WHEEL:
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                wheelCtrl = self.integratedTaskDic[moduleDic]["wheelCtrlList"][s]
                                # connect Option_Ctrl RigScale_MD output to the radiusScale:
                                if cmds.objExists(self.rigScaleMD+".dpRigScale") and cmds.getAttr(self.rigScaleMD+".dpRigScale") == True:
                                    cmds.connectAttr(self.rigScaleMD+".outputX", wheelCtrl+".radiusScale", force=True)
                                # get father module:
                                fatherModule   = self.hookDic[moduleDic]['fatherModule']
                                if fatherModule == STEERING:
                                    # getting Steering data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    try:
                                        steeringCtrl  = self.integratedTaskDic[fatherGuide]['steeringCtrlList'][s]
                                    except:
                                        steeringCtrl  = self.integratedTaskDic[fatherGuide]['steeringCtrlList'][0]
                                    # connect modules to be integrated:
                                    cmds.connectAttr(steeringCtrl+'.'+self.langDic[self.langName]['c070_steering'], wheelCtrl+'.'+self.langDic[self.langName]['i037_to']+self.langDic[self.langName]['c070_steering'].capitalize(), force=True)
                                    # reparent wheel module:
                                    wheelHookCtrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][s]
                                    cmds.parent(wheelHookCtrlGrp, self.ctrlsVisGrp)
                        
                        # integrate the Suspension module with Wheel:
                        if moduleType == SUSPENSION:
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                loadedFatherB = self.integratedTaskDic[moduleDic]['fatherBList'][s]
                                if loadedFatherB:
                                    suspensionBCtrlGrp = self.integratedTaskDic[moduleDic]['suspensionBCtrlGrpList'][s]
                                    # find the correct fatherB node in order to parent the B_Ctrl:
                                    if "__" in loadedFatherB and ":" in loadedFatherB: # means we need to parent to a rigged guide
                                        # find fatherB module dic:
                                        fatherBNamespace = loadedFatherB[:loadedFatherB.find(":")]
                                        for hookItem in self.hookDic:
                                            if self.hookDic[hookItem]['guideModuleNamespace'] == fatherBNamespace:
                                                # got father module dic:
                                                fatherBModuleDic = hookItem
                                                self.fatherBGuideMirrorAxis     = self.hookDic[fatherBModuleDic]['guideMirrorAxis']
                                                self.fatherBGuideMirrorNameList = self.hookDic[fatherBModuleDic]['guideMirrorName']
                                                self.fatherBCustomName          = self.hookDic[fatherBModuleDic]['guideCustomName']
                                                self.fatherBGuideInstance       = self.hookDic[fatherBModuleDic]['guideInstance']
                                                # working with fatherB guide mirror:
                                                self.fatherBMirrorNameList = [""]
                                                # get itemGuideName:
                                                if self.fatherBGuideMirrorAxis != "off":
                                                    self.fatherBMirrorNameList = self.fatherBGuideMirrorNameList
                                                for fB, fBSideName in enumerate(self.fatherBMirrorNameList):
                                                    if self.fatherBCustomName:
                                                        fatherB = fBSideName + self.prefix + self.fatherBCustomName + "_" + loadedFatherB[loadedFatherB.rfind(":")+1:]
                                                    else:
                                                        fatherB = fBSideName + self.prefix + self.fatherBGuideInstance + "_" + loadedFatherB[loadedFatherB.rfind(":")+1:]
                                                    fatherBRiggedNode = self.originedFromDic[fatherB]
                                                    if cmds.objExists(fatherBRiggedNode):
                                                        if len(self.fatherBMirrorNameList) > 1: #means fatherB has mirror
                                                            if s == fB:
                                                                cmds.parentConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ParentConstraint")
                                                                cmds.scaleConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScaleConstraint")
                                                        else:
                                                            cmds.parentConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ParentConstraint")
                                                            cmds.scaleConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScaleConstraint")
                                    else: # probably we will parent to a control curve already generated and rigged before
                                        if cmds.objExists(loadedFatherB):
                                            cmds.parentConstraint(loadedFatherB, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ParentConstraint")
                                            cmds.scaleConstraint(loadedFatherB, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScaleConstraint")
                                # get father module:
                                fatherModule = self.hookDic[moduleDic]['fatherModule']
                                if fatherModule == WHEEL:
                                    # getting spine data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    # parent suspension control group to wheel Main_Ctrl
                                    suspensionHookCtrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][s]
                                    wheelMainCtrl = self.integratedTaskDic[fatherGuide]['mainCtrlList'][s]
                                    cmds.parentConstraint(wheelMainCtrl, suspensionHookCtrlGrp, maintainOffset=True, name=suspensionHookCtrlGrp+"_ParentConstraint")
                                    cmds.scaleConstraint(wheelMainCtrl, suspensionHookCtrlGrp, maintainOffset=True, name=suspensionHookCtrlGrp+"_ScaleConstraint")
                
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
        
            # Close progress window
            cmds.progressWindow(endProgress=True)
        
            #Actualise all controls (All_Grp.controlList) for this rig:
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
                            self.ctrls.colorShape([pCtrl.__melobject__()], "red")
                        elif (rPattern.match(pCtrl.name())):
                            self.ctrls.colorShape([pCtrl.__melobject__()], "blue")
                        elif (pCtrl in aBCtrl):
                            self.ctrls.colorShape([pCtrl.__melobject__()], "black")
                        else:
                            self.ctrls.colorShape([pCtrl.__melobject__()], "yellow")

            # Add usefull attributes for the animators
            if (bAddAttr):
                pOptCtrl = pymel.PyNode(self.optionCtrl)
                pRenderGrp = pymel.PyNode(self.renderGrp)
                pCtrlVisGrp = pymel.PyNode(self.ctrlsVisGrp)
                pProxyGrp = pymel.PyNode(self.proxyGrp)
                
                # defining attribute name strings:
                generalAttr = self.langDic[self.langName]['c066_general']
                vvAttr = self.langDic[self.langName]['c031_volumeVariation']
                spineAttr = self.langDic[self.langName]['m011_spine']
                limbAttr = self.langDic[self.langName]['m019_limb'].lower()
                armAttr = self.langDic[self.langName]['m028_arm']
                legAttr = self.langDic[self.langName]['m030_leg']
                frontAttr = self.langDic[self.langName]['c056_front']
                backAttr = self.langDic[self.langName]['c057_back']
                leftAttr = self.langDic[self.langName]['p002_left'].lower()
                rightAttr = self.langDic[self.langName]['p003_right'].lower()
                tweaksAttr = self.langDic[self.langName]['m081_tweaks'].lower()
                
                if not pymel.hasAttr(pOptCtrl, generalAttr):
                    pymel.addAttr(pOptCtrl, ln=generalAttr, at="enum", enumName="----------", keyable=True)
                    pymel.setAttr(pOptCtrl+"."+generalAttr, lock=True)
                
                # Only create if a VolumeVariation attribute is found
                if not pymel.hasAttr(pOptCtrl, vvAttr):
                    if (pOptCtrl.listAttr(string="*"+vvAttr+"*")):
                        pymel.addAttr(pOptCtrl, ln=vvAttr, at="enum", enumName="----------", keyable=True)
                        pymel.setAttr(pOptCtrl+"."+vvAttr, lock=True)
                
                # Only create if a IkFk attribute is found
                if not pymel.hasAttr(pOptCtrl, "ikFkBlend"):
                    if (pOptCtrl.listAttr(string="*ikFk*")):
                        pymel.addAttr(pOptCtrl, ln="ikFkBlend", at="enum", enumName="----------", keyable=True)
                        pymel.setAttr(pOptCtrl.ikFkBlend, lock=True)
                
                if not pymel.hasAttr(pOptCtrl, "display"):
                    pymel.addAttr(pOptCtrl, ln="display", at="enum", enumName="----------", keyable=True)
                    pymel.setAttr(pOptCtrl.display, lock=True)
                
                if not pymel.hasAttr(pOptCtrl, "mesh"):
                    pymel.addAttr(pOptCtrl, ln="mesh", min=0, max=1, defaultValue=1, attributeType="long", keyable=True)
                    pymel.connectAttr(pOptCtrl.mesh, pRenderGrp.visibility, force=True)
                
                if not pymel.hasAttr(pOptCtrl, "proxy"):
                    pymel.addAttr(pOptCtrl, ln="proxy", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                    pymel.connectAttr(pOptCtrl.proxy, pProxyGrp.visibility, force=True)
                    #pymel.setAttr(pOptCtrl.proxy, channelBox=True)
                
                if not pymel.hasAttr(pOptCtrl, "control"):
                    pymel.addAttr(pOptCtrl, ln="control", min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                    pymel.connectAttr(pOptCtrl.control, pCtrlVisGrp.visibility, force=True)
                    pymel.setAttr(pOptCtrl.control, channelBox=True)
                
                # try to organize Option_Ctrl attributes:
                # get current user defined attributes:
                currentAttrList = cmds.listAttr(self.optionCtrl, userDefined=True)
                # clean up "_ikFkBlend" atributes:
                if currentAttrList:
                    for cAttr in currentAttrList:
                        if cAttr.endswith("_ikFkBlend"):
                            if not cmds.objExists(self.optionCtrl+"."+cAttr[:cAttr.find("_ikFkBlend")]):
                                cmds.renameAttr(self.optionCtrl+"."+cAttr, cAttr[:cAttr.find("_ikFkBlend")])
                # clean up "VolumeVariation" attributes:
                if currentAttrList:
                    for cAttr in currentAttrList:
                        if cAttr.endswith("_"+vvAttr):
                            if not cmds.objExists(self.optionCtrl+"."+cAttr[:cAttr.find("_"+vvAttr)]):
                                cmds.renameAttr(self.optionCtrl+"."+cAttr, cAttr[:cAttr.find("_"+vvAttr)])
                            
                # list desirable Option_Ctrl attributes order:
                desiredAttrList = [generalAttr, 'rigScale', 'rigScaleMultiplier', 'globalStretch', vvAttr,
                spineAttr+'_active', spineAttr, spineAttr+'1_active', spineAttr+'1', spineAttr+'2_active', spineAttr+'2',
                limbAttr, limbAttr+'Min', limbAttr+'Manual', 'ikFkBlend', spineAttr+'Fk', spineAttr+'1Fk', spineAttr+'Fk2', 
                leftAttr+spineAttr+'Fk', rightAttr+spineAttr+'Fk', leftAttr+spineAttr+'Fk1', rightAttr+spineAttr+'Fk1', leftAttr+spineAttr+'Fk2', rightAttr+spineAttr+'Fk2',
                armAttr, legAttr, leftAttr+armAttr, rightAttr+armAttr,
                leftAttr+legAttr, rightAttr+legAttr, leftAttr+legAttr+frontAttr, rightAttr+legAttr+frontAttr, leftAttr+legAttr+backAttr, rightAttr+legAttr+backAttr,
                armAttr+'1', legAttr+'1', leftAttr+armAttr+'1', rightAttr+armAttr+'1', leftAttr+legAttr+'1', rightAttr+legAttr+'1',
                leftAttr+legAttr+frontAttr+'1', rightAttr+legAttr+frontAttr+'1', leftAttr+legAttr+backAttr+'1', rightAttr+legAttr+backAttr+'1',
                'display', 'mesh', 'proxy', 'control', 'bends', 'extraBends', tweaksAttr]
                # call method to reorder Option_Ctrl attributes:
                self.reorderAttributes([self.optionCtrl], desiredAttrList)
                
            #Try add hand follow (space switch attribute) on bipeds:
            self.initExtraModule("dpAddHandFollow", EXTRAS)
            
            # show dialogBox if detected a bug:
            if integrate == 1:
                if self.detectedBug:
                    print "\n\n"
                    print self.bugMessage
                    cmds.confirmDialog(title=self.langDic[self.langName]['i078_detectedBug'], message=self.bugMessage, button=["OK"])

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
                        baseName = utils.extractSuffix(geomSkin)
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)
                print self.langDic[self.langName]['i077_skinned'] + ', '.join(geomSkinList),
        else:
            print self.langDic[self.langName]['i029_skinNothing'],

    ###################### End: Skinning.
