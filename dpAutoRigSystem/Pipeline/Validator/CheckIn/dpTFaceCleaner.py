# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "TFaceCleaner"
TITLE = "v128_tFaceCleaner"
DESCRIPTION = "v129_tFaceCleanerDesc"
ICON = "/Icons/dp_tFaceCleaner.png"
WIKI = "07-‐-Validator#-t-face-cleaner"

DP_TFACECLEANER_VERSION = 1.01


class TFaceCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_TFACECLEANER_VERSION
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
                tFaceList = []
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
                                # get edges
                                edgeIter = OpenMaya.MItMeshEdge(shapeNode)
                                # run in faces listing faces
                                while not edgeIter.isDone():
                                    # list faces from this edge
                                    faceIntArray = OpenMaya.MIntArray()
                                    edgeIter.getConnectedFaces(faceIntArray)
                                    # verify the lenght of the connectedFaces
                                    if len(faceIntArray) > 2:
                                        # found tFace
                                        tFaceList.append(objectName+".e["+str(edgeIter.index())+"]")
                                    edgeIter.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if tFaceList:
                    tFaceList.sort()
                    for item in tFaceList:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.select(item)
                                # Cleanup T Faces
                                mel.eval('polyCleanupArgList 3 { \"0\",\"1\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"2\",\"0\" };')
                                cmds.select(clear=True)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                    if self.firstMode:
                        cmds.select(tFaceList)
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
