# importing libraries:
from maya import cmds
from ....library.base import action
from ....library.util import weights
from importlib import reload

# global variables to this module:
CLASS_NAME = "ComponentTagIO"
TITLE = "r048_componentTagIO"
DESCRIPTION = "r049_componentTagIODesc"
WIKI = "10-‐-Rebuilder#-componenttag"



class ComponentTagIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_componentTagIO"
        self.start_name = "dpComponentTag"
        if self.ar.dev:
            reload(weights)
        self.defWeights = weights.Weights(self.ar)
    

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
            if self.ar.pipeliner.checkAssetContext():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    nodeList = None
                    if objList:
                        nodeList = objList
                    else:
                        nodeList = cmds.listRelatives(cmds.ls(selection=False, type=["mesh", "lattice"]), parent=True)
                    if self.first_mode: #export
                        if nodeList:
                            # finding tags
                            hasTag = False
                            for node in nodeList:
                                if cmds.geometryAttrInfo(node+"."+cmds.deformableShape(node, localShapeOutAttr=True)[0], componentTagHistory=True):
                                    hasTag = True
                                    break
                            if hasTag:
                                # Declaring the data dictionary to export it
                                self.tagDataDic = { "tagged"     : self.defWeights.getComponentTagInfo(nodeList),
                                                    "influencer" : self.defWeights.getComponentTagInfluencer(),
                                                    "falloff"    : self.defWeights.getComponentTagFalloff()
                                                }
                                self.export_json_file(self.tagDataDic)
                            else:
                                self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" componentTag")
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" mesh, lattice")
                    else: #import
                        tagDataDic = self.import_latest_json_file(self.get_exported_items())
                        if tagDataDic:
                            self.importTag(tagDataDic, nodeList)
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
        cmds.select(clear=True)
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def importTag(self, tagDataDic, nodeList, *args):
        """ Import componentTag data.
        """
        fail = False
        # import tagged (tag info into the received deformed mesh)
        if tagDataDic["tagged"]:
            if not self.defWeights.importComponentTagInfo(tagDataDic["tagged"], nodeList):
                self.fail_io(self.latest_data_file+": tagged - "+", ".join(self.defWeights.notWorkWellInfoList))
                fail = True
        # import influencers (tag info into the deformer node)
        if tagDataDic["influencer"]:
            if not self.defWeights.importComponentTagInfluencer(tagDataDic["influencer"]):
                self.fail_io(self.latest_data_file+": influencer - "+", ".join(self.defWeights.notWorkWellInfoList))
                fail = True
        # import falloffs
        if tagDataDic["falloff"]:
            if not self.defWeights.importComponentTagFalloff(tagDataDic["falloff"]):
                self.fail_io(self.latest_data_file+": falloff - "+", ".join(self.defWeights.notWorkWellInfoList))
                fail = True
        if not fail:
            self.well_done_io(self.latest_data_file)
