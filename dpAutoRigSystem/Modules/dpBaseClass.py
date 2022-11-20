# importing libraries:
from maya import cmds
from maya import mel

from .Library import dpControls
from .Library import dpUtils
from ..Extras import dpCorrectionManager

class RigType(object):
    biped = "biped"
    quadruped = "quadruped"
    default = "unknown" #Support old guide system

class StartClass(object):
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, userGuideName, rigType, CLASS_NAME, TITLE, DESCRIPTION, ICON, *args):
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
        self.rigType = rigType
        self.presetDic = presetDic
        self.presetName = presetName
        # defining namespace:
        self.guideNamespace = self.guideModuleName + "__" + self.userGuideName
        # defining guideNamespace:
        cmds.namespace(setNamespace=":")
        self.namespaceExists = cmds.namespace(exists=self.guideNamespace)
        self.guideName = self.guideNamespace + ":Guide"
        self.moduleGrp = self.guideName+"_Base"
        self.radiusCtrl = self.moduleGrp+"_RadiusCtrl"
        self.annotation = self.moduleGrp+"_Ant"
        # calling dpControls:
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName, self.moduleGrp)
        # starting correctionManater:
        self.correctionManager = dpCorrectionManager.CorrectionManager(self.dpUIinst, self.langDic, self.langName, self.presetDic, self.presetName, False)
        # starting module:
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
        self.topColumn = cmds.columnLayout(self.moduleLayout+"_TopColumn", adjustableColumn=True, parent=self.moduleFrameLayout)
        # here we have just the column layouts to be populated by modules.
    
    
    def createGuide(self, *args):
        """ Create the elements to Guide module in the scene, like controls, etc...
        """
        # GUIDE:
        dpUtils.useDefaultRenderLayer()
        # create guide base (moduleGrp):
        guideBaseList = self.ctrls.cvBaseGuide(self.moduleGrp, r=2)
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
        
        baseStringAttrList  = ['moduleNamespace', 'customName', 'mirrorAxis', 'mirrorName', 'mirrorNameList', 'hookNode', 'moduleInstanceInfo', 'guideObjectInfo', 'rigType', 'dpARVersion']
        for baseStringAttr in baseStringAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseStringAttr, dataType='string')
        cmds.setAttr(self.moduleGrp+".mirrorAxis", "off", type='string')
        cmds.setAttr(self.moduleGrp+".mirrorName", self.langDic[self.langName]['p002_left']+' --> '+self.langDic[self.langName]['p003_right'], type='string')
        cmds.setAttr(self.moduleGrp+".hookNode", "_Grp", type='string')
        cmds.setAttr(self.moduleGrp+".moduleInstanceInfo", self, type='string')
        cmds.setAttr(self.moduleGrp+".guideObjectInfo", self.dpUIinst.guide, type='string')
        cmds.setAttr(self.moduleGrp+".rigType", self.rigType, type='string')
        cmds.setAttr(self.moduleGrp+".dpARVersion", self.dpUIinst.dpARVersion, type='string')
        
        baseFloatAttrList = ['shapeSize']
        for baseFloatAttr in baseFloatAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseFloatAttr, attributeType='float')
        cmds.setAttr(self.moduleGrp+".shapeSize", 1)
        
        baseIntegerAttrList = ['degree']
        for baseIntAttr in baseIntegerAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseIntAttr, attributeType='short')
        cmds.setAttr(self.moduleGrp+".degree", self.dpUIinst.degreeOption)
        
        # create annotation to this module:
        self.annotation = cmds.annotate( self.moduleGrp, tx=self.moduleGrp, point=(0,2,0) )
        self.annotation = cmds.listRelatives(self.annotation, parent=True)[0]
        self.annotation = cmds.rename(self.annotation, self.moduleGrp+"_Ant")
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
                        mel.eval('warning \"'+ self.langDic[self.langName]['e000_GuideNotFound'] +' - '+ self.moduleGrp +'\";')
                    except:
                        pass
                    return False
    
    
    def deleteModule(self, *args):
        """ Delete the Guide, ModuleLayout and Namespace.
        """
        # delete mirror preview:
        try:
            cmds.delete(self.moduleGrp[:self.moduleGrp.find(":")]+"_MirrorGrp")
        except:
            pass
        # delete the guide module:
        dpUtils.clearNodeGrp(nodeGrpName=self.moduleGrp, attrFind='guideBase', unparent=True)
        # clear default 'dpAR_GuideMirror_Grp':
        dpUtils.clearNodeGrp()
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
    

    def duplicateModule(self, *args):
        """ This module will just do a simple duplicate from Maya because we have a scriptJob to do the creating a new instance setup.
        """
        cmds.duplicate(self.moduleGrp)

    
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
            self.enteredText = self.enteredText.replace(" ", "_")
            # call utils to return the normalized text:
            self.customName = dpUtils.normalizeText(self.enteredText, prefixMax=30)
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
                            if currentName:
                                if not currentName in dpAR_nameList:
                                    dpAR_nameList.append(currentName)
                    if dpAR_nameList:
                        dpAR_nameList.sort()
                        for currentName in dpAR_nameList:
                            if currentName == self.customName:
                                # getting the index of the last digit in the name:
                                n = len(currentName)+1
                                hasDigit = False
                                for i in reversed(range(len(currentName))):
                                    if currentName[i].isdigit():
                                        n = i
                                        hasDigit = True
                                    else:
                                        break
                                # adding a sequential number:
                                if hasDigit:
                                    moduleDigit = int(currentName[n:])
                                    self.customName = self.customName[:n] + str(moduleDigit+1)
                                # adding 1 at the name end:
                                else:
                                    self.customName = self.customName + str(1)
                                
                # edit the prefixTextField with the normalText:
                try:
                    cmds.textField(self.userName, edit=True, text=self.customName)
                except:
                    pass
                cmds.setAttr(self.moduleGrp+".customName", self.customName, type='string')
                cmds.setAttr(self.annotation+".text", self.customName, type='string')
                # set userGuideName:
                self.userGuideName = self.customName
    

    def setupCorrectiveNet(self, ctrl, firstNode, secondNode, netName, axis, axisOrder, inputEndValue, isLeg=None, legList=None, *args):
        """ Create the correction manager network node and returns it.
            legList = [
                        0 = rename,
                        1 = axis,
                        2 = axisOrder
                        3 = inputValue,
                    ]
        """
        if not cmds.objExists(ctrl+"."+self.langDic[self.langName]['c124_corrective']):
            cmds.addAttr(ctrl, longName=self.langDic[self.langName]['c124_corrective'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
        # corrective network node
        correctiveNet = self.correctionManager.createCorrectionManager([firstNode, secondNode], name=netName, correctType=self.correctionManager.angleName, toRivet=False, fromUI=False)
        cmds.connectAttr(ctrl+"."+self.langDic[self.langName]['c124_corrective'], correctiveNet+".corrective", force=True)
        cmds.setAttr(correctiveNet+".axis", axis)
        cmds.setAttr(correctiveNet+".axisOrder", axisOrder)
        if isLeg:
            cmds.setAttr(correctiveNet+".axis", legList[1])
            cmds.setAttr(correctiveNet+".axisOrder", legList[2])
        correctionNetInputValue = cmds.getAttr(correctiveNet+".inputValue")
        if correctionNetInputValue+inputEndValue == 0:
            inputEndValue += 1
        cmds.setAttr(correctiveNet+".inputStart", correctionNetInputValue) #offset default position
        cmds.setAttr(correctiveNet+".inputEnd", correctionNetInputValue+inputEndValue)
        if isLeg:
            if correctionNetInputValue+legList[3] == 0:
                legList[3] += 1
            cmds.setAttr(correctiveNet+".inputEnd", correctionNetInputValue+legList[3])
            correctiveNet = self.correctionManager.changeName(legList[0])+"_Net"
        return correctiveNet


    def setupJcrControls(self, jcrList, s, jointLabelAdd, labelName, correctiveNetList, calibratePresetList, invertList, mirrorList=None, *args):
        """ Create corrective joint controllers.
        """
        if jcrList:
            l = 0
            sDefault = s
            mirrorPrefixList = [self.langDic[self.langName]['p002_left'], self.langDic[self.langName]['p003_right']]
            for i, jcr in enumerate(jcrList):
                if not i == 0: #exclude jar in the index 0
                    # logic to mirror calibration setup for left and right sides of a centered module like neck/head
                    m = i
                    if mirrorList:
                        if mirrorList[i]:
                            s += 1
                            if l == 0:
                                oldJcr = jcr
                                jcr = cmds.rename(jcr, mirrorPrefixList[l]+"_"+jcr)
                            else:
                                jcr = cmds.rename(jcr, mirrorPrefixList[l]+"_"+oldJcr)
                                m -= 1
                            jcrList[i] = jcr
                            l += 1
                        else:
                            m = i
                            s = sDefault
                    else:
                        s = sDefault
                    # add joint label, create controller, zeroOut
                    dpUtils.setJointLabel(jcr, s+jointLabelAdd, 18, labelName+"_"+str(m))
                    jcrCtrl, jcrGrp = self.ctrls.createCorrectiveJointCtrl(jcrList[i], correctiveNetList[i], radius=self.ctrlRadius*0.2)
                    cmds.parent(jcrGrp, self.correctiveCtrlsGrp)
                    # preset calibration
                    for calibrateAttr in calibratePresetList[i].keys():
                        cmds.setAttr(jcrCtrl+"."+calibrateAttr, calibratePresetList[i][calibrateAttr]*self.ctrlRadius)
                    if invertList:
                        invertAttrList = invertList[i]
                        if invertAttrList:
                            for invertAttr in invertAttrList:
                                cmds.setAttr(jcrCtrl+"."+invertAttr, 1)
                                cmds.addAttr(jcrCtrl+"."+invertAttr, edit=True, defaultValue=1)

    
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
            
            # unPinGuides before Rig them:
            self.ctrls.unPinGuide(self.moduleGrp)
            
            # RIG:
            dpUtils.useDefaultRenderLayer()
            
            # get the radius value to controls:
            if cmds.objExists(self.radiusCtrl):
                self.ctrlRadius = dpUtils.getCtrlRadius(self.radiusCtrl)
            else:
                self.ctrlRadius = 1
                
            # get curve degree:
            self.curveDegree = cmds.getAttr(self.moduleGrp+".degree")
            
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
        
        
    # Getters:
    #
    def getArticulation(self, *args):
        return cmds.getAttr(self.moduleGrp+".articulation")

    def getModuleAttr(self, moduleAttr, *args):
        return cmds.getAttr(self.moduleGrp + "." + moduleAttr)

    
    # Setters:
    #
    def setArticulation(self, value, *args):
        self.addArticJoint = value
        cmds.setAttr(self.moduleGrp + ".articulation", value)
    
    def setCorrective(self, value, *args):
        self.addCorrective = value
        cmds.setAttr(self.moduleGrp + ".corrective", value)