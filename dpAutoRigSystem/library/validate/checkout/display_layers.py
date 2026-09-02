# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DisplayLayers"
TITLE = "v054_displayLayers"
DESCRIPTION = "v055_displayLayersDesc"
WIKI = "07-‐-Validator#-display-layers"



class DisplayLayers(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

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
                ctrlsGeometryList = inputs
            else:
                # List all controls
                ctrlsGeometryList = None
                self.allCtrlsList = self.ar.ctrls.get_controllers()
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
                        layersConfigurationCheckList = [True, False, 2, True, False, 0]
                        geoLyrVisibility = cmds.getAttr(self.geoLayerName+".visibility") #True
                        geoLyrHideOnPlayback = cmds.getAttr(self.geoLayerName+".hideOnPlayback") #False
                        geolLyrDisplayType = cmds.getAttr(self.geoLayerName+".displayType") #2 = ref
                        ctrlLyrVisibility = cmds.getAttr(self.ctrlLayerName+".visibility") #True
                        ctrlLyrHideOnPlayback = cmds.getAttr(self.ctrlLayerName+".hideOnPlayback") #False
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
                                self.verifyFixMode([self.ar.data.lang['v056_emptyLayers']])
                        else:
                            # Layer configuration
                            self.verifyFixMode([self.ar.data.lang['v057_layerConfiguration']])
                    else:
                        # No display layer
                        self.verifyFixMode([self.ar.data.lang['v054_displayLayers']])
                else:
                    # Extra Lyr to delete
                    self.verifyFixMode(self.extraLayerToDelete)
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


    def createDisplayLayers(self, *args):
        """ Call functions to create Geo_Lyr and Ctrl_Lyr
            If there's no geometry on the groups Render_Grp and Proxy_Grp, it will delete the Geo_Lyr
        """ 
        geos = self.getGeometryTranform()
        if geos:
            self.createNewLayer(geos, self.geoLayerName)
        else:
            if cmds.objExists(self.geoLayerName):
                cmds.delete(self.geoLayerName)
        self.createNewLayer(self.allCtrlsList, self.ctrlLayerName, False)
        if self.extraLayerToDelete:
            cmds.delete(self.extraLayerToDelete)
        

    def createNewLayer(self, items, layerName, geoType=True, *args):
        """ Creates Geo_Lyr with the objects inside Render_Grp and Proxy_Grp
        """
        if items:
            cmds.select(items)
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
        renderGrp = self.ar.utils.get_node_by_message("renderGrp")
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
                    transforms = cmds.listRelatives(shape, fullPath=True, parent=True)
                    if transforms:
                        # Get the transform only
                        allGeoList.append(transforms[0])
            return allGeoList
    

    def verifyFixMode(self, items, *args):
        """ This function will check if the item is a list or not.
            If it's a list it will append the items in the data and run the main function once.
            If it's not a list it will append the item and run the main function.
        """
        if items:
            self.ar.utils.set_progress(max=len(items), add_one=False, add_number=False)
            for i, item in enumerate(items):
                self.ar.utils.set_progress(self.ar.data.lang[self.title])
                if self.first_mode:
                    self.good_results.append(False)
                    self.checked_items.append(item)
                    self.found_issues.append(True)
                else:
                    try:#verify
                        # It will run function only one time to create displayLayers in the last index from the loop, 
                        # otherwise it will create for every index
                        if i == len(items) - 1:
                            self.createDisplayLayers()    
                        self.good_results.append(True)
                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                    except:#fix
                        self.good_results.append(False)
                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
