# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ConnectionIO"
TITLE = "r045_connectionIO"
DESCRIPTION = "r046_connectionIODesc"
WIKI = "10-‐-Rebuilder#-connection"



class ConnectionIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_connectionIO"
        self.start_name = "dpConnection"
    

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
                    controllers = None
                    if inputs:
                        controllers = inputs
                    else:
                        controllers = self.ar.ctrls.get_controllers()
                    if controllers:
                        if self.first_mode: #export
                            to_export_data = self.get_connection_data(controllers)
                            to_export_data.update(self.get_utilities_data(cmds.ls(selection=False, type=self.ar.utils.utility_types))) #utilityNodes without dpID
                            self.export_json_file(to_export_data)
                        else: #import
                            connection_data = self.import_latest_json_file(self.get_exported_items())
                            if connection_data:
                                self.import_connection_data(connection_data)
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


    def get_connection_data(self, items):
        """ Processes the given list to collect the info about their connections to rebuild.
            Returns a dictionary to export.
        """
        data = {}
        self.ar.ui_manager.set_progress(max=len(items), add_one=False, add_number=False)
        for item in items:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                attributes = self.ar.data.transform_attrs.copy()
                user_defined_attributes = cmds.listAttr(item, userDefined=True)
                if user_defined_attributes:
                    attributes.extend(user_defined_attributes)
                connected_attributes = []
                for attr in attributes:
                    if cmds.objExists(item+"."+attr):
                        if cmds.listConnections(item+"."+attr):
                            connected_attributes.append(attr)
                if connected_attributes:
                    data[item] = {}
                    for attr in connected_attributes:
                        data[item][attr] = self.get_connection_io_data(item, attr)
        return data


    def get_connection_infos(self, item, source_connection, destination_connection):
        """ Return a list of plugged nodes and their attributes of the given item.
        """
        results = []
        if cmds.listConnections(item, plugs=True, source=source_connection, destination=destination_connection):
            infos = cmds.listConnections(item, plugs=True, source=source_connection, destination=destination_connection)
            if infos:
                for info in infos:
                    if cmds.objectType(info[:info.find(".")]) == "unitConversion":
                        if source_connection:
                            connections = self.get_connection_infos(info[:info.find(".")]+".input", source_connection, destination_connection) or [None]
                            results.append({info : connections})
                        else:
                            connections = self.get_connection_infos(info[:info.find(".")]+".output", source_connection, destination_connection) or [None]
                            results.append({info : connections})
                        results[-1][list(results[-1].keys())[0]].append(cmds.getAttr(info[:info.find(".")]+".conversionFactor"))
                    else:
                        results.append(info)
        return results


    def get_attr_connections(self, item, attr_data, multi=False):
        """ Return a dictionary with the connections for the attributes.
        """
        data = {}
        node_type = cmds.objectType(item)
        if node_type in attr_data.keys():
            connected_attributes = []
            for attr in attr_data[node_type]:
                if cmds.listConnections(item+"."+attr):
                    connected_attributes.append(attr)
            if connected_attributes:
                for attr in connected_attributes:
                    if multi:
                        indexes = cmds.getAttr(item+"."+attr, multiIndices=True)
                        if indexes:
                            dot = ""
                            multi_attributes = [""]
                            if attr_data[node_type][attr]:
                                dot = "."
                                multi_attributes = attr_data[node_type][attr]
                            for i in indexes:
                                for multi_attr in multi_attributes:
                                    attr_name = attr+"["+str(i)+"]"+dot+multi_attr
                                    data[attr_name] = self.get_connection_io_data(item, attr_name)
                    else:
                        data[attr] = self.get_connection_io_data(item, attr)
        return data
    

    def get_utilities_data(self, items):
        """ Return the connection data from given utility nodes list.
        """
        data = {}
        self.ar.ui_manager.set_progress(max=len(items), add_one=False, add_number=False)
        for item in items:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                if not cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True) or not self.ar.utils.validate_id(item):
                    for attr_data, multi in zip([self.ar.utils.type_attr_data, self.ar.utils.type_out_attr_data, self.ar.utils.type_multi_attr_data, self.ar.utils.type_out_multi_attr_data], [False, False, True, True]):
                        attr_connection_data = self.get_attr_connections(item, attr_data, multi)
                        if attr_connection_data:
                            if not item in data.keys():
                                data[item] = attr_connection_data
                            else:
                                data[item].update(attr_connection_data)
        return data
        

    def get_connection_io_data(self, item, attr):
        """ Return the connection from and to the given item and its attribute.
        """
        return {
                "in"  : self.get_connection_infos(item+"."+attr, source_connection=True, destination_connection=False),
                "out" : self.get_connection_infos(item+"."+attr, source_connection=False, destination_connection=True)
                }


    def import_connection_data(self, connection_data):
        """ Import connection data.
            Check if need to create an unitConversion node and set its conversionFactor value.
            Only redo the connection if it doesn't exists yet.
        """
        self.ar.ui_manager.set_progress(max=len(connection_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in connection_data.keys():
            not_found_nodes = []
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                # check connections
                for attr in connection_data[item].keys():
                    #if attr in cmds.listAttr(item): #can't have this conditional because multiIndices doesn't exists before connect them
                    for i, io in enumerate(["in", "out"]): #input and output
                        if connection_data[item][attr][io]: #there's connection
                            for io_info in connection_data[item][attr][io]:
                                if isinstance(io_info, dict): #is dictionary, so there's an unitConversion node
                                    plug = list(io_info.keys())[0]
                                    if not cmds.objExists(plug):
                                        uc = cmds.createNode("unitConversion", name=plug.split(".")[0])
                                        cmds.setAttr(uc+".conversionFactor", io_info[plug][1])
                                    else:
                                        uc = plug.split(".")[0]
                                    if not io_info[plug][0] == None:
                                        if i == 0: #in
                                            if not cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False) or not uc+".output" in cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False):
                                                is_locked = cmds.getAttr(item+"."+attr, lock=True)
                                                cmds.setAttr(item+"."+attr, lock=False)
                                                cmds.connectAttr(uc+".output", item+"."+attr, force=True)
                                                if is_locked:
                                                    cmds.setAttr(item+"."+attr, lock=True)
                                            if not cmds.listConnections(uc+".input", plugs=True, source=True, destination=False) or not io_info[plug][0] in cmds.listConnections(uc+".input", plugs=True, source=True, destination=False):
                                                cmds.connectAttr(io_info[plug][0], uc+".input", force=True)
                                        else: #out
                                            if not cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True) or not uc+".input" in cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True):
                                                cmds.connectAttr(item+"."+attr, uc+".input", force=True)
                                            if not cmds.listConnections(uc+".output", plugs=True, source=False, destination=True) or not io_info[plug][0] in cmds.listConnections(uc+".output", plugs=True, source=False, destination=True):
                                                is_locked = cmds.getAttr(io_info[plug][0], lock=True)
                                                cmds.setAttr(io_info[plug][0], lock=False)
                                                cmds.connectAttr(uc+".output", io_info[plug][0], force=True)
                                                if is_locked:
                                                    cmds.setAttr(io_info[plug][0], lock=True)
                                    else: #there is a not connected unitConversion node
                                        self.fail_io(self.ar.data.lang['r047_notConnectedUC']+": "+uc)
                                elif cmds.objExists(io_info[:io_info.find(".")]):
                                    if i == 0: #in
                                        # if there isn't this attribute here, maybe it's an issue parenting the guides. Check the guide serialization before rig them.
                                        if not cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False) or not io_info in cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False):
                                            is_locked = cmds.getAttr(item+"."+attr, lock=True)
                                            cmds.setAttr(item+"."+attr, lock=False)
                                            cmds.connectAttr(io_info, item+"."+attr, force=True)
                                            if is_locked:
                                                cmds.setAttr(item+"."+attr, lock=True)
                                    else: #out
                                        if not cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True) or not io_info in cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True):
                                            is_locked = cmds.getAttr(io_info, lock=True)
                                            cmds.setAttr(io_info, lock=False)
                                            cmds.connectAttr(item+"."+attr, io_info, force=True)
                                            if is_locked:
                                                cmds.setAttr(io_info, lock=True)
                                else:
                                     self.maybe_done_io(io_info[:io_info.find(".")])
                                if not item in well_imported_items:
                                    well_imported_items.append(item)
            else:
                not_found_nodes.append(item)
        if not_found_nodes:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
        elif well_imported_items:
            self.well_done_io(self.latest_data_file)
