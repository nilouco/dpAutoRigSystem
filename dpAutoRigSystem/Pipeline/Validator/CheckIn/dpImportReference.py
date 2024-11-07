# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ImportReference"
TITLE = "v042_importReference"
DESCRIPTION = "v043_importReferenceDesc"
ICON = "/Icons/dp_importReference.png"

DP_IMPORTREFERENCE_VERSION = 1.3


class ImportReference(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_IMPORTREFERENCE_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
    

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
            referenceList = objList
        else:
            referenceList = cmds.file(query=True, reference=True)
        if referenceList:
            self.utils.setProgress(max=len(referenceList), addOne=False, addNumber=False)
            for reference in referenceList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                self.checkedObjList.append(reference)
                self.foundIssueList.append(True)
            if self.firstMode:
                self.resultOkList.append(False)
            else: #fix
                self.importReference()
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def importReference(self, *args):
        """ This function will import objects from referenced file.
        """
        refList = cmds.file(query=True, reference=True)
        if refList:
            for ref in refList:
                topRef = cmds.referenceQuery(ref, referenceNode=True, topReference=True)
                if cmds.objExists(topRef):
                    # Only import it if it's loaded, otherwise it would throw an error.
                    if cmds.referenceQuery(ref, isLoaded=True):
                        try:
                            cmds.file(ref, importReference=True)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+ref)
                            self.importReference()
                            break
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+ref)
                    else:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+ref)
