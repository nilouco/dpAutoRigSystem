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
                        netList = None
                        if inputs:
                            netList = inputs
                        else:
                            netList = self.ar.utils.getNetworkNodeByAttr("dpGuideNet")
                            netList.extend(self.ar.utils.getNetworkNodeByAttr("dpHeadDeformerNet") or [])
                        if netList:
                            self.ar.job.unpin_guide(force=True)
                            self.export_json_file(self.getGuideDataDic(netList))
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
                            cmds.select(clear=True)
                    else: #import
                        # apply viewport xray
                        modelPanelList = cmds.getPanel(type="modelPanel")
                        for mp in modelPanelList:
                            cmds.modelEditor(mp, edit=True, xray=True)
                        guideDic = self.import_latest_json_file(self.get_exported_items())
                        if guideDic:
                            wellImported = False
                            try:
                                guide_data = self.parse_repeated_nets(guideDic)
                                wellImported = self.importGuide(guide_data)
                                self.setupGuideBaseParenting(guide_data)
                            except Exception as e:
                                if not wellImported: #guide initialization issue
                                    self.fail_io(self.ar.data.lang['m195_couldNotBeSet']+": "+str(e))
                                else: #parenting issue
                                    self.fail_io(self.ar.data.lang['m197_notPossibleParent']+": "+str(e))
                                wellImported = False
                            if wellImported:
                                self.well_done_io(self.latest_data_file)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                        cmds.select(clear=True)
                        # remove viewport xray
                        for mp in modelPanelList:
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


    def getGuideDataDic(self, netList, *args):
        """ Return a dictionary of the guide data to export it.
        """
        to_export_data = {}
        self.ar.utils.setProgress(max=len(netList), add_one=False, add_number=False)
        for net in netList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # mount a data with all data 
            if "afterData" in cmds.listAttr(net):
                if "rawGuide" in cmds.listAttr(net) and cmds.getAttr(net+".rawGuide"):
                    # get data from not rendered guide (rawGuide status on)
                    moduleInstanceInfoString = cmds.getAttr(cmds.listConnections(net+".linkedNode")[0]+".moduleInstanceInfo")
                    for moduleInstance in self.ar.data.guide_instances:
                        if str(moduleInstance) == moduleInstanceInfoString:
                            moduleInstance.serialize_guide(False) #serialize it without build it
                to_export_data[net] = ast.literal_eval(cmds.getAttr(net+".afterData"))
            elif "dpHeadDeformerNet" in cmds.listAttr(net):
                if not cmds.listConnections(net+".guideNet", source=True, destination=False):
                    to_export_data[net] = ast.literal_eval(cmds.getAttr(net+".netData"))
        return to_export_data


    def setupInstanceChanges(self, rebuilding=True, *args):
        """ Run instance code to Guide_Base node configuration or just set the simple attributes.
        """
        directionList = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        customAttrList = ["flip",
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
        for item in list(self.netDic["GuideData"]):
            new_item = self.get_new_name(item)
            if cmds.objExists(new_item):
                if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #main
                    for baseAttr in list(self.netDic["GuideData"][item]):
                        if baseAttr == "customName":
                            custom_name = self.netDic["GuideData"][item]["customName"]
                            if custom_name:
                                if not rebuilding: #template
                                    custom_name = self.ar.utils.get_translated_names(custom_name)
                                self.instance.set_guide_custom_name(custom_name)
                        elif baseAttr == "mirrorAxis":
                            cmds.setAttr(new_item+".mirrorAxis", self.netDic["GuideData"][item]["mirrorAxis"], type="string")
                            start = self.ar.utils.get_translated_names(self.netDic["GuideData"][item]["mirrorName"][0])
                            end = self.ar.utils.get_translated_names(self.netDic["GuideData"][item]["mirrorName"][-1])
                            cmds.setAttr(new_item+".mirrorName", f"{start} --> {end}", type="string")
                            self.instance.create_mirror_preview()
                        elif baseAttr == "articulation":
                            self.instance.set_articulation(self.netDic["GuideData"][item]["articulation"])
                        elif baseAttr == "nJoints":
                            self.instance.changeJointNumber(self.netDic["GuideData"][item]["nJoints"])
                        elif baseAttr == "type": #limb
                            self.instance.changeType(self.netDic["GuideData"][item]["type"])
                        elif baseAttr == "hasBend": #limb
                            self.instance.changeBend(self.netDic["GuideData"][item]["hasBend"])
                        elif baseAttr == "aimDirection": #eye
                            self.instance.changeAimDirection(directionList[(int(self.netDic["GuideData"][item]["aimDirection"]))])
                        elif baseAttr == "fatherB": #suspention
                            fatherBData = self.netDic["GuideData"][item]["fatherB"]
                            if fatherBData:
                                cmds.setAttr(item+".fatherB", fatherBData, type="string")
                        elif baseAttr == "geo": #wheel
                            geoData = self.netDic["GuideData"][item]["geo"]
                            if geoData:
                                cmds.setAttr(new_item+".geo", geoData, type="string")
                        #TODO: modernize rigType to rigStyle new code
                        elif baseAttr == "rigType": #all
                            rigTypeData = self.netDic["GuideData"][item]["rigType"]
                            if rigTypeData:
                                cmds.setAttr(new_item+".rigType", rigTypeData, type="string")
                                self.instance.rigType = rigTypeData
                        elif baseAttr == "style":  #to be compatible with old versions of style value 4 (quadruped extra control)
                            cmds.setAttr(new_item+"."+baseAttr, min(self.netDic["GuideData"][item][baseAttr], 2))
                        else: #just set simple attributes
                            if baseAttr in customAttrList:
                                cmds.setAttr(new_item+"."+baseAttr, self.netDic["GuideData"][item][baseAttr])
                        cmds.refresh()


    def setupGuideTransformations(self, *args):
        """ Work with guide transformations to put the transform as imported data.
        """
        for item in list(self.netDic["GuideData"]):
            if item in self.netDic["GuideData"].keys():
                new_item = self.get_new_name(item)
                if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #main
                    if cmds.listRelatives(new_item, parent=True):
                        cmds.parent(new_item, world=True)
                for attr in list(self.netDic["GuideData"][item]):
                    if attr in self.ar.data.transform_attrs:
                        if not cmds.getAttr(new_item+"."+attr, lock=True): #unlocked attribute
                            if not cmds.listConnections(new_item+"."+attr, destination=False, source=True): #without input connection
                                cmds.setAttr(new_item+"."+attr, self.netDic["GuideData"][item][attr])
                    cmds.refresh()


    def setupGuideBaseParenting(self, guideDic, *args):
        """ Rebuild the Guide_Base parenting.
        """
        for net in guideDic.keys():
            netDic = guideDic[net]
            if "GuideData" in netDic.keys():
                for item in list(netDic["GuideData"]):
                    new_item = self.get_new_name(item)
                    if cmds.objExists(new_item):
                        if "guideBase" in cmds.listAttr(new_item) and cmds.getAttr(new_item+".guideBase") == 1: #main
                            fatherNodeData = netDic["GuideData"][item]['FatherNode']
                            if fatherNodeData:
                                new_father = self.get_new_name(fatherNodeData)
                                if cmds.objExists(new_father):
                                    if not cmds.listRelatives(new_item, parent=True) or not cmds.listRelatives(new_item, parent=True)[0] == new_father:
                                        cmds.parent(new_item, new_father)


    def parse_repeated_nets(self, guideDic):
        if len(self.ar.utils.getNetworkNodeByAttr("dpGuideNet")):
            last_number = int(self.ar.utils.findLastNumber())
            for n in reversed(range(0, len(guideDic))):
                old_net_number = str(guideDic[list(guideDic.keys())[n]]['GuideNumber']).zfill(3)
                new_net_number = str(last_number+n).zfill(3)
                new_net_name = f"dpGuide_{new_net_number}_Net"
                guideDic = ast.literal_eval(str(guideDic).replace(f"__dpAR_{old_net_number}", f"__dpAR_{new_net_number}"))
                guideDic[new_net_name] = guideDic.pop(list(guideDic.keys())[n])
                guideDic[new_net_name]['GuideNumber'] = new_net_number
            guideDic = dict(sorted(guideDic.items()))
        return guideDic


    def importGuide(self, guideDic, rebuilding=True, *args):
        """ Import guide info and initialize guide setting it attribute values.
        """
        wellImported = True
        toInitializeGuide = True
        ask_again = True
        self.correlations = {}
        self.ar.utils.setProgress(max=len(guideDic.keys()), add_one=False, add_number=False)
        if self.ar.data.ui_state:
            self.ar.data.collapse_edit_sel_mod = True
            self.ar.filler.fill_created_guides()
        for net in guideDic.keys():
            if "moduleType" in guideDic[net].keys():
                if guideDic[net]["moduleType"] == self.head_deformer.headDeformerName:
                    wellImported = self.importHeadDeformer(guideDic[net])
            else:
                if rebuilding:
                    if cmds.objExists(net):
                        if cmds.getAttr(net+".rawGuide"):
                           toInitializeGuide = False
                        else:
                           cmds.lockNode(net, lock=False)
                           cmds.delete(net)
                else: #problably template
                    net_data = self.get_nets_info()
                    for module_type in net_data.keys():
                        if toInitializeGuide:
                            if module_type == guideDic[net]["ModuleType"]:
                                net_custom_name = guideDic[net]["GuideData"][f"{module_type}__dpAR_{guideDic[net]['GuideNumber']}:Guide_Base"]["customName"]
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
                                                    toInitializeGuide = False
                                                    break
                                                else:
                                                    ask_again = False
                                                    break
                if toInitializeGuide:
                    try:
                        self.netDic = guideDic[net]
                        self.ar.utils.setProgress(self.ar.data.lang[self.title]+': '+guideDic[net]['ModuleType'])
                        # create a module instance:
                        self.instance = self.ar.lib.initialize_library(self.netDic['ModuleType'], self.ar.data.standard_folder)[0]
                        self.correlations[f"{self.netDic['ModuleType']}__dpAR_{self.netDic['GuideNumber']}"] = self.instance.guide_namespace
                        self.instance.build_raw_guide()
                        self.setupInstanceChanges(rebuilding)
                        self.setupGuideTransformations()
                        cmds.select(clear=True)
                    except Exception as e:
                        wellImported = False
                        self.fail_io(net+": "+str(e))
                        break
        if self.ar.data.ui_state:
            self.ar.data.collapse_edit_sel_mod = False
        return wellImported


    def importHeadDeformer(self, hdNet, *args):
        """ Process the headDeformer importing.
        """
        return self.head_deformer.dpHeadDeformer(hdNet["hdName"], hdNet["hdList"], ui=False)


    def get_new_name(self, name):
        if not cmds.objExists(name):
            base = name.split(":")[0]
            if base in self.correlations.keys():
                return name.replace(base, self.correlations[base])
        return name


    def get_nets_info(self):
        net_data = {}
        nets = self.ar.utils.getNetworkNodeByAttr("dpGuideNet")
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
