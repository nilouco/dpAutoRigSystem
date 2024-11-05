# importing libraries:
from maya import cmds
from maya import mel
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "SetupGeometryIO"
TITLE = "r023_setupGeometryIO"
DESCRIPTION = "r024_setupGeometryIODesc"
ICON = "/Icons/dp_setupGeometryIO.png"

DP_SETUPGEOMETRYIO_VERSION = 1.0


class SetupGeometryIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SETUPGEOMETRYIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_setupGeometryIO"
        self.startName = "dpSetupGeometry"
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
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
        # --- rebuilder code --- beginning
        if self.pipeliner.checkAssetContext():
            # load alembic plugin
            if self.utils.checkLoadedPlugin("AbcExport") and self.utils.checkLoadedPlugin("AbcImport"):
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    if self.firstMode: #export
                        meshList = None
                        if objList:
                            meshList = objList
                        else:
                            meshList = self.getGeometryToExportList()
                        if meshList:
                            progressAmount = 0
                            maxProcess = len(meshList)
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+' - '+str(meshList)))
                            try:
                                nodeStateDic = self.changeNodeState(meshList, state=1) #has no effect
                                # export alembic
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                ioItems = ' -root '.join(meshList)
                                abcName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".abc"
                                cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+" -file "+abcName)
                                if nodeStateDic:
                                    self.changeNodeState(meshList, findDeformers=False, dic=nodeStateDic) #back deformer as before
                                self.wellDoneIO(', '.join(meshList))
                            except Exception as e:
                                self.notWorkedWellIO(', '.join(meshList)+": "+str(e))
                        else:
                            self.notWorkedWellIO("Geometries")
                    else: #import
                        exportedList = self.getExportedList()
                        if exportedList:
                            try:
                                # import alembic
                                exportedList.sort()
                                abcToImport = self.ioPath+"/"+exportedList[-1]
                                #cmds.AbcImport(jobArg="-mode import \""+abcToImport+"\"")
                                mel.eval("AbcImport -mode import \""+abcToImport+"\";")
                                self.wellDoneIO(exportedList[-1])
                            except Exception as e:
                                self.notWorkedWellIO(exportedList[-1]+": "+str(e))
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['e022_notLoadedPlugin']+"AbcExport")
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getGeometryToExportList(self, *args):
        """ Returns a list of the first children node in geometry groups.
        """
        geoList = []
        geoGrpList = ["modelsGrp", "blendShapesGrp", "wipGrp"]
        for geoGrp in geoGrpList:
            grp = self.utils.getNodeByMessage(geoGrp)
            if grp:
                meshList = cmds.listRelatives(grp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
                if meshList:
                    geoList.extend(cmds.listRelatives(grp, children=True, type="transform"))
        return geoList
