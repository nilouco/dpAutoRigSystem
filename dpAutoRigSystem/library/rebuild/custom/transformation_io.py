# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "TransformationIO"
TITLE = "r037_transformationIO"
DESCRIPTION = "r038_transformationIODesc"
WIKI = "10-‐-Rebuilder#-transformation"



class TransformationIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_transformationIO"
        self.start_name = "dpTransformation"
    

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
                            items = cmds.ls(selection=False, long=True, type="transform")
                        if items:
                            self.export_json_file(self.get_transform_data(items))
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
                    else: #import
                        transform_data = self.import_latest_json_file(self.get_exported_items())
                        if transform_data:
                            self.import_transformation(transform_data)
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


    def get_transform_data(self, items):
        """ Return the transform data info to export.
        """
        self.ar.ui_manager.set_progress(max=len(items), add_one=False, add_number=False)
        # define dictionary to export
        transform_data = {}
        items = self.ar.utils.filter_transforms(items, filter_lattice=False, filter_basename=False, verbose=self.ar.data.verbose, title=self.ar.data.lang[self.title])
        for item in items:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            use_this_transform = True
            if cmds.objExists(item+".dpNotTransformIO"):
                if cmds.getAttr(item+".dpNotTransformIO") == 1:
                    use_this_transform = False
            if use_this_transform:
                data = self.get_transformation(item)
                data.update(self.get_limit(item))
                if data:
                    transform_data[item] = data
        return transform_data


    def get_transformation(self, item):
        """ Returns a dictionary with the transformation attribute values of the given transform node.
        """
        data = {}
        need_run_get = True
        for attr, default in zip(["tx", "ty",  "tz",  "rx",  "ry",  "rz",  "sx",  "sy",  "sz"], [0, 0, 0, 0, 0, 0, 1, 1, 1]):
            value = cmds.getAttr(item+"."+attr)
            if not value == default:
                if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                    if need_run_get:
                        data = { 
                                "transform" : {},
                                "matrix" : cmds.xform(item, query=True, worldSpace=False, matrix=True)
                                }
                        need_run_get = False
                    data["transform"][attr] = cmds.getAttr(item+"."+attr)
        return data


    def get_limit(self, item):
        """ Returns a dictionary with the transformation limits if there are.
        """
        data = {}
        enables = []
        enable_attributes = ["enableTranslationX", "enableTranslationY", "enableTranslationZ", "enableRotationX", "enableRotationY", "enableRotationZ", "enableScaleX", "enableScaleY", "enableScaleZ"]
        enables.append(cmds.transformLimits(item, enableTranslationX=True, query=True))
        enables.append(cmds.transformLimits(item, enableTranslationY=True, query=True))
        enables.append(cmds.transformLimits(item, enableTranslationZ=True, query=True))
        enables.append(cmds.transformLimits(item, enableRotationX=True, query=True))
        enables.append(cmds.transformLimits(item, enableRotationY=True, query=True))
        enables.append(cmds.transformLimits(item, enableRotationZ=True, query=True))
        enables.append(cmds.transformLimits(item, enableScaleX=True, query=True))
        enables.append(cmds.transformLimits(item, enableScaleY=True, query=True))
        enables.append(cmds.transformLimits(item, enableScaleZ=True, query=True))
        has_true = [i for i in enables if True in i]
        if has_true:
            limits = []
            #limitAttrList = ["translationX", "translationY", "translationZ", "rotationX", "rotationY", "rotationZ", "scaleX", "scaleY", "scaleZ"]
            limits.append(cmds.transformLimits(item, translationX=True, query=True))
            limits.append(cmds.transformLimits(item, translationY=True, query=True))
            limits.append(cmds.transformLimits(item, translationZ=True, query=True))
            limits.append(cmds.transformLimits(item, rotationX=True, query=True))
            limits.append(cmds.transformLimits(item, rotationY=True, query=True))
            limits.append(cmds.transformLimits(item, rotationZ=True, query=True))
            limits.append(cmds.transformLimits(item, scaleX=True, query=True))
            limits.append(cmds.transformLimits(item, scaleY=True, query=True))
            limits.append(cmds.transformLimits(item, scaleZ=True, query=True))
            data = {"limit" : {}}
            for e, enable_attr in enumerate(enable_attributes):
                if True in enables[e]:
                    data["limit"][enable_attr] = [
                                                int(enables[e][0]), #minEnable
                                                int(enables[e][1]), #maxEnable
                                                limits[e][0], #minValue
                                                limits[e][1] #maxValue
                                            ]
        return data


    def import_transformation(self, transform_data):
        """ Import transfomation data from given dictionary.
        """
        self.ar.ui_manager.set_progress(max=len(transform_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in transform_data.keys():
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            not_found_nodes = []
            # check transform
            #if not cmds.objExists(item):
            #    item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                ran = False
                if "transform" in transform_data[item].keys():
                    ran = True
                    for attr in transform_data[item]["transform"].keys():
                        if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                            # unlock attribute
                            was_locked = cmds.getAttr(item+"."+attr, lock=True)
                            cmds.setAttr(item+"."+attr, lock=False)
                            try:
                                # set transformation value
                                cmds.setAttr(item+"."+attr, transform_data[item]["transform"][attr])
                                # lock attribute again if it was locked
                                cmds.setAttr(item+"."+attr, lock=was_locked)
                                if not item in well_imported_items:
                                    well_imported_items.append(item)
                            except Exception as e:
                                self.fail_io(item+" - "+str(e))
                    cmds.xform(item, worldSpace=False, matrix=transform_data[item]["matrix"])
                if "limit" in transform_data[item].keys():
                    ran = True
                    for limit_attr in transform_data[item]["limit"].keys():
                        try:
                            if limit_attr == "enableTranslationX":
                                cmds.transformLimits(item, enableTranslationX=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], translationX=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableTranslationY":
                                cmds.transformLimits(item, enableTranslationY=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], translationY=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableTranslationZ":
                                cmds.transformLimits(item, enableTranslationZ=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], translationZ=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableRotationX":
                                cmds.transformLimits(item, enableRotationX=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], rotationX=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableRotationY":
                                cmds.transformLimits(item, enableRotationY=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], rotationY=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableRotationZ":
                                cmds.transformLimits(item, enableRotationZ=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], rotationZ=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableScaleX":
                                cmds.transformLimits(item, enableScaleX=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], scaleX=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableScaleY":
                                cmds.transformLimits(item, enableScaleY=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], scaleY=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                            elif limit_attr == "enableScaleZ":
                                cmds.transformLimits(item, enableScaleZ=[transform_data[item]["limit"][limit_attr][0], transform_data[item]["limit"][limit_attr][1]], scaleZ=[transform_data[item]["limit"][limit_attr][2], transform_data[item]["limit"][limit_attr][3]])
                        except Exception as e:
                            self.fail_io(item+" - "+str(e))
                if not ran:
                    self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
            else:
                not_found_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
