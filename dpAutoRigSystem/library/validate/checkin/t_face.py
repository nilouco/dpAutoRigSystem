# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "TFace"
TITLE = "v128_tFace"
DESCRIPTION = "v129_tFaceDesc"
WIKI = "07-‐-Validator#-t-face-cleaner"



class TFace(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

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
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                # declare resulted lists
                t_faces = []
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
                            self.ar.utils.set_progress(self.ar.data.lang[self.title])
                            if item == shape_name and not cmds.getAttr(item+".intermediateObject"):
                                # get edges
                                iter_edge = OpenMaya.MItMeshEdge(shape)
                                # run in faces listing faces
                                while not iter_edge.isDone():
                                    # list faces from this edge
                                    face_int_array = OpenMaya.MIntArray()
                                    iter_edge.getConnectedFaces(face_int_array)
                                    # verify the lenght of the connectedFaces
                                    if len(face_int_array) > 2:
                                        # found tFace
                                        t_faces.append(item_name+".e["+str(iter_edge.index())+"]")
                                    iter_edge.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if t_faces:
                    t_faces.sort()
                    for item in t_faces:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                cmds.select(item)
                                # Cleanup T Faces
                                mel.eval('polyCleanupArgList 3 { \"0\",\"1\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"2\",\"0\" };')
                                cmds.select(clear=True)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    if self.first_mode:
                        cmds.select(t_faces)
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
