# importing libraries:
from maya import cmds
from maya import mel
import os
import getpass
import shutil
from functools import partial

# global variables to this module:
DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ISSUE_COLOR = (1.0, 0.65, 0.65)
RUNNING_COLOR = (1.0, 1.0, 1.0)

DP_ACTIONSTARTCLASS_VERSION = 2.5


class ActionStartClass(object):
    def __init__(self, dpUIinst, CLASS_NAME, TITLE, DESCRIPTION, ICON, ui=True, verbose=True):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.pipeliner = dpUIinst.pipeliner
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.ui = ui
        self.verbose = verbose
        self.active = True
        self.actionCB = None
        self.firstBT = None
        self.secondBT = None
        self.deleteDataITB = None
        self.actionType = "v000_validator" #or r000_rebuilder
        self.firstBTEnable = True
        self.secondBTEnable = True
        self.deleteDataBTEnable = False
        self.firstBTLabel = None
        self.secondBTLabel = None
        self.firstBTCustomLabel = None
        self.secondBTCustomLabel = None
        self.ioDir = None
        self.maybeDone = False
        self.infoText = self.dpUIinst.lang['i305_none']
        self.dpID = self.dpUIinst.dpID
        # returned lists
        self.checkedObjList = []
        self.foundIssueList = []
        self.resultOkList = []
        self.messageList = []
        self.dataLogDic = {}
        # start action type
        self.setActionType(self.actionType)


    def setActionType(self, value, *args):
        """ Define the button label texts.
        """
        self.actionType = value
        if self.actionType == "v000_validator":
            self.firstBTLabel = self.dpUIinst.lang['i210_verify']
            self.secondBTLabel = self.dpUIinst.lang['c052_fix']
        else: #r000_rebuilder
            self.firstBTLabel = self.dpUIinst.lang['i164_export']
            self.secondBTLabel = self.dpUIinst.lang['i196_import']
        if self.firstBTCustomLabel:
            self.firstBTLabel = self.firstBTCustomLabel
        if self.secondBTCustomLabel:
            self.secondBTLabel = self.secondBTCustomLabel


    def changeActive(self, value, *args):
        """ Set active attribute to given value.
            If there's an UI it will work to update the checkBox and buttons.
        """
        self.active = value
        if self.ui:
            cmds.checkBox(self.actionCB, edit=True, value=value)
            cmds.button(self.firstBT, edit=True, enable=value)
            cmds.button(self.secondBT, edit=True, enable=value)


    def cleanUpToStart(self, *args):
        """ Just redeclare variables and close openned window to run the code properly.
        """
        # redeclare variables
        self.checkedObjList = []
        self.foundIssueList = []
        self.resultOkList = []
        self.messageList = []
        self.dataLogDic = {}
        # close info log window if it exists
        if cmds.window('dpInfoWindow', query=True, exists=True):
            cmds.deleteUI('dpInfoWindow', window=True)
        self.updateButtonColors(True) #running
        cmds.refresh()
        if self.verbose:
            titleText = self.getTitle()
            self.utils.setProgress(titleText+': '+self.dpUIinst.lang['c110_start'], self.dpUIinst.lang[self.actionType], addOne=False, addNumber=False)


    def resetButtonColors(self, *args):
        """ Just set the button colors as default.
        """
        if self.ui:
            if cmds.button(self.firstBT, exists=True):
                cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)


    def updateButtonColors(self, running=False, *args):
        """ Update button background colors if using UI.
        """
        if self.ui:
            if cmds.button(self.firstBT, exists=True):
                if running:
                    if self.firstMode: #verify/export
                        cmds.button(self.firstBT, edit=True, backgroundColor=RUNNING_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=RUNNING_COLOR)
                elif self.maybeDone:
                    if self.firstMode: #verify/export
                        cmds.button(self.firstBT, edit=True, backgroundColor=WARNING_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=WARNING_COLOR)
                elif self.checkedObjList: #ran
                    if self.firstMode: #verify/export
                        if True in self.foundIssueList:
                            cmds.button(self.firstBT, edit=True, backgroundColor=ISSUE_COLOR)
                            if self.actionType == "v000_validator":
                                cmds.button(self.secondBT, edit=True, backgroundColor=WARNING_COLOR)
                            else:
                                cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        else:
                            cmds.button(self.firstBT, edit=True, backgroundColor=CHECKED_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        if False in self.resultOkList:
                            if self.actionType == "v000_validator":
                                cmds.button(self.firstBT, edit=True, backgroundColor=WARNING_COLOR)
                            else:
                                cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=ISSUE_COLOR)
                        else:
                            cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=CHECKED_COLOR)
                else: #wellDone
                    if self.firstMode: #verify/export
                        cmds.button(self.firstBT, edit=True, backgroundColor=CHECKED_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=CHECKED_COLOR)
    

    def updateInfoDataButton(self, *args):
        """ Just get the latest exported data and edit the info button text.
        """
        self.infoText = "\n\n"+self.dpUIinst.lang['r060_latestExportedData']+"\n"
        buttonLabel = self.getLatestExportedData()
        buttonCommand = self.dpUIinst.packager.openFolder
        buttonArgument = self.ioPath
        if cmds.iconTextButton(self.infoITB, query=True, exists=True):
            cmds.iconTextButton(self.infoITB, edit=True, command=partial(self.dpUIinst.logger.infoWin, self.title, self.description, self.infoText, 'center', 305, 250, buttonList=[buttonLabel, buttonCommand, buttonArgument]))


    def getLatestExportedData(self, *args):
        """ Returns the latest exported data or "None".
        """
        latestData = self.dpUIinst.lang['i305_none']
        exportedList = self.getExportedList()
        if exportedList:
            exportedList.sort()
            latestData = exportedList[-1]
        return latestData


    def updateActionButtons(self, running=False, color=True, *args):
        """ Update buttons colors and enable.
        """
        if color:
            self.updateButtonColors(running)
        if self.actionType == "r000_rebuilder":
            self.updateDeleteDataButton()
            self.updateInfoDataButton()


    def getTitle(self, *args):
        """ Check if there's a key in the dictionary with the current title.
            Returns its value or the current title text only.
        """
        titleText = self.title
        if self.title in self.dpUIinst.lang.keys():
            titleText = self.dpUIinst.lang[self.title]
        return titleText


    def reportLog(self, *args):
        """ Prepare the log output text and data dictionary for this checked validator/rebuilder.
        """
        # texts
        nameText = self.dpUIinst.lang['m006_name']
        modeText = self.dpUIinst.lang['v003_mode']
        foundIssueText = self.dpUIinst.lang['v006_foundIssue']
        everythingOkText = self.dpUIinst.lang['v007_allOk']
        titleText = self.getTitle()
        # header
        logText = nameText+": "+titleText+"\n"
        # mode
        logText += modeText+": "
        actionText = self.secondBTLabel.upper()
        if self.firstMode:
            actionText = self.firstBTLabel.upper()
        logText += actionText+"\n"
        # issues
        if True in self.foundIssueList:
            logText += foundIssueText+":\n"
            for i, item in enumerate(self.foundIssueList):
                if item == True:
                    logText += self.checkedObjList[i]
                    if i != len(self.checkedObjList)-1:
                        logText += "\n"
        else:
            logText += everythingOkText
        # messages
        if self.messageList:
            for msg in self.messageList:
                logText += "\n"+msg
        logText += "\n"
        # dataLog
        self.dataLogDic["log"] = self.dpUIinst.lang[self.actionType]
        self.dataLogDic["user"] = getpass.getuser()
        self.dataLogDic["time"] = self.pipeliner.getToday(True)
        self.dataLogDic["dpARVersion"] = self.dpUIinst.dpARVersion
        self.dataLogDic["module"] = self.guideModuleName
        self.dataLogDic["version"] = self.version
        self.dataLogDic["name"] = self.title
        self.dataLogDic["mode"] = actionText
        self.dataLogDic["checkedObjList"] = self.checkedObjList
        self.dataLogDic["foundIssueList"] = self.foundIssueList
        self.dataLogDic["resultOkList"] = self.resultOkList
        self.dataLogDic["messageList"] = self.messageList
        self.dataLogDic["logText"] = logText
        # verbose call info window
        if self.verbose:
            self.dpUIinst.logger.infoWin('i019_log', self.actionType, self.dataLogDic["time"]+"\n\n"+logText, "left", 250, 250)
            print("\n-------------\n"+self.dpUIinst.lang[self.actionType]+"\n"+self.dataLogDic["time"]+"\n\n"+logText)
            if not self.utils.exportLogDicToJson(self.dataLogDic, subFolder=self.dpUIinst.dpData+"/"+self.dpUIinst.dpLog):
                print(self.dpUIinst.lang['i201_saveScene'])

    
    def notFoundNodes(self, item=None, *args):
        """ Set dataLog when don't have any objects to verify.
        """
        self.checkedObjList.append(item)
        self.foundIssueList.append(False)
        self.resultOkList.append(True)
        self.messageList.append(self.dpUIinst.lang['v014_notFoundNodes'])


    def notWorkedWellIO(self, item="", *args):
        """ Set dataLog when IO not working well for rebuilders.
        """
        self.checkedObjList.append(item)
        self.foundIssueList.append(True)
        self.resultOkList.append(False)
        self.messageList.append(self.dpUIinst.lang['r005_notWorkedWell']+": "+item)


    def wellDoneIO(self, item="", text="r006_wellDone", *args):
        """ Set dataLog when rebuilder IO worked well.
        """
        self.checkedObjList.append(item)
        self.foundIssueList.append(False)
        self.resultOkList.append(True)
        self.messageList.append(self.dpUIinst.lang[text]+": "+item)


    def maybeDoneIO(self, item="", *args):
        """ Set dataLog when IO possible worked well for rebuilders, maybe.
        """
        self.maybeDone = True
        self.checkedObjList.append(item)
        self.foundIssueList.append(False)
        self.resultOkList.append(True)
        self.messageList.append(self.dpUIinst.lang['r063_maybeDoneIO']+": "+item)


    def getIOPath(self, ioDir, *args):
        """ Returns the IO path for the current scene.
        """
        if "assetPath" in self.pipeliner.pipeData.keys() and ioDir:
            return self.pipeliner.pipeData['assetPath']+"/"+self.pipeliner.pipeData[ioDir]


    def getExportedList(self, objList=None, subFolder="", askHasData=False, *args):
        """ Returns the exported file list in the current asset folder IO or the given objList.
        """
        exportedList = None
        resultList = []
        self.ioPath = self.getIOPath(self.ioDir)
        if self.ioPath:
            if askHasData:
                return os.path.exists(self.ioPath)
            if objList:
                exportedList = objList
                if not type(objList) == list:
                    exportedList = [objList]
            else:
                if os.path.exists(self.ioPath+"/"+subFolder):
                    exportedList = next(os.walk(self.ioPath+"/"+subFolder))[2]
            if exportedList:
                if subFolder:
                    return exportedList
                assetName = self.pipeliner.pipeData["assetName"]
                for item in exportedList:
                    if assetName in item:
                        resultList.append(item)
        return resultList


    def runActionsInSilence(self, actionToRunList, actionInstanceList, firstMode, objList, *args):
        """ Run action from a list without verbose.
        """
        if actionInstanceList:
            for actionToRun in actionToRunList:
                for aInst in actionInstanceList:
                    if actionToRun in str(aInst):
                        aInst.verbose = False
                        aInst.runAction(firstMode, objList)
                        aInst.verbose = True


    def refreshView(self, *args):
        """ Just refresh the viewport and fit the view camera to all visible nodes.
        """
        cmds.refresh()
        cmds.viewFit(allObjects=True, animate=True)
        mel.eval("flushUndo;")
        cmds.select(clear=True)


    def changeNodeState(self, itemList, findDeformers=True, state=None, dic=None, *args):
        """ Useful for rebuilder to set deformer node state as has no effect before export a not edited mesh.
            Returns the current node state dictionary of the given node list and all descendent hierarchy too.
        """
        resultDic = {}
        toChangeNodeStateList = []
        if findDeformers:
            for item in itemList:
                childrenList = cmds.listRelatives(item, children=True, allDescendents=True)
                if childrenList:
                    childrenList.append(item)
                else:
                    childrenList = [item]
                for child in childrenList:
                    try:
                        inputDeformerList = cmds.findDeformers(child)
                    except:
                        self.messageList.append(self.dpUIinst.lang['i075_moreOne']+": "+child)
                        inputDeformerList = False
                    if inputDeformerList:
                        for defNode in inputDeformerList:
                            if not defNode in toChangeNodeStateList:
                                toChangeNodeStateList.append(defNode)
        elif dic:
            toChangeNodeStateList = dic.keys()
        else:
            toChangeNodeStateList = itemList
        if toChangeNodeStateList:
            for node in toChangeNodeStateList:
                if not cmds.listConnections(node+".nodeState", source=True, destination=False):
                    value = state
                    if dic:
                        value = dic[node]
                    resultDic[node] = cmds.getAttr(node+".nodeState")
                    lockAttrStatus = cmds.getAttr(node+".nodeState", lock=True)
                    lockNodeStatus = cmds.lockNode(node, query=True, lock=True)[0]
                    cmds.lockNode(node, lock=False)
                    cmds.setAttr(node+".nodeState", lock=False)
                    # set nodeState attribute value
                    cmds.setAttr(node+".nodeState", value)
                    cmds.setAttr(node+".nodeState", lock=lockAttrStatus)
                    if lockNodeStatus:
                        cmds.lockNode(node, lock=True)
        return resultDic
    

    def getBrokenIDDataDic(self, toCheckList=None, *args):
        """ Return a dictionary with the broken ID nodes as keys and them father nodes as values.
        """
        dic = {"BrokenID" : {}}
        if not toCheckList:
            toCheckList = cmds.ls(selection=False, long=True, type="transform", noIntermediate=True)
        if toCheckList:
            self.utils.setProgress(self.dpUIinst.lang[self.title], self.dpUIinst.lang[self.actionType], addOne=False, addNumber=False)
            self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
            filteredList = self.utils.filterTransformList(toCheckList, filterConstraint=False, filterFollicle=False, filterJoint=False, filterLocator=False, filterHandle=False, filterLinearDeform=False, filterEffector=False, title=self.dpUIinst.lang[self.title]+" "+self.dpUIinst.lang['i329_broken'])
            if filteredList:
                for item in filteredList:
                    shortName = item[item.rfind("|")+1:]
                    if not self.utils.validateID(shortName):
                        itemType = cmds.objectType(item)
                        if not itemType in dic["BrokenID"].keys():
                            dic["BrokenID"][itemType] = {}
                        dic["BrokenID"][itemType][shortName] = None
                        fatherList = cmds.listRelatives(item, parent=True, fullPath=True)
                        if fatherList:
                            dic["BrokenID"][itemType][shortName] = fatherList[0]
        return dic


    def endProgress(self, *args):
        if self.verbose:
            self.utils.setProgress(endIt=True)


    def exportDicToJsonFile(self, dic, *args):
        """ Export given dictionary to json file using ioPath and startName as prefix of the current file name.
        """
        if dic:
            try:
                # export json file
                self.pipeliner.makeDirIfNotExists(self.ioPath)
                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                self.pipeliner.saveJsonFile(dic, jsonName)
                self.wellDoneIO(jsonName)
            except Exception as e:
                self.notWorkedWellIO(jsonName+": "+str(e))
        else:
            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])


    def exportAlembicFile(self, itemList, path=None, startName=None, fileName=None, attr=True, curve=False, *args):
        """ Export given mesh list to alembic file.
            If curve argument is True, it'll also accept export nurbsCurve shapes.
        """
        try:
            if not path:
                path = self.ioPath
            if not startName:
                startName = self.startName
            if not fileName:
                fileName = self.pipeliner.pipeData['currentFileName']
            nodeStateDic = self.changeNodeState(itemList, state=1) #has no effect
            # export alembic
            self.pipeliner.makeDirIfNotExists(path)
            ioItems = ' -root '.join(itemList)
            attrStr = ""
            if attr:
                itemList.extend(cmds.listRelatives(itemList, type="mesh", children=True, allDescendents=True, noIntermediate=True))
                if curve:
                    itemList.extend(cmds.listRelatives(itemList, type="nurbsCurve", children=True, allDescendents=True, noIntermediate=True))
                for mesh in itemList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    userDefAttrList = cmds.listAttr(mesh, userDefined=True)
                    if userDefAttrList:
                        for userDefAttr in userDefAttrList:
                            attrStr += " -attr "+userDefAttr
            abcName = path+"/"+startName+"_"+fileName+".abc"
            cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+attrStr+" -file "+abcName)
            if nodeStateDic:
                self.changeNodeState(itemList, findDeformers=False, dic=nodeStateDic) #back deformer as before
            self.wellDoneIO(abcName)
        except Exception as e:
            self.notWorkedWellIO(', '.join(itemList)+": "+str(e))


    def importLatestAlembicFile(self, exportedList, *args):
        """ Import the latest alembic file from given exported list.
        """
        self.latestDataFile = None
        if exportedList:
            self.utils.setProgress(self.dpUIinst.lang[self.title], addOne=False, addNumber=False)
            try:
                # import alembic
                exportedList.sort()
                self.latestDataFile = exportedList[-1]
                abcToImport = self.ioPath+"/"+self.latestDataFile
                #cmds.AbcImport(jobArg="-mode import \""+abcToImport+"\"")
                mel.eval("AbcImport -mode import \""+abcToImport+"\";")
                self.wellDoneIO(self.latestDataFile)
            except Exception as e:
                self.notWorkedWellIO(self.latestDataFile+": "+str(e))
        else:
            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])


    def importLatestJsonFile(self, exportedList, path=None, *args):
        """ Return the latest exported json file from given list.
        """
        self.latestDataFile = None
        if exportedList:
            if not path:
                path = self.ioPath
            exportedList.sort()
            self.latestDataFile = exportedList[-1]
            return self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
        else:
            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])


    def updateDeleteDataButton(self, *args):
        """ Check if there's some exported data for this module and update the delete data button as enable or disable.
        """
        if self.ioDir and cmds.iconTextButton(self.deleteDataITB, query=True, exists=True):
            if self.getExportedList(askHasData=True):
                cmds.iconTextButton(self.deleteDataITB, edit=True, enable=True)
            else:
                cmds.iconTextButton(self.deleteDataITB, edit=True, enable=False)


    def deleteData(self, *args):
        """ Confirm if the user really want to delete the rebuilding exported data, then delete its folder.
        """
        # to confirm before delete data
        confirm = cmds.confirmDialog(title=self.dpUIinst.lang[self.title], icon="question", message=self.dpUIinst.lang['r059_deleteData'], button=[self.dpUIinst.lang['i071_yes'], self.dpUIinst.lang['i072_no']], defaultButton=self.dpUIinst.lang['i072_no'], cancelButton=self.dpUIinst.lang['i072_no'], dismissString=self.dpUIinst.lang['i072_no'])
        if confirm == self.dpUIinst.lang['i071_yes']:
            oldFirstBTLabel = self.firstBTLabel
            self.firstMode = True
            self.firstBTLabel = self.dpUIinst.lang['i344_deleted']
            try:
                shutil.rmtree(self.ioPath, ignore_errors=False)
                self.updateDeleteDataButton()
                self.updateInfoDataButton()
                self.wellDoneIO(self.ioPath, 'i344_deleted')
            except:
                self.notWorkedWellIO(self.ioPath)
            self.reportLog()
            self.firstBTLabel = oldFirstBTLabel
