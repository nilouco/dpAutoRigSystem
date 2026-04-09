# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
from ....Tools import dpHeadDeformer
from importlib import reload
import ast

# global variables to this module:
CLASS_NAME = "GuideIO"
TITLE = "r012_guideIO"
DESCRIPTION = "r013_guideIODesc"
ICON = "/Icons/dp_guideIO.png"
WIKI = "10-‐-Rebuilder#-guide"

MODULES = "Modules.Standard"

DP_GUIDEIO_VERSION = 1.05


class GuideIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = WIKI
        self.version = DP_GUIDEIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_guideIO"
        self.startName = "dpGuide"
        if self.ar.dev:
            reload(dpHeadDeformer)
        self.dpHeadDeformer = dpHeadDeformer.HeadDeformer(self.ar)
        self.dpHeadDeformer.ui = False
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    if self.firstMode: #export
                        netList = None
                        if objList:
                            netList = objList
                        else:
                            netList = self.utils.getNetworkNodeByAttr("dpGuideNet")
                            netList.extend(self.utils.getNetworkNodeByAttr("dpHeadDeformerNet") or [])
                        if netList:
                            self.ar.ctrls.unPinGuide(force=True)
                            self.exportDicToJsonFile(self.getGuideDataDic(netList))
                        else:
                            self.maybeDoneIO(self.ar.data.lang['v014_notFoundNodes'])
                            cmds.select(clear=True)
                    else: #import
                        # apply viewport xray
                        modelPanelList = cmds.getPanel(type="modelPanel")
                        for mp in modelPanelList:
                            cmds.modelEditor(mp, edit=True, xray=True)
                        guideDic = self.importLatestJsonFile(self.getExportedList())
                        if guideDic:
                            wellImported = False
                            try:
                                wellImported = self.importGuide(guideDic)
                                self.setupGuideBaseParenting(guideDic)
                            except Exception as e:
                                if not wellImported: #guide initialization issue
                                    self.notWorkedWellIO(self.ar.data.lang['m195_couldNotBeSet']+": "+str(e))
                                else: #parenting issue
                                    self.notWorkedWellIO(self.ar.data.lang['m197_notPossibleParent']+": "+str(e))
                                wellImported = False
                            if wellImported:
                                self.wellDoneIO(self.latestDataFile)
                        else:
                            self.maybeDoneIO(self.ar.data.lang['r007_notExportedData'])
                        cmds.select(clear=True)
                        # remove viewport xray
                        for mp in modelPanelList:
                            cmds.modelEditor(mp, edit=True, xray=False)
                else:
                    self.notWorkedWellIO(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        if self.ar.data.ui_state:
            self.ar.ui_manager.clear_guide_layout()
            self.ar.filler.fill_created_guides()
        return self.dataLogDic


    def getGuideDataDic(self, netList, *args):
        """ Return a dictionary of the guide data to export it.
        """
        toExportDataDic = {}
        self.utils.setProgress(max=len(netList), addOne=False, addNumber=False)
        for net in netList:
            self.utils.setProgress(self.ar.data.lang[self.title])
            # mount a dic with all data 
            if "afterData" in cmds.listAttr(net):
                if "rawGuide" in cmds.listAttr(net) and cmds.getAttr(net+".rawGuide"):
                    # get data from not rendered guide (rawGuide status on)
                    moduleInstanceInfoString = cmds.getAttr(cmds.listConnections(net+".moduleGrp")[0]+".moduleInstanceInfo")
                    for moduleInstance in self.ar.data.standard_instances:
                        if str(moduleInstance) == moduleInstanceInfoString:
                            moduleInstance.serializeGuide(False) #serialize it without build it
                toExportDataDic[net] = ast.literal_eval(cmds.getAttr(net+".afterData"))
            elif "dpHeadDeformerNet" in cmds.listAttr(net):
                if not cmds.listConnections(net+".guideNet", source=True, destination=False):
                    toExportDataDic[net] = ast.literal_eval(cmds.getAttr(net+".netData"))
        return toExportDataDic


    def setupInstanceChanges(self, *args):
        """ Run instance code to Guide_Base node configuration or just set the simple attributes.
        """
        directionList = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        customAttrList = ["flip",
                          "mainControls",
                          "nMain",
                          "dynamic",
                          "corrective",
                          "alignWorld",
                          "additional",
                          "softIk",
                          "nostril",
                          "indirectSkin",
                          "holder",
                          "sdkLocator",
                          "startFrame",
                          "showControls",
                          "steering",
                          "degree",
                          "eyelid",
                          "iris",
                          "pupil",
                          "specular",
                          "lidPivot",
                          "style",
                          "rigType",
                          "numBendJoints",
                          "facial",
                          "facialBrow",
                          "facialEyelid",
                          "facialMouth",
                          "facialLips",
                          "facialSneer",
                          "facialGrimace",
                          "facialFace",
                          "deformer",
                          "deformedBy",
                          "worldSize",
                          "jaw",
                          "chin",
                          "lips",
                          "upperHead"
                          ]
        for item in list(self.netDic["GuideData"]):
            new_item = self.get_new_name(item)
            if cmds.objExists(new_item):
                if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #moduleGrp
                    for baseAttr in list(self.netDic["GuideData"][item]):
                        if baseAttr == "customName":
                            customNameData = self.netDic["GuideData"][item]["customName"]
                            if customNameData:
                                self.instance.editGuideModuleName(customNameData)
                        elif baseAttr == "mirrorAxis":
                            cmds.setAttr(new_item+".mirrorAxis", self.netDic["GuideData"][item]["mirrorAxis"], type="string")
                            cmds.setAttr(new_item+".mirrorName", self.netDic["GuideData"][item]["mirrorName"], type="string")
                            self.instance.createPreviewMirror()
                        elif baseAttr == "articulation":
                            self.instance.setArticulation(self.netDic["GuideData"][item]["articulation"])
                        elif baseAttr == "nJoints":
                            self.instance.changeJointNumber(self.netDic["GuideData"][item]["nJoints"])
                        elif baseAttr == "type": #limb
                            self.instance.changeType(self.netDic["GuideData"][item]["type"])
                        elif baseAttr == "hasBend": #limb
                            self.instance.changeBend(self.netDic["GuideData"][item]["hasBend"])
                        elif baseAttr == "aimDirection": #eye
                            self.instance.changeAimDirection(directionList[(int(self.netDic["GuideData"][item]["aimDirection"]))])
                        elif baseAttr == "fatherB": #suspention
                            fatherBData = self.netDic["GuideData"][item]["fatherB"]
                            if fatherBData:
                                cmds.setAttr(item+".fatherB", fatherBData, type="string")
                        elif baseAttr == "geo": #wheel
                            geoData = self.netDic["GuideData"][item]["geo"]
                            if geoData:
                                cmds.setAttr(new_item+".geo", geoData, type="string")
                        #TODO: modernize rigType to rigStyle new code
                        elif baseAttr == "rigType": #all
                            rigTypeData = self.netDic["GuideData"][item]["rigType"]
                            if rigTypeData:
                                cmds.setAttr(new_item+".rigType", rigTypeData, type="string")
                                self.instance.rigType = rigTypeData
                        else: #just set simple attributes
                            if baseAttr in customAttrList:
                                cmds.setAttr(new_item+"."+baseAttr, self.netDic["GuideData"][item][baseAttr])
                        cmds.refresh()


    def setupGuideTransformations(self, *args):
        """ Work with guide transformations to put the transform as imported data.
        """
        for item in list(self.netDic["GuideData"]):
            if item in self.netDic["GuideData"].keys():
                new_item = self.get_new_name(item)
                for attr in list(self.netDic["GuideData"][item]):
                    if attr in self.ar.data.transform_attrs:
                        if not cmds.getAttr(new_item+"."+attr, lock=True): #unlocked attribute
                            if not cmds.listConnections(new_item+"."+attr, destination=False, source=True): #without input connection
                                cmds.setAttr(new_item+"."+attr, self.netDic["GuideData"][item][attr])
                    cmds.refresh()


    def setupGuideBaseParenting(self, guideDic, *args):
        """ Rebuild the Guide_Base parenting.
        """
        for net in guideDic.keys():
            netDic = guideDic[net]
            if "GuideData" in netDic.keys():
                for item in list(netDic["GuideData"]):
                    new_item = self.get_new_name(item)
                    if cmds.objExists(new_item):
                        if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #moduleGrp
                            fatherNodeData = netDic["GuideData"][item]['FatherNode']
                            if fatherNodeData:
                                new_father = self.get_new_name(fatherNodeData)
                                if cmds.objExists(new_father):
                                    if not cmds.listRelatives(new_item, parent=True) or not cmds.listRelatives(new_item, parent=True)[0] == new_father:
                                        cmds.parent(new_item, new_father)


    def importGuide(self, guideDic, *args):
        """ Import guide info and initialize guide setting it attribute values.
        """
        wellImported = True
        self.correlations = {}
        self.utils.setProgress(max=len(guideDic.keys()), addOne=False, addNumber=False)
        if self.ar.data.ui_state:
            self.ar.data.collapse_edit_sel_mod = True
            self.ar.filler.fill_created_guides()
        for net in guideDic.keys():
            if "moduleType" in guideDic[net].keys():
                if guideDic[net]["moduleType"] == self.dpHeadDeformer.headDeformerName:
                    wellImported = self.importHeadDeformer(guideDic[net])
            else:
                toInitializeGuide = True
                if cmds.objExists(net):
                    if cmds.getAttr(net+".rawGuide"):
                        toInitializeGuide = False
                    else:
                        cmds.lockNode(net, lock=False)
                        cmds.delete(net)
                if toInitializeGuide:
                    #try:
                        #self.netDic = json.loads(guideDic[net])
                        self.netDic = guideDic[net]
                        self.utils.setProgress(self.ar.data.lang[self.title]+': '+guideDic[net]['ModuleType'])
                        # create a module instance:
                        self.instance = self.ar.lib.initialize_library("dp"+self.netDic['ModuleType'], self.ar.data.standard_folder)[0]
                        self.correlations[f"{self.netDic['ModuleType']}__dpAR_{self.netDic['GuideNumber']}"] = self.instance.guideNamespace
                        self.instance.build_raw_guide()
                        self.setupInstanceChanges()
                        self.setupGuideTransformations()
                        cmds.select(clear=True)
                    #except Exception as e:
                    #    print("Error:", e)
                    #    wellImported = False
                    #    self.notWorkedWellIO(net+": "+str(e))
                    #    break
        if self.ar.data.ui_state:
            self.ar.data.collapse_edit_sel_mod = False

        return wellImported


    def importHeadDeformer(self, hdNet, *args):
        """ Process the headDeformer importing.
        """
        return self.dpHeadDeformer.dpHeadDeformer(hdNet["hdName"], hdNet["hdList"])


    def get_new_name(self, name):
        if not cmds.objExists(name):
            base = name.split(":")[0]
            if base in self.correlations.keys():
                return name.replace(base, self.correlations[base])
        return name
