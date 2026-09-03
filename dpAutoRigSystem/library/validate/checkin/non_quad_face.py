# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "NonQuadFace"
TITLE = "v119_nonQuadFace"
DESCRIPTION = "v120_nonQuadFaceDesc"
WIKI = "07-‐-Validator#-non-quad-face"



class NonQuadFace(action.BaseAction):
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
                self.ar.ui_manager.set_progress(max=len(check_items), add_one=False, add_number=False)
                # declare resulted lists
                poly_items, tris_items, tris_faces, poly_faces = [], [], [], []
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
                                iter_polys = OpenMaya.MItMeshPolygon(shape)
                                # Iterate through polys on current mesh
                                while not iter_polys.isDone():
                                    n_vertex = iter_polys.polygonVertexCount()
                                    if n_vertex > 4:
                                        if not item_name in poly_items:
                                            poly_items.append(item_name)
                                        poly_faces.append(item_name+'.f['+str(iter_polys.index())+']')
                                    elif n_vertex == 3:
                                        if not item_name in tris_items:
                                            tris_items.append(item_name)
                                        tris_faces.append(item_name+'.f['+str(iter_polys.index())+']')
                                    # Move to next polygon in the mesh list
                                    iter_polys.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if poly_items or tris_items:
                    non_quad_items = list(set(poly_items+tris_items))
                    non_quad_faces = list(set(poly_faces+tris_faces))
                    non_quad_items.sort()
                    non_quad_faces.sort()
                    for item in non_quad_items:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    self.messages.append("Tris:    "+str(tris_faces)+"\nPolys: "+str(poly_faces))
                    self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(non_quad_faces)+")\n---")
                    cmds.select(non_quad_faces)
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
