# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "BrokenRivet"
TITLE = "v107_passthroughAttributes"
DESCRIPTION = "v108_passthroughAttributesDesc"
ICON = "/Icons/dp_passthroughAttributes.png"

DP_BROKEN_RIVET = 1.0


class BrokenRivet(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_BROKEN_RIVET
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)

    def isFollicleAtOrigin(self, follicle_shape):
        
        parentList = cmds.listRelatives(follicle_shape, parent=True)
        if not parentList:
            return False
        follicle_transform = parentList[0]
        pos = cmds.xform(follicle_transform, query=True, translation=True, worldSpace=True)
        return pos == [0.0, 0.0, 0.0]
    

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
                toCheckList = cmds.ls(type='follicle')
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for follicle in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    if self.isFollicleAtOrigin(follicle):
                        self.checkedObjList.append(follicle)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                parentList = cmds.listRelatives(follicle, parent=True)
                                follicleTransform = parentList[0]
                                if not follicleTransform:
                                    raise ValueError("Follicle has no transform.")
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+follicle)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+follicle)
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
