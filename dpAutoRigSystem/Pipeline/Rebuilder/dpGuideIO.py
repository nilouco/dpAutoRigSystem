# importing libraries:
from maya import cmds
from .. import dpBaseActionClass
import json

# global variables to this module:
CLASS_NAME = "GuideIO"
TITLE = "r012_guideIO"
DESCRIPTION = "r013_guideIODesc"
ICON = "/Icons/dp_guideIO.png"

MODULES = "Modules"

DP_GUIDEIO_VERSION = 1.0


class GuideIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_GUIDEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_guideIO"
        self.startName = "dpGuide"
    

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
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    netList = None
                    if objList:
                        netList = objList
                    else:
                        netList = self.utils.getNetworkNodeByAttr("dpGuideNet")
                    if netList:
                        toExportDataDic = {}
                        progressAmount = 0
                        maxProcess = len(netList)
                        for net in netList:
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                            # mount a dic with all data 
                            if cmds.objExists(net+".afterData"):
                                if cmds.getAttr(net+".rawGuide"): 
                                    # get data from not rendered guide (rawGuide status on)
                                    moduleInstanceInfoString = cmds.getAttr(cmds.listConnections(net+".moduleGrp")[0]+".moduleInstanceInfo")
                                    for moduleInstance in self.dpUIinst.moduleInstancesList:
                                        if str(moduleInstance) == moduleInstanceInfoString:
                                            moduleInstance.serializeGuide(False) #serialize it without build it
                                toExportDataDic[net] = cmds.getAttr(net+".afterData")
                        if toExportDataDic:
                            try:
                                # export json file
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".json"
                                self.pipeliner.saveJsonFile(toExportDataDic, jsonName)
                                self.wellDoneIO(jsonName)
                            except:
                                self.notWorkedWellIO(jsonName)
                        else:
                            self.notWorkedWellIO("v014_notFoundNodes")
                        cmds.select(clear=True)
                    else:
                        self.notWorkedWellIO("v014_notFoundNodes")
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            self.importedDataDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if self.importedDataDic:
                                wellImported = True
                                progressAmount = 0
                                maxProcess = len(self.importedDataDic.keys())
                                for net in self.importedDataDic.keys():
                                    progressAmount += 1
                                    toInitializeGuide = True
                                    if cmds.objExists(net):
                                        if cmds.getAttr(net+".rawGuide"):
                                            toInitializeGuide = False
                                        else:
                                            cmds.lockNode(net, lock=False)
                                            cmds.delete(net)
                                    if toInitializeGuide:
                                        try:
                                            self.netDic = json.loads(self.importedDataDic[net])
                                            if self.verbose:
                                                # Update progress window
                                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" - "+self.netDic['ModuleType']))
                                            # create a module instance:
                                            self.instance = self.dpUIinst.initGuide("dp"+self.netDic['ModuleType'], MODULES, number=self.netDic["GuideNumber"])
                                            self.setupInstanceChanges()
                                            self.setupGuideTransformations()
                                        except:
                                            wellImported = False
                                            self.notWorkedWellIO(net)
                                            break
                                try:
                                    # Parenting guides
                                    self.setupGuideBaseParenting(self.dpUIinst.lang['m197_notPossibleParent'])
                                except:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                                    wellImported = False
                                if wellImported:
                                    self.wellDoneIO(exportedList[-1])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                            cmds.select(clear=True)
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    except:
                        self.notWorkedWellIO(exportedList[-1])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        cmds.refresh()
        return self.dataLogDic


    def setupInstanceChanges(self, *args):
        """ Run instance code to Guide_Base node configuration or just set the simple attributes.
        """
        directionList = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        customAttrList = ["flip", "mainControls", "nMain", "dynamic", "corrective", "alignWorld", "additional", "softIk", "nostril", "indirectSkin", "holder", "sdkLocator", "startFrame", "showControls", "steering", "degree", "eyelid", "iris", "pupil", "specular", "lidPivot", "style", "rigType"]
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
            for attr in list(self.netDic["GuideData"][item]):
                if attr in transformAttrList:
                    if not cmds.getAttr(item+"."+attr, lock=True): #unlocked attribute
                        if not cmds.listConnections(item+"."+attr, destination=False, source=True): #without input connection
                            cmds.setAttr(item+"."+attr, self.netDic["GuideData"][item][attr])
                cmds.refresh()


    def setupGuideBaseParenting(self, *args):
        """ Rebuild the Guide_Base parenting.
        """
        for net in self.importedDataDic.keys():
            netDic = json.loads(self.importedDataDic[net])
            for item in list(netDic["GuideData"]):
                if cmds.objExists(item+".guideBase") and cmds.getAttr(item+".guideBase") == 1: #moduleGrp
                    fatherNodeData = netDic["GuideData"][item]['FatherNode']
                    if fatherNodeData:
                        if cmds.objExists(fatherNodeData):
                            cmds.parent(item, fatherNodeData)
