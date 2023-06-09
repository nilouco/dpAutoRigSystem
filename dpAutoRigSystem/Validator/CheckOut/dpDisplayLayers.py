# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ...Modules.Library import dpUtils

# global variables to this module:
CLASS_NAME = "DisplayLayers"
TITLE = "v054_displayLayers"
DESCRIPTION = "v055_displayLayersDesc"
ICON = "/Icons/dp_displayLyr.png"

DP_DISPLAYLAYERS_VERSION = 1.1


class DisplayLayers(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
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
                    layersConfigurationCheckList = [True, False, 2, True, True, 0]
                    geoLyrVisibility = cmds.getAttr(self.geoLayerName+".visibility") #True
                    geoLyrHideOnPlayback = cmds.getAttr(self.geoLayerName+".hideOnPlayback") #False
                    geolLyrDisplayType = cmds.getAttr(self.geoLayerName+".displayType") #2
                    ctrlLyrVisibility = cmds.getAttr(self.ctrlLayerName+".visibility") #True
                    ctrlLyrHideOnPlayback = cmds.getAttr(self.ctrlLayerName+".hideOnPlayback") #True
                    ctrlLyrDisplayType = cmds.getAttr(self.ctrlLayerName+".displayType") #0
                    layersConfiguration = [geoLyrVisibility, geoLyrHideOnPlayback, geolLyrDisplayType, ctrlLyrVisibility, ctrlLyrHideOnPlayback, ctrlLyrDisplayType]
                    # Check layers configuration
                    if layersConfiguration == layersConfigurationCheckList:
                        itemsInGeoLayerList = cmds.editDisplayLayerMembers(self.geoLayerName, query=True)
                        itemsInCtrlLayerList = cmds.editDisplayLayerMembers(self.ctrlLayerName, query=True)
                        # Check layers members
                        if itemsInGeoLayerList and itemsInCtrlLayerList:
                            progressAmount = 0
                            maxProcess = len(self.allCtrlsList)
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
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
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
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
                else: #ctrl
                    cmds.setAttr(newLayer+".hideOnPlayback", 1)
                cmds.select(clear=True)
            else:
                if geoType:
                    cmds.setAttr(layerName+".displayType", 2)
                else: #ctrl
                    cmds.setAttr(layerName+".hideOnPlayback", 1)
                cmds.select(clear=True)


    def getGeometryTranform(self, *args):
        """ Get all transform nodes from Render_Grp and Proxy_Grp. If finds nothing, it will return an empty list.
        """
        renderGrp = dpUtils.getNodeByMessage("renderGrp")
        proxyGrp = dpUtils.getNodeByMessage("proxyGrp")
        if renderGrp and proxyGrp:
            renderGrpShapesList = cmds.listRelatives(renderGrp, allDescendents=True, type="mesh") or []
            proxyGrpShapesList = cmds.listRelatives(proxyGrp, allDescendents=True, type="mesh") or []
            allShapesList = list(set(renderGrpShapesList + proxyGrpShapesList))
            allGeoList = []
            if allShapesList:
                for shape in allShapesList:
                    if not "Orig" in shape:
                        try:
                            transform = cmds.listRelatives(shape, parent=True)[0]
                            # Get the transform only
                            allGeoList.append(transform)
                        except:
                            pass
            return allGeoList


    def verifyFixMode(self, itemList, *args):
        """ This function will check if the item is a list or not.
            If it's a list it will append the items in the dic and run the main function once.
            If it's not a list it will append the obj and run the main function.
        """
        if itemList:
            for i, item in enumerate(itemList):
                if self.verifyMode:
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
