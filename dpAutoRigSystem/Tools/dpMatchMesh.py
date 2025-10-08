# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya

# global variables to this module:
CLASS_NAME = "MatchMesh"
TITLE = "m049_matchMesh"
DESCRIPTION = "m050_matchMeshDesc"
ICON = "/Icons/dp_matchMesh.png"

DP_MATCHMESH_VERSION = 3.00


class MatchMesh(object):
    def __init__(self, dpUIinst, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.utils = self.dpUIinst.utils
        # call main function
        self.dpMatchMesh(self)
    

    def dpMatchMesh(self, *args):
        """ Get selection and transfere vertices information.
        """
        # get a list of selected items
        selList = cmds.ls(selection=True)
        
        if(len(selList) <= 1):
            cmds.warning(self.dpUIinst.lang['i040_notMatchSel'])
        else:
            # declaring current variables
            fromMesh = selList[0]
            toMesh = selList[1]
            gotMeshes = True
            
            # getting meshes
            if cmds.objectType(selList[0]) != "mesh":
                childrenList = cmds.listRelatives(selList[0], children=True, type="mesh")
                if childrenList:
                    fromMesh = childrenList[0]
                else:
                    gotMeshes = False
            if cmds.objectType(selList[1]) != "mesh":
                childrenList = cmds.listRelatives(selList[1], children=True, type="mesh")
                if childrenList:
                    toMesh = childrenList[0]
                else:
                    gotMeshes = False
            
            if gotMeshes:
                # get list of mesh vertices proccess
                # selecting meshes
                cmds.select([fromMesh, toMesh])
                meshList = OpenMaya.MSelectionList()
                OpenMaya.MGlobal.getActiveSelectionList(meshList)
                
                # declaring from and to objects, dagPaths and vertice lists
                fromObject = OpenMaya.MObject()
                fromDagPath = OpenMaya.MDagPath()
                toObject = OpenMaya.MObject()
                toDagPath = OpenMaya.MDagPath()
                fromVerticeList = OpenMaya.MPointArray()
                toVerticeList = OpenMaya.MPointArray()
                
                # getting dagPaths
                meshList.getDagPath(0, fromDagPath, fromObject)
                meshList.getDagPath(1, toDagPath, toObject)
                # getting open maya API mesh
                fromMeshFn = OpenMaya.MFnMesh(fromDagPath)
                toMeshFn = OpenMaya.MFnMesh(toDagPath)
                
                # verify the same number of vertices
                if fromMeshFn.numVertices() == toMeshFn.numVertices():
                    
                    # getting vertices as points
                    fromMeshFn.getPoints(fromVerticeList)
                    toMeshFn.getPoints(toVerticeList)
                    
                    # progress window
                    self.utils.setProgress(self.dpUIinst.lang['i035_transfData']+': '+self.dpUIinst.lang['c110_start'], 'Match Mesh Data', fromVerticeList.length(), isInterruptable=True)
                    cancelled = False
                    
                    # transfer vetex position from FROM mesh to TO mesh selected
                    for i in range(0, fromVerticeList.length()):
                        # check if the dialog has been cancelled
                        if cmds.progressWindow(query=True, isCancelled=True):
                            cancelled = True
                            break
                        self.utils.setProgress(self.dpUIinst.lang['i035_transfData'])
                        
                        # transfer data
                        cmds.move(fromVerticeList[i].x, fromVerticeList[i].y, fromVerticeList[i].z, toMesh+".vtx["+str(i)+"]", absolute=True)
                    
                    self.utils.setProgress(endIt=True)

                    if not cancelled:
                        cmds.select(selList)
                        self.dpUIinst.logger.infoWin('m049_matchMesh', 'm049_matchMesh', " -> ".join(selList), "center", 300, 200)
                        print(self.dpUIinst.lang['i035_transfData'], self.dpUIinst.lang['i036_from'].upper(), ":", fromMesh, ",", self.dpUIinst.lang['i037_to'].upper(), ":", toMesh)
                    else:
                        print(self.dpUIinst.lang['i038_canceled'])
                else:
                    mel.eval("warning \""+self.dpUIinst.lang['i039_notMatchDif']+"\";")
                cmds.select(selList)
            else:
                mel.eval("warning \""+self.dpUIinst.lang['i040_notMatchSel']+"\";")
