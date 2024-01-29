# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ControlShapeIO"
TITLE = "r014_controlShapeIO"
DESCRIPTION = "r015_controlShapeIODesc"
ICON = "/Icons/dp_controlShapeIO.png"

MODULES = "Modules"

DP_CONTROLSHAPEIO_VERSION = 1.0


class ControlShapeIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONTROLSHAPEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_controlShapeIO"
        self.startName = "dpControlShape"
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
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
        # --- rebuilder code --- beginning
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                ctrlList = None
                if objList:
                    ctrlList = objList
                else:
                    ctrlList = self.dpUIinst.ctrls.getControlList()
                if ctrlList:
                    if self.firstMode: #export
                        try:
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            ctrlFileName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".ma"
                            self.dpUIinst.ctrls.exportShape(ctrlList, ctrlFileName)
                            self.wellDoneIO(', '.join(ctrlList))
                        except:
                            self.notWorkedWellIO(', '.join(ctrlList))
                    else: #import
                        exportedList = self.getExportedList()
                        if exportedList:
                            try:
                                self.dpUIinst.rigAll(rebuilding=True)
                                exportedList.sort()
                                ctrlsToImport = self.ioPath+"/"+exportedList[-1]
                                self.dpUIinst.ctrls.importShape(ctrlList, ctrlsToImport)
                                self.wellDoneIO(exportedList[-1])
                            except:
                                self.notWorkedWellIO(exportedList[-1])
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO("Ctrls_Grp")
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        cmds.refresh()
        return self.dataLogDic
