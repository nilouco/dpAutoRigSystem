#import libraries
import re
import time
import getpass
from maya import cmds



class Maker(object):
    def __init__(self, ar):
        self.ar = ar



    def create_raw_guide(self, module, *args):
        #
        # TODO: review after rename modules without dp
        #
        if not module.startswith("dp"):
            module = "dp"+module

        mod = self.ar.lib.initialize_library(module, self.ar.data.standard_folder)[0]
        return [mod, mod.build_raw_guide()]


    #
    # TODO: it isn't used yet.
    #

    def set_new_guide(self, module, name, t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1), size=1, radius=2, end=1.3, mirror=None, flip=1, deformed=0, indSkin=0, annot=1, annot_pos=None, parent=None, progress=True):
        """ Creates a new standard guide, set the given values and returns a list with the imported module and the created guide.
        """
        if progress:
            self.ar.utils.setProgress(self.ar.data.lang['m094_doing']+name)
            cmds.refresh()
        mod, guide = self.create_raw_guide(module)
        mod.editGuideModuleName(name)
        cmds.setAttr(mod.radiusCtrl+".translateX", radius)
        cmds.setAttr(mod.cvEndJoint+".translateZ", end)
        cmds.setAttr(guide+".translateX", t[0])
        cmds.setAttr(guide+".translateY", t[1])
        cmds.setAttr(guide+".translateZ", t[2])
        cmds.setAttr(guide+".rotateX", r[0])
        cmds.setAttr(guide+".rotateY", r[1])
        cmds.setAttr(guide+".rotateZ", r[2])
        cmds.setAttr(guide+".scaleX", s[0])
        cmds.setAttr(guide+".scaleY", s[1])
        cmds.setAttr(guide+".scaleZ", s[2])
        cmds.setAttr(guide+".shapeSize", size)
        if mirror:
            mod.changeMirror(mirror)
            cmds.setAttr(guide+".flip", flip)
        if deformed:
            cmds.setAttr(guide+".deformedBy", deformed)
        if indSkin:
            cmds.setAttr(guide+".indirectSkin", indSkin)
        cmds.setAttr(guide+".displayAnnotation", annot)
        cmds.setAttr(guide+"_Ant.visibility", annot)
        if annot_pos:
            cmds.setAttr(mod.annotation+".translateX", annot_pos[0])
            cmds.setAttr(mod.annotation+".translateY", annot_pos[1])
            cmds.setAttr(mod.annotation+".translateZ", annot_pos[2])
        else:
            cmds.setAttr(mod.annotation+".translateX", 0)
            cmds.setAttr(mod.annotation+".translateY", radius)
            cmds.setAttr(mod.annotation+".translateZ", 0)
        if parent:
            cmds.parent(guide, parent, absolute=True)
        return [mod, guide]


    def create_template(self, name=None, *args):
        self.ar.ui_manager.refresh_ui()
        nets = self.ar.utils.getNetworkNodeByAttr("dpGuideNet")
        nets.extend(self.ar.utils.getNetworkNodeByAttr("dpHeadDeformerNet") or [])
        if nets:
            self.ar.ctrls.unPinGuide(force=True)
            guide_io = self.ar.config.get_instance("dpGuideIO", [self.ar.data.setup_folder])
            guides_data = guide_io.getGuideDataDic(nets)
            if not name:
                if self.ar.data.ui_state:
                    if self.ar.data.ui_state:
                        name = self.ar.ui_manager.ask_prompt_dialog("Template", self.ar.data.lang["m006_name"]).lower()
            if name:
                # export json file
                self.ar.pipeliner.saveJsonFile(guides_data, f"{self.ar.data.dp_auto_rig_path}/{self.ar.data.template_folder.replace('.', '/')}/{name}.json")
                print(self.ar.data.lang["i133_presetCreated"], name)
                self.ar.ui_manager.reload_ui()
        else:
            print(self.ar.data.lang["e000_guideNotFound"])


    def setup_duplicated_guide(self, selectedItem, *args):
        """ This method will create a new module instance for a duplicated guide found.
            Returns a guideBase for a new module instance.
        """
        # Duplicating a module guide
        print(self.ar.data.lang['i067_duplicating'])
        self.ar.utils.setProgress("dpAutoRigSystem", self.ar.data.lang['i067_duplicating'], max=3, addOne=False, addNumber=False)
        # declaring variables
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
        moduleNamespaceValue = cmds.getAttr(selectedItem+"."+self.ar.data.module_namespace_attr)
        moduleInstanceInfoValue = cmds.getAttr(selectedItem+"."+self.ar.data.module_instance_info_attr)
        # generating naming values
        origGuideName = moduleNamespaceValue+":"+self.ar.data.guide_base_name
        thatClassName = moduleNamespaceValue.partition("__")[0]
        thatModuleName = moduleInstanceInfoValue[:moduleInstanceInfoValue.rfind(thatClassName)-1]
        thatModuleName = thatModuleName[thatModuleName.rfind(".")+1:]
        moduleDir = moduleInstanceInfoValue[:moduleInstanceInfoValue.rfind(thatModuleName)-1]
        moduleDir = moduleDir[moduleDir.find(".")+1:]
        self.ar.utils.setProgress(self.ar.data.lang['i067_duplicating'])
        # initializing a new module instance
        #newGuideInstance = eval('self.initGuide("'+thatModuleName+'")')#, "'+moduleDir+'")')
        #newGuideName = cmds.ls(selection=True)[0]

        newGuideInstance = self.ar.lib.initialize_library(thatModuleName, self.ar.data.standard_folder)[0]
        newGuideName = newGuideInstance.build_raw_guide()
