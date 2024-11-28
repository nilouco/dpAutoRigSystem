# importing libraries:
from maya import cmds
from maya import mel
import os
import getpass

# global variables to this module:
DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ISSUE_COLOR = (1.0, 0.7, 0.7)
RUNNING_COLOR = (1.0, 1.0, 1.0)

DP_ACTIONSTARTCLASS_VERSION = 2.3


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
        self.actionType = "v000_validator" #or r000_rebuilder
        self.firstBTEnable = True
        self.secondBTEnable = True
        self.firstBTLabel = None
        self.secondBTLabel = None
        self.firstBTCustomLabel = None
        self.secondBTCustomLabel = None
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
                elif self.checkedObjList:
                    if self.firstMode: #verify/export
                        if True in self.foundIssueList:
                            cmds.button(self.firstBT, edit=True, backgroundColor=ISSUE_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=WARNING_COLOR)
                        else:
                            cmds.button(self.firstBT, edit=True, backgroundColor=CHECKED_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        if False in self.resultOkList:
                            cmds.button(self.firstBT, edit=True, backgroundColor=WARNING_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=ISSUE_COLOR)
                        else:
                            cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=CHECKED_COLOR)
                else:
                    if self.firstMode: #verify/export
                        cmds.button(self.firstBT, edit=True, backgroundColor=CHECKED_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=CHECKED_COLOR)
    

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
        logText = "\n"+nameText+": "+titleText+"\n"
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
            self.dpUIinst.logger.infoWin('i019_log', self.actionType, self.dataLogDic["time"]+"\n"+logText, "left", 250, 250)
            print("\n-------------\n"+self.dpUIinst.lang[self.actionType]+"\n"+self.dataLogDic["time"]+"\n"+logText)
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


    def wellDoneIO(self, item="", *args):
        """ Set dataLog when rebuilder IO worked well.
        """
        self.checkedObjList.append(item)
        self.foundIssueList.append(False)
        self.resultOkList.append(True)
        self.messageList.append(self.dpUIinst.lang['r006_wellDone']+": "+item)


    def getIOPath(self, ioDir, *args):
        """ Returns the IO path for the current scene.
        """
        return self.pipeliner.pipeData['assetPath']+"/"+self.pipeliner.pipeData[ioDir]


    def getExportedList(self, objList=None, subFolder="", *args):
        """ Returns the exported file list in the current asset folder IO or the given objList.
        """
        exportedList = None
        resultList = []
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
                    lockNodeStatus = cmds.lockNode(node, query=True, lock=True)
                    cmds.lockNode(node, lock=False)
                    cmds.setAttr(node+".nodeState", lock=False)
                    # set nodeState attribute value
                    cmds.setAttr(node+".nodeState", value)
                    cmds.setAttr(node+".nodeState", lock=lockAttrStatus)
                    if lockNodeStatus:
                        cmds.lockNode(node, lock=1)
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
            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])


    def exportAlembicFile(self, meshList, path=None, name=None, attr=True, *args):
        """ Export given mesh list to alembic file.
        """
        try:
            if not path:
                path = self.ioPath
            if not name:
                name = self.startName
            nodeStateDic = self.changeNodeState(meshList, state=1) #has no effect
            # export alembic
            self.pipeliner.makeDirIfNotExists(path)
            ioItems = ' -root '.join(meshList)
            attrStr = ""
            if attr:
                meshList.extend(cmds.listRelatives(meshList, type="mesh", children=True, allDescendents=True, noIntermediate=True))
                for mesh in meshList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    userDefAttrList = cmds.listAttr(mesh, userDefined=True)
                    if userDefAttrList:
                        for userDefAttr in userDefAttrList:
                            attrStr += " -attr "+userDefAttr
            abcName = path+"/"+name+"_"+self.pipeliner.pipeData['currentFileName']+".abc"
            cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+attrStr+" -file "+abcName)
            if nodeStateDic:
                self.changeNodeState(meshList, findDeformers=False, dic=nodeStateDic) #back deformer as before
            self.wellDoneIO(', '.join(meshList))
        except Exception as e:
            self.notWorkedWellIO(', '.join(meshList)+": "+str(e))
