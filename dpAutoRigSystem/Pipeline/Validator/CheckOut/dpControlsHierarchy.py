# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
import json
import os

# global variables to this module:
CLASS_NAME = "ControlsHierarchy"
TITLE = "v060_controlsHierarchy"
DESCRIPTION = "v061_controlsHierarchyDesc"
ICON = "/Icons/dp_controlsHierarchy.png"



DP_CONTROLSHIERARCHY_VERSION = 1.06


class ControlsHierarchy(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONTROLSHIERARCHY_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_hierarchyIO"
        self.startName = "dpHierarchy"


    def checkNurbs(self, transform):
        try:
            shapeList = cmds.listRelatives(transform, shapes=True)
        except Exception as e:
            print(e)
            self.messageList.append(f"{self.dpUIinst.lang['v070_duplicateName']} {transform}")
            return False
        if shapeList:
            for shape in shapeList:
                if "nurbsCurve" not in cmds.objectType(shape):
                    return False
        else:
            return False
        return True
    

    def findNurbsParent(self, node):
        parentList = cmds.listRelatives(node, parent=True)
        while parentList != None:
            for parent in parentList:
                if self.checkNurbs(parent):
                    return parent
            parentList = cmds.listRelatives(parentList, parent=True)
        return None
    

    def addToTree(self, node, dictionary):
        nurbsParent = self.findNurbsParent(node)
        if nurbsParent != None:
            if nurbsParent in dictionary:
                dictionary[nurbsParent].append(node)
            else:
                dictionary[nurbsParent] = [node]
        if node not in dictionary:
            dictionary[node] = []


    def raiseHierarchy(self, rootNode):
        hierarchyDic = {}
        self.addToTree(rootNode, hierarchyDic)
        transformDescendentsList = cmds.listRelatives(rootNode, allDescendents=True, type="transform")
        if transformDescendentsList != None:
            for node in transformDescendentsList:
                if self.checkNurbs(node):
                    self.addToTree(node, hierarchyDic)
        return hierarchyDic
    

    def findDiffInHierarchy(self, diff, newHierarchy):
        for list in newHierarchy:
            if diff in newHierarchy[list]:
                return list
        return None
    

    def checkHierarchyChange(self, originalHierarchy, newHierarchy):
        # This dictionary is in a way wich each key is the changed control and first value is a list in wich index 0 is the original Father and index 1 is the new Father. 
        hierarchyChangedCtlsSet = {}
        for key in originalHierarchy:
            if (key in newHierarchy):
                if (originalHierarchy[key] != newHierarchy[key]):
                    diffSet = set(originalHierarchy[key]) ^ set(newHierarchy[key])
                    for diff in diffSet:
                        if diff in originalHierarchy[key]:
                            lastParent = key
                        else:
                            lastParent = self.findDiffInHierarchy(diff, originalHierarchy)
                        newDad = self.findDiffInHierarchy(diff, newHierarchy)
                        hierarchyChangedCtlsSet[diff] = [lastParent, newDad]
        return hierarchyChangedCtlsSet
    

    def logInfo(self, informationDictionary):
        for ctrl in informationDictionary:
            if informationDictionary[ctrl][0] == None:
                self.messageList.append(f"{ctrl} {self.dpUIinst.lang['v065_addedSonOf']} {informationDictionary[ctrl][1]}")
            elif informationDictionary[ctrl][1] == None:
                self.messageList.append(f"{ctrl} {self.dpUIinst.lang['v066_wasRemoved']}")
            else:
                self.messageList.append(f"{ctrl} {self.dpUIinst.lang['v067_changedParent']} {informationDictionary[ctrl][0]}, new parent: {informationDictionary[ctrl][1]}")


    def compareHierarchy(self, originalHierarchy, newHierarchy):
        if originalHierarchy != newHierarchy:
            infoDic = self.checkHierarchyChange(originalHierarchy, newHierarchy)
            self.logInfo(infoDic)
            return False
        else:
            self.messageList.append(self.dpUIinst.lang['v068_matchingHierarchies'])
            return True


    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It"s in verify mode by default.
            If firstMode parameter is False, it"ll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn"t an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            rootNode = None
            
            globalCtrl = self.utils.getNodeByMessage("globalCtrl")
            # Verify if another Ctrl was sent via code to check hierarchy from.
            if objList and cmds.objExists(objList[0]) and self.checkNurbs(objList[0]):
                rootNode = objList[0]
            elif cmds.objExists(globalCtrl) and self.checkNurbs(globalCtrl):
                rootNode = globalCtrl
            else:
                self.checkedObjList.append(str(rootNode))
                self.foundIssueList.append(False)
                self.resultOkList.append(True)
                self.messageList.append(self.dpUIinst.lang['v062_globalMissing'])

            if rootNode:
                isHierarchySame = True
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    currentFileHierarchyDic = self.raiseHierarchy(rootNode)
                    lastHierarchyDic = self.importLatestJsonFile(self.getExportedList(getAny=True))
                    if lastHierarchyDic:
                        isHierarchySame = self.compareHierarchy(lastHierarchyDic, currentFileHierarchyDic)
                        self.checkedObjList.append(str(lastHierarchyDic))
                    else:
                        self.checkedObjList.append("Controls Hierarchy")
                        self.messageList.append(self.dpUIinst.lang['v063_firstHierarchy'])

                    if self.firstMode: #verify
                        if isHierarchySame:
                            self.foundIssueList.append(False)
                            self.resultOkList.append(True)
                        else:
                            self.foundIssueList.append(True)
                            self.resultOkList.append(False)
                    else: #fix
                        if cmds.file(query=True, sceneName=True) != "":
                            if lastHierarchyDic == None or not isHierarchySame:
                                self.exportDicToJsonFile(currentFileHierarchyDic)
                            self.foundIssueList.append(False)
                            self.resultOkList.append(True)
                        else:
                            self.checkedObjList.append("Scene")
                            self.foundIssueList.append(True)
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+" "+self.dpUIinst.lang['v064_hierarchy'])
                            self.messageList.append(self.dpUIinst.lang['i201_saveScene'])
                    self.maybeDone = False
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.maybeDone = True
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