#        print("newGuideInstance, newGuideName =", newGuideInstance, newGuideName)
        newGuideNamespace = cmds.getAttr(newGuideName+"."+self.ar.data.module_namespace_attr)
        
        # reset radius as original
        origRadius = cmds.getAttr(moduleNamespaceValue+":"+self.ar.data.guide_base_name+"_RadiusCtrl.translateX")
        cmds.setAttr(newGuideName+"_RadiusCtrl.translateX", origRadius)
        
        # getting a good attribute list
        toSetAttrList = cmds.listAttr(selectedItem)
        currentAttrList = toSetAttrList.copy()
        guideBaseAttrIdx = toSetAttrList.index(self.ar.data.guide_base_attr)
        toSetAttrList = toSetAttrList[guideBaseAttrIdx:]
        toSetAttrList.remove(self.ar.data.guide_base_attr)
        toSetAttrList.remove(self.ar.data.module_namespace_attr)
        toSetAttrList.remove(customNameAttr)
        toSetAttrList.remove(mirrorAxisAttr)
        # check for special attributes
        if nSegmentsAttr in currentAttrList:
            toSetAttrList.remove(nSegmentsAttr)
            nJointsValue = cmds.getAttr(selectedItem+'.'+nSegmentsAttr)
            if nJointsValue > 0:
                newGuideInstance.changeJointNumber(nJointsValue)
        self.ar.utils.setProgress(self.ar.data.lang['i067_duplicating'])
        if customNameAttr in currentAttrList:
            customNameValue = cmds.getAttr(selectedItem+'.'+customNameAttr)
            if customNameValue != "" and customNameValue != None:
                newGuideInstance.editGuideModuleName(customNameValue)
        self.ar.utils.setProgress(self.ar.data.lang['i067_duplicating'])
        if mirrorAxisAttr in currentAttrList:
            mirroirAxisValue = cmds.getAttr(selectedItem+'.'+mirrorAxisAttr)
            if mirroirAxisValue != "off":
                newGuideInstance.changeMirror(mirroirAxisValue)
        if dispAnnotAttr in currentAttrList:
            toSetAttrList.remove(dispAnnotAttr)
            currentDisplayAnnotValue = cmds.getAttr(selectedItem+'.'+dispAnnotAttr)
            newGuideInstance.displayAnnotation(currentDisplayAnnotValue)
        if netAttr in currentAttrList:
            toSetAttrList.remove(netAttr)
        
        # TODO: change to unify style and type attributes        
        if "type" in currentAttrList:
            typeValue = cmds.getAttr(selectedItem+'.type')
            newGuideInstance.changeType(typeValue)
        if "style" in currentAttrList:
            styleValue = cmds.getAttr(selectedItem+'.style')
            newGuideInstance.changeStyle(styleValue)
        
        # get and set transformations
        childrenList = cmds.listRelatives(selectedItem, children=True, allDescendents=True, fullPath=True, type="transform")
        if childrenList:
            for child in childrenList:
                if not "|Guide_Base|Guide_Base" in child:
                    newChild = newGuideNamespace+":"+child[child.rfind("|")+1:]
                    for transfAttr in self.ar.data.transform_attrs:
                        try:
                            isLocked = cmds.getAttr(child+"."+transfAttr, lock=True)
                            cmds.setAttr(newChild+"."+transfAttr, lock=False)
                            cmds.setAttr(newChild+"."+transfAttr, cmds.getAttr(child+"."+transfAttr))
                            if isLocked:
                                cmds.setAttr(newChild+"."+transfAttr, lock=True)
                        except:
                            pass
        
        # set transformation for Guide_Base
        for transfAttr in self.ar.data.transform_attrs:
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
        print(self.ar.data.lang['r006_wellDone']+" "+newGuideName)
        self.ar.utils.setProgress(endIt=True)
        return newGuideName
    

    def getBaseGrp(self, sAttrName, sGrpName, oldList=None):
        if not cmds.objExists(sGrpName):
            needCreateIt = True
            if oldList:
                if cmds.objExists(oldList[1]):
                    sAttrName = oldList[0]
                    sGrpName = oldList[1]
                    needCreateIt = False
            if needCreateIt:
                cmds.createNode("transform", name=sGrpName)
        if not sAttrName in cmds.listAttr(self.masterGrp):
            cmds.addAttr(self.masterGrp, longName=sAttrName, attributeType="message")
        if not cmds.listConnections(self.masterGrp+"."+sAttrName, destination=False, source=True):
            cmds.connectAttr(sGrpName+".message", self.masterGrp+"."+sAttrName, force=True)
        self.ar.customAttr.addAttr(0, [sGrpName]) #dpID
        return sGrpName
    

    def getBaseCtrl(self, sCtrlType, sAttrName, sCtrlName, fRadius, iDegree=1):
        nCtrl = sCtrlName
        self.ctrlCreated = False
        if not sAttrName in cmds.listAttr(self.masterGrp):
            cmds.addAttr(self.masterGrp, longName=sAttrName, attributeType="message")
        if not cmds.objExists(sCtrlName):
            if (sCtrlName != (self.ar.data.prefix+"Option_Ctrl")):
                nCtrl = self.ar.ctrls.cvControl(sCtrlType, sCtrlName, r=fRadius, d=iDegree, dir="+X")
            else:
                nCtrl = self.ar.ctrls.cvCharacter(sCtrlType, sCtrlName, r=(fRadius*0.2))
            cmds.setAttr(nCtrl+".rotateOrder", 3)
            cmds.connectAttr(sCtrlName+".message", self.masterGrp+"."+sAttrName, force=True)
            self.ctrlCreated = True
        return nCtrl
    

    def createBaseRigNode(self):
        localTime = str(time.asctime(time.localtime(time.time())))
        self.masterGrp = self.ar.utils.getAllGrp()
        if not self.masterGrp:
            if cmds.objExists(self.ar.data.master_name):
                # rename existing All_Grp node without connections as All_Grp_Old
                cmds.rename(self.ar.data.master_name, self.ar.data.master_name+"_Old")
            #Create Master Grp
            self.masterGrp = cmds.createNode("transform", name=self.ar.data.prefix+self.ar.data.master_name)
            self.ar.customAttr.addAttr(0, [self.masterGrp]) #dpID
            # adding All_Grp attributes
            cmds.addAttr(self.masterGrp, longName=self.ar.data.master_attr, attributeType="bool")
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
            cmds.setAttr(self.masterGrp+"."+self.ar.data.master_attr, True)
            cmds.setAttr(self.masterGrp+".dpAutoRigSystem", self.ar.data.github_url, type="string")
            cmds.setAttr(self.masterGrp+".date", localTime, type="string")
            cmds.setAttr(self.masterGrp+".maya", cmds.about(version=True), type="string")
            cmds.setAttr(self.masterGrp+".system", self.ar.data.version, type="string")
            cmds.setAttr(self.masterGrp+".language", self.ar.data.lang["_preset"], type="string")
            #
            # TODO WIP (self.presetName)
            #
            #cmds.setAttr(self.masterGrp+".preset", self.presetName, type="string")
            #
            #
            #
            cmds.setAttr(self.masterGrp+".preset", "WIP_PRESET_NAME_HERE", type="string")
            cmds.setAttr(self.masterGrp+".author", getpass.getuser(), type="string")
            cmds.setAttr(self.masterGrp+".prefix", self.ar.data.prefix, type="string")
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
            for guideType in self.ar.data.lib[self.ar.data.standard_folder]["modules"]:
                cmds.addAttr(self.masterGrp, longName=guideType+"Count", attributeType="long", defaultValue=0)
            # set outliner color
            self.ar.ctrls.colorShape([self.masterGrp], [1, 1, 1], outliner=True) #white

        # update data
        cmds.setAttr(self.masterGrp+".lastModification", localTime, type="string")
        # setting pipeline data
        if not cmds.objExists(self.masterGrp+".lastGuidesFile"):
            cmds.addAttr(self.masterGrp, longName="lastGuidesFile", dataType="string")
        cmds.setAttr(self.masterGrp+".lastGuidesFile", cmds.file(query=True, sceneName=True), type="string")

        # Get or create all the needed group
        self.supportGrp     = self.getBaseGrp("supportGrp", self.ar.data.prefix+"Support_Grp", ["modelsGrp", self.ar.data.prefix+"Model_Grp"]) #just to make compatibility with old rigs
        self.ctrlsGrp       = self.getBaseGrp("ctrlsGrp", self.ar.data.prefix+"Ctrls_Grp")
        self.ctrlsVisGrp    = self.getBaseGrp("ctrlsVisibilityGrp", self.ar.data.prefix+"Ctrls_Visibility_Grp")
        self.dataGrp        = self.getBaseGrp("dataGrp", self.ar.data.prefix+"Data_Grp")
        self.renderGrp      = self.getBaseGrp("renderGrp", self.ar.data.prefix+"Render_Grp")
        self.proxyGrp       = self.getBaseGrp("proxyGrp", self.ar.data.prefix+"Proxy_Grp")
        self.fxGrp          = self.getBaseGrp("fxGrp", self.ar.data.prefix+"FX_Grp")
        self.staticGrp      = self.getBaseGrp("staticGrp", self.ar.data.prefix+"Static_Grp")
        self.scalableGrp    = self.getBaseGrp("scalableGrp", self.ar.data.prefix+"Scalable_Grp")
        self.blendShapesGrp = self.getBaseGrp("blendShapesGrp", self.ar.data.prefix+"BlendShapes_Grp")
        self.wipGrp         = self.getBaseGrp("wipGrp", self.ar.data.prefix+"WIP_Grp")
        # set outliner color
        self.ar.ctrls.colorShape([self.ctrlsGrp], [0, 0.65, 1], outliner=True) #blue
        self.ar.ctrls.colorShape([self.dataGrp], [1, 1, 0], outliner=True) #yellow
        self.ar.ctrls.colorShape([self.renderGrp], [1, 0.45, 0], outliner=True) #orange

        # Arrange Hierarchy if using an original setup or preserve existing if integrating to another studio setup
        if self.ar.utils.getAllGrp():
            if self.masterGrp == self.ar.data.prefix+self.ar.data.master_name:
                cmds.parent(self.ctrlsGrp, self.dataGrp, self.renderGrp, self.proxyGrp, self.fxGrp, self.masterGrp)
                cmds.parent(self.supportGrp, self.staticGrp, self.scalableGrp, self.blendShapesGrp, self.wipGrp, self.dataGrp)
        cmds.select(clear=True)

        # Hide FX groups
        try:
            cmds.setAttr(self.fxGrp+".visibility", 0)
        except:
            pass

        # Lock and Hide attributes
        aToLock = [self.masterGrp,
                   self.supportGrp,
                   self.ctrlsGrp,
                   self.renderGrp,
                   self.dataGrp,
                   self.proxyGrp,
                   self.fxGrp,
                   self.staticGrp,
                   self.ctrlsVisGrp]
        self.ar.ctrls.setLockHide(aToLock, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        # Controllers Setup
        fMasterRadius = self.ar.ctrls.dpCheckLinearUnit(10)
        self.masterCtrl = self.getBaseCtrl("id_004_Master", "masterCtrl", self.ar.data.prefix+"Master_Ctrl", fMasterRadius, iDegree=3)
        self.globalCtrl = self.getBaseCtrl("id_003_Global", "globalCtrl", self.ar.data.prefix+"Global_Ctrl", self.ar.ctrls.dpCheckLinearUnit(13))
        # Create root control
        self.rootCtrl = self.getBaseCtrl("id_005_Root", "rootCtrl", self.ar.data.prefix+"Root_Ctrl", self.ar.ctrls.dpCheckLinearUnit(8))
        self.rootPivotCtrl = self.getBaseCtrl("id_099_RootPivot", "rootPivotCtrl", self.ar.data.prefix+"Root_Pivot_Ctrl", self.ar.ctrls.dpCheckLinearUnit(1), iDegree=3)
        needConnectPivotAttr = False
        if (self.ctrlCreated):
            needConnectPivotAttr = True
            self.rootPivotCtrlGrp = self.ar.utils.zeroOut([self.rootPivotCtrl])[0]
            cmds.parent(self.rootPivotCtrlGrp, self.rootCtrl)
            self.changeRootToCtrlsVisConstraint()
            self.ar.ctrls.createGroundDirectionShape(self.globalCtrl, 2, 15, 1)
            self.ar.ctrls.createGroundDirectionShape(self.masterCtrl, 1, 11, 0)
            self.ar.ctrls.createGroundDirectionShape(self.rootCtrl, 1, 8, 0)
        self.optionCtrl = self.getBaseCtrl("id_006_Option", "optionCtrl", self.ar.data.prefix+"Option_Ctrl", self.ar.ctrls.dpCheckLinearUnit(16))
        if (self.ctrlCreated):
            cmds.makeIdentity(self.optionCtrl, apply=True)
            self.optionCtrlGrp = self.ar.utils.zeroOut([self.optionCtrl], notTransformIO=False)[0]
            cmds.setAttr(self.optionCtrlGrp+".translateX", fMasterRadius)
            # use Option_Ctrl rigScale and rigScaleMultiplier attribute to Master_Ctrl
            self.rigScaleMD = cmds.createNode("multiplyDivide", name=self.ar.data.prefix+'RigScale_MD')
            self.ar.customAttr.addAttr(0, [self.rigScaleMD]) #dpID
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
            self.ar.ctrls.setLockHide([self.masterCtrl], ['sx', 'sy', 'sz'])
            self.ar.ctrls.setLockHide([self.optionCtrl], ['rigScaleOutput'])
            self.ar.ctrls.setNonKeyable([self.optionCtrl], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            self.ar.ctrls.setStringAttrFromList(self.optionCtrl, ['rigScaleMultiplier'])
            cmds.parent(self.rootCtrl, self.masterCtrl)
            cmds.parent(self.masterCtrl, self.globalCtrl)
            cmds.parent(self.globalCtrl, self.ctrlsGrp)
            cmds.parent(self.optionCtrlGrp, self.rootCtrl)
            cmds.parent(self.ctrlsVisGrp, self.rootCtrl)
        else:
            self.rigScaleMD = self.ar.data.prefix+'RigScale_MD'

        # parent Tag
        if "parentTag" in cmds.listAttr(self.globalCtrl):
            cmds.connectAttr(self.globalCtrl+".message", self.masterCtrl+".parentTag", force=True)
            cmds.connectAttr(self.masterCtrl+".message", self.rootCtrl+".parentTag", force=True)
            cmds.connectAttr(self.rootCtrl+".message", self.optionCtrl+".parentTag", force=True)
            cmds.connectAttr(self.rootCtrl+".message", self.rootPivotCtrl+".parentTag", force=True)

        # set lock and hide attributes
        self.ar.ctrls.setLockHide([self.scalableGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])
        self.ar.ctrls.setLockHide([self.rootCtrl, self.globalCtrl], ['sx', 'sy', 'sz', 'v'])
        self.ar.ctrls.setLockHide([self.rootPivotCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])

        # root pivot controller setup
        if needConnectPivotAttr:
            for axis in ["X", "Y", "Z"]:
                cmds.connectAttr(self.rootPivotCtrl+".translate"+axis, self.rootCtrl+".rotatePivot"+axis, force=True)
                cmds.connectAttr(self.rootPivotCtrl+".translate"+axis, self.rootCtrl+".scalePivot"+axis, force=True)

        cmds.setAttr(self.masterCtrl+".visibility", keyable=False)
        cmds.select(clear=True)

        #Base joint
        self.baseRootJnt = self.ar.data.prefix+"BaseRoot_Jnt"
        self.baseRootJntGrp = self.ar.data.prefix+"BaseRoot_Joint_Grp"
        if not cmds.objExists(self.baseRootJnt):
            self.baseRootJnt = cmds.createNode("joint", name=self.ar.data.prefix+"BaseRoot_Jnt")
            if not cmds.objExists(self.baseRootJntGrp):
                self.baseRootJntGrp = cmds.createNode("transform", name=self.ar.data.prefix+"BaseRoot_Joint_Grp")
            cmds.parent(self.baseRootJnt, self.baseRootJntGrp)
            cmds.parent(self.baseRootJntGrp, self.scalableGrp)
            cmds.parentConstraint(self.rootCtrl, self.baseRootJntGrp, maintainOffset=True, name=self.baseRootJntGrp+"_PaC")
            cmds.scaleConstraint(self.rootCtrl, self.baseRootJntGrp, maintainOffset=True, name=self.baseRootJntGrp+"_ScC")
            self.ar.customAttr.addAttr(0, [self.baseRootJntGrp], descendents=True) #dpID
            cmds.setAttr(self.baseRootJntGrp+".visibility", 0)
            self.ar.ctrls.setLockHide([self.baseRootJnt, self.baseRootJntGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
    

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


    def reorderAttributes(self, objList, attrList, verbose=True, *args):
        """ Reorder Attributes of a given objectList following the desiredAttribute list.
            Useful for organize the Option_Ctrl attributes, for example.
        """
        if objList and attrList:
            for obj in objList:
                # load dpReorderAttribute:
                #dpRAttr = dpReorderAttr.ReorderAttr(self)
                dpRAttr = self.ar.config.get_instance_info("dpReorderAttr", [self.ar.data.tools_folder])
                #dpRAttr.build_tool()

                if verbose and not self.ar.data.rebuilding:
                    self.ar.utils.setProgress('Reordering: '+self.ar.data.lang['c110_start'], 'Reordering Attributes', len(attrList), addOne=False, addNumber=False)
                delta = 0
                for i, desAttr in enumerate(attrList):
                    if verbose:
                        self.ar.utils.setProgress('Reordering Attributes: '+obj)
                    # get current user defined attributes:
                    currentAttrList = cmds.listAttr(obj, userDefined=True)
                    if desAttr in currentAttrList:
                        cAttrIndex = currentAttrList.index(desAttr)
                        maxRange = cAttrIndex+1-i+delta
                        for n in range(1, maxRange):
                            dpRAttr.dpMoveAttr(1, [obj], [desAttr])
                    else:
                        delta = delta+1
                if verbose and not self.ar.data.rebuilding:
                    self.ar.utils.setProgress(endIt=True)
                self.ar.utils.closeUI(dpRAttr.winName)
    


    #maker
    def rigAll(self, integrate=None, *args):
        """ Create the RIG based in the Guide Modules in the scene.
            Most important function to automate the generating process.
        """
        print('\ndpAutoRigSystem Log: ' + self.ar.data.lang['i178_startRigging'] + '...\n')
        # Starting progress window
        self.ar.utils.setProgress(self.ar.data.lang['i178_startRigging'], 'dpAutoRigSystem', addOne=False, addNumber=False)
        self.ar.utils.closeUI(self.ar.data.plus_info_win_name)
        self.ar.utils.closeUI(self.ar.data.color_override_win_name)
        # force refresh in order to avoid calculus error if creating Rig at the same time of guides:
        cmds.refresh()
        if self.ar.data.rebuilding:
            self.ar.filler.fill_created_guides()
        else:
            self.ar.ui_manager.refresh_ui()
        
        # get a list of modules to be rigged and re-declare the riggedModuleDic to store for log in the end:
        self.modulesToBeRiggedList = self.ar.utils.getModulesToBeRigged(self.ar.data.standard_instances)
        self.riggedModuleDic = {}
        
        # declare a list to store all integrating information:
        self.integratedTaskDic = {}
        
        # verify if there are instances of modules (guides) to rig in the scene:
        if self.modulesToBeRiggedList:
            self.ar.utils.setProgress(max=len(self.modulesToBeRiggedList), addOne=False, addNumber=False)
            
            # check guide versions to be sure we are building with the same dpAutoRigSystem version:
            for guideModule in self.modulesToBeRiggedList:
                guideVersion = cmds.getAttr(guideModule.moduleGrp+'.dpARVersion')
                if not guideVersion == self.ar.data.version:
                    btYes = self.ar.data.lang['i071_yes']
                    btUpdateGuides = self.ar.data.lang['m186_updateGuides']
                    btNo = self.ar.data.lang['i072_no']
                    userChoose = cmds.confirmDialog(title='dpAutoRigSystem - v'+self.ar.data.version, message=self.ar.data.lang['i127_guideVersionDif'], button=[btYes, btUpdateGuides, btNo], defaultButton=btYes, cancelButton=btNo, dismissString=btNo)
                    if userChoose == btNo:
                        return
                    elif userChoose == btUpdateGuides:
                        
                        #self.initExtraModule("dpUpdateGuides", self.ar.data.tools_folder)
                        #self.ar.config.get_instance_info("dpUpdateGuides", [self.ar.data.tools_folder]).build_tool()
                        self.ar.config.get_instance_info("dpUpdateGuides", [self.ar.data.tools_folder]).build_tool()
                        return
                    else:
                        break
            
            # clear all duplicated names in order to run without find same names if they exists:
            if cmds.objExists(self.ar.data.guide_mirror_grp):
                cmds.delete(self.ar.data.guide_mirror_grp)
            
            # regenerate mirror information for all guides:
            for guideModule in self.modulesToBeRiggedList:
                guideModule.checkFatherMirror()
            
            # store hierarchy from guides:
            self.hookDic = self.ar.utils.hook()
            
            # serialize all guides before build them
            for guideModule in self.modulesToBeRiggedList:
                guideModule.serializeGuide()

            if self.ar.data.integrate_all:
                self.createBaseRigNode()
            # run RIG function for each guideModule:
            for guideModule in self.modulesToBeRiggedList:
                # create the rig for this guideModule:
                guideModuleCustomName = cmds.getAttr(guideModule.moduleGrp+'.customName')
                
                # Update progress window
                guideName = guideModuleCustomName
                if not guideName:
                    guideName = cmds.getAttr(guideModule.moduleGrp+'.moduleNamespace')
                self.ar.utils.setProgress('Rigging: '+str(guideName))
                
                # Rig it :)
                guideModule.rigModule()
                # get rigged module name:
                self.riggedModuleDic[guideModule.moduleGrp.split(":")[0]] = guideModuleCustomName
                # get integrated information:
                if guideModule.integratedActionsDic:
                    self.integratedTaskDic[guideModule.moduleGrp] = guideModule.integratedActionsDic["module"]
            
            #Colorize all controller in yellow as a base
            if self.ar.data.colorize_curve:
                aBCtrl = [self.globalCtrl, self.rootCtrl, self.optionCtrl]
                aAllCtrls = cmds.ls("*_Ctrl")
                lPattern = re.compile(self.ar.data.lang['p002_left'] + '_.*._Ctrl')
                rPattern = re.compile(self.ar.data.lang['p003_right'] + '_.*._Ctrl')
                for pCtrl in aAllCtrls:
                    shapeList = cmds.listRelatives(pCtrl, children=True, allDescendents=True, fullPath=True, type="shape")
                    if shapeList:
                        if not cmds.getAttr(shapeList[0]+".overrideEnabled"):
                            if (lPattern.match(pCtrl)):
                                self.ar.ctrls.colorShape([pCtrl], "red")
                            elif (rPattern.match(pCtrl)):
                                self.ar.ctrls.colorShape([pCtrl], "blue")
                            elif (pCtrl in aBCtrl):
                                self.ar.ctrls.colorShape([pCtrl], "black")
                            else:
                                self.ar.ctrls.colorShape([pCtrl], "yellow")
            
            if self.ar.data.integrate_all:
                # Update progress window
                self.ar.utils.setProgress('Rigging: '+self.ar.data.lang['i010_integrateCB'])
                
                # get all parent info from rigged modules:
                self.originedFromDic = self.ar.utils.getOriginedFromDic()
                
                # verify if is necessary organize the hierarchies for each module:
                for guideModule in self.modulesToBeRiggedList:
                    # get guideModule info:
                    self.itemGuideModule         = self.hookDic[guideModule.moduleGrp]['name']
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
                            self.itemGuideName = sideName + self.ar.data.prefix + self.itemGuideCustomName
                        else:
                            self.itemGuideName = sideName + self.ar.data.prefix + self.itemGuideInstance
                        
                        # get hook groups info:
                        self.staticHookGrp = cmds.listConnections(guideModule.guideNet+"."+sideName+"StaticHookGrp", destination=False, source=True)[0]
                        self.scalableHookGrp = cmds.listConnections(guideModule.guideNet+"."+sideName+"ScalableHookGrp", destination=False, source=True)[0]
                        self.ctrlHookGrp = cmds.listConnections(guideModule.guideNet+"."+sideName+"ControlHookGrp", destination=False, source=True)[0]
                        
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
                                    self.fatherName = sideFatherName + self.ar.data.prefix + self.fatherCustomName
                                else:
                                    self.fatherName = sideFatherName + self.ar.data.prefix + self.fatherInstance
                                # get final rigged parent node from originedFromDic:
                                self.fatherRiggedParentNode = self.originedFromDic[self.fatherName+"_Guide_"+self.fatherGuideLoc]
                                if self.fatherRiggedParentNode:
                                    if len(self.fatherMirrorNameList) != 1: # tell us 'the father has mirror'
                                        if s == f:
                                            # parent them to the correct side of the father's mirror:
                                            if self.ctrlHookGrp:
                                                cmds.parent(self.ctrlHookGrp, self.fatherRiggedParentNode)
                                    else:
                                        # parent them to the unique father:
                                        if self.ctrlHookGrp:
                                            cmds.parent(self.ctrlHookGrp, self.fatherRiggedParentNode)
                        elif self.parentNode:
                            # parent module control to just a node in the scene:
                            cmds.parent(self.ctrlHookGrp, self.parentNode)
                        else:
                            # parent module control to default masterGrp:
                            cmds.parent(self.ctrlHookGrp, self.ctrlsVisGrp)
                        # put static and scalable groups in dataGrp:
                        cmds.parent(self.staticHookGrp, self.staticGrp)
                        cmds.parent(self.scalableHookGrp, self.scalableGrp)
                        # finish hookGrps:
                        cmds.setAttr(self.staticHookGrp+".staticHook", 0)
                        cmds.setAttr(self.scalableHookGrp+".scalableHook", 0)
                        cmds.setAttr(self.ctrlHookGrp+".ctrlHook", 0)
                        cmds.lockNode(guideModule.guideNet, lock=False)
                        cmds.deleteAttr(guideModule.guideNet+"."+sideName+"StaticHookGrp")
                        cmds.deleteAttr(guideModule.guideNet+"."+sideName+"ScalableHookGrp")
                        cmds.deleteAttr(guideModule.guideNet+"."+sideName+"ControlHookGrp")
                        cmds.lockNode(guideModule.guideNet, lock=True)

                
                # prepare to show a dialog box if find a bug:
                self.detectedBug = False
                self.bugMessage = self.ar.data.lang['b000_bugGeneral']
                
                # integrating modules together:
                if self.integratedTaskDic:
                    self.toIDList = []
                    # working with specific cases:
                    for moduleDic in self.integratedTaskDic:
                        moduleType = moduleDic[:moduleDic.find("__")]
                        
                        # display corrective controls by Option_Ctrl attribute:
                        try:
                            correctiveGrpList = self.integratedTaskDic[moduleDic]['correctiveCtrlGrpList']
                            if correctiveGrpList:
                                if not cmds.objExists(self.optionCtrl+"."+self.ar.data.lang['c124_corrective']+"Ctrls"):
                                    cmds.addAttr(self.optionCtrl, longName=self.ar.data.lang['c124_corrective']+"Ctrls", min=0, max=1, defaultValue=0, attributeType="long", keyable=False)
                                    cmds.setAttr(self.optionCtrl+"."+self.ar.data.lang['c124_corrective']+"Ctrls", channelBox=True)
                                for correctiveGrp in correctiveGrpList:
                                    cmds.connectAttr(self.optionCtrl+"."+self.ar.data.lang['c124_corrective']+"Ctrls", correctiveGrp+".visibility", force=True)
                        except:
                            pass

                        # footGuide parented in the extremGuide of the limbModule:
                        if moduleType == self.ar.data.foot_name:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                            if fatherModule == self.ar.data.limb_name and fatherGuideLoc == 'Extrem':
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
                                    # getting limb data:
                                    fatherGuide           = self.hookDic[moduleDic]['fatherGuide']
                                    ikCtrl                = self.integratedTaskDic[fatherGuide]['ikCtrlList'][s]
                                    ikHandleGrp           = self.integratedTaskDic[fatherGuide]['ikHandleGrpList'][s]
                                    ikHandleConstList     = self.integratedTaskDic[fatherGuide]['ikHandleConstList'][s]
                                    ikHandleGrpConstList  = self.integratedTaskDic[fatherGuide]['ikHandleGrpConstList'][s]
                                    ikFkBlendGrpToRevFoot = self.integratedTaskDic[fatherGuide]['ikFkBlendGrpToRevFootList'][s]
                                    extremJnt             = self.integratedTaskDic[fatherGuide]['extremJntList'][s]
                                    ikStretchExtremLoc    = self.integratedTaskDic[fatherGuide]['ikStretchExtremLoc'][s]
                                    limbTypeName          = self.integratedTaskDic[fatherGuide]['limbTypeName']
                                    worldRef              = self.integratedTaskDic[fatherGuide]['worldRefList'][s]
                                    addArticJoint         = self.integratedTaskDic[fatherGuide]['addArticJoint']
                                    addCorrective         = self.integratedTaskDic[fatherGuide]['addCorrective']
                                    ankleArticList        = self.integratedTaskDic[fatherGuide]['ankleArticList'][s]
                                    ankleCorrectiveList   = self.integratedTaskDic[fatherGuide]['ankleCorrectiveList'][s]
                                    # do task actions in order to integrate the limb and foot:
                                    cmds.cycleCheck(evaluation=False)
                                    cmds.delete(ikHandleConstList, ikHandleGrpConstList, parentConst, scaleConst) #there's an undesirable cycleCheck evaluation error here when we delete ikHandleConstList!
                                    cmds.cycleCheck(evaluation=True)
                                    cmds.parent(revFootCtrlGrp, ikFkBlendGrpToRevFoot, absolute=True)
                                    cmds.parent(ikHandleGrp, toLimbIkHandleGrp, absolute=True)
                                    self.toIDList.extend(cmds.parentConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_PaC"))
                                    if limbTypeName == self.ar.data.leg_name:
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
                                            self.toIDList.extend(cmds.parentConstraint(extremJnt, footJnt, maintainOffset=True, name=footJnt+"_PaC"))
                                        # extracting angle to avoid orientConstraint issue when uniform scaling
                                        extractAngleMM  = cmds.createNode("multMatrix", name=ankleArticList[0]+"_ExtractAngle_MM")
                                        extractAngleDM  = cmds.createNode("decomposeMatrix", name=ankleArticList[0]+"_ExtractAngle_DM")
                                        extractAngleQtE = cmds.createNode("quatToEuler", name=ankleArticList[0]+"_ExtractAngle_QtE")
                                        extractAngleMD  = cmds.createNode("multiplyDivide", name=ankleArticList[0]+"_ExtractAngle_MD")
                                        origLoc = cmds.spaceLocator(name=ankleArticList[0]+"_ExtractAngle_Orig_Loc")[0]
                                        actionLoc = cmds.spaceLocator(name=ankleArticList[0]+"_ExtractAngle_Action_Loc")[0]
                                        cmds.matchTransform(origLoc, actionLoc, ankleArticList[2], position=True, rotation=True)
                                        cmds.parent(origLoc, ankleArticList[2])
                                        cmds.parent(actionLoc, footJnt)
                                        cmds.setAttr(origLoc+".visibility", 0)
                                        cmds.setAttr(actionLoc+".visibility", 0)
                                        cmds.connectAttr(actionLoc+".worldMatrix[0]", extractAngleMM+".matrixIn[0]", force=True)
                                        cmds.connectAttr(origLoc+".worldInverseMatrix[0]", extractAngleMM+".matrixIn[1]", force=True)
                                        cmds.connectAttr(extractAngleMM+".matrixSum", extractAngleDM+".inputMatrix", force=True)
                                        cmds.connectAttr(extractAngleDM+".outputQuatX", extractAngleQtE+".inputQuatX", force=True)
                                        cmds.connectAttr(extractAngleDM+".outputQuatY", extractAngleQtE+".inputQuatY", force=True)
                                        cmds.connectAttr(extractAngleDM+".outputQuatZ", extractAngleQtE+".inputQuatZ", force=True)
                                        cmds.connectAttr(extractAngleDM+".outputQuatW", extractAngleQtE+".inputQuatW", force=True)
                                        for axis in self.ar.data.axis:
                                            cmds.setAttr(extractAngleMD+".input2"+axis, 0.5)
                                            cmds.connectAttr(extractAngleQtE+".outputRotate"+axis, ankleArticList[0]+".rotate"+axis, force=True)
                                        self.toIDList.extend([extractAngleMM, extractAngleDM, extractAngleQtE, origLoc, actionLoc])
                                        if addCorrective:
                                            for netNode in ankleCorrectiveList:
                                                if netNode:
                                                    if cmds.objExists(netNode):
                                                        actionLocList = cmds.listConnections(netNode+".actionLoc", destination=False, source=True)
                                                        if actionLocList:
                                                            cmds.connectAttr(footJnt+".message", actionLocList[0]+".inputNode", force=True)
                                                            actionLocGrp = cmds.listRelatives(actionLocList[0], parent=True, type="transform")[0]
                                                            cmds.delete(actionLocGrp+"_PaC")
                                                            self.toIDList.extend(cmds.parentConstraint(footJnt, actionLocGrp, maintainOffset=True, name=actionLocGrp+"_PaC"))
                                    scalableGrp = self.integratedTaskDic[moduleDic]["scalableGrp"][s]
                                    self.toIDList.extend(cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScC"))
                                    # hide this controller shape
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
                                    self.ar.customAttr.removeAttr("dpControl", [revFootCtrlOld])
                                    self.ar.customAttr.updateID([revFootCtrlOld])
                        
                        # worldRef of extremGuide from limbModule controlled by optionCtrl:
                        if moduleType == self.ar.data.limb_name:
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
                                self.toIDList.extend(cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_PaC"))

                                # remove dpControl attribute
                                self.ar.customAttr.removeAttr("dpControl", [worldRef])
                                self.toIDList.append(worldRef)

                                # fix poleVector follow feature integrating with Master_Ctrl and Root_Ctrl:
                                self.toIDList.extend(cmds.parentConstraint(self.masterCtrl, masterCtrlRefList[w], maintainOffset=True, name=masterCtrlRefList[w]+"_PaC"))
                                self.toIDList.extend(cmds.parentConstraint(self.rootCtrl, rootCtrlRefList[w], maintainOffset=True, name=rootCtrlRefList[w]+"_PaC"))
                            
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
                                self.toIDList.extend(cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScC"))

                                if fatherModule == self.ar.data.spine_name:
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
                                    if limbTypeName == self.ar.data.leg_name:
                                        # do task actions in order to integrate the limb of leg type to rootCtrl:
                                        cmds.parent(ikPoleVectorCtrlZero, self.ctrlsVisGrp, absolute=True)
                                    else:
                                        # do task actions in order to integrate the limb and spine (ikCtrl):
                                        self.toIDList.extend(cmds.parentConstraint(tipCtrl, ikHandleGrp, mo=1, name=ikHandleGrp+"_PaC"))
                                        # poleVector autoOrient for arm
                                        cmds.delete(rootCtrlRefList[s]+"_PaC")
                                        self.toIDList.extend(cmds.parentConstraint(tipCtrl, rootCtrlRefList[s], maintainOffset=True, name=rootCtrlRefList[s]+"_PaC"))

                                    # verify if is quadruped
                                    if limbStyle == self.ar.data.lang['m037_quadruped']:
                                        if fatherGuideLoc != "JointLoc1":
                                            # get extra info from limb module data:
                                            quadFrontLeg = self.integratedTaskDic[moduleDic]['quadFrontLegList'][s]
                                            ikCtrl       = self.integratedTaskDic[moduleDic]['ikCtrlList'][s]
                                            # if quadruped, create a parent contraint from tipCtrl to front leg:
                                            quadChestParentConst = cmds.parentConstraint(self.rootCtrl, tipCtrl, quadFrontLeg, maintainOffset=True, name=quadFrontLeg+"_PaC")[0]
                                            revNode = cmds.createNode('reverse', name=quadFrontLeg+"_Rev")
                                            self.toIDList.extend([quadChestParentConst, revNode])
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
                                    self.toIDList.extend(cmds.scaleConstraint(self.masterCtrl, nFix, name=nFix+"_ScC"))
                            
                        # integrate the volumeVariation and ikFkBlend attributes from Spine module to optionCtrl:
                        if moduleType == self.ar.data.spine_name:
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
                                self.toIDList.extend(cmds.scaleConstraint(self.masterCtrl, clusterGrp, name=clusterGrp+"_ScC"))
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
                                if self.ar.data.colorize_curve:
                                    self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['InnerCtrls'][s], "cyan")
                                    self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['OuterCtrls'][s], "yellow")
                        
                        # integrate the head orient from the masterCtrl and facial controllers to optionCtrl:
                        if moduleType == self.ar.data.head_name:
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            self.facialCtrlGrpList       = self.integratedTaskDic[moduleDic]['facialCtrlGrpList']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                # connect the masterCtrl to head group using a orientConstraint:
                                worldRef = self.integratedTaskDic[moduleDic]['worldRefList'][s]
                                self.toIDList.extend(cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_PaC"))
                                if self.ar.data.colorize_curve:
                                    if self.integratedTaskDic[moduleDic]['ctrlList']:
                                        self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['ctrlList'][s], "yellow")
                                    if self.integratedTaskDic[moduleDic]['InnerCtrls']:
                                        self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['InnerCtrls'][s], "cyan")
                                    if self.integratedTaskDic[moduleDic]['lCtrls']:
                                        self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['lCtrls'][s], "red")
                                    if self.integratedTaskDic[moduleDic]['rCtrls']:
                                        self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['rCtrls'][s], "blue")
                            if self.facialCtrlGrpList:
                                if not cmds.objExists(self.optionCtrl+"."+self.ar.data.lang['c059_facial'].lower()):
                                    cmds.addAttr(self.optionCtrl, longName=self.ar.data.lang['c059_facial'].lower(), min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                                    cmds.setAttr(self.optionCtrl+"."+self.ar.data.lang['c059_facial'].lower(), channelBox=True)
                                for facialCtrlGrp in self.facialCtrlGrpList:
                                    cmds.connectAttr(self.optionCtrl+"."+self.ar.data.lang['c059_facial'].lower(), facialCtrlGrp+".visibility", force=True)
                        
                        # integrate the Eye with the Head setup:
                        if moduleType == self.ar.data.eye_name:
                            eyeCtrl = self.integratedTaskDic[moduleDic]['eyeCtrl']
                            eyeGrp = self.integratedTaskDic[moduleDic]['eyeGrp']
                            upLocGrp = self.integratedTaskDic[moduleDic]['upLocGrp']
                            cmds.parent(eyeGrp, self.ctrlsVisGrp, relative=False)
                            # get father module:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                            if fatherModule == self.ar.data.head_name:
                                # getting head data:
                                fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                upperCtrl  = self.integratedTaskDic[fatherGuide]['upperCtrlList'][0]
                                headParentConst = cmds.parentConstraint(self.rootCtrl, upperCtrl, eyeGrp, maintainOffset=True, name=eyeGrp+"_PaC")[0]
                                eyeRevNode = cmds.createNode('reverse', name=eyeGrp+"_Rev")
                                self.toIDList.extend([headParentConst, eyeRevNode])
                                cmds.connectAttr(eyeCtrl+'.'+self.ar.data.lang['c032_follow'], eyeRevNode+".inputX", force=True)
                                cmds.connectAttr(eyeRevNode+".outputX", headParentConst+"."+self.rootCtrl+"W0", force=True)
                                cmds.connectAttr(eyeCtrl+'.'+self.ar.data.lang['c032_follow'], headParentConst+"."+upperCtrl+"W1", force=True)
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
                                    self.toIDList.extend(cmds.parentConstraint(upperCtrl, eyeScaleGrp, maintainOffset=True, name=eyeScaleGrp+"_PaC"))
                            # changing iris and pupil color override:
                            if self.ar.data.colorize_curve:
                                self.itemMirrorNameList = [""]
                                # get itemGuideName:
                                self.itemGuideMirrorAxis = self.hookDic[moduleDic]['guideMirrorAxis']
                                if self.itemGuideMirrorAxis != "off":
                                    self.itemMirrorNameList = self.itemGuideMirrorNameList
                                for s, sideName in enumerate(self.itemMirrorNameList):
                                    if self.integratedTaskDic[moduleDic]['hasIris']:
                                        irisCtrl = self.integratedTaskDic[moduleDic]['irisCtrl'][s]
                                        self.ar.ctrls.colorShape([irisCtrl], "cyan")
                                    if self.integratedTaskDic[moduleDic]['hasPupil']:
                                        pupilCtrl = self.integratedTaskDic[moduleDic]['pupilCtrl'][s]
                                        self.ar.ctrls.colorShape([pupilCtrl], "yellow")
                        
                        # integrate the Finger module:
                        if moduleType == self.ar.data.finger_name:
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
                                self.toIDList.extend(cmds.scaleConstraint(self.masterCtrl, scalableGrp, name=scalableGrp+"_ScC"))
                                # correct ikCtrl parent to root ctrl:
                                cmds.parent(ikCtrlZero, self.ctrlsVisGrp, relative=True)
                                # get father guide data:
                                fatherModule   = self.hookDic[moduleDic]['fatherModule']
                                fatherGuideLoc = self.hookDic[moduleDic]['fatherGuideLoc']
                                if fatherModule == self.ar.data.limb_name and fatherGuideLoc == 'Extrem':
                                    # getting limb type:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    limbTypeName = self.integratedTaskDic[fatherGuide]['limbTypeName']
                                    if limbTypeName == self.ar.data.arm_name:
                                        origFromList = self.integratedTaskDic[fatherGuide]['integrateOrigFromList'][s]
                                        origFrom = origFromList[-1]
                                        self.toIDList.extend(cmds.parentConstraint(origFrom, scalableGrp, maintainOffset=True, name=scalableGrp+"_PaC"))
                
                        # integrate the Single module with another Single as a father:
                        if moduleType == self.ar.data.single_name:
                            # connect Option_Ctrl display attribute to the visibility:
                            if not cmds.objExists(self.optionCtrl+"."+self.ar.data.lang['m081_tweaks'].lower()):
                                cmds.addAttr(self.optionCtrl, longName=self.ar.data.lang['m081_tweaks'].lower(), min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                                cmds.setAttr(self.optionCtrl+"."+self.ar.data.lang['m081_tweaks'].lower(), channelBox=True)
                            self.itemGuideMirrorAxis     = self.hookDic[moduleDic]['guideMirrorAxis']
                            self.itemGuideMirrorNameList = self.hookDic[moduleDic]['guideMirrorName']
                            # working with item guide mirror:
                            self.itemMirrorNameList = [""]
                            # get itemGuideName:
                            if self.itemGuideMirrorAxis != "off":
                                self.itemMirrorNameList = self.itemGuideMirrorNameList
                            for s, sideName in enumerate(self.itemMirrorNameList):
                                ctrlGrp = self.integratedTaskDic[moduleDic]["ctrlGrpList"][s]
                                cmds.connectAttr(self.optionCtrl+"."+self.ar.data.lang['m081_tweaks'].lower(), ctrlGrp+".visibility", force=True)
                            # get father module:
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            if fatherModule == self.ar.data.single_name:
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
                                    self.toIDList.extend(cmds.parentConstraint(mainJis, staticGrp, maintainOffset=True, name=staticGrp+"_PaC"))
                                    self.toIDList.extend(cmds.scaleConstraint(mainJis, staticGrp, maintainOffset=True, name=staticGrp+"_ScC"))
                                    
                        # integrate the Wheel module with another Option_Ctrl:
                        if moduleType == self.ar.data.wheel_name:
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
                                if fatherModule == self.ar.data.steering_name:
                                    # getting Steering data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    try:
                                        steeringCtrl  = self.integratedTaskDic[fatherGuide]['steeringCtrlList'][s]
                                    except:
                                        steeringCtrl  = self.integratedTaskDic[fatherGuide]['steeringCtrlList'][0]
                                    # connect modules to be integrated:
                                    cmds.connectAttr(steeringCtrl+'.'+self.ar.data.lang['c070_steering'], wheelCtrl+'.'+self.ar.data.lang['i037_to']+self.ar.data.lang['c070_steering'].capitalize(), force=True)
                                    # reparent wheel module:
                                    wheelHookCtrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][s]
                                    cmds.parent(wheelHookCtrlGrp, self.ctrlsVisGrp)
                        
                        # integrate the Suspension module with Wheel:
                        if moduleType == self.ar.data.suspension_name:
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
                                                        fatherB = fBSideName + self.ar.data.prefix + self.fatherBCustomName + "_" + loadedFatherB[loadedFatherB.rfind(":")+1:]
                                                    else:
                                                        fatherB = fBSideName + self.ar.data.prefix + self.fatherBGuideInstance + "_" + loadedFatherB[loadedFatherB.rfind(":")+1:]
                                                    fatherBRiggedNode = self.originedFromDic[fatherB]
                                                    if cmds.objExists(fatherBRiggedNode):
                                                        if len(self.fatherBMirrorNameList) != 1: #means fatherB has mirror
                                                            if s == fB:
                                                                self.toIDList.extend(cmds.parentConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_PaC"))
                                                                self.toIDList.extend(cmds.scaleConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScC"))
                                                        else:
                                                            self.toIDList.extend(cmds.parentConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_PaC"))
                                                            self.toIDList.extend(cmds.scaleConstraint(fatherBRiggedNode, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScC"))
                                    else: # probably we will parent to a control curve already generated and rigged before
                                        if cmds.objExists(loadedFatherB):
                                            self.toIDList.extend(cmds.parentConstraint(loadedFatherB, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_PaC"))
                                            self.toIDList.extend(cmds.scaleConstraint(loadedFatherB, suspensionBCtrlGrp, maintainOffset=True, name=suspensionBCtrlGrp+"_ScC"))
                                # get father module:
                                fatherModule = self.hookDic[moduleDic]['fatherModule']
                                if fatherModule == self.ar.data.wheel_name:
                                    # getting spine data:
                                    fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                    # parent suspension control group to wheel Main_Ctrl
                                    suspensionHookCtrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][s]
                                    wheelMainCtrl = self.integratedTaskDic[fatherGuide]['mainCtrlList'][s]
                                    self.toIDList.extend(cmds.parentConstraint(wheelMainCtrl, suspensionHookCtrlGrp, maintainOffset=True, name=suspensionHookCtrlGrp+"_PaC"))
                                    self.toIDList.extend(cmds.scaleConstraint(wheelMainCtrl, suspensionHookCtrlGrp, maintainOffset=True, name=suspensionHookCtrlGrp+"_ScC"))

                        # integrate the nose control colors:
                        if moduleType == self.ar.data.nose_name:
                            self.itemGuideMirrorAxis = self.hookDic[moduleDic]['guideMirrorAxis']
                            if self.itemGuideMirrorAxis == "off":
                                if self.ar.data.colorize_curve:
                                    self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['ctrlList'][0], "yellow")
                                    self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['lCtrls'][0], "red")
                                    self.ar.ctrls.colorShape(self.integratedTaskDic[moduleDic]['rCtrls'][0], "blue")
                            fatherModule   = self.hookDic[moduleDic]['fatherModule']
                            if fatherModule == self.ar.data.head_name:
                                fatherGuide = self.hookDic[moduleDic]['fatherGuide']
                                upperCtrl  = self.integratedTaskDic[fatherGuide]['upperCtrlList'][0]
                                upperJawCtrl = self.integratedTaskDic[fatherGuide]['upperJawCtrlList'][0]
                                if not upperJawCtrl == upperCtrl:
                                    ctrlGrp = self.integratedTaskDic[moduleDic]['ctrlHookGrpList'][0]
                                    mainCtrl = self.integratedTaskDic[moduleDic]['mainCtrlList'][0]
                                    cmds.addAttr(mainCtrl, longName="spaceSwitch", attributeType="enum", en="Upper Jaw:Upper Head", keyable=True)
                                    revNode = cmds.createNode("reverse", name="Nose_SpaceSwitch_Rev")
                                    pac = cmds.parentConstraint(upperJawCtrl, upperCtrl, ctrlGrp, maintainOffset=True, name=ctrlGrp+"_PaC")[0]
                                    cmds.connectAttr(mainCtrl+".spaceSwitch", pac+"."+upperCtrl+"W1", force=True)
                                    cmds.connectAttr(mainCtrl+".spaceSwitch", revNode+".inputX", force=True)
                                    cmds.connectAttr(revNode+".outputX", pac+"."+upperJawCtrl+"W0", force=True)
                                    self.toIDList.extend([pac, revNode])
                        
                        # worldRef of chain controlled by optionCtrl:
                        if moduleType == self.ar.data.chain_name:
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
                                self.toIDList.extend(cmds.parentConstraint(self.rootCtrl, worldRef, maintainOffset=True, name=worldRef+"_PaC"))
                                # remove dpControl attribute
                                self.ar.customAttr.removeAttr("dpControl", [worldRef])

                    # dpID
                    if self.toIDList:
                        self.toIDList = list(set(self.toIDList))
                        self.ar.customAttr.addAttr(0, self.toIDList, descendents=True)

                # actualise the number of rigged guides by type
                for guideType in self.ar.data.lib[self.ar.data.standard_folder]["modules"]:
                    typeCounter = 0
                    guideNetList = cmds.ls(selection=False, type="network")
                    for net in guideNetList:
                        if cmds.objExists(net+'.moduleType'):
                            dpARType = 'dp'+(cmds.getAttr(net+'.moduleType'))
                            if dpARType == guideType:
                                typeCounter = typeCounter + 1
                    if typeCounter != cmds.getAttr(self.masterGrp+'.'+guideType+'Count'):
                        cmds.setAttr(self.masterGrp+'.'+guideType+'Count', typeCounter)
                
                # parentTag
                missingParentTagCtrlList = [c for c in self.ar.ctrls.getControlList("parentTag") if not cmds.listConnections(c+".parentTag", source=True, destination=False)]
                holderCtrlList = self.ar.ctrls.getControlList("dpHolder")
                allCtrlList = self.ar.ctrls.getControlList()
                allCtrlList.extend(holderCtrlList)
                guideSourceDic = {}
                for ctrl in allCtrlList:
                    if "guideSource" in cmds.listAttr(ctrl):
                        guideSourceDic[cmds.getAttr(ctrl+".guideSource")] = ctrl
                for pTagCtrl in missingParentTagCtrlList:
                    if not pTagCtrl == self.globalCtrl:
                        if "controlID" in cmds.listAttr(pTagCtrl):
                            if not cmds.getAttr(pTagCtrl+".controlID") == "id_092_Correctives":
                                if "guideSource" in cmds.listAttr(pTagCtrl):
                                    guideSource = cmds.getAttr(pTagCtrl+".guideSource")
                                    guideBase = guideSource.split(":")[0]+":Guide_Base"
                                    parentNode = self.hookDic[guideBase]['parentNode']
                                    fatherGuide = self.hookDic[guideBase]['fatherGuide']
                                    if parentNode:
                                        if not parentNode in guideSourceDic.keys():
                                            parentNode = self.ar.utils.replaceItemSuffix(parentNode, guideSourceDic)
                                        if not parentNode in guideSourceDic.keys():
                                            continue
                                        foundCtrl = guideSourceDic[parentNode]
                                        if foundCtrl in holderCtrlList: #holder
                                            guideSource = cmds.getAttr(foundCtrl+".guideSource")
                                            guideBase = guideSource.split(":")[0]+":Guide_Base"
                                            parentNode = self.hookDic[guideBase]['parentNode']
                                            fatherGuide = self.hookDic[guideBase]['fatherGuide']
                                            parentNode = self.ar.utils.replaceItemSuffix(parentNode, guideSourceDic)
                                            if not parentNode in guideSourceDic.keys():
                                                continue
                                            foundCtrl = guideSourceDic[parentNode]
                                        if not self.hookDic[fatherGuide]['guideMirrorAxis'] == "off": #father guide has mirror
                                            mirrorNameList = self.hookDic[fatherGuide]['guideMirrorName']
                                            if pTagCtrl.startswith(mirrorNameList[0]):
                                                if not foundCtrl.startswith(mirrorNameList[0]):
                                                    foundCtrl = mirrorNameList[0]+foundCtrl[2:]
                                            else:
                                                if not foundCtrl.startswith(mirrorNameList[1]):
                                                    foundCtrl = mirrorNameList[1]+foundCtrl[2:]
                                        if cmds.objExists(foundCtrl):
                                            cmds.connectAttr(foundCtrl+".message", pTagCtrl+".parentTag", force=True)
                                    else:
                                        cmds.connectAttr(self.rootCtrl+".message", pTagCtrl+".parentTag", force=True)


            # Add usefull attributes for the animators
            if self.ar.data.supplementary_attr:
                # defining attribute name strings:
                generalAttr = self.ar.data.lang['c066_general']
                vvAttr = self.ar.data.lang['c031_volumeVariation']
                spineAttr = self.ar.data.lang['m011_spine'].lower()
                limbAttr = self.ar.data.lang['m019_limb'].lower()
                armAttr = self.ar.data.lang['m028_arm']
                legAttr = self.ar.data.lang['m030_leg']
                frontAttr = self.ar.data.lang['c056_front']
                backAttr = self.ar.data.lang['c057_back']
                leftAttr = self.ar.data.lang['p002_left'].lower()
                rightAttr = self.ar.data.lang['p003_right'].lower()
                tweaksAttr = self.ar.data.lang['m081_tweaks'].lower()
                facialAttr = self.ar.data.lang['c059_facial'].lower()
                
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
                
                if not cmds.objExists(self.optionCtrl+".controllers"):
                    cmds.addAttr(self.optionCtrl, longName="controllers", min=0, max=1, defaultValue=1, attributeType="long", keyable=False)
                    cmds.connectAttr(self.optionCtrl+".controllers", self.ctrlsVisGrp+".visibility", force=True)
                    cmds.setAttr(self.optionCtrl+".controllers", channelBox=True)

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
                'display', 'mesh', 'proxy', 'controllers', 'bends', 'extraBends', facialAttr, tweaksAttr, 'correctiveCtrls']
                # call method to reorder Option_Ctrl attributes:
                self.reorderAttributes([self.optionCtrl], desiredAttrList)
                
            #Try add hand follow (space switch attribute) on bipeds:
            
            #self.initExtraModule("dpLimbSpaceSwitch", self.ar.data.tools_folder)
            #self.ar.config.get_instance_info("dpLimbSpaceSwitch", [self.ar.data.tools_folder]).build_tool()
            
            self.ar.config.get_instance_info("dpLimbSpaceSwitch", [self.ar.data.tools_folder]).build_tool()
            # add fingers hand pose:
            
            #self.initExtraModule("dpFingerHandPose", self.ar.data.tools_folder)#, hidden=True)
            #self.ar.config.get_instance_info("dpLimbSpaceSwitch", [self.ar.data.tools_folder]).build_tool()
            
            self.ar.config.get_instance_info("dpFingerHandPose", [self.ar.data.tools_folder]).build_tool()
            #self.ar.utils.closeUI("dpInfoWindow")

            # show dialogBox if detected a bug:
            if self.ar.data.integrate_all:
                if self.detectedBug:
                    print("\n\n")
                    print(self.bugMessage)
                    cmds.confirmDialog(title=self.ar.data.lang['i078_detectedBug'], message=self.bugMessage, button=["OK"])

        # re-declaring guideMirror and previewMirror groups:
        if cmds.objExists(self.ar.data.guide_mirror_grp):
            cmds.delete(self.ar.data.guide_mirror_grp)
        
        # reload the jointSkinList:
        self.ar.filler.populate_joints()
        if not self.ar.data.rebuilding:
            self.ar.ui_manager.refresh_ui()
            # call log window:
            self.ar.logger.logWin()
            # close progress window
            self.ar.utils.setProgress(endIt=True)
        
        cmds.select(clear=True)


        