# importing libraries:
from maya import cmds
from maya import mel
from ..tool import correction_manager
from importlib import reload


DP_BASESTANDARD_VERSION = 2.13


class BaseStandard(object):
    def __init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI, *args):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.ar = ar
        self.name = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        #self.icon = ICON
        self.wiki = WIKI
        
        self.get_namespace_for_it()
        # WIP TODO: redefine them here?
        #
        


        # utils
        self.utils = ar.utils
        if self.ar.dev:
            reload(correction_manager)
        # starting correctionManager:
        self.correctionManager = correction_manager.CorrectionManager(self.ar)
        self.correctionManager.ui = False
        self.raw = True
        self.serialized = False
        self.sideList = [""]
        self.axisList = ["X", "Y", "Z"]
        self.guideNet = None
        

    def get_namespace_for_it(self, userGuideName=None):
        self.userGuideName = userGuideName
        if not self.userGuideName:
            self.userGuideName = self.ar.data.base_name+str(self.ar.utils.findLastNumber())
        self.rigType = "biped"
        # defining namespace:
        self.guideNamespace = self.name+"__"+self.userGuideName
        # defining guideNamespace:
        cmds.namespace(setNamespace=":")
        self.namespaceExists = cmds.namespace(exists=self.guideNamespace)
        self.guideName = self.guideNamespace+":Guide"
        self.guide_base = self.guideName+"_Base"
        self.radiusCtrl = self.guide_base+"_RadiusCtrl"
        self.annotation = self.guide_base+"_Ant"


    def build_raw_guide(self, userGuideName=None, *args):
        #
        #
        #self.number = number
        #
        # WIP TODO: get new userGuideName by findLastNumber in utils
        #

        self.get_namespace_for_it(userGuideName)
        # starting module:
        if not self.namespaceExists:
            cmds.namespace(add=self.guideNamespace)
            # create GUIDE for this module:
            self.createGuide()
        
        self.load_raw_guide()
        return self.guide_base
    

    def load_raw_guide(self, userGuideName=None):
        if userGuideName:
            self.userGuideName = userGuideName
        if self.ar.data.ui_state:
            # create the Module layout in the mainUI - modulesLayoutA:        
            self.createModuleLayout()
        # update module instance info:
        self.updateModuleInstanceInfo()
        self.guideNet = self.utils.getNodeByMessage("net", self.guide_base)
        if self.guideNet:
            self.raw = cmds.getAttr(self.guideNet+".rawGuide")


    
    def createModuleLayout(self, *args):
        """ Create the Module Layout, so it will exists in the right as a new options to editModules.
        """
        # MODULE LAYOUT:
