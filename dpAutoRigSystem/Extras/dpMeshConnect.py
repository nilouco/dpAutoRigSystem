# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "MeshConnect"
TITLE = "m045_meshConnect"
DESCRIPTION = "m046_meshConnDesc"
ICON = "/Icons/dp_meshConnect.png"


class MeshConnect():
    def __init__(self, dpUIinst, langDic, langName):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Found masterGrp and call to connect mesh shapes.
        """
        # get masterGrp list
        self.masterGrpList = self.dpGetMasterGrpList()
        if len(self.masterGrpList) > 0:
            for masterGrp in self.masterGrpList:
                # call to connect meshes in this masterGrp
                self.dpConnectMeshes(masterGrp)
        else:
            mel.eval("warning \""+self.langDic[self.langName]['i033_notMasterGrp']+"\";")
        
        
    def dpGetMasterGrpList(*args):
        """ Get masterGrp list and return it.
        """
        # get selection
        selTransformList = cmds.ls(selection=True, type="transform")
        masterGrpList = []
        for transformNode in selTransformList:
            if cmds.objExists(transformNode+".masterGrp") and cmds.getAttr(transformNode+".masterGrp") == 1:
                if not transformNode in masterGrpList:
                    # found a masterGrp
                    masterGrpList.append(transformNode)
            else:
                # search in children list
                selParentList = []
                parentList = cmds.listRelatives(transformNode, parent=True, type='transform')
                if parentList:
                    nextLoop = True
                    while nextLoop:
                        if cmds.objExists(parentList[0]+".masterGrp") and cmds.getAttr(parentList[0]+".masterGrp") == 1:
                            # found a masterGrp
                            selParentList.append(parentList[0])
                            nextLoop = False
                        else:
                            parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
                            if parentList:
                                nextLoop = True
                            else:
                                nextLoop = False
                        if selParentList:
                            for item in selParentList:
                                if not item in masterGrpList:
                                    # found a masterGrp
                                    masterGrpList.append(item)
        return masterGrpList
        
        
    def dpConnectMeshes(self, masterGrp, *args):
        """ List meshes and connect them as:
            FROM (MODELS_Grp *geoShape)
            TO (render_Grp *meshShape)
        """
        # name convention
        geoName = "_GeoShape"
        renderName = "_MeshShape"
        
        # get modelsGrp and renderGrp
        self.modelsGrp = cmds.listConnections(masterGrp+".modelsGrp")[0]
        self.renderGrp = cmds.listConnections(masterGrp+".renderGrp")[0]
        # list polygon shapes
        self.geoShapeList = cmds.listRelatives(self.modelsGrp, allDescendents=True, type="mesh")
        self.meshShapeList = cmds.listRelatives(self.renderGrp, allDescendents=True, type="mesh")
        
        # TODO: change here to found meshes from IDs instead naming convention
        #       wating a good attribute integration with Alembic - Maya/Max
        
        # organize lists of connected and not found relactives
        self.shapeNameList, self.connectedList, self.notFoundRelativeList, self.notFoundNameConventionList = [], [], [], []
        if self.meshShapeList:
            for meshShape in self.meshShapeList:
                if renderName in meshShape:
                    meshName = meshShape.split("_MeshShape")[0]
                    self.shapeNameList.append(meshName)
                else:
                    self.shapeNameList.append(None)
                    self.notFoundNameConventionList.append(meshShape)
                    
            # search FROM and TO shapes to connect them
            if self.shapeNameList:
                for i, shapeName in enumerate(self.shapeNameList):
                    for geoShape in self.geoShapeList:
                        if shapeName:
                            if shapeName in geoShape and not "Orig" in geoShape:
                                if cmds.connectionInfo(self.meshShapeList[i]+".inMesh", isDestination=True):
                                    # break connections
                                    destinationConnection = cmds.connectionInfo(self.meshShapeList[i]+".inMesh", getExactDestination=True)
                                    sourceConnection = cmds.connectionInfo(destinationConnection, sourceFromDestination=True)
                                    cmds.disconnectAttr(sourceConnection, destinationConnection)
                                try:
                                    # create a new connection
                                    cmds.connectAttr(geoShape+".outMesh", self.meshShapeList[i]+".inMesh", force=True)
                                    verticeList = cmds.ls(geoShape+".vtx[:]", flatten=True)
                                    for v, vertex in enumerate(verticeList):
                                        cmds.setAttr(geoShape+".pnts["+str(v)+"].pntx", 0)
                                        cmds.setAttr(geoShape+".pnts["+str(v)+"].pnty", 0)
                                        cmds.setAttr(geoShape+".pnts["+str(v)+"].pntz", 0)
                                    self.connectedList.append(shapeName)
                                except:
                                    self.notFoundRelativeList.append(shapeName)
                                    
            # log
            print "\n-------"
            print "Mesh Connection Log:"
            print "Geometries:", self.geoShapeList
            print "Meshes:", self.meshShapeList
            print "Shape names:", self.shapeNameList
            print "Connected:", self.connectedList
            print "Not found relatives:", self.notFoundRelativeList
            print "Not found name conventions:", self.notFoundNameConventionList
            print "-------"
            
        else:
            mel.eval("warning \""+self.langDic[self.langName]['i041_meshConnEmpty']+"\";")