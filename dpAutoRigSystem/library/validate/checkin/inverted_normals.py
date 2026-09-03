# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "InvertedNormals"
TITLE = "v086_invertedNormals"
DESCRIPTION = "v087_invertedNormalsDesc"
WIKI = "07-‐-Validator#-inverted-normals"



class InvertedNormals(action.BaseAction):
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
            inverted_items = []
            if inputs:
                meshes = inputs
            else:
                meshes = cmds.ls(selection=False, type='mesh')
            if meshes:
                self.ar.ui_manager.set_progress(max=len(meshes), add_one=False, add_number=False)
                iter_geo = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kMesh)
                while not iter_geo.isDone():
                    next_geo = False
                    use_this_item = False
                    # get mesh data
                    shape = iter_geo.thisNode()
                    fn_shape_node = OpenMaya.MFnDagNode(shape)
                    shape_name = fn_shape_node.name()
                    parent_node = fn_shape_node.parent(0)
                    fn_parent_node = OpenMaya.MFnDagNode(parent_node)
                    item_name = fn_parent_node.name()
                    self.ar.ui_manager.set_progress(self.ar.data.lang[self.title]+": "+shape_name)
                    # verify if item_name or shape_name is in meshes
                    for item in meshes:
                        if item_name in item or shape_name in item:
                            use_this_item = True
                            break
                    if use_this_item:
                        # get faces
                        iter_face   = OpenMaya.MItMeshPolygon(shape)
                        con_faces_it = OpenMaya.MItMeshPolygon(shape)
                        # run in faces listing vertices
                        while not iter_face.isDone() and not next_geo:
                            # list vertices from this face
                            vtx_int_array = OpenMaya.MIntArray()
                            iter_face.getVertices(vtx_int_array)
                            vtx_int_array.append(vtx_int_array[0])
                            # get connected faces of this face
                            con_faces_int_array = OpenMaya.MIntArray()
                            iter_face.getConnectedFaces(con_faces_int_array)
                            # run in adjacent faces to list them vertices
                            for f in con_faces_int_array:
                                # say this is the face index to use for next iterations
                                last_index_ptr = OpenMaya.MScriptUtil().asIntPtr()
                                con_faces_it.setIndex(f, last_index_ptr)
                                # get vertices from this adjacent face
                                con_vtx_int_array = OpenMaya.MIntArray()
                                con_faces_it.getVertices(con_vtx_int_array)
                                con_vtx_int_array.append(con_vtx_int_array[0])
                                # compare vertex in order to find double consecutive vertices
                                for i in range(0, len(vtx_int_array)-1):
                                    i_pair = str(vtx_int_array[i])+","+str(vtx_int_array[i+1])
                                    for c in range(0, len(con_vtx_int_array)-1):
                                        c_pair = str(con_vtx_int_array[c])+","+str(con_vtx_int_array[c+1])
                                        if i_pair == c_pair:
                                            # found inverted normals
                                            inverted_items.append(item_name)
                                            next_geo = True
                            iter_face.next()
                    # go to next geometry
                    iter_geo.next()
            # verify if there are inverted normals
            if inverted_items:
                inverted_items = list(set(inverted_items))
                for mesh in inverted_items:
                    self.checked_items.append(mesh)
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            # conform normals to fix
                            cmds.polyNormal(mesh, normalMode=2, userNormalMode=0, constructionHistory=False)
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
