# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
import json
import os
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "CtrlsHierarchy"
TITLE = "v060_expCtrlHierarchy"
DESCRIPTION = "v061_expCtrlHierarchyDesc"
ICON = "/Icons/dp_controlsHierarchy.png"

dpCtrlsHierarchy_Version = 1.0

class CtrlsHierarchy(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)

    def checkNurbs(self, transform):
        shapeList = cmds.listRelatives(transform, shapes=True)
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
                self.messageList.append(f"{ctrl} was added to the hierarchy, sun of {informationDictionary[ctrl][1]}")
            elif informationDictionary[ctrl][1] == None:
                self.messageList.append(f"{ctrl} was removed.")
            else:
                self.messageList.append(f"{ctrl} changed hierarchy, last parent: {informationDictionary[ctrl][0]}, new parent: {informationDictionary[ctrl][1]}")

    def compareHierarchy(self, originalHierarchy, newHierarchy):
        if originalHierarchy != newHierarchy:
            infoDic = self.checkHierarchyChange(originalHierarchy, newHierarchy)
            self.logInfo(infoDic)
            return False
        else:
            self.messageList.append("Matching hierarchys.")
            return True

    def changeIntVersionToString(self, int):
        stringVersion = str(int)
        if len(stringVersion) < 3:
            stringVersion = stringVersion.zfill(3)
        return f"_h{stringVersion}"

    def lookForLastHierarchy(self):
        lastHierarchyFilePath = None
        currentPath = cmds.file(query=True, sceneName=True)
        dpHierarchyPath = currentPath[:currentPath.rfind("/")+1]+"dpData/dpHierarchy"
        if os.path.exists(dpHierarchyPath):
            if self.dpTeamFile:
                lastHierarchyFilePath = f"{dpHierarchyPath}/{self.currentFileName}.json"
            else:
                lastFileVersion = self.findLastFileVersion(dpHierarchyPath)
                if lastFileVersion:
                    lastFileVersionString = self.changeIntVersionToString(lastFileVersion)
                    lastHierarchyFilePath = f"{dpHierarchyPath}/{self.currentFileName}{lastFileVersionString}.json"
        return lastHierarchyFilePath
    
    def retrieveDicFromFile(self, filePath):
        with open(filePath) as json_file:
            prevHierarchy = json.load(json_file)
        return prevHierarchy
    
    def findLastFileVersion(self, filesPath):
        lastFileVersion = None
        filesList = os.listdir(filesPath)
        if len(filesList) > 0:
            lastBiggerVersion = 0
            for file in filesList:
                length = len(file)
                if self.currentFileName in file and file[length - 5:] == ".json":
                    thisFileVersion = int(file[file.rfind("_h")+2:-5])
                    if thisFileVersion > lastBiggerVersion:
                            lastBiggerVersion = thisFileVersion
            lastFileVersion = lastBiggerVersion
        return lastFileVersion

    def exportCtlrsHierarchyToFile(self, dicToJson):
        currentPath = cmds.file(query=True, sceneName=True)
        dpHierarchyPath = currentPath[:currentPath.rfind("/")+1]+"dpData/dpHierarchy"
        finalSaveFilePath = f"{dpHierarchyPath}/{self.currentFileName}_h001.json"
        if os.path.exists(dpHierarchyPath):
            if self.dpTeamFile:
                finalSaveFilePath = f"{dpHierarchyPath}/{self.currentFileName}.json"
            else:
                lastFileVersion = self.findLastFileVersion(dpHierarchyPath)
                if lastFileVersion:
                    lastFileVersionString = self.changeIntVersionToString(lastFileVersion+1)
                    finalSaveFilePath = f"{dpHierarchyPath}/{self.currentFileName}{lastFileVersionString}.json"
        else:
            os.mkdir(dpHierarchyPath)
        with open (finalSaveFilePath, "w") as json_file:
            json.dump(dicToJson, json_file)
        self.messageList.append(f"File exported: {finalSaveFilePath}")
    
    def checkIfdpTeam(self):
        length = len(self.currentFileName)
        return self.currentFileName[length-5:-3] == "_v"

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It"s in verify mode by default.
            If verifyMode parameter is False, it"ll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn"t an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.startValidation()
        
        # ---
        # --- validator code --- beginning

        self.currentFileName = cmds.file(query=True, sceneName=True, shortName=True)[:-3]
        rootNode = None

        self.dpTeamFile = self.checkIfdpTeam()
        if self.dpTeamFile:
            self.currentFileName = self.currentFileName.replace("_v", "_h")
        
        # Verify if another Ctrl was sent via code to check hierarchy from.
        if objList and cmds.objExists(objList[0]) and self.checkNurbs(objList[0]):
            rootNode = objList[0]
        elif cmds.objExists("Global_Ctrl") and self.checkNurbs("Global_Ctrl"):
            rootNode = "Global_Ctrl"
        else:
            self.checkedObjList.append(str(rootNode))
            self.foundIssueList.append(False)
            self.resultOkList.append(True)
            self.messageList.append("There is no Global_Ctrl")
            self.finishValidation()
            return self.dataLogDic

        currentFileHierarchyDic = self.raiseHierarchy(rootNode)
        lastHierarchyFilePath = self.lookForLastHierarchy()
        isHierarchySame = True

        if lastHierarchyFilePath:
            lastHierarchyDic = self.retrieveDicFromFile(lastHierarchyFilePath)
            isHierarchySame = self.compareHierarchy(lastHierarchyDic, currentFileHierarchyDic)
            self.checkedObjList.append(lastHierarchyFilePath)
        else:
            self.checkedObjList.append("Ctrls Hierarchy")
            self.messageList.append("This is the first hierarchy version. OK")

        if self.verifyMode:
            if isHierarchySame:
                self.foundIssueList.append(False)
                self.resultOkList.append(True)
            else:
                self.foundIssueList.append(True)
                self.resultOkList.append(False)
        else:
            if lastHierarchyFilePath == None:
                self.exportCtlrsHierarchyToFile(currentFileHierarchyDic)
            elif not isHierarchySame:
                self.exportCtlrsHierarchyToFile(currentFileHierarchyDic)
            self.foundIssueList.append(False)
            self.resultOkList.append(True)

        # --- validator code --- end
        # ---

        # finishing
        self.finishValidation()
        return self.dataLogDic


    def startValidation(self, *args):
        """ Procedures to start the validation cleaning old data.
        """
        dpBaseValidatorClass.ValidatorStartClass.cleanUpToStart(self)


    def finishValidation(self, *args):
        """ Call main base methods to finish the validation of this class.
        """
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
        dpBaseValidatorClass.ValidatorStartClass.reportLog(self)
        dpBaseValidatorClass.ValidatorStartClass.endProgressBar(self)