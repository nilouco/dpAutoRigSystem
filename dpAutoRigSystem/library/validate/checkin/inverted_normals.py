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
    

    def runAction(self, first_mode=True, objList=None, *args):
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
            invertedObjList = []
            if objList:
                objMeshList = objList
            else:
                objMeshList = cmds.ls(selection=False, type='mesh')
            if objMeshList:
                self.ar.utils.setProgress(max=len(objMeshList), addOne=False, addNumber=False)
                geomIter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kMesh)
                while not geomIter.isDone():
                    nextGeom = False
                    useThisObj = False
                    # get mesh data
                    shapeNode = geomIter.thisNode()
                    fnShapeNode = OpenMaya.MFnDagNode(shapeNode)
                    shapeName = fnShapeNode.name()
                    parentNode = fnShapeNode.parent(0)
                    fnParentNode = OpenMaya.MFnDagNode(parentNode)
                    objName = fnParentNode.name()
                    self.ar.utils.setProgress(self.ar.data.lang[self.title]+": "+shapeName)
                    # verify if objName or shapeName is in objMeshList
                    for obj in objMeshList:
                        if objName in obj or shapeName in obj:
                            useThisObj = True
                            break
                    if useThisObj:
                        # get faces
                        faceIter   = OpenMaya.MItMeshPolygon(shapeNode)
                        conFacesIt = OpenMaya.MItMeshPolygon(shapeNode)
                        # run in faces listing vertices
                        while not faceIter.isDone() and not nextGeom:
                            # list vertices from this face
                            vtxIntArray = OpenMaya.MIntArray()
                            faceIter.getVertices(vtxIntArray)
                            vtxIntArray.append(vtxIntArray[0])
                            # get connected faces of this face
                            conFacesIntArray = OpenMaya.MIntArray()
                            faceIter.getConnectedFaces(conFacesIntArray)
                            # run in adjacent faces to list them vertices
                            for f in conFacesIntArray:
                                # say this is the face index to use for next iterations
                                lastIndexPtr = OpenMaya.MScriptUtil().asIntPtr()
                                conFacesIt.setIndex(f, lastIndexPtr)
                                # get vertices from this adjacent face
                                conVtxIntArray = OpenMaya.MIntArray()
                                conFacesIt.getVertices(conVtxIntArray)
                                conVtxIntArray.append(conVtxIntArray[0])
                                # compare vertex in order to find double consecutive vertices
                                for i in range(0, len(vtxIntArray)-1):
                                    iPair = str(vtxIntArray[i])+","+str(vtxIntArray[i+1])
                                    for c in range(0, len(conVtxIntArray)-1):
                                        cPair = str(conVtxIntArray[c])+","+str(conVtxIntArray[c+1])
                                        if iPair == cPair:
                                            # found inverted normals
                                            invertedObjList.append(objName)
                                            nextGeom = True
                            faceIter.next()
                    # go to next geometry
                    geomIter.next()
            # verify if there are inverted normals
            if invertedObjList:
                invertedObjList = list(set(invertedObjList))
                for mesh in invertedObjList:
                    self.checked_items.append(mesh)
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            # conform normals to fix
                            cmds.polyNormal(mesh, normalMode=2, userNormalMode=0, constructionHistory=False)
                            #cmds.setAttr(mesh+".displayNormal", 0)
                            #cmds.setAttr(mesh+".doubleSided", 0)
                            #cmds.setAttr(mesh+".opposite", 0)
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
        self.endProgress()
        return self.log_data