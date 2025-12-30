# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ControllerTag"
TITLE = "v073_controllerTag"
DESCRIPTION = "v074_controllerTagDesc"
ICON = "/Icons/dp_controllerTag.png"
WIKI = "07-‐-Validator#-controller-tag"

DP_CONTROLLERTAG_VERSION = 1.03


class ControllerTag(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONTROLLERTAG_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        # path to get the hierarchy json from controller hierarchy validator
        self.ioDir = "s_hierarchyIO"
        self.startName = "dpHierarchy"
    

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
                toCheckList = self.dpUIinst.ctrls.getControlList()
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                firstFixed = False
                # Get file info
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    # get last hierarchy dic, extracted from controls hierarchy json
                    self.lastHierarchyDic = self.importLatestJsonFile(self.getExportedList(getAny=True))
                for item in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    # conditional to check here
                    if not cmds.controller(item, query=True, isController=True):
                        # found issue here
                        if not firstFixed:
                            self.checkedObjList.append(item+" + controllers")
                            self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v075_missingControllerTags'])
                            break
                        else: #fix
                            try:
                                # tag as controller
                                cmds.controller(item, isController=True)
                                if self.lastHierarchyDic:
                                    self.addParentControllerTag(item)
                                if not firstFixed:
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": Controllers.")
                                    firstFixed = True
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


    def addParentControllerTag(self, item, *args):
        """ Add parent controller tag to the item, using Controls Hierarchy json to find the parent.  
        """
        parentCtrl = None
        # Find parent from last hierarchy dic
        for possibleParent, childrenList in self.lastHierarchyDic.items():
            if not childrenList:
                continue
            if item in childrenList:
                parentCtrl = possibleParent
                break
        # return if no parent found
        if not parentCtrl:
            return
        # add controller tag to parent if not already tagged
        if not cmds.controller(parentCtrl, query=True, isController=True):
            cmds.controller(parentCtrl, isController=True)
        # check if there's already a parent tag
        currentParent = cmds.controller(item, query=True, pickWalkUp=True)
        if currentParent == parentCtrl:
            return
        # controller tag command to set parent
        cmds.controller(item, parentCtrl, parent=True)