# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ...Modules.Library import dpUtils
from importlib import reload
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
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.startValidation()
        
        # ---
        # --- validator code --- beginning

        # Verify if another Ctrl was sent via code to check hierarchy from.
        if objList:
            rootCtrl = objList[0]
        elif cmds.objExists('Root_Ctrl'):
            rootCtrl = 'Root_Ctrl'
        else:
            print('EXIT NO ROOT')

        hierarchyDictionary = self.raiseHierarchy(rootCtrl)

        dpUtils.exportLogDicToJson(hierarchyDictionary)
            
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
        if cmds.objExists(rootNode) and self.checkNurbs(rootNode):
            self.addToTree(rootNode, hierarchyDic)
            transformDescendentsList = cmds.listRelatives(rootNode, allDescendents=True, type="transform")
            if transformDescendentsList != None:
                for node in transformDescendentsList:
                    if self.checkNurbs(node):
                        self.addToTree(node, hierarchyDic)
        else:
            print('Maybe implement?')
        return hierarchyDic