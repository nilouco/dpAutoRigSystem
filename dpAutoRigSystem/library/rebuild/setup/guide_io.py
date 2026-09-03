# importing libraries:
from maya import cmds
from ....library.base import action
from ....library.tool import head_deformer
from importlib import reload
import ast

# global variables to this module:
CLASS_NAME = "GuideIO"
TITLE = "r012_guideIO"
DESCRIPTION = "r013_guideIODesc"
WIKI = "10-‐-Rebuilder#-guide"

MODULES = "Modules.Standard"



class GuideIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_guideIO"
        self.start_name = "dpGuide"
        if self.ar.dev:
            reload(head_deformer)
        self.head_deformer = head_deformer.HeadDeformer(self.ar)
        self.head_deformer.ui = False
    

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
                    self.ar.ui_manager.refresh_ui(reset_buttons=False)
                    if self.first_mode: #export
                        nets = None
                        if inputs:
                            nets = inputs
                        else:
                            nets = self.ar.utils.get_network_by_attr("dpGuideNet")
                            nets.extend(self.ar.utils.get_network_by_attr("dpHeadDeformerNet") or [])
                        if nets:
                            self.ar.job.unpin_guide(force=True)
                            self.export_json_file(self.get_guide_data(nets))
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
                            cmds.select(clear=True)
                    else: #import
                        # apply viewport xray
                        model_panels = cmds.getPanel(type="modelPanel")
                        for mp in model_panels:
                            cmds.modelEditor(mp, edit=True, xray=True)
                        guide_data = self.import_latest_json_file(self.get_exported_items())
                        if guide_data:
                            well_imported = False
                            try:
                                guide_data = self.parse_repeated_nets(guide_data)
                                well_imported = self.import_guide(guide_data)
                                self.setup_guide_base_parenting(guide_data)
                            except Exception as e:
                                if not well_imported: #guide initialization issue
                                    self.fail_io(self.ar.data.lang['m195_couldNotBeSet']+": "+str(e))
                                else: #parenting issue
                                    self.fail_io(self.ar.data.lang['m197_notPossibleParent']+": "+str(e))
                                well_imported = False
                            if well_imported:
                                self.well_done_io(self.latest_data_file)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                        cmds.select(clear=True)
                        # remove viewport xray
                        for mp in model_panels:
                            cmds.modelEditor(mp, edit=True, xray=False)
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
        self.end_progress(True)
        self.refresh_view()
        if self.ar.data.ui_state:
            self.ar.ui_manager.clear_guide_layout()
            self.ar.filler.fill_created_guides()
        return self.log_data


    def get_guide_data(self, nets):
        """ Return a dictionary of the guide data to export it.
        """
        to_export_data = {}
        self.ar.ui_manager.set_progress(max=len(nets), add_one=False, add_number=False)
        for net in nets:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            # mount a data with all data 
            if "afterData" in cmds.listAttr(net):
                if "rawGuide" in cmds.listAttr(net) and cmds.getAttr(net+".rawGuide"):
                    # get data from not rendered guide (rawGuide status on)
                    module_instance_info_string = cmds.getAttr(cmds.listConnections(net+".linkedNode")[0]+".moduleInstanceInfo")
                    for module_instance in self.ar.data.guide_instances:
                        if str(module_instance) == module_instance_info_string:
                            module_instance.serialize_guide(False) #serialize it without build it
                to_export_data[net] = ast.literal_eval(cmds.getAttr(net+".afterData"))
            elif "dpHeadDeformerNet" in cmds.listAttr(net):
                if not cmds.listConnections(net+".guideNet", source=True, destination=False):
                    to_export_data[net] = ast.literal_eval(cmds.getAttr(net+".netData"))
        return to_export_data


    def setup_instance_changes(self, rebuilding=True):
        """ Run instance code to Guide_Base node configuration or just set the simple attributes.
        """
        custom_attributes = ["articulation",
                            "flip",
                            "mainControls",
                            "nMain",
                            "dynamic",
                            "corrective",
                            "alignWorld",
                            "additional",
                            "softIk",
                            "nostril",
                            "indirectSkin",
                            "holder",
                            "sdkLocator",
                            "startFrame",
                            "showControls",
                            "steering",
                            "degree",
                            "eyelid",
                            "iris",
                            "pupil",
                            "specular",
                            "lidPivot",
                            "style",
                            "rigType",
                            "numBendJoints",
                            "facial",
                            "facialBrow",
                            "facialEyelid",
                            "facialMouth",
                            "facialLips",
                            "facialSneer",
                            "facialGrimace",
                            "facialFace",
                            "deformer",
                            "deformedBy",
                            "worldSize",
                            "shapeSize",
                            "jaw",
                            "chin",
                            "lips",
                            "upperHead"
                            ]
        for item in list(self.net_data["GuideData"]):
            new_item = self.get_new_name(item)
            if cmds.objExists(new_item):
                if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #main
                    for base_attr in list(self.net_data["GuideData"][item]):
                        if base_attr == "customName":
                            custom_name = self.net_data["GuideData"][item]["customName"]
                            if custom_name:
                                if not rebuilding: #template
                                    custom_name = self.ar.naming.get_translated_names(custom_name)
                                self.instance.set_guide_custom_name(custom_name)
                        elif base_attr == "mirrorAxis":
                            cmds.setAttr(new_item+".mirrorAxis", self.net_data["GuideData"][item]["mirrorAxis"], type="string")
                            start = self.ar.naming.get_translated_names(self.net_data["GuideData"][item]["mirrorName"][0])
                            end = self.ar.naming.get_translated_names(self.net_data["GuideData"][item]["mirrorName"][-1])
                            cmds.setAttr(new_item+".mirrorName", f"{start} --> {end}", type="string")
                            self.instance.create_mirror_preview()
                        elif base_attr == "nJoints":
                            self.instance.change_joint_number(self.net_data["GuideData"][item]["nJoints"])
                        elif base_attr == "type": #limb
                            self.instance.change_type(self.net_data["GuideData"][item]["type"])
                        elif base_attr == "hasBend": #limb
                            self.instance.change_bend(self.net_data["GuideData"][item]["hasBend"])
                        elif base_attr == "aimDirection": #eye
                            self.instance.change_aim_direction(self.ar.data.directions[(int(self.net_data["GuideData"][item]["aimDirection"]))])
                        elif base_attr == "fatherB": #suspention
                            father_b_data = self.net_data["GuideData"][item]["fatherB"]
                            if father_b_data:
                                cmds.setAttr(item+".fatherB", father_b_data, type="string")
                        elif base_attr == "geo": #wheel
                            geo_info = self.net_data["GuideData"][item]["geo"]
                            if geo_info:
                                cmds.setAttr(new_item+".geo", geo_info, type="string")
                        #TODO: modernize rigType to rigStyle new code
                        elif base_attr == "rigType": #all
                            rigTypeData = self.net_data["GuideData"][item]["rigType"]
                            if rigTypeData:
                                cmds.setAttr(new_item+".rigType", rigTypeData, type="string")
                                self.instance.rigType = rigTypeData
                        elif base_attr == "style":  #to be compatible with old versions of style value 4 (quadruped extra control)
                            cmds.setAttr(new_item+"."+base_attr, min(self.net_data["GuideData"][item][base_attr], 2))
                        else: #just set simple attributes
                            if base_attr in custom_attributes:
                                cmds.setAttr(new_item+"."+base_attr, self.net_data["GuideData"][item][base_attr])
                        cmds.refresh()


    def setup_guide_transformations(self):
        """ Work with guide transformations to put the transform as imported data.
        """
        for item in list(self.net_data["GuideData"]):
            if item in self.net_data["GuideData"].keys():
                new_item = self.get_new_name(item)
                if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #main
                    if cmds.listRelatives(new_item, parent=True):
                        cmds.parent(new_item, world=True)
                for attr in list(self.net_data["GuideData"][item]):
                    if attr in self.ar.data.transform_attrs:
                        if not cmds.getAttr(new_item+"."+attr, lock=True): #unlocked attribute
                            if not cmds.listConnections(new_item+"."+attr, destination=False, source=True): #without input connection
                                cmds.setAttr(new_item+"."+attr, self.net_data["GuideData"][item][attr])
                    cmds.refresh()


    def setup_guide_base_parenting(self, guide_data):
        """ Rebuild the Guide_Base parenting.
        """
        for net in guide_data.keys():
            net_data = guide_data[net]
            if "GuideData" in net_data.keys():
                for item in list(net_data["GuideData"]):
                    new_item = self.get_new_name(item)
                    if cmds.objExists(new_item):
                        if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #main
                            father_node_data = net_data["GuideData"][item]['FatherNode']
                            if father_node_data:
                                new_father = self.get_new_name(father_node_data)
                                if cmds.objExists(new_father):
                                    if not cmds.listRelatives(new_item, parent=True) or not cmds.listRelatives(new_item, parent=True)[0] == new_father:
                                        cmds.parent(new_item, new_father)


    def parse_repeated_nets(self, guide_data):
        if len(self.ar.utils.get_network_by_attr("dpGuideNet")):
            last_number = int(self.ar.naming.find_last_number())
            for n in reversed(range(0, len(guide_data))):
                old_net_number = str(guide_data[list(guide_data.keys())[n]]['GuideNumber']).zfill(3)
                new_net_number = str(last_number+n).zfill(3)
                new_net_name = f"dpGuide_{new_net_number}_Net"
                guide_data = ast.literal_eval(str(guide_data).replace(f"__dpAR_{old_net_number}", f"__dpAR_{new_net_number}"))
                guide_data[new_net_name] = guide_data.pop(list(guide_data.keys())[n])
                guide_data[new_net_name]['GuideNumber'] = new_net_number
            guide_data = dict(sorted(guide_data.items()))
        return guide_data


    def import_guide(self, guide_data, rebuilding=True):
        """ Import guide info and initialize guide setting it attribute values.
        """
        well_imported = True
        to_initialize_guide = True
        ask_again = True
        self.correlations = {}
        self.ar.ui_manager.set_progress(max=len(guide_data.keys()), add_one=False, add_number=False)
        if self.ar.data.ui_state:
            self.ar.data.collapse_edit_sel_mod = True
            self.ar.filler.fill_created_guides()
        for net in guide_data.keys():
            if "moduleType" in guide_data[net].keys():
                if guide_data[net]["moduleType"] == self.head_deformer.headDeformerName:
                    well_imported = self.import_head_deformer(guide_data[net])
            else:
                if rebuilding:
                    if cmds.objExists(net):
                        if cmds.getAttr(net+".rawGuide"):
                           to_initialize_guide = False
                        else:
                           cmds.lockNode(net, lock=False)
                           cmds.delete(net)
                else: #problably template
                    net_data = self.get_nets_info()
                    for module_type in net_data.keys():
                        if to_initialize_guide:
                            if module_type == guide_data[net]["ModuleType"]:
                                net_custom_name = guide_data[net]["GuideData"][f"{module_type}__dpAR_{guide_data[net]['GuideNumber']}:Guide_Base"]["customName"]
                                if not net_custom_name is None:
                                    for item in net_data[module_type].keys():
                                        if net_data[module_type][item] == net_custom_name:
                                            if ask_again:
                                                # open dialog to confirm repeated net name:
                                                yes_text = self.ar.data.lang['i071_yes']
                                                no_text = self.ar.data.lang['i072_no']
                                                result = cmds.confirmDialog(title=self.name, message=f"{self.ar.data.lang['i364_repeatedNetName']}\n{net_custom_name}", 
                                                                            button=[yes_text, no_text], defaultButton=yes_text, cancelButton=no_text, dismissString=no_text)
                                                if result == yes_text: #skip them
                                                    to_initialize_guide = False
                                                    break
                                                else:
                                                    ask_again = False
                                                    break
                if to_initialize_guide:
                    try:
                        self.net_data = guide_data[net]
                        self.ar.ui_manager.set_progress(self.ar.data.lang[self.title]+': '+guide_data[net]['ModuleType'])
                        # create a module instance:
                        self.instance = self.ar.lib.initialize_library(self.net_data['ModuleType'], self.ar.data.standard_folder)[0]
                        self.correlations[f"{self.net_data['ModuleType']}__dpAR_{self.net_data['GuideNumber']}"] = self.instance.guide_namespace
                        self.instance.build_raw_guide()
                        self.setup_instance_changes(rebuilding)
                        self.setup_guide_transformations()
                        cmds.select(clear=True)
                    except Exception as e:
                        well_imported = False
                        self.fail_io(net+": "+str(e))
                        break
        if self.ar.data.ui_state:
            self.ar.data.collapse_edit_sel_mod = False
        return well_imported


    def import_head_deformer(self, hd_net):
        """ Process the headDeformer importing.
        """
        return self.head_deformer.create_head_def(hd_net["hdName"], hd_net["hdList"], ui=False)


    def get_new_name(self, name):
        if not cmds.objExists(name):
            base = name.split(":")[0]
            if base in self.correlations.keys():
                return name.replace(base, self.correlations[base])
        return name


    def get_nets_info(self):
        net_data = {}
        nets = self.ar.utils.get_network_by_attr("dpGuideNet")
        if nets:
            module_types = list(set([cmds.getAttr(f"{n}.moduleType") for n in nets]))
            for module_type in module_types:
                net_data[module_type] = {}
                for net in nets:
                    if cmds.getAttr(f"{net}.moduleType") == module_type:
                        net_data[module_type][net] = self.get_net_custom_name(net)
        return net_data
    

    def get_net_custom_name(self, net):
        if cmds.getAttr(f"{net}.rawGuide"):
            return cmds.getAttr(f"{cmds.listConnections(f'{net}.linkedNode', source=True, destination=False)[0]}.customName")
        return cmds.getAttr(f"{net}.guideName")
