# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
import dpControls as ctrls
import dpUtils as utils


class StartClass:
    def __init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.userGuideName = userGuideName
        # defining namespace:
        self.guideNamespace = self.guideModuleName + "__" + self.userGuideName
        # defining guideNamespace:
        cmds.namespace(setNamespace=":")
        self.namespaceExists = cmds.namespace(exists=self.guideNamespace)
        self.guideName = self.guideNamespace + ":guide"
        self.moduleGrp = self.guideName+"_base"
        self.radiusCtrl = self.moduleGrp+"_radiusCtrl"
        self.annotation = self.moduleGrp+"_ant"
        if not self.namespaceExists:
            cmds.namespace(add=self.guideNamespace)
            # create GUIDE for this module:
            self.createGuide()
        # create the Module layout in the mainUI - modulesLayoutA:        
        self.createModuleLayout()
        # update module instance info:
        self.updateModuleInstanceInfo()
    
    
    def createModuleLayout(self, *args):
        """ Create the Module Layout, so it will exists in the right as a new options to editModules.
        """
        # MODULE LAYOUT:
        self.moduleLayout = self.langDic[self.langName][self.title]+" - "+self.userGuideName
        self.moduleFrameLayout = cmds.frameLayout(self.moduleLayout , label=self.moduleLayout, collapsable=True, collapse=False, parent="modulesLayoutA")
        self.topColumn = cmds.columnLayout(self.moduleLayout+"_topColumn", adjustableColumn=True, parent=self.moduleFrameLayout)
        # here we have just the column layouts to be populated by modules.
    
    
    def createGuide(self, *args):
        """ Create the elements to Guide module in the scene, like controls, etc...
        """
        # GUIDE:
        utils.useDefaultRenderLayer()
        # create guide base (moduleGrp):
        guideBaseList = ctrls.cvBaseGuide(self.moduleGrp, r=2)
        self.moduleGrp = guideBaseList[0]
        self.radiusCtrl = guideBaseList[1]
        # add attributes to be read when rigging module:
        baseBooleanAttrList = ['guideBase', 'mirrorEnable', 'displayAnnotation']
        for baseBooleanAttr in baseBooleanAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseBooleanAttr, attributeType='bool')
            cmds.setAttr(self.moduleGrp+"."+baseBooleanAttr, 1)
        
        baseIntegerAttrList = ['guideColor']
        for baseIntegerAttr in baseIntegerAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseIntegerAttr, attributeType='long')
        
        baseStringAttrList  = ['moduleNamespace', 'customName', 'mirrorAxis', 'mirrorName', 'mirrorNameList', 'hookNode', 'moduleInstanceInfo', 'guideObjectInfo']
        for baseStringAttr in baseStringAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseStringAttr, dataType='string')
        cmds.setAttr(self.moduleGrp+".mirrorAxis", "off", type='string')
        cmds.setAttr(self.moduleGrp+".mirrorName", self.langDic[self.langName]['p002_Left']+' --> '+self.langDic[self.langName]['p003_Right'], type='string')
        cmds.setAttr(self.moduleGrp+".hookNode", "_grp", type='string')
        cmds.setAttr(self.moduleGrp+".moduleInstanceInfo", self, type='string')
        cmds.setAttr(self.moduleGrp+".guideObjectInfo", self.dpUIinst.guide, type='string')
        
        # create annotation to this module:
        self.annotation = cmds.annotate( self.moduleGrp, tx=self.moduleGrp, point=(0,2,0) )
        self.annotation = cmds.listRelatives(self.annotation, parent=True)[0]
        self.annotation = cmds.rename(self.annotation, self.moduleGrp+"_ant")
        cmds.parent(self.annotation, self.moduleGrp)
        cmds.setAttr(self.annotation+'.text', self.moduleGrp[self.moduleGrp.find("__")+2:self.moduleGrp.rfind(":")], type='string')
        cmds.setAttr(self.annotation+'.template', 1)
    
    
    def updateModuleInstanceInfo(self, *args):
        """ Just update modeuleInstanceInfo attribute in the guideNode transform.
        """
        cmds.setAttr(self.moduleGrp+".moduleInstanceInfo", self, type='string')
    
    
    def verifyGuideModuleIntegrity(self, *args):
        """ This function verify the integrity of the current module.
            Returns True if Ok and False if Fail.
        """
        # conditionals to be elegible as a rigged guide module:
        if cmds.objExists(self.moduleGrp):
            if cmds.objExists(self.moduleGrp+'.guideBase'):
                if cmds.getAttr(self.moduleGrp+'.guideBase') == 1:
                    return True
                else:
                    try:
                        self.deleteModule()
                        mel.eval('warning \"'+ self.langDic[self.langName]['e000_guideNotFound'] +' - '+ self.moduleGrp +'\";')
                    except:
                        pass
                    return False
    
    
    def deleteModule(self, *args):
        """ Delete the Guide, ModuleLayout and Namespace.
        """
        # delete mirror preview:
        try:
            cmds.delete(self.moduleGrp[:self.moduleGrp.find(":")]+"_mirrorGrp")
        except:
            pass
        # delete the guide module:
        utils.clearNodeGrp(nodeGrpName=self.moduleGrp, attrFind='guideBase', unparent=True)
        # clear default 'dpAR_guideMirror_grp':
        utils.clearNodeGrp()
        # remove the namespaces:
        allNamespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        if self.guideNamespace in allNamespaceList:
            cmds.namespace(moveNamespace=(self.guideNamespace, ':'), force=True)
            cmds.namespace(removeNamespace=self.guideNamespace, force=True)
        try:
            # delete the moduleFrameLayout from window UI:
            cmds.deleteUI(self.moduleFrameLayout)
            self.clearSelectedModuleLayout()
            # edit the footer A text:
            self.currentText = cmds.text("footerAText", query=True, label=True)
            cmds.text("footerAText", edit=True, label=str(int(self.currentText[:self.currentText.find(" ")]) - 1) +" "+ self.langDic[self.langName]['i005_footerA'])
        except:
            pass
        # clear module from instance list (clean dpUI list):
        delIndex = self.dpUIinst.moduleInstancesList.index(self)
        self.dpUIinst.moduleInstancesList.pop(delIndex)
    
    
    def editUserName(self, checkText=None, *args):
        """ Edit the userGuideName to use the userName from module UI.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            if checkText:
                self.enteredText = checkText
            else:
                try:
                    # get the entered text:
                    self.enteredText = cmds.textField(self.userName, query=True, text=True)
                except:
                    self.enteredText = ""
            # call utils to return the normalized text:
            self.customName = utils.normalizeText(self.enteredText, prefixMax=10)
            # check if there is another rigged module using the same customName:
            if self.customName == "":
                try:
                    cmds.textField(self.userName, edit=True, text="")
                except:
                    pass
                cmds.setAttr(self.moduleGrp+".customName", "", type='string')
                self.userGuideName = self.guideNamespace.split("__")[-1]
            else:
                allTransformList = cmds.ls(selection=False, transforms=True)
                if allTransformList:
                    dpAR_nameList = []
                    for transform in allTransformList:
                        if cmds.objExists(transform+".dpAR_name"):
                            currentName = cmds.getAttr(transform+".dpAR_name")
                            dpAR_nameList.append(currentName)
                        if cmds.objExists(transform+".customName"):
                            currentName = cmds.getAttr(transform+".customName")
                            if not currentName in dpAR_nameList:
                                dpAR_nameList.append(currentName)
                    if dpAR_nameList:
                        for currentName in dpAR_nameList:
                            if currentName == self.customName:
                                addSuffix = True
                                while addSuffix:
                                    for n in range(1,len(dpAR_nameList)+1):
                                        if not self.customName+str(n) in dpAR_nameList:
                                            self.customName = self.customName + str(n)
                                            addSuffix = False
                                            break
                                    addSuffix = False
                # edit the prefixTextField with the normalText:
                try:
                    cmds.textField(self.userName, edit=True, text=self.customName)
                except:
                    pass
                cmds.setAttr(self.moduleGrp+".customName", self.customName, type='string')
                cmds.setAttr(self.annotation+".text", self.customName, type='string')
                # set userGuideName:
                self.userGuideName = self.customName
    
    
    def rigModule(self, *args):
        """ The fun part of the module, just read the values from editModuleLayout and create the rig for this guide.
            Delete the moduleLayout, guide and namespaces for this module.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            try:
                # clear selected module layout:
                self.clearSelectedModuleLayout()
            except:
                pass
            
            # RIG:
            utils.useDefaultRenderLayer()
            
            # get the radius value to controls:
            if cmds.objExists(self.radiusCtrl):
                self.ctrlRadius = utils.getCtrlRadius(self.radiusCtrl)
            else:
                self.ctrlRadius = 1
            
            # unparent all guide modules child:
            childrenList = cmds.listRelatives(self.moduleGrp, allDescendents=True, type='transform')
            if childrenList:
                for child in childrenList:
                    if cmds.objExists(child+".guideBase") and cmds.getAttr(child+".guideBase") == 1:
                        cmds.parent(child, world=True)
            
            # just edit customName and prefix:
            self.customName = cmds.getAttr(self.moduleGrp+".customName")
            if self.customName != "" and self.customName != " " and self.customName != "_" and self.customName != None:
                allTransformList = cmds.ls(selection=False, type="transform")
                if allTransformList:
                    for transform in allTransformList:
                        if cmds.objExists(transform+".dpAR_name"):
                            currentName = cmds.getAttr(transform+".dpAR_name")
                            if currentName == self.customName:
                                self.customName = self.customName + "1"
                self.userGuideName = self.customName
            prefix = cmds.textField("prefixTextField", query=True, text=True)
            if prefix != "" and prefix != " " and prefix != "_" and prefix != None:
                if prefix[len(prefix)-1] != "_":
                    prefix = prefix + "_"
                self.userGuideName = prefix + self.userGuideName
            cmds.select(clear=True)
    
    
    def integratingInfo(self, *args):
        """ This method just create this dictionary in order to build information of module integration.
        """
        self.integratedActionsDic = {}
