# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "InputOrderIO"
TITLE = "r035_inputOrderIO"
DESCRIPTION = "r036_inputOrderIODesc"
WIKI = "10-‐-Rebuilder#-input-order"



class InputOrderIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_inputOrderIO"
        self.startName = "dpInputOrder"
    

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
                    if self.first_mode: #export
                        deformedList = None
                        if objList:
                            deformedList = objList
                        else:
                            deformedList = self.ar.skin.getDeformedItemList(deformerTypeList=self.ar.skin.getAllDeformerTypeList(), ignoreAttr=self.ar.skin.ignoreSkinningAttr)
                        if deformedList:
                            self.exportDicToJsonFile(self.getOrderDataDic(deformedList))
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" - meshes")
                    else: #import
                        orderDic = self.importLatestJsonFile(self.get_exported_items())
                        if orderDic:
                            self.importInputOrder(orderDic)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
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


    def getOrderDataDic(self, deformedList, *args):
        """ Return the deformer order data dictionary to export.
        """
        orderDic = {}
        self.ar.utils.setProgress(max=len(deformedList), addOne=False, addNumber=False)
        for item in deformedList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            orderDic[item] = self.ar.skin.getOrderList(item)
        return orderDic
    

    def importInputOrder(self, orderDic, *args):
        """ Import the input order data from given dictionary.
        """
        self.ar.utils.setProgress(max=len(orderDic.keys()), addOne=False, addNumber=False)
        wellImported = True
        toImportList, notFoundMeshList, = [], []
        for item in orderDic.keys():
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                toImportList.append(item)
            else:
                notFoundMeshList.append(item)
        if toImportList:
            warningStatus = cmds.scriptEditorInfo(query=True, suppressWarnings=True)
            cmds.scriptEditorInfo(edit=True, suppressWarnings=True)
            for item in toImportList:
                try:
                    # reorder deformers
                    deformerList = orderDic[item]
                    if deformerList:
                        if len(deformerList) > 1:
                            self.ar.skin.setOrderList(item, deformerList)
                except Exception as e:
                    wellImported = False
                    print(e)
                    self.fail_io(self.latestDataFile)
            cmds.scriptEditorInfo(edit=True, suppressWarnings=warningStatus)
            if wellImported:
                self.well_done_io(self.latestDataFile)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