#        print("self.guide_base = ", self.guide_base)
        layoutName = ""
        if "customName" in cmds.listAttr(self.guide_base):
            layoutName = cmds.getAttr(self.guide_base+".customName")
        if not layoutName:
            layoutName = self.userGuideName
        self.moduleLayoutName = self.ar.data.lang[self.title]+" - "+layoutName
        if cmds.columnLayout("rig_guides_inst_cl", query=True, exists=True):
            self.moduleFrameLayout = cmds.frameLayout(self.moduleLayoutName , label=self.moduleLayoutName, collapsable=True, collapse=False, parent="rig_guides_inst_cl")
            self.topColumn = cmds.columnLayout(self.moduleLayoutName+"_TopColumn", adjustableColumn=True, parent=self.moduleFrameLayout)
        # rig_guides_inst_cl -> here we have just the column layouts to be populated by modules.
    
    
    def createGuide(self, *args):
        """ Create the elements to Guide module in the scene, like controls, etc...
        """
        # GUIDE:
        self.ar.opt.check_use_default_render_layer()
        # create guide base (main):
        guideBaseList = self.ar.ctrls.cvBaseGuide(self.guide_base, r=2)
        self.guide_base = guideBaseList[0]
        self.radiusCtrl = guideBaseList[1]
        # add attributes to be read when rigging module:
        baseBooleanAttrList = ['guideBase', 'mirrorEnable', 'displayAnnotation']
        for baseBooleanAttr in baseBooleanAttrList:
            cmds.addAttr(self.guide_base, longName=baseBooleanAttr, attributeType='bool')
            cmds.setAttr(self.guide_base+"."+baseBooleanAttr, 1)
        
        baseStringAttrList  = ['moduleType', 'moduleNamespace', 'customName', 'mirrorAxis', 'mirrorName', 'mirrorNameList', 'hookNode', 'moduleInstanceInfo', 'guideObjectInfo', 'rigType', 'dpARVersion']
        for baseStringAttr in baseStringAttrList:
            cmds.addAttr(self.guide_base, longName=baseStringAttr, dataType='string')
        cmds.setAttr(self.guide_base+".moduleType", self.name, type='string')
        cmds.setAttr(self.guide_base+".moduleNamespace", self.guide_base[:self.guide_base.rfind(":")], type='string')
        cmds.setAttr(self.guide_base+".mirrorAxis", "off", type='string')
        cmds.setAttr(self.guide_base+".mirrorName", self.ar.data.lang['p002_left']+' --> '+self.ar.data.lang['p003_right'], type='string')
        cmds.setAttr(self.guide_base+".hookNode", "_Grp", type='string')
        cmds.setAttr(self.guide_base+".moduleInstanceInfo", self, type='string')

        cmds.setAttr(self.guide_base+".guideObjectInfo", self.ar.config.get_instance(self.name, [self.ar.data.standard_folder], "imported"), type='string')
        cmds.setAttr(self.guide_base+".rigType", self.rigType, type='string')
        cmds.setAttr(self.guide_base+".dpARVersion", self.ar.data.version, type='string')
        
        baseFloatAttrList = ['shapeSize', 'worldSize']
        for baseFloatAttr in baseFloatAttrList:
            cmds.addAttr(self.guide_base, longName=baseFloatAttr, attributeType='float', defaultValue=1)
            cmds.setAttr(self.guide_base+"."+baseFloatAttr, keyable=True)

        baseIntegerAttrList = ['degree']
        for baseIntAttr in baseIntegerAttrList:
            cmds.addAttr(self.guide_base, longName=baseIntAttr, attributeType='short')
        cmds.setAttr(self.guide_base+".degree", self.ar.data.degree_option)
        
        baseIntegerAttrList = ['guideColorIndex']
        for baseIntegerAttr in baseIntegerAttrList:
            cmds.addAttr(self.guide_base, longName=baseIntegerAttr, attributeType='long')
        for c, guideColorAttr in enumerate(['guideColorR', 'guideColorG', 'guideColorB']):
            cmds.addAttr(self.guide_base, longName=guideColorAttr, attributeType='float')
            cmds.setAttr(self.guide_base+"."+guideColorAttr, self.ar.ctrls.colorList[0][c])

        # create annotation to this module:
        self.annotation = cmds.annotate(self.guide_base, tx=self.guide_base, point=(0,2,0))
        self.annotation = cmds.listRelatives(self.annotation, parent=True)[0]
        self.annotation = cmds.rename(self.annotation, self.guide_base+"_Ant")
        cmds.parent(self.annotation, self.guide_base)
        cmds.setAttr(self.annotation+'.text', self.guide_base[self.guide_base.find("__")+2:self.guide_base.rfind(":")], type='string')
        cmds.setAttr(self.annotation+'.template', 1)
        cmds.connectAttr(self.guide_base+"_RadiusCtrl.translateX", self.annotation+".translateY", force=True)
        # setup worldSize
        self.ar.ctrls.getDPARTempGrp()
        self.createWorldSize()
        # prepare guide to serialization
        self.createGuideNetwork()
        self.ar.data.guide_instances.append(self)
        if self.ar.data.ui_state:
            self.ar.ui_manager.update_guide_footer()
    
    
    def updateModuleInstanceInfo(self, *args):
        """ Just update modeuleInstanceInfo attribute in the guideNode transform.
        """
        cmds.setAttr(self.guide_base+".moduleInstanceInfo", self, type='string')
    
    
    def verifyGuideModuleIntegrity(self, *args):
        """ This function verify the integrity of the current module.
            Returns True if Ok and False if Fail.
        """
        # conditionals to be elegible as a rigged guide module:
        if cmds.objExists(self.guide_base):
            if 'guideBase' in cmds.listAttr(self.guide_base):
                if cmds.getAttr(self.guide_base+'.guideBase') == 1:
                    return True
                else:
                    try:
                        self.deleteModule()
                        mel.eval('warning \"'+ self.ar.data.lang['e000_guideNotFound'] +' - '+ self.guide_base +'\";')
                    except:
                        pass
                    return False
    
    
    def deleteModule(self, *args):
        """ Delete the Guide, ModuleLayout and Namespace.
        """
        for item in [self.guide_base[:self.guide_base.find(":")]+"_MirrorGrp",
                     self.guide_base+"_WorldSize_Ref"]:
            if cmds.objExists(item):
                cmds.delete(item)
        # delete the guide module:
        self.utils.clearNodeGrp(self.guide_base, 'guideBase', unparent=True)
        # remove the namespaces:
        allNamespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        if self.guideNamespace in allNamespaceList:
            cmds.namespace(moveNamespace=(self.guideNamespace, ':'), force=True)
            cmds.namespace(removeNamespace=self.guideNamespace, force=True)
        if not self.ar.data.rebuilding:
            self.ar.ui_manager.refresh_ui(clearSel=True)
    

    def duplicateModule(self, *args):
        """ This module will just do a simple duplicate from Maya because we have a scriptJob to do the creating a new instance setup.
        """
        cmds.duplicate(self.guide_base)

    
    def editGuideModuleName(self, checkText=None, pad=1, *args):
        """ Edit the userGuideName to use the user custom name from module UI.
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
                cmds.setAttr(self.guide_base+".customName", "", type='string')
                self.userGuideName = self.guideNamespace.split("__")[-1]
            else:
                baseName = self.customName
                suffixNumberList = self.utils.getSuffixNumberList(self.customName)
                if suffixNumberList[1]:
                    baseName = suffixNumberList[1]
                dpAR_nameList = []
                nets = self.ar.utils.getNetworkNodeByAttr("dpGuideNet")
                for net in nets:
                    if baseName == self.utils.getSuffixNumberList(cmds.getAttr(net+".guideName"))[1]:
                        dpAR_nameList.append(cmds.getAttr(net+".guideName"))
                if dpAR_nameList:
                    if self.customName in dpAR_nameList:
                        for n in range(1, len(dpAR_nameList)+2):
                            if not baseName+str(n).zfill(pad) in dpAR_nameList:
                                self.customName = baseName+str(n).zfill(pad)
                                break
                # edit the prefixTextField with the normalText:
                try:
                    cmds.textField(self.userName, edit=True, text=self.customName)
                    cmds.frameLayout(self.moduleFrameLayout, edit=True, label=self.ar.data.lang[self.title]+" - "+self.customName)
                except:
                    pass
                cmds.setAttr(self.guide_base+".customName", self.customName, type='string')
                cmds.setAttr(self.annotation+".text", self.customName, type='string')
                if self.guideNet:
                    cmds.setAttr(self.guideNet+".guideName", self.customName, type='string')
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
        if not cmds.objExists(ctrl+"."+self.ar.data.lang['c124_corrective']):
            cmds.addAttr(ctrl, longName=self.ar.data.lang['c124_corrective'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
        # corrective network node
        correctiveNet = self.correctionManager.createCorrectionManager([firstNode, secondNode], name=netName, correctType=self.correctionManager.angleName, toRivet=False, fromUI=False)
        cmds.connectAttr(ctrl+"."+self.ar.data.lang['c124_corrective'], correctiveNet+".corrective", force=True)
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
            mirrorPrefixList = [self.ar.data.lang['p002_left'], self.ar.data.lang['p003_right']]
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
                    jcrCtrl, jcrGrp = self.ar.ctrls.createCorrectiveJointCtrl(jcrList[i], correctiveNetList[i], radius=self.ctrlRadius*0.2)
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
        self.ar.opt.check_use_default_render_layer()
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
        cmds.setAttr(self.guide_base+".nMain", self.nMainCtrlAttr)


    def changeStyle(self, style, *args):
        """ Change the style to be applyed custom actions to be more animator friendly.
            We will optimise: control world orientation
        """
        if style == self.ar.data.lang['m042_default'] or style == 0:
            cmds.setAttr(self.guide_base+".style", 0)
        elif style == self.ar.data.lang['m026_biped'] or style == 1:
            cmds.setAttr(self.guide_base+".style", 1)
        elif style == self.ar.data.lang['m037_quadruped'] or style == 2:
            cmds.setAttr(self.guide_base+".style", 2)


    def enableMainCtrls(self, value, *args):
        """ Just enable or disable the main controllers int field UI.
        """
        cmds.intField(self.nMainCtrlIF, edit=True, editable=value)
        cmds.checkBox(self.mainCtrlsCB, edit=True, editable=True)


    def setAddMainCtrls(self, value, *args):
        """ Just store the main controllers checkBox value and enable the int field.
        """
        cmds.setAttr(self.guide_base+".mainControls", value)
        self.enableMainCtrls(value)


    def addFkMainCtrls(self, side, ctrlList, *args):
        """ Implement the fk main controllers.
        """
        mainCtrlList = []
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
                    mainCtrl = self.ar.ctrls.cvControl("id_096_FkLineMain", side+self.userGuideName+"_%02d_Main_Fk_Ctrl"%(n), r=self.ctrlRadius*1.2, d=self.curveDegree, guideSource=self.guideName+"_Base", parentTag=self.getParentToTag(mainCtrlList))
                    mainCtrlList.append(mainCtrl)
                    self.ar.ctrls.colorShape([mainCtrl], "cyan")
                    cmds.addAttr(mainCtrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                    # position
                    cmds.parent(mainCtrl, currentCtrlZero)
                    cmds.makeIdentity(mainCtrl, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(currentCtrl, mainCtrl)
                    # intensity utilities
                    rIntensityMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_R_Main_MD")
                    self.to_ids.append(rIntensityMD)
                    for axis in self.axisList:
                        cmds.connectAttr(mainCtrl+".rotate"+axis, rIntensityMD+".input1"+axis, force=True)
                        cmds.connectAttr(mainCtrl+"."+self.ar.data.lang['c049_intensity'], rIntensityMD+".input2"+axis, force=True)
                else:
                    # offseting sub controllers
                    offsetGrp = cmds.group(name=currentCtrl+"_Offset_Grp", empty=True)
                    cmds.parent(offsetGrp, currentCtrlZero)
                    cmds.makeIdentity(offsetGrp, apply=False, translate=True, rotate=True, scale=True)
                    cmds.parent(currentCtrl, offsetGrp)
                    for axis in self.axisList:
                        cmds.connectAttr(rIntensityMD+".output"+axis, offsetGrp+".rotate"+axis, force=True)
                # display sub controllers shapes
                self.ar.ctrls.setSubControlDisplay(mainCtrl, currentCtrl, 0)
    

    def getMirrorSideList(self, *args):
        """ Processes the mirror information for the current guide.
        Defines self.sideList to be used by the module.
        """
        # analisys the mirror module:
        self.mirrorAxis = cmds.getAttr(self.guide_base+".mirrorAxis")
        if self.mirrorAxis != 'off':
            # get rigs names:
            self.mirrorNames = cmds.getAttr(self.guide_base+".mirrorName")
            # get first and last letters to use as side initials (prefix):
            self.sideList = [self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_']
            for s, side in enumerate(self.sideList):
                duplicated = cmds.duplicate(self.guide_base, name=side+self.userGuideName+'_Guide_Base')[0]
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
                    if cmds.objExists(self.guide_base+".flip"):
                        if cmds.getAttr(self.guide_base+".flip") == 0:
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
            duplicated = cmds.duplicate(self.guide_base, name=self.userGuideName+'_Guide_Base')[0]
            allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
            for item in allGuideList:
                cmds.rename(item, self.userGuideName+"_"+item)
            self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
            # re-rename grp:
            cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # joint labelling:
            self.jointLabelAdd = 0
        # store the number of this guide by module type
        self.dpAR_count = self.utils.findModuleLastNumber(self.name, "moduleType", True)


    def rig_me(self, *args):
        """ The fun part of the module, just read the values from editModuleLayout and create the rig for this guide.
        """
        self.ar.utils.closeUI(self.ar.data.plus_info_win_name)
        self.ar.utils.closeUI(self.ar.data.color_override_win_name)
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            self.to_ids = []
            self.oldUnitConversionList = cmds.ls(selection=False, type="unitConversion")
            try:
                # clear selected module layout:
                self.clearSelectedModuleLayout()
            except:
                pass

            # unPinGuides before Rig them:
            self.ar.job.unpin_guide([self.guide_base], force=True)
            
            # RIG:
            self.ar.opt.check_use_default_render_layer()
            
            # get the radius value to controls:
            if cmds.objExists(self.radiusCtrl):
                self.ctrlRadius = self.utils.getCtrlRadius(self.radiusCtrl)
            else:
                self.ctrlRadius = 1
                
            # get curve degree:
            self.curveDegree = cmds.getAttr(self.guide_base+".degree")
            
            # unparent all guide modules child:
            childrenList = cmds.listRelatives(self.guide_base, allDescendents=True, type='transform')
            if childrenList:
                for child in childrenList:
                    if "guideBase" in cmds.listAttr(child) and cmds.getAttr(child+".guideBase") == 1:
                        cmds.parent(child, world=True)
            
            # just edit customName and prefix:
            if self.customName != "" and self.customName != " " and self.customName != "_" and self.customName != None:
                names = [n for n in cmds.ls(selection=False, type="transform") if "dpAR_name" in cmds.listAttr(n)]
                for item in names:
                   if self.customName == cmds.getAttr(item+".dpAR_name"):
                       self.customName = self.customName + "1"
                self.userGuideName = self.customName

            if self.ar.data.prefix:
                self.userGuideName = self.ar.data.prefix + self.userGuideName
            cmds.select(clear=True)
            self.getMirrorSideList()
    

    def hookSetup(self, side, ctrlList, scalableList=None, staticList=None, *args):
        """ Generate the hook setup to find lists of controllers, scalable and static groups.
            Add message attributes to map hooked groups for the rigged module.
        """
        # create a masterModuleGrp to be checked if this rig exists:
        self.toCtrlHookGrp     = cmds.group(ctrlList, name=side+self.userGuideName+"_Control_Grp")
        self.toScalableHookGrp = cmds.group(empty=True, name=side+self.userGuideName+"_Scalable_Grp")
        self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Static_Grp")
        if staticList:
            cmds.parent(staticList, self.toStaticHookGrp)
        if scalableList:
            cmds.parent(scalableList, self.toScalableHookGrp)
        self.ar.custom_attr.addAttr(0, [self.toCtrlHookGrp, self.toScalableHookGrp, self.toStaticHookGrp]) #dpID
        # add hook attributes to be read when rigging composed modules:
        self.utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
        self.utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
        self.utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
        cmds.lockNode(self.guideNet, lock=False)
        # add module type counter value
        if not 'dpAR_count' in cmds.listAttr(self.guideNet):
            cmds.addAttr(self.guideNet, longName='dpAR_count', attributeType='long', keyable=False)
            cmds.setAttr(self.guideNet+'.dpAR_count', self.dpAR_count)
        # message attributes
        cmds.addAttr(self.guideNet, longName=side+"ControlHookGrp", attributeType="message")
        cmds.addAttr(self.guideNet, longName=side+"StaticHookGrp", attributeType="message")
        cmds.addAttr(self.guideNet, longName=side+"ScalableHookGrp", attributeType="message")
        cmds.connectAttr(self.toCtrlHookGrp+".message", self.guideNet+"."+side+"ControlHookGrp", force=True)
        cmds.connectAttr(self.toScalableHookGrp+".message", self.guideNet+"."+side+"ScalableHookGrp", force=True)
        cmds.connectAttr(self.toStaticHookGrp+".message", self.guideNet+"."+side+"StaticHookGrp", force=True)
        cmds.setAttr(self.toScalableHookGrp+".visibility", self.getJointsVisibility())
        cmds.setAttr(self.toStaticHookGrp+".visibility", self.getJointsVisibility())
        cmds.lockNode(self.guideNet, lock=True)

    
    def composingInfo(self, *args):
        """ This method just create this dictionary in order to build information of module integration.
        """
        self.composed = {}
    

    def createGuideNetwork(self, number=None, *args):
        """ Create a network for the current guide and store on it the nodes used in this module by message.
        """
        if number:
            guideNumber = number
        else:
            guideNumber = self.utils.findLastNumber()
        self.guideNet = cmds.createNode("network", name="dpGuide_"+guideNumber+"_Net")
        self.dpID = self.ar.custom_attr.addAttr(0, [self.guideNet])[0] #dpID
        for baseAttr in ["dpNetwork", "dpGuideNet", "rawGuide"]:
            cmds.addAttr(self.guideNet, longName=baseAttr, attributeType="bool")
            cmds.setAttr(self.guideNet+"."+baseAttr, 1)
        cmds.addAttr(self.guideNet, longName="moduleType", dataType="string")
        cmds.addAttr(self.guideNet, longName="guideName", dataType="string")
        cmds.addAttr(self.guideNet, longName="guideNumber", dataType="string")
        cmds.addAttr(self.guideNet, longName="beforeData", dataType="string")
        cmds.addAttr(self.guideNet, longName="afterData", dataType="string")
        cmds.addAttr(self.guideNet, longName="linkedNode", attributeType="message")
        cmds.setAttr(self.guideNet+".moduleType", self.name, type="string")
        cmds.setAttr(self.guideNet+".guideName", self.userGuideName, type="string")
        cmds.setAttr(self.guideNet+".guideNumber", guideNumber, type="string")
        if not "net" in cmds.listAttr(self.guide_base):
            cmds.addAttr(self.guide_base, longName="net", attributeType="message")
        cmds.lockNode(self.guideNet, lock=False)
        cmds.connectAttr(self.guideNet+".message", self.guide_base+".net", force=True)
        cmds.connectAttr(self.guide_base+".message", self.guideNet+".linkedNode", force=True)
        self.addNodeToGuideNet([self.guide_base, self.radiusCtrl, self.annotation], ["main", "radiusCtrl", "annotation"])

    
    def addNodeToGuideNet(self, nodeList, messageAttrList, *args):
        """ Include the given node list to the respective given attribute list as message connection in the network.
        """
        for node, messageAttr in zip(nodeList, messageAttrList):
            if not cmds.objExists(self.guideNet+"."+messageAttr):
                self.lockNodeStatus = cmds.lockNode(self.guideNet, query=True, lock=True)[0]
                cmds.lockNode(self.guideNet, lock=False)
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
        if self.lockNodeStatus:
            cmds.lockNode(self.guideNet, lock=True)
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
            if "guideBase" in cmds.listAttr(node) and cmds.getAttr(node+".guideBase") == 1:
                if fatherList:
                    cmds.parent(node, fatherList[0])
            return attrDic


    def serialize_guide(self, buildIt=True, *args):
        """ Work in the guide info to store it as a json dictionary in order to be able to rebuild it in the future.
        """
        self.ar.job.unpin_guide(force=True)
        if cmds.objExists(self.guide_base):
            self.customName = cmds.getAttr(self.guide_base+".customName") or ""
        if not self.serialized:
            afterDataDic, guideDic = {}, {}
            beforeList = self.getBeforeList()
            if beforeList:
                if buildIt:
                    self.raw = False
                    cmds.setAttr(self.guideNet+".rawGuide", 0)
                afterDataDic["GuideNumber"] = cmds.getAttr(self.guideNet+".guideNumber")
                afterDataDic["ModuleType"] = self.name
                afterDataDic["RawGuide"] = self.raw
                afterDataDic["BeforeData"] = beforeList
                for beforeAttr in beforeList:
                    nodeName = cmds.listConnections(self.guideNet+"."+beforeAttr, source=True, destination=False) or None
                    if nodeName:
                        if cmds.objExists(nodeName[0]):
                            guideDic[nodeName[0]] = self.getNodeData(nodeName[0])
                            if buildIt:
                                cmds.lockNode(self.guideNet, lock=False)
                                cmds.deleteAttr(self.guideNet+"."+beforeAttr)
                                cmds.lockNode(self.guideNet, lock=True)
                afterDataDic["GuideData"] = guideDic
                cmds.setAttr(self.guideNet+".afterData", afterDataDic, type="string")
                if buildIt:
                    cmds.lockNode(self.guideNet, lock=True) #to avoid deleting this network node
                    self.serialized = True
        else: #update linked node to avoid cleanup this network if it's broken
            cmds.lockNode(self.guideNet, lock=False)
            optionCtrl = self.utils.getNodeByMessage("optionCtrl")
            if optionCtrl:
                cmds.connectAttr(optionCtrl+".message", self.guideNet+".linkedNode", force=True)
            else:
                cmds.connectAttr(self.toStaticHookGrp+".message", self.guideNet+".linkedNode", force=True)
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
        """ Create a null transform and use it as worldSize reference setup to scale the main by offsetTransformMatrix.
        """
        self.wsRef = cmds.createNode("transform", name=self.guideNamespace+":Guide_Base_WorldSize_Ref")
        for attr in ["X", "Y", "Z"]:
            cmds.connectAttr(self.guide_base+".worldSize", self.wsRef+".scale"+attr)
        cmds.connectAttr(self.wsRef+".worldMatrix[0]", self.guide_base+".offsetParentMatrix", force=True)
        cmds.setAttr(self.wsRef+".visibility", False)
        cmds.setAttr(self.wsRef+".template", 1)
        cmds.parent(self.wsRef, self.ar.data.temp_grp)


    def getParentToTag(self, itemList, returnItem=None, *args):
        """ Return the latest item from given list or the second given param.
        """
        if itemList:
            return itemList[-1]
        return returnItem


    # Getters:
    #
    def getArticulation(self, *args):
        return cmds.getAttr(self.guide_base+".articulation")

    def getModuleAttr(self, moduleAttr, *args):
        return cmds.getAttr(self.guide_base+"."+moduleAttr)
    
    def getJointsVisibility(self, *args):
        try:
            return cmds.checkBox('displayJointsCB', query=True, value=True)
        except:
            return 1

    
    # Setters:
    #
    def setArticulation(self, value, *args):
        self.addArticJoint = value
        cmds.setAttr(self.guide_base+".articulation", value)
    
    def setCorrective(self, value, *args):
        self.addCorrective = value
        cmds.setAttr(self.guide_base+".corrective", value)
