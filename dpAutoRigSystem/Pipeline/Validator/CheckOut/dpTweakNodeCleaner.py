# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "TweakNodeCleaner"
TITLE = "v130_tweakNodeCleaner"
DESCRIPTION = "v131_tweakNodeCleanerDesc"
ICON = "/Icons/dp_tweakNodeCleaner.png"

DP_TWEAKNODECLEANER_VERSION = 1.1


class TweakNodeCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_TWEAKNODECLEANER_VERSION
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
                toCheckList = cmds.ls(objList, type='tweak')
            else:
                toCheckList = cmds.ls(selection=False, type='tweak') #tweakNodes
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    # check for edited control shape
                    if not self.checkEditedControlPoints(item):
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                if cmds.objExists(item):
                                    cmds.lockNode(item, lock=False)
                                    cmds.delete(item)
                                cmds.select(clear=True)
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


    def checkEditedControlPoints(self, item, *args):
        """ Check if there are edited control point in the given tweak node and return them.
        """
        if cmds.objExists(item):
            pList = cmds.getAttr(item+".plist", multiIndices=True)
            if pList:
                for idx in pList:
                    cpList = cmds.getAttr(item+".plist["+str(idx)+"].controlPoints", multiIndices=True)
                    if cpList:
                        for cp in cpList:
                            if not cmds.getAttr(item+".plist["+str(idx)+"].controlPoints["+str(cp)+"]") == [0.0, 0.0, 0.0]:
                                return True
