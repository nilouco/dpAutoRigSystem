# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action
from importlib import reload

# global variables to this module:
CLASS_NAME = "BorderGap"
TITLE = "v122_borderGap"
DESCRIPTION = "v123_borderGapDesc"
WIKI = "07-‐-Validator#-border-gap"



class BorderGap(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(action)


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
                check_items = cmds.ls(inputs, type="mesh")
            else:
                check_items = cmds.ls(selection=False, type="mesh")
            if check_items:
                self.ar.ui_manager.set_progress(max=len(check_items), add_one=False, add_number=False)
                # declare resulted lists
                gap_components, gap_items = [], []
                iter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kGeometric)
                if iter != None:
                    while not iter.isDone():
                        # get mesh data
                        shape = iter.thisNode()
                        fn_shape_node = OpenMaya.MFnDagNode(shape)
                        shape_name = fn_shape_node.name()
                        parent_node = fn_shape_node.parent(0)
                        fn_parent_node = OpenMaya.MFnDagNode(parent_node)
                        item_name = fn_parent_node.name()
                        # verify if objName or shape_name is in check_items
                        for item in check_items:
                            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                            if item == shape_name and not cmds.getAttr(item+".intermediateObject"):
                                iter_polys = OpenMaya.MItMeshEdge(shape)
                                # Iterate through polys on current mesh
                                while not iter_polys.isDone():
                                    # Get current polygons connected faces
                                    index_con_faces = OpenMaya.MIntArray()
                                    iter_polys.getConnectedFaces(index_con_faces)
                                    if len(index_con_faces) == 1:
                                        if not item_name in gap_items:
                                            gap_items.append(item_name)
                                        gap_components.append(item_name+'.e['+str(iter_polys.index())+']')
                                    # Move to next polygon in the mesh list
                                    iter_polys.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if gap_items:
                    gap_items.sort()
                    for item in gap_items:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    self.messages.append(self.ar.data.lang['v122_borderGap']+": "+str(gap_components))
                    self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(gap_components)+")\n---")
                    cmds.select(gap_components)
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
