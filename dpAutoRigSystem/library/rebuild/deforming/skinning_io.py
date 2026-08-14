# importing libraries:
from maya import cmds
from ....library.base import action
import os

# global variables to this module:
CLASS_NAME = "SkinningIO"
TITLE = "r016_skinningIO"
DESCRIPTION = "r017_skinningIODesc"
WIKI = "10-‐-Rebuilder#-skinning"



class SkinningIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_skinningIO"
        self.start_name = "skinning"
        self.import_ref_name = "dpSkinningIO_Import"
    

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
                        items = None
                        if inputs:
                            items = inputs
                        else:
                            items = self.ar.skin.getDeformedItemList(deformerTypeList=["skinCluster"], ignoreAttr=self.ar.skin.ignoreSkinningAttr)
                        if items:
                            self.export_json_file(self.ar.skin.getSkinWeightData(items))
                        else:
                            self.maybe_done_io("Render_Grp")
                    else: #import
                        skin_weight_data = self.import_latest_json_file(self.get_exported_items())
                        if skin_weight_data:
                            self.import_skinning(skin_weight_data)
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
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def ref_old_wip_file(self, *args):
        """ Reference the latest wip rig file before the current, and return it's tranform elements, if there.
        """
        #
        # UNUSED
        # TODO: waiting needing continue developing this method or delete it further.
        #
        ref_nodes = []
        wip_files = next(os.walk(self.ar.pipeliner.pipe_data['assetPath']))[2]
        if len(wip_files) > 1:
            wip_files.sort()
            if len(self.exported_items) > 1:
                self.ref_path_name = self.exported_items[-2][len(self.start_name)+1:-5]
                if os.path.isfile(self.ar.pipeliner.pipe_data['assetPath']+"/"+self.ref_path_name+".ma"):
                    self.ref_path_name = self.ref_path_name+".ma"
                else:
                    self.ref_path_name = self.ref_path_name+".mb"
                self.ref_path_name = self.ar.pipeliner.pipe_data['assetPath']+"/"+wip_files[-2]
                cmds.file(self.ref_path_name, reference=True, namespace=self.import_ref_name)
                ref_node = cmds.file(self.ref_path_name, referenceNode=True, query=True)
                ref_nodes = cmds.referenceQuery(ref_node, nodes=True)
                if ref_nodes:
                    ref_nodes = cmds.ls(ref_nodes, type="transform")
        return ref_nodes


    def import_skinning(self, skin_weight_data):
        """ Import the skinning from exported skin weight dictionary.
        """
        well_imported = True
        to_import_items, not_found_meshs, changed_topo_meshes, changed_shape_meshes = [], [], [], []
        
        # TODO: reference old wip rig version to compare meshes changes
        #ref_nodes = self.ref_old_wip_file()
        ref_nodes = None

        for item in skin_weight_data.keys():
            if cmds.objExists(item):
                if ref_nodes: #disable at the momment
                    for ref_node_name in ref_nodes:
                        if ref_node_name[ref_node_name.rfind(":")+1:] == self.ar.skin.getIOFileName(item):
                            if cmds.polyCompare(item, ref_node_name, vertices=True) > 0 or cmds.polyCompare(item, ref_node_name, edges=True) > 0: #check if shape changes
                                changed_shape_meshes.append(item)
                                well_imported = False
                            elif not len(cmds.ls(item+".vtx[*]", flatten=True)) == len(cmds.ls(ref_node_name+".vtx[*]", flatten=True)): #check if poly count changes
                                changed_topo_meshes.append(item)
                                well_imported = False
                            else:
                                to_import_items.append(item)
                else:
                    to_import_items.append(item)
            else:
                not_found_meshs.append(item)
        if ref_nodes:
            cmds.file(self.ref_path_name, removeReference=True)
        if to_import_items:
            try:
                # import skin weights
                self.ar.skin.importSkinWeightsFromFile(to_import_items, self.io_path, self.latest_data_file, False)
                self.well_done_io(self.latest_data_file)
            except Exception as e:
                self.fail_io(self.latest_data_file+": "+str(e))
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(skin_weight_data.keys())))
        if not well_imported:
            if changed_shape_meshes:
                self.fail_io(self.ar.data.lang['r018_changedMesh']+" shape "+str(', '.join(changed_shape_meshes)))
            elif changed_topo_meshes:
                self.fail_io(self.ar.data.lang['r018_changedMesh']+" topology "+str(', '.join(changed_topo_meshes)))
            elif not_found_meshs:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(not_found_meshs)))
