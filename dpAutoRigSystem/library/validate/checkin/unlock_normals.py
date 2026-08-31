# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action
from ....library.util import edge_normals
from importlib import reload


# global variables to this module:
CLASS_NAME = "UnlockNormals"
TITLE = "v078_unlockNormals"
DESCRIPTION = "v079_unlockNormalsDesc"
WIKI = "07-‐-Validator#-unlock-normals"



class UnlockNormals(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(edge_normals)
        self.softHardEdges = edge_normals.ConvertNormals(self.ar)
    

    def run_action(self, first_mode=True, inputs=None, *args):
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
            if inputs:
                allMeshList = inputs
            else:
                allMeshList = cmds.ls(selection=False, type='mesh')
            if allMeshList:
                self.ar.utils.setProgress(max=len(allMeshList), add_one=False, add_number=False)
                for mesh in allMeshList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if cmds.objExists(mesh):
                        lockedList = cmds.polyNormalPerVertex(mesh+".vtx[*]", query=True, freezeNormal=True)
                        # check if there's any locked normal
                        if True in lockedList:
                            self.checked_items.append(mesh)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    #cmds.polyNormalPerVertex(mesh+".vtx[*]", unFreezeNormal=True) #it doesn't keep the soft and hard edges when importing mesh
                                    self.softHardEdges.set_soft_hard(mesh)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+mesh)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+mesh)
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data