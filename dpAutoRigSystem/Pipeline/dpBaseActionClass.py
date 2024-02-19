# importing libraries:
from maya import cmds
import os
import time
import getpass

# global variables to this module:
DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ISSUE_COLOR = (1.0, 0.7, 0.7)

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
        # returned lists
        self.checkedObjList = []
        self.foundIssueList = []
        self.resultOkList = []
        self.messageList = []
        self.dataLogDic = {}


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
        if self.verbose:
            # Starting progress window
            cmds.progressWindow(title=self.dpUIinst.lang[self.actionType], progress=0, status=self.dpUIinst.lang[self.title]+': 0%', isInterruptable=False)


    def updateButtonColors(self, *args):
        """ Update button background colors if using UI.
        """
        if self.ui:
            if cmds.button(self.firstBT, exists=True):
                if self.checkedObjList:
                    if self.firstMode:
                        if True in self.foundIssueList:
                            cmds.button(self.firstBT, edit=True, backgroundColor=ISSUE_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=WARNING_COLOR)
                        else:
                            cmds.button(self.firstBT, edit=True, backgroundColor=CHECKED_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix
                        if False in self.resultOkList:
                            cmds.button(self.firstBT, edit=True, backgroundColor=WARNING_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=ISSUE_COLOR)
                        else:
                            cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.secondBT, edit=True, backgroundColor=CHECKED_COLOR)
                else:
                    if self.firstMode:
                        cmds.button(self.firstBT, edit=True, backgroundColor=CHECKED_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix
                        cmds.button(self.firstBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.secondBT, edit=True, backgroundColor=CHECKED_COLOR)
    

    def reportLog(self, *args):
        """ Prepare the log output text and data dictionary for this checked validator/rebuilder.
        """
        thisTime = str(time.asctime(time.localtime(time.time())))
        # texts
        nameText = self.dpUIinst.lang['m006_name']
        titleText = self.dpUIinst.lang[self.title]
        modeText = self.dpUIinst.lang['v003_mode']
        if self.actionType == "v000_validator":
            firstText = self.dpUIinst.lang['i210_verify'].upper()
            secondText = self.dpUIinst.lang['c052_fix'].upper()
        else: #r000_rebuilder
            firstText = self.dpUIinst.lang['i164_export'].upper()
            secondText = self.dpUIinst.lang['i196_import'].upper()
        foundIssueText = self.dpUIinst.lang['v006_foundIssue']
        everythingOkText = self.dpUIinst.lang['v007_allOk']
        # header
        logText = "\n"+nameText+": "+titleText+"\n"
        # mode
        logText += modeText+": "
        actionText = secondText
        if self.firstMode:
            actionText = firstText
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
        self.dataLogDic["time"] = thisTime
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
            self.dpUIinst.logger.infoWin('i019_log', self.actionType, thisTime+"\n"+logText, "left", 250, 250)
            print("\n-------------\n"+self.dpUIinst.lang[self.actionType]+"\n"+thisTime+"\n"+logText)
            if not self.utils.exportLogDicToJson(self.dataLogDic, subFolder=self.dpUIinst.dpData+"/"+self.dpUIinst.dpLog):
                print(self.dpUIinst.lang['i201_saveScene'])


    def endProgressBar(self, *args):
        if self.verbose:
            cmds.progressWindow(endProgress=True)

    
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
        return self.pipeliner.getCurrentPath()+"/"+self.pipeliner.pipeData[ioDir]


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
            assetName = self.pipeliner.getCurrentFileName()
            assetName = assetName[:assetName.find("_")]
            print("assetName =", assetName)
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
