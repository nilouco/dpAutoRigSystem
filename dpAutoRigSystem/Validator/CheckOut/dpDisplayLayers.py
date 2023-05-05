# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
from maya import mel
from ...Modules.Library import dpUtils
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "DisplayLayers"
TITLE = "v054_displayLayers"
DESCRIPTION = "v055_displayLayersDesc"
ICON = "/Icons/dp_displayLyr.png"

dpExitEditMode_Version = 1.0

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
        self.startValidation()
        
        # ---
        # --- validator code --- beginning
        if objList:
            toCheckList = ctrlsGeometryList
        else:
            # List all controls
            ctrlsGeometryList = None
            self.allCtrlsList = self.dpUIinst.ctrls.getControlList()
            if self.allCtrlsList:
                renderGrpList = self.getGeometryTranform()
                if renderGrpList:
                    ctrlsGeometryList = self.allCtrlsList + renderGrpList
                else:
                    ctrlsGeometryList = self.allCtrlsList
        if ctrlsGeometryList:
            self.geoLayerName = "Geo_Lyr"
            self.ctrlLayerName = "Ctrl_Lyr"
            allLayersList = cmds.ls(type="displayLayer")
            self.extraLyrToDelete = []
            for layer in allLayersList:
                if layer != self.geoLayerName and layer != self.ctrlLayerName and layer != "defaultLayer":
                    self.extraLyrToDelete.append(layer)
            if not self.extraLyrToDelete:
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
                            for item in itemsInCtrlLayerList:
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                            missingGeoList = list(set(renderGrpList) - set(itemsInGeoLayerList))
                            remainingGeoList = list(set(itemsInGeoLayerList) - set(renderGrpList))
                            missingCtrlList = list(set(self.allCtrlsList) - set(itemsInCtrlLayerList))
                            remainingCtrlList = list(set(itemsInCtrlLayerList) - set(self.allCtrlsList))
                            toFixList = missingGeoList + remainingGeoList + missingCtrlList + remainingCtrlList
                            if toFixList:
                                self.verifyFixMode(toFixList)
                        else:
                            # Empty layer
                            self.verifyFixMode(self.dpUIinst.langDic[self.dpUIinst.langName]['v056_emptyLayers'])
                    else:
                        # Layer configuration
                        self.verifyFixMode(self.dpUIinst.langDic[self.dpUIinst.langName]['v057_layerConfiguration'])
                else:
                    # No display layer
                    self.verifyFixMode(self.dpUIinst.langDic[self.dpUIinst.langName]['v054_displayLayers'])
            else:
                # Extra Lyr to delete
                self.verifyFixMode(self.extraLyrToDelete)
        else:
            self.checkedObjList.append("")
            self.foundIssueList.append(False)
            self.resultOkList.append(True)
            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v014_notFoundNodes'])
        # --- validator code --- end
        # ---

        # finishing
        self.finishValidation()
        return self.dataLogDic


    def startValidation(self, *args):
        """ Procedures to start the validation cleaning old data.
        """
        dpBaseValidatorClass.ValidatorStartClass.cleanUpToStart(self)


    def finishValidation(self, *args):
        """ Call main base methods to finish the validation of this class.
        """
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
        dpBaseValidatorClass.ValidatorStartClass.reportLog(self)
        dpBaseValidatorClass.ValidatorStartClass.endProgressBar(self)


    def createDisplayLayers(self, *args):
        """ Call functions to create Geo_Lyr and Ctrl_Lyr
            If there's no geometry on the groups Render_Grp and Proxy_Grp, it will delete the Geo_Lyr
        """ 
        geoList = self.getGeometryTranform()
        if geoList:
            self.createGeoLyr(geoList, self.geoLayerName)
        else:
            if cmds.objExists(self.geoLayerName):
                cmds.delete(self.geoLayerName)

        self.createCtrlLyr(self.allCtrlsList, self.ctrlLayerName)
        if self.extraLyrToDelete:
            for layer in self.extraLyrToDelete:
                cmds.delete(layer)
        

    def createGeoLyr(self, geoList, geoLayerName, *args):
        """ Creates Geo_Lyr with the objects inside Render_Grp and Proxy_Grp
        """
        if geoList:
            cmds.select(geoList)
            geoLyr = str(cmds.createDisplayLayer (name=geoLayerName, noRecurse=True))
            # Count numbers in name
            numeric = 0
            for n in geoLyr:
                if n.isdigit():
                    numeric +=1
            # If there's numeric in name, delete the first, rename the new one and displayType 2 option
            if numeric > 0:           
                cmds.delete (self.geoLayerName)
                newLyr = cmds.rename (geoLyr, self.geoLayerName)
                cmds.setAttr(newLyr+".displayType", 2)
                cmds.select(clear=True)
            else:
                cmds.setAttr(self.geoLayerName+".displayType", 2)
                cmds.select(clear=True)


    def createCtrlLyr(self, ctrlList, ctrlLayerName, *args):
        """ Creates Ctrl_Lyr with all dpControls
        """
        if ctrlList:
            cmds.select(ctrlList)
            ctrlLyr = str(cmds.createDisplayLayer (name=ctrlLayerName, noRecurse=True))
            # Count numbers in name
            numeric = 0
            for n in ctrlLyr:
                if n.isdigit():
                    numeric +=1
            # If there's numeric in name, delete the first, rename the new one and hide Playblack option
            if numeric > 0:           
                cmds.delete (self.ctrlLayerName)
                newLyr = cmds.rename (ctrlLyr, self.ctrlLayerName)
                cmds.setAttr (newLyr+".hideOnPlayback", 1)
                cmds.select(clear=True)
            else:
                cmds.setAttr (self.ctrlLayerName+".hideOnPlayback", 1)
                cmds.select(clear=True)


    def getGeometryTranform(self, *args):
        """ Get all transform nodes from Render_Grp and Proxy_Grp. If it found nothing it will return an empty list.
        """
        # Get all transform node from Render_Grp
        renderGrp = dpUtils.getNodeByMessage("renderGrp")
        proxyGrp = dpUtils.getNodeByMessage("proxyGrp")
        if renderGrp and proxyGrp:
            renderGrpShapesList = cmds.listRelatives(renderGrp, allDescendents=True, type="mesh")
            proxyGrpShapesList = cmds.listRelatives(proxyGrp, allDescendents=True, type="mesh")
            if proxyGrpShapesList == None:
                proxyGrpShapesList = []
            if renderGrpShapesList == None:
                renderGrpShapesList = []
            allShapesList = list(set(renderGrpShapesList + proxyGrpShapesList))
            if allShapesList:
                renderGrpList = []
                for shape in allShapesList:
                    if not "Orig" in shape:
                        transform = cmds.listRelatives(shape, parent=True)[0]
                        # Get the transform only
                        renderGrpList.append(transform)
            else:
                renderGrpList = []
            return renderGrpList


    def verifyFixMode(self, itemList, *args):
        """ This function will check if the item is a list or not.
            If it's a list it will append the items in the dic and run the main function once.
            If it's not a list it will append the obj and run the main function.
        """
        if isinstance(itemList, list):
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
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item)
                    except:#fix
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item)
        else:    
            if self.verifyMode:#verify
                self.resultOkList.append(False)
                self.checkedObjList.append(itemList)
                self.foundIssueList.append(True)
            else:#fix
                try:
                    self.createDisplayLayers()
                    self.resultOkList.append(True)
                    self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+itemList)
                except:
                    self.resultOkList.append(False)
                    self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+itemList)

                
