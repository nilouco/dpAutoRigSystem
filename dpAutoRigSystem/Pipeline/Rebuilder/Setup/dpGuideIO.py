# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
from ....Tools import dpHeadDeformer
import ast

# global variables to this module:
CLASS_NAME = "GuideIO"
TITLE = "r012_guideIO"
DESCRIPTION = "r013_guideIODesc"
ICON = "/Icons/dp_guideIO.png"

MODULES = "Modules.Standard"

DP_GUIDEIO_VERSION = 1.2


class GuideIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_GUIDEIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_guideIO"
        self.startName = "dpGuide"
        self.dpHeadDeformer = dpHeadDeformer.HeadDeformer(self.dpUIinst, ui=False)
    

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
        if self.pipeliner.checkAssetContext():
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    netList = None
                    if objList:
                        netList = objList
                    else:
                        netList = self.utils.getNetworkNodeByAttr("dpGuideNet")
                        netList.extend(self.utils.getNetworkNodeByAttr("dpHeadDeformerNet"))
                    if netList:
                        self.exportDicToJsonFile(self.getGuideDataDic(netList))
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes'])
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
                                self.notWorkedWellIO(self.dpUIinst.lang['m195_couldNotBeSet']+": "+str(e))
                            else: #parenting issue
                                self.notWorkedWellIO(self.dpUIinst.lang['m197_notPossibleParent']+": "+str(e))
                            wellImported = False
                        if wellImported:
                            self.wellDoneIO(self.latestDataFile)
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    cmds.select(clear=True)
                    # remove viewport xray
                    for mp in modelPanelList:
                        cmds.modelEditor(mp, edit=True, xray=False)
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getGuideDataDic(self, netList, *args):
        """ Return a dictionary of the guide data to export it.
        """
        toExportDataDic = {}
        self.utils.setProgress(max=len(netList), addOne=False, addNumber=False)
        for net in netList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # mount a dic with all data 
            if "afterData" in cmds.listAttr(net):
                if "rawGuide" in cmds.listAttr(net) and cmds.getAttr(net+".rawGuide"):
                    # get data from not rendered guide (rawGuide status on)
                    moduleInstanceInfoString = cmds.getAttr(cmds.listConnections(net+".moduleGrp")[0]+".moduleInstanceInfo")
                    for moduleInstance in self.dpUIinst.moduleInstancesList:
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
        customAttrList = ["flip", "mainControls", "nMain", "dynamic", "corrective", "alignWorld", "additional", "softIk", "nostril", "indirectSkin", "holder", "sdkLocator", "startFrame", "showControls", "steering", "degree", "eyelid", "iris", "pupil", "specular", "lidPivot", "style", "rigType", "numBendJoints", "facial", "facialBrow", "facialEyelid", "facialMouth", "facialLips", "facialSneer", "facialGrimace", "facialFace", "deformer", "deformedBy", "worldSize"]
        for item in list(self.netDic["GuideData"]):
            if cmds.objExists(item+".guideBase") and cmds.getAttr(item+".guideBase") == 1: #moduleGrp
                for baseAttr in list(self.netDic["GuideData"][item]):
                    if baseAttr == "customName":
                        customNameData = self.netDic["GuideData"][item]["customName"]
                        if customNameData:
                            self.instance.editUserName(customNameData)
                    elif baseAttr == "mirrorAxis":
                        cmds.setAttr(item+".mirrorAxis", self.netDic["GuideData"][item]["mirrorAxis"], type="string")
                        cmds.setAttr(item+".mirrorName", self.netDic["GuideData"][item]["mirrorName"], type="string")                                                        
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
                            cmds.setAttr(item+".geo", geoData, type="string")
                    elif baseAttr == "rigType": #all
                        rigTypeData = self.netDic["GuideData"][item]["rigType"]
                        if rigTypeData:
                            cmds.setAttr(item+".rigType", rigTypeData, type="string")
                            self.instance.rigType = rigTypeData
                    else: #just set simple attributes
                        if baseAttr in customAttrList:
                            cmds.setAttr(item+"."+baseAttr, self.netDic["GuideData"][item][baseAttr])
                    cmds.refresh()


    def setupGuideTransformations(self, *args):
        """ Work with guide transformations to put the transform as imported data.
        """
        transformAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
        for item in list(self.netDic["GuideData"]):
            if self.netDic["GuideData"][item]:
                for attr in list(self.netDic["GuideData"][item]):
                    if attr in transformAttrList:
                        if not cmds.getAttr(item+"."+attr, lock=True): #unlocked attribute
                            if not cmds.listConnections(item+"."+attr, destination=False, source=True): #without input connection
                                cmds.setAttr(item+"."+attr, self.netDic["GuideData"][item][attr])
                    cmds.refresh()


    def setupGuideBaseParenting(self, guideDic, *args):
        """ Rebuild the Guide_Base parenting.
        """
        for net in guideDic.keys():
            netDic = guideDic[net]
            if "GuideData" in netDic.keys():
                for item in list(netDic["GuideData"]):
                    if "guideBase" in cmds.listAttr(item) and cmds.getAttr(item+".guideBase") == 1: #moduleGrp
                        fatherNodeData = netDic["GuideData"][item]['FatherNode']
                        if fatherNodeData:
                            if cmds.objExists(fatherNodeData):
                                cmds.parent(item, fatherNodeData)


    def importGuide(self, guideDic, *args):
        """ Import guide info and initialize guide setting it attribute values.
        """
        wellImported = True
        self.utils.setProgress(max=len(guideDic.keys()), addOne=False, addNumber=False)
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
                    try:
                        #self.netDic = json.loads(guideDic[net])
                        self.netDic = guideDic[net]
                        self.utils.setProgress(self.dpUIinst.lang[self.title]+': '+guideDic[net]['ModuleType'])
                        # create a module instance:
                        self.instance = self.dpUIinst.initGuide("dp"+self.netDic['ModuleType'], MODULES, number=self.netDic["GuideNumber"])
                        self.setupInstanceChanges()
                        self.setupGuideTransformations()
                    except Exception as e:
                        wellImported = False
                        self.notWorkedWellIO(net+": "+str(e))
                        break
        return wellImported


    def importHeadDeformer(self, hdNet, *args):
        """ Process the headDeformer importing.
        """
        return self.dpHeadDeformer.dpHeadDeformer(hdNet["hdName"], hdNet["hdList"])
