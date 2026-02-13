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

DP_SOFTHARDEDGES_VERSION = 1.00


class ConvertNormals(object):
    def __init__(self, dpUIinst):
        self.utils = dpUIinst.utils
        self.version = DP_SOFTHARDEDGES_VERSION


    def getHardEdges(self, item):
        """ Return a list of hard edges if exists.
        """
        m_path = self.utils.getMDagPathbyName(item)
        m_hardEdges = []
        m_itEdgeIt = OpenMaya.MItMeshEdge(m_path) 
        self.m_fnMesh = OpenMaya.MFnMesh(m_path)
        while not m_itEdgeIt.isDone():
            m_facesArray = OpenMaya.MIntArray()
            m_edgeId = m_itEdgeIt.index()
            m_itEdgeIt.getConnectedFaces(m_facesArray)  
            m_start, m_end = self.getEdgeVertices(m_edgeId)
            m_state = self.isEdgeSmooth(m_start, m_end, m_facesArray)
            if m_state == False:
                m_hardEdges.append(m_edgeId)
            #print(m_edgeId, m_state, m_start, m_end, m_facesArray)
            m_itEdgeIt.next()
        return m_hardEdges


    def setSoftHard(self, item):
        """ It checks the edge state (soft/hard) and set it after unlock normals.
        """
        m_path = self.utils.getMDagPathbyName(item)
        m_hardEdges = self.getHardEdges(item)
        # select and set Hard Edges 
        m_aMember = ''
        m_lastIndices = [-1, -1]
        m_haveEdge = False
        for m_edgeId in m_hardEdges:
            if m_lastIndices[0] == -1:
                m_lastIndices[0] = m_edgeId
                m_lastIndices[1] = m_edgeId
            else:
                m_currentIndex = m_edgeId
                if m_currentIndex > (m_lastIndices[1]+1):
                    m_aMember += '{0}.e[{1}:{2}] '.format(m_path.fullPathName(), m_lastIndices[0], m_lastIndices[1])
                    m_lastIndices[0] = m_currentIndex
                    m_lastIndices[1] = m_currentIndex 
                else:
                    m_lastIndices[1] = m_currentIndex
            m_haveEdge = True
        if m_haveEdge:
            m_aMember += '{0}.e[{1}:{2}] '.format(m_path.fullPathName(), m_lastIndices[0], m_lastIndices[1])
        m_resultString = ""
        m_resultString += "select -r {};\n".format(m_path.fullPathName())
        m_resultString += "polyNormalPerVertex -ufn true;\n"
        m_resultString += "polySoftEdge -a 180 -ch 0;\n"
        if m_aMember != '':
            m_resultString += "select -r {0};\n".format(m_aMember)
            m_resultString += "polySoftEdge -a 0 -ch 0;\n"
        #else:
        #    print("No hard edges in this mesh, set all edges to soft!")
        m_resultString += "select -cl;"
        #print(m_resultString)
        OpenMaya.MGlobal.executeCommand(m_resultString)
    

    def getEdgeVertices(self, m_edgeId):
        """ Returns the connected vertices of the given edge (start and end).
        """
        m_util = OpenMaya.MScriptUtil() 
        m_util.createFromList([0, 0], 2)
        m_ptr = m_util.asInt2Ptr()
        self.m_fnMesh.getEdgeVertices(m_edgeId, m_ptr)
        m_start = m_util.getInt2ArrayItem(m_ptr,0,0)
        m_end = m_util.getInt2ArrayItem(m_ptr,0,1)
        return m_start, m_end
        

    def isEdgeSmooth(self, m_start, m_end, m_facesArray):
        """ Verifies if the edge is smooth or not.
            Returns:
                     True if soft
                     False if hard
        """
        m_state = True
        m_normalStartArr = OpenMaya.MVectorArray()
        m_normalEndArr   = OpenMaya.MVectorArray()
        for m_faceId in m_facesArray:
            m_normalStart = OpenMaya.MVector()
            m_normalEnd   = OpenMaya.MVector()
            self.m_fnMesh.getFaceVertexNormal(m_faceId, m_start, m_normalStart, OpenMaya.MFn.kWorld)
            self.m_fnMesh.getFaceVertexNormal(m_faceId, m_end, m_normalEnd, OpenMaya.MFn.kWorld)
            m_normalStartArr.append(m_normalStart)
            m_normalEndArr.append(m_normalEnd)
        m_normalStart1 = m_normalStartArr[0]
        for i in range(m_normalStartArr.length()):
            m_normalStart2 = m_normalStartArr[i]
            if m_normalStart1 != m_normalStart2:
                m_state = False
            m_normalStart1 = m_normalStart2
        m_normalEnd1 = m_normalEndArr[0]
        for i in range(m_normalEndArr.length()):
            m_normalEnd2 = m_normalEndArr[i]
            if m_normalEnd1 != m_normalEnd2:
                m_state = False
            m_normalEnd1 = m_normalEnd2
        return m_state
