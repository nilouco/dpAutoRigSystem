# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ...Modules.Library import dpUtils
from importlib import reload
import json
import os
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "CheckCtrlsHierarchy"
TITLE = "v054_expCtrlHierarchy"
DESCRIPTION = "v055_expCtrlHierarchyDesc"
ICON = "/Icons/dp_CheckCtrlsHierarchy.png"

dpCheckCtrlsHierarchy_Version = 1.0

class CheckCtrlsHierarchy(dpBaseValidatorClass.ValidatorStartClass):
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
                print(f"{ctrl} foi adicionado a hierarquia, filho do {informationDictionary[ctrl][1]}")
            elif informationDictionary[ctrl][1] == None:
                print(f"{ctrl} foi excluído.")
            else:
                print(f"{ctrl} mudou de hierarquia, onde seu antigo pai era {informationDictionary[ctrl][0]}, e o novo pai é {informationDictionary[ctrl][1]}")

    def compareHierarchy(self, originalHierarchy, newHierarchy):
        if originalHierarchy != newHierarchy:
            infoDic = self.checkHierarchyChange(originalHierarchy, newHierarchy)
            self.logInfo(infoDic)
        else:
            print("Hierarquias iguais")

    def lookForLastHierarchy(self):
        lastHyerarchyFilePath = None
        currentFileName = cmds.file(query=True, sceneName=True, shortName=True)
        currentPath = cmds.file(query=True, sceneName=True)
        dpHyerarchyPath = currentPath[:currentPath.rfind("/")+1]+"dpData/dpHyerarchy"
        if os.path.exists(dpHyerarchyPath):
            filesList = os.listdir(dpHyerarchyPath)
            if len(filesList) > 0:
                lastBiggerVersion = 0
                for idx, file in enumerate(filesList):
                    length = len(file)
                    if currentFileName[:-3] in file and file[length - 5:] == ".json":
                        thisFileVersion = int(file[file.rfind("_v")+2:-5])
                        if thisFileVersion > lastBiggerVersion:
                            lastBiggerVersion = thisFileVersion
                            fileIndex = idx
                            lastHyerarchyFilePath = f"{dpHyerarchyPath}/{filesList[fileIndex]}"
        return lastHyerarchyFilePath
    
    def retrieveDicFromFile(self, filePath):
        with open(filePath) as json_file:
            prevHyerarchy = json.load(json_file)
        return prevHyerarchy

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

        rootCtrl = None
        # Verify if another Ctrl was sent via code to check hierarchy from.
        if objList and cmds.objExists(objList[0]) and self.checkNurbs(objList[0]):
            rootCtrl = objList[0]
        elif cmds.objExists("Root_Ctrl") and self.checkNurbs("Root_Ctrl"):
            rootCtrl = "Root_Ctrl"
        else:
            self.foundIssueList.append(True)
            self.resultOkList.append(False)
            self.messageList("Nao existe Root, chame o validador via código e passe o controle raiz em uma lista [Raiz_Ctrl]")
            self.finishValidation()
            return self.dataLogDic

        currentFileHierarchyDic = self.raiseHierarchy(rootCtrl)
        lastHierarchyFilePath = self.lookForLastHierarchy()
        if lastHierarchyFilePath:
            lastHierarchyDic = self.retrieveDicFromFile(lastHierarchyFilePath)
            self.compareHierarchy(lastHierarchyDic, currentFileHierarchyDic)
        else:
            print("Nao tem hierarquia para comparar")

            
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