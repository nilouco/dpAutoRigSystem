# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = 'UnlockAttributes'
TITLE = 'v092_unlockAttributes'
DESCRIPTION = 'v093_unlockAttributesDesc'
ICON = '/Icons/dp_unlockAttributes.png'

DP_UNLOCKATTRIBUTES_VERSION = 1.2


class UnlockAttributes(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs['CLASS_NAME'] = CLASS_NAME
        kwargs['TITLE'] = TITLE
        kwargs['DESCRIPTION'] = DESCRIPTION
        kwargs['ICON'] = ICON
        self.version = DP_UNLOCKATTRIBUTES_VERSION
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
        if not self.utils.getAllGrp():
            if not self.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    nodeList = cmds.ls(selection=False)
                    if objList:
                        nodeList = objList
                    if nodeList:
                        lockedAttrDic = {}
                        self.utils.setProgress(max=len(nodeList), addOne=False, addNumber=False)
                        for item in nodeList:
                            self.utils.setProgress(self.dpUIinst.lang[self.title])
                            lockedAttrList = cmds.listAttr(item, locked=True)
                            if lockedAttrList:
                                lockedAttrDic[item] = lockedAttrList
                        # conditional to check here
                        if lockedAttrDic:
                            for item in lockedAttrDic.keys():
                                self.checkedObjList.append(item)
                                self.foundIssueList.append(True)
                                if self.firstMode:
                                    self.resultOkList.append(False)
                                else: #fix
                                    try:
                                        cmds.lockNode(item, lock=False, lockUnpublished=False)
                                        for attr in lockedAttrDic[item]:
                                            cmds.setAttr(item+"."+attr, lock=False)
                                        self.resultOkList.append(True)
                                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+" = "+str(lockedAttrDic[item]))
                                    except:
                                        self.resultOkList.append(False)
                                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item+" = "+attr)
                    else:
                        self.notFoundNodes()
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v100_cantExistsGuides'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
