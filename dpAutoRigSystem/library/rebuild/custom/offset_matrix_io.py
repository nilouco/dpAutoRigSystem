# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "OffsetMatrixIO"
TITLE = "r061_offsetMatrixIO"
DESCRIPTION = "r062_offsetMatrixIODesc"
WIKI = "10-‐-Rebuilder#-offset-matrix"



class OffsetMatrixIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_offsetMatrixIO"
        self.start_name = "dpOffsetMatrix"
        self.offsetMatrixAttr = "offsetParentMatrix"
    

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
            if self.ar.pipeliner.check_asset_context():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    nodes = None
                    if objList:
                        nodes = objList
                    else:
                        nodes = cmds.ls(selection=False, type="transform")
                    if nodes:
                        if self.first_mode: #export
                            toExportDataDic = self.getOffsetMatrixDataDic(nodes)
                            self.export_json_file(toExportDataDic)
                        else: #import
                            toImportDic = self.import_latest_json_file(self.get_exported_items())
                            if toImportDic:
                                self.importOffsetMatrixData(toImportDic)
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
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


    def getOffsetMatrixDataDic(self, items, *args):
        """ Processes the given list to collect the info about their parent offset matrix connections to rebuild.
            Returns a dictionary to export.
        """
        dic = {}
        self.ar.utils.setProgress(max=len(items), addOne=False, addNumber=False)
        for item in items:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                inPlugList = cmds.listConnections(item+"."+self.offsetMatrixAttr, source=True, destination=False, plugs=True)
                if inPlugList:
                    dic[item] = inPlugList[0]
        return dic


    def importOffsetMatrixData(self, connectDic, *args):
        """ Import connection data.
            Check if need to create an unitConversion node and set its conversionFactor value.
            Only redo the connection if it doesn't exists yet.
        """
        self.ar.utils.setProgress(max=len(connectDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in connectDic.keys():
            notFoundNodesList = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                omAttr = item+"."+self.offsetMatrixAttr
                if not cmds.listConnections(omAttr, plugs=True, source=True, destination=False):
                    isLocked = cmds.getAttr(omAttr, lock=True)
                    cmds.setAttr(omAttr, lock=False)
                    cmds.connectAttr(connectDic[item]+"[0]", omAttr, force=True)
                    if isLocked:
                        cmds.setAttr(omAttr, lock=True)
                if not item in wellImportedList:
                    wellImportedList.append(item)
            else:
                notFoundNodesList.append(item+"."+self.offsetMatrixAttr)
        if notFoundNodesList:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
        elif wellImportedList:
            self.well_done_io(self.latest_data_file)
