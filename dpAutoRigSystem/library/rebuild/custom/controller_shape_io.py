# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ControllerShapeIO"
TITLE = "r014_controllerShapeIO"
DESCRIPTION = "r015_controllerShapeIODesc"
WIKI = "10-‐-Rebuilder#-controller-shape"



class ControllerShapeIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_controlShapeIO"
        self.startName = "dpControlShape"
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.checkAssetContext():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    ctrlList = None
                    if objList:
                        ctrlList = objList
                    else:
                        ctrlList = self.ar.ctrls.getControlList()
                    if ctrlList:
                        self.ar.utils.setProgress(max=len(ctrlList), addOne=False, addNumber=False)
                        if self.first_mode: #export
                            try:
                                self.ar.pipeliner.makeDirIfNotExists(self.io_path)
                                ctrlFileName = self.io_path+"/"+self.startName+"_"+self.ar.pipeliner.pipeData['currentFileName']+".ma"
                                self.ar.ctrls.exportShape(ctrlList, ctrlFileName, ui=False, verbose=True)
                                self.well_done_io(ctrlFileName)
                            except Exception as e:
                                self.fail_io(', '.join(ctrlList)+": "+str(e))
                        else: #import
                            exportedList = self.get_exported_items()
                            if exportedList:
                                try:
                                    exportedList.sort()
                                    ctrlsToImport = self.io_path+"/"+exportedList[-1]
                                    self.ar.ctrls.importShape(ctrlList, ctrlsToImport, ui=False, verbose=True)
                                    self.well_done_io(exportedList[-1])
                                except Exception as e:
                                    self.fail_io(exportedList[-1]+": "+str(e))
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.maybe_done_io("Ctrls_Grp")
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        self.refresh_view()
        return self.log_data
