# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Outliner"
TITLE = "v076_outliner"
DESCRIPTION = "v077_outlinerDesc"
WIKI = "07-‐-Validator#-outliner-cleaner"



class Outliner(action.BaseAction):
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
            hiddenList = [self.ar.data.temp_grp, self.ar.data.guide_mirror_grp]
            
            
            #TODO = get node by attribute (dpTemp)


            if not objList:
                objList = cmds.ls(selection=False, type="transform")
            if objList:
                self.ar.utils.setProgress(max=len(hiddenList), addOne=False, addNumber=False)
                for item in hiddenList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if item in objList:
                        self.checkedObjList.append(item)
                        if cmds.objExists(item):
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:    
                                    cmds.delete(item)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.ar.data.lang['v004_fixed']+": "+item)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+item)
                        else:
                            self.foundIssueList.append(False)
                            self.resultOkList.append(True)
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
