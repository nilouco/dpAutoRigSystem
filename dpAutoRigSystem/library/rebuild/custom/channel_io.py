# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ChannelIO"
TITLE = "r064_channelIO"
DESCRIPTION = "r065_channelIODesc"
WIKI = "10-‐-Rebuilder#-channel"



class ChannelIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_channelIO"
        self.start_name = "dpChannel"
    

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
                    items = None
                    if inputs:
                        items = inputs
                    else:
                        items = cmds.ls(selection=False, type="transform")
                    if items:
                        if self.first_mode: #export
                            self.export_json_file(self.get_channel_data(items))
                        else: #import
                            attr_data = self.import_latest_json_file(self.get_exported_items())
                            if attr_data:
                                self.import_channel_data(attr_data)
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


    def get_channel_data(self, items):
        """ Processes the given item list to collect and mount the tranform attributes data.
            Returns the dictionary to export.
        """
        data = {}
        self.ar.utils.set_progress(max=len(items), add_one=False, add_number=False)
        for item in items:
            self.ar.utils.set_progress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                data[item] = {}
                for attr in self.ar.data.transform_attrs:
                    data[item][attr] = {
                                        "locked" : cmds.getAttr(item+"."+attr, lock=True),
                                        "keyable" : cmds.getAttr(item+"."+attr, keyable=True),
                                        "channelBox" : cmds.getAttr(item+"."+attr, channelBox=True)
                                        }
        return data


    def import_channel_data(self, attr_data):
        """ Import tranform attributes states from exported dictionary.
            Just set them as locked, hidden, non keyable or not.
        """
        self.ar.utils.set_progress(max=len(attr_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in attr_data.keys():
            not_found_nodes = []
            self.ar.utils.set_progress(self.ar.data.lang[self.title])
            # check attributes
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in self.ar.data.transform_attrs:
                    try:
                        cmds.setAttr(item+"."+attr, keyable=attr_data[item][attr]['keyable'])
                        if not attr_data[item][attr]['keyable']:
                            cmds.setAttr(item+"."+attr, channelBox=attr_data[item][attr]['channelBox'])
                        cmds.setAttr(item+"."+attr, lock=attr_data[item][attr]['locked'])
                        if not item in well_imported_items:
                            well_imported_items.append(item)
                    except Exception as e:
                        self.fail_io(item+" - "+str(e))
            else:
                not_found_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
