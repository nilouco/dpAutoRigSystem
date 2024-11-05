# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya as om

# global variables to this module:    
CLASS_NAME = "MatchMesh"
TITLE = "m049_matchMesh"
DESCRIPTION = "m050_matchMeshDesc"
ICON = "/Icons/dp_matchMesh.png"

DP_MATCHMESH_VERSION = 2.0


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
        # declaring variables
        fromTransformDic, toTransformDic = {}, {}
        attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        
        # get a list of selected items
        selList = cmds.ls(selection=True)
        
        if(len(selList) <= 1):
            cmds.warning(self.dpUIinst.lang['i040_notMatchSel'])
        else:
            # declaring current variables
            fromFather = None
            fromTransform = selList[0]
            toTransform = selList[1]
            fromMesh = selList[0]
            toMesh = selList[1]
            gotMeshes = True
            
            # getting transforms
            if cmds.objectType(selList[0]) != "transform":
                parentList = cmds.listRelatives(selList[0], allParents=True, type="transform")
                if parentList:
                    fromTransform = parentList[0]
            if cmds.objectType(selList[1]) != "transform":
                parentList = cmds.listRelatives(selList[1], allParents=True, type="transform")
                if parentList:
                    toTransform = parentList
            
            # getting fromTransform father
            fromFatherList = cmds.listRelatives(fromTransform, allParents=True, type="transform")
            if fromFatherList:
                fromFather = fromFatherList[0]
            
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
                # storing transformation data
                for attr in attrList:
                    fromTransformDic[attr] = cmds.getAttr(fromTransform+"."+attr)
                    toTransformDic[attr] = cmds.getAttr(toTransform+"."+attr)
                
                # get list of mesh vertices proccess
                # selecting meshes
                cmds.select([fromMesh, toMesh])
                meshList = om.MSelectionList()
                om.MGlobal.getActiveSelectionList(meshList)
                
                # declaring from and to objects, dagPaths and vertice lists
                fromObject = om.MObject()
                fromDagPath = om.MDagPath()
                toObject = om.MObject()
                toDagPath = om.MDagPath()
                fromVerticeList = om.MPointArray()
                toVerticeList = om.MPointArray()
                
                # getting dagPaths
                meshList.getDagPath(0, fromDagPath, fromObject)
                meshList.getDagPath(1, toDagPath, toObject)
                # getting open maya API mesh
                fromMeshFn = om.MFnMesh(fromDagPath)
                toMeshFn = om.MFnMesh(toDagPath)
                
                # verify the same number of vertices
                if fromMeshFn.numVertices() == toMeshFn.numVertices():
                    # put fromTransform in the same location then toTransform
                    if fromFather != None:
                        cmds.parent(fromTransform, world=True)
                    for attr in attrList:
                        cmds.setAttr(fromTransform+"."+attr, lock=False)
                        cmds.setAttr(toTransform+"."+attr, lock=False)
                        if not "s" in attr:
                            cmds.setAttr(fromTransform+"."+attr, 0)
                            cmds.setAttr(toTransform+"."+attr, 0)
                        else:
                            cmds.setAttr(fromTransform+"."+attr, 1)
                            cmds.setAttr(toTransform+"."+attr, 1)
                    tempToDeleteA = cmds.parentConstraint(fromTransform, toTransform, maintainOffset=False)
                    tempToDeleteB = cmds.scaleConstraint(fromTransform, toTransform, maintainOffset=False)
                    cmds.delete(tempToDeleteA, tempToDeleteB)
                    
                    # getting vertices as points
                    fromMeshFn.getPoints(fromVerticeList)
                    toMeshFn.getPoints(toVerticeList)
                    
                    # progress window
                    self.utils.setProgress(self.dpUIinst.lang['i035_transfData']+': 0%', 'Match Mesh Data', fromVerticeList.length(), isInterruptable=True)
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
                    
                    if fromFather != None:
                        cmds.parent(fromTransform, fromFather)
                    # restore transformation data
                    for attr in attrList:
                        cmds.setAttr(fromTransform+"."+attr, fromTransformDic[attr])
                        cmds.setAttr(toTransform+"."+attr, toTransformDic[attr])
                    
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
