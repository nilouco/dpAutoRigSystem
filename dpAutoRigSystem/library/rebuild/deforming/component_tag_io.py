# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ComponentTagIO"
TITLE = "r048_componentTagIO"
DESCRIPTION = "r049_componentTagIODesc"
WIKI = "10-‐-Rebuilder#-componenttag"



class ComponentTagIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_componentTagIO"
        self.start_name = "dpComponentTag"
    

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
                    nodes = None
                    if inputs:
                        nodes = inputs
                    else:
                        nodes = cmds.listRelatives(cmds.ls(selection=False, type=["mesh", "lattice"]), parent=True)
                    if self.first_mode: #export
                        if nodes:
                            # finding tags
                            has_tag = False
                            for node in nodes:
                                if cmds.geometryAttrInfo(node+"."+cmds.deformableShape(node, localShapeOutAttr=True)[0], componentTagHistory=True):
                                    has_tag = True
                                    break
                            if has_tag:
                                # Declaring the data dictionary to export it
                                self.tag_data = { "tagged"     : self.ar.skin.get_component_tag_info(nodes),
                                                    "influencer" : self.ar.skin.get_component_tag_influencer(),
                                                    "falloff"    : self.ar.skin.get_component_tag_falloff()
                                                }
                                self.export_json_file(self.tag_data)
                            else:
                                self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" componentTag")
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" mesh, lattice")
                    else: #import
                        tag_data = self.import_latest_json_file(self.get_exported_items())
                        if tag_data:
                            self.import_tag(tag_data, nodes)
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
        cmds.select(clear=True)
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def import_tag(self, tag_data, nodes):
        """ Import componentTag data.
        """
        fail = False
        # import tagged (tag info into the received deformed mesh)
        if tag_data["tagged"]:
            if not self.ar.skin.import_component_tag_info(tag_data["tagged"], nodes):
                self.fail_io(self.latest_data_file+": tagged - "+", ".join(self.ar.skin.notWorkWellInfoList))
                fail = True
        # import influencers (tag info into the deformer node)
        if tag_data["influencer"]:
            if not self.ar.skin.import_component_tag_influencer(tag_data["influencer"]):
                self.fail_io(self.latest_data_file+": influencer - "+", ".join(self.ar.skin.notWorkWellInfoList))
                fail = True
        # import falloffs
        if tag_data["falloff"]:
            if not self.ar.skin.import_component_tag__falloff(tag_data["falloff"]):
                self.fail_io(self.latest_data_file+": falloff - "+", ".join(self.ar.skin.notWorkWellInfoList))
                fail = True
        if not fail:
            self.well_done_io(self.latest_data_file)
