# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "NgSkinToolsCleaner"
TITLE = "v026_ngskintoolsCleaner"
DESCRIPTION = "v027_ngskintoolsCleanerDesc"
ICON = "/Icons/dp_ngskintoolsCleaner.png"

DP_NGSKINTOOLSCLEANER_VERSION = 1.2


class NgSkinToolsCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_NGSKINTOOLSCLEANER_VERSION
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
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, type='ngst2SkinLayerData')
        if toCheckList:
            self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
            for item in toCheckList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                # conditional to check here
                self.checkedObjList.append(item)
                self.foundIssueList.append(True)
                if self.firstMode:
                    self.resultOkList.append(False)
                else: #fix
                    try:
                        cmds.delete(item)
                        cmds.select(clear=True)
                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                    except:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
