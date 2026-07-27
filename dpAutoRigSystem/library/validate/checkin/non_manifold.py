# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "NonManifold"
TITLE = "v101_nonManifold"
DESCRIPTION = "v102_nonManifoldDesc"
WIKI = "07-‐-Validator#-nonmanifold-cleaner"



class NonManifold(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def runAction(self, first_mode=True, objList=None, *args):
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
        if not self.ar.utils.getAllGrp():
            if not self.ar.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    if objList:
                        geoToCleanList = objList
                    else:
                        geoToCleanList = cmds.ls(list(set(self.checkNonManifold(self.getMeshTransformList()))), long=False)
                    if geoToCleanList:
                        self.ar.utils.setProgress(max=len(geoToCleanList), addOne=False, addNumber=False)
                        for geo in geoToCleanList:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if cmds.objExists(geo):
                                self.checked_items.append(geo)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    try:
                                        cmds.select(geo)
                                        # Cleanup non manifolds
                                        mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')
                                        self.good_results.append(True)
                                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+geo)
                                        mel.eval('changeSelectMode -object;')
                                        cmds.select(clear=True)
                                    except:
                                        self.good_results.append(False)
                                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+geo)
                    else:
                        self.not_found_node()
                else:
                    self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
            else:
                self.fail_io(self.ar.data.lang['v100_cantExistsGuides'])
        else:
            self.fail_io(self.ar.data.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        return self.log_data


    def checkNonManifold(self, itemList, *args):
        """ Verify if there are non manifold meshes and return them if exists.
        """
        nonManifoldList = []
        if itemList:
            for item in itemList:
                if cmds.polyInfo(item, nonManifoldEdges=True, nonManifoldUVEdges=True, nonManifoldUVs=True, nonManifoldVertices=True):
                    nonManifoldList.append(item)
        return nonManifoldList
