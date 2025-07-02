# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
from ....Tools import dpRivet
import random

# global variables to this module:
CLASS_NAME = "BrokenRivet"
TITLE = "v126_brokenRivet"
DESCRIPTION = "v127_brokenRivetDesc"
ICON = "/Icons/dp_brokenRivet.png"

DP_BROKEN_RIVET = 1.0


class BrokenRivet(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_BROKEN_RIVET
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.dpRivet = dpRivet.Rivet(self.dpUIinst, ui=False)


    def listFolliclesAtOrigin(self):
        follicles_at_origin = []
        
        follicle_shapes = cmds.ls(type='follicle')
        
        for follicle_shape in follicle_shapes:
            # Each follicle shape typically has a transform parent
            parents = cmds.listRelatives(follicle_shape, parent=True)
            if not parents:
                continue
            follicle_transform = parents[0]
            
            pos = cmds.xform(follicle_transform, query=True, translation=True, worldSpace=True)
            
            if pos == [0.0, 0.0, 0.0]:
                follicles_at_origin.append(follicle_transform)
        
        return follicles_at_origin


    def disablePac(self, folTr, netNode):
        try:
            parentConstraint = cmds.listConnections(f"{netNode}.pacNode", destination=False)[0]
            pacAttrList = cmds.listAttr(parentConstraint, settable=True, visible=True, string=f"{folTr}*")
            if pacAttrList:
                pacAttr = pacAttrList[0]
                cmds.setAttr(f"{parentConstraint}.{pacAttr}", 0)
        except Exception as e:
            print(e)


    def removeRivetFromNetNode(self, folTr, rivetNetNode):
            """ Remove the rivet from its network node.
            """
            rivetTransform = cmds.listConnections(f"{rivetNetNode}.rivet", destination=False)
            if rivetTransform:
                rivetTransform = rivetTransform[0]
            rivetControl = cmds.listConnections(f"{rivetNetNode}.itemNode", destination=False)[0]
            try:
                originalParent = cmds.listRelatives(rivetTransform, parent=True)
                currentParent = cmds.listRelatives(rivetControl, parent=True)
                if originalParent == None:
                    if currentParent != originalParent:
                        cmds.parent(rivetControl, world=True)
                else:
                    originalParent = originalParent[0]
                    if not originalParent in currentParent:
                        cmds.parent(rivetControl, originalParent)
                if rivetControl != rivetTransform:
                    cmds.delete([rivetTransform, folTr])
                else:
                    cmds.delete(folTr)
            except Exception as e:
                print(e)
                cmds.delete(folTr)
            print(f"{folTr} removed.")

            connectionList = cmds.listConnections(f"{rivetNetNode}.message", plugs=True, destination=True)
            if len(connectionList) > 1:
                for connection in connectionList:
                    if "rivetNet" in connection:
                        cmds.deleteAttr(connection)
                        break
            else:
                cmds.deleteAttr(connectionList[0])

            cmds.delete(rivetNetNode)


    def getRivetNetFromFolTransform(self, folTr):
        folTrOutputList = cmds.listConnections(f"{folTr}.message", source=False, destination=True)
        for connection in folTrOutputList:
            if "_Net" in connection:
                return connection


    def removeRivetFromFollicleTransformList(self, follicle_transform_list):
        for folTr in follicle_transform_list:
            rivetNetNode = self.getRivetNetFromFolTransform(folTr)
            self.disablePac(folTr, rivetNetNode)
            self.removeRivetFromNetNode(folTr, rivetNetNode)


    def getConnectionsFromFollicle(self, follicles_origin_list):
        controllers_list = []
        attach_geo_list = []
        for folTr in follicles_origin_list:
            rivetNetNode = self.getRivetNetFromFolTransform(folTr)
            rivet_controller = cmds.listConnections(f"{rivetNetNode}.itemNode", source=True, destination=False)[0]
            face_to_rivet_geo = cmds.listConnections(f"{rivetNetNode}.geoToAttach", source=True, destination=False)[0]
            if rivet_controller:
                controllers_list.append(rivet_controller)
            if face_to_rivet_geo:
                attach_geo_list.append(face_to_rivet_geo)
        return controllers_list, attach_geo_list


    def getClosestVertex(self, point, vtx_list):
        """
        Finds the closest vertex to a given point in Maya using cmds.
        :param point: A tuple (x, y, z) representing the target point.
        :return: Index of the closest vertex.
        """
        closest_vertex = None
        min_distance = float("inf")

        for vertex in vtx_list:
            vtx_index = int(vertex.split("[")[1].strip("]"))  # Extract index
            vtx_pos = cmds.xform(vertex, query=True, translation=True, worldSpace=True)

            # Compute Euclidean distance
            distance = (sum((point[i] - vtx_pos[i]) ** 2 for i in range(3))) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest_vertex = vtx_index

        return closest_vertex


    def getConnectedEdges(self, mesh_name, vertex_index):
        """
        Returns all edge indexes connected to a given vertex.
        :param mesh_name: Name of the mesh object.
        :param vertex_index: Index of the vertex.
        :return: List of connected edge indexes.
        """
        vertex = f"{mesh_name}.vtx[{vertex_index}]"  # Format vertex identifier
        edges_info = cmds.polyInfo(vertex, vertexToEdge=True)  # Get connected edges
        
        if not edges_info:
            return None

        # Extract edge indexes from the returned string
        edge_indexes = [int(e) for e in edges_info[0].split()[2:]]

        return edge_indexes


    def getEdgeLength(self, mesh_name, edge_index):
        """
        Returns the length of an edge given its index.
        :param mesh_name: Name of the mesh object.
        :param edge_index: Index of the edge.
        :return: Length of the edge.
        """
        edge = f"{mesh_name}.e[{edge_index}]"  # Format edge identifier
        verts = cmds.polyInfo(edge, edgeToVertex=True)

        if not verts:
            return None

        verts = [int(v) for v in verts[0].split()[2:]]  # Extract vertex indices

        # Get vertex positions
        vtx1_pos = cmds.xform(f"{mesh_name}.vtx[{verts[0]}]", query=True, translation=True, worldSpace=True)
        vtx2_pos = cmds.xform(f"{mesh_name}.vtx[{verts[1]}]", query=True, translation=True, worldSpace=True)

        # Compute Euclidean distance (edge length)
        length = (sum((vtx1_pos[i] - vtx2_pos[i]) ** 2 for i in range(3))) ** 0.5

        return length


    def normalizeVectorSum(self, vectors):
        """
        Sums a list of vectors and returns the normalized result.
        
        :param vectors: List of tuples or lists representing vectors (x, y, z).
        :return: Normalized list [x, y, z].
        """
        if not vectors:
            raise ValueError("Vector list is empty")

        total = [0.0, 0.0, 0.0]
        for vec in vectors:
            total[0] += vec[0]
            total[1] += vec[1]
            total[2] += vec[2]

        norm = (total[0]**2 + total[1]**2 + total[2]**2) ** 0.5
        if norm == 0:
            raise ValueError("Sum of vectors is zero, cannot normalize")

        return [total[0] / norm, total[1] / norm, total[2] / norm]


    def getDirectionVector(self, model, vtx_index):
        cmds.select(clear=True)
        cmds.select(f"{model}.vtx[{vtx_index}]")
        cmds.GrowPolygonSelectionRegion()
        vertex_list = cmds.ls(selection=True, flatten=True)
        vertex_vectors = []

        for vertex in vertex_list:
            if ".vtx[" in vertex:  # Ensure it's a vertex selection
                vtx_vector = cmds.pointPosition(vertex)
                vertex_vectors.append(vtx_vector)
        normalized_vectors = self.normalizeVectorSum(vertex_vectors)

        return normalized_vectors


    def randomizeTranslation(self, tweakCtrl, model):
        """
        Randomizes the translation of an tweakCtrl in Maya while ensuring the offset is insignificant compared to its scale.
        """

        if cmds.objExists(tweakCtrl):
            # Get current translation
            translation = cmds.xform(tweakCtrl, query=True, translation=True, worldSpace=True)
            vertex_set = cmds.ls(f"{model}.vtx[*]", flatten=True)
            closestVertexIndex = self.getClosestVertex(translation, vertex_set)
            closestEdgeIndexList = self.getConnectedEdges(model, closestVertexIndex)

            closestEdgeAvgLen = 0.0
            for edgeIndex in closestEdgeIndexList:
                closestEdgeAvgLen += self.getEdgeLength(model, edgeIndex)
            closestEdgeAvgLen = closestEdgeAvgLen/len(closestEdgeIndexList)
            
            # Unitary direction vector to use as offset direction.
            u_vector =  self.getDirectionVector(model, closestVertexIndex)
            
            # Calculate a small offset based on scale.
            max_offset = closestEdgeAvgLen * 0.1

            # Compute the offset that is going to be used.
            offset = random.uniform(0, max_offset)

            # new_position = t* + d.u*
            new_translation = (translation[0] + offset * u_vector[0], 
                            translation[1] + offset * u_vector[1],
                            translation[2] + offset * u_vector[2])
                
            # Getting the new vertex set not to compare with the whole model again.
            cmds.select(clear=True)
            cmds.select(f"{model}.vtx[{closestVertexIndex}]")
            (cmds.GrowPolygonSelectionRegion() for _ in range(3))
            vertex_set = cmds.ls(selection=True, flatten=True)
            cmds.select(clear=True)

            translatedClosestVertexIndex = self.getClosestVertex(new_translation, vertex_set)
            if closestVertexIndex == translatedClosestVertexIndex:
                cmds.xform(tweakCtrl, piv=new_translation, ws=True)
            else:
                print("Error: offset changed closest vertex")


    def randomizeNewPivot(self, rivet_controllers_list, attach_to_geo_list):
        cmds.progressWindow(title="Processing", progress=0, status=rivet_controllers_list[0], isInterruptable=True)
        for idx, control in enumerate(rivet_controllers_list):
            cmds.progressWindow(edit=True, progress=int((idx+1)/len(rivet_controllers_list) * 100), status=control)
            self.randomizeTranslation(control, attach_to_geo_list[idx])
        cmds.progressWindow(endProgress=True)


    def getRivetOptionsList(self, follicles_origin_list):
        rivetControllerOptionsDic = {}
        for follicle in follicles_origin_list:
            rivetNet = self.getRivetNetFromFolTransform(follicle)
            rivet_controller = cmds.listConnections(f"{rivetNet}.itemNode", source=True, destination=False)[0]
            pacNode = cmds.listConnections(f"{rivetNet}.pacNode", source=True, destination=False)[0]
            transformAttached = cmds.listConnections(f"{rivetNet}.rivet", source=True, destination=False)[0]
            has_inv_translate = True if cmds.listConnections(f"{rivetNet}.invTGrp", source=True, destination=False) else False
            has_inv_rotate = True if cmds.listConnections(f"{rivetNet}.invRGrp", source=True, destination=False) else False
            addInvert = has_inv_translate or has_inv_rotate
            connections = cmds.listConnections(pacNode, source=True, destination=True, plugs=True) or []
            found_attrs = [conn.split('.')[-1] for conn in connections]
            translate_connected = all(attr in found_attrs for attr in ['translateX', 'translateY', 'translateZ'])
            rotate_connected = all(attr in found_attrs for attr in ['rotateX', 'rotateY', 'rotateZ'])
            has_parent_group = transformAttached.endswith("_Grp")
            rivetControllerOptionsDic[rivet_controller] = [translate_connected, rotate_connected, has_parent_group, addInvert, has_inv_translate, has_inv_rotate, False]
        return rivetControllerOptionsDic


    def recreateRivetWithNewPivot(self, rivet_controllers_list, attach_geo_list):
        for idx, controller in enumerate(rivet_controllers_list):
            uvSet = cmds.polyUVSet(attach_geo_list[idx], query=True, allUVSets=True)[0]
            self.dpRivet.dpCreateRivet(attach_geo_list[idx], uvSet, [controller], *self.rivetOptionsDic[controller])


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
                toCheckList = objList
            else:
                toCheckList = cmds.ls(type='follicle')
            if toCheckList:
                follicles_origin_list = self.listFolliclesAtOrigin()
                rivet_controllers_list, attach_geo_list = self.getConnectionsFromFollicle(follicles_origin_list)
                self.checkedObjList = rivet_controllers_list.copy()
                self.foundIssueList = [True] * len(self.checkedObjList)
                if not self.firstMode:
                    self.rivetOptionsDic = self.getRivetOptionsList(follicles_origin_list)
                    self.removeRivetFromFollicleTransformList(follicles_origin_list)
                    self.randomizeNewPivot(rivet_controllers_list, attach_geo_list)
                    self.recreateRivetWithNewPivot(rivet_controllers_list, attach_geo_list)
                    follicles_origin_list = self.listFolliclesAtOrigin()
                    if len(follicles_origin_list) == 0:
                        self.resultOkList.append(True)
                        for fixed in rivet_controllers_list:
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+fixed)
                    else:
                        self.resultOkList.append(False)
                        rivet_controllers_list, attach_geo_list = self.getConnectionsFromFollicle(follicles_origin_list)
                        for nonFixed in rivet_controllers_list:
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+nonFixed)
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
