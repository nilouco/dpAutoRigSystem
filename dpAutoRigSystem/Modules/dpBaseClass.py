# importing libraries:
from maya import cmds
from maya import mel
from .Library import dpControls
from ..Extras import dpCorrectionManager
import json

class RigType(object):
    biped = "biped"
    quadruped = "quadruped"
    default = "unknown" #Support old guide system

DP_STARTCLASS_VERSION = 2.3


class StartClass(object):
    def __init__(self, dpUIinst, userGuideName, rigType, CLASS_NAME, TITLE, DESCRIPTION, ICON, *args):
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
        self.guideNamespace = self.guideModuleName + "__" + self.userGuideName
        # defining guideNamespace:
        cmds.namespace(setNamespace=":")
        self.namespaceExists = cmds.namespace(exists=self.guideNamespace)
        self.guideName = self.guideNamespace + ":Guide"
        self.moduleGrp = self.guideName+"_Base"
        self.radiusCtrl = self.moduleGrp+"_RadiusCtrl"
        self.annotation = self.moduleGrp+"_Ant"
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
    
    
    def createModuleLayout(self, *args):
        """ Create the Module Layout, so it will exists in the right as a new options to editModules.
        """
        # MODULE LAYOUT:
        self.moduleLayout = self.dpUIinst.lang[self.title]+" - "+self.userGuideName
        self.moduleFrameLayout = cmds.frameLayout(self.moduleLayout , label=self.moduleLayout, collapsable=True, collapse=False, parent="modulesLayoutA")
        self.topColumn = cmds.columnLayout(self.moduleLayout+"_TopColumn", adjustableColumn=True, parent=self.moduleFrameLayout)
        # here we have just the column layouts to be populated by modules.
    
    
    def createGuide(self, raw=True, *args):
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
        
        baseIntegerAttrList = ['guideColor']
        for baseIntegerAttr in baseIntegerAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseIntegerAttr, attributeType='long')
        
        baseStringAttrList  = ['moduleNamespace', 'customName', 'mirrorAxis', 'mirrorName', 'mirrorNameList', 'hookNode', 'moduleInstanceInfo', 'guideObjectInfo', 'rigType', 'dpARVersion']
        for baseStringAttr in baseStringAttrList:
            cmds.addAttr(self.moduleGrp, longName=baseStringAttr, dataType='string')
        cmds.setAttr(self.moduleGrp+".mirrorAxis", "off", type='string')
        cmds.setAttr(self.moduleGrp+".mirrorName", self.dpUIinst.lang['p002_left']+' --> '+self.dpUIinst.lang['p003_right'], type='string')
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
        # prepare guide to serialization
        self.createGuideNetwork(raw)
    
    
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
        # delete the guide module:
        self.utils.clearNodeGrp(nodeGrpName=self.moduleGrp, attrFind='guideBase', unparent=True)
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
                    self.utils.setJointLabel(jcr, s+jointLabelAdd, 18, labelName+"_"+str(m))
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
        axisList = ['X', 'Y', 'Z']
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
                    for axis in axisList:
                        cmds.connectAttr(mainCtrl+".rotate"+axis, rIntensityMD+".input1"+axis, force=True)
                        cmds.connectAttr(mainCtrl+"."+self.dpUIinst.lang['c049_intensity'], rIntensityMD+".input2"+axis, force=True)
                else:
                    # offseting sub controllers
                    offsetGrp = cmds.group(name=currentCtrl+"_Offset_Grp", empty=True)
                    cmds.parent(offsetGrp, currentCtrlZero)
                    cmds.makeIdentity(offsetGrp, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(currentCtrl, offsetGrp)
                    for axis in axisList:
                        cmds.connectAttr(rIntensityMD+".output"+axis, offsetGrp+".rotate"+axis, force=True)
                # display sub controllers shapes
                self.ctrls.setSubControlDisplay(mainCtrl, currentCtrl, 0)
    

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
            
            # start serialization
            self.serializeGuide()

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
    

    def hookSetup(self, *args):
        """ Add message attributes to map hooked groups for the rigged module.
        """
        cmds.addAttr(self.toStaticHookGrp, longName="controlHookGrp", attributeType="message")
        cmds.addAttr(self.toStaticHookGrp, longName="scalableHookGrp", attributeType="message")
        cmds.connectAttr(self.toCtrlHookGrp+".message", self.toStaticHookGrp+".controlHookGrp", force=True)
        cmds.connectAttr(self.toScalableHookGrp+".message", self.toStaticHookGrp+".scalableHookGrp", force=True)

    
    def integratingInfo(self, *args):
        """ This method just create this dictionary in order to build information of module integration.
        """
        self.integratedActionsDic = {}
    

    def createGuideNetwork(self, raw=True, *args):
        """ Create a network for the current guide and store on it the nodes used in this module by message.
            Set it as locked node in order to keep it existing after generating the rig.
            Returns the network node useful to guide rebuilding.
        """
        if raw:
            self.guideNet = cmds.createNode("network", name=self.userGuideName+"_Guide_Net")
            for baseAttr in ["dpNetwork", "dpGuideNet", "rawGuide"]:
                cmds.addAttr(self.guideNet, longName=baseAttr, attributeType="bool")
                cmds.setAttr(self.guideNet+"."+baseAttr, 1)
            cmds.addAttr(self.guideNet, longName="beforeData", dataType="string")
            cmds.addAttr(self.guideNet, longName="afterData", dataType="string")
        else:
            cmds.lockNode(self.guideNet, lock=False)
        cmds.addAttr(self.moduleGrp, longName="net", attributeType="message")
        cmds.connectAttr(self.guideNet+".message", self.moduleGrp+".net", force=True)
        self.addNodeToGuideNet([self.moduleGrp, self.radiusCtrl, self.annotation], ["moduleGrp", "radiusCtrl", "annotation"], raw)
        return self.guideNet

    
    def addNodeToGuideNet(self, nodeList, messageAttrList, raw=True, *args):
        """ Include the given node list to the respective given attribute list as message connection in the network.
        """
        for node, messageAttr in zip(nodeList, messageAttrList):
            if not cmds.objExists(self.guideNet+"."+messageAttr):
                cmds.addAttr(self.guideNet, longName=messageAttr, attributeType="message")
            cmds.connectAttr(node+".message", self.guideNet+"."+messageAttr, force=True)
            self.updateBeforeData(messageAttr)


    def removeAttrFromGuideNet(self, attrList, *args):
        """ Remove the given attribute list from the network node.
        """
        for attr in attrList:
            cmds.deleteAttr(self.guideNet+"."+attr)
    

    def updateBeforeData(self, attr, *args):
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


    def getNodeData(self, node, *args):
        """ Get and return all transformation data for the transform, also the userDefined attributes and them values.
            Returns a dictionary with this info.
        """
        attrList = cmds.listAttr(node, keyable=True)
        userDefinedAttrList = cmds.listAttr(node, unlocked=True, userDefined=True)
        if attrList:
            if userDefinedAttrList:
                attrList.extend(userDefinedAttrList)
            attrList = list(set(attrList))
            attrList.sort()
            attrDic = {}
            for attr in attrList:
                if cmds.getAttr(node+"."+attr, type=True) == "message":
                    attrConnectList = cmds.listConnections(node+"."+attr, source=True, destination=False)
                    if attrConnectList:
                        attrDic[attr] = attrConnectList[0]
                else:
                    attrDic[attr] = cmds.getAttr(node+"."+attr)

            # get father?
            fatherList = cmds.listRelatives(node, parent=True)
            if fatherList:
                attrDic["fatherNode"] = fatherList[0]
            else:
                attrDic["fatherNode"] = None
            return attrDic


    def serializeGuide(self, *args):
        """ Work in the guide info to store it as a json dictionary in order to be able to rebuild it in the future.
        """
        afterDataDic = {}
        beforeList = self.getBeforeList()
        if beforeList:
            for beforeAttr in beforeList:
                nodeName = cmds.listConnections(self.guideNet+"."+beforeAttr, source=True, destination=False) or None
                if nodeName:
                    if cmds.objExists(nodeName[0]):
                        afterDataDic[nodeName[0]] = self.getNodeData(nodeName[0])
        cmds.setAttr(self.guideNet+".afterData", json.dumps(afterDataDic), type="string")
        cmds.setAttr(self.guideNet+".rawGuide", 0)
        cmds.lockNode(self.guideNet, lock=True) #to avoid deleting network node




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
