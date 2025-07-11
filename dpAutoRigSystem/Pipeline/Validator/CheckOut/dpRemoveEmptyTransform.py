# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "RemoveEmptyTransform"
TITLE = "v138_removeEmptyTransform"
DESCRIPTION = "v139_removeEmptyTransformDesc"
ICON = "/Icons/dp_removeEmptyTransform.png"

DP_REMOVEEMPTYTRANSFORM_VERSION = 1.0


class RemoveEmptyTransform(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_REMOVEEMPTYTRANSFORM_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
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
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList =  cmds.ls(selection=False, long=True, type="transform") #list all transforms in the scene
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                emptyTransformList = self.filterEmptyTransformList(toCheckList)
                 # conditional to check here
                if emptyTransformList:
                    for item in emptyTransformList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        self.checkedObjList.append(self.utils.getShortName(item))
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.lockNode(item, lock=False)
                                cmds.delete(item)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
            else:
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
    
    def filterEmptyTransformList(self, transformList=None, *args):
        """ Filter the transform list to remove those without children or connections.
            Returns a list of transforms that are empty.
        """
        filteredList = self.utils.filterTransformList(transformList, verbose=self.verbose, title=self.dpUIinst.lang[self.title])
        filteredList = self.reorderList(filteredList) #self.reorderList(filteredList)
        emptyTransforms = []
        for transform in filteredList:
            if not cmds.listRelatives(transform, children=True, fullPath=True) and not cmds.listConnections(transform):
                emptyTransforms.append(transform)
        return emptyTransforms


    def reorderList(self, itemList, *args):
        """ Returns a list with high to low counting of '|' in the item list given. That means a descending order.
        """
        return sorted(itemList, key = lambda x: x.count("|"), reverse=False)