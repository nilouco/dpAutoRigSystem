# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action
from importlib import reload

# global variables to this module:
CLASS_NAME = "BorderGap"
TITLE = "v122_borderGap"
DESCRIPTION = "v123_borderGapDesc"
WIKI = "07-‐-Validator#-border-gap"



class BorderGap(action.ActionStartClass):
    def __init__(self, ar):
        action.ActionStartClass.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(action)


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
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                # declare resulted lists
                gapList, gapObjList = [], []
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
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if obj == shapeName and not cmds.getAttr(obj+".intermediateObject"):
                                iterPolys = OpenMaya.MItMeshEdge(shapeNode)
                                # Iterate through polys on current mesh
                                while not iterPolys.isDone():
                                    # Get current polygons connected faces
                                    indexConFaces = OpenMaya.MIntArray()
                                    iterPolys.getConnectedFaces(indexConFaces)
                                    if len(indexConFaces) == 1:
                                        if not objectName in gapObjList:
                                            gapObjList.append(objectName)
                                        gapList.append(objectName+'.e['+str(iterPolys.index())+']')
                                    # Move to next polygon in the mesh list
                                    iterPolys.next()
                        # Move to the next selected node in the list
                        iter.next()
                # conditional to check here
                if gapObjList:
                    gapObjList.sort()
                    for item in gapObjList:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            self.resultOkList.append(False)
                            self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    self.messageList.append(self.ar.data.lang['v122_borderGap']+": "+str(gapList))
                    self.messageList.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(gapList)+")\n---")
                    cmds.select(gapList)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
