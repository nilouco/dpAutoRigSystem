# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ControllerTag"
TITLE = "v073_controllerTag"
DESCRIPTION = "v074_controllerTagDesc"
ICON = "/Icons/dp_controllerTag.png"
WIKI = "07-‐-Validator#-controller-tag"

DP_CONTROLLERTAG_VERSION = 1.04


class ControllerTag(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONTROLLERTAG_VERSION
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
                toCheckList = self.dpUIinst.ctrls.getControlList()
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    if not "controlID" in cmds.listAttr(item):
                        continue
                    if not cmds.getAttr(item+".controlID") == "id_092_Correctives":
                        if self.firstMode:
                            # conditional to check here
                            if not cmds.controller(item, query=True, isController=True):
                                self.checkedObjList.append(item+" + controllers")
                                self.foundIssueList.append(True)
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v075_missingControllerTags'])
                                break
                        else: #fix
                            try:
                                # tag as controller
                                cmds.controller(item, isController=True)
                                result = self.addParentControllerTag(item)
                                self.resultOkList.append(True)
                                if result:
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+result)
                                else:
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


    def addParentControllerTag(self, item, *args):
        """ Add parent controller tag to the given item.
        """
        if "parentTag" in cmds.listAttr(item):
            parentCtrlList = cmds.listConnections(item+".parentTag", source=True, destination=False)
            if parentCtrlList:
                cmds.controller(item, parentCtrlList[0], parent=True)
                return ("Tagged parent = "+item+" --> "+parentCtrlList[0])
