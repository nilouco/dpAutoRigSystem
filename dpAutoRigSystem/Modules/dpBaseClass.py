# importing libraries:
from maya import cmds
from maya import mel
from .Library import dpControls
from ..Tools import dpCorrectionManager

class RigType(object):
    biped = "biped"
    quadruped = "quadruped"
    default = "unknown" #Support old guide system

DP_STARTCLASS_VERSION = 2.4


class StartClass(object):
    def __init__(self, dpUIinst, userGuideName, rigType, CLASS_NAME, TITLE, DESCRIPTION, ICON, number=None, *args):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.userGuideName = userGuideName
        self.rigType = rigType
        # defining namespace:
        self.guideNamespace = self.guideModuleName+"__"+self.userGuideName
        # defining guideNamespace:
        cmds.namespace(setNamespace=":")
        self.namespaceExists = cmds.namespace(exists=self.guideNamespace)
        self.guideName = self.guideNamespace + ":Guide"
        self.moduleGrp = self.guideName+"_Base"
        self.radiusCtrl = self.moduleGrp+"_RadiusCtrl"
        self.annotation = self.moduleGrp+"_Ant"
        self.number = number
        self.raw = True
        self.serialized = False
        self.sideList = [""]
        self.axisList = ["X", "Y", "Z"]
        # utils
        self.utils = dpUIinst.utils
        # calling dpControls:
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.moduleGrp)
        # starting correctionManater:
        self.correctionManager = dpCorrectionManager.CorrectionManager(self.dpUIinst, False)
        # starting module:
        if not self.namespaceExists:
            cmds.namespace(add=self.guideNamespace)
            # create GUIDE for this module:
            self.createGuide()
        # create the Module layout in the mainUI - modulesLayoutA:        
        self.createModuleLayout()
        # update module instance info:
        self.updateModuleInstanceInfo()
        self.guideNet = self.utils.getNodeByMessage("net", self.moduleGrp)
        if self.guideNet:
            self.raw = cmds.getAttr(self.guideNet+".rawGuide")
    
    
    def createModuleLayout(self, *args):
        """ Create the Module Layout, so it will exists in the right as a new options to editModules.
        """
        # MODULE LAYOUT:
        self.moduleLayout = self.dpUIinst.lang[self.title]+" - "+self.userGuideName
        self.moduleFrameLayout = cmds.frameLayout(self.moduleLayout , label=self.moduleLayout, collapsable=True, collapse=False, parent="modulesLayoutA")
        self.topColumn = cmds.columnLayout(self.moduleLayout+"_TopColumn", adjustableColumn=True, parent=self.moduleFrameLayout)
        # here we have just the column layouts to be populated by modules.
    
    
    def createGuide(self, *args):
        """ Create the elements to Guide module in the scene, like controls, etc...
        """
        # GUIDE:
        self.utils.useDefaultRenderLayer()
        # create guide base (moduleGrp):
        guideBaseList = self.ctrls.cvBaseGuide(self.moduleGrp, r=2)
        self.moduleGrp = guideBaseList[0]
        self.radiusCtrl = guideBaseList[1]
        # add attributes to be read when rigging module:
        baseBooleanAttrList = ['guideBase', 'mirrorEnable', 'displayAnnotation']
        for baseBooleanAttr in baseBooleanAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseBooleanAttr, attributeType='bool')
            cmds.setAttr(self.moduleGrp+"."+baseBooleanAttr, 1)
        
        baseStringAttrList  = ['moduleType', 'moduleNamespace', 'customName', 'mirrorAxis', 'mirrorName', 'mirrorNameList', 'hookNode', 'moduleInstanceInfo', 'guideObjectInfo', 'rigType', 'dpARVersion']
        for baseStringAttr in baseStringAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseStringAttr, dataType='string')
        cmds.setAttr(self.moduleGrp+".moduleType", self.guideModuleName, type='string')
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        cmds.setAttr(self.moduleGrp+".mirrorAxis", "off", type='string')
        cmds.setAttr(self.moduleGrp+".mirrorName", self.dpUIinst.lang['p002_left']+' --> '+self.dpUIinst.lang['p003_right'], type='string')
        cmds.setAttr(self.moduleGrp+".hookNode", "_Grp", type='string')
        cmds.setAttr(self.moduleGrp+".moduleInstanceInfo", self, type='string')
        cmds.setAttr(self.moduleGrp+".guideObjectInfo", self.dpUIinst.guide, type='string')
        cmds.setAttr(self.moduleGrp+".rigType", self.rigType, type='string')
        cmds.setAttr(self.moduleGrp+".dpARVersion", self.dpUIinst.dpARVersion, type='string')
        
        baseFloatAttrList = ['shapeSize', 'worldSize']
        for baseFloatAttr in baseFloatAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseFloatAttr, attributeType='float', defaultValue=1)
        cmds.setAttr(self.moduleGrp+".worldSize", keyable=True)

        baseIntegerAttrList = ['degree']
        for baseIntAttr in baseIntegerAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseIntAttr, attributeType='short')
        cmds.setAttr(self.moduleGrp+".degree", self.dpUIinst.degreeOption)
        
        baseIntegerAttrList = ['guideColorIndex']
        for baseIntegerAttr in baseIntegerAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseIntegerAttr, attributeType='long')
        for c, guideColorAttr in enumerate(['guideColorR', 'guideColorG', 'guideColorB']):
            cmds.addAttr(self.moduleGrp, longName=guideColorAttr, attributeType='float')
            cmds.setAttr(self.moduleGrp+"."+guideColorAttr, self.dpUIinst.ctrls.colorList[0][c])

        # create annotation to this module:
        self.annotation = cmds.annotate( self.moduleGrp, tx=self.moduleGrp, point=(0,2,0) )
        self.annotation = cmds.listRelatives(self.annotation, parent=True)[0]
        self.annotation = cmds.rename(self.annotation, self.moduleGrp+"_Ant")
        cmds.parent(self.annotation, self.moduleGrp)
        cmds.setAttr(self.annotation+'.text', self.moduleGrp[self.moduleGrp.find("__")+2:self.moduleGrp.rfind(":")], type='string')
        cmds.setAttr(self.annotation+'.template', 1)
        # setup worldSize
        self.dpUIinst.ctrls.getDPARTempGrp()
        self.createWorldSize()
        # prepare guide to serialization
        self.createGuideNetwork()
    
    
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
                        mel.eval('warning \"'+ self.dpUIinst.lang['e000_guideNotFound'] +' - '+ self.moduleGrp +'\";')
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
        if cmds.objExists(self.moduleGrp+"_WorldSize_Ref"):
            cmds.delete(self.moduleGrp+"_WorldSize_Ref")
        # delete the guide module:
        self.utils.clearNodeGrp(self.moduleGrp, 'guideBase', unparent=True)
        # clear default 'dpAR_GuideMirror_Grp':
        self.utils.clearNodeGrp()
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
            cmds.text("footerAText", edit=True, label=str(int(self.currentText[:self.currentText.find(" ")]) - 1) +" "+ self.dpUIinst.lang['i005_footerA'])
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
            self.customName = self.utils.normalizeText(self.enteredText, prefixMax=30)
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
        if not cmds.objExists(ctrl+"."+self.dpUIinst.lang['c124_corrective']):
            cmds.addAttr(ctrl, longName=self.dpUIinst.lang['c124_corrective'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
        # corrective network node
        correctiveNet = self.correctionManager.createCorrectionManager([firstNode, secondNode], name=netName, correctType=self.correctionManager.angleName, toRivet=False, fromUI=False)
        cmds.connectAttr(ctrl+"."+self.dpUIinst.lang['c124_corrective'], correctiveNet+".corrective", force=True)
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
            mirrorPrefixList = [self.dpUIinst.lang['p002_left'], self.dpUIinst.lang['p003_right']]
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
                    self.utils.setJointLabel(jcr, s+self.jointLabelAdd, 18, labelName+"_"+str(m))
                    jcrCtrl, jcrGrp = self.ctrls.createCorrectiveJointCtrl(jcrList[i], correctiveNetList[i], radius=self.ctrlRadius*0.2)
                    cmds.parent(jcrGrp, self.correctiveCtrlsGrp)
                    # preset calibration
                    for calibrateAttr in calibratePresetList[i].keys():
                        if "calibrateT" in calibrateAttr:
                            cmds.setAttr(jcrCtrl+"."+calibrateAttr, calibratePresetList[i][calibrateAttr]*self.ctrlRadius)
                        else:
                            cmds.setAttr(jcrCtrl+"."+calibrateAttr, calibratePresetList[i][calibrateAttr])
                    if invertList:
                        invertAttrList = invertList[i]
                        if invertAttrList:
                            for invertAttr in invertAttrList:
                                cmds.setAttr(jcrCtrl+"."+invertAttr, 1)
                                cmds.addAttr(jcrCtrl+"."+invertAttr, edit=True, defaultValue=1)


    def changeMainCtrlsNumber(self, enteredNCtrls, *args):
        """ Edit the number of main controllers in the guide.
        """
        self.utils.useDefaultRenderLayer()
        # get the number of main controllers entered by user:
        if enteredNCtrls == 0:
            try:
                self.nMainCtrlAttr = cmds.intField(self.nMainCtrlIF, query=True, value=True)
            except:
                return
        else:
            self.nMainCtrlAttr = enteredNCtrls
        # limit range
        if self.nMainCtrlAttr >= self.currentNJoints:
            self.nMainCtrlAttr = self.currentNJoints - 1
            if self.nMainCtrlAttr == 0:
                self.nMainCtrlAttr = 1
                cmds.checkBox(self.mainCtrlsCB, edit=True, editable=False)
            cmds.intField(self.nMainCtrlIF, edit=True, value=self.nMainCtrlAttr)
        cmds.setAttr(self.moduleGrp+".nMain", self.nMainCtrlAttr)


    def enableMainCtrls(self, value, *args):
        """ Just enable or disable the main controllers int field UI.
        """
        cmds.intField(self.nMainCtrlIF, edit=True, editable=value)
        cmds.checkBox(self.mainCtrlsCB, edit=True, editable=True)


    def setAddMainCtrls(self, value, *args):
        """ Just store the main controllers checkBox value and enable the int field.
        """
        cmds.setAttr(self.moduleGrp+".mainControls", value)
        self.enableMainCtrls(value)


    def addFkMainCtrls(self, side, ctrlList, *args):
        """ Implement the fk main controllers.
        """
        # getting and calculating values
        totalToAddMain = 1
        self.nMain = cmds.getAttr(self.base+".nMain")
        if self.nMain > 1:
            totalToAddMain = int(self.nJoints/self.nMain)
        # run throgh the chain
        for m in range(0, self.nMain):
            startAt = m*totalToAddMain
            endAt = (m+1)*totalToAddMain
            if m == self.nMain-1:
                endAt = self.nJoints
            for n in range(startAt, endAt):
                currentCtrl = ctrlList[n]
                currentCtrlZero = cmds.listRelatives(currentCtrl, parent=True)[0]
                if n == startAt:
                    # create a main controller
                    mainCtrl = self.ctrls.cvControl("id_096_FkLineMain", side+self.userGuideName+"_%02d_Main_Fk_Ctrl"%(n), r=self.ctrlRadius*1.2, d=self.curveDegree)
                    self.ctrls.colorShape([mainCtrl], "cyan")
                    cmds.addAttr(mainCtrl, longName=self.dpUIinst.lang['c049_intensity'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                    # position
                    cmds.parent(mainCtrl, currentCtrlZero)
                    cmds.makeIdentity(mainCtrl, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(currentCtrl, mainCtrl)
                    # intensity utilities
                    rIntensityMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_R_Main_MD")
                    self.toIDList.append(rIntensityMD)
                    for axis in self.axisList:
                        cmds.connectAttr(mainCtrl+".rotate"+axis, rIntensityMD+".input1"+axis, force=True)
                        cmds.connectAttr(mainCtrl+"."+self.dpUIinst.lang['c049_intensity'], rIntensityMD+".input2"+axis, force=True)
                else:
                    # offseting sub controllers
                    offsetGrp = cmds.group(name=currentCtrl+"_Offset_Grp", empty=True)
                    cmds.parent(offsetGrp, currentCtrlZero)
                    cmds.makeIdentity(offsetGrp, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(currentCtrl, offsetGrp)
                    for axis in self.axisList:
                        cmds.connectAttr(rIntensityMD+".output"+axis, offsetGrp+".rotate"+axis, force=True)
                # display sub controllers shapes
                self.ctrls.setSubControlDisplay(mainCtrl, currentCtrl, 0)
    

    def getMirrorSideList(self, *args):
        """ Processes the mirror information for the current guide.
        Defines self.sideList to be used by the module.
        """
        # analisys the mirror module:
        self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
        if self.mirrorAxis != 'off':
            # get rigs names:
            self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
            # get first and last letters to use as side initials (prefix):
            self.sideList = [self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_']
            for s, side in enumerate(self.sideList):
                duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, side+self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirrorGrp, absolute=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                # do a group mirror with negative scaling:
                if s == 1:
                    withoutFlip = False
                    if cmds.objExists(self.moduleGrp+".flip"):
                        if cmds.getAttr(self.moduleGrp+".flip") == 0:
                            withoutFlip = True
                    if withoutFlip:
                        for axis in self.mirrorAxis:
                            gotValue = cmds.getAttr(side+self.userGuideName+"_Guide_Base.translate"+axis)
                            flipedValue = gotValue*(-2)
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                    else:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
            # joint labelling:
            self.jointLabelAdd = 1
        else: # if not mirror:
            duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
            allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
            for item in allGuideList:
                cmds.rename(item, self.userGuideName+"_"+item)
            self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
            # re-rename grp:
            cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # joint labelling:
            self.jointLabelAdd = 0
        # store the number of this guide by module type
        self.dpAR_count = self.utils.findModuleLastNumber(self.guideModuleName, "dpAR_type")+1


    def rigModule(self, *args):
        """ The fun part of the module, just read the values from editModuleLayout and create the rig for this guide.
        """
        self.dpUIinst.utils.closeUI(self.dpUIinst.plusInfoWinName)
        self.dpUIinst.utils.closeUI(self.dpUIinst.colorOverrideWinName)
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            self.toIDList = []
            self.oldUnitConversionList = cmds.ls(selection=False, type="unitConversion")
            try:
                # clear selected module layout:
                self.clearSelectedModuleLayout()
            except:
                pass

            # unPinGuides before Rig them:
            self.ctrls.unPinGuide(self.moduleGrp)
            
            # RIG:
            self.utils.useDefaultRenderLayer()
            
            # get the radius value to controls:
            if cmds.objExists(self.radiusCtrl):
                self.ctrlRadius = self.utils.getCtrlRadius(self.radiusCtrl)
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
            self.getMirrorSideList()
    

    def hookSetup(self, side, ctrlList, scalableList, staticList=None, *args):
        """ Generate the hook setup to find lists of controllers, scalable and static groups.
            Add message attributes to map hooked groups for the rigged module.
        """
        # create a masterModuleGrp to be checked if this rig exists:
        self.toCtrlHookGrp     = cmds.group(ctrlList, name=side+self.userGuideName+"_Control_Grp")
        self.toScalableHookGrp = cmds.group(scalableList, name=side+self.userGuideName+"_Scalable_Grp")
        self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Static_Grp")
        if staticList:
            cmds.parent(staticList, self.toStaticHookGrp)
        # create a locator in order to avoid delete static group
        loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE_PLEASE_Loc")[0]
        self.dpUIinst.customAttr.addAttr(0, [self.toCtrlHookGrp, self.toScalableHookGrp, self.toStaticHookGrp, loc]) #dpID
        cmds.setAttr(loc+".visibility", 0)
        cmds.parent(loc, self.toStaticHookGrp, absolute=True)
        self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        # add hook attributes to be read when rigging integrated modules:
        self.utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
        self.utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
        self.utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
        cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
        cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
        cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
        cmds.setAttr(self.toStaticHookGrp+".dpAR_type", self.guideModuleName, type="string")
        # add module type counter value
        cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
        cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', self.dpAR_count)
        # message attributes
        cmds.addAttr(self.toStaticHookGrp, longName="controlHookGrp", attributeType="message")
        cmds.addAttr(self.toStaticHookGrp, longName="scalableHookGrp", attributeType="message")
        cmds.connectAttr(self.toCtrlHookGrp+".message", self.toStaticHookGrp+".controlHookGrp", force=True)
        cmds.connectAttr(self.toScalableHookGrp+".message", self.toStaticHookGrp+".scalableHookGrp", force=True)
        cmds.setAttr(self.toScalableHookGrp+".visibility", self.getJointsVisibility())
        cmds.setAttr(self.toStaticHookGrp+".visibility", self.getJointsVisibility())

    
    def integratingInfo(self, *args):
        """ This method just create this dictionary in order to build information of module integration.
        """
        self.integratedActionsDic = {}
    

    def createGuideNetwork(self, *args):
        """ Create a network for the current guide and store on it the nodes used in this module by message.
        """
        if self.number:
            guideNumber = self.number
        else:
            guideNumber = self.utils.findLastNumber()
        self.guideNet = cmds.createNode("network", name="dpGuide_"+guideNumber+"_Net")
        self.dpUIinst.customAttr.addAttr(0, [self.guideNet]) #dpID
        for baseAttr in ["dpNetwork", "dpGuideNet", "rawGuide"]:
            cmds.addAttr(self.guideNet, longName=baseAttr, attributeType="bool")
            cmds.setAttr(self.guideNet+"."+baseAttr, 1)
        cmds.addAttr(self.guideNet, longName="moduleType", dataType="string")
        cmds.addAttr(self.guideNet, longName="guideNumber", dataType="string")
        cmds.addAttr(self.guideNet, longName="beforeData", dataType="string")
        cmds.addAttr(self.guideNet, longName="afterData", dataType="string")
        cmds.addAttr(self.guideNet, longName="linkedNode", attributeType="message")
        cmds.setAttr(self.guideNet+".moduleType", self.guideModuleName, type="string")
        cmds.setAttr(self.guideNet+".guideNumber", guideNumber, type="string")
        cmds.addAttr(self.moduleGrp, longName="net", attributeType="message")
        cmds.lockNode(self.guideNet, lock=False)
        cmds.connectAttr(self.guideNet+".message", self.moduleGrp+".net", force=True)
        cmds.connectAttr(self.moduleGrp+".message", self.guideNet+".linkedNode", force=True)
        self.addNodeToGuideNet([self.moduleGrp, self.radiusCtrl, self.annotation], ["moduleGrp", "radiusCtrl", "annotation"])

    
    def addNodeToGuideNet(self, nodeList, messageAttrList, *args):
        """ Include the given node list to the respective given attribute list as message connection in the network.
        """
        for node, messageAttr in zip(nodeList, messageAttrList):
            if not cmds.objExists(self.guideNet+"."+messageAttr):
                cmds.addAttr(self.guideNet, longName=messageAttr, attributeType="message")
            cmds.connectAttr(node+".message", self.guideNet+"."+messageAttr, force=True)
            self.addAttrToBeforeData(messageAttr)


    def removeAttrFromGuideNet(self, attrList, *args):
        """ Remove the given attribute list from the network node.
        """
        for attr in attrList:
            cmds.deleteAttr(self.guideNet+"."+attr)
            beforeList = self.getBeforeList()
            if attr in beforeList:
                beforeList.remove(attr)
                self.setBeforeList(beforeList)
    

    def addAttrToBeforeData(self, attr, *args):
        """ Just read the current before attribute string, add the new give attribute to it and set the guide network attibute with this new info.
            Returns the updated before data string.
        """
        beforeString = cmds.getAttr(self.guideNet+".beforeData") or ""
        beforeString = beforeString + attr + ";"
        cmds.setAttr(self.guideNet+".beforeData", beforeString, type="string")
        return beforeString


    def getBeforeList(self, *args):
        """ Just return a list with the splited items from the guide network beforeData string attribute.
        """
        beforeString = cmds.getAttr(self.guideNet+".beforeData")
        if beforeString:
            return list(filter(None, beforeString.split(";")))


    def setBeforeList(self, bList, *args):
        """ Receives a list and set it as beforeData string attribute in the guide network.
        """
        cmds.setAttr(self.guideNet+".beforeData", (";").join(bList)+";", type="string")


    def getNodeData(self, node, *args):
        """ Get and return all transformation data for the transform, also the userDefined attributes and them values.
            Returns a dictionary with this info.
        """
        attrList = cmds.listAttr(node, keyable=True)
        userDefinedAttrList = cmds.listAttr(node, unlocked=True, userDefined=True)
        if attrList:
            attrDic = {}
            fatherList = cmds.listRelatives(node, parent=True)
            if fatherList:
                attrDic["FatherNode"] = fatherList[0]
                if cmds.objExists(node+".guideBase") and cmds.getAttr(node+".guideBase") == 1:
                    if not "__" in fatherList[0]: #not a rawGuide
                        if cmds.objExists(fatherList[0]+".guideSource"):
                            attrDic["FatherNode"] = cmds.getAttr(fatherList[0]+".guideSource")
                    cmds.parent(node, world=True) #to export guide base transformation in worldSpace
            else:
                attrDic["FatherNode"] = None
            if userDefinedAttrList:
                attrList.extend(userDefinedAttrList)
            attrList = list(set(attrList))
            attrList.sort()
            for attr in attrList:
                if cmds.getAttr(node+"."+attr, type=True) == "message":
                    attrConnectList = cmds.listConnections(node+"."+attr, source=True, destination=False)
                    if attrConnectList:
                        attrDic[attr] = attrConnectList[0]
                else:
                    attrDic[attr] = cmds.getAttr(node+"."+attr)
            if cmds.objExists(node+".guideBase") and cmds.getAttr(node+".guideBase") == 1:
                if fatherList:
                    cmds.parent(node, fatherList[0])
            return attrDic


    def serializeGuide(self, buildIt=True, *args):
        """ Work in the guide info to store it as a json dictionary in order to be able to rebuild it in the future.
        """
        if not self.serialized:
            afterDataDic, guideDic = {}, {}
            beforeList = self.getBeforeList()
            if beforeList:
                if buildIt:
                    self.raw = False
                    cmds.setAttr(self.guideNet+".rawGuide", 0)
                afterDataDic["GuideNumber"] = cmds.getAttr(self.guideNet+".guideNumber")
                afterDataDic["ModuleType"] = self.guideModuleName
                afterDataDic["RawGuide"] = self.raw
                afterDataDic["BeforeData"] = beforeList
                for beforeAttr in beforeList:
                    nodeName = cmds.listConnections(self.guideNet+"."+beforeAttr, source=True, destination=False) or None
                    if nodeName:
                        if cmds.objExists(nodeName[0]):
                            guideDic[nodeName[0]] = self.getNodeData(nodeName[0])
                            if buildIt:
                                cmds.deleteAttr(self.guideNet+"."+beforeAttr)
                afterDataDic["GuideData"] = guideDic
                cmds.setAttr(self.guideNet+".afterData", afterDataDic, type="string")
                if buildIt:
                    cmds.lockNode(self.guideNet, lock=True) #to avoid deleting this network node
                    self.serialized = True
        else: #update linked node to avoid cleanup this network if it's broken
            cmds.lockNode(self.guideNet, lock=False)
            cmds.connectAttr(self.toStaticHookGrp+".message", self.guideNet+".linkedNode", force=True)
            cmds.addAttr(self.toStaticHookGrp, longName="net", attributeType="message")
            cmds.connectAttr(self.guideNet+".message", self.toStaticHookGrp+".net", force=True)
            cmds.lockNode(self.guideNet, lock=True)
    

    def renameUnitConversion(self, unitConversionList=None, *args):
        """ Rename just the new unitConverson created after the beginning of the module building.
        """
        if not unitConversionList:
            unitConversionList = cmds.ls(selection=False, type="unitConversion")
        if unitConversionList:
            if self.oldUnitConversionList:
                unitConversionList = list(set(unitConversionList)-set(self.oldUnitConversionList))
            if unitConversionList:
                self.utils.nodeRenamingTreatment(unitConversionList)


    def createWorldSize(self, *args):
        """ Create a null transform and use it as worldSize reference setup to scale the moduleGrp by offsetTransformMatrix.
        """
        cmds.namespace(set=self.guideNamespace, force=True)
        wsRef = cmds.createNode("transform", name="Guide_Base_WorldSize_Ref")
        cmds.namespace(set=":")
        for attr in ["X", "Y", "Z"]:
            cmds.connectAttr(self.moduleGrp+".worldSize", wsRef+".scale"+attr)
        cmds.connectAttr(wsRef+".worldMatrix[0]", self.moduleGrp+".offsetParentMatrix", force=True)
        cmds.setAttr(wsRef+".visibility", False)
        cmds.setAttr(wsRef+".template", 1)
        cmds.parent(wsRef, self.dpUIinst.tempGrp)


    # Getters:
    #
    def getArticulation(self, *args):
        return cmds.getAttr(self.moduleGrp+".articulation")

    def getModuleAttr(self, moduleAttr, *args):
        return cmds.getAttr(self.moduleGrp+"."+moduleAttr)
    
    def getJointsVisibility(self, *args):
        try:
            return cmds.checkBox('displayJointsCB', query=True, value=True)
        except:
            return 1

    
    # Setters:
    #
    def setArticulation(self, value, *args):
        self.addArticJoint = value
        cmds.setAttr(self.moduleGrp+".articulation", value)
    
    def setCorrective(self, value, *args):
        self.addCorrective = value
        cmds.setAttr(self.moduleGrp+".corrective", value)
