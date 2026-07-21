# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "JointEnd"
TITLE = "v111_jointEnd"
DESCRIPTION = "v112_jointEndDesc"
WIKI = "07-‐-Validator#-joint-end-cleaner"



class JointEnd(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

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
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                # list joint ends
                jEndList = [j for j in toCheckList if self.ar.data.joint_end_attr in cmds.listAttr(j)] #by attribute
                jEndList.extend([j for j in cmds.ls(selection=False, type="joint") if j.endswith(self.ar.data.joint_end_attr)]) #by suffix
                if jEndList:
                    # check connection with skinCluster to avoid delete it and crash the setup
                    jEndList = list(set(jEndList)-set(self.ar.skin.getSkinnedJointList())) #remove duplicated and skinned joints
                    jEndList = [j for j in jEndList if not cmds.listRelatives(j, children=True)] #remove if there are children
                    if jEndList:
                        jEndList.sort()
                        for item in jEndList:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            self.checkedObjList.append(item)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    cmds.lockNode(item, lock=False)
                                    cmds.delete(item)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.ar.data.lang['v004_fixed']+": "+item)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    else:
                        self.notFoundNodes()
                else:
                    self.notFoundNodes()
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
