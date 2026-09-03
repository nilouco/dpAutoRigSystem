# importing libraries:
from maya import cmds
import json
from ....library.base import action
from ....library.tool import rivet
from importlib import reload

# global variables to this module:
CLASS_NAME = "RivetIO"
TITLE = "r039_rivetIO"
DESCRIPTION = "r040_rivetIODesc"
WIKI = "10-‐-Rebuilder#-rivet"



class RivetIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(rivet)
        self.rivet = rivet.Rivet(self.ar)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_rivetIO"
        self.start_name = "dpRivet"
    

    def run_action(self, first_mode=True, inputs=None, *args):
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
                    if self.first_mode: #export
                        nets = None
                        if inputs:
                            nets = inputs
                        else:
                            nets = self.ar.utils.get_network_by_attr("dpRivetNet")
                        if nets:
                            self.export_json_file(self.get_rivet_data(nets))
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
                            cmds.select(clear=True)
                    else: #import
                        rivet_data = self.import_latest_json_file(self.get_exported_items())
                        if rivet_data:
                            self.import_rivet(rivet_data)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                        cmds.select(clear=True)
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


    def get_rivet_data(self, nets):
        """ Processes the given rivet network list and mount the right info pack to rebuild the module.
            Returns the dictionary to export.
        """
        result_data = {}
        self.ar.ui_manager.set_progress(max=len(nets), add_one=False, add_number=False)
        i = 0
        for n, net in enumerate(nets):
            if self.ar.data.verbose:
                self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            # mount a rivet data dictionary
            if cmds.objExists(net+".rivetData"):
                data = json.loads(cmds.getAttr(net+".rivetData"))
                add_it = True
                if n > 0:
                    for x in range(0, i):
                        if data["itemNode"] in result_data[x]["itemList"]:
                            add_it = False
                            break
                if add_it:
                    result_data[i] = data
                    i += 1
        return result_data


    def import_rivet(self, rivet_data):
        """ Import rivet data creating new instances with exported attribute values.
        """
        well_imported = True
        self.ar.ui_manager.set_progress(max=len(rivet_data.keys()), add_one=False, add_number=False)
        for net in rivet_data.keys():
            try:
                net_data = rivet_data[net]
                self.ar.ui_manager.set_progress(self.ar.data.lang[self.title]+': '+net_data['geoToAttach'])
                old_ui_state = self.ar.data.ui_state
                self.ar.data.ui_state = False
                # recreate rivet:
                self.rivet.deformerToUse = net_data['deformerToUse']
                rivets = self.rivet.create_rivet(net_data['geoToAttach'], net_data['uvSetName'], net_data['itemList'], net_data['attachTranslate'], net_data['attachRotate'], net_data['addFatherGrp'], net_data['addInvert'], net_data['invT'], net_data['invR'], net_data['faceToRivet'], net_data['rivetGrpName'], net_data['askComponent'], net_data['useOffset'], net_data['reuseFaceToRivet'])
                self.ar.data.ui_state = old_ui_state
                if not rivets:
                    well_imported = False
                    self.fail_io(net+": "+self.ar.data.lang['r032_notImportedData'])
            except Exception as e:
                well_imported = False
                self.fail_io(net+": "+str(e))
                break
        if well_imported:
            self.well_done_io(self.latest_data_file)
