# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "RemainingVertex"
TITLE = "v134_remainingVertex"
DESCRIPTION = "v135_remainingVertexDesc"
WIKI = "07-‐-Validator#-remaining-vertex-cleaner"



class RemainingVertex(action.BaseAction):
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
                border_edge_indexes, remaining_vertices = [], []
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
                                iter_vertex = OpenMaya.MItMeshVertex(shape)
                                iter_edges  = OpenMaya.MItMeshEdge(shape)
                                # Iterate through edges on current mesh
                                while not iter_edges.isDone():
                                    # Get current polygons connected faces
                                    index_con_faces = OpenMaya.MIntArray()
                                    iter_edges.getConnectedFaces(index_con_faces)
                                    if len(index_con_faces) == 1:
                                        # got a border edge
                                        border_edge_indexes.append(iter_edges.index())
                                    # Move to next edge in the mesh list
                                    iter_edges.next()
                                # Iterate through vertices on current mesh
                                while not iter_vertex.isDone():
                                    # Get current vertex connected edges
                                    index_con_edges = OpenMaya.MIntArray()
                                    iter_vertex.getConnectedEdges(index_con_edges)
                                    if len(index_con_edges) < 3:
                                        if border_edge_indexes:
                                            if not set(index_con_edges).intersection(border_edge_indexes):
                                                remaining_vertices.append(item_name+'.vtx['+str(iter_vertex.index())+']')
                                        else:
                                            remaining_vertices.append(item_name+'.vtx['+str(iter_vertex.index())+']')
                                    # Move to next vertex in the mesh list
                                    iter_vertex.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if remaining_vertices:
                    remaining_vertices.reverse()
                    for item in remaining_vertices:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                cmds.delete(item)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    if self.first_mode:
                        self.messages.append("Remaining vertex: "+str(remaining_vertices))
                        self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(remaining_vertices)+")\n---")
                        cmds.select(remaining_vertices)
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
