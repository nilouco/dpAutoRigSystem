#----------------------------------------------------------------------------------
#
#   Thanks to:
#              Zaitsev Evgeniy
#              ev.zaitsev@gmail.com
#              vtxNormalsToSoftHardEdges.py
#              https://github.com/evzaitsev/maya_scripts/blob/main/modeling/vtxNormalsToSoftHardEdges.py
#
#----------------------------------------------------------------------------------

# importing libraries:
from maya import OpenMaya



class ConvertNormals(object):
    def __init__(self, ar):
        self.ar = ar


    def get_hard_edge(self, item):
        """ Return a list of hard edges if exists.
        """
        m_path = self.ar.naming.get_mdagpath_by_name(item)
        m_hard_edges = []
        m_it_edge = OpenMaya.MItMeshEdge(m_path) 
        self.m_fn_mesh = OpenMaya.MFnMesh(m_path)
        while not m_it_edge.isDone():
            m_faces_array = OpenMaya.MIntArray()
            m_edge_id = m_it_edge.index()
            m_it_edge.getConnectedFaces(m_faces_array)  
            m_start, m_end = self.get_edge_vertices(m_edge_id)
            m_state = self.is_edge_smooth(m_start, m_end, m_faces_array)
            if m_state == False:
                m_hard_edges.append(m_edge_id)
            #print(m_edge_id, m_state, m_start, m_end, m_faces_array)
            m_it_edge.next()
        return m_hard_edges


    def set_soft_hard(self, item):
        """ It checks the edge state (soft/hard) and set it after unlock normals.
        """
        m_path = self.ar.naming.get_mdagpath_by_name(item)
        m_hard_edges = self.get_hard_edge(item)
        # select and set Hard Edges 
        m_a_member = ''
        m_last_indices = [-1, -1]
        m_have_edge = False
        for m_edge_id in m_hard_edges:
            if m_last_indices[0] == -1:
                m_last_indices[0] = m_edge_id
                m_last_indices[1] = m_edge_id
            else:
                m_current_index = m_edge_id
                if m_current_index > (m_last_indices[1]+1):
                    m_a_member += '{0}.e[{1}:{2}] '.format(m_path.fullPathName(), m_last_indices[0], m_last_indices[1])
                    m_last_indices[0] = m_current_index
                    m_last_indices[1] = m_current_index 
                else:
                    m_last_indices[1] = m_current_index
            m_have_edge = True
        if m_have_edge:
            m_a_member += '{0}.e[{1}:{2}] '.format(m_path.fullPathName(), m_last_indices[0], m_last_indices[1])
        m_result_string = ""
        m_result_string += "select -r {};\n".format(m_path.fullPathName())
        m_result_string += "polyNormalPerVertex -ufn true;\n"
        m_result_string += "polySoftEdge -a 180 -ch 0;\n"
        if m_a_member != '':
            m_result_string += "select -r {0};\n".format(m_a_member)
            m_result_string += "polySoftEdge -a 0 -ch 0;\n"
        #else:
        #    print("No hard edges in this mesh, set all edges to soft!")
        m_result_string += "select -cl;"
        #print(m_result_string)
        OpenMaya.MGlobal.executeCommand(m_result_string)
    

    def get_edge_vertices(self, m_edge_id):
        """ Returns the connected vertices of the given edge (start and end).
        """
        m_util = OpenMaya.MScriptUtil() 
        m_util.createFromList([0, 0], 2)
        m_ptr = m_util.asInt2Ptr()
        self.m_fn_mesh.get_edge_vertices(m_edge_id, m_ptr)
        m_start = m_util.getInt2ArrayItem(m_ptr,0,0)
        m_end = m_util.getInt2ArrayItem(m_ptr,0,1)
        return m_start, m_end
        

    def is_edge_smooth(self, m_start, m_end, m_faces_array):
        """ Verifies if the edge is smooth or not.
            Returns:
                     True if soft
                     False if hard
        """
        m_state = True
        m_normal_start_arr = OpenMaya.MVectorArray()
        m_normal_end_arr   = OpenMaya.MVectorArray()
        for m_faceId in m_faces_array:
            m_normal_start = OpenMaya.MVector()
            m_normal_end   = OpenMaya.MVector()
            self.m_fn_mesh.getFaceVertexNormal(m_faceId, m_start, m_normal_start, OpenMaya.MFn.kWorld)
            self.m_fn_mesh.getFaceVertexNormal(m_faceId, m_end, m_normal_end, OpenMaya.MFn.kWorld)
            m_normal_start_arr.append(m_normal_start)
            m_normal_end_arr.append(m_normal_end)
        m_normal_start_1 = m_normal_start_arr[0]
        for i in range(m_normal_start_arr.length()):
            m_normal_start_2 = m_normal_start_arr[i]
            if m_normal_start_1 != m_normal_start_2:
                m_state = False
            m_normal_start_1 = m_normal_start_2
        m_normal_end_1 = m_normal_end_arr[0]
        for i in range(m_normal_end_arr.length()):
            m_normal_end_2 = m_normal_end_arr[i]
            if m_normal_end_1 != m_normal_end_2:
                m_state = False
            m_normal_end_1 = m_normal_end_2
        return m_state
