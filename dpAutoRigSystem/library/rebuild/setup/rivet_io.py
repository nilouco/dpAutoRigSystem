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
    

    def runAction(self, first_mode=True, objList=None, *args):
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
                        netList = None
                        if objList:
                            netList = objList
                        else:
                            netList = self.ar.utils.getNetworkNodeByAttr("dpRivetNet")
                        if netList:
                            self.export_json_file(self.getRivetDataDic(netList))
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
                            cmds.select(clear=True)
                    else: #import
                        rivetDic = self.import_latest_json_file(self.get_exported_items())
                        if rivetDic:
                            self.importRivet(rivetDic)
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


    def getRivetDataDic(self, netList, *args):
        """ Processes the given rivet network list and mount the right info pack to rebuild the module.
            Returns the dictionary to export.
        """
        dic = {}
        self.ar.utils.setProgress(max=len(netList), add_one=False, add_number=False)
        i = 0
        for n, net in enumerate(netList):
            if self.ar.data.verbose:
                self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # mount a dic
            if cmds.objExists(net+".rivetData"):
                data = json.loads(cmds.getAttr(net+".rivetData"))
                addIt = True
                if n > 0:
                    for x in range(0, i):
                        if data["itemNode"] in dic[x]["items"]:
                            addIt = False
                            break
                if addIt:
                    dic[i] = data
                    i += 1
        return dic


    def importRivet(self, rivetDic, *args):
        """ Import rivet data creating new instances with exported attribute values.
        """
        wellImported = True
        self.ar.utils.setProgress(max=len(rivetDic.keys()), add_one=False, add_number=False)
        for net in rivetDic.keys():
            try:
                netDic = rivetDic[net]
                self.ar.utils.setProgress(self.ar.data.lang[self.title]+': '+netDic['geoToAttach'])
                old_ui_state = self.ar.data.ui_state
                self.ar.data.ui_state = False
                # recreate rivet:
                self.rivet.deformerToUse = netDic['deformerToUse']
                rivetList = self.rivet.dpCreateRivet(netDic['geoToAttach'], netDic['uvSetName'], netDic['items'], netDic['attachTranslate'], netDic['attachRotate'], netDic['addFatherGrp'], netDic['addInvert'], netDic['invT'], netDic['invR'], netDic['faceToRivet'], netDic['rivetGrpName'], netDic['askComponent'], netDic['useOffset'], netDic['reuseFaceToRivet'])
                self.ar.data.ui_state = old_ui_state
                if not rivetList:
                    wellImported = False
                    self.fail_io(net+": "+self.ar.data.lang['r032_notImportedData'])
            except Exception as e:
                wellImported = False
                self.fail_io(net+": "+str(e))
                break
        if wellImported:
            self.well_done_io(self.latest_data_file)
