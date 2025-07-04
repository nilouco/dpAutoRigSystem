# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "LaminaFaceCleaner"
TITLE = "v124_laminaFaceCleaner"
DESCRIPTION = "v125_laminaFaceCleanerDesc"
ICON = "/Icons/dp_laminaFaceCleaner.png"

DP_LAMINAFACECLEANER_VERSION = 1.1


class LaminaFaceCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_LAMINAFACECLEANER_VERSION
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
                laminaObjList, laminaFaceList = [], []
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
                                faceIter   = OpenMaya.MItMeshPolygon(shapeNode)
                                conFacesIt = OpenMaya.MItMeshPolygon(shapeNode)
                                # run in faces listing edges
                                while not faceIter.isDone():
                                    # list vertices from this face
                                    edgesIntArray = OpenMaya.MIntArray()
                                    faceIter.getEdges(edgesIntArray)
                                    # get connected faces of this face
                                    conFacesIntArray = OpenMaya.MIntArray()
                                    faceIter.getConnectedFaces(conFacesIntArray)
                                    # run in adjacent faces to list them vertices
                                    for f in conFacesIntArray:
                                        # say this is the face index to use for next iterations
                                        lastIndexPtr = OpenMaya.MScriptUtil().asIntPtr()
                                        conFacesIt.setIndex(f, lastIndexPtr)
                                        # get edges from this adjacent face
                                        conEdgesIntArray = OpenMaya.MIntArray()
                                        conFacesIt.getEdges(conEdgesIntArray)
                                        # compare edges to verify if the list are the same
                                        if sorted(edgesIntArray) == sorted(conEdgesIntArray):
                                            # found laminaFaces
                                            if not objectName in laminaObjList:
                                                laminaObjList.append(objectName)
                                            laminaFaceList.append(objectName+'.f['+str(faceIter.index())+']')
                                    faceIter.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if laminaObjList:
                    laminaObjList.sort()
                    laminaFaceList.sort()
                    for item in laminaObjList:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                            self.messageList.append("Lamina faces: "+str(laminaFaceList))
                            cmds.select(laminaFaceList)
                        else: #fix
                            try:
                                cmds.select(item)
                                mel.eval('polyCleanupArgList 3 { \"0\",\"1\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"-1\",\"1\" };')
                                cmds.select(clear=True)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+" - Faces: "+", ".join(laminaFaceList))
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item+" - Faces: "+", ".join(laminaList))
                    if self.firstMode:
                        self.messageList.append("Lamina faces: "+str(laminaList))
                        self.messageList.append("---\n"+self.dpUIinst.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(laminaList)+")\n---")
                        cmds.select(laminaList)
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
