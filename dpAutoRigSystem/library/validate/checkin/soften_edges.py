# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "SoftenEdges"
TITLE = "v088_softenEdges"
DESCRIPTION = "v089_softenEdgesDesc"
WIKI = "07-‐-Validator#-soften-edges"



class SoftenEdges(action.BaseAction):
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
        if not cmds.file(query=True, reference=True):
            if objList:
                allMeshList = objList
            else:
                allMeshList = cmds.ls(selection=False, type="mesh")
            if allMeshList:
                self.ar.utils.setProgress(max=len(allMeshList), addOne=False, addNumber=False)
                for mesh in allMeshList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if cmds.objExists(mesh):
                        cmds.select(mesh)
                        # set selection only non-smoothed edges
                        cmds.polySelectConstraint(type=0x8000, mode=3, smoothness=1)
                        hardenEdges = cmds.ls(selection=True)
                        cmds.polySelectConstraint(mode=0)
                        if hardenEdges:
                            # converts the selected edges to faces
                            toFace = cmds.polyListComponentConversion(hardenEdges, toFace=True, internal=True)
                            # check if there's any non-smoothed edges
                            if toFace:
                                self.checked_items.append(mesh)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    try:
                                        cmds.polySoftEdge(mesh, angle=180, constructionHistory=False)
                                        self.good_results.append(True)
                                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+mesh)
                                    except:
                                        self.good_results.append(False)
                                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+mesh)
                        cmds.select(clear=True)
        
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        return self.log_data