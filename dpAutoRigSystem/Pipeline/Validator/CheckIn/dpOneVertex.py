# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "OneVertex"
TITLE = "v132_oneVertex"
DESCRIPTION = "v133_oneVertexDesc"
ICON = "/Icons/dp_oneVertex.png"

DP_ONEVERTEX_VERSION = 1.0


class OneVertex(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_ONEVERTEX_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = cmds.ls(objList, type="mesh")
            else:
                toCheckList = cmds.ls(selection=False, type="mesh")
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                # declare resulted lists
                oneVertexList = []
                iter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kGeometric)
                if iter != None:
                    while not iter.isDone():
                        # get mesh data
                        shapeNode    = iter.thisNode()
                        fnShapeNode  = OpenMaya.MFnDagNode(shapeNode)
                        shapeName    = fnShapeNode.name()
                        parentNode   = fnShapeNode.parent(0)
                        fnParentNode = OpenMaya.MFnDagNode(parentNode)
                        objectName   = fnParentNode.name()
                        # verify if objName or shapeName is in toCheckList
                        for obj in toCheckList:
                            self.utils.setProgress(self.dpUIinst.lang[self.title])
                            if obj == shapeName and not cmds.getAttr(obj+".intermediateObject"):
                                # get faces
                                faceIter      = OpenMaya.MItMeshPolygon(shapeNode)
                                conFacesIter  = OpenMaya.MItMeshPolygon(shapeNode)
                                conFacesBIter = OpenMaya.MItMeshPolygon(shapeNode)
                                vertexIter    = OpenMaya.MItMeshVertex(shapeNode)
                                # run in faces listing edges
                                while not faceIter.isDone():
                                    thisFace = faceIter.index()
                                    # list vertices from this face
                                    verticesIntArray = OpenMaya.MIntArray()
                                    faceIter.getVertices(verticesIntArray)
                                    # list edges from this face
                                    edgesIntArray = OpenMaya.MIntArray()
                                    faceIter.getEdges(edgesIntArray)
                                    # run in vertex
                                    for v in verticesIntArray:
                                        # say this is the vertex index to use for next iterations
                                        lastIndexPtr = OpenMaya.MScriptUtil().asIntPtr()
                                        vertexIter.setIndex(v, lastIndexPtr)
                                        # get connected faces of this vertex
                                        conFacesIntArray = OpenMaya.MIntArray()
                                        vertexIter.getConnectedFaces(conFacesIntArray)
                                        # run in faces
                                        for f in conFacesIntArray:
                                            if f != thisFace:
                                                # say this is the face index to use for next iterations
                                                lastIndexPtr = OpenMaya.MScriptUtil().asIntPtr()
                                                conFacesIter.setIndex(f, lastIndexPtr)
                                                # get edges from this adjacent face
                                                conEdgesIntArray = OpenMaya.MIntArray()
                                                conFacesIter.getEdges(conEdgesIntArray)
                                                # get vertices from this adjacent face
                                                conVerticesIntArray = OpenMaya.MIntArray()
                                                conFacesIter.getVertices(conVerticesIntArray)
                                                # get connected facesB of this face
                                                conFacesBIntArray = OpenMaya.MIntArray()
                                                conFacesIter.getConnectedFaces(conFacesBIntArray)
                                                # compare sharing of vertices and edges
                                                for vertex in verticesIntArray:
                                                    for conVertex in conVerticesIntArray:
                                                        if vertex == conVertex:
                                                            sameEdge = False
                                                            for edge in edgesIntArray:
                                                                for conEdge in conEdgesIntArray:
                                                                    if edge == conEdge:
                                                                        sameEdge = True
                                                                    else:
                                                                        for fB in conFacesBIntArray:
                                                                            # say this is the vertex index to use for next iterations
                                                                            lastIndexBPtr = OpenMaya.MScriptUtil().asIntPtr()
                                                                            conFacesBIter.setIndex(fB, lastIndexBPtr)
                                                                            # get edges from this secound adjacent face
                                                                            conEdgesBIntArray = OpenMaya.MIntArray()
                                                                            conFacesBIter.getEdges(conEdgesBIntArray)
                                                                            # get vertices from this secound adjacent face
                                                                            conVerticesBIntArray = OpenMaya.MIntArray()
                                                                            conFacesBIter.getVertices(conVerticesBIntArray)
                                                                            for conVertexB in conVerticesBIntArray:
                                                                                if vertex == conVertexB:
                                                                                    for conEdgeB in conEdgesBIntArray:
                                                                                        if edge == conEdgeB:
                                                                                            sameEdge = True
                                                            if sameEdge == False:
                                                                # found oneVetex
                                                                if not objectName+".vtx["+str(vertex)+"]" in oneVertexList:
                                                                    oneVertexList.append(objectName+".vtx["+str(vertex)+"]")
                                    # go to next face
                                    faceIter.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if oneVertexList:
                    oneVertexList.sort()
                    for item in oneVertexList:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                    self.messageList.append("---\n"+self.dpUIinst.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(oneVertexList)+")\n---")
                    cmds.select(oneVertexList)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
