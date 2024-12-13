# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = 'OverrideCleaner'
TITLE = 'v090_overrideCleaner'
DESCRIPTION = 'v091_overrideCleanerDesc'
ICON = '/Icons/dp_overrideCleaner.png'

DP_OVERRIDECLEANER_VERSION = 1.2


class OverrideCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs['CLASS_NAME'] = CLASS_NAME
        kwargs['TITLE'] = TITLE
        kwargs['DESCRIPTION'] = DESCRIPTION
        kwargs['ICON'] = ICON
        self.version = DP_OVERRIDECLEANER_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)


    def runAction(self, firstMode=True, objList=None, *args):
        ''' Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        '''
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
        nodeList = cmds.ls(selection=False)
        if objList:
            nodeList = objList
        if nodeList:
            overridedList = []
            self.utils.setProgress(max=len(nodeList), addOne=False, addNumber=False)
            for item in nodeList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if cmds.objExists(item+".overrideEnabled"):
                    if cmds.getAttr(item+".overrideEnabled") == 1:
                        overridedList.append(item)
            # conditional to check here
            if overridedList:
                for item in overridedList:
                    self.checkedObjList.append(item)
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            cmds.lockNode(item, lock=False, lockUnpublished=False)
                            cmds.setAttr(item+".overrideEnabled", lock=False)
                            cmds.setAttr(item+".overrideEnabled", 0)
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
