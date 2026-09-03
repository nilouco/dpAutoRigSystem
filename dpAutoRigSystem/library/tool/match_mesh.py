# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "MatchMesh"
TITLE = "m049_matchMesh"
DESCRIPTION = "m050_matchMeshDesc"
WIKI = "06-‐-Tools#-match-mesh"



class MatchMesh(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)


    def build_tool(self, *args):
        # call main function
        self.run_match_mesh()
    

    def run_match_mesh(self):
        """ Get selection and transfere vertices information.
        """
        # declaring variables
        from_transform_data, to_transform_data = {}, {}
        # get a list of selected items
        selection = cmds.ls(selection=True)
        
        if(len(selection) <= 1):
            cmds.warning(self.ar.data.lang['i040_notMatchSel'])
        else:
            # declaring current variables
            from_father = None
            from_transform = selection.copy()[0]
            to_transform = selection.copy()[1]
            from_mesh = selection.copy()[0]
            to_mesh = selection.copy()[1]
            got_meshes = True
            
            # getting transforms
            if cmds.objectType(selection[0]) != "transform":
                parents = cmds.listRelatives(selection[0], allParents=True, type="transform")
                if parents:
                    from_transform = parents[0]
            if cmds.objectType(selection[1]) != "transform":
                parents = cmds.listRelatives(selection[1], allParents=True, type="transform")
                if parents:
                    to_transform = parents
            
            # getting from_transform father
            from_fathers = cmds.listRelatives(from_transform, allParents=True, type="transform")
            if from_fathers:
                from_father = from_fathers[0]

            # getting meshes
            if cmds.objectType(selection[0]) != "mesh":
                children = cmds.listRelatives(selection[0], children=True, type="mesh")
                if children:
                    from_mesh = children[0]
                else:
                    got_meshes = False
            if cmds.objectType(selection[1]) != "mesh":
                children = cmds.listRelatives(selection[1], children=True, type="mesh")
                if children:
                    to_mesh = children[0]
                else:
                    got_meshes = False
            
            if got_meshes:
                # storing transformation data
                for attr in self.ar.data.transform_attrs[:-1]:
                    from_transform_data[attr] = cmds.getAttr(from_transform+"."+attr)
                    to_transform_data[attr] = cmds.getAttr(to_transform+"."+attr)

                # get list of mesh vertices proccess
                # selecting meshes
                cmds.select([from_mesh, to_mesh])
                meshes = OpenMaya.MSelectionList()
                OpenMaya.MGlobal.getActiveSelectionList(meshes)
                
                # declaring from and to objects, dagPaths and vertice lists
                from_object = OpenMaya.MObject()
                from_dagpath = OpenMaya.MDagPath()
                to_object = OpenMaya.MObject()
                to_dagpath = OpenMaya.MDagPath()
                from_vertices = OpenMaya.MPointArray()
                to_vertices = OpenMaya.MPointArray()
                
                # getting dagPaths
                meshes.getDagPath(0, from_dagpath, from_object)
                meshes.getDagPath(1, to_dagpath, to_object)
                # getting open maya API mesh
                from_mesh_fn = OpenMaya.MFnMesh(from_dagpath)
                to_mesh_fn = OpenMaya.MFnMesh(to_dagpath)
                
                # verify the same number of vertices
                if from_mesh_fn.numVertices() == to_mesh_fn.numVertices():
                    
                    # put from_transform in the same location then to_transform
                    if from_father != None:
                        cmds.parent(from_transform, world=True)
                    for attr in self.ar.data.transform_attrs[:-1]:
                        cmds.setAttr(from_transform+"."+attr, lock=False)
                        cmds.setAttr(to_transform+"."+attr, lock=False)
                        if "scale" in attr:
                            cmds.setAttr(from_transform+"."+attr, 1)
                            cmds.setAttr(to_transform+"."+attr, 1)
                        else:
                            cmds.setAttr(from_transform+"."+attr, 0)
                            cmds.setAttr(to_transform+"."+attr, 0)
                    cmds.matchTransform(to_transform, from_transform, position=True, rotation=True, scale=True)
                    # getting vertices as points
                    from_mesh_fn.getPoints(from_vertices)
                    to_mesh_fn.getPoints(to_vertices)
                    
                    # progress window
                    self.ar.ui_manager.set_progress(self.ar.data.lang['i035_transfData']+': '+self.ar.data.lang['c110_start'], 'Match Mesh Data', from_vertices.length(), is_interruptable=True)
                    cancelled = False
                    
                    # transfer vetex position from FROM mesh to TO mesh selected
                    for i in range(0, from_vertices.length()):
                        # check if the dialog has been cancelled
                        if cmds.progressWindow(query=True, isCancelled=True):
                            cancelled = True
                            break
                        self.ar.ui_manager.set_progress(self.ar.data.lang['i035_transfData'])
                        
                        # transfer data
                        cmds.move(from_vertices[i].x, from_vertices[i].y, from_vertices[i].z, to_mesh+".vtx["+str(i)+"]", absolute=True)
                    
                    self.ar.ui_manager.set_progress(end_it=True)

                    if from_father != None:
                        cmds.parent(from_transform, from_father)
                    # restore transformation data
                    for attr in self.ar.data.transform_attrs[:-1]:
                        cmds.setAttr(from_transform+"."+attr, from_transform_data[attr])
                        cmds.setAttr(to_transform+"."+attr, to_transform_data[attr])

                    if not cancelled:
                        cmds.select(selection)
                        if self.ar.data.ui_state:
                            self.ar.logger.infoWin('m049_matchMesh', 'm049_matchMesh', " -> ".join(selection), "center", 300, 200)
                        print(self.ar.data.lang['i035_transfData'], self.ar.data.lang['i036_from'].upper(), ":", from_mesh, ",", self.ar.data.lang['i037_to'].upper(), ":", to_mesh)
                    else:
                        print(self.ar.data.lang['i038_canceled'])
                else:
                    mel.eval("warning \""+self.ar.data.lang['i039_notMatchDif']+"\";")
                cmds.select(selection)
            else:
                mel.eval("warning \""+self.ar.data.lang['i040_notMatchSel']+"\";")
