# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "DisplayLayers"
TITLE = "v054_displayLayers"
DESCRIPTION = "v055_displayLayersDesc"
ICON = "/Icons/dp_displayLyr.png"

DP_DISPLAYLAYERS_VERSION = 1.5


class DisplayLayers(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DISPLAYLAYERS_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

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
        if objList:
            ctrlsGeometryList = objList
        else:
            # List all controls
            ctrlsGeometryList = None
            self.allCtrlsList = self.dpUIinst.ctrls.getControlList()
            if self.allCtrlsList:
                allGeoList = self.getGeometryTranform()
                ctrlsGeometryList = self.allCtrlsList
                if allGeoList:
                    ctrlsGeometryList = self.allCtrlsList + allGeoList
        if ctrlsGeometryList:
            self.geoLayerName = "Geo_Lyr"
            self.ctrlLayerName = "Ctrl_Lyr"
            allLayersList = cmds.ls(type="displayLayer")
            self.extraLayerToDelete = []
            for layer in allLayersList:
                if layer != self.geoLayerName and layer != self.ctrlLayerName and layer != "defaultLayer":
                    self.extraLayerToDelete.append(layer)
            if not self.extraLayerToDelete:
                if cmds.objExists(self.geoLayerName) and cmds.objExists(self.ctrlLayerName):
                    layersConfigurationCheckList = [True, True, 2, True, True, 0]
                    geoLyrVisibility = cmds.getAttr(self.geoLayerName+".visibility") #True
                    geoLyrHideOnPlayback = cmds.getAttr(self.geoLayerName+".hideOnPlayback") #True
                    geolLyrDisplayType = cmds.getAttr(self.geoLayerName+".displayType") #2 = ref
                    ctrlLyrVisibility = cmds.getAttr(self.ctrlLayerName+".visibility") #True
                    ctrlLyrHideOnPlayback = cmds.getAttr(self.ctrlLayerName+".hideOnPlayback") #True
                    ctrlLyrDisplayType = cmds.getAttr(self.ctrlLayerName+".displayType") #0 = none
                    layersConfiguration = [geoLyrVisibility, geoLyrHideOnPlayback, geolLyrDisplayType, ctrlLyrVisibility, ctrlLyrHideOnPlayback, ctrlLyrDisplayType]
                    # Check layers configuration
                    if layersConfiguration == layersConfigurationCheckList:
                        itemsInGeoLayerList = cmds.editDisplayLayerMembers(self.geoLayerName, fullNames=True, query=True)
                        itemsInCtrlLayerList = cmds.editDisplayLayerMembers(self.ctrlLayerName, query=True)
                        # Check layers members
                        if itemsInGeoLayerList and itemsInCtrlLayerList:
                            missingGeoList = list(set(allGeoList) - set(itemsInGeoLayerList))
                            remainingGeoList = list(set(itemsInGeoLayerList) - set(allGeoList))
                            missingCtrlList = list(set(self.allCtrlsList) - set(itemsInCtrlLayerList))
                            remainingCtrlList = list(set(itemsInCtrlLayerList) - set(self.allCtrlsList))
                            toFixList = missingGeoList + remainingGeoList + missingCtrlList + remainingCtrlList
                            if toFixList:
                                self.verifyFixMode(toFixList)
                        else:
                            # Empty layer
                            self.verifyFixMode([self.dpUIinst.lang['v056_emptyLayers']])
                    else:
                        # Layer configuration
                        self.verifyFixMode([self.dpUIinst.lang['v057_layerConfiguration']])
                else:
                    # No display layer
                    self.verifyFixMode([self.dpUIinst.lang['v054_displayLayers']])
            else:
                # Extra Lyr to delete
                self.verifyFixMode(self.extraLayerToDelete)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def createDisplayLayers(self, *args):
        """ Call functions to create Geo_Lyr and Ctrl_Lyr
            If there's no geometry on the groups Render_Grp and Proxy_Grp, it will delete the Geo_Lyr
        """ 
        geoList = self.getGeometryTranform()
        if geoList:
            self.createNewLayer(geoList, self.geoLayerName)
        else:
            if cmds.objExists(self.geoLayerName):
                cmds.delete(self.geoLayerName)
        self.createNewLayer(self.allCtrlsList, self.ctrlLayerName, False)
        if self.extraLayerToDelete:
            cmds.delete(self.extraLayerToDelete)
        

    def createNewLayer(self, itemList, layerName, geoType=True, *args):
        """ Creates Geo_Lyr with the objects inside Render_Grp and Proxy_Grp
        """
        if itemList:
            cmds.select(itemList)
            newLayer = str(cmds.createDisplayLayer(name=layerName, noRecurse=True))
            # Count numbers in name
            numeric = 0
            for n in newLayer:
                if n.isdigit():
                    numeric +=1
            # If there's numeric in name, delete the first, rename the new one and displayType 2 option
            if numeric > 0:           
                cmds.delete(layerName)
                newLayer = cmds.rename(newLayer, layerName)
                if geoType:
                    cmds.setAttr(newLayer+".displayType", 2)
                cmds.select(clear=True)
            else:
                if geoType:
                    cmds.setAttr(layerName+".displayType", 2)
                cmds.select(clear=True)


    def getGeometryTranform(self, *args):
        """ Get all transform nodes from Render_Grp or convention geometry group name.
            If it finds nothing, it will return an empty list.
        """
        existsGrpList, allShapesList = [], []
        meshGrpList = ["Mesh_Grp", "mesh_grp", "Geo_Grp", "geo_grp", "grp_cache"]
        renderGrp = self.utils.getNodeByMessage("renderGrp")
        if renderGrp:
            existsGrpList.append(renderGrp)
        for grp in meshGrpList:
            if cmds.objExists(grp):
                existsGrpList.append(grp)
        if existsGrpList:
            for meshGrp in existsGrpList:
                meshGrpShapesList = cmds.listRelatives(meshGrp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
                if meshGrpShapesList:
                    allShapesList = list(set(allShapesList + meshGrpShapesList))
            allGeoList = []
            if allShapesList:
                for shape in allShapesList:
                    transformList = cmds.listRelatives(shape, fullPath=True, parent=True)
                    if transformList:
                        # Get the transform only
                        allGeoList.append(transformList[0])
            return allGeoList
    

    def verifyFixMode(self, itemList, *args):
        """ This function will check if the item is a list or not.
            If it's a list it will append the items in the dic and run the main function once.
            If it's not a list it will append the obj and run the main function.
        """
        if itemList:
            self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
            for i, item in enumerate(itemList):
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if self.firstMode:
                    self.resultOkList.append(False)
                    self.checkedObjList.append(item)
                    self.foundIssueList.append(True)
                else:
                    try:#verify
                        # It will run function only one time to create displayLayers in the last index from the loop, 
                        # otherwise it will create for every index
                        if i == len(itemList) - 1:
                            self.createDisplayLayers()    
                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                    except:#fix
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
