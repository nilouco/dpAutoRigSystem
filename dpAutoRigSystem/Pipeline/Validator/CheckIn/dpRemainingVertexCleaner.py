# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "RemainingVertexCleaner"
TITLE = "v134_remainingVertexCleaner"
DESCRIPTION = "v135_remainingVertexCleanerDesc"
ICON = "/Icons/dp_remainingVertexCleaner.png"

DP_REMAININGVERTEXCLEANER_VERSION = 1.00


class RemainingVertexCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_REMAININGVERTEXCLEANER_VERSION
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
                borderEdgeIdxList, remainingVertexList = [], []
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
                                vertexIter = OpenMaya.MItMeshVertex(shapeNode)
                                iterEdges  = OpenMaya.MItMeshEdge(shapeNode)
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
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.delete(item)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                    if self.firstMode:
                        self.messageList.append("Remaining vertex: "+str(remainingVertexList))
                        self.messageList.append("---\n"+self.dpUIinst.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(remainingVertexList)+")\n---")
                        cmds.select(remainingVertexList)
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
