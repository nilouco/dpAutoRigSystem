# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DrivenKeyIO"
TITLE = "r052_drivenKeyIO"
DESCRIPTION = "r053_drivenKeyIODesc"
WIKI = "10-‐-Rebuilder#-driven-key"



class DrivenKeyIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_drivenKeyIO"
        self.start_name = "dpDrivenKey"


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
                        nodes = cmds.ls(selection=False, type=self.ar.data.drivenkey_types)
                    if self.first_mode: #export
                        if nodes:
                            self.export_json_file(self.get_drivenkey_data(nodes))
                        else:
                            self.maybe_done_io("Set Driven Keys")
                    else: #import
                        drivenkey_data = self.import_latest_json_file(self.get_exported_items())
                        if drivenkey_data:
                            self.import_drivenkey_data(drivenkey_data)
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


    def get_drivenkey_data(self, nodes):
        """ Processes the given set driven key node list to collect and mount the info data.
            Returns the dictionary to export.
        """
        data = {}
        attributes = ["preInfinity", "postInfinity", "useCurveColor", "stipplePattern", "outStippleThreshold", "stippleReverse"]
        key_attributes = ["keyBreakdown", "keyTickDrawSpecial"]
        key_time_attributes = ["keyTime", "keyValue"]
        self.ar.utils.setProgress(max=len(nodes), add_one=False, add_number=False)
        for item in nodes:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if not cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True) or not self.ar.utils.validateID(item):
                # getting attributes if they exists
                data[item] = { "attributes"     : {},
                            "keys"             : {},
                            "keyTimeValue"     : {},
                            "keyTanInType"     : {},
                            "keyTanOutType"    : {},
                            "keyTanInX"        : {},
                            "keyTanInY"        : {},
                            "keyTanOutX"       : {},
                            "keyTanOutY"       : {},
                            "keyTanLocked"     : {},
                            "keyWeightLocked"  : {},
                            "inAngle"          : {},
                            "inWeight"         : {},
                            "outAngle"         : {},
                            "outWeight"        : {},
                            "input"            : cmds.listConnections(item+".input", source=True, destination=False, plugs=True),
                            "output"           : cmds.listConnections(item+".output", source=False, destination=True, plugs=True),
                            "curveColor"       : cmds.getAttr(item+".curveColor")[0],
                            "weightedTangents" : cmds.getAttr(item+".weightedTangents"),
                            "type"             : cmds.objectType(item),
                            "size"             : cmds.getAttr(item+".keyTimeValue", multiIndices=True, size=True),
                            "name"             : item
                            }
                for attr in attributes:
                    if cmds.objExists(item+"."+attr):
                        data[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                # storage the keys
                if cmds.getAttr(item+".keyTimeValue", multiIndices=True):
                    for i, index in enumerate(cmds.getAttr(item+".keyTimeValue", multiIndices=True)):
                        data[item]["keyTimeValue"][index] = {}
                        data[item]["keys"][index] = {}
                        for kt_attr in key_time_attributes:
                            data[item]["keyTimeValue"][index][kt_attr] = cmds.getAttr(item+".keyTimeValue["+str(i)+"]."+kt_attr)
                        for k_attr in key_attributes:
                            data[item]["keys"][index][k_attr] = cmds.getAttr(item+"."+k_attr+"["+str(i)+"]")
                        data[item]["keyTanInType"][index]    = cmds.keyTangent(item, query=True, index=(i, i), inTangentType=True)[0]
                        data[item]["keyTanOutType"][index]   = cmds.keyTangent(item, query=True, index=(i, i), outTangentType=True)[0]
                        data[item]["keyTanInX"][index]       = cmds.keyTangent(item, query=True, index=(i, i), ix=True)[0]
                        data[item]["keyTanInY"][index]       = cmds.keyTangent(item, query=True, index=(i, i), iy=True)[0]
                        data[item]["keyTanOutX"][index]      = cmds.keyTangent(item, query=True, index=(i, i), ox=True)[0]
                        data[item]["keyTanOutY"][index]      = cmds.keyTangent(item, query=True, index=(i, i), oy=True)[0]
                        data[item]["keyTanLocked"][index]    = cmds.keyTangent(item, query=True, index=(i, i), lock=True)[0]
                        data[item]["keyWeightLocked"][index] = cmds.keyTangent(item, query=True, index=(i, i), weightLock=True)[0]
                        data[item]["inAngle"][index]         = cmds.keyTangent(item, query=True, index=(i, i), inAngle=True)[0]
                        data[item]["inWeight"][index]        = cmds.keyTangent(item, query=True, index=(i, i), inWeight=True)[0]
                        data[item]["outAngle"][index]        = cmds.keyTangent(item, query=True, index=(i, i), outAngle=True)[0]
                        data[item]["outWeight"][index]       = cmds.keyTangent(item, query=True, index=(i, i), outWeight=True)[0]
        return data


    def import_drivenkey_data(self, drivenkey_data):
        """ Import set driven key nodes from exported dictionary.
            Create missing set driven key nodes and set them values if they don't exists.
        """
        self.ar.utils.setProgress(max=len(drivenkey_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in drivenkey_data.keys():
            existing_nodes = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # create set driven key node if it needs
            if not cmds.objExists(item):
                node = cmds.createNode(drivenkey_data[item]["type"], name=drivenkey_data[item]["name"])
                # set attribute values
                for attr in drivenkey_data[item]["attributes"].keys():
                    if cmds.objExists(node+"."+attr):
                        cmds.setAttr(node+"."+attr, drivenkey_data[item]["attributes"][attr])
                cmds.setAttr(node+".curveColor", drivenkey_data[item]["curveColor"][0], drivenkey_data[item]["curveColor"][1], drivenkey_data[item]["curveColor"][2], type="double3")
                cmds.keyTangent(node, edit=True, weightedTangents=drivenkey_data[item]["weightedTangents"])
                # set driven keys
                for i in range(0, drivenkey_data[item]["size"]):
                    cmds.setKeyframe(item, float=drivenkey_data[item]["keyTimeValue"][str(i)]["keyTime"], value=drivenkey_data[item]["keyTimeValue"][str(i)]["keyValue"])
                    for k_attr in drivenkey_data[item]["keys"][str(i)].keys():
                        cmds.setAttr(item+"."+k_attr+"["+str(i)+"]", drivenkey_data[item]["keys"][str(i)][k_attr])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), inTangentType=drivenkey_data[item]["keyTanInType"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), outTangentType=drivenkey_data[item]["keyTanOutType"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), ix=drivenkey_data[item]["keyTanInX"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), iy=drivenkey_data[item]["keyTanInY"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), ox=drivenkey_data[item]["keyTanOutX"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), oy=drivenkey_data[item]["keyTanOutX"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), lock=drivenkey_data[item]["keyTanLocked"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), inAngle=drivenkey_data[item]["inAngle"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), inWeight=drivenkey_data[item]["inWeight"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), outAngle=drivenkey_data[item]["outAngle"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), outWeight=drivenkey_data[item]["outWeight"][str(i)])
                    if drivenkey_data[item]["weightedTangents"]:
                        cmds.keyTangent(node, edit=True, index=(int(i), int(i)), weightLock=drivenkey_data[item]["keyWeightLocked"][str(i)])
                # reconnect node
                if drivenkey_data[item]["input"]:
                    if cmds.objExists(drivenkey_data[item]["input"][0]):
                        cmds.connectAttr(drivenkey_data[item]["input"][0], node+".input", force=True)
                if drivenkey_data[item]["output"]:
                    for c, output_node in enumerate(drivenkey_data[item]["output"]):
                        if cmds.objExists(drivenkey_data[item]["output"][c]):
                            is_locked = cmds.getAttr(drivenkey_data[item]["output"][c], lock=True)
                            cmds.setAttr(drivenkey_data[item]["output"][c], lock=False)
                            cmds.connectAttr(node+".output", drivenkey_data[item]["output"][c], force=True)
                            if is_locked:
                                cmds.setAttr(drivenkey_data[item]["output"][c], lock=True)
                well_imported_items.append(node)
            else:
                existing_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        else:
            if existing_nodes:
                self.well_done_io(self.ar.data.lang['r032_notImportedData'])
            else:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(existing_nodes))
