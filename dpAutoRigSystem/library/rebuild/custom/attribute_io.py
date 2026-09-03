# importing libraries:
from maya import cmds
from ....library.base import action
from importlib import reload

# global variables to this module:
CLASS_NAME = "AttributeIO"
TITLE = "r043_attributeIO"
DESCRIPTION = "r044_attributeIODesc"
WIKI = "10-‐-Rebuilder#-new-scene"



class AttributeIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(action)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_attributeIO"
        self.start_name = "dpAttribute"
        self.default_value_types = ["bool", "long",  "short",  "byte",  "char",  "enum",  "'float'",  "double",  "doubleAngle",  "doubleLinear"]
    

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
                        items = self.ar.ctrls.get_controllers()
                        items.extend(self.get_models_to_export())
                    if items:
                        if self.first_mode: #export
                            self.export_json_file(self.get_attribute_data(items))
                        else: #import
                            attr_data = self.import_latest_json_file(self.get_exported_items())
                            if attr_data:
                                self.import_attribute_data(attr_data)
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


    def get_attribute_data(self, inputs):
        """ Processes the given controller list to collect and mount the attributes data.
            Also works with meshes.
            Returns the dictionary to export.
        """
        data = {}
        items = inputs.copy()
        self.ar.ui_manager.set_progress(max=len(items), add_one=False, add_number=False)
        for node in inputs:
            meshes = cmds.listRelatives(node, allDescendents=True, children=True, type="mesh")
            if meshes:
                items.extend([m for m in meshes if not cmds.getAttr(m+".intermediateObject")] or [])
                items.extend([t for t in cmds.listRelatives(node, allDescendents=True, children=True, type="transform") or [] if cmds.listRelatives(t, children=True, type="mesh")] or [])
        items = list(set(items))
        items.sort()
        for item in items:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            attributes = cmds.listAttr(item, userDefined=True)
            if attributes:
                data[item] = {"attributes" : {},
                                "order" : attributes}
                for attr in attributes:
                    if not cmds.getAttr(item+"."+attr, type=True) == "message":
                        attr_type = cmds.getAttr(item+"."+attr, type=True)
                        data[item]["attributes"][attr] = {
                                            "type" : attr_type,
                                            "value" : cmds.getAttr(item+"."+attr),
                                            "locked" : cmds.getAttr(item+"."+attr, lock=True),
                                            "keyable" : cmds.getAttr(item+"."+attr, keyable=True),
                                            "channelBox" : cmds.getAttr(item+"."+attr, channelBox=True)
                                            }
                        if attr_type in self.default_value_types:
                            if attr_type == "enum":
                                data[item]["attributes"][attr]["enumName"] = cmds.attributeQuery(attr, node=item, listEnum=True)[0]
                            data[item]["attributes"][attr]["default"] = cmds.addAttr(item+"."+attr, query=True, defaultValue=True)
                            data[item]["attributes"][attr]["maxExists"] = cmds.attributeQuery(attr, node=item, maxExists=True) or False
                            if data[item]["attributes"][attr]["maxExists"]:
                                data[item]["attributes"][attr]["maximum"] = cmds.attributeQuery(attr, node=item, maximum=True)[0]
                            data[item]["attributes"][attr]["minExists"] = cmds.attributeQuery(attr, node=item, minExists=True) or False
                            if data[item]["attributes"][attr]["minExists"]:
                                data[item]["attributes"][attr]["minimum"] = cmds.attributeQuery(attr, node=item, minimum=True)[0]
        return data


    def import_attribute_data(self, attr_data):
        """ Import attributes from exported dictionary.
            Add missing attributes and set them values if they don't exists.
        """
        self.ar.ui_manager.set_progress(max=len(attr_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in attr_data.keys():
            not_found_nodes = []
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            # check attributes
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in attr_data[item]["attributes"].keys():
                    if not cmds.objExists(item+"."+attr):
                        try:
                            # add and set attribute value
                            if attr_data[item]["attributes"][attr]['type'] == "string":
                                cmds.addAttr(item, longName=attr, dataType="string")
                                cmds.setAttr(item+"."+attr, attr_data[item]["attributes"][attr]['value'], type="string")
                            elif attr_data[item]["attributes"][attr]['type'] == "enum":
                                cmds.addAttr(item, longName=attr, attributeType="enum", enumName=attr_data[item]["attributes"][attr]['enumName'])
                            else:
                                if attr_data[item]["attributes"][attr]['minExists']:
                                    if attr_data[item]["attributes"][attr]['maxExists']:
                                        cmds.addAttr(item, longName=attr, attributeType=attr_data[item]["attributes"][attr]['type'], minValue=attr_data[item]["attributes"][attr]['minimum'], maxValue=attr_data[item]["attributes"][attr]['maximum'], defaultValue=attr_data[item]["attributes"][attr]['default'])
                                    else:
                                        cmds.addAttr(item, longName=attr, attributeType=attr_data[item]["attributes"][attr]['type'], minValue=attr_data[item]["attributes"][attr]['minimum'], defaultValue=attr_data[item]["attributes"][attr]['default'])
                                elif attr_data[item]["attributes"][attr]['maxExists']:
                                    cmds.addAttr(item, longName=attr, attributeType=attr_data[item]["attributes"][attr]['type'], maxValue=attr_data[item]["attributes"][attr]['maximum'], defaultValue=attr_data[item]["attributes"][attr]['default'])
                                else:
                                    cmds.addAttr(item, longName=attr, attributeType=attr_data[item]["attributes"][attr]['type'], defaultValue=attr_data[item]["attributes"][attr]['default'])
                            if attr_data[item]["attributes"][attr]['type'] in self.default_value_types:
                                cmds.setAttr(item+"."+attr, attr_data[item]["attributes"][attr]['value'])
                                cmds.setAttr(item+"."+attr, keyable=attr_data[item]["attributes"][attr]['keyable'])
                                if not attr_data[item]["attributes"][attr]['keyable']:
                                    cmds.setAttr(item+"."+attr, channelBox=attr_data[item]["attributes"][attr]['channelBox'])
                                cmds.setAttr(item+"."+attr, lock=attr_data[item]["attributes"][attr]['locked'])
                            if not item in well_imported_items:
                                well_imported_items.append(item)
                        except Exception as e:
                            self.fail_io(item+" - "+str(e))
                    else:
                        well_imported_items.append(item)
                        # TODO: should we set the attribute value here?
                # reorder attr
                self.ar.maker.reorder_option_attributes([item], attr_data[item]["order"], False)
            else:
                not_found_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
