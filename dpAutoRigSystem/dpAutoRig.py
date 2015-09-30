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
#                                    print messages (, at the end), centered pivot of chestB_ctrl (spine),
#                                    clavicle pivot position, correct controls mirror based in dpLimb style,
#                                    quadruped front legs using ikSpring solver, find environment path,
#                                    loading decomposeMatrix node in order to create mirror, headFollow
#                             implemented: new feature for dpLimb with bend ribbons by James do Carmo
#
#
###################################################################



# importing libraries:
try:
    import maya.cmds as cmds
    import json
    import os
    import sys
    import re
    import time
    from functools import partial
    import Modules.dpUtils as utils
    import Modules.dpControls as ctrls
except Exception as e:
    print "Error: importing python modules!!!\n",
    print e

DPAR_VERSION = "2.4"

class DP_AutoRig_UI:
    
    ###################### Start: UI
    
    def __init__(self):
        """ Start the window, menus and main layout for dpAutoRig UI.
        """
        try:
            # store all UI elements in a dictionary:
            self.allUIs = {}
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
                    if "English" in self.langList:
                        cmds.optionVar( stringValue=('dpAutoRigLastLanguage', 'English') )
                    else:
                        cmds.optionVar( stringValue=('dpAutoRigLastLanguage', self.langList[0]) )
                # get its value puting in a variable lastLang:
                self.lastLang = cmds.optionVar( query='dpAutoRigLastLanguage' )
                # if the last language in the system was different of json files, set it to English or to the first language in the list also:
                if not self.lastLang in self.langList:
                    if "English" in self.langList:
                        self.lastLang = 'English'
                    else:
                        self.lastLang = self.langList[0]
                # create menuItems with the command to set the last language variable, delete languageUI and call mainUI() again when changed:
                for idiom in self.langList:
                    cmds.menuItem( idiom+"_MI", label=idiom, radioButton=False, collection='languageRadioMenuCollection', command='cmds.optionVar(remove=\"dpAutoRigLastLanguage\"); cmds.optionVar(stringValue=(\"dpAutoRigLastLanguage\", \"'+idiom+'\")); cmds.deleteUI(\"languageTabLayout\"); dpUI.mainUI()')
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
        
        # call UI window:
        cmds.dockControl( 'dpAutoRigSystem', area="left", content=self.allUIs["dpAutoRigWin"])
    
    
    def deleteExistWindow(self, *args):
        """ Check if there are the dpAutoRigWindow and dpAutoRigSystem_control to deleteUI.
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
        self.guideModuleList = self.startGuideModules("Modules", "start")
        cmds.separator(style='doubleDash', height=10, parent=self.allUIs["guidesLayoutA"])
        self.allUIs["i031_integrated"] = cmds.text(self.langDic[self.langName]['i031_integrated'], font="obliqueLabelFont", align='left', parent=self.allUIs["guidesLayoutA"])
        self.startGuideModules("Scripts", "start")
        cmds.setParent(self.allUIs["riggingTabLayout"])
        
        #colMiddleRightA - scrollLayout - modulesLayout:
        self.allUIs["colMiddleRightA"] = cmds.scrollLayout("colMiddleRightA", width=150, parent=self.allUIs["riggingTabLayout"])
        self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=150, parent=self.allUIs["colMiddleRightA"])
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
        self.allUIs["hideJointsCB"] = cmds.checkBox('hideJointsCB', label=self.langDic[self.langName]['i009_hideJointsCB'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["integrateCB"] = cmds.checkBox('integrateCB', label=self.langDic[self.langName]['i010_integrateCB'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
        self.allUIs["defaultRenderLayerCB"] = cmds.checkBox('defaultRenderLayerCB', label=self.langDic[self.langName]['i004_defaultRL'], align='left', v=1, parent=self.allUIs["rigOptionsLayout"])
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
        cmds.scriptJob(event=('deleteAll', self.jobReloadUI), parent='dpAutoRigWindow', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
        cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)
        
        # interface of Skinning tab:
        self.allUIs["skinningTabLayout"] = cmds.formLayout('skinningTabLayout', numberOfDivisions=100, parent=self.allUIs["languageTabLayout"])
        
        #colSkinLeftA - columnLayout:
        self.allUIs["colSkinLeftA"] = cmds.columnLayout('colSkinLeftA', adjustableColumn=True, width=190, parent=self.allUIs["skinningTabLayout"])
        # radio buttons:
        self.allUIs["jntCollection"] = cmds.radioCollection('jntCollection', parent=self.allUIs["colSkinLeftA"])
        allJoints   = cmds.radioButton( label=self.langDic[self.langName]['i022_listAllJnts'], annotation="allJoints", onCommand=self.populateJoints )
        dpARJoints  = cmds.radioButton( label=self.langDic[self.langName]['i023_listdpARJnts'], annotation="dpARJoints", onCommand=self.populateJoints )
        self.allUIs["jntTextScrollLayout"] = cmds.textScrollList( 'jntTextScrollLayout', width=30, allowMultiSelection=True, selectCommand=self.atualizeSkinFooter, parent=self.allUIs["skinningTabLayout"] )
        cmds.radioCollection( self.allUIs["jntCollection"], edit=True, select=dpARJoints )
        cmds.setParent(self.allUIs["skinningTabLayout"])
        
        #colSkinRightA - columnLayout:
        self.allUIs["colSkinRightA"] = cmds.columnLayout('colSkinRightA', adjustableColumn=True, width=190, parent=self.allUIs["skinningTabLayout"])
        self.allUIs["geomCollection"] = cmds.radioCollection('geomCollection', parent=self.allUIs["colSkinRightA"])
        allGeoms   = cmds.radioButton( label=self.langDic[self.langName]['i026_listAllJnts'], annotation="allGeoms", onCommand=self.populateGeoms )
        selGeoms   = cmds.radioButton( label=self.langDic[self.langName]['i027_listSelJnts'], annotation="selGeoms", onCommand=self.populateGeoms )
        self.allUIs["modelsTextScrollLayout"] = cmds.textScrollList( 'modelsTextScrollLayout', width=30, allowMultiSelection=True, selectCommand=self.atualizeSkinFooter, parent=self.allUIs["skinningTabLayout"] )
        cmds.radioCollection( self.allUIs["geomCollection"], edit=True, select=allGeoms )
        cmds.setParent(self.allUIs["skinningTabLayout"])
        
        #footerB - columnLayout:
        self.allUIs["footerB"] = cmds.columnLayout('footerB', adjustableColumn=True, parent=self.allUIs["skinningTabLayout"])
        cmds.separator(style='none', height=3, parent=self.allUIs["footerB"])
        self.allUIs["skinButton"] = cmds.button("skinButton", label=self.langDic[self.langName]['i028_skinButton'], backgroundColor=(0.5, 0.8, 0.8), command=self.skinFromUI, parent=self.allUIs["footerB"])
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
        
        # call tabLayouts:
        cmds.tabLayout( self.allUIs["languageTabLayout"], edit=True, tabLabel=((self.allUIs["riggingTabLayout"], 'Rigging'), (self.allUIs["skinningTabLayout"], 'Skinning')) )
        cmds.select(clear=True)
    
    
    def jobReloadUI(self, *args):
        """ This scriptJob active when we got one new scene in order to reload the UI.
        """
        cmds.select(clear=True)
        import dpAutoRig as dpAR
        reload( dpAR )
        dpUI = dpAR.DP_AutoRig_UI()
    
    
    def jobSelectedGuide(self):
        """ This scriptJob read if the selected item in the scene is a guideModule and reload the UI.
        """
        # run the UI part:
        selectedGuideNode = False
        selectedGuideNodeList = []
        selectedList = []
        # get selected items:
        selectedList = cmds.ls(selection=True, long=True)
        if selectedList:
            for selectedItem in selectedList:
                if cmds.objExists(selectedItem+".guideBase") and cmds.getAttr(selectedItem+".guideBase") == 1:
                    selectedGuideNode = True
                    selectedGuideNodeList.append(selectedItem)
        # re-create module layout:
        if selectedGuideNode:
            for moduleInstance in self.moduleInstancesList:
                cmds.button(moduleInstance.selectButton, edit=True, label=" ")
                for selectedGuide in selectedGuideNodeList:
                    selectedGuideInfo = cmds.getAttr(selectedGuide+".moduleInstanceInfo")
                    if selectedGuideInfo == str(moduleInstance):
                        moduleInstance.reCreateEditSelectedModuleLayout()
        # delete module layout:
        else:
            try:
                cmds.frameLayout('editSelectedModuleLayoutA', edit=True, label=self.langDic[self.langName]['i011_selectedModule'])
                cmds.deleteUI("selectedColumn")
                for moduleInstance in self.moduleInstancesList:
                    cmds.button(moduleInstance.selectButton, edit=True, label=" ")
            except:
                pass
        # re-select items:
        if selectedList:
            cmds.select(selectedList)
        # call reload the geometries in skin UI:
        self.reloadPopulatedGeoms()
    
    
    def populateJoints(self, *args):
        """ This function is responsable to list all joints or only dpAR joints in the interface in order to use in skinning.
        """
        # get current jointType (all or just dpAutoRig joints):
        jntSelectedRadioButton = cmds.radioCollection(self.allUIs["jntCollection"], query=True, select=True)
        chooseJnt = cmds.radioButton(jntSelectedRadioButton, query=True, annotation=True)
        
        # list joints to be populated:
        jntList = []
        allJointList = cmds.ls(selection=False, type="joint")
        if chooseJnt == "allJoints":
            jntList = allJointList
        elif chooseJnt == "dpARJoints":
            for jnt in allJointList:
                if cmds.objExists(jnt+'.dpAR_joint'):
                    jntList.append(jnt)
        
        # populate the list:
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, removeAll=True)
        cmds.textScrollList( self.allUIs["jntTextScrollLayout"], edit=True, append=jntList)
        # atualize of footerB text:
        self.atualizeSkinFooter()
    
    
    def populateGeoms(self, *args):
        """ This function is responsable to list all geometries or only selected geometries in the interface in order to use in skinning.
        """
        # get current geomType (all or just selected):
        geomSelectedRadioButton = cmds.radioCollection(self.allUIs["geomCollection"], query=True, select=True)
        chooseGeom = cmds.radioButton(geomSelectedRadioButton, query=True, annotation=True)
        
        # list geometries to be populated:
        geomList = []
        currentSelectedList = cmds.ls(selection=True, long=True)
        geomTypeList = ["mesh", "nurbsSurface", "subdiv"]
        for geomType in geomTypeList:
            allGeomList = cmds.ls(selection=False, type=geomType, long=True)
            if allGeomList:
                for meshName in allGeomList:
                    transformNameList = cmds.listRelatives(meshName, parent=True, fullPath=True, type="transform")
                    if transformNameList:
                        # do not add ribbon nurbs plane to the list:
                        if not cmds.objExists(transformNameList[0]+".doNotSkinIt"):
                            if not transformNameList[0] in geomList:
                                if chooseGeom == "allGeoms":
                                    geomList.append(transformNameList[0])
                                elif chooseGeom == "selGeoms":
                                    if transformNameList[0] in currentSelectedList or meshName in currentSelectedList:
                                        geomList.append(transformNameList[0])
        
        # populate the list:
        cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], edit=True, removeAll=True)
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
    def startGuideModules(self, guideDir, action, checkModuleList=None):
        """ Find and return the modules in the directory 'Modules'.
            Returns a list with the found modules.
        """
        # find path where 'dpAutoRig.py' is been executed:
        path = utils.findPath("dpAutoRig.py")
        print "dpAutoRigPath: "+path
        # list all guide modules:
        guideModuleList = utils.findAllModules(path, guideDir)
        print "Modules: "+str(guideModuleList)
        if guideModuleList:
            # change guide module list for alphabetic order:
            guideModuleList.sort()
            if action == "start":
                # create guide buttons:
                for guideModule in guideModuleList:
                    self.createGuideButton(guideModule, guideDir)
            elif action == "check":
                notFoundModuleList = []
                # verify the list if exists all elements in the folder:
                if checkModuleList:
                    for checkModule in checkModuleList:
                        if not checkModule in guideModuleList:
                            notFoundModuleList.append(checkModule)
                return notFoundModuleList
        return guideModuleList;
    
    
    def createGuideButton(self, guideModule, guideDir):
        """ Create a guideButton for guideModule in the respective colMiddleLeftA guidesLayout.
        """
        # especific import command for guides storing theses guides modules in a variable:
        #guide = __import__("dpAutoRigSystem."+guideDir+"."+guideModule, {}, {}, [guideModule])
        basePath = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(guide)
        # getting data from guide module:
        title = self.langDic[self.langName][guide.TITLE]
        description = self.langDic[self.langName][guide.DESCRIPTION]
        icon = guide.ICON
        # find path where 'dpAutoRig.py' is been executed to get the icon:
        path = utils.findPath("dpAutoRig.py")
        iconDir = path+icon
        # creating a basic layout for guide buttons:
        cmds.rowLayout( numberOfColumns=3, columnWidth3=(15, 30, 55), height=30, adjustableColumn=3, columnAlign=(1, 'left'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], parent=self.allUIs["guidesLayoutA"] )
        cmds.button(label='?', height=30, backgroundColor=(0.8, 0.8, 0.8), command=partial(self.info, guide.TITLE, guide.DESCRIPTION, None, 'center', 305, 250))
        cmds.image(i=iconDir)
        if guideDir == "Modules":
            cmds.button(label=title, height=30, command=partial(self.initGuide, guideModule, guideDir) )
        elif guideDir == "Scripts":
            cmds.button(label=title, height=30, command=partial(self.execScriptedGuide, guideModule, guideDir) )
        cmds.setParent('..')
    
    
    def initGuide(self, guideModule, guideDir, *args):
        """ Create a guideModuleReference (instance) of a further guideModule that will be rigged (installed).
            Returns the guide instance initialised.
        """
        # creating unique namespace:
        basename = "dpAR_"
        cmds.namespace(setNamespace=":")
        # list all namespaces:
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        # check if there is "__" (double undersore) in the namespaces:
        for i in range(len(namespaceList)):
            if namespaceList[i].find("__") != -1:
                # if yes, get the name after the "__":
                namespaceList[i] = namespaceList[i].partition("__")[2]
        # send this result to findLastNumber in order to get the next moduleName +1:
        newSuffix = utils.findLastNumber(namespaceList, basename) + 1
        # generate the current moduleName added the next new suffix:
        userSpecName = basename + str(newSuffix)
        # especific import command for guides storing theses guides modules in a variable:
        basePath = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        self.guide = __import__(basePath+"."+guideDir+"."+guideModule, {}, {}, [guideModule])
        reload(self.guide)
        # get the CLASS_NAME from guideModule:
        guideClass = getattr(self.guide, self.guide.CLASS_NAME)
        # initialize this guideModule as an guide Instance:
        dpUIinst = self
        guideInstance = guideClass(dpUIinst, self.langDic, self.langName, userSpecName)
        self.moduleInstancesList.append(guideInstance)
        # edit the footer A text:
        self.allGuidesList.append([guideModule, userSpecName])
        self.modulesToBeRiggedList = utils.getModulesToBeRigged(self.moduleInstancesList)
        cmds.text(self.allUIs["footerAText"], edit=True, label=str(len(self.modulesToBeRiggedList)) +" "+ self.langDic[self.langName]['i005_footerA'])
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
        # reload modules before scripted creation:
        self.populateCreatedGuideModules()
    
    
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
        guideDir = "Modules"
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
                    temp = validModuleNames[index]+"__"+userSpecName+":guide_base"
                    if cmds.objExists(validModuleNames[index]+"__"+userSpecName+":guide_base"):
                        self.allGuidesList.append([validModules[index], userSpecName])
                        
        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.allGuidesList:
            # clear current layout before reload modules:
            cmds.deleteUI(self.allUIs["modulesLayoutA"])
            self.allUIs["modulesLayoutA"] = cmds.columnLayout("modulesLayoutA", adjustableColumn=True, width=200, parent=self.allUIs["colMiddleRightA"])
            # load again the modules:
            guideFolder = utils.findEnv("PYTHONPATH", "dpAutoRigSystem")+".Modules"
            # this list will be used to rig all modules pressing the RIG button:
            for module in self.allGuidesList:
                mod = __import__(guideFolder+"."+module[0], {}, {}, [module[0]])
                reload(mod)
                # identify the guide modules and add to the moduleInstancesList:
                moduleClass = getattr(mod, mod.CLASS_NAME)
                dpUIinst = self
                moduleInst = moduleClass(dpUIinst, self.langDic, self.langName, userGuideName=module[1])
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
        prefixName = utils.normalizeText(enteredText, prefixMax=4)
        if prefixName == "":
            print self.langDic[self.langName]['p001_prefixText'],
            cmds.textField(self.allUIs["prefixTextField"], edit=True, text="")
        # edit the prefixTextField with the normalText:
        cmds.textField(self.allUIs["prefixTextField"], edit=True, text=prefixName+"_")
    
    
    def info(self, title, description, text, align, width, height, *args):
        """ Create a window showing the text info with the description about any module.
        """
        # declaring variables:
        self.info_title       = title
        self.info_description = description
        self.info_text          = text
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
    
    
    ###################### Start: Rigging Modules Instances.
    
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
            if cmds.objExists("dpAR_guideMirror_grp"):
                cmds.delete("dpAR_guideMirror_grp")
            
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
            
            # verify the integrate options:
            try:
                integrate = cmds.checkBox(self.allUIs["integrateCB"], query=True, value=True)
            except:
                pass
            if integrate == 1:
                # create master hierarchy:
                allTransformList = cmds.ls(selection=False, type='transform')
                foundMasterGrp  = False
                foundMasterCtrl = False
                for transform in allTransformList:
                    if cmds.objExists(transform+".masterGrp") and cmds.getAttr(transform+".masterGrp") == 1:
                        self.masterGrp = transform
                        # re-declare group names:
                        self.modelsGrp   = self.prefix+'MODELS_grp'
                        self.ctrlsGrp    = self.prefix+'CTRLS_grp'
                        self.dataGrp     = self.prefix+'DATA_grp'
                        self.staticGrp   = self.prefix+'static_grp'
                        self.scalableGrp = self.prefix+'scalable_grp'
                        foundMasterGrp = True
                    if cmds.objExists(transform+".masterCtrl") and cmds.getAttr(transform+".masterCtrl") == 1:
                        self.masterCtrl = transform
                        # re-declare controls:
                        self.rootCtrl   = self.prefix+'root_ctrl'
                        foundMasterCtrl = True
                if not foundMasterGrp:
                    # create a dpAR_masterGrp:
                    self.masterGrp = cmds.group(name=self.prefix+'dpAR_all_grp', empty=True)
                    cmds.addAttr(self.masterGrp, longName='masterGrp', attributeType='bool')
                    cmds.setAttr(self.masterGrp+'.masterGrp', 1)
                    # add data log:
                    # system:
                    cmds.addAttr(self.masterGrp, longName='system', dataType='string')
                    cmds.setAttr(self.masterGrp+".system", "dpAutoRig_"+DPAR_VERSION , type='string')
                    # date:
                    cmds.addAttr(self.masterGrp, longName='date', dataType='string')
                    localTime = str( time.asctime( time.localtime(time.time()) ) )
                    cmds.setAttr(self.masterGrp+".date", localTime, type='string')
                    # author:
                    cmds.addAttr(self.masterGrp, longName='author', dataType='string')
                    cmds.setAttr(self.masterGrp+".author", 'Danilo Pinheiro', type='string')
                    # module counts:
                    for guideType in self.guideModuleList:
                        cmds.addAttr(self.masterGrp, longName=guideType+'Count', attributeType='long', keyable=False)
                        cmds.setAttr(self.masterGrp+'.'+guideType+'Count', 0)
                    # create groups to parent module parts:
                    self.modelsGrp   = cmds.group(name=self.prefix+'MODELS_grp', empty=True)
                    self.ctrlsGrp    = cmds.group(name=self.prefix+'CTRLS_grp', empty=True)
                    self.dataGrp     = cmds.group(name=self.prefix+'DATA_grp', empty=True)
                    self.staticGrp   = cmds.group(name=self.prefix+'static_grp', empty=True)
                    self.scalableGrp = cmds.group(name=self.prefix+'scalable_grp', empty=True)
                    # arrange hierarchy:
                    cmds.parent(self.modelsGrp, self.ctrlsGrp, self.dataGrp, self.masterGrp)
                    cmds.parent(self.staticGrp, self.scalableGrp, self.dataGrp)
                    cmds.select(clear=True)
                    # set lock and hide attributes:
                    ctrls.setLockHide([self.masterGrp, self.modelsGrp, self.ctrlsGrp, self.dataGrp, self.staticGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])#, 'v'])
                if not foundMasterCtrl:
                    # create a dpAR_masterCtrl:
                    self.masterCtrl = cmds.circle(name=self.prefix+'master_ctrl', normal=(0, 1, 0), degree=3, radius=10, constructionHistory=False)[0]
                    cmds.addAttr(self.masterCtrl, longName='masterCtrl', attributeType='bool')
                    cmds.setAttr(self.masterCtrl+'.masterCtrl', 1)
                    # create a dpAR_rootCtrl:
                    self.rootCtrl = cmds.circle(name=self.prefix+'root_ctrl', normal=(0, 1, 0), degree=1, radius=9.5, constructionHistory=False)[0]
                    cmds.parent(self.rootCtrl, self.masterCtrl)
                    cmds.parent(self.masterCtrl, self.ctrlsGrp)
                    # prepare globalScale:
                    cmds.scaleConstraint(self.masterCtrl, self.scalableGrp, name=self.scalableGrp+"_scaleConstraint")
                    # set lock and hide attributes:
                    ctrls.setLockHide([self.scalableGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])
                    ctrls.setLockHide([self.rootCtrl], ['sx', 'sy', 'sz'])
                    cmds.setAttr(self.masterCtrl+'.visibility', keyable=False)

                    
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
                        self.itemRiggedGrp = self.itemGuideName + "_grp"
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
                                self.fatherRiggedParentNode = self.originedFromDic[self.fatherName+"_guide_"+self.fatherGuideLoc]
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
                            cmds.parent(self.ctrlHookGrp, self.rootCtrl)
                            # make ctrlHookGrp inactive:
                            cmds.setAttr(self.ctrlHookGrp+".ctrlHook", 0)
                        
                        if self.rootHookGrp:
                            # parent module rootHook to rootCtrl:
                            cmds.parent(self.rootHookGrp, self.rootCtrl)
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
                
                # integrating modules togheter:
                # working with specific cases:
                if self.integratedTaskDic:
                    defaultAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
                    for moduleDic in self.integratedTaskDic:
                        moduleType = moduleDic[:moduleDic.find("__")]
                        # footGuide parented in the extremGuide of the limbModule:
                        if moduleType == "Foot":
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                            if fatherModule == "Limb" and fatherGuideLoc == 'extrem':
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
                                    footJnt           = self.integratedTaskDic[moduleDic]['footJntList'][s]
                                    # getting limb data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    ikCtrl                = self.integratedTaskDic[fatherGuide]['ikCtrlList'][s]
                                    ikHandleGrp           = self.integratedTaskDic[fatherGuide]['ikHandleGrpList'][s]
                                    ikHandlePointConst    = self.integratedTaskDic[fatherGuide]['ikHandlePointConstList'][s]
                                    ikFkBlendGrpToRevFoot = self.integratedTaskDic[fatherGuide]['ikFkBlendGrpToRevFootList'][s]
                                    extremJntList         = self.integratedTaskDic[fatherGuide]['extremJntList'][s]
                                    parentConstToRFOffset = self.integratedTaskDic[fatherGuide]['parentConstToRFOffsetList'][s]
                                    # do task actions in order to integrate the limb and foot:
                                    cmds.delete(ikHandlePointConst, parentConst)
                                    cmds.parent(revFootCtrlZero, ikFkBlendGrpToRevFoot, absolute=True)
                                    cmds.parent(ikHandleGrp, toLimbIkHandleGrp, absolute=True)
                                    parentConstExtremFoot = cmds.parentConstraint(extremJntList, footJnt, maintainOffset=True, name=footJnt+"_parentConstraint")[0]
                                    # organize to avoid offset error in the parentConstraint with negative scale:
                                    if cmds.getAttr(parentConstToRFOffset+".mustCorrectOffset") == 1:
                                        cmds.setAttr(parentConstToRFOffset+".target[1].targetOffsetRotateX", cmds.getAttr(parentConstToRFOffset+".fixOffsetX"))
                                        cmds.setAttr(parentConstToRFOffset+".target[1].targetOffsetRotateY", cmds.getAttr(parentConstToRFOffset+".fixOffsetY"))
                                        cmds.setAttr(parentConstToRFOffset+".target[1].targetOffsetRotateZ", cmds.getAttr(parentConstToRFOffset+".fixOffsetZ"))
                                    # hide this control shape
                                    cmds.setAttr(revFootCtrlShape+".visibility", 0)
                                    # add float attributes and connect from ikCtrl to revFootCtrl:
                                    floatAttrList = cmds.listAttr(revFootCtrl, visible=True, scalar=True, keyable=True)
                                    for floatAttr in floatAttrList:
                                        if not floatAttr in defaultAttrList and not cmds.objExists(ikCtrl+'.'+floatAttr):
                                            cmds.addAttr(ikCtrl, longName=floatAttr, attributeType='float', keyable=True)
                                            cmds.connectAttr(ikCtrl+'.'+floatAttr, revFootCtrl+'.'+floatAttr, force=True)
                        
                        # worldRef of extremGuide from limbModule controled by masterCtrl:
                        if moduleType == "Limb":
                            # getting limb data:
                            worldRefList      = self.integratedTaskDic[moduleDic]['worldRefList']
                            worldRefShapeList = self.integratedTaskDic[moduleDic]['worldRefShapeList']
                            for w, worldRef in enumerate(worldRefList):
                                # do actions in order to make limb be controled by masterCtrl:
                                floatAttrList = cmds.listAttr(worldRef, visible=True, scalar=True, keyable=True)
                                for f, floatAttr in enumerate(floatAttrList):
                                    if f < len(floatAttrList):
                                        if not floatAttr in defaultAttrList:
                                            if not cmds.objExists(self.masterCtrl+'.'+floatAttr):
                                                currentValue = cmds.getAttr(worldRef+'.'+floatAttr)
                                                cmds.addAttr(self.masterCtrl, longName=floatAttr, attributeType='float', minValue=0, maxValue=1, defaultValue=currentValue, keyable=True)
                                            cmds.connectAttr(self.masterCtrl+'.'+floatAttr, worldRef+'.'+floatAttr, force=True)
                                if not floatAttrList[len(floatAttrList)-1] in defaultAttrList and not cmds.objExists(self.masterCtrl+'.'+floatAttrList[len(floatAttrList)-1]):
                                    cmds.addAttr(self.masterCtrl, longName=floatAttrList[len(floatAttrList)-1], attributeType='float', defaultValue=1, keyable=True)
                                    cmds.connectAttr(self.masterCtrl+'.'+floatAttrList[len(floatAttrList)-1], worldRef+'.'+floatAttrList[len(floatAttrList)-1], force=True)
                                cmds.setAttr(worldRefShapeList[w]+'.visibility', 0)
                            
                            # parenting correctely the ikCtrlZero to spineModule:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                            if fatherModule == "Spine":
                                self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                                self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                                # working with item guide mirror:
                                self.itemMirrorNameList = [""]
                                # get itemGuideName:
                                if self.itemGuideMirrorAxis != "off":
                                    self.itemMirrorNameList = self.itemGuideMirrorNameList
                                for s, sideName in enumerate(self.itemMirrorNameList):
                                    # getting limb data:
                                    limbType             = self.integratedTaskDic[moduleDic]['limbType']
                                    ikCtrlZero           = self.integratedTaskDic[moduleDic]['ikCtrlZeroList'][s]
                                    ikPoleVectorCtrlZero = self.integratedTaskDic[moduleDic]['ikPoleVectorZeroList'][s]
                                    limbStyle            = self.integratedTaskDic[moduleDic]['limbStyle']
                                    
                                    # getting spine data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    hipsA  = self.integratedTaskDic[fatherGuide]['hipsAList'][0]
                                    chestA = self.integratedTaskDic[fatherGuide]['chestAList'][0]
                                    # verifing what part will be used, the hips or chest:
                                    if limbType == "leg":
                                        # do task actions in order to integrate the limb of leg type to rootCtrl:
                                        cmds.parent(ikCtrlZero, self.rootCtrl, absolute=True)
                                        cmds.parent(ikPoleVectorCtrlZero, self.rootCtrl, absolute=True)
                                    elif fatherGuideLoc == "jointLoc1":
                                        # do task actions in order to integrate the limb and spine (ikCtrl):
                                        cmds.parent(ikCtrlZero, hipsA, absolute=True)
                                    else:
                                        # do task actions in order to integrate the limb and spine (ikCtrl):
                                        cmds.parent(ikCtrlZero, chestA, absolute=True)
                                    # verify if is quadruped
                                    if limbStyle == "quadruped" or limbStyle == "quadSpring":
                                        if fatherGuideLoc != "jointLoc1":
                                            # get extra info from limb module data:
                                            quadFrontLeg = self.integratedTaskDic[moduleDic]['quadFrontLegList'][s]
                                            ikCtrl       = self.integratedTaskDic[moduleDic]['ikCtrlList'][s]
                                            # if quadruped, create a parent contraint from chestA to front leg:
                                            quadChestParentConst = cmds.parentConstraint(self.rootCtrl, chestA, quadFrontLeg, maintainOffset=True, name=quadFrontLeg+"_parentConstraint")[0]
                                            revNode = cmds.createNode('reverse', name=quadFrontLeg+"_rev")
                                            cmds.addAttr(ikCtrl, longName="followChestA", attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                                            cmds.connectAttr(ikCtrl+".followChestA", quadChestParentConst+"."+chestA+"W1", force=True)
                                            cmds.connectAttr(ikCtrl+".followChestA", revNode+".inputX", force=True)
                                            cmds.connectAttr(revNode+".outputX", quadChestParentConst+"."+self.rootCtrl+"W0", force=True)
                            
                            # fixing ikSpringSolver parenting for quadrupeds:
                            # getting limb data:
                            fixIkSpringSolverGrp = self.integratedTaskDic[moduleDic]['fixIkSpringSolverGrpList']
                            if fixIkSpringSolverGrp:
                                cmds.parent(fixIkSpringSolverGrp, self.scalableGrp, absolute=True)
                            
                        # integrate the volumeVariation attribute from Spine module to masterCtrl:
                        if moduleType == "Spine":
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                # connect the masterCtrl vvAttr to hipsA vvAttr and hide it for each side of the mirror (if it exists):
                                hipsA  = self.integratedTaskDic[moduleDic]['hipsAList'][s]
                                vvAttr = self.integratedTaskDic[moduleDic]['volumeVariationAttrList'][s]
                                cmds.addAttr(self.masterCtrl, longName=vvAttr, attributeType="float", defaultValue=1, keyable=True)
                                cmds.connectAttr(self.masterCtrl+'.'+vvAttr, hipsA+'.'+vvAttr)
                                cmds.setAttr(hipsA+'.'+vvAttr, keyable=False)
                
                        # integrate the head orient from the masterCtrl:
                        if moduleType == "Head":
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                # connect the masterCtrl to head group B using a orientConstraint:
                                grpHeadB = self.integratedTaskDic[moduleDic]['grpHeadBList'][s]
                                headRevNode = self.integratedTaskDic[moduleDic]['headRevNodeList'][s]
                                headOrientConst = cmds.orientConstraint(self.rootCtrl, grpHeadB, maintainOffset=True, name=grpHeadB+"_orientConstraint")[0]
                                cmds.connectAttr(headRevNode+'.outputX', headOrientConst+".root_ctrlW1", force=True)
                                
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
        
        # re-declaring guideMirror and previewMirror groups:
        self.guideMirrorGrp = 'dpAR_guideMirror_grp'
        if cmds.objExists(self.guideMirrorGrp):
            cmds.delete(self.guideMirrorGrp)
        
        # reload the jointSkinList:
        self.populateJoints()
        
        # select the masterCtrl:
        try:
            cmds.select(self.masterCtrl)
        except:
            pass
        
        # call log window:
        self.logWin()
        
    
    ###################### End: Rigging Modules Instances.
    
    
    ###################### Start: Skinning.
    
    def skinFromUI(self, *args):
        """ Skin the geometries using the joints, reading from UI the selected items of the textScrollLists or getting all items if nothing selected.
        """
        # get joints to be skinned:
        jointSkinList = cmds.textScrollList( self.allUIs["jntTextScrollLayout"], query=True, selectItem=True)
        if not jointSkinList:
            jointSkinList = cmds.textScrollList( self.allUIs["jntTextScrollLayout"], query=True, allItems=True)
        
        # get geometries to be skinned:
        geomSkinList = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, selectItem=True)
        if not geomSkinList:
            geomSkinList = cmds.textScrollList( self.allUIs["modelsTextScrollLayout"], query=True, allItems=True)
        
        if jointSkinList and geomSkinList:
            for geomSkin in geomSkinList:
                cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, removeUnusedInfluence=False)
        else:
            print self.langDic[self.langName]['i029_skinNothing'],
    
    ###################### End: Skinning.