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
                borderEdgeIdxList, remainingVertexList = [], []
                iter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kGeometric)
                if iter != None:
                    while not iter.isDone():
                        # get mesh data
                        shape    = iter.thisNode()
                        fnShapeNode  = OpenMaya.MFnDagNode(shape)
                        shapeName    = fnShapeNode.name()
                        parentNode   = fnShapeNode.parent(0)
                        fnParentNode = OpenMaya.MFnDagNode(parentNode)
                        objectName   = fnParentNode.name()
                        # verify if objName or shapeName is in check_items
                        for obj in check_items:
                            self.ar.utils.set_progress(self.ar.data.lang[self.title])
                            if obj == shapeName and not cmds.getAttr(obj+".intermediateObject"):
                                vertexIter = OpenMaya.MItMeshVertex(shape)
                                iterEdges  = OpenMaya.MItMeshEdge(shape)
                                # Iterate through edges on current mesh
                                while not iterEdges.isDone():
                                    # Get current polygons connected faces
                                    indexConFaces = OpenMaya.MIntArray()
                                    iterEdges.getConnectedFaces(indexConFaces)
                                    if len(indexConFaces) == 1:
                                        # got a border edge
                                        borderEdgeIdxList.append(iterEdges.index())
                                    # Move to next edge in the mesh list
                                    iterEdges.next()
                                # Iterate through vertices on current mesh
                                while not vertexIter.isDone():
                                    # Get current vertex connected edges
                                    indexConEdges = OpenMaya.MIntArray()
                                    vertexIter.getConnectedEdges(indexConEdges)
                                    if len(indexConEdges) < 3:
                                        if borderEdgeIdxList:
                                            if not set(indexConEdges).intersection(borderEdgeIdxList):
                                                remainingVertexList.append(objectName+'.vtx['+str(vertexIter.index())+']')
                                        else:
                                            remainingVertexList.append(objectName+'.vtx['+str(vertexIter.index())+']')
                                    # Move to next vertex in the mesh list
                                    vertexIter.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if remainingVertexList:
                    remainingVertexList.reverse()
                    for item in remainingVertexList:
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
                        self.messages.append("Remaining vertex: "+str(remainingVertexList))
                        self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(remainingVertexList)+")\n---")
                        cmds.select(remainingVertexList)
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
