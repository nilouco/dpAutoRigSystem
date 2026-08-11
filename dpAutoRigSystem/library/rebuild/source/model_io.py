# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ModelIO"
TITLE = "r003_modelIO"
DESCRIPTION = "r004_modelIODesc"
WIKI = "10-‐-Rebuilder#-model"



class ModelIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_modelIO"
        self.start_name = "dpModel"
    

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
                # load alembic plugin
                if self.ar.utils.checkLoadedPlugin("AbcExport") and self.ar.utils.checkLoadedPlugin("AbcImport"):
                    self.io_path = self.get_io_path(self.io_folder)
                    if self.io_path:
                        if self.first_mode: #export
                            meshList = None
                            if objList:
                                meshList = objList
                            else:
                                meshList = self.ar.utils.filterTransformList(self.get_models_to_export(), verbose=self.ar.data.verbose, title=self.ar.data.lang[self.title])
                            if meshList:
                                self.ar.utils.setProgress(max=len(meshList), add_one=False, add_number=False)
                                constraintDataDic = self.remove_constraints(meshList)
                                self.export_alembic_file(meshList)
                                if constraintDataDic:
                                    self.import_constraint_data(constraintDataDic, False)
                            else:
                                self.maybe_done_io("Render_Grp")
                        else: #import
                            self.import_latest_alembic_file(self.get_exported_items())
                    else:
                        self.fail_io(self.ar.data.lang['r010_notFoundPath'])
                else:
                    self.fail_io(self.ar.data.lang['e018_notLoadedPlugin']+"AbcExport")
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
