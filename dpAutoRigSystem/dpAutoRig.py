#!/usr/bin/env python3

###################################################################
#
#    dpAutoRigSystem Free Open Source Python Script for Maya
#
#    author:  Danilo Pinheiro
#
#    contact: nilouco@gmail.com
#             https://nilouco.blogspot.com
#
#    GitHub, Wiki:
#             https://github.com/nilouco/dpAutoRigSystem
#
#    Dev Sheet, Collaborators, Logs:
#             https://docs.google.com/spreadsheets/d/154HoO-bLApA7CKpIJ1bDwSxRF146Kyo2etmHDUJGdiw
#
###################################################################


DPAR_VERSION_PY3 = "4.04.26"
DPAR_UPDATELOG = "N790 - Rebuilder."



###################### Start: Loading.

import os
import random
from maya import cmds

def clearDPARLoadingWindow():
    if cmds.window('dpARLoadWin', query=True, exists=True):
        cmds.deleteUI('dpARLoadWin', window=True)

def dpARLoadingWindow():
    """ Just create a Loading window in order to show we are working to user when calling dpAutoRigSystem.
    """
    loadingString = "Loading dpAutoRigSystem v%s ... " %DPAR_VERSION_PY3
    print(loadingString)
    path = os.path.dirname(__file__)
    randImage = random.randint(0,7)
    clearDPARLoadingWindow()
    cmds.window('dpARLoadWin', title='dpAutoRigSystem', iconName='dpAutoRig', widthHeight=(285, 203), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
    cmds.columnLayout('dpARLoadLayout')
    cmds.image('loadingImage', image=(path+"/Icons/dp_loading_0%i.png" %randImage), backgroundColor=(0.8, 0.8, 0.8), parent='dpARLoadLayout')
    cmds.text('versionText', label=loadingString, parent='dpARLoadLayout')
    cmds.showWindow('dpARLoadWin')
    cmds.window('dpARLoadWin', edit=True, widthHeight=(285, 203))

dpARLoadingWindow()

###################### End: Loading.


###################### Start: Download master.

def dpARDownloadMaster():
    """ Help user to download a dpAutoRigSystem master file from GitHub to reinstall it
    """
    confirm = cmds.confirmDialog(title="Reinstall", message="There's an unexpected issue, sorry!\nPlease reinstall the dpAutoRigSystem.\nRemember to delete the current folder before install a new one from:\n\nhttps://github.com/nilouco/dpAutoRigSystem/zipball/master/", button="Download", dismissString="No")
    if confirm == "Download":
        if os.name == "nt":
            DOWNLOAD_FOLDER = f"{os.getenv('USERPROFILE')}\\Downloads"
        else:  # PORT: For *Nix systems
            DOWNLOAD_FOLDER = f"{os.getenv('HOME')}/Downloads"
        urllib.request.urlretrieve("https://github.com/nilouco/dpAutoRigSystem/zipball/master/", DOWNLOAD_FOLDER+"/dpAutoRigSystem-master.zip")

###################### End: Download master.


# importing libraries:
try:
    import json
    import re
    import time
    import getpass
    import urllib.request
    import shutil
    import zipfile
    import datetime
    import io
    import sys
    import socket
    import platform
    from maya import mel
    from functools import partial
    from .Modules.Library import dpUtils
    from .Modules.Library import dpControls
    from .Modules import dpBaseClass
    from .Modules import dpLayoutClass
    from .Extras import dpUpdateRigInfo
    from .Extras import dpReorderAttr
    from .Extras import dpCustomAttr
    from .Languages.Translator import dpTranslator
    from .Pipeline import dpPipeliner
    from .Pipeline import dpPublisher
    from .Pipeline import dpPackager
    from .Pipeline import dpLogger
    from .Deforms import dpSkinning
    from importlib import reload
    reload(dpUtils)
    reload(dpControls)
    reload(dpUpdateRigInfo)
    reload(dpBaseClass)
    reload(dpLayoutClass)
    reload(dpPublisher)
    reload(dpPipeliner)
    reload(dpPackager)
    reload(dpLogger)
    reload(dpCustomAttr)
    reload(dpSkinning)
except Exception as e:
    print("Error: importing python modules!!!\n")
    print(e)
    dpARDownloadMaster()
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
CONTROLS_PRESETS = "Controls/Presets"
EXTRAS = "Extras"
LANGUAGES = "Languages"
VALIDATOR = "Pipeline/Validator"
CHECKIN = "Pipeline/Validator/CheckIn"
CHECKOUT = "Pipeline/Validator/CheckOut"
VALIDATOR_PRESETS = "Pipeline/Validator/Presets"
REBUILDER =  "Pipeline/Rebuilder"
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
NOSE = "Nose"
CHAIN = "Chain"
GUIDE_BASE_NAME = "Guide_Base"
GUIDE_BASE_ATTR = "guideBase"
MODULE_NAMESPACE_ATTR = "moduleNamespace"
MODULE_INSTANCE_INFO_ATTR = "moduleInstanceInfo"
TEMP_GRP = "dpAR_Temp_Grp"
GUIDEMIRROR_GRP = "dpAR_GuideMirror_Grp"
INFO_ICON = "dp_info.png"
DPAR_SITE = "https://nilouco.blogspot.com"
DPAR_RAWURL = "https://raw.githubusercontent.com/nilouco/dpAutoRigSystem/master/dpAutoRigSystem/dpAutoRig.py"
DPAR_GITHUB = "https://github.com/nilouco/dpAutoRigSystem"
DPAR_MASTERURL = "https://github.com/nilouco/dpAutoRigSystem/zipball/master/"
DPAR_WHATSCHANGED = "https://github.com/nilouco/dpAutoRigSystem/commits/master"
DONATE = "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=nilouco%40gmail.com&item_name=Support+dpAutoRigSystem+and+Tutorials+by+Danilo+Pinheiro+%28nilouco%29&currency_code="
LOCATION_URL = "https://ipinfo.io/json"
MASTER_ATTR = "masterGrp"
DPDATA = "dpData"
DPLOG = "dpLog"


class DP_AutoRig_UI(object):

    ###################### Start: UI
    
    def __init__(self):
        """ Start the window, menus and main layout for dpAutoRig UI.
        """
        self.dpARVersion = DPAR_VERSION_PY3
        self.loadedPath = False
        self.loadedModules = False
        self.loadedScripts = False
        self.loadedControls = False
        self.loadedCombined = False
        self.loadedExtras = False
        self.loadedCheckIn = False
        self.loadedCheckOut = False
        self.loadedAddOns = False
        self.loadedRebuilder = False
        self.controlInstanceList = []
        self.checkInInstanceList = []
        self.checkOutInstanceList = []
        self.checkAddOnsInstanceList = []
        self.rebuilderInstanceList = []
        self.rebuilding = False
        self.degreeOption = 0
        self.tempGrp = TEMP_GRP
        self.guideMirrorGrp = GUIDEMIRROR_GRP
        self.userDefAutoCheckUpdate = 1
        self.userDefAgreeTerms = 1
        self.dpData = DPDATA
        self.dpLog = DPLOG
        self.optionCtrl = None
        self.utils = dpUtils.Utils()
        self.pipeliner = dpPipeliner.Pipeliner(self)
        self.packager = dpPackager.Packager()
#        self.logger = dpLogger.Logger(None) #placeholder
        
        try:
            # store all UI elements in a dictionary:
            self.allUIs = {}
            self.iDeleteJobId = 0
            self.iSelChangeJobId = 0
            # creating User Interface (UI) Window:
            self.deleteExistWindow()
            dpAR_winWidth  = 305
            dpAR_winHeight = 605
            self.allUIs["dpAutoRigWin"] = cmds.window('dpAutoRigWindow', title='dpAutoRigSystem - v'+str(self.dpARVersion)+' - UI', iconName='dpAutoRig', widthHeight=(dpAR_winWidth, dpAR_winHeight), menuBar=True, sizeable=True, minimizeButton=True, maximizeButton=False)
            
            # creating menus:
            self.allUIs["settingsMenu"] = cmds.menu('settingsMenu', label='Settings')
            # language menu:
            self.allUIs["languageMenu"] = cmds.menuItem('languageMenu', label='Language', parent='settingsMenu', subMenu=True)
            cmds.radioMenuItemCollection('languageRadioMenuCollection')
            # create a language list:
            self.langList, self.langDic = self.getJsonFileInfo(LANGUAGES)
            # create menuItems from language list:
            if self.langList:
                # verify if there is an optionVar of last choosen by user in Maya system:
                lastLang = self.checkLastOptionVar("dpAutoRigLastLanguage", ENGLISH, self.langList)
                # create menuItems with the command to set the last language variable, delete languageUI and call mainUI() again when changed:
                for idiom in self.langList:
                    cmds.menuItem(idiom+"_MI", label=idiom, radioButton=False, collection='languageRadioMenuCollection', command='from maya import cmds; cmds.optionVar(remove=\"dpAutoRigLastLanguage\"); cmds.optionVar(stringValue=(\"dpAutoRigLastLanguage\", \"'+idiom+'\")); cmds.evalDeferred(\"import sys; sys.modules[\'dpAutoRigSystem.dpAutoRig\'].DP_AutoRig_UI()\", lowestPriority=True)')
                # load the last language from optionVar value:
                cmds.menuItem(lastLang+"_MI", edit=True, radioButton=True, collection='languageRadioMenuCollection')
            else:
                print("Error: Cannot load json language files!\n")
                return
            
            # preset menu:
            self.allUIs["controlsPresetMenu"] = cmds.menuItem('controlsPresetMenu', label='Controls Preset', parent='settingsMenu', subMenu=True)
            cmds.radioMenuItemCollection('presetRadioMenuCollection')
            # create a preset list:
            self.presetList, self.presetDic = self.getJsonFileInfo(CONTROLS_PRESETS)
            # create menuItems from preset list:
            if self.presetList:
                # verify if there is an optionVar of last choosen by user in Maya system:
                lastPreset = self.checkLastOptionVar("dpAutoRigLastPreset", "Default", self.presetList)
                # create menuItems with the command to set the last preset variable, delete languageUI and call mainUI() again when changed:
                for preset in self.presetList:
                    cmds.menuItem( preset+"_MI", label=preset, radioButton=False, collection='presetRadioMenuCollection', command='from maya import cmds; cmds.optionVar(remove=\"dpAutoRigLastPreset\"); cmds.optionVar(stringValue=(\"dpAutoRigLastPreset\", \"'+preset+'\")); cmds.evalDeferred(\"import sys; sys.modules[\'dpAutoRigSystem.dpAutoRig\'].DP_AutoRig_UI())\", lowestPriority=True)')
                # load the last preset from optionVar value:
                cmds.menuItem(lastPreset+"_MI", edit=True, radioButton=True, collection='presetRadioMenuCollection', parent='controlsPresetMenu')
            else:
                print("Error: Cannot load json preset files!\n")
                return
            
            # validator preset menu:
            self.allUIs["validatorPresetMenu"] = cmds.menuItem('validatorPresetMenu', label='Validator Preset', parent='settingsMenu', subMenu=True)
            cmds.radioMenuItemCollection('validatorPresetRadioMenuCollection')
            # create a validator preset list:
            self.validatorPresetList, self.validatorPresetDic = self.getJsonFileInfo(VALIDATOR_PRESETS)
            if self.pipeliner.pipeData['presetsPath']:
                self.loadPipelineValidatorPresets()
            # create menuItems from validator preset list:
            if self.validatorPresetList:
                # create menuItems with the validator presets
                for validatorPreset in self.validatorPresetList:
                    cmds.menuItem( validatorPreset+"_MI", label=validatorPreset, radioButton=False, collection='validatorPresetRadioMenuCollection', command=self.setValidatorPreset)
                # load the first validator preset, expected to be the pipeline studio item if it exists:
                cmds.menuItem(self.validatorPresetList[0]+"_MI", edit=True, radioButton=True, collection='validatorPresetRadioMenuCollection', parent='validatorPresetMenu')
            else:
                print("Error: Cannot load json validator preset files!\n")
                return
            
            
            # create the main layout:
            self.allUIs["mainLayout"] = cmds.formLayout('mainLayout')
            # here we will populate with layout from mainUI based in the choose language.
            
            # call mainUI in order to populate the main layout:
            self.mainUI()
            
            # check if we need to automatically check for update:
            self.autoCheckOptionVar("dpAutoRigAutoCheckUpdate", "dpAutoRigLastDateAutoCheckUpdate", "update")
            # also check for agreement of terms and conditions
            self.autoCheckOptionVar("dpAutoRigAgreeTermsCond", "dpAutoRigLastDateAgreeTermsCond", "terms")

        except Exception as e:
            print("Error: dpAutoRig UI window !!!\n")
            print("Exception:", e)
            try:
                # error logging
                self.packager.toDiscord(self.utils.mountWH(dpPipeliner.DISCORD_URL, self.pipeliner.pipeData['h002_error']), self.dpARVersion+": "+str(e))
            except:
                pass
            print(self.langDic[self.langName]['i008_errorUI'])
            dpARDownloadMaster()
            clearDPARLoadingWindow()
            return
        
        # call UI window: Also ensure that when thedock controler X button is hit, the window is killed and the dock control too
        self.iUIKilledId = cmds.scriptJob(uiDeleted=[self.allUIs["dpAutoRigWin"], self.jobWinClose])
        self.pDockCtrl = cmds.dockControl('dpAutoRigSystem', area="left", content=self.allUIs["dpAutoRigWin"], visibleChangeCommand=self.jobDockVisChange)
        self.refreshAssetSaveJob = cmds.scriptJob(event=('SceneSaved', partial(self.refreshMainUI, True)), parent='dpAutoRigSystem', killWithScene=True, compressUndo=True)
        self.ctrls.startCorrectiveEditMode()
        clearDPARLoadingWindow()
        self.refreshMainUI()


    def deleteExistWindow(self, *args):
        """ Check if there are the dpAutoRigWindow and dpAutoRigSystem_Control to deleteUI.
        """
        if cmds.window('dpAutoRigWindow', query=True, exists=True):
            cmds.deleteUI('dpAutoRigWindow', window=True)
        if cmds.dockControl('dpAutoRigSystem', query=True, exists=True):
            cmds.deleteUI('dpAutoRigSystem', control=True)
    
    
    def getJsonFileInfo(self, dir, absolute=False):
        """ Find all json files in the given path and get contents used for each file.
            Create a dictionary with dictionaries of all file found.
            Return a list with the name of the found files.
        """
        # declare the resulted list:
        resultList = []
        resultDic = {}
        jsonPath = dir
        if not absolute:
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
                fileDictionary = open(jsonPath + file, "r", encoding='utf-8')
                try:
                    # read the json file content and store it in a dictionary:
                    content = json.loads(fileDictionary.read())
                    resultDic[typeName] = content
                    resultList.append(typeName)
                except:
                    print("Error: json file corrupted:", file)
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
        # optimize dictionaries
        self.lang = self.langDic[self.langName]
        self.ctrlPreset = self.presetDic[self.presetName]
        
        # initialize some objects here:
        self.ctrls = dpControls.ControlClass(self)
        self.publisher = dpPublisher.Publisher(self)
        self.customAttr = dpCustomAttr.CustomAttr(self, False)
        self.skin = dpSkinning.Skinning(self)
        self.logger = dpLogger.Logger(self)
        # --

        # create menu:
        self.allUIs["createMenu"] = cmds.menu('createMenu', label='Create')
        cmds.menuItem('translator_MI', label='Translator', command=self.translator)
        cmds.menuItem('pipeliner_MI', label='Pipeliner', command=partial(self.pipeliner.mainUI, self))
        cmds.menuItem('createControlPreset_MI', label='Controls Preset', command=partial(self.createPreset, "controls", CONTROLS_PRESETS, True))
        cmds.menuItem('createValidatorPreset_MI', label='Validator Preset', command=partial(self.createPreset, "validator", VALIDATOR_PRESETS, False))
        # window menu:
        self.allUIs["windowMenu"] = cmds.menu( 'windowMenu', label='Window')
        cmds.menuItem('reloadUI_MI', label='Reload UI', command=self.reloadMainUI)
        cmds.menuItem('quit_MI', label='Quit', command=self.deleteExistWindow)
        # help menu:
        self.allUIs["helpMenu"] = cmds.menu( 'helpMenu', label='Help', helpMenu=True)
        cmds.menuItem('about_MI"', label='About', command=partial(self.logger.infoWin, 'm015_about', 'i006_aboutDesc', None, 'center', 305, 250))
        cmds.menuItem('author_MI', label='Author', command=partial(self.logger.infoWin, 'm016_author', 'i007_authorDesc', None, 'center', 305, 250))
        cmds.menuItem('collaborators_MI', label='Collaborators', command=partial(self.logger.infoWin, 'i165_collaborators', 'i166_collabDesc', "\n\n"+self.langDic[ENGLISH]['_collaborators'], 'center', 305, 250))
        cmds.menuItem('donate_MI', label='Donate', command=partial(self.donateWin))
        cmds.menuItem('idiom_MI', label='Idioms', command=partial(self.logger.infoWin, 'm009_idioms', 'i012_idiomsDesc', None, 'center', 305, 250))
        cmds.menuItem('terms_MI', label='Terms and Conditions', command=self.checkTermsAndCond)
        cmds.menuItem('update_MI', label='Update', command=partial(self.checkForUpdate, True))
        cmds.menuItem('help_MI', label='Help...', command=partial(self.utils.visitWebSite, DPAR_SITE))
        
        # creating tabs - mainTabLayout:
        self.allUIs["mainTabLayout"] = cmds.tabLayout('mainTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=self.allUIs["mainLayout"])
        cmds.formLayout( self.allUIs["mainLayout"], edit=True, attachForm=((self.allUIs["mainTabLayout"], 'top', 0), (self.allUIs["mainTabLayout"], 'left', 0), (self.allUIs["mainTabLayout"], 'bottom', 0), (self.allUIs["mainTabLayout"], 'right', 0)) )
        
        # --
        
        # interface of Rigging tab - formLayout:
        self.allUIs["riggingTabLayout"] = cmds.formLayout('riggingTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        
        #colTopLefA - columnLayout:
        self.allUIs["colTopLeftA"] = cmds.columnLayout('colTopLeftA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["i000_guides"] = cmds.text(self.lang['i000_guides'], font="boldLabelFont", width=150, align='center', parent=self.allUIs["colTopLeftA"])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colTopRightA - columnLayout:
        self.allUIs["colTopRightA"] = cmds.columnLayout('colTopRightA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["i001_modules"] = cmds.text(self.lang['i001_modules'], font="boldLabelFont", width=150, align='center', parent=self.allUIs["colTopRightA"])
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colMiddleLeftA - scrollLayout - guidesLayout:
        self.allUIs["colMiddleLeftA"] = cmds.scrollLayout("colMiddleLeftA", width=150, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["guidesLayoutA"] = cmds.columnLayout("guidesLayoutA", adjustableColumn=True, width=122, rowSpacing=3, parent=self.allUIs["colMiddleLeftA"])
        # here will be populated by guides of modules and scripts...
        self.allUIs["i030_standard"] = cmds.text(self.lang['i030_standard'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.guideModuleList = self.startGuideModules(MODULES, "start", "guidesLayoutA")
        cmds.separator(style='doubleDash', height=10, parent=self.allUIs["guidesLayoutA"])
        self.allUIs["i031_integrated"] = cmds.text(self.lang['i031_integrated'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.startGuideModules(SCRIPTS, "start", "guidesLayoutA")
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colMiddleRightA - scrollLayout - modulesLayout:
        self.allUIs["colMiddleRightA"] = cmds.scrollLayout("colMiddleRightA", width=150, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=200, parent=self.allUIs["colMiddleRightA"])
        # here will be populated by created instances of modules...
        # after footerA we will call the function to populate here, because it edits the footerAText
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #editSelectedModuleLayoutA - frameLayout:
        self.allUIs["editSelectedModuleLayoutA"] = cmds.frameLayout('editSelectedModuleLayoutA', label=self.lang['i011_editSelected']+" "+self.lang['i143_module'], collapsable=True, collapse=False, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["selectedModuleLayout"] = cmds.columnLayout('selectedModuleLayout', adjustableColumn=True, parent=self.allUIs["editSelectedModuleLayoutA"])
        
        #optionsA - frameLayout:
        self.allUIs["optionsA"] = cmds.frameLayout('optionsA', label=self.lang['i002_options'], collapsable=True, collapse=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigOptionsLayout"] = cmds.columnLayout('rigOptionsLayout', adjustableColumn=True, columnOffset=('left', 5), parent=self.allUIs["optionsA"])
        self.allUIs["prefixLayout"] = cmds.rowColumnLayout('prefixLayout', numberOfColumns=2, columnWidth=[(1, 40), (2, 100)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["prefixTextField"] = cmds.textField('prefixTextField', text="", parent= self.allUIs["prefixLayout"], changeCommand=self.setPrefix)
        self.allUIs["prefixText"] = cmds.text('prefixText', align='left', label=self.lang['i003_prefix'], parent=self.allUIs["prefixLayout"])
        cmds.setParent(self.allUIs["rigOptionsLayout"])
        self.allUIs["hideJointsCB"] = cmds.checkBox('hideJointsCB', label=self.lang['i009_hideJointsCB'], align='left', v=0, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["hideGuideGrpCB"] = cmds.checkBox('hideGuideGrpCB', label=self.lang['i183_hideGuideGrp'], align='left', v=1, changeCommand=self.displayGuideGrp, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["integrateCB"] = cmds.checkBox('integrateCB', label=self.lang['i010_integrateCB'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["defaultRenderLayerCB"] = cmds.checkBox('defaultRenderLayerCB', label=self.lang['i004_defaultRL'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["colorizeCtrlCB"] = cmds.checkBox('colorizeCtrlCB', label=self.lang['i065_colorizeCtrl'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["addAttrCB"] = cmds.checkBox('addAttrCB', label=self.lang['i066_addAttr'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["degreeLayout"] = cmds.rowColumnLayout('degreeLayout', numberOfColumns=2, columnWidth=[(1, 100), (2, 250)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=self.allUIs["rigOptionsLayout"])
        # option Degree:
        self.degreeOptionMenu = cmds.optionMenu("degreeOptionMenu", label='', changeCommand=self.changeOptionDegree, parent=self.allUIs["degreeLayout"])
        self.degreeOptionMenuItemList = ['0 - Preset', '1 - Linear', '3 - Cubic']
        # verify if there is an optionVar of last choosen by user in Maya system:
        lastDegreeOption = self.checkLastOptionVar("dpAutoRigLastDegreeOption", "0 - Preset", self.degreeOptionMenuItemList)
        for degreeOption in self.degreeOptionMenuItemList:
            cmds.menuItem(label=degreeOption, parent=self.degreeOptionMenu)
        cmds.optionMenu(self.degreeOptionMenu, edit=True, value=lastDegreeOption)
        cmds.text(self.lang['i128_optionDegree'], parent=self.allUIs["degreeLayout"])
        self.degreeOption = int(lastDegreeOption[0])

        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #footerA - columnLayout:
        self.allUIs["footerA"] = cmds.columnLayout('footerA', adjustableColumn=True, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["rigAllButton"] = cmds.button(label=self.lang['i020_rigAll'], annotation=self.lang['i021_rigAllDesc'], backgroundColor=(0.6, 1.0, 0.6), command=self.rigAll, parent=self.allUIs["footerA"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerA"])
        # this text will be actualized by the number of module instances created in the scene...
        self.allUIs["footerAText"] = cmds.text('footerAText', align='center', label="# "+self.lang['i005_footerA'], parent=self.allUIs["footerA"])
        cmds.setParent( self.allUIs["mainTabLayout"] )
        
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["riggingTabLayout"], edit=True,
                        attachForm=[(self.allUIs["colTopLeftA"], 'top', 5), (self.allUIs["colTopLeftA"], 'left', 5), (self.allUIs["colTopRightA"], 'top', 5), (self.allUIs["colTopRightA"], 'right', 5), (self.allUIs["colMiddleLeftA"], 'left', 5), (self.allUIs["colMiddleRightA"], 'right', 5), (self.allUIs["optionsA"], 'left', 5), (self.allUIs["optionsA"], 'right', 5), (self.allUIs["editSelectedModuleLayoutA"], 'left', 5), (self.allUIs["editSelectedModuleLayoutA"], 'right', 5), (self.allUIs["footerA"], 'left', 5), (self.allUIs["footerA"], 'bottom', 5), (self.allUIs["footerA"], 'right', 5)],
                        attachControl=[(self.allUIs["colMiddleLeftA"], 'top', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colTopRightA"], 'left', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colMiddleLeftA"], 'bottom', 5, self.allUIs["editSelectedModuleLayoutA"]), (self.allUIs["colMiddleRightA"], 'top', 5, self.allUIs["colTopLeftA"]), (self.allUIs["colMiddleRightA"], 'bottom', 5, self.allUIs["editSelectedModuleLayoutA"]), (self.allUIs["colMiddleRightA"], 'left', 5, self.allUIs["colMiddleLeftA"]), (self.allUIs["editSelectedModuleLayoutA"], 'bottom', 5, self.allUIs["optionsA"]), (self.allUIs["optionsA"], 'bottom', 5, self.allUIs["footerA"])],
                        #attachPosition=[(self.allUIs["colTopLeftA"], 'right', 5, 50), (self.allUIs["colTopRightA"], 'left', 0, 50)],
                        attachNone=[(self.allUIs["footerA"], 'top')]
                        )
        
        # create the job of selected guide module and when new scene is created:
        self.iDeleteJobId = cmds.scriptJob(event=('deleteAll', self.refreshMainUI), parent='dpAutoRigWindow', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
        self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)
        
        # --
        
        # interface of Skinning tab:
        self.allUIs["skinningTabLayout"] = cmds.formLayout('skinningTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        # skinMainLayout - scrollLayout:
        self.allUIs["skinMainLayout"] = cmds.scrollLayout('skinMainLayout', parent=self.allUIs["skinningTabLayout"])
        self.allUIs["skinLayout"] = cmds.columnLayout('skinLayout', adjustableColumn=True, rowSpacing=10, parent=self.allUIs['skinMainLayout'])
        self.allUIs["skinCreateFL"] = cmds.frameLayout('skinCreateFL', label=self.lang['i158_create']+" SkinCluster", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["skinLayout"])
        self.allUIs["skinLists2Layout"] = cmds.paneLayout("skinLists2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["skinCreateFL"])
        
        #colSkinLeftA - columnLayout:
        self.allUIs["colSkinLeftA"] = cmds.columnLayout('colSkinLeftA', adjustableColumn=True, width=170, parent=self.allUIs["skinLists2Layout"])
        # radio buttons:
        self.allUIs["jntCollection"] = cmds.radioCollection('jntCollection', parent=self.allUIs["colSkinLeftA"])
        allJoints  = cmds.radioButton(label=self.lang['i022_listAllJnts'], annotation="allJoints", onCommand=self.populateJoints)
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
        allGeoms = cmds.radioButton(label=self.lang['i026_listAllJnts'], annotation="allGeoms", onCommand=self.populateGeoms)
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
        self.allUIs["footerAddRem"] = cmds.paneLayout("footerAddRem", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["footerB"])
        self.allUIs["addSkinButton"] = cmds.button("addSkinButton", label=self.lang['i063_skinAddBtn'], backgroundColor=(0.7, 0.9, 0.9), command=partial(self.skin.skinFromUI, "Add"), parent=self.allUIs["footerAddRem"])
        self.allUIs["removeSkinButton"] = cmds.button("removeSkinButton", label=self.lang['i064_skinRemBtn'], backgroundColor=(0.1, 0.3, 0.3), command=partial(self.skin.skinFromUI, "Remove"), parent=self.allUIs["footerAddRem"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerB"])
        # this text will be actualized by the number of joints and geometries in the textScrollLists for skinning:
        self.allUIs["footerBText"] = cmds.text('footerBText', align='center', label="0 "+self.lang['i025_joints']+" 0 "+self.lang['i024_geometries'], parent=self.allUIs["footerB"])
        
        #skinCopy - layout
        self.allUIs["skinCopyFL"] = cmds.frameLayout('skinCopyFL', label=self.lang['i287_copy']+" Skinning", collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["skinLayout"])
        self.allUIs['skinCopyRowLayout'] = cmds.rowLayout('skinCopyRowLayout', numberOfColumns=3, columnWidth3=(90, 90, 150), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent=self.allUIs["skinCopyFL"])
        self.allUIs["skinSurfAssociationCollection"] = cmds.radioCollection('skinSurfAssociationCollection', parent=self.allUIs["skinCopyRowLayout"])
        closestPoint = cmds.radioButton(label="closestPoint", annotation="closestPoint")
        uvSpace      = cmds.radioButton(label="uvSpace", annotation="uvSpace")
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
        
        # --
        
        # interface of Control tab - formLayout:
        self.allUIs["controlTabLayout"] = cmds.formLayout('controlTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        # controlMainLayout - scrollLayout:
        self.allUIs["controlMainLayout"] = cmds.scrollLayout('controlMainLayout', parent=self.allUIs["controlTabLayout"])
        self.allUIs["controlLayout"] = cmds.columnLayout('controlLayout', adjustableColumn=True, rowSpacing=10, parent=self.allUIs['controlMainLayout'])
        
        # setupControl - frameLayout:
        self.allUIs["defaultValuesControlFL"] = cmds.frameLayout('defaultValuesControlFL', label=self.lang['i270_defaultValues'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controlLayout"])
        self.allUIs["defaultValuesControl3Layout"] = cmds.paneLayout("defaultValuesControl3Layout", configuration="vertical3", separatorThickness=2.0, parent=self.allUIs["defaultValuesControlFL"])
        self.allUIs["resetToDefaultValuesButton"] = cmds.button("resetToDefaultValuesButton", label=self.lang['i271_reset'], backgroundColor=(1.0, 0.9, 0.6), height=30, command=partial(self.ctrls.setupDefaultValues, True), parent=self.allUIs["defaultValuesControl3Layout"])
        self.allUIs["setDefaultValuesButton"] = cmds.button("setDefaultValuesButton", label=self.lang['i272_set'], backgroundColor=(1.0, 0.8, 0.5), height=30, command=partial(self.ctrls.setupDefaultValues, False), parent=self.allUIs["defaultValuesControl3Layout"])
        self.allUIs["setupDefaultValuesButton"] = cmds.button("setupDefaultValuesButton", label=self.lang['i274_editor'], backgroundColor=(1.0, 0.6, 0.4), height=30, command=self.ctrls.defaultValueEditor, parent=self.allUIs["defaultValuesControl3Layout"])

        # createControl - frameLayout:
        self.allUIs["createControlLayout"] = cmds.frameLayout('createControlLayout', label=self.lang['i114_createControl'], collapsable=True, collapse=False, marginWidth=10, marginHeight=10, parent=self.allUIs["controlLayout"])
        self.allUIs["optionsB"] = cmds.frameLayout('optionsB', label=self.lang['i002_options'], collapsable=True, collapse=False, marginWidth=10, parent=self.allUIs["createControlLayout"])
        self.allUIs["controlOptionsLayout"] = cmds.columnLayout('controlOptionsLayout', adjustableColumn=True, width=50, rowSpacing=5, parent=self.allUIs["optionsB"])
        self.allUIs["controlNameTFG"] = cmds.textFieldGrp('controlNameTFG', text="", label=self.lang['i101_customName'], columnAlign2=("right", "left"), adjustableColumn2=2, columnAttach=((1, "right", 5), (2, "left", 5)), parent=self.allUIs["controlOptionsLayout"])
        self.allUIs["controlActionRBG"] = cmds.radioButtonGrp("controlActionRBG", label=self.lang['i109_action'], labelArray3=[self.lang['i108_newControl'], self.lang['i107_addShape'], self.lang['i102_replaceShape']], vertical=True, numberOfRadioButtons=3, parent=self.allUIs["controlOptionsLayout"])
        cmds.radioButtonGrp(self.allUIs["controlActionRBG"], edit=True, select=1) #new control
        self.allUIs["degreeRBG"] = cmds.radioButtonGrp("degreeRBG", label=self.lang['i103_degree'], labelArray2=[self.lang['i104_linear'], self.lang['i105_cubic']], vertical=True, numberOfRadioButtons=2, parent=self.allUIs["controlOptionsLayout"])
        cmds.radioButtonGrp(self.allUIs["degreeRBG"], edit=True, select=1) #linear
        self.allUIs["controlSizeFSG"] = cmds.floatSliderGrp("controlSizeFSG", label=self.lang['i115_size'], field=True, minValue=0.01, maxValue=10.0, fieldMinValue=0, fieldMaxValue=1000.0, precision=2, value=1.0, parent=self.allUIs["controlOptionsLayout"])
        self.allUIs["directionOMG"] = cmds.optionMenuGrp("directionOMG", label=self.lang['i106_direction'], parent=self.allUIs["controlOptionsLayout"])
        cmds.menuItem(label='-X')
        cmds.menuItem(label='+X')
        cmds.menuItem(label='-Y')
        cmds.menuItem(label='+Y')
        cmds.menuItem(label='-Z')
        cmds.menuItem(label='+Z')
        cmds.optionMenuGrp(self.allUIs["directionOMG"], edit=True, value='+Y')
        
        # curveShapes - frameLayout:
        self.allUIs["controlShapesLayout"] = cmds.frameLayout('controlShapesLayout', label=self.lang['i100_curveShapes'], collapsable=True, collapse=False, parent=self.allUIs["createControlLayout"])
        self.allUIs["controlModuleLayout"] = cmds.gridLayout('controlModuleLayout', numberOfColumns=7, cellWidthHeight=(48, 50), backgroundColor=(0.3, 0.3, 0.3), parent=self.allUIs['controlShapesLayout'])
        # here we populate the control module layout with the items from Controls folder:
        self.controlModuleList = self.startGuideModules(CONTROLS, "start", "controlModuleLayout")
        
        self.allUIs["combinedControlShapesLayout"] = cmds.frameLayout('combinedControlShapesLayout', label=self.lang['i118_combinedShapes'], collapsable=True, collapse=False, parent=self.allUIs["createControlLayout"])
        self.allUIs["combinedControlModuleLayout"] = cmds.gridLayout('combinedControlModuleLayout', numberOfColumns=7, cellWidthHeight=(48, 50), backgroundColor=(0.3, 0.3, 0.3), parent=self.allUIs['combinedControlShapesLayout'])
        # here we populate the control module layout with the items from Controls folder:
        self.combinedControlModuleList = self.startGuideModules(COMBINED, "start", "combinedControlModuleLayout")
        
        # editSeletedController - frameLayout:
        self.allUIs["editSelectedControllerFL"] = cmds.frameLayout('editSelectedControllerFL', label=self.lang['i011_editSelected']+" "+self.lang['i111_controller'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controlLayout"])
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
        self.allUIs["calibrationFL"] = cmds.frameLayout('calibrationFL', label=self.lang['i193_calibration'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controlLayout"])
        self.allUIs["calibration2Layout"] = cmds.paneLayout("calibration2Layout", configuration="vertical2", separatorThickness=2.0, parent=self.allUIs["calibrationFL"])
        self.allUIs["transferCalibrationButton"] = cmds.button("transferCalibrationButton", label=self.lang['i194_transfer'], backgroundColor=(0.5, 1.0, 1.0), height=30, command=self.ctrls.transferCalibration, parent=self.allUIs["calibration2Layout"])
        self.allUIs["importCalibrationButton"] = cmds.button("importCalibrationButton", label=self.lang['i196_import'], backgroundColor=(0.5, 0.8, 1.0), height=30, command=self.ctrls.importCalibration, parent=self.allUIs["calibration2Layout"])
        # mirror calibration - layout:
        self.allUIs["mirrorCalibrationFL"] = cmds.frameLayout('mirrorCalibrationFL', label=self.lang['m010_mirror']+" "+self.lang['i193_calibration'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["calibrationFL"])
        self.allUIs["mirrorCalibrationLayout"] = cmds.rowColumnLayout('mirrorCalibrationLayout', numberOfColumns=6, columnWidth=[(1, 60), (2, 40), (3, 40), (4, 40), (5, 40), (6, 70)], columnAlign=[(1, 'left'), (2, 'right'), (3, 'left'), (4, 'right'), (5, 'left'), (6, 'right')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 20)], parent="mirrorCalibrationFL" )
        self.allUIs["prefixT"] = cmds.text("prefixT", label=self.lang['i144_prefix'], parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["fromPrefixT"] = cmds.text("fromPrefixT", label=self.lang['i036_from'], parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["fromPrefixTF"] = cmds.textField('fromPrefixTF', text=self.lang['p002_left']+"_", parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["toPrefixT"] = cmds.text("toPrefixT", label=self.lang['i037_to'], parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["toPrefixTF"] = cmds.textField('toPrefixTF', text=self.lang['p003_right']+"_", parent=self.allUIs["mirrorCalibrationLayout"])
        self.allUIs["mirrorCalibrationButton"] = cmds.button("mirrorCalibrationButton", label=self.lang['m010_mirror'], backgroundColor=(0.5, 0.7, 1.0), height=30, width=70, command=self.ctrls.mirrorCalibration, parent=self.allUIs["mirrorCalibrationLayout"])
        
        # ControlShapeIO - frameLayout:
        self.allUIs["shapeIOFL"] = cmds.frameLayout('shapeIOFL', label=self.lang['m067_shape']+" "+self.lang['i199_io'], collapsable=True, collapse=False, marginHeight=10, marginWidth=10, parent=self.allUIs["controlLayout"])
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
        
        # interface of Validator tab - formLayout:
        self.allUIs["validatorTabLayout"] = cmds.formLayout('validatorTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        # validatorMainLayout - scrollLayout:
        self.allUIs["validatorMainLayout"] = cmds.scrollLayout("validatorMainLayout", parent=self.allUIs["validatorTabLayout"])
        self.allUIs["validatorLayout"] = cmds.columnLayout("validatorLayout", adjustableColumn=True, rowSpacing=3, parent=self.allUIs["validatorMainLayout"])
        self.allUIs["validatorCheckInLayout"] = cmds.frameLayout('validatorCheckInLayout', label=self.lang['i208_checkin'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
        # check-in
        self.validatorCheckInModuleList = self.startGuideModules(CHECKIN, "start", "validatorCheckInLayout")
        cmds.separator(style="none", parent=self.allUIs["validatorCheckInLayout"])
        self.allUIs["selectAllCheckinCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i208_checkin'], value=True, changeCommand=partial(self.changeActiveAllModules, self.checkInInstanceList), parent=self.allUIs["validatorCheckInLayout"])
        self.allUIs["selectedCheckIn2Layout"] = cmds.paneLayout("selectedCheckIn2Layout", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorCheckInLayout"])
        self.allUIs["verifyAllSelectCheckinBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkInInstanceList, True, True), parent=self.allUIs["selectedCheckIn2Layout"])
        self.allUIs["fixAllSelectCheckinBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkInInstanceList, False, True), parent=self.allUIs["selectedCheckIn2Layout"])
        cmds.separator(height=30, parent=self.allUIs["validatorLayout"])
        # check-out
        self.allUIs["validatorCheckOutLayout"] = cmds.frameLayout('validatorCheckOutLayout', label=self.lang['i209_checkout'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
        self.validatorCheckOutModuleList = self.startGuideModules(CHECKOUT, "start", "validatorCheckOutLayout")
        cmds.separator(style="none", parent=self.allUIs["validatorCheckOutLayout"])
        self.allUIs["selectAllCheckoutCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i209_checkout'], value=True, changeCommand=partial(self.changeActiveAllModules, self.checkOutInstanceList), parent=self.allUIs["validatorCheckOutLayout"])
        self.allUIs["selectedCheckOut2Layout"] = cmds.paneLayout("selectedCheckOut2Layout", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorCheckOutLayout"])
        self.allUIs["verifyAllSelectCheckoutBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkOutInstanceList, True, True), parent=self.allUIs["selectedCheckOut2Layout"])
        self.allUIs["fixAllSelectCheckoutBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkOutInstanceList, False, True), parent=self.allUIs["selectedCheckOut2Layout"])
        # pipeline check-addons
        if self.pipeliner.pipeData['addOnsPath']:
            if self.getValidatorsAddOns():
                cmds.separator(height=30, parent=self.allUIs["validatorLayout"])
                self.allUIs["validatorAddOnsLayout"] = cmds.frameLayout('validatorAddOnsLayout', label=self.lang['i212_addOns'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["validatorLayout"])
                self.validatorAddOnsModuleList = self.startGuideModules("", "start", "validatorAddOnsLayout", path=self.pipeliner.pipeData['addOnsPath'])
                cmds.separator(style="none", parent=self.allUIs["validatorAddOnsLayout"])
                self.allUIs["selectAllAddonCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i212_addOns'], value=True, changeCommand=partial(self.changeActiveAllModules, self.checkAddOnsInstanceList), parent=self.allUIs["validatorAddOnsLayout"])
                self.allUIs["selectedCheckAddOns2Layout"] = cmds.paneLayout("selectedCheckAddOns2Layout", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["validatorAddOnsLayout"])
                self.allUIs["verifyAllSelectAddonBT"] = cmds.button(label=self.lang['i210_verify'].upper(), command=partial(self.runSelectedActions, self.checkAddOnsInstanceList, True, True), parent=self.allUIs["selectedCheckAddOns2Layout"])
                self.allUIs["fixAllSelectAddonBT"] = cmds.button(label=self.lang['c052_fix'].upper(), command=partial(self.runSelectedActions, self.checkAddOnsInstanceList, False, True), parent=self.allUIs["selectedCheckAddOns2Layout"])
        # publisher
        self.allUIs["footerPublish"] = cmds.columnLayout('footerPublish', adjustableColumn=True, parent=self.allUIs["validatorTabLayout"])
        cmds.separator(style='none', height=3, parent=self.allUIs["footerPublish"])
        self.allUIs["publisherButton"] = cmds.button("publisherButton", label=self.lang['m046_publisher'], backgroundColor=(0.75, 0.75, 0.75), height=40, command=self.publisher.mainUI, parent=self.allUIs["footerPublish"])
        cmds.separator(style='none', height=5, parent=self.allUIs["footerPublish"])
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["validatorTabLayout"], edit=True,
                        attachForm=[(self.allUIs["validatorMainLayout"], 'top', 20), (self.allUIs["validatorMainLayout"], 'left', 5), (self.allUIs["validatorMainLayout"], 'right', 5), (self.allUIs["validatorMainLayout"], 'bottom', 55), (self.allUIs["footerPublish"], 'left', 5), (self.allUIs["footerPublish"], 'right', 5), (self.allUIs["footerPublish"], 'bottom', 5)],
                        attachNone=[(self.allUIs["footerPublish"], 'top')]
                        )
        self.setValidatorPreset()

        # --

        # interface of Rebuilder tab - formLayout:
        self.allUIs["rebuilderTabLayout"] = cmds.formLayout('rebuilderTabLayout', numberOfDivisions=100, parent=self.allUIs["mainTabLayout"])
        # rebuilderMainLayout - scrollLayout:
        self.allUIs["rebuilderMainLayout"] = cmds.scrollLayout("rebuilderMainLayout", parent=self.allUIs["rebuilderTabLayout"])
        self.allUIs["rebuilderLayout"] = cmds.columnLayout("rebuilderLayout", adjustableColumn=True, rowSpacing=3, parent=self.allUIs["rebuilderMainLayout"])
        # asset
        self.allUIs["rebuilderAssetFL"] = cmds.frameLayout('rebuilderAssetFL', label=self.lang['i303_asset'], collapsable=True, collapse=True, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["rebuilderLayout"])
        self.allUIs["rebuilderAsset2Layout"] = cmds.paneLayout("rebuilderAsset2Layout", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["rebuilderAssetFL"])
        self.allUIs['newAssetBT'] = cmds.button("newAssetBT", label=self.lang['i304_new'], command=self.pipeliner.createNewAssetUI, parent=self.allUIs["rebuilderAsset2Layout"])
        self.allUIs['replaceDPDataBT'] = cmds.button("replaceDPDataBT", label=self.lang['m219_replace']+" "+self.dpData, command=self.pipeliner.replaceDPData, parent=self.allUIs["rebuilderAsset2Layout"])
        cmds.separator(style="none", parent=self.allUIs["rebuilderLayout"])
        self.allUIs["rebuilderProcessLayout"] = cmds.frameLayout('rebuilderProcessLayout', label=self.lang['i292_processes'].upper(), collapsable=True, collapse=False, backgroundShade=True, marginHeight=10, marginWidth=10, parent=self.allUIs["rebuilderLayout"])
        # processes
        self.rebuilderModuleList = self.startGuideModules(REBUILDER, "start", "rebuilderProcessLayout")
        cmds.separator(style="none", parent=self.allUIs["rebuilderProcessLayout"])
        self.allUIs["selectAllProcessCB"] = cmds.checkBox(label=self.lang['m004_select']+" "+self.lang['i211_all']+" "+self.lang['i292_processes'].lower(), value=True, changeCommand=partial(self.changeActiveAllModules, self.rebuilderInstanceList), parent=self.allUIs["rebuilderProcessLayout"])
        self.allUIs["selectedRebuilders2Layout"] = cmds.paneLayout("selectedRebuilders2Layout", configuration="vertical2", separatorThickness=7.0, parent=self.allUIs["rebuilderProcessLayout"])
        self.allUIs["splitDataSelectProcessBT"] = cmds.button("splitDataSelectProcessBT", label=self.lang['r002_splitData'].upper(), command=partial(self.runSelectedActions, self.rebuilderInstanceList, True, True, actionType="r000_rebuilder"), parent=self.allUIs["selectedRebuilders2Layout"])
        self.allUIs["rebuildSelectProcessBT"] = cmds.button("rebuildSelectProcessBT", label=self.lang['r001_rebuild'].upper(), command=partial(self.runSelectedActions, self.rebuilderInstanceList, False, True, actionType="r000_rebuilder"), parent=self.allUIs["selectedRebuilders2Layout"])
        cmds.separator(height=30, parent=self.allUIs["rebuilderLayout"])
        # edit formLayout in order to get a good scalable window:
        cmds.formLayout( self.allUIs["rebuilderTabLayout"], edit=True,
                        attachForm=[(self.allUIs["rebuilderMainLayout"], 'top', 20), (self.allUIs["rebuilderMainLayout"], 'left', 5), (self.allUIs["rebuilderMainLayout"], 'right', 5), (self.allUIs["rebuilderMainLayout"], 'bottom', 55)]
                        )
        
        # --
        # call tabLayouts:
        cmds.tabLayout(self.allUIs["mainTabLayout"], edit=True, tabLabel=((self.allUIs["riggingTabLayout"], 'Rigging'), (self.allUIs["skinningTabLayout"], 'Skinning'), (self.allUIs["controlTabLayout"], 'Control'), (self.allUIs["extraTabLayout"], 'Extra'), (self.allUIs["validatorTabLayout"], self.lang['v000_validator']), (self.allUIs["rebuilderTabLayout"], self.lang['r000_rebuilder'])))
        self.selList = cmds.ls(selection=True)
    

    def reloadMainUI(self, *args):
        """ This scriptJob active when we got one new scene in order to reload the UI.
        """
        from maya import cmds
        cmds.evalDeferred("import sys; sys.modules['dpAutoRigSystem.dpAutoRig'].DP_AutoRig_UI()", lowestPriority=True)
        self.refreshMainUI()
    
    
    def refreshMainUI(self, savedScene=None, *args):
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
            self.resetAllButtonColors()
            self.pipeliner.refreshAssetData()
        try:
            self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=True, compressUndo=True)
        except:
            self.iSelChangeJobId = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=False, killWithScene=True, compressUndo=True)
        if savedScene:
            cmds.select(clear=True)
            if self.selList:
                cmds.select(self.selList)
        self.rebuilding = False


    def jobWinClose(self, *args):
        #This job will ensure that the dock control is killed correctly
        if self.pDockCtrl:
            if cmds.objExists(self.pDockCtrl):
                if (not cmds.dockControl(self.pDockCtrl, vis=True, query=True)):
                    if cmds.dockControl('dpAutoRigSystem', exists=True):
                        cmds.deleteUI('dpAutoRigSystem', control=True)
    
    
    def jobDockVisChange(self, *args):
        #Force focus
        try:
            cmds.dockControl(self.pDockCtrl, r=True, edit=True) #Force focus on the tool when it's open
        except:
            pass
    
    
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
                self.refreshMainUI()
                cmds.select(updatedGuideNodeList)

        # re-create module layout:
        if selectedGuideNodeList:
            for moduleInstance in self.moduleInstancesList:
                if moduleInstance.selectButton:
                    cmds.button(moduleInstance.selectButton, edit=True, label=" ", backgroundColor=(0.5, 0.5, 0.5))
                    for selectedGuide in selectedGuideNodeList:
                        selectedGuideInfo = cmds.getAttr(selectedGuide+"."+MODULE_INSTANCE_INFO_ATTR)
                        if selectedGuideInfo == str(moduleInstance):
                            moduleInstance.reCreateEditSelectedModuleLayout(bSelect=False)
        # delete module layout:
        else:
            try:
                cmds.frameLayout('editSelectedModuleLayoutA', edit=True, label=self.lang['i011_editSelected']+" "+self.lang['i143_module'])
                cmds.deleteUI("selectedModuleColumn")
                for moduleInstance in self.moduleInstancesList:
                    cmds.button(moduleInstance.selectButton, edit=True, label=" ", backgroundColor=(0.5, 0.5, 0.5))
            except:
                pass        

        # call reload the geometries in skin UI:
        self.reloadPopulatedGeoms()
    

    def resetAllButtonColors(self, *args):
        """ Just reset the button colors to default for each validator or rebuilder module.
        """
        buttonInstanceList = self.checkInInstanceList + self.checkOutInstanceList + self.checkAddOnsInstanceList + self.rebuilderInstanceList
        if buttonInstanceList:
            for item in buttonInstanceList:
                item.resetButtonColors()

    
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
        

    def createPreset(self, type="controls", presetDir=CONTROLS_PRESETS, setOptionVar=True, *args):
        """ Just call ctrls create preset and set it as userDefined preset.
        """
        if type == "controls":
            newPresetString = self.ctrls.dpCreateControlsPreset()
        elif type == "validator":
            newPresetString = self.utils.dpCreateValidatorPreset(self)
        if newPresetString:
            # create json file:
            resultDic = self.createJsonFile(newPresetString, presetDir, '_preset')
            # set this new preset as userDefined preset:
            self.presetName = resultDic['_preset']
            if setOptionVar:
                cmds.optionVar(remove="dpAutoRigLastPreset")
                cmds.optionVar(stringValue=("dpAutoRigLastPreset", self.presetName))
            # show preset creation result window:
            self.logger.infoWin('i129_createPreset', 'i133_presetCreated', '\n'+self.presetName+'\n\n'+self.lang['i134_rememberPublish']+'\n\n'+self.lang['i018_thanks'], 'center', 205, 270)
            # close and reload dpAR UI in order to avoid Maya crash
            self.reloadMainUI()
    
    
    def setupDuplicatedGuide(self, selectedItem, *args):
        """ This method will create a new module instance for a duplicated guide found.
            Returns a guideBase for a new module instance.
        """
        # Duplicating a module guide
        print(self.lang['i067_duplicating'])

        # declaring variables
        transformAttrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        nSegmentsAttr = "nJoints"
        customNameAttr = "customName"
        mirrorAxisAttr = "mirrorAxis"
        dispAnnotAttr = "displayAnnotation"
        netAttr = "net"

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
            if nJointsValue > 0:
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
        if cmds.objExists(selectedItem+"."+netAttr):
            toSetAttrList.remove(netAttr)
        
        # TODO: change to unify style and type attributes        
        if cmds.objExists(selectedItem+".type"):
            typeValue = cmds.getAttr(selectedItem+'.type')
            newGuideInstance.changeType(typeValue)
        if cmds.objExists(selectedItem+".style"):
            styleValue = cmds.getAttr(selectedItem+'.style')
            newGuideInstance.changeStyle(styleValue)
        
        # get and set transformations
        childrenList = cmds.listRelatives(selectedItem, children=True, allDescendents=True, fullPath=True, type="transform")
        if childrenList:
            for child in childrenList:
                if not "|Guide_Base|Guide_Base" in child:
                    newChild = newGuideNamespace+":"+child[child.rfind("|")+1:]
                    for transfAttr in transformAttrList:
                        try:
                            isLocked = cmds.getAttr(child+"."+transfAttr, lock=True)
                            cmds.setAttr(newChild+"."+transfAttr, lock=False)
                            cmds.setAttr(newChild+"."+transfAttr, cmds.getAttr(child+"."+transfAttr))
                            if isLocked:
                                cmds.setAttr(newChild+"."+transfAttr, lock=True)
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
            cmds.checkBox(self.allUIs["_JarCB"], edit=True, enable=False)
            cmds.checkBox(self.allUIs["_JadCB"], edit=True, enable=False)
            cmds.checkBox(self.allUIs["_JcrCB"], edit=True, enable=False)
            cmds.checkBox(self.allUIs["_JisCB"], edit=True, enable=False)
        elif chooseJnt == "dpARJoints":
            cmds.checkBox(self.allUIs["_JntCB"], edit=True, enable=True)
            cmds.checkBox(self.allUIs["_JarCB"], edit=True, enable=True)
            cmds.checkBox(self.allUIs["_JadCB"], edit=True, enable=True)
            cmds.checkBox(self.allUIs["_JcrCB"], edit=True, enable=True)
            cmds.checkBox(self.allUIs["_JisCB"], edit=True, enable=True)
            displayJnt = cmds.checkBox(self.allUIs["_JntCB"], query=True, value=True)
            displayJar = cmds.checkBox(self.allUIs["_JarCB"], query=True, value=True)
            displayJad = cmds.checkBox(self.allUIs["_JadCB"], query=True, value=True)
            displayJcr = cmds.checkBox(self.allUIs["_JcrCB"], query=True, value=True)
            displayJis = cmds.checkBox(self.allUIs["_JisCB"], query=True, value=True)
            for jointNode in allJointList:
                if cmds.objExists(jointNode+'.'+BASE_NAME+'joint'):
                    if displayJnt:
                        if jointNode.endswith("_Jnt"):
                            jointList.append(jointNode)
                    if displayJar:
                        if jointNode.endswith("_Jar"):
                            jointList.append(jointNode)
                    if displayJad:
                        if jointNode.endswith("_Jad"):
                            jointList.append(jointNode)
                    if displayJcr:
                        if jointNode.endswith("_Jcr"):
                            jointList.append(jointNode)
                    if displayJis:
                        if jointNode.endswith("_Jis"):
                            jointList.append(jointNode)
        
        # sort joints by name filter:
        jointName = cmds.textField(self.allUIs["jointNameTF"], query=True, text=True)
        if jointList:
            if jointName:
                sortedJointList = self.utils.filterName(jointName, jointList, " ")
            else:
                sortedJointList = jointList
        
        # populate the list:
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, removeAll=True)
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, append=sortedJointList)
        # atualize of footerB text:
        self.actualizeSkinFooter()
        
        
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
                            if not cmds.objExists(transformNameList[0]+"."+self.skin.ignoreSkinningAttr):
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
            geomList.append(self.lang['i074_attention'])
            geomList.append(self.lang['i075_moreOne'])
            geomList.append(self.lang['i076_sameName'])
            for sameName in sameNameList:
                geomList.append(sameName)
        
        # sort geometries by name filter:
        geoName = cmds.textField(self.allUIs["geoNameTF"], query=True, text=True)
        if geomList:
            if geoName:
                sortedGeoList = self.utils.filterName(geoName, geomList, " ")
            else:
                sortedGeoList = geomList
        
        # populate the list:
        cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, removeAll=True)
        if sameNameList:
            cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, lineFont=[(len(sortedGeoList)-len(sameNameList)-2, 'boldLabelFont'), (len(sortedGeoList)-len(sameNameList)-1, 'obliqueLabelFont'), (len(sortedGeoList)-len(sameNameList), 'obliqueLabelFont')], append=sortedGeoList)
        else:
            cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, append=sortedGeoList)
        # atualize of footerB text:
        self.actualizeSkinFooter()
    
    
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
    
    
    def actualizeSkinFooter(self, *args):
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
                cmds.text(self.allUIs["footerBText"], edit=True, label=str(nSelectedJoints)+" "+self.lang['i025_joints']+" "+str(nSelectedGeoms)+" "+self.lang['i024_geometries'])
            else:
                cmds.text(self.allUIs["footerBText"], edit=True, label=self.lang['i029_skinNothing'])
        except:
            pass
    
    
    def checkForUpdate(self, verbose=True, *args):
        """ Check if there's an update for this current script version.
            Output the result in a window.
        """
        print("\n", self.lang['i084_checkUpdate'])
        
        # compare current version with GitHub master
        rawResult = self.utils.checkRawURLForUpdate(self.dpARVersion, DPAR_RAWURL)
        
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
    
    
    def displayGuideGrp(self, value, *args):
        """ Change display hidden guide groups in the Outliner:
            dpAR_Temp_Grp
            dpAR_GuideMirror_Grp
        """
        if cmds.objExists(self.tempGrp):
            cmds.setAttr(self.tempGrp+".hiddenInOutliner", value)
        if cmds.objExists(self.guideMirrorGrp):
            cmds.setAttr(self.guideMirrorGrp+".hiddenInOutliner", value)
        mel.eval('source AEdagNodeCommon;')
        mel.eval('AEdagNodeCommonRefreshOutliners();')
    
    
    # Start working with Guide Modules:
    def startGuideModules(self, guideDir, action, layout, checkModuleList=None, path=None):
        """ Find and return the modules in the directory 'Modules'.
            Returns a list with the found modules.
        """
        if not path:
            # find path where 'dpAutoRig.py' is been executed:
            path = self.utils.findPath("dpAutoRig.py")
        if not self.loadedPath:
            print("dpAutoRigPath: "+path)
            self.loadedPath = True
        # list all guide modules:
        guideModuleList = self.utils.findAllModules(path, guideDir)
        if guideModuleList:
            if action == "start":
                # create guide buttons:
                for guideModule in guideModuleList:
                    self.createGuideButton(guideModule, guideDir, layout, path)
            elif action == "check":
                notFoundModuleList = []
                # verify the list if exists all elements in the folder:
                if checkModuleList:
                    for checkModule in checkModuleList:
                        if not checkModule in guideModuleList:
                            notFoundModuleList.append(checkModule)
                return notFoundModuleList
            elif action == "exists":
                return guideModuleList
            # avoid print again the same message:
            if guideDir == MODULES and not self.loadedModules:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedModules = True
            if guideDir == SCRIPTS and not self.loadedScripts:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedScripts = True
            if guideDir == CONTROLS and not self.loadedControls:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedControls = True
            if guideDir == COMBINED and not self.loadedCombined:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedCombined = True
            if guideDir == EXTRAS and not self.loadedExtras:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedExtras = True
            if guideDir == CHECKIN and not self.loadedCheckIn:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedCheckIn = True
            if guideDir == CHECKOUT and not self.loadedCheckOut:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedCheckOut = True
            if guideDir == REBUILDER and not self.loadedRebuilder:
                print(guideDir+" : "+str(guideModuleList))
                self.loadedRebuilder = True
            if guideDir == "" and not self.loadedAddOns:
                print(path+" : "+str(guideModuleList))
                self.loadedAddOns = True
        return guideModuleList
    
    
    def createGuideButton(self, guideModule, guideDir, layout, path=None):
        """ Create a guideButton for guideModule in the respective colMiddleLeftA guidesLayout.
        """
        # especific import command for guides storing theses guides modules in a variable:
        #guide = __import__("dpAutoRigSystem."+guideDir+"."+guideModule, {}, {}, [guideModule])
        basePath = self.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")

        # Sandbox the module import process so a single guide cannot crash the whole Autorig.
        # https://github.com/SqueezeStudioAnimation/dpAutoRigSystem/issues/28
        try:
            if guideDir:
                guideDir = guideDir.replace("/", ".")
                guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
                reload(guide)
            else:
                sys.path.append(path)
                guide = __import__(guideModule, {}, {}, [guideModule])
                reload(guide)
        except Exception as e:
            errorString = self.lang['e017_loadingExtension']+" "+guideModule+" : "+str(e.args)
            mel.eval('warning \"'+errorString+'\";')
            return

        # getting data from guide module:
        title = self.lang[guide.TITLE]
        description = self.lang[guide.DESCRIPTION]
        icon = guide.ICON
        if guideDir:
            # find path where 'dpAutoRig.py' is been executed to get the icon:
            path = self.utils.findPath("dpAutoRig.py")
        iconDir = path+icon
        iconInfo = self.utils.findPath("dpAutoRig.py")+"/Icons/"+INFO_ICON
        guideName = guide.CLASS_NAME
        
        # creating a basic layout for guide buttons:
        if guideDir == CONTROLS or guideDir == COMBINED.replace("/", "."):
            controlInstance = self.initExtraModule(guideModule, guideDir)
            cmds.iconTextButton(image=iconDir, label=guideName, annotation=guideName, height=32, width=32, command=partial(self.installControlModule, controlInstance, True), parent=self.allUIs[layout])
            self.controlInstanceList.append(controlInstance)
        else:
            moduleLayout = cmds.rowLayout(numberOfColumns=5, columnWidth3=(32, 55, 17), height=32, adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'left', 2)], parent=self.allUIs[layout])
            cmds.image(image=iconDir, width=32, parent=moduleLayout)

            if guideDir == MODULES:
                '''
                We need to passe the rigType parameters because the cmds.button command will send a False parameter that
                will be stock in the rigType if we don't pass the parameter
                https://stackoverflow.com/questions/24616757/maya-python-cmds-button-with-ui-passing-variables-and-calling-a-function
                '''
                cmds.button(label=title, height=32, command=partial(self.initGuide, guideModule, guideDir, dpBaseClass.RigType.biped), parent=moduleLayout)
            elif guideDir == SCRIPTS:
                cmds.button(label=title, height=32, command=partial(self.execScriptedGuide, guideModule, guideDir), parent=moduleLayout)
            elif guideDir == EXTRAS:
                cmds.button(label=title, height=32, width=200, command=partial(self.initExtraModule, guideModule, guideDir), parent=moduleLayout)
            elif guideDir == CHECKIN.replace("/", ".") or guideDir == CHECKOUT.replace("/", ".") or guideDir == "": #addOns
                validatorInstance = self.initExtraModule(guideModule, guideDir)
                validatorInstance.actionCB = cmds.checkBox(label=title, value=True, changeCommand=validatorInstance.changeActive)
                validatorInstance.firstBT = cmds.button(label=validatorInstance.firstBTLabel, width=45, command=partial(validatorInstance.runAction, True), backgroundColor=(0.5, 0.5, 0.5), enable=validatorInstance.firstBTEnable, parent=moduleLayout)
                validatorInstance.secondBT = cmds.button(label=validatorInstance.secondBTLabel.capitalize(), width=45, command=partial(validatorInstance.runAction, False), backgroundColor=(0.5, 0.5, 0.5), enable=validatorInstance.secondBTEnable, parent=moduleLayout)
                if guideDir == CHECKIN.replace("/", "."):
                    self.checkInInstanceList.append(validatorInstance)
                elif guideDir == CHECKOUT.replace("/", "."):
                    self.checkOutInstanceList.append(validatorInstance)
                else: #addOns
                    self.checkAddOnsInstanceList.append(validatorInstance)
                    if validatorInstance.customName:
                        cmds.checkBox(validatorInstance.actionCB, edit=True, label=validatorInstance.customName)
                        validatorInstance.title = validatorInstance.customName
            elif guideDir == REBUILDER.replace("/", "."):
                rebuilderInstance = self.initExtraModule(guideModule, guideDir)
                rebuilderInstance.actionCB = cmds.checkBox(label=title, value=True, changeCommand=rebuilderInstance.changeActive)
                rebuilderInstance.firstBT = cmds.button(label=rebuilderInstance.firstBTLabel, width=45, command=partial(rebuilderInstance.runAction, True), backgroundColor=(0.5, 0.5, 0.5), enable=rebuilderInstance.firstBTEnable, parent=moduleLayout)
                rebuilderInstance.secondBT = cmds.button(label=rebuilderInstance.secondBTLabel, width=45, command=partial(rebuilderInstance.runAction, False), backgroundColor=(0.5, 0.5, 0.5), enable=rebuilderInstance.secondBTEnable, parent=moduleLayout)
                self.rebuilderInstanceList.append(rebuilderInstance)

            cmds.iconTextButton(image=iconInfo, height=30, width=17, style='iconOnly', command=partial(self.logger.infoWin, guide.TITLE, guide.DESCRIPTION, None, 'center', 305, 250), parent=moduleLayout)
        cmds.setParent('..')
    
    
    #@dpUtils.profiler
    def initGuide(self, guideModule, guideDir, rigType=dpBaseClass.RigType.biped, number=None, *args):
        """ Create a guideModuleReference (instance) of a further guideModule that will be rigged (installed).
            Returns the guide instance initialised.
        """
        # creating unique namespace:
        cmds.namespace(setNamespace=":")
        # generate the current moduleName added the next new number suffix:
        if number:
            userSpecName = BASE_NAME + str(number)
        else:
            userSpecName = BASE_NAME + self.utils.findLastNumber()
        # especific import command for guides storing theses guides modules in a variable:
        basePath = self.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        self.guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(self.guide)
        # get the CLASS_NAME from guideModule:
        guideClass = getattr(self.guide, self.guide.CLASS_NAME)
        # initialize this guideModule as an guide Instance:
        guideInstance = guideClass(self, userSpecName, rigType, number=number)
        self.moduleInstancesList.append(guideInstance)
        # edit the footer A text:
        self.allGuidesList.append([guideModule, userSpecName])
        self.modulesToBeRiggedList = self.utils.getModulesToBeRigged(self.moduleInstancesList)
        cmds.text(self.allUIs["footerAText"], edit=True, label=str(len(self.modulesToBeRiggedList)) +" "+ self.lang['i005_footerA'])
        return guideInstance
    
    
    def initExtraModule(self, guideModule, guideDir=None, *args):
        """ Create a guideModuleReference (instance) of a further guideModule that will be rigged (installed).
            Returns the guide instance initialised.
        """
        if guideDir:
            # especific import command for guides storing theses guides modules in a variable:
            basePath = self.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
            self.guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        else:
            self.guide = __import__(guideModule, {}, {}, [guideModule])
        reload(self.guide)
        # get the CLASS_NAME from extraModule:
        guideClass = getattr(self.guide, self.guide.CLASS_NAME)
        # initialize this extraModule as an Instance:
        guideInstance = guideClass(self)
        return guideInstance
    
    
    def installControlModule(self, controlInstance, useUI, *args):
        """  Start the creation of this Control module using the UI info.
        """
        controlInstance.cvMain(useUI)
    
    
    def execScriptedGuide(self, guideModule, guideDir, *args):
        """ Create a instance of a scripted guide that will create several guideModules in order to integrate them.
        """
        # import this scripted module:
        basePath = self.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(guide)
        # get the CLASS_NAME from guideModule:
        startScriptFunction = getattr(guide, guide.CLASS_NAME)
        # execute this scriptedGuideModule:
        startScriptFunction(self)
    
    
    def clearGuideLayout(self, *args):
        """ Clear current guide layout before reload modules.
        """
        self.allUIs["editSelectedModuleLayoutA"] = cmds.frameLayout('editSelectedModuleLayoutA', edit=True, label=self.lang['i011_editSelected'], collapsable=True, collapse=False, parent=self.allUIs["riggingTabLayout"])
        cmds.deleteUI(self.allUIs["modulesLayoutA"])
        cmds.deleteUI(self.allUIs["selectedModuleLayout"])
        self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=200, parent=self.allUIs["colMiddleRightA"])
        self.allUIs["selectedModuleLayout"] = cmds.columnLayout('selectedModuleLayout', adjustableColumn=True, parent=self.allUIs["editSelectedModuleLayoutA"])


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
        path = self.utils.findPath("dpAutoRig.py")
        guideDir = MODULES
        # find all module names:
        moduleNameInfo = self.utils.findAllModuleNames(path, guideDir)
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

        self.clearGuideLayout()
        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.allGuidesList:
            # load again the modules:
            guideFolder = self.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")+"."+MODULES
            # this list will be used to rig all modules pressing the RIG button:
            for module in self.allGuidesList:
                mod = __import__(guideFolder+"."+module[0], {}, {}, [module[0]])
                reload(mod)
                # identify the guide modules and add to the moduleInstancesList:
                moduleClass = getattr(mod, mod.CLASS_NAME)
                dpUIinst = self
                if cmds.attributeQuery("rigType", node=module[2], ex=True):
                    curRigType = cmds.getAttr(module[2] + ".rigType")
                    moduleInst = moduleClass(dpUIinst, module[1], curRigType)
                else:
                    if cmds.attributeQuery("Style", node=module[2], ex=True):
                        iStyle = cmds.getAttr(module[2] + ".Style")
                        if (iStyle == 0 or iStyle == 1):
                            moduleInst = moduleClass(dpUIinst, module[1], dpBaseClass.RigType.biped)
                        else:
                            moduleInst = moduleClass(dpUIinst, module[1], dpBaseClass.RigType.quadruped)
                    else:
                        moduleInst = moduleClass(dpUIinst, module[1], dpBaseClass.RigType.default)
                self.moduleInstancesList.append(moduleInst)
                # reload pinGuide scriptJob:
                self.ctrls.startPinGuide(module[2])
        # edit the footer A text:
        self.modulesToBeRiggedList = self.utils.getModulesToBeRigged(self.moduleInstancesList)
        cmds.text(self.allUIs["footerAText"], edit=True, label=str(len(self.modulesToBeRiggedList)) +" "+ self.lang['i005_footerA'])
    

    def checkImportedGuides(self, askUser=True, *args):
        """ This method will check if there's imported dpGuides in the scene and ask if the user wants to delete the namespace.
            Use a recursive method to remove imported of imported guides.
        """
        importedNamespaceList = []
        self.modulesToBeRiggedList = self.utils.getModulesToBeRigged(self.moduleInstancesList)
        currentCustomNameList = list(map(lambda guideModule : cmds.getAttr(guideModule.moduleGrp+".customName"), self.modulesToBeRiggedList))
        cmds.namespace(setNamespace=':')
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        if namespaceList:
            for n, name in enumerate(namespaceList):
                if name != "UI" and name != "shared":
                    if name.count(":") > 0:
                        if name.find("_dpAR_") != -1:
                            if askUser:
                                # open dialog to confirm merge namespaces:
                                yesTxt = self.lang['i071_yes']
                                noTxt = self.lang['i072_no']
                                result = cmds.confirmDialog(title=self.lang['i205_guide'], message=self.lang['i206_removeNamespace'], 
                                                            button=[yesTxt, noTxt], defaultButton=yesTxt, cancelButton=noTxt, dismissString=noTxt)
                                if result == yesTxt:
                                    askUser = False
                                else:
                                    return
                            importedNamespaceList.append(name)
            if importedNamespaceList:
                # review guide custom name before remove namespaces
                for name in importedNamespaceList:
                    if cmds.objExists(name+":Guide_Base.customName"):
                        n = 1
                        oldCustomName = cmds.getAttr(name+":Guide_Base.customName")
                        if oldCustomName:
                            baseName = oldCustomName
                            while oldCustomName in currentCustomNameList:
                                oldCustomName = baseName+str(n)
                                n += 1
                            cmds.setAttr(name+":Guide_Base.customName", oldCustomName, type="string")
                            currentCustomNameList.append(oldCustomName)
                # remove namespaces
                for name in importedNamespaceList:
                    if ":" in name:
                        if cmds.namespace(exists=name):
                            namespaceString = name.split(":")[0]
                            cmds.namespace(removeNamespace=namespaceString, mergeNamespaceWithRoot=True)
                            print(f"{self.lang['m206_mergeNamespace']}: {namespaceString}")
                            self.checkImportedGuides(False)
                            break
    

    def checkGuideNets(self, *args):
        """ Verify if there are guideNet nodes to existing guides, otherwise it'll call the updatedGuides tool to fix it.
        """
        self.modulesToBeRiggedList = self.utils.getModulesToBeRigged(self.moduleInstancesList)
        for item in self.modulesToBeRiggedList:
            if not item.guideNet:
                self.initExtraModule("dpUpdateGuides", EXTRAS)
                break


    def setPrefix(self, *args):
        """ Get the text entered in the textField and change it to normal.
        """
        # get the entered text:
        enteredText = cmds.textField(self.allUIs["prefixTextField"], query=True, text=True)
        # call utils to return the normalized text:
        prefixName = self.utils.normalizeText(enteredText, prefixMax=10)
        # edit the prefixTextField with the prefixName:
        if len(prefixName) != 0:
            cmds.textField(self.allUIs["prefixTextField"], edit=True, text=prefixName+"_")


    def getValidatorsAddOns(self, *args):
        """ Return a list of Validator's AddOns to load.
        """
        if os.path.exists(self.pipeliner.pipeData['addOnsPath']):
            self.validatorAddOnsModuleList = self.startGuideModules("", "exists", None, path=self.pipeliner.pipeData['addOnsPath'])
            return self.validatorAddOnsModuleList


    def loadPipelineValidatorPresets(self, *args):
        """ Load the Validator's presets from the pipeline path.
        """
        if os.path.exists(self.pipeliner.pipeData['presetsPath']):
            studioPreset, studioPresetDic = self.getJsonFileInfo(self.pipeliner.pipeData['presetsPath']+"/", True)
            if studioPreset:
                self.validatorPresetList.insert(0, studioPreset[0])
                self.validatorPresetDic.update(studioPresetDic)

    
    def setValidatorPreset(self, *args):
        self.validatorPresetName = self.getCurrentMenuValue(self.validatorPresetList)
        checkInstanceList = self.checkInInstanceList + self.checkOutInstanceList + self.checkAddOnsInstanceList
        if checkInstanceList:
            for presetKey in self.validatorPresetDic[self.validatorPresetName]:
                for validatorModule in checkInstanceList:
                    if presetKey == validatorModule.guideModuleName:
                        validatorModule.changeActive(self.validatorPresetDic[self.validatorPresetName][validatorModule.guideModuleName])


    def changeActiveAllModules(self, instList, value, *args):
        """ Set all module instances active attribute as True or False.
            Used by validators and rebuilders.
        """
        if instList:
            for inst in instList:
                inst.changeActive(value)


    def runSelectedActions(self, actionInstList, firstMode, verbose=True, stopIfFoundBlock=False, publishLog=None, actionType="v000_validator", *args):
        """ Run the code for each active validator/rebuilder instance.
            firstMode = True for verify/export
                      = False for fix/import
        """
        self.resetAllButtonColors()
        actionResultData = {}
        logText = ""
        if publishLog:
            logText = "\nPublisher"
            logText += "\nScene: "+publishLog["scene"]
            logText += "\nPublished: "+publishLog["published"]
            logText += "\nExported: "+publishLog["exportPath"]
            logText += "\nComments: "+publishLog["comments"]+"\n"
        if actionInstList:
            progressAmount = 0
            maxProcess = len(actionInstList)
            cmds.progressWindow(title=self.lang[actionType], progress=progressAmount, status=self.lang[actionType]+': 0%', isInterruptable=False)
            for a, actionInst in enumerate(actionInstList):
                if actionInst.active:
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(actionInst.guideModuleName+': '+repr(progressAmount)))
                    actionInst.verbose = False
                    actionResultData[actionInst.guideModuleName] = actionInst.runAction(firstMode)
                    actionInst.verbose = True
                    if stopIfFoundBlock:
                        if True in actionInst.foundIssueList:
                            if False in actionInst.resultOkList:
                                return actionResultData, True, a
        if actionResultData:
            dataList = list(actionResultData.keys())
            dataList.sort()
            for i, dataItem in enumerate(dataList):
                logText += actionResultData[dataItem]["logText"]
                if i != len(dataList)-1:
                    logText += "\n"
            heightSize = len(dataList)
        else:
            logText += "\n"+self.lang['i207_notMarked']
            heightSize = 2
        logText = self.pipeliner.getToday(True)+"\n"+logText
        if verbose:
            self.logger.infoWin('i019_log', actionType, logText, "left", 250, (150+(heightSize)*13))
            print("\n-------------\n"+self.lang[actionType]+"\n"+logText)
            if publishLog:
                actionResultData["Publisher"] = publishLog
            if not self.utils.exportLogDicToJson(actionResultData, subFolder=self.dpData+"/"+self.dpLog):
                print(self.lang['i201_saveScene'])
        cmds.progressWindow(endProgress=True)
        return actionResultData, False, 0

    
    def donateWin(self, *args):
        """ Simple window with links to donate in order to support this free and openSource code via PayPal.
        """
        # declaring variables:
        self.donate_title       = 'dpAutoRig - v'+self.dpARVersion+' - '+self.lang['i167_donate']
        self.donate_description = self.lang['i168_donateDesc']
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
        brPaypalButton = cmds.button('brlPaypalButton', label=self.lang['i167_donate']+" - R$ - Real", align=self.donate_align, command=partial(self.utils.visitWebSite, DONATE+"BRL"), parent=donateColumnLayout)
        #usdPaypalButton = cmds.button('usdPaypalButton', label=self.lang['i167_donate']+" - USD - Dollar", align=self.donate_align, command=partial(self.utils.visitWebSite, DONATE+"USD"), parent=donateColumnLayout)
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
        dpUpdateWin = cmds.window('dpUpdateWindow', title='dpAutoRigSystem - '+self.lang['i089_update'], iconName='dpInfo', widthHeight=(self.update_winWidth, self.update_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        updateLayout = cmds.columnLayout('updateLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpUpdateWin)
        if self.update_text:
            updateDesc = cmds.text("\n"+self.lang[self.update_text], align="center", parent=updateLayout)
            cmds.text("\n"+self.dpARVersion+self.lang['i090_currentVersion'], align="left", parent=updateLayout)
        if self.update_remoteVersion:
            cmds.text(self.update_remoteVersion+self.lang['i091_onlineVersion'], align="left", parent=updateLayout)
            cmds.separator(height=30)
            if self.update_remoteLog:
                remoteLog = self.update_remoteLog.replace("\\n", "\n")
                cmds.text(self.lang['i171_updateLog']+":\n", align="center", parent=updateLayout)
                cmds.text(remoteLog, align="left", parent=updateLayout)
                cmds.separator(height=30)
            whatsChangedButton = cmds.button('whatsChangedButton', label=self.lang['i117_whatsChanged'], align="center", command=partial(self.utils.visitWebSite, DPAR_WHATSCHANGED), parent=updateLayout)
            visiteGitHubButton = cmds.button('visiteGitHubButton', label=self.lang['i093_gotoWebSite'], align="center", command=partial(self.utils.visitWebSite, DPAR_GITHUB), parent=updateLayout)
            downloadButton = cmds.button('downloadButton', label=self.lang['i094_downloadUpdate'], align="center", command=partial(self.downloadUpdate, DPAR_MASTERURL, "zip"), parent=updateLayout)
            installButton = cmds.button('installButton', label=self.lang['i095_installUpdate'], align="center", command=partial(self.installUpdate, DPAR_MASTERURL, self.update_remoteVersion), parent=updateLayout)
        # automatically check for updates:
        cmds.separator(height=30)
        self.autoCheckUpdateCB = cmds.checkBox('autoCheckUpdateCB', label=self.lang['i092_autoCheckUpdate'], align="left", value=self.userDefAutoCheckUpdate, changeCommand=self.setAutoCheckUpdatePref, parent=updateLayout)
        cmds.separator(height=30)
        # call Update Window:
        cmds.showWindow(dpUpdateWin)
        print(self.lang[self.update_text])
    
    
    def downloadUpdate(self, url, ext, *args):
        """ Download file from given url adrees and ask user to choose folder and file name to save
        """
        extFilter = "*."+ext
        downloadFolder = cmds.fileDialog2(fileFilter=extFilter, dialogStyle=2)
        if downloadFolder:
            cmds.progressWindow(title='Download Update', progress=50, status='Downloading...', isInterruptable=False)
            try:
                urllib.request.urlretrieve(url, downloadFolder[0])
                self.logger.infoWin('i094_downloadUpdate', 'i096_downloaded', downloadFolder[0]+'\n\n'+self.lang['i018_thanks'], 'center', 205, 270)
                # closes dpUpdateWindow:
                if cmds.window('dpUpdateWindow', query=True, exists=True):
                    cmds.deleteUI('dpUpdateWindow', window=True)
            except:
                self.logger.infoWin('i094_downloadUpdate', 'e009_failDownloadUpdate', downloadFolder[0]+'\n\n'+self.lang['i097_sorry'], 'center', 205, 270)
            cmds.progressWindow(endProgress=True)
    
    
    def keepJsonFilesWhenUpdate(self, currentDir, tempUpdateDir, *args):
        """ Check in given folder if we have custom json files and keep then when we install a new update.
            It will just check if there are user created json files, and copy them to temporarily extracted update folder.
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
        btContinue = self.lang['i174_continue']
        btCancel = self.lang['i132_cancel']
        confirmAutoInstall = cmds.confirmDialog(title=self.lang['i098_installing'], message=self.lang['i172_updateManual'], button=[btContinue, btCancel], defaultButton=btContinue, cancelButton=btCancel, dismissString=btCancel)
        if confirmAutoInstall == btContinue:
            print(self.lang['i098_installing'])
            # declaring variables:
            dpAR_Folder = "dpAutoRigSystem"
            dpAR_DestFolder = self.utils.findPath("dpAutoRig.py")
            
            # progress window:
            installAmount = 0
            cmds.progressWindow(title=self.lang['i098_installing'], progress=installAmount, status='Installing: 0%', isInterruptable=False)
            maxInstall = 100
            
            try:
                # get remote file from url:
                remoteSource = urllib.request.urlopen(url)

                installAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + repr(installAmount)))
                
                # read the downloaded Zip file stored in the RAM memory:
                dpAR_Zip = zipfile.ZipFile(io.BytesIO(remoteSource.read()))

                installAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + repr(installAmount)))

                # list Zip file contents in order to extract them in a temporarily folder:
                zipNameList = dpAR_Zip.namelist()
                for fileName in zipNameList:
                    if dpAR_Folder in fileName:
                        dpAR_Zip.extract(fileName, dpAR_DestFolder)
                dpAR_Zip.close()

                installAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + repr(installAmount)))
                
                # declare temporarily folder:
                dpAR_TempDir = dpAR_DestFolder+"/"+zipNameList[0]+dpAR_Folder

                # store custom presets in order to avoid overwrite them when installing the update:
                self.keepJsonFilesWhenUpdate(dpAR_DestFolder+"/"+LANGUAGES, dpAR_TempDir+"/"+LANGUAGES)
                self.keepJsonFilesWhenUpdate(dpAR_DestFolder+"/"+CONTROLS_PRESETS, dpAR_TempDir+"/"+CONTROLS_PRESETS)
                # keep dpPipelineInfo data
                if os.path.exists(dpAR_DestFolder+"/_dpPipelineSettings.json"):
                    shutil.copy2(os.path.join(dpAR_DestFolder, "_dpPipelineSettings.json"), dpAR_TempDir)
                if os.path.exists(dpAR_DestFolder+"/dpPipelineInfo.json"):
                    shutil.copy2(os.path.join(dpAR_DestFolder, "dpPipelineInfo.json"), dpAR_TempDir)

                # remove all old live files and folders for this current version, that means delete myself, OMG!
                for eachFolder in next(os.walk(dpAR_DestFolder))[1]:
                    if not "-"+dpAR_Folder+"-" in eachFolder:
                        shutil.rmtree(dpAR_DestFolder+"/"+eachFolder)
                for eachFile in next(os.walk(dpAR_DestFolder))[2]:
                    os.remove(dpAR_DestFolder+"/"+eachFile)

                # pass in all files to copy them (doing the simple installation):
                for sourceDir, dirList, fileList in os.walk(dpAR_TempDir):       
                    # declare destination directory:
                    destDir = sourceDir.replace(dpAR_TempDir, dpAR_DestFolder, 1).replace("\\", "/")
                    
                    installAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + repr(installAmount)))
                    
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
                        cmds.progressWindow(edit=True, maxValue=maxInstall, progress=installAmount, status=('Installing: ' + repr(installAmount)))

                # delete the temporarily folder used to download and install the update:
                folderToDelete = dpAR_DestFolder+"/"+zipNameList[0]
                shutil.rmtree(folderToDelete)

                # report finished update installation:
                self.logger.infoWin('i095_installUpdate', 'i099_installed', '\n\n'+newVersion+'\n\n'+self.lang['i173_reloadScript']+'\n\n'+self.lang['i018_thanks'], 'center', 205, 270)
                # closes dpUpdateWindow:
                if cmds.window('dpUpdateWindow', query=True, exists=True):
                    cmds.deleteUI('dpUpdateWindow', window=True)
                # quit UI in order to force user to refresh dpAutoRigSystem creating a new instance:
                self.deleteExistWindow()
            except:
                # report fail update installation:
                self.logger.infoWin('i095_installUpdate', 'e010_failInstallUpdate', '\n\n'+newVersion+'\n\n'+self.lang['i097_sorry'], 'center', 205, 270)
            cmds.progressWindow(endProgress=True)
        else:
            print(self.lang['i038_canceled'])
    
    
    def setAutoCheckUpdatePref(self, currentValue, *args):
        """ Set the optionVar for auto check update preference as stored userDefAutoCheckUpdate read variable.
        """
        cmds.optionVar(intValue=('dpAutoRigAutoCheckUpdate', int(currentValue)))
        self.userDefAutoCheckUpdate = currentValue


    def setAutoCheckAgreePref(self, currentValue, *args):
        """ Set the optionVar for auto check agree terms and conditions preference as stored userDefAgreeTerms read variable.
        """
        cmds.optionVar(intValue=('dpAutoRigAgreeTermsCond', int(currentValue)))
        self.userDefAgreeTerms = currentValue
    
    
    def autoCheckOptionVar(self, checkOptVar,  lastDateOptVar, mode, *args):
        """ Store user choose about automatically check for update or agree terms and conditions in an optionVar.
            If active, try to check for update or location once a day.
        """
        firstTimeOpenDPAR = False
        # verify if there is an optionVar of last optionVar checkBox choose value by user in the maya system:
        autoCheckExists = cmds.optionVar(exists=checkOptVar)
        if not autoCheckExists:
            cmds.optionVar(intValue=(checkOptVar, 1))
            firstTimeOpenDPAR = True
        
        # get its value puting in a self variable:
        optVarValue = cmds.optionVar(query=checkOptVar)
        if mode == "update":
            self.userDefAutoCheckUpdate = optVarValue
        else: #terms
            self.userDefAgreeTerms = optVarValue
        if optVarValue == 1:
            # verify if there is an optionVar for store the date of the lastest optionVar ran in order to avoid many hits in the GitHub server:
            todayDate = str(datetime.datetime.now().date())
            lastAutoCheckExists = cmds.optionVar(exists=lastDateOptVar)
            if not lastAutoCheckExists:
                cmds.optionVar(stringValue=(lastDateOptVar, todayDate))
            # get its value puting in a variable:
            lastDateAutoCheck = cmds.optionVar(query=lastDateOptVar)
            if not lastDateAutoCheck == todayDate:
                cmds.optionVar(stringValue=(lastDateOptVar, todayDate))
                if mode == "update":
                    self.checkForUpdate(verbose=False)
                else: # agree terms and cond
                    self.getLocalData()
        
        # force checkForUpdate if it's the first time openning the dpAutoRigSystem in this computer:
        if firstTimeOpenDPAR:
            if mode == "update":
                self.checkForUpdate(verbose=True)
            else: #terms
                self.checkTermsAndCond()

    
    def getLocalData(self, *args):
        """ Collect info for statistical purposes.
        """
        locDic = False
        try:
            locResponse = urllib.request.urlopen(LOCATION_URL)
            locDic = json.loads(locResponse.read())
        except:
            pass
        if locDic:
            infoData = {}
            infoData['country'] = locDic['country']
            infoData['region'] = locDic['region']
            infoData['city'] = locDic['city']
            infoData['user'] = getpass.getuser()
            infoData['host'] = socket.gethostname()
            infoData['os'] = platform.system()
            infoData['lang'] = self.langName
            infoData['Maya'] = cmds.about(version=True)
            infoData['dpAR'] = self.dpARVersion
            #print(infoData)
            if infoData:
                wh = self.utils.mountWH(dpPipeliner.DISCORD_URL, self.pipeliner.pipeData['h000_location'])
                self.packager.toDiscord(wh, str(infoData))

    
    def checkTermsAndCond(self, *args):
        """ Create a window to ask user if agree to terms and conditions.
        """
        terms_winWidth  = 205
        terms_winHeight = 200
        # creating Terms and Conditions Window:
        if cmds.window('dpTermsCondWindow', query=True, exists=True):
            cmds.deleteUI('dpTermsCondWindow', window=True)
        dpTermsCondWin = cmds.window('dpTermsCondWindow', title='dpAutoRigSystem - '+self.lang['i281_termsCond'], iconName='dpInfo', widthHeight=(terms_winWidth, terms_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        termsLayout = cmds.columnLayout('termsLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpTermsCondWin)
        cmds.text("\n"+self.lang['i282_termsCondDesc'], align="center", parent=termsLayout)
        # agreement:
        cmds.separator(height=30)
        self.autoCheckTermsCondCB = cmds.checkBox('autoCheckTermsCondCB', label=self.lang['i280_iAgreeTermsCond'], align="left", value=self.userDefAgreeTerms, changeCommand=self.setAutoCheckAgreePref, parent=termsLayout)
        cmds.separator(height=30)
        # call window:
        cmds.showWindow(dpTermsCondWin)


    ###################### End: UI
    
    
    ###################### Start: Rigging Modules Instances
    def checkIfNeedCreateAllGrp(self):
        """ Verify if there's a All_Grp, masterGrp and return a boolean if need to create one.
        """
        masterGrpList = []
        allTransformList = cmds.ls(selection=False, type="transform")
        #Get all the masterGrp nodes and ensure it isn't referenced
        for item in allTransformList:
            if cmds.objExists(item+"."+MASTER_ATTR):
                if not cmds.referenceQuery(item, isNodeReferenced=True):
                    masterGrpList.append(item)
        if masterGrpList:
            # validate master (All_Grp) node
            # If it doesn't work, the user need to clean the current scene to avoid duplicated names, for the moment.
            for nodeGrp in masterGrpList:
                if self.validateMasterGrp(nodeGrp):
                    self.masterGrp = nodeGrp
                    return False
        return True


    '''
        Generic function to create base group
        TODO maybe move it to utils?
    '''
    def getBaseGrp(self, sAttrName, sGrpName):
        if not cmds.objExists(sGrpName):
            cmds.createNode("transform", name=sGrpName)
        if not cmds.objExists(self.masterGrp+"."+sAttrName):
            cmds.addAttr(self.masterGrp, longName=sAttrName, attributeType="message")
        if not cmds.listConnections(self.masterGrp+"."+sAttrName, destination=False, source=True):
            cmds.connectAttr(sGrpName+".message", self.masterGrp+"."+sAttrName, force=True)
        return sGrpName


    '''
        Generic function to create base controller
        TODO maybe move it to utils?
    '''
    def getBaseCtrl(self, sCtrlType, sAttrName, sCtrlName, fRadius, iDegree=1):
        nCtrl = sCtrlName
        self.ctrlCreated = False
        if not cmds.objExists(self.masterGrp+"."+sAttrName):
            cmds.addAttr(self.masterGrp, longName=sAttrName, attributeType="message")
        if not cmds.objExists(sCtrlName):
            if (sCtrlName != (self.prefix + "Option_Ctrl")):
                nCtrl = self.ctrls.cvControl(sCtrlType, sCtrlName, r=fRadius, d=iDegree, dir="+X")
            else:
                nCtrl = self.ctrls.cvCharacter(sCtrlType, sCtrlName, r=(fRadius*0.2))
            cmds.setAttr(nCtrl+".rotateOrder", 3)
            cmds.connectAttr(sCtrlName+".message", self.masterGrp+"."+sAttrName, force=True)
            self.ctrlCreated = True
        return nCtrl
        

    '''
        Ensure that the main group and Ctrl of the rig exist in the scene or else create them
        TODO maybe move it to utils?
    '''
    def createBaseRigNode(self):
        sAllGrp = "All_Grp"
        localTime = str( time.asctime( time.localtime(time.time()) ) )
        needCreateAllGrp = self.checkIfNeedCreateAllGrp()
        if needCreateAllGrp:
            if cmds.objExists(sAllGrp):
                # rename existing All_Grp node without connections as All_Grp_Old
                cmds.rename(sAllGrp, sAllGrp+"_Old")
            #Create Master Grp
            self.masterGrp = cmds.createNode("transform", name=self.prefix+sAllGrp)
            # adding All_Grp attributes
            cmds.addAttr(self.masterGrp, longName=MASTER_ATTR, attributeType="bool")
            cmds.addAttr(self.masterGrp, longName="dpAutoRigSystem", dataType="string")
            cmds.addAttr(self.masterGrp, longName="date", dataType="string")
            # system:
            cmds.addAttr(self.masterGrp, longName="maya", dataType="string")
            cmds.addAttr(self.masterGrp, longName="system", dataType="string")
            cmds.addAttr(self.masterGrp, longName="language", dataType="string")
            cmds.addAttr(self.masterGrp, longName="preset", dataType="string")
            # author:
            cmds.addAttr(self.masterGrp, longName="author", dataType="string")
            # rig info to be updated:
            cmds.addAttr(self.masterGrp, longName="geometryList", dataType="string")
            cmds.addAttr(self.masterGrp, longName="controlList", dataType="string")
            cmds.addAttr(self.masterGrp, longName="prefix", dataType="string")
            cmds.addAttr(self.masterGrp, longName="name", dataType="string")
            # setting All_Grp data
            cmds.setAttr(self.masterGrp+"."+MASTER_ATTR, True)
            cmds.setAttr(self.masterGrp+".dpAutoRigSystem", DPAR_GITHUB, type="string")
            cmds.setAttr(self.masterGrp+".date", localTime, type="string")
            cmds.setAttr(self.masterGrp+".maya", cmds.about(version=True), type="string")
            cmds.setAttr(self.masterGrp+".system", self.dpARVersion, type="string")
            cmds.setAttr(self.masterGrp+".language", self.langName, type="string")
            cmds.setAttr(self.masterGrp+".preset", self.presetName, type="string")
            cmds.setAttr(self.masterGrp+".author", getpass.getuser(), type="string")
            cmds.setAttr(self.masterGrp+".prefix", self.prefix, type="string")
            cmds.setAttr(self.masterGrp+".name", self.masterGrp, type="string")
            # add date data log:
            cmds.addAttr(self.masterGrp, longName="lastModification", dataType="string")
            # add pipeline data:
            cmds.addAttr(self.masterGrp, longName="firstGuidesFile", dataType="string")
            cmds.addAttr(self.masterGrp, longName="lastGuidesFile", dataType="string")
            cmds.addAttr(self.masterGrp, longName="publishedFromFile", dataType="string")
            cmds.addAttr(self.masterGrp, longName="assetName", dataType="string")
            cmds.addAttr(self.masterGrp, longName="comment", dataType="string")
            cmds.addAttr(self.masterGrp, longName="modelVersion", attributeType="long", defaultValue=0, minValue=0)
            # set data
            cmds.setAttr(self.masterGrp+".firstGuidesFile", cmds.file(query=True, sceneName=True), type="string")
            cmds.setAttr(self.masterGrp+".lastGuidesFile", cmds.file(query=True, sceneName=True), type="string")
            # module counts:
            for guideType in self.guideModuleList:
                cmds.addAttr(self.masterGrp, longName=guideType+"Count", attributeType="long", defaultValue=0)
            # set outliner color
            self.ctrls.colorShape([self.masterGrp], [1, 1, 1], outliner=True) #white

        # update data
        cmds.setAttr(self.masterGrp+".lastModification", localTime, type="string")
        # setting pipeline data
        if not cmds.objExists(self.masterGrp+".lastGuidesFile"):
            cmds.addAttr(self.masterGrp, longName="lastGuidesFile", dataType="string")
        cmds.setAttr(self.masterGrp+".lastGuidesFile", cmds.file(query=True, sceneName=True), type="string")

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
        # set outliner color
        self.ctrls.colorShape([self.ctrlsGrp], [0, 0.65, 1], outliner=True) #blue
        self.ctrls.colorShape([self.dataGrp], [1, 1, 0], outliner=True) #yellow
        self.ctrls.colorShape([self.renderGrp], [1, 0.45, 0], outliner=True) #orange

        #Arrange Hierarchy if using an original setup or preserve existing if integrating to another studio setup
        if needCreateAllGrp:
            if self.masterGrp == self.prefix+sAllGrp:
                cmds.parent(self.modelsGrp, self.ctrlsGrp, self.dataGrp, self.renderGrp, self.proxyGrp, self.fxGrp, self.masterGrp)
                cmds.parent(self.staticGrp, self.scalableGrp, self.blendShapesGrp, self.wipGrp, self.dataGrp)
        cmds.select(None)

        #Hide Models and FX groups
        try:
            cmds.setAttr(self.modelsGrp+".visibility", 0)
            cmds.setAttr(self.fxGrp+".visibility", 0)
        except:
            pass

        #Lock and Hide attributes
        aToLock = [self.masterGrp,
                   self.modelsGrp,
                   self.ctrlsGrp,
                   self.renderGrp,
                   self.dataGrp,
                   self.proxyGrp,
                   self.fxGrp,
                   self.staticGrp,
                   self.ctrlsVisGrp]
        self.ctrls.setLockHide(aToLock, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        #Control Setup
        fMasterRadius = self.ctrls.dpCheckLinearUnit(10)
        self.masterCtrl = self.getBaseCtrl("id_004_Master", "masterCtrl", self.prefix+"Master_Ctrl", fMasterRadius, iDegree=3)
        self.globalCtrl = self.getBaseCtrl("id_003_Global", "globalCtrl", self.prefix+"Global_Ctrl", self.ctrls.dpCheckLinearUnit(13))
        self.rootCtrl   = self.getBaseCtrl("id_005_Root", "rootCtrl", self.prefix+"Root_Ctrl", self.ctrls.dpCheckLinearUnit(8))
        self.rootPivotCtrl = self.getBaseCtrl("id_099_RootPivot", "rootPivotCtrl", self.prefix+"Root_Pivot_Ctrl", self.ctrls.dpCheckLinearUnit(1), iDegree=3)
        needConnectPivotAttr = False
        if (self.ctrlCreated):
            needConnectPivotAttr = True
            self.rootPivotCtrlGrp = self.utils.zeroOut([self.rootPivotCtrl])[0]
            cmds.parent(self.rootPivotCtrlGrp, self.rootCtrl)
            self.changeRootToCtrlsVisConstraint()
        self.optionCtrl = self.getBaseCtrl("id_006_Option", "optionCtrl", self.prefix+"Option_Ctrl", self.ctrls.dpCheckLinearUnit(16))
        if (self.ctrlCreated):
            cmds.makeIdentity(self.optionCtrl, apply=True)
            self.optionCtrlGrp = self.utils.zeroOut([self.optionCtrl], notTransformIO=False)[0]
            cmds.setAttr(self.optionCtrlGrp+".translateX", fMasterRadius)
            # use Option_Ctrl rigScale and rigScaleMultiplier attribute to Master_Ctrl
            self.rigScaleMD = cmds.createNode("multiplyDivide", name=self.prefix+'RigScale_MD')
            cmds.addAttr(self.rigScaleMD, longName="dpRigScale", attributeType="bool", defaultValue=True)
            cmds.addAttr(self.optionCtrl, longName="dpRigScaleNode", attributeType="message")
            cmds.addAttr(self.optionCtrl, longName="rigScaleOutput", attributeType="float", defaultValue=1)
            cmds.connectAttr(self.rigScaleMD+".message", self.optionCtrl+".dpRigScaleNode", force=True)
            cmds.connectAttr(self.optionCtrl+".rigScale", self.rigScaleMD+".input1X", force=True)
            cmds.connectAttr(self.optionCtrl+".rigScaleMultiplier", self.rigScaleMD+".input2X", force=True)
            cmds.connectAttr(self.rigScaleMD+".outputX", self.optionCtrl+".rigScaleOutput", force=True)
            cmds.connectAttr(self.rigScaleMD+".outputX", self.masterCtrl+".scaleX", force=True)
            cmds.connectAttr(self.rigScaleMD+".outputX", self.masterCtrl+".scaleY", force=True)
            cmds.connectAttr(self.rigScaleMD+".outputX", self.masterCtrl+".scaleZ", force=True)
            self.ctrls.setLockHide([self.masterCtrl], ['sx', 'sy', 'sz'])
            self.ctrls.setLockHide([self.optionCtrl], ['rigScaleOutput'])
            self.ctrls.setNonKeyable([self.optionCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            self.ctrls.setStringAttrFromList(self.optionCtrl, ['rigScaleMultiplier'])
            cmds.parent(self.rootCtrl, self.masterCtrl)
            cmds.parent(self.masterCtrl, self.globalCtrl)
            cmds.parent(self.globalCtrl, self.ctrlsGrp)
            cmds.parent(self.optionCtrlGrp, self.rootCtrl)
            cmds.parent(self.ctrlsVisGrp, self.rootCtrl)
        else:
            self.rigScaleMD = self.prefix+'RigScale_MD'

        # set lock and hide attributes
        self.ctrls.setLockHide([self.scalableGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])
        self.ctrls.setLockHide([self.rootCtrl, self.globalCtrl], ['sx', 'sy', 'sz', 'v'])
        self.ctrls.setLockHide([self.rootPivotCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])

        # root pivot control setup
        if needConnectPivotAttr:
            for axis in ["X", "Y", "Z"]:
                cmds.connectAttr(self.rootPivotCtrl+".translate"+axis, self.rootCtrl+".rotatePivot"+axis, force=True)
                cmds.connectAttr(self.rootPivotCtrl+".translate"+axis, self.rootCtrl+".scalePivot"+axis, force=True)

        cmds.setAttr(self.masterCtrl+".visibility", keyable=False)
        cmds.select(None)

        #Base joint
        self.baseRootJnt = self.prefix+"BaseRoot_Jnt"
        self.baseRootJntGrp = self.prefix+"BaseRoot_Joint_Grp"
        if not cmds.objExists(self.baseRootJnt):
            self.baseRootJnt = cmds.createNode("joint", name=self.prefix+"BaseRoot_Jnt")
            if not cmds.objExists(self.baseRootJntGrp):
                self.baseRootJntGrp = cmds.createNode("transform", name=self.prefix+"BaseRoot_Joint_Grp")
            cmds.parent(self.baseRootJnt, self.baseRootJntGrp)
            cmds.parent(self.baseRootJntGrp, self.scalableGrp)
            cmds.parentConstraint(self.rootCtrl, self.baseRootJntGrp, maintainOffset=True, name=self.baseRootJntGrp+"_PaC")
            cmds.scaleConstraint(self.rootCtrl, self.baseRootJntGrp, maintainOffset=True, name=self.baseRootJntGrp+"_ScC")
            cmds.setAttr(self.baseRootJntGrp+".visibility", 0)
            self.ctrls.setLockHide([self.baseRootJnt, self.baseRootJntGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
    

    def changeRootToCtrlsVisConstraint(self, *args):
        """ Just recreate the Root_Ctrl output connections to a constraint, now using the ctrlsVisibilityGrp as source node instead.
            It keeps the dpAR compatibility to old rigs.
        """
        changeAttrList = ["rotateOrder", "translate", "rotate", "scale", "parentMatrix[0]", "rotatePivot", "rotatePivotTranslate"]
        for attr in changeAttrList:
            pacList = cmds.listConnections(self.rootCtrl+"."+attr, destination=True, source=False, plugs=True)
            if pacList:
                for pac in pacList:
                    cmds.connectAttr(self.ctrlsVisGrp+"."+attr, pac, force=True)


    def validateMasterGrp(self, nodeGrp, *args):
        """ Check if the current nodeGrp is a valid masterGrp (All_Grp) verifying it's message attribute connections.
        """
        masterGroupAttrList = ["modelsGrp", "ctrlsGrp", "ctrlsVisibilityGrp", "dataGrp", "renderGrp", "proxyGrp", "fxGrp", "staticGrp", "scalableGrp", "blendShapesGrp", "wipGrp"]
        for masterGroupAttr in masterGroupAttrList:
            if not cmds.objExists(nodeGrp+"."+masterGroupAttr):
                cmds.setAttr(nodeGrp+"."+MASTER_ATTR, 0)
                return False
        return cmds.getAttr(nodeGrp+"."+MASTER_ATTR)


    def reorderAttributes(self, objList, attrList, *args):
        """ Reorder Attributes of a given objectList following the desiredAttribute list.
            Useful for organize the Option_Ctrl attributes, for example.
        """
        if objList and attrList:
            for obj in objList:
                # load dpReorderAttribute:
                dpRAttr = dpReorderAttr.ReorderAttr(self, False)
                # Reordering Option_Ctrl attributos progress window
                progressAmount = 0
                cmds.progressWindow(title='Reordering Attributes', progress=progressAmount, status='Reordering: 0%', isInterruptable=False)
                nbDesAttr = len(attrList)
                delta = 0
                for i, desAttr in enumerate(attrList):
                    # update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=nbDesAttr, progress=progressAmount, status=('Reordering: ' + repr(progressAmount) + ' '+ obj + ' attributes'))
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

    
    def unPinAllGuides(self, *args):
        """ Brute force to un pin all guides.
            Useful to clean up guides before start the rigAll process.
        """
        pConstList = cmds.ls(selection=False, type="parentConstraint")
        if pConstList:
            for pConst in pConstList:
                if "PinGuide" in pConst:
                    pinnedGuide = cmds.listRelatives(pConst, parent=True, type="transform")[0]
                    self.ctrls.setLockHide([pinnedGuide], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], l=False)
                    cmds.delete(pConst)
    
    
    def rigAll(self, integrate=None, *args):
        """ Create the RIG based in the Guide Modules in the scene.
            Most important function to automate the generating process.
        """
        print('\ndpAutoRigSystem Log: ' + self.lang['i178_startRigging'] + '...\n')
        # force refresh in order to avoid calculus error if creating Rig at the same time of guides:
        cmds.refresh()
        if self.rebuilding:
            self.populateCreatedGuideModules()
        else:
            self.refreshMainUI()
        
        # get a list of modules to be rigged and re-declare the riggedModuleDic to store for log in the end:
        self.modulesToBeRiggedList = self.utils.getModulesToBeRigged(self.moduleInstancesList)
        self.riggedModuleDic = {}
        
        # declare a list to store all integrating information:
        self.integratedTaskDic = {}
        
        # verify if there are instances of modules (guides) to rig in the scene:
        if self.modulesToBeRiggedList:
            
            # check guide versions to be sure we are building with the same dpAutoRigSystem version:
            for guideModule in self.modulesToBeRiggedList:
                guideVersion = cmds.getAttr(guideModule.moduleGrp+'.dpARVersion')
                if not guideVersion == self.dpARVersion:
                    btYes = self.lang['i071_yes']
                    btUpdateGuides = self.lang['m186_updateGuides']
                    btNo = self.lang['i072_no']
                    userChoose = cmds.confirmDialog(title='dpAutoRigSystem - v'+self.dpARVersion, message=self.lang['i127_guideVersionDif'], button=[btYes, btUpdateGuides, btNo], defaultButton=btYes, cancelButton=btNo, dismissString=btNo)
                    if userChoose == btNo:
                        return
                    elif userChoose == btUpdateGuides:
                        self.initExtraModule("dpUpdateGuides", EXTRAS)
                        return
                    else:
                        break
            
            # force unPin all Guides:
            self.unPinAllGuides()
            
            # Starting progress window
            rigProgressAmount = 0
            cmds.progressWindow(title='dpAutoRigSystem', progress=rigProgressAmount, status='Rigging : 0%', isInterruptable=False)
            maxProcess = len(self.modulesToBeRiggedList)
            
            # clear all duplicated names in order to run without find same names if they exists:
            if cmds.objExists(self.guideMirrorGrp):
                cmds.delete(self.guideMirrorGrp)
            
            # regenerate mirror information for all guides:
            for guideModule in self.modulesToBeRiggedList:
                guideModule.checkFatherMirror()
            
            # store hierarchy from guides:
            self.hookDic = self.utils.hook()
            # serialize guides before change hierarchy
            for guideModule in self.modulesToBeRiggedList:
                guideModule.serializeGuide()
            
            # get prefix:
            self.prefix = cmds.textField("prefixTextField", query=True, text=True)
            if self.prefix != "" and self.prefix != " " and self.prefix != "_" and self.prefix != None:
                if self.prefix[len(self.prefix)-1] != "_":
                    self.prefix = self.prefix + "_"

            #Check if we need to colorize control shapes
            #Check integrate option
            bColorize = False
            bAddAttr = False
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
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=rigProgressAmount, status=('Rigging : ' + repr(rigProgressAmount) + ' '+str(guideModuleCustomName)))
                
                # Rig it :)
                guideModule.rigModule()
                # get rigged module name:
                self.riggedModuleDic[guideModule.moduleGrp.split(":")[0]] = guideModuleCustomName
                # get integrated information:
                if guideModule.integratedActionsDic:
                    self.integratedTaskDic[guideModule.moduleGrp] = guideModule.integratedActionsDic["module"]
            
            #Colorize all controller in yellow as a base
            if bColorize:
                aBCtrl = [self.globalCtrl, self.rootCtrl, self.optionCtrl]
                aAllCtrls = cmds.ls("*_Ctrl")
                lPattern = re.compile(self.lang['p002_left'] + '_.*._Ctrl')
                rPattern = re.compile(self.lang['p003_right'] + '_.*._Ctrl')
                for pCtrl in aAllCtrls:
                    shapeList = cmds.listRelatives(pCtrl, children=True, allDescendents=True, fullPath=True, type="shape")
                    if shapeList:
                        if not cmds.getAttr(shapeList[0]+".overrideEnabled"):
                            if (lPattern.match(pCtrl)):
                                self.ctrls.colorShape([pCtrl], "red")
                            elif (rPattern.match(pCtrl)):
                                self.ctrls.colorShape([pCtrl], "blue")
                            elif (pCtrl in aBCtrl):
                                self.ctrls.colorShape([pCtrl], "black")
                            else:
                                self.ctrls.colorShape([pCtrl], "yellow")
            
            if integrate == 1:
                # Update progress window
                rigProgressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=rigProgressAmount, status=('Rigging : ' + repr(rigProgressAmount) + ' '+self.lang['i010_integrateCB']))
                
                # get all parent info from rigged modules:
                self.originedFromDic = self.utils.getOriginedFromDic()
                
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
                        self.itemRiggedGrp = self.itemGuideName+"_Static_Grp"
                        self.staticHookGrp = self.itemRiggedGrp
                        self.ctrlHookGrp = cmds.listConnections(self.itemRiggedGrp+".controlHookGrp", destination=False, source=True)[0]
                        self.scalableHookGrp = cmds.listConnections(self.itemRiggedGrp+".scalableHookGrp", destination=False, source=True)[0]
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
                        self.fatherGuide = self.hookDic[guideModule.moduleGrp]['fatherGuide']
                        self.parentNode  = self.hookDic[guideModule.moduleGrp]['parentNode']
                        
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
                                if self.fatherRiggedParentNode:
                                    if len(self.fatherMirrorNameList) != 1: # tell us 'the father has mirror'
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
                self.bugMessage = self.lang['b000_bugGeneral']
                
                # integrating modules together:
                if self.integratedTaskDic:
                    # working with specific cases:
                    for moduleDic in self.integratedTaskDic:
                        moduleType = moduleDic[:moduleDic.find("__")]
                        
                        # display corrective controls by Option_Ctrl attribute:
                        try:
                            correctiveGrpList = self.integratedTaskDic[moduleDic]['correctiveCtrlGrpList']
                            if correctiveGrpList:
                                if not cmds.objExists(self.optionCtrl+"."+self.lang['c124_corrective']+"Ctrls"):
                                    cmds.addAttr(self.optionCtrl, longName=self.lang['c124_corrective']+"Ctrls", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                                    cmds.setAttr(self.optionCtrl+"."+self.lang['c124_corrective']+"Ctrls", channelBox=True)
                                for correctiveGrp in correctiveGrpList:
                                    cmds.connectAttr(self.optionCtrl+"."+self.lang['c124_corrective']+"Ctrls", correctiveGrp+".visibility", force=True)
                        except:
                            pass

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
                                    revFootCtrlGrp    = self.integratedTaskDic[moduleDic]['revFootCtrlGrpList'][s]
                                    revFootCtrlShape  = self.integratedTaskDic[moduleDic]['revFootCtrlShapeList'][s]
                                    toLimbIkHandleGrp = self.integratedTaskDic[moduleDic]['toLimbIkHandleGrpList'][s]
                                    parentConst       = self.integratedTaskDic[moduleDic]['parentConstList'][s]
                                    scaleConst        = self.integratedTaskDic[moduleDic]['scaleConstList'][s]
                                    footJnt           = self.integratedTaskDic[moduleDic]['footJntList'][s]
                                    ballRFList        = self.integratedTaskDic[moduleDic]['ballRFList'][s]
                                    middleFootCtrl    = self.integratedTaskDic[moduleDic]['middleFootCtrlList'][s]
                                    # getting limb data:
                                    fatherGuide           = self.hookDic[moduleDic]['fatherGuide']
                                    ikCtrl                = self.integratedTaskDic[fatherGuide]['ikCtrlList'][s]
                                    ikHandleGrp           = self.integratedTaskDic[fatherGuide]['ikHandleGrpList'][s]
                                    ikHandleConstList     = self.integratedTaskDic[fatherGuide]['ikHandleConstList'][s]
                                    ikFkBlendGrpToRevFoot = self.integratedTaskDic[fatherGuide]['ikFkBlendGrpToRevFootList'][s]
                                    extremJnt             = self.integratedTaskDic[fatherGuide]['extremJntList'][s]
                                    ikStretchExtremLoc    = self.integratedTaskDic[fatherGuide]['ikStretchExtremLoc'][s]
                                    limbTypeName          = self.integratedTaskDic[fatherGuide]['limbTypeName']
                                    worldRef              = self.integratedTaskDic[fatherGuide]['worldRefList'][s]
                                    addArticJoint         = self.integratedTaskDic[fatherGuide]['addArticJoint']
                                    addCorrective         = self.integratedTaskDic[fatherGuide]['addCorrective']
                                    ankleArticList        = self.integratedTaskDic[fatherGuide]['ankleArticList'][s]
                                    ankleCorrectiveList   = self.integratedTaskDic[fatherGuide]['ankleCorrectiveList'][s]
                                    jaxRotZMDList         = self.integratedTaskDic[fatherGuide]['jaxRotZMDList']
                                    # do task actions in order to integrate the limb and foot:
                                    cmds.cycleCheck(evaluation=False)
                                    cmds.delete(ikHandleConstList, parentConst, scaleConst) #there's an undesirable cycleCheck evaluation error here when we delete ikHandleConstList!
                                    cmds.cycleCheck(evaluation=True)
                                    cmds.parent(revFootCtrlGrp, ikFkBlendGrpToRevFoot, absolute=True)
                                    cmds.parent(ikHandleGrp, toLimbIkHandleGrp, absolute=True)
                                    cmds.parentConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_PaC")[0]
                                    if limbTypeName == LEG:
                                        cmds.connectAttr(extremJnt+".scaleX", footJnt+".scaleX", force=True)
                                        cmds.connectAttr(extremJnt+".scaleY", footJnt+".scaleY", force=True)
                                        cmds.connectAttr(extremJnt+".scaleZ", footJnt+".scaleZ", force=True)
                                        if ikStretchExtremLoc: # avoid issue parenting if quadruped
                                            cmds.parent(ikStretchExtremLoc, ballRFList, absolute=True)
                                        if cmds.objExists(extremJnt+".dpAR_joint"):
                                            cmds.deleteAttr(extremJnt+".dpAR_joint")
                                        # reconnect correctly the interation for ankle and correctives
                                        if addArticJoint:
                                            cmds.delete(ankleArticList[1])
                                            # workaround to avoid orientConstraint offset issue
                                            footJntFather = cmds.listRelatives(footJnt, parent=True)[0]
                                            cmds.delete(cmds.listRelatives(footJnt, children=True, type="parentConstraint")[0])
                                            footJntChildrenList = cmds.listRelatives(footJnt, children=True)
                                            cmds.parent(footJntChildrenList, world=True)
                                            cmds.parent(footJnt, extremJnt, relative=True)
                                            cmds.makeIdentity(footJnt, apply=True, translate=True, rotate=True, jointOrient=True, scale=False)
                                            cmds.parent(footJnt, footJntFather)
                                            cmds.parent(footJntChildrenList, footJnt)
                                            cmds.parentConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_PaC")
                                            if addCorrective:
                                                oc = cmds.orientConstraint(footJnt, ankleArticList[2], ankleArticList[0], maintainOffset=True, name=ankleArticList[0]+"_OrC", skip="z")[0]
                                                if jaxRotZMDList:
                                                    cmds.connectAttr(oc+".constraintRotateZ", jaxRotZMDList[s]+".input1Z", force=True)
                                                for netNode in ankleCorrectiveList:
                                                    if netNode:
                                                        if cmds.objExists(netNode):
                                                            actionLocList = cmds.listConnections(netNode+".actionLoc", destination=False, source=True)
                                                            if actionLocList:
                                                                cmds.connectAttr(footJnt+".message", actionLocList[0]+".inputNode", force=True)
                                                                actionLocGrp = cmds.listRelatives(actionLocList[0], parent=True, type="transform")[0]
                                                                cmds.delete(actionLocGrp+"_PaC")
                                                                cmds.parentConstraint(footJnt, actionLocGrp, maintainOffset=True, name=actionLocGrp+"_PaC")
                                            else:
                                                oc = cmds.orientConstraint(footJnt, ankleArticList[2], ankleArticList[0], maintainOffset=True, name=ankleArticList[0]+"_OrC")[0]
                                            cmds.setAttr(oc+".interpType", 2) #shortest
                                    scalableGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                    cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScC")
                                    # hide this control shape
                                    cmds.setAttr(revFootCtrlShape+".visibility", 0)
                                    # add attributes and connect from ikCtrl to revFootCtrl:
                                    userAttrList = cmds.listAttr(revFootCtrl, visible=True, scalar=True, userDefined=True)
                                    for attr in userAttrList:
                                        if not cmds.objExists(ikCtrl+'.'+attr):
                                            attrType = cmds.getAttr(revFootCtrl+'.'+attr, type=True)
                                            currentValue = cmds.getAttr(revFootCtrl+'.'+attr)
                                            keyableStatus = cmds.getAttr(revFootCtrl+'.'+attr, keyable=True)
                                            channelBoxStatus = cmds.getAttr(revFootCtrl+'.'+attr, channelBox=True)
                                            defValue = cmds.addAttr(revFootCtrl+'.'+attr, query=True, defaultValue=True)
                                            attrMinValue = cmds.addAttr(revFootCtrl+'.'+attr, query=True, minValue=True)
                                            attrMaxValue = cmds.addAttr(revFootCtrl+'.'+attr, query=True, maxValue=True)
                                            cmds.addAttr(ikCtrl, longName=attr, attributeType=attrType, keyable=keyableStatus, defaultValue=defValue)
                                            if not attrMinValue == None:
                                                cmds.addAttr(ikCtrl+'.'+attr, edit=True, minValue=attrMinValue)
                                            if not attrMaxValue == None:
                                                cmds.addAttr(ikCtrl+'.'+attr, edit=True, maxValue=attrMaxValue)
                                            cmds.setAttr(ikCtrl+'.'+attr, currentValue)
                                            if not keyableStatus:
                                                cmds.setAttr(ikCtrl+'.'+attr, channelBox=channelBoxStatus)
                                            cmds.connectAttr(ikCtrl+'.'+attr, revFootCtrl+'.'+attr, force=True)
                                            if attr == "visIkFk":
                                                if not cmds.objExists(worldRef):
                                                    worldRef = worldRef.replace("_Ctrl", "_Grp")
                                                if cmds.objExists(worldRef):
                                                    wrAttrList = cmds.listAttr(worldRef, userDefined=True)
                                                    for wrAttr in wrAttrList:
                                                        if "Fk_ikFkBlendRevOutputX" in wrAttr:
                                                            cmds.connectAttr(worldRef+"."+wrAttr, ikCtrl+'.'+attr, force=True)
                                    revFootCtrlOld = cmds.rename(revFootCtrl, revFootCtrl+"_Old")
                                    self.customAttr.removeAttr("dpControl", [revFootCtrlOld])
                        
                        # worldRef of extremGuide from limbModule controlled by optionCtrl:
                        if moduleType == LIMB:
                            # getting limb data:
                            worldRefList      = self.integratedTaskDic[moduleDic]['worldRefList']
                            worldRefShapeList = self.integratedTaskDic[moduleDic]['worldRefShapeList']
                            ikCtrlList        = self.integratedTaskDic[moduleDic]['ikCtrlList']
                            lvvAttr           = self.integratedTaskDic[moduleDic]['limbManualVolume']
                            masterCtrlRefList = self.integratedTaskDic[moduleDic]['masterCtrlRefList']
                            rootCtrlRefList   = self.integratedTaskDic[moduleDic]['rootCtrlRefList']
                            softIkCalibList   = self.integratedTaskDic[moduleDic]['softIkCalibrateList']
                            for w, worldRef in enumerate(worldRefList):
                                # do actions in order to make limb be controlled by optionCtrl:
                                floatAttrList = cmds.listAttr(worldRef, visible=True, scalar=True, keyable=True, userDefined=True)
                                for f, floatAttr in enumerate(floatAttrList):
                                    if f != len(floatAttrList):
                                        if not cmds.objExists(self.optionCtrl+'.'+floatAttr):
                                            currentValue = cmds.getAttr(worldRef+'.'+floatAttr)
                                            if floatAttr == lvvAttr:
                                                cmds.addAttr(self.optionCtrl, longName=floatAttr, attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), defaultValue=currentValue, keyable=True)
                                                # TODO fix or remove Limb manual volume variation attribute
                                                cmds.setAttr(self.optionCtrl+"."+floatAttr, channelBox=False, keyable=False)
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
                                # connect Option_Ctrl RigScale_MD output to the radiusScale:
                                if cmds.objExists(self.rigScaleMD+".dpRigScale") and cmds.getAttr(self.rigScaleMD+".dpRigScale") == True:
                                    cmds.connectAttr(self.rigScaleMD+".outputX", softIkCalibList[w]+".input2X", force=True)

                                cmds.delete(worldRefShapeList[w])
                                worldRef = cmds.rename(worldRef, worldRef.replace("_Ctrl", "_Grp"))
                                cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_PaC")

                                # remove dpControl attribute
                                self.customAttr.removeAttr("dpControl", [worldRef])
                            
                                # fix poleVector follow feature integrating with Master_Ctrl and Root_Ctrl:
                                cmds.parentConstraint(self.masterCtrl, masterCtrlRefList[w], maintainOffset=True, name=masterCtrlRefList[w]+"_PaC")
                                cmds.parentConstraint(self.rootCtrl, rootCtrlRefList[w], maintainOffset=True, name=rootCtrlRefList[w]+"_PaC")
                            
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
                                scalableGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScC")

                                if fatherModule == SPINE:
                                    # getting limb data:
                                    limbTypeName         = self.integratedTaskDic[moduleDic]['limbTypeName']
                                    ikCtrlZero           = self.integratedTaskDic[moduleDic]['ikCtrlZeroList'][s]
                                    ikPoleVectorCtrlZero = self.integratedTaskDic[moduleDic]['ikPoleVectorZeroList'][s]
                                    limbStyle            = self.integratedTaskDic[moduleDic]['limbStyle']
                                    ikHandleGrp          = self.integratedTaskDic[moduleDic]['ikHandleGrpList'][s]
                                    
                                    # getting spine data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    hipsA  = self.integratedTaskDic[fatherGuide]['hipsAList'][0]
                                    tipCtrl = self.integratedTaskDic[fatherGuide]['tipList'][0]

                                    cmds.parent(ikCtrlZero, self.ctrlsVisGrp, absolute=True)
                                    # verifying what part will be used, the hips or chest:
                                    if limbTypeName == LEG:
                                        # do task actions in order to integrate the limb of leg type to rootCtrl:
                                        cmds.parent(ikPoleVectorCtrlZero, self.ctrlsVisGrp, absolute=True)
                                    else:
                                        # do task actions in order to integrate the limb and spine (ikCtrl):
                                        cmds.parentConstraint(tipCtrl, ikHandleGrp, mo=1, name=ikHandleGrp+"_PaC")
                                        # poleVector autoOrient for arm
                                        cmds.delete(rootCtrlRefList[s]+"_PaC")
                                        cmds.parentConstraint(tipCtrl, rootCtrlRefList[s], maintainOffset=True, name=rootCtrlRefList[s]+"_PaC")

                                    # verify if is quadruped
                                    if limbStyle == self.lang['m037_quadruped'] or limbStyle == self.lang['m043_quadSpring']:
                                        if fatherGuideLoc != "JointLoc1":
                                            # get extra info from limb module data:
                                            quadFrontLeg = self.integratedTaskDic[moduleDic]['quadFrontLegList'][s]
                                            ikCtrl       = self.integratedTaskDic[moduleDic]['ikCtrlList'][s]
                                            # if quadruped, create a parent contraint from tipCtrl to front leg:
                                            quadChestParentConst = cmds.parentConstraint(self.rootCtrl, tipCtrl, quadFrontLeg, maintainOffset=True, name=quadFrontLeg+"_PaC")[0]
                                            revNode = cmds.createNode('reverse', name=quadFrontLeg+"_Rev")
                                            cmds.addAttr(ikCtrl, longName="followChestA", attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                                            cmds.connectAttr(ikCtrl+".followChestA", quadChestParentConst+"."+tipCtrl+"W1", force=True)
                                            cmds.connectAttr(ikCtrl+".followChestA", revNode+".inputX", force=True)
                                            cmds.connectAttr(revNode+".outputX", quadChestParentConst+"."+self.rootCtrl+"W0", force=True)
                            
                            # fixing ikSpringSolver parenting for quadrupeds:
                            # getting limb data:
                            fixIkSpringSolverGrp = self.integratedTaskDic[moduleDic]['fixIkSpringSolverGrpList']
                            if fixIkSpringSolverGrp:
                                cmds.parent(fixIkSpringSolverGrp, self.scalableGrp, absolute=True)
                                for nFix in fixIkSpringSolverGrp:
                                    cmds.scaleConstraint(self.masterCtrl, nFix, name=nFix+"_ScC")
                            
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
                                clusterGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                shapeVisAttrList = self.integratedTaskDic[moduleDic]["shapeVisAttrList"]
                                cmds.scaleConstraint(self.masterCtrl, clusterGrp, name=clusterGrp+"_ScC")
                                cmds.addAttr(self.optionCtrl, longName=vvAttr, attributeType="float", defaultValue=1, keyable=True)
                                cmds.connectAttr(self.optionCtrl+'.'+vvAttr, hipsA+'.'+vvAttr)
                                cmds.setAttr(hipsA+'.'+vvAttr, keyable=False)
                                cmds.addAttr(self.optionCtrl, longName=actVVAttr, attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                                cmds.connectAttr(self.optionCtrl+'.'+actVVAttr, hipsA+'.'+actVVAttr)
                                cmds.setAttr(hipsA+'.'+actVVAttr, keyable=False)
                                cmds.connectAttr(self.masterCtrl+'.scaleX', hipsA+'.'+mScaleVVAttr)
                                cmds.setAttr(hipsA+'.'+mScaleVVAttr, keyable=False)
                                cmds.addAttr(self.optionCtrl, longName=ikFkBlendAttr, attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                                cmds.connectAttr(self.optionCtrl+'.'+ikFkBlendAttr, hipsA+'.'+ikFkBlendAttr)
                                cmds.setAttr(hipsA+'.'+ikFkBlendAttr, keyable=False)
                                if shapeVisAttrList:
                                    for shapeVisAttr in shapeVisAttrList:
                                        if not cmds.objExists(self.optionCtrl+"."+shapeVisAttr):
                                            cmds.addAttr(self.optionCtrl, longName=shapeVisAttr, attributeType="long", min=0, max=1, defaultValue=0, keyable=False)
                                            cmds.setAttr(self.optionCtrl+'.'+shapeVisAttr, channelBox=True)
                                            cmds.connectAttr(self.optionCtrl+'.'+shapeVisAttr, hipsA+'.'+shapeVisAttr)
                                            cmds.setAttr(hipsA+'.'+shapeVisAttr, keyable=False)
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
                                cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_PaC")
                                if bColorize:
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['ctrlList'][s], "yellow")
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['InnerCtrls'][s], "cyan")
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
                                upperCtrl  = self.integratedTaskDic[fatherGuide]['upperCtrlList'][0]
                                headParentConst = cmds.parentConstraint(self.rootCtrl, upperCtrl, eyeGrp, maintainOffset=True, name=eyeGrp+"_PaC")[0]
                                eyeRevNode = cmds.createNode('reverse', name=eyeGrp+"_Rev")
                                cmds.connectAttr(eyeCtrl+'.'+self.lang['c032_follow'], eyeRevNode+".inputX", force=True)
                                cmds.connectAttr(eyeRevNode+".outputX", headParentConst+"."+self.rootCtrl+"W0", force=True)
                                cmds.connectAttr(eyeCtrl+'.'+self.lang['c032_follow'], headParentConst+"."+upperCtrl+"W1", force=True)
                                cmds.parent(upLocGrp, upperCtrl, relative=False)
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
                                    cmds.parentConstraint(upperCtrl, eyeScaleGrp, maintainOffset=True, name=eyeScaleGrp+"_PaC")
                            # changing iris and pupil color override:
                            if bColorize:
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
                                        self.ctrls.colorShape([pupilCtrl], "yellow")
                        
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
                                cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScC")
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
                                        cmds.parentConstraint(origFrom, scalableGrp, maintainOffset=True, name=scalableGrp+"_PaC")
                
                        # integrate the Single module with another Single as a father:
                        if moduleType == SINGLE:
                            # connect Option_Ctrl display attribute to the visibility:
                            if not cmds.objExists(self.optionCtrl+"."+self.lang['m081_tweaks'].lower()):
                                cmds.addAttr(self.optionCtrl, longName=self.lang['m081_tweaks'].lower(), min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                                cmds.setAttr(self.optionCtrl+"."+self.lang['m081_tweaks'].lower(), channelBox=True)
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                ctrlGrp = self.integratedTaskDic[moduleDic]["ctrlGrpList"][s]
                                cmds.connectAttr(self.optionCtrl+"."+self.lang['m081_tweaks'].lower(), ctrlGrp+".visibility", force=True)
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
                                    cmds.parentConstraint(mainJis, staticGrp, maintainOffset=True, name=staticGrp+"_PaC")
                                    cmds.scaleConstraint(mainJis, staticGrp, maintainOffset=True, name=staticGrp+"_ScC")
                                    
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
                                    cmds.connectAttr(steeringCtrl+'.'+self.lang['c070_steering'], wheelCtrl+'.'+self.lang['i037_to']+self.lang['c070_steering'].capitalize(), force=True)
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
                                                        if len(self.fatherBMirrorNameList) != 1: #means fatherB has mirror
                                                            if s == fB:
                                                                cmds.parentConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_PaC")
                                                                cmds.scaleConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScC")
                                                        else:
                                                            cmds.parentConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_PaC")
                                                            cmds.scaleConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScC")
                                    else: # probably we will parent to a control curve already generated and rigged before
                                        if cmds.objExists(loadedFatherB):
                                            cmds.parentConstraint(loadedFatherB, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_PaC")
                                            cmds.scaleConstraint(loadedFatherB, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScC")
                                # get father module:
                                fatherModule = self.hookDic[moduleDic]['fatherModule']
                                if fatherModule == WHEEL:
                                    # getting spine data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    # parent suspension control group to wheel Main_Ctrl
                                    suspensionHookCtrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][s]
                                    wheelMainCtrl = self.integratedTaskDic[fatherGuide]['mainCtrlList'][s]
                                    cmds.parentConstraint(wheelMainCtrl, suspensionHookCtrlGrp, maintainOffset=True, name=suspensionHookCtrlGrp+"_PaC")
                                    cmds.scaleConstraint(wheelMainCtrl, suspensionHookCtrlGrp, maintainOffset=True, name=suspensionHookCtrlGrp+"_ScC")

                        # integrate the nose control colors:
                        if moduleType == NOSE:
                            self.itemGuideMirrorAxis = self.hookDic[moduleDic]['guideMirrorAxis']
                            if self.itemGuideMirrorAxis == "off":
                                if bColorize:
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['ctrlList'][0], "yellow")
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['lCtrls'][0], "red")
                                    self.ctrls.colorShape(self.integratedTaskDic[moduleDic]['rCtrls'][0], "blue")
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            if fatherModule == HEAD:
                                fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                upperCtrl  = self.integratedTaskDic[fatherGuide]['upperCtrlList'][0]
                                upperJawCtrl = self.integratedTaskDic[fatherGuide]['upperJawCtrlList'][0]
                                ctrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][0]
                                mainCtrl = self.integratedTaskDic[moduleDic]['mainCtrlList'][0]
                                cmds.addAttr(mainCtrl, longName="spaceSwitch", attributeType="enum", en="Upper Jaw:Upper Head", keyable=True)
                                revNode = cmds.createNode("reverse", name="Nose_SpaceSwitch_Rev")
                                pac = cmds.parentConstraint(upperJawCtrl, upperCtrl, ctrlGrp, maintainOffset=True, name=ctrlGrp+"_PaC")[0]
                                cmds.connectAttr(mainCtrl+".spaceSwitch", pac+"."+upperCtrl+"W1", force=True)
                                cmds.connectAttr(mainCtrl+".spaceSwitch", revNode+".inputX", force=True)
                                cmds.connectAttr(revNode+".outputX", pac+"."+upperJawCtrl+"W0", force=True)
                        
                        # worldRef of chain controlled by optionCtrl:
                        if moduleType == CHAIN:
                            # getting limb data:
                            worldRefList      = self.integratedTaskDic[moduleDic]['worldRefList']
                            worldRefShapeList = self.integratedTaskDic[moduleDic]['worldRefShapeList']
                            for w, worldRef in enumerate(worldRefList):
                                # do actions in order to make chain be controlled by optionCtrl:
                                floatAttrList = cmds.listAttr(worldRef, visible=True, scalar=True, keyable=True, userDefined=True)
                                for f, floatAttr in enumerate(floatAttrList):
                                    if f != len(floatAttrList):
                                        if not cmds.objExists(self.optionCtrl+'.'+floatAttr):
                                            currentValue = cmds.getAttr(worldRef+'.'+floatAttr)
                                            cmds.addAttr(self.optionCtrl, longName=floatAttr, attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), minValue=0, maxValue=1, defaultValue=currentValue, keyable=True)
                                        cmds.connectAttr(self.optionCtrl+'.'+floatAttr, worldRef+'.'+floatAttr, force=True)
                                if not cmds.objExists(self.optionCtrl+'.'+floatAttrList[len(floatAttrList)-1]):
                                    cmds.addAttr(self.optionCtrl, longName=floatAttrList[len(floatAttrList)-1], attributeType=cmds.getAttr(worldRef+"."+floatAttr, type=True), defaultValue=1, keyable=True)
                                    cmds.connectAttr(self.optionCtrl+'.'+floatAttrList[len(floatAttrList)-1], worldRef+'.'+floatAttrList[len(floatAttrList)-1], force=True)
                                cmds.connectAttr(self.masterCtrl+".scaleX", worldRef+".scaleX", force=True)
                                cmds.delete(worldRefShapeList[w])
                                worldRef = cmds.rename(worldRef, worldRef.replace("_Ctrl", "_Grp"))
                                cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_PaC")
                                # remove dpControl attribute
                                self.customAttr.removeAttr("dpControl", [worldRef])

                # atualise the number of rigged guides by type
                for guideType in self.guideModuleList:
                    typeCounter = 0
                    newTranformList = cmds.ls(selection=False, type="transform")
                    for transf in newTranformList:
                        if cmds.objExists(transf+'.dpAR_type'):
                            dpARType = ( 'dp'+(cmds.getAttr(transf+'.dpAR_type')) )
                            if ( dpARType == guideType ):
                                typeCounter = typeCounter + 1
                    if ( typeCounter != cmds.getAttr(self.masterGrp+'.'+guideType+'Count') ):
                        cmds.setAttr(self.masterGrp+'.'+guideType+'Count', typeCounter)
        
            # Close progress window
            cmds.progressWindow(endProgress=True)
            
            #Actualise all controls (All_Grp.controlList) for this rig:
            dpUpdateRigInfo.UpdateRigInfo.updateRigInfoLists()

            # Add usefull attributes for the animators
            if (bAddAttr):
                # defining attribute name strings:
                generalAttr = self.lang['c066_general']
                vvAttr = self.lang['c031_volumeVariation']
                spineAttr = self.lang['m011_spine'].lower()
                limbAttr = self.lang['m019_limb'].lower()
                armAttr = self.lang['m028_arm']
                legAttr = self.lang['m030_leg']
                frontAttr = self.lang['c056_front']
                backAttr = self.lang['c057_back']
                leftAttr = self.lang['p002_left'].lower()
                rightAttr = self.lang['p003_right'].lower()
                tweaksAttr = self.lang['m081_tweaks'].lower()
                
                if not cmds.objExists(self.optionCtrl+"."+generalAttr):
                    cmds.addAttr(self.optionCtrl, longName=generalAttr, attributeType="enum", enumName="----------", keyable=True)
                    cmds.setAttr(self.optionCtrl+"."+generalAttr, lock=True)
                
                # Only create if a VolumeVariation attribute is found
                if not cmds.objExists(self.optionCtrl+"."+vvAttr):
                    if cmds.listAttr(self.optionCtrl, string="*"+vvAttr+"*"):
                        cmds.addAttr(self.optionCtrl, longName=vvAttr, attributeType="enum", enumName="----------", keyable=True)
                        cmds.setAttr(self.optionCtrl+"."+vvAttr, lock=True)
                
                # Only create if an IkFk attribute is found
                if not cmds.objExists(self.optionCtrl+".ikFkBlend"):
                    if cmds.listAttr(self.optionCtrl, string="*ikFk*"):
                        cmds.addAttr(self.optionCtrl, longName="ikFkBlend", attributeType="enum", enumName="----------", keyable=True)
                        cmds.setAttr(self.optionCtrl+".ikFkBlend", lock=True)
                
                if cmds.objExists(self.optionCtrl+".ikFkSnap"):
                    cmds.setAttr(self.optionCtrl+".ikFkSnap", keyable=False, channelBox=True)
                
                if not cmds.objExists(self.optionCtrl+".display"):
                    cmds.addAttr(self.optionCtrl, longName="display", attributeType="enum", enumName="----------", keyable=True)
                    cmds.setAttr(self.optionCtrl+".display", lock=True)
                
                if not cmds.objExists(self.optionCtrl+".mesh"):
                    cmds.addAttr(self.optionCtrl, longName="mesh", min=0, max=1, defaultValue=1, attributeType="long", keyable=True)
                    cmds.connectAttr(self.optionCtrl+".mesh", self.renderGrp+".visibility", force=True)
                
                if not cmds.objExists(self.optionCtrl+".proxy"):
                    cmds.addAttr(self.optionCtrl, longName="proxy", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                    cmds.connectAttr(self.optionCtrl+".proxy", self.proxyGrp+".visibility", force=True)
                
                if not cmds.objExists(self.optionCtrl+".control"):
                    cmds.addAttr(self.optionCtrl, longName="control", min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                    cmds.connectAttr(self.optionCtrl+".control", self.ctrlsVisGrp+".visibility", force=True)
                    cmds.setAttr(self.optionCtrl+".control", channelBox=True)

                if not cmds.objExists(self.optionCtrl+".rootPivot"):
                    cmds.addAttr(self.optionCtrl, longName="rootPivot", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                    cmds.connectAttr(self.optionCtrl+".rootPivot", self.rootPivotCtrlGrp+".visibility", force=True)
                    cmds.setAttr(self.optionCtrl+".rootPivot", channelBox=True)

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
                desiredAttrList = [generalAttr, 'globalStretch', 'rigScale', 'rigScaleMultiplier', vvAttr,
                spineAttr+'Active', spineAttr, spineAttr+'001Active', spineAttr+'001', spineAttr+'002Active', spineAttr+'002',
                limbAttr, limbAttr+'Min', limbAttr+'Manual', 'ikFkBlend', 'ikFkSnap', spineAttr+'Fk', spineAttr+'Fk1', spineAttr+'Fk2', spineAttr+'001Fk', spineAttr+'002Fk', 
                leftAttr+spineAttr+'Fk', rightAttr+spineAttr+'Fk', leftAttr+spineAttr+'Fk1', rightAttr+spineAttr+'Fk1', leftAttr+spineAttr+'Fk2', rightAttr+spineAttr+'Fk2',
                armAttr+"Fk", legAttr+"Fk", leftAttr+armAttr+"Fk", rightAttr+armAttr+"Fk", armAttr.lower()+"Fk", legAttr.lower()+"Fk", leftAttr+armAttr.lower()+"Fk", rightAttr+armAttr.lower()+"Fk",
                leftAttr+legAttr+"Fk", rightAttr+legAttr+"Fk", leftAttr+legAttr+frontAttr+"Fk", rightAttr+legAttr+frontAttr+"Fk", leftAttr+legAttr+backAttr+"Fk", rightAttr+legAttr+backAttr+"Fk",
                armAttr+'Fk1', legAttr+'Fk1', leftAttr+armAttr+'Fk1', rightAttr+armAttr+'Fk1', leftAttr+legAttr+'Fk1', rightAttr+legAttr+'Fk1',
                leftAttr+legAttr+frontAttr+'Fk1', rightAttr+legAttr+frontAttr+'Fk1', leftAttr+legAttr+backAttr+'Fk1', rightAttr+legAttr+backAttr+'Fk1',
                'tailFk', 'tailDyn', 'tail1Fk', 'tail1Dyn', 'tailFk1', 'tailDyn1', leftAttr+'TailFk', leftAttr+'TailFk1', rightAttr+'TailFk', rightAttr+'TailFk1', leftAttr+'TailDyn', leftAttr+'TailDyn1', rightAttr+'TailDyn', rightAttr+'TailDyn1',
                'hairFk', 'hairDyn', 'hair1Fk', 'hair1Dyn', 'hairFk1', 'hairDyn1', leftAttr+'HairFk', leftAttr+'HairFk1', rightAttr+'HairFk', rightAttr+'HairFk1', leftAttr+'HairDyn', leftAttr+'HairDyn1', rightAttr+'HairDyn', rightAttr+'HairDyn1',
                'dpAR_000Fk', 'dpAR_000Dyn', 'dpAR_001Fk', 'dpAR_001Dyn', 'dpAR_002Fk', 'dpAR_002Dyn', 
                'dpAR_000Fk1', 'dpAR_000Dyn1', leftAttr+'dpAR_000Fk', leftAttr+'dpAR_000Fk1', rightAttr+'dpAR_000Fk', rightAttr+'dpAR_000Fk1', leftAttr+'dpAR_000Dyn', leftAttr+'dpAR_000Dyn1', rightAttr+'dpAR_000Dyn', rightAttr+'dpAR_000Dyn1',
                'dpAR_001Fk1', 'dpAR_001Dyn1', leftAttr+'dpAR_001Fk', leftAttr+'dpAR_001Fk1', rightAttr+'dpAR_001Fk', rightAttr+'dpAR_001Fk1', leftAttr+'dpAR_001Dyn', leftAttr+'dpAR_001Dyn1', rightAttr+'dpAR_001Dyn', rightAttr+'dpAR_001Dyn1',
                'display', 'mesh', 'proxy', 'control', 'bends', 'extraBends', tweaksAttr, 'correctiveCtrls']
                # call method to reorder Option_Ctrl attributes:
                self.reorderAttributes([self.optionCtrl], desiredAttrList)
                
            #Try add hand follow (space switch attribute) on bipeds:
            self.initExtraModule("dpLimbSpaceSwitch", EXTRAS)
            
            # show dialogBox if detected a bug:
            if integrate == 1:
                if self.detectedBug:
                    print("\n\n")
                    print(self.bugMessage)
                    cmds.confirmDialog(title=self.lang['i078_detectedBug'], message=self.bugMessage, button=["OK"])

        # re-declaring guideMirror and previewMirror groups:
        if cmds.objExists(self.guideMirrorGrp):
            cmds.delete(self.guideMirrorGrp)
        
        # reload the jointSkinList:
        self.populateJoints()
        
        # select the MasterCtrl:
        try:
            cmds.select(self.masterCtrl)
        except:
            pass
        
        if not self.rebuilding:
            # call log window:
            self.logger.logWin()
        
    
    ###################### End: Rigging Modules Instances.
