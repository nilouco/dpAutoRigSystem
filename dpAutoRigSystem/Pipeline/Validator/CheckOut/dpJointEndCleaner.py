# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "JointEndCleaner"
TITLE = "v111_jointEndCleaner"
DESCRIPTION = "v112_jointEndCleanerDesc"
ICON = "/Icons/dp_jointEndCleaner.png"

DP_JOINTENDCLEANER_VERSION = 1.01


class JointEndCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_JOINTENDCLEANER_VERSION
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
                toCheckList = cmds.ls(selection=False, type="joint")
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                # list joint ends
                jEndList = [j for j in toCheckList if self.dpUIinst.jointEndAttr in cmds.listAttr(j)] #by attribute
                jEndList.extend([j for j in cmds.ls(selection=False, type="joint") if j.endswith(self.dpUIinst.jointEndAttr)]) #by suffix
                if jEndList:
                    # check connection with skinCluster to avoid delete it and crash the setup
                    jEndList = list(set(jEndList)-set(self.dpUIinst.skin.getSkinnedJointList())) #remove duplicated and skinned joints
                    jEndList = [j for j in jEndList if not cmds.listRelatives(j, children=True)] #remove if there are children
                    if jEndList:
                        jEndList.sort()
                        for item in jEndList:
                            self.utils.setProgress(self.dpUIinst.lang[self.title])
                            self.checkedObjList.append(item)
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
                    self.notFoundNodes()
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
