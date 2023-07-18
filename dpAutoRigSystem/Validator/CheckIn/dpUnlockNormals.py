# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass

# global variables to this module:
CLASS_NAME = "UnlockNormals"
TITLE = "v078_unlockNormals"
DESCRIPTION = "v079_unlockNormalsDesc"
ICON = "/Icons/dp_unlockNormals.png"

DP_UNLOCKNORMALS_VERSION = 1.1


class UnlockNormals(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        if objList:
            allMeshList = objList
        else:
            allMeshList = cmds.ls(selection=False, type='mesh')
        if allMeshList:
            progressAmount = 0
            maxProcess = len(allMeshList)
            for obj in allMeshList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                if cmds.objExists(obj):
                    lockedList = cmds.polyNormalPerVertex(obj+".vtx[*]", query=True, freezeNormal=True)
                    # check if there's any locked normal
                    if True in lockedList:
                        self.checkedObjList.append(obj)
                        self.foundIssueList.append(True)
                        if self.verifyMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.polyNormalPerVertex(obj+".vtx[*]", unFreezeNormal=True)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+obj)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+obj)
    
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic