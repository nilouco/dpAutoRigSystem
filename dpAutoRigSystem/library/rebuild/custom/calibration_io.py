# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "CalibrationIO"
TITLE = "r041_calibrationIO"
DESCRIPTION = "r042_calibrationIODesc"
WIKI = "10-‐-Rebuilder#-calibration"



class CalibrationIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_calibrationIO"
        self.start_name = "dpCalibration"
    

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
                        if self.first_mode: #export
                            self.export_json_file(self.getCalibrationDataDic(ctrlList))
                        else: #import
                            calibrationDic = self.import_latest_json_file(self.get_exported_items())
                            if calibrationDic:
                                self.importCalibrationData(calibrationDic)
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
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def getCalibrationDataDic(self, ctrlList, *args):
        """ Processes the given controller list to collect and mount the calibration data.
            Returns the dictionary to export.
        """
        dic = {}
        self.ar.utils.setProgress(max=len(ctrlList), addOne=False, addNumber=False)
        for ctrl in ctrlList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            calibrationList = self.ar.ctrls.getListFromStringAttr(ctrl)
            if calibrationList:
                dic[ctrl] = {}
                for attr in calibrationList:
                    dic[ctrl][attr] = cmds.getAttr(ctrl+"."+attr)
        return dic


    def importCalibrationData(self, calibrationDic, *args):
        """ Import the calibration setup from the given calibration data dictionary.
        """
        self.ar.utils.setProgress(max=len(calibrationDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in calibrationDic.keys():
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            notFoundNodesList = []
            # check transformations
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in calibrationDic[item].keys():
                    if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                        # unlock attribute
                        wasLocked = cmds.getAttr(item+"."+attr, lock=True)
                        cmds.setAttr(item+"."+attr, lock=False)
                        try:
                            # set calibration value
                            cmds.setAttr(item+"."+attr, calibrationDic[item][attr])
                            # lock attribute again if it was locked
                            cmds.setAttr(item+"."+attr, lock=wasLocked)
                            if not item in wellImportedList:
                                wellImportedList.append(item)
                        except Exception as e:
                            self.fail_io(item+" - "+str(e))
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.well_done_io(self.latest_data_file)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
