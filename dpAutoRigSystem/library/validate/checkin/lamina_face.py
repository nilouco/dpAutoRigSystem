# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "LaminaFace"
TITLE = "v124_laminaFace"
DESCRIPTION = "v125_laminaFaceDesc"
WIKI = "07-‐-Validator#-lamina-face-cleaner"



class LaminaFace(action.BaseAction):
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
                lamina_items, lamina_faces = [], []
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
                                # get faces
                                iter_face   = OpenMaya.MItMeshPolygon(shape)
                                con_faces_it = OpenMaya.MItMeshPolygon(shape)
                                # run in faces listing edges
                                while not iter_face.isDone():
                                    # list vertices from this face
                                    edges_int_array = OpenMaya.MIntArray()
                                    iter_face.getEdges(edges_int_array)
                                    # get connected faces of this face
                                    con_faces_int_array = OpenMaya.MIntArray()
                                    iter_face.getConnectedFaces(con_faces_int_array)
                                    # run in adjacent faces to list them vertices
                                    for f in con_faces_int_array:
                                        # say this is the face index to use for next iterations
                                        last_index_ptr = OpenMaya.MScriptUtil().asIntPtr()
                                        con_faces_it.setIndex(f, last_index_ptr)
                                        # get edges from this adjacent face
                                        con_edges_int_array = OpenMaya.MIntArray()
                                        con_faces_it.getEdges(con_edges_int_array)
                                        # compare edges to verify if the list are the same
                                        if sorted(edges_int_array) == sorted(con_edges_int_array):
                                            # found laminaFaces
                                            if not item_name in lamina_items:
                                                lamina_items.append(item_name)
                                            lamina_faces.append(item_name+'.f['+str(iter_face.index())+']')
                                    iter_face.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if lamina_items:
                    lamina_items.sort()
                    lamina_faces.sort()
                    for item in lamina_items:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                            self.messages.append("Lamina faces: "+str(lamina_faces))
                            cmds.select(lamina_faces)
                        else: #fix
                            try:
                                cmds.select(item)
                                mel.eval('polyCleanupArgList 3 { \"0\",\"1\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"-1\",\"1\" };')
                                cmds.select(clear=True)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+" - Faces: "+", ".join(lamina_faces))
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+" - Faces: "+", ".join(lamina_faces))
                    if self.first_mode:
                        self.messages.append("Lamina faces: "+str(lamina_faces))
                        self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(lamina_faces)+")\n---")
                        cmds.select(lamina_faces)
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
