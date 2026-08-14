# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "BlendshapeIO"
TITLE = "r030_blendShapeIO"
DESCRIPTION = "r031_blendShapeIODesc"
WIKI = "10-‐-Rebuilder#-blendshape"



class BlendshapeIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_blendShapeIO"
        self.start_name = "dpBlendShape"
        self.target_name = "dpTarget"
        self.original_name = "dpOriginal"
        self.extention = "shp"
    

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
                # load alembic plugin
                if self.ar.utils.checkLoadedPlugin("AbcExport") and self.ar.utils.checkLoadedPlugin("AbcImport"):
                    self.io_path = self.get_io_path(self.io_folder)
                    self.target_path = self.io_path+"/"+self.target_name
                    self.original_path = self.io_path+"/"+self.original_name
                    if self.io_path:
                        if self.first_mode: #export
                            bs_items = None
                            if inputs:
                                bs_items = inputs
                            else:
                                bs_items = [n for n in cmds.ls(selection=False, type="blendShape") if cmds.blendShape(n, query=True, geometry=True)]
                            if bs_items:
                                bs_data = self.get_bs_data(bs_items)
                                for bs_node in bs_items:
                                    self.export_target_file(bs_node)
                                    transforms = [cmds.listRelatives(geoShape, parent=True, type="transform")[0] for geoShape in bs_data[bs_node]["geometry"]]
                                    self.export_alembic_file(transforms, self.original_path, self.original_name, bs_node, False)
                                self.export_json_file(bs_data)
                            else:
                                self.maybe_done_io("BlendShapes_Grp")
                        else: #import
                            bs_data = self.import_latest_json_file(self.get_exported_items())
                            if bs_data:
                                self.import_blendshapes(bs_data)
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.fail_io(self.ar.data.lang['r010_notFoundPath'])
                else:
                    self.fail_io(self.ar.data.lang['e018_notLoadedPlugin']+"AbcExport")
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


    def get_bs_data(self, bs_items):
        """ Return the blendShape data dictionary to export info.
        """
        bs_data = {}
        self.ar.utils.setProgress(max=len(bs_items), add_one=False, add_number=False)
        for bs_node in bs_items:
            self.ar.utils.setProgress(self.ar.data.lang[self.title]+": "+bs_node)
            bs_data[bs_node] = {}
            bs_data[bs_node]["targets"] = {}
            # get blendShape node info
            bs_data[bs_node]['geometry'] = cmds.blendShape(bs_node, query=True, geometry=True)
            bs_data[bs_node]['envelope'] = cmds.getAttr(bs_node+".envelope")
            bs_data[bs_node]['supportNegativeWeights'] = cmds.getAttr(bs_node+".supportNegativeWeights")
            targets = cmds.listAttr("{}.weight".format(bs_node), multi=True)
            if targets:
                # prepare index to deleted targets
                indexes = cmds.getAttr("{}.weight".format(bs_node), multiIndices=True)
                bs_data[bs_node]["indexTargetDic"] = dict(zip(indexes, targets))
                deleted_indexes = []
                i = 0 #workaround to avoid deleted target index when importing data
                for t, target in enumerate(targets):
                    weight_data = {}
                    combination = False
                    combination_method = None
                    combinations = []
                    unit_conversion_factor = None
                    unit_conversion_input_plug = None
                    plug = cmds.listConnections(bs_node+"."+target, destination=False, source=True, plugs=True)
                    if plug:
                        plug_node = plug[0][:plug[0].find(".")]
                        if cmds.objectType(plug_node) == "combinationShape":
                            combination = True
                            combination_method = cmds.getAttr(plug_node+".combinationMethod")
                            input_weights = cmds.listAttr(plug_node+".inputWeight", multi=True)
                            if input_weights:
                                for input_weight in input_weights:
                                    combinations.append(cmds.listConnections(plug_node+"."+input_weight, destination=False, source=True, plugs=True)[0])
                        elif cmds.objectType(plug_node) == "unitConversion":
                            unit_conversion_factor = cmds.getAttr(plug_node+".conversionFactor")
                            unit_conversion_input_plug = cmds.listConnections(plug_node+".input", destination=False, source=True, plugs=True)[0]
                    # getting vertex weights if not equal to 1
                    for s, shape in enumerate(bs_data[bs_node]["geometry"]):
                        # write deleted target to compose a clear target list to avoid Maya's garbage issue
                        while not i == indexes[t]:
                            bs_data[bs_node]["targets"][i] = {"deleted" : True}
                            deleted_indexes.append(i)
                            i += 1
                        # continue writing relevant or just info data
                        vertices = cmds.polyEvaluate(shape, vertex=True)
                        if type(vertices) == "int": #to accept non polygon blendShapes like curves by Zipper
                            raw_weights = cmds.getAttr("{}.inputTarget[{}].inputTargetGroup[{}].targetWeights[0:{}]".format(bs_node, s, t, vertices-1))
                            if not len(raw_weights) == raw_weights.count(1.0):
                                for w, weight in enumerate(raw_weights):
                                    if not weight == 1.0:
                                        weight_data[w] = weight
                    # data dictionary to export
                    bs_data[bs_node]["targets"][i] = { "name"           : target,
                                                    "deleted"        : False,
                                                    "regenerate"     : cmds.objExists(target),
                                                    "value"          : cmds.getAttr(bs_node+"."+target),
                                                    "plug"           : plug,
                                                    "comb"           : combination,
                                                    "combMethod"     : combination_method,
                                                    "combList"       : combinations,
                                                    "unitConvFactor" : unit_conversion_factor,
                                                    "unitConvInput"  : unit_conversion_input_plug,
                                                    "weightDic"      : weight_data
                                                    }
                    bs_data[bs_node]["deletedIndexList"] = deleted_indexes
                    i += 1
        return bs_data


    def export_target_file(self, bs_node):
        """ Export the given blendShape target.
        """
        try:
            self.ar.pipeliner.make_dir_if_not_exists(self.target_path)
            # export blendShape targets as compiled maya file
            cmds.blendShape(bs_node, edit=True, export=self.target_path+"/"+self.target_name+"_"+bs_node+"."+self.extention)
        except Exception as e:
            self.fail_io(str(e))


    def import_blendshapes(self, bs_data):
        """ Import blendShapes from given exported list getting the latest file.
        """
        well_imported = True
        # not working scriptEditor suppress command...
        suppress_warnings_state = cmds.scriptEditorInfo(query=True, suppressWarnings=True)
        suppress_info_state = cmds.scriptEditorInfo(query=True, suppressInfo=True)
        suppress_errors_state = cmds.scriptEditorInfo(query=True, suppressErrors=True)
        suppress_results_state = cmds.scriptEditorInfo(query=True, suppressResults=True)
        cmds.scriptEditorInfo(suppressWarnings=True, suppressInfo=True, suppressErrors=True, suppressResults=True)
        # rebuild blendShapes
        for bs_node in bs_data.keys():
            # import alembic original mesh if it doesn't exists
            original_shapes = bs_data[bs_node]["geometry"]
            for original_shape in original_shapes:
                if not cmds.objExists(original_shape):
                    try:
                        abc_to_import = self.original_path+"/"+self.original_name+"_"+bs_node+".abc"
                        mel.eval("AbcImport -mode import \""+abc_to_import+"\";")
                    except:
                        self.fail_io(self.ar.data.lang["r032_notImportedData"]+": "+self.original_name+"_"+bs_node+".abc")
                        well_imported = False
            if not cmds.objExists(bs_node):
                # create an empty blendShape node
                cmds.blendShape(original_shapes, name=bs_node)
                cmds.setAttr(bs_node+".envelope", bs_data[bs_node]["envelope"])
                cmds.setAttr(bs_node+".supportNegativeWeights", bs_data[bs_node]["supportNegativeWeights"])
                # import targets
                try:
                    # OMG!
                    print("--------------------------------\nStarting Autodesk not suppressed messages, sorry!\n--------------------------------\n")
                    cmds.blendShape(bs_node, edit=True, ip=self.target_path+"/"+self.target_name+"_"+bs_node+"."+self.extention)
                    #mel.eval('catchQuiet(`blendShape -edit -ip "'+self.target_path+'/'+self.target_name+'_'+bs_node+'.'+self.extention+'" '+bs_node+'`);')
                    print("--------------------------------\nEnding Autodesk not suppressed messages, sorry!\n--------------------------------\n")
                except Exception as e:
                    self.fail_io(self.ar.data.lang["r032_notImportedData"]+": "+self.target_name+"_"+bs_node+"."+self.extention+" - "+str(e))
                    well_imported = False
            for i in list(bs_data[bs_node]["indexTargetDic"].keys()):
                target = bs_data[bs_node]["indexTargetDic"][i]
                # set target value
                try:
                    cmds.setAttr(bs_node+"."+target, bs_data[bs_node]["targets"][i]["value"])
                except:
                    pass #connected combination target
                # set target weights
                for s, shape in enumerate(bs_data[bs_node]["geometry"]):
                    for idx in list(bs_data[bs_node]["targets"][i]["weightDic"].keys()):
                        cmds.setAttr("{}.inputTarget[{}].inputTargetGroup[{}].targetWeights[{}]".format(bs_node, s, i, idx), bs_data[bs_node]["targets"][i]["weightDic"][idx])
                # regenerate target
                if bs_data[bs_node]["targets"][i]["regenerate"]:
                    tgt_already_exists = cmds.objExists(target)
                    tgt = cmds.sculptTarget(bs_node, edit=True, regenerate=True, target=int(i))[0]
                    if tgt_already_exists:
                        tgt = cmds.rename("|"+tgt, "dpTemp_"+tgt)
                        if cmds.listConnections(cmds.listRelatives(tgt, children=True, type="mesh")):
                            plug_out = cmds.listConnections(cmds.listRelatives(tgt, children=True, type="mesh")[0]+".worldMesh[0]", destination=True, source=False, plugs=True)[0]
                            cmds.connectAttr(cmds.listRelatives(target, children=True, type="mesh")[0]+".worldMesh[0]", plug_out, force=True)
                        #elif cmds.listConnections(cmds.listRelatives(tgt, children=True, type="shape")):
                            #TODO edit to accept nurbsShape blendShapes like Zipper
                        cmds.delete(tgt)
                    else:
                        cmds.rename(cmds.listRelatives(tgt, children=True, type="mesh")[0], bs_data[bs_node]["targets"][i]["name"]+"Shape")

                # TODO
                    # fix double original mesh / import double targets by group issue = Maya 2024 bug, supposed fixed on Maya 2025
                    # remove script editor messages from import targets

            for d in bs_data[bs_node]["deletedIndexList"]:
                cmds.removeMultiInstance("{}.weight[{}]".format(bs_node, d), b=True) #doing nothing... I don't know why, sorry. Maya2024.2 at 2024-03-24
        cmds.scriptEditorInfo(suppressWarnings=suppress_warnings_state, suppressInfo=suppress_info_state, suppressErrors=suppress_errors_state, suppressResults=suppress_results_state)
        if well_imported:
            self.well_done_io(self.latest_data_file)
