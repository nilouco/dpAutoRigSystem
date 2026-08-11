# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action

# global variables to this module:
CLASS_NAME = "NonQuadFace"
TITLE = "v119_nonQuadFace"
DESCRIPTION = "v120_nonQuadFaceDesc"
WIKI = "07-‐-Validator#-non-quad-face"



class NonQuadFace(action.BaseAction):
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
            if objList:
                check_items = cmds.ls(objList, type="mesh")
            else:
                check_items = cmds.ls(selection=False, type="mesh")
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
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
                        # verify if objName or shapeName is in check_items
                        for obj in check_items:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
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
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    self.messages.append("Tris:    "+str(trisList)+"\nPolys: "+str(polyList))
                    self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(nonQuadFaceList)+")\n---")
                    cmds.select(nonQuadFaceList)
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
