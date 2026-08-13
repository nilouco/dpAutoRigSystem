# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "LaminaFace"
TITLE = "v124_laminaFace"
DESCRIPTION = "v125_laminaFaceDesc"
WIKI = "07-‐-Validator#-lamina-face-cleaner"



class LaminaFace(action.BaseAction):
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
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
                # declare resulted lists
                laminaObjList, laminaFaceList = [], []
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
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if obj == shapeName and not cmds.getAttr(obj+".intermediateObject"):
                                # get faces
                                faceIter   = OpenMaya.MItMeshPolygon(shape)
                                conFacesIt = OpenMaya.MItMeshPolygon(shape)
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
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                            self.messages.append("Lamina faces: "+str(laminaFaceList))
                            cmds.select(laminaFaceList)
                        else: #fix
                            try:
                                cmds.select(item)
                                mel.eval('polyCleanupArgList 3 { \"0\",\"1\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"1e-005\",\"0\",\"-1\",\"1\" };')
                                cmds.select(clear=True)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+" - Faces: "+", ".join(laminaFaceList))
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+" - Faces: "+", ".join(laminaFaceList))
                    if self.first_mode:
                        self.messages.append("Lamina faces: "+str(laminaFaceList))
                        self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(laminaFaceList)+")\n---")
                        cmds.select(laminaFaceList)
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
