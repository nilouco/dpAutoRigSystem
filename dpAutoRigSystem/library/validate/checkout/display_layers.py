# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DisplayLayers"
TITLE = "v054_displayLayers"
DESCRIPTION = "v055_displayLayersDesc"
WIKI = "07-‐-Validator#-display-layers"



class DisplayLayers(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if inputs:
                ctrl_geo_items = inputs
            else:
                # List all controls
                ctrl_geo_items = None
                self.all_ctrls = self.ar.ctrls.get_controllers()
                if self.all_ctrls:
                    all_geos = self.get_geo_transform()
                    ctrl_geo_items = self.all_ctrls
                    if all_geos:
                        ctrl_geo_items = self.all_ctrls + all_geos
            if ctrl_geo_items:
                self.geo_layer_name = "Geo_Lyr"
                self.ctrl_layer_name = "Ctrl_Lyr"
                all_layers = cmds.ls(type="displayLayer")
                self.to_delete_extra_layers = []
                for layer in all_layers:
                    if layer != self.geo_layer_name and layer != self.ctrl_layer_name and layer != "defaultLayer":
                        self.to_delete_extra_layers.append(layer)
                if not self.to_delete_extra_layers:
                    if cmds.objExists(self.geo_layer_name) and cmds.objExists(self.ctrl_layer_name):
                        layers_config_checks = [True, False, 2, True, False, 0]
                        geo_layer_vis = cmds.getAttr(self.geo_layer_name+".visibility") #True
                        geo_layer_hide_on_playback = cmds.getAttr(self.geo_layer_name+".hideOnPlayback") #False
                        geo_layer_display_type = cmds.getAttr(self.geo_layer_name+".displayType") #2 = ref
                        ctrl_layer_vis = cmds.getAttr(self.ctrl_layer_name+".visibility") #True
                        ctrl_layer_hide_on_playback = cmds.getAttr(self.ctrl_layer_name+".hideOnPlayback") #False
                        ctrl_layer_display_type = cmds.getAttr(self.ctrl_layer_name+".displayType") #0 = none
                        layer_configs = [geo_layer_vis, geo_layer_hide_on_playback, geo_layer_display_type, ctrl_layer_vis, ctrl_layer_hide_on_playback, ctrl_layer_display_type]
                        # Check layers configuration
                        if layer_configs == layers_config_checks:
                            in_geo_layer_items = cmds.editDisplayLayerMembers(self.geo_layer_name, fullNames=True, query=True)
                            in_ctrl_layer_items = cmds.editDisplayLayerMembers(self.ctrl_layer_name, query=True)
                            # Check layers members
                            if in_geo_layer_items and in_ctrl_layer_items:
                                missing_geos = list(set(all_geos) - set(in_geo_layer_items))
                                remaining_geos = list(set(in_geo_layer_items) - set(all_geos))
                                missing_ctrls = list(set(self.all_ctrls) - set(in_ctrl_layer_items))
                                remaining_ctrls = list(set(in_ctrl_layer_items) - set(self.all_ctrls))
                                to_fix_items = missing_geos + remaining_geos + missing_ctrls + remaining_ctrls
                                if to_fix_items:
                                    self.verify_fix_mode(to_fix_items)
                            else:
                                # Empty layer
                                self.verify_fix_mode([self.ar.data.lang['v056_emptyLayers']])
                        else:
                            # Layer configuration
                            self.verify_fix_mode([self.ar.data.lang['v057_layerConfiguration']])
                    else:
                        # No display layer
                        self.verify_fix_mode([self.ar.data.lang['v054_displayLayers']])
                else:
                    # Extra Lyr to delete
                    self.verify_fix_mode(self.to_delete_extra_layers)
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data


    def create_display_layers(self):
        """ Call functions to create Geo_Lyr and Ctrl_Lyr
            If there's no geometry on the groups Render_Grp and Proxy_Grp, it will delete the Geo_Lyr
        """ 
        geos = self.get_geo_transform()
        if geos:
            self.create_new_layer(geos, self.geo_layer_name)
        else:
            if cmds.objExists(self.geo_layer_name):
                cmds.delete(self.geo_layer_name)
        self.create_new_layer(self.all_ctrls, self.ctrl_layer_name, False)
        if self.to_delete_extra_layers:
            cmds.delete(self.to_delete_extra_layers)
        

    def create_new_layer(self, items, layer_name, geo_type=True):
        """ Creates Geo_Lyr with the objects inside Render_Grp and Proxy_Grp
        """
        if items:
            cmds.select(items)
            new_layer = str(cmds.createDisplayLayer(name=layer_name, noRecurse=True))
            # Count numbers in name
            numeric = 0
            for n in new_layer:
                if n.isdigit():
                    numeric +=1
            # If there's numeric in name, delete the first, rename the new one and displayType 2 option
            if numeric > 0:           
                cmds.delete(layer_name)
                new_layer = cmds.rename(new_layer, layer_name)
                if geo_type:
                    cmds.setAttr(new_layer+".displayType", 2)
                cmds.select(clear=True)
            else:
                if geo_type:
                    cmds.setAttr(layer_name+".displayType", 2)
                cmds.select(clear=True)


    def get_geo_transform(self):
        """ Get all transform nodes from Render_Grp or convention geometry group name.
            If it finds nothing, it will return an empty list.
        """
        exist_grps, all_shapes = [], []
        mesh_grps = ["Mesh_Grp", "mesh_grp", "Geo_Grp", "geo_grp", "grp_cache", "GES_Grp", "ges_grp"]
        render_grp = self.ar.utils.get_node_by_message("renderGrp")
        if render_grp:
            exist_grps.append(render_grp)
        for grp in mesh_grps:
            if cmds.objExists(grp):
                exist_grps.append(grp)
        if exist_grps:
            for mesh_grp in exist_grps:
                mesh_grp_shapes = cmds.listRelatives(mesh_grp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
                if mesh_grp_shapes:
                    all_shapes = list(set(all_shapes + mesh_grp_shapes))
            all_geos = []
            if all_shapes:
                for shape in all_shapes:
                    transforms = cmds.listRelatives(shape, fullPath=True, parent=True)
                    if transforms:
                        # Get the transform only
                        all_geos.append(transforms[0])
            return all_geos
    

    def verify_fix_mode(self, items):
        """ This function will check if the item is a list or not.
            If it's a list it will append the items in the data and run the main function once.
            If it's not a list it will append the item and run the main function.
        """
        if items:
            self.ar.ui_manager.set_progress(max=len(items), add_one=False, add_number=False)
            for i, item in enumerate(items):
                self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                if self.first_mode:
                    self.good_results.append(False)
                    self.checked_items.append(item)
                    self.found_issues.append(True)
                else:
                    try:#verify
                        # It will run function only one time to create displayLayers in the last index from the loop, 
                        # otherwise it will create for every index
                        if i == len(items) - 1:
                            self.create_display_layers()    
                        self.good_results.append(True)
                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                    except:#fix
                        self.good_results.append(False)
                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
