# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "NonQuadFace"
TITLE = "v119_nonQuadFace"
DESCRIPTION = "v120_nonQuadFaceDesc"
ICON = "/Icons/dp_nonQuadFace.png"

DP_NONQUADFACE_VERSION = 1.0


class NonQuadFace(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_NONQUADFACE_VERSION
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
                polyObjList, trisObjList, trisList, polyList = [], [], [], []
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
                                iterPolys = OpenMaya.MItMeshPolygon(shapeNode)
                                # Iterate through polys on current mesh
                                while not iterPolys.isDone():
                                    nVertex = iterPolys.polygonVertexCount()
                                    if nVertex > 4:
                                        if not objectName in polyObjList:
                                            polyObjList.append(objectName)
                                        polyList.append(objectName+'.f['+str(iterPolys.index())+']')
                                    elif nVertex == 3:
                                        if not objectName in trisObjList:
                                            trisObjList.append(objectName)
                                        trisList.append(objectName+'.f['+str(iterPolys.index())+']')
                                    # Move to next polygon in the mesh list
                                    iterPolys.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if polyObjList or trisObjList:
                    nonQuadObjList = list(set(polyObjList+trisObjList))
                    nonQuadFaceList = list(set(polyList+trisList))
                    nonQuadObjList.sort()
                    nonQuadFaceList.sort()
                    for item in nonQuadObjList:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                    self.messageList.append("Tris:    "+str(trisList)+"\nPolys: "+str(polyList))
                    self.messageList.append("---\n"+self.dpUIinst.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(nonQuadFaceList)+")\n---")
                    cmds.select(nonQuadFaceList)
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
