# importing libraries:
from maya import cmds
from collections import defaultdict
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "DuplicatedName"
TITLE = "v024_duplicatedName"
DESCRIPTION = "v025_duplicatedNameDesc"
ICON = "/Icons/dp_duplicatedName.png"
WIKI = "07-‐-Validator#-duplicated-name"

DP_DUPLICATEDNAME_VERSION = 1.05


class DuplicatedName(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DUPLICATEDNAME_VERSION
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
                toCheckList = cmds.ls(dag=True, long=True)
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                # Dictionary {shortName: [Full paths]}
                names = defaultdict(list)
                for obj in toCheckList:
                    short = obj.split("|")[-1]
                    names[short].append(obj)
                # Filter only duplicates
                duplicates = {k:v for k,v in names.items() if len(v) > 1}
                if duplicates:
                    for name, paths in duplicates.items():
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        # found issue here
                        self.checkedObjList.append(name)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                for path in paths:
                                    if cmds.objExists(path):
                                        renamedOkay = False
                                        for i in range(1, len(paths)+1):
                                            if not cmds.objExists(name+str(i)):
                                                cmds.rename(path, name+str(i))
                                                renamedOkay = True
                                                break
                                        if not renamedOkay:
                                            raise NameError
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+name)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+name)
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
