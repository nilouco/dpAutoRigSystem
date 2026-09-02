# importing libraries:
from maya import cmds
from maya import mel
from maya.api import OpenMaya
from ....library.base import action
from ....library.tool import rivet
import random
from importlib import reload

# global variables to this module:
CLASS_NAME = "BrokenRivet"
TITLE = "v126_brokenRivet"
DESCRIPTION = "v127_brokenRivetDesc"
WIKI = "07-‐-Validator#-broken-rivets"



class BrokenRivet(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(rivet)
        self.rivet = rivet.Rivet(self.ar)
        self.rivet.ui = False


    def get_at_origin_follicles(self):
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


    def disable_pac(self, fol_tr, net_node):
        try:
            pac = cmds.listConnections(f"{net_node}.pacNode", destination=False)[0]
            pac_attrs = cmds.listAttr(pac, settable=True, visible=True, string=f"{fol_tr}*")
            if pac_attrs:
                cmds.setAttr(f"{pac}.{pac_attrs[0]}", 0) #pac_attr
        except Exception as e:
            print(e)


    def remove_rivet_from_net(self, fol_tr, rivet_net):
        """ Remove the rivet from its network node.
        """
        rivet_transform = cmds.listConnections(f"{rivet_net}.rivet", destination=False)
        if rivet_transform:
            rivet_transform = rivet_transform[0]
        rivet_ctrl = cmds.listConnections(f"{rivet_net}.itemNode", destination=False)[0]
        try:
            original_parent = cmds.listRelatives(rivet_transform, parent=True)
            current_parent = cmds.listRelatives(rivet_ctrl, parent=True)
            if original_parent == None:
                if current_parent != original_parent:
                    cmds.parent(rivet_ctrl, world=True)
            else:
                original_parent = original_parent[0]
                if not original_parent in current_parent:
                    cmds.parent(rivet_ctrl, original_parent)
            if rivet_ctrl != rivet_transform:
                cmds.delete([rivet_transform, fol_tr])
            else:
                cmds.delete(fol_tr)
        except Exception as e:
            print(e)
            cmds.delete(fol_tr)
        connections = cmds.listConnections(f"{rivet_net}.message", plugs=True, destination=True)
        if len(connections) > 1:
            for connection in connections:
                if "rivet_net" in connection:
                    cmds.deleteAttr(connection)
                    break
        else:
            cmds.deleteAttr(connections[0])
        cmds.delete(rivet_net)


    def get_rivet_from_fol_transform(self, fol_tr):
        fol_tr_outputs = cmds.listConnections(f"{fol_tr}.message", source=False, destination=True)
        for connection in fol_tr_outputs:
            if "_Net" in connection:
                return connection


    def remove_rivet_from_fol_transforms(self, fol_transforms):
        for fol_tr in fol_transforms:
            rivet_net = self.get_rivet_from_fol_transform(fol_tr)
            self.disable_pac(fol_tr, rivet_net)
            self.remove_rivet_from_net(fol_tr, rivet_net)


    def get_connections_from_fol(self, fol_origins):
        controllers_list = []
        attach_geos = []
        for fol_tr in fol_origins:
            rivet_net = self.get_rivet_from_fol_transform(fol_tr)
            rivet_controller = cmds.listConnections(f"{rivet_net}.itemNode", source=True, destination=False)[0]
            face_to_rivet_geo = cmds.listConnections(f"{rivet_net}.geoToAttach", source=True, destination=False)[0]
            if rivet_controller:
                controllers_list.append(rivet_controller)
            if face_to_rivet_geo:
                attach_geos.append(face_to_rivet_geo)
        return controllers_list, attach_geos


    def get_closest_vertex(self, point, vertices):
        """
        Finds the closest vertex to a given point from a list of vertex component strings.
        :param point: A tuple (x, y, z) representing the target point.
        :param vertices: List of strings like "mesh.vtx[0]"
        :return: Index of the closest vertex in the list.
        """
        if not vertices:
            raise ValueError("Vertex list is empty.")
        # Extract mesh name from the first element
        mesh_name = vertices[0].split(".")[0]
        # Get MDagPath from mesh name
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(mesh_name)
        dag_path = selection_list.getDagPath(0)
        fn_mesh = OpenMaya.MFnMesh(dag_path)
        target_point = OpenMaya.MPoint(point)
        # Extract indices from vertex strings
        vertex_indices = [int(v.split("[")[1].strip("]")) for v in vertices]
        # Find closest vertex
        closest_vertex_index = -1
        min_distance = float("inf")
        for i in vertex_indices:
            vtx_pos = fn_mesh.getPoint(i, OpenMaya.MSpace.kWorld)
            distance = (vtx_pos - target_point).length()
            if distance < min_distance:
                min_distance = distance
                closest_vertex_index = i
        return closest_vertex_index


    def get_connected_edges(self, mesh_name, vertex_index):
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


    def get_edge_length(self, mesh_name, edge_index):
        """
        Returns the length of an edge given its index using OpenMaya.
        :param mesh_name: Name of the mesh object.
        :param edge_index: Index of the edge.
        :return: Length of the edge.
        """
        # Get DAG path of the mesh
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(mesh_name)
        dag_path = selection_list.getDagPath(0)
        fn_mesh = OpenMaya.MFnMesh(dag_path)
        # Get the two vertex indices that form the edge
        edge_vertices = fn_mesh.getEdgeVertices(edge_index)
        # Get vertex positions in world space
        pt1 = fn_mesh.getPoint(edge_vertices[0], OpenMaya.MSpace.kWorld)
        pt2 = fn_mesh.getPoint(edge_vertices[1], OpenMaya.MSpace.kWorld)
        # Compute Euclidean distance
        return (pt2 - pt1).length()


    def normalize_vector_sum(self, vectors):
        """
        Sums a list of vectors and returns the normalized result using OpenMaya.
        :param vectors: List of tuples or lists representing vectors (x, y, z).
        :return: Normalized MVector.
        """
        if not vectors:
            raise ValueError("Vector list is empty")
        total = OpenMaya.MVector(0.0, 0.0, 0.0)
        for vec in vectors:
            total += OpenMaya.MVector(vec)
        if total.length() == 0.0:
            raise ValueError("Sum of vectors is zero, cannot normalize")
        return total.normal()


    def get_direction_vector(self, model, vtx_index):
        cmds.select(clear=True)
        cmds.select(f"{model}.vtx[{vtx_index}]")
        cmds.GrowPolygonSelectionRegion()
        vertex_list = cmds.ls(selection=True, flatten=True)
        vertex_vectors = []
        for vertex in vertex_list:
            if ".vtx[" in vertex:  # Ensure it's a vertex selection
                vtx_vector = cmds.pointPosition(vertex)
                vertex_vectors.append(vtx_vector)
        normalized_vectors = self.normalize_vector_sum(vertex_vectors)
        return normalized_vectors


    def randomize_translation(self, tweak_ctrl, model):
        """
        Randomizes the translation of an tweak_ctrl in Maya while ensuring the offset is insignificant compared to its scale.
        """
        if cmds.objExists(tweak_ctrl):
            # Get current translation
            translation = cmds.xform(tweak_ctrl, query=True, translation=True, worldSpace=True)
            vertex_set = cmds.ls(f"{model}.vtx[*]", flatten=True)
            closest_vertex_index = self.get_closest_vertex(translation, vertex_set)
            closest_edge_indexes = self.get_connected_edges(model, closest_vertex_index)
            closest_edge_avg_len = 0.0
            for edge_index in closest_edge_indexes:
                closest_edge_avg_len += self.get_edge_length(model, edge_index)
            closest_edge_avg_len = closest_edge_avg_len/len(closest_edge_indexes)
            # Unitary direction vector to use as offset direction.
            u_vector =  self.get_direction_vector(model, closest_vertex_index)
            # Calculate a small offset based on scale.
            max_offset = closest_edge_avg_len * 0.1
            # Compute the offset that is going to be used.
            offset = random.uniform(0, max_offset)
            # new_position = t* + d.u*
            new_translation = (translation[0] + offset * u_vector[0], 
                            translation[1] + offset * u_vector[1],
                            translation[2] + offset * u_vector[2])
            # Getting the new vertex set not to compare with the whole model again.
            cmds.select(clear=True)
            cmds.select(f"{model}.vtx[{closest_vertex_index}]")
            (cmds.GrowPolygonSelectionRegion() for _ in range(3))
            vertex_set = cmds.ls(selection=True, flatten=True)
            cmds.select(clear=True)
            translated_closest_vertex_index = self.get_closest_vertex(new_translation, vertex_set)
            if closest_vertex_index == translated_closest_vertex_index:
                cmds.xform(tweak_ctrl, piv=new_translation, ws=True)
            else:
                mel.eval('warning \"'+self.ar.data.lang['e022_offsetClosetVertex']+'\";')


    def randomize_new_pivot(self, rivet_controllers, attach_to_geo_list):
        for idx, control in enumerate(rivet_controllers):
            self.randomize_translation(control, attach_to_geo_list[idx])


    def get_rivet_options(self, fol_origins):
        rivet_controller_options_data = {}
        for follicle in fol_origins:
            rivet_net = self.get_rivet_from_fol_transform(follicle)
            rivet_controller = cmds.listConnections(f"{rivet_net}.itemNode", source=True, destination=False)[0]
            pac = cmds.listConnections(f"{rivet_net}.pacNode", source=True, destination=False)[0]
            transform_attached = cmds.listConnections(f"{rivet_net}.rivet", source=True, destination=False)[0]
            has_inv_translate = cmds.listConnections(f"{rivet_net}.invTGrp", source=True, destination=False) or "multiplyDivide" in list(map(lambda node : cmds.nodeType(node), cmds.listConnections(f"{rivet_controller}.translateX", source=False, destination=True) or [None]))
            has_inv_rotate = cmds.listConnections(f"{rivet_net}.invRGrp", source=True, destination=False) or "multiplyDivide" in list(map(lambda node : cmds.nodeType(node), cmds.listConnections(f"{rivet_controller}.rotateX", source=False, destination=True) or [None]))
            add_invet = has_inv_translate or has_inv_rotate
            connections = cmds.listConnections(pac, source=True, destination=True, plugs=True) or []
            found_attrs = [conn.split('.')[-1] for conn in connections]
            translate_connected = all(attr in found_attrs for attr in ['translateX', 'translateY', 'translateZ'])
            rotate_connected = all(attr in found_attrs for attr in ['rotateX', 'rotateY', 'rotateZ'])
            has_parent_group = transform_attached.endswith("_Grp")
            rivet_controller_options_data[rivet_controller] = [translate_connected, rotate_connected, has_parent_group, add_invet, has_inv_translate, has_inv_rotate, False]
        return rivet_controller_options_data


    def recreate_rivet_with_new_pivot(self, rivet_controllers, attach_geos):
        for idx, controller in enumerate(rivet_controllers):
            uv_set = cmds.polyUVSet(attach_geos[idx], query=True, allUVSets=True)[0]
            self.rivet.create_rivet(attach_geos[idx], uv_set, [controller], *self.rivet_options_data[controller])
            connected_joints = cmds.listConnections(controller, source=False, type="joint")
            if connected_joints:
                suffix = connected_joints[0][connected_joints[0].rfind('_'):]
                if suffix != "_Jis":
                    pac_connected_attr = cmds.listConnections(f"{controller}.rotatePivot", source=False, plugs=True, type="pac")[0]
                    if pac_connected_attr:
                        # If it is not an indirect skinning joint, disregard the new pivot adjusted in the parent constraint.
                        cmds.disconnectAttr(f"{controller}.rotatePivot", pac_connected_attr)


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
                check_items = cmds.ls(inputs, type="follicle")
            else:
                check_items = cmds.ls(type='follicle')
            if check_items:
                fol_origins = self.get_at_origin_follicles()
                rivet_controllers, attach_geos = self.get_connections_from_fol(fol_origins)
                self.checked_items = rivet_controllers.copy()
                self.found_issues = [True] * len(self.checked_items)
                if not self.first_mode:
                    max_tries = 5
                    while len(fol_origins) != 0 and max_tries != 0:
                        max_tries -= 1
                        self.rivet_options_data = self.get_rivet_options(fol_origins)
                        self.remove_rivet_from_fol_transforms(fol_origins)
                        self.randomize_new_pivot(rivet_controllers, attach_geos)
                        self.recreate_rivet_with_new_pivot(rivet_controllers, attach_geos)
                        fol_origins = self.get_at_origin_follicles()
                        rivet_controllers, attach_geos = self.get_connections_from_fol(fol_origins)
                    if len(fol_origins) == 0:
                        self.good_results.append(True)
                        for fixed in rivet_controllers:
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+fixed)
                    else:
                        self.good_results.append(False)
                        rivet_controllers, attach_geos = self.get_connections_from_fol(fol_origins)
                        for non_fixed in rivet_controllers:
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+non_fixed)
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
