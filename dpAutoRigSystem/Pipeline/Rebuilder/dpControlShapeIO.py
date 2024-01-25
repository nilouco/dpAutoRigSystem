# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ControlShapeIO"
TITLE = "r014_ctrlShapeIO"
DESCRIPTION = "r015_ctrlShapeIODesc"
ICON = "/Icons/dp_controlShapeIO.png"

MODULES = "Modules"

DP_CONTROLSHAPEIO_VERSION = 1.0


class ControlShapeIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONTROLSHAPEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_controlShapeIO"
        self.startName = "dpControlShape"
    

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
        
        
                    #
                    # WIP
                    #
                    # ref
                    #self.allUIs["rechargeShapeButton"] = cmds.button("rechargeShapeButton", label=self.lang['i204_recharge'], backgroundColor=(1.0, 0.7, 0.7), height=30, command=partial(self.ctrls.importShape, recharge=True), parent=self.allUIs["shapeIO4Layout"])
                    #self.allUIs["publishShapeButton"] = cmds.button("publishShapeButton", label=self.lang['i200_publish'], backgroundColor=(1.0, 0.6, 0.6), height=30, command=partial(self.ctrls.exportShape, publish=True), parent=self.allUIs["shapeIO4Layout"])
                    #
        
        
        # ---
        # --- rebuilder code --- beginning
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    meshList = None
                    if objList:
                        meshList = objList
                    else:
                        meshList = self.getModelToExportList()
                    if meshList:
                        progressAmount = 0
                        maxProcess = len(meshList)
                        if self.verbose:
                            # Update progress window
                            progressAmount += 1
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                        try:
                            # export alembic
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            ioItems = ' -root '.join(meshList)
                            abcName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".abc"
                            cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+" -file "+abcName)
                            self.wellDoneIO(', '.join(meshList))
                        except:
                            self.notWorkedWellIO(', '.join(meshList))
                    else:
                        self.notWorkedWellIO("Render_Grp")
                else: #import
                    exportedList = self.getExportedList()
                    if exportedList:
                        try:
                            # import alembic
                            exportedList.sort()
                            abcToImport = self.ioPath+"/"+exportedList[-1]
                            #cmds.AbcImport(jobArg="-mode import \""+abcToImport+"\"")
                            mel.eval("AbcImport -mode import \""+abcToImport+"\";")
                            # clean up geometries
                            validatorToRunList = ["dpUnlockNormals", "dpSoftenEdges", "dpFreezeTransform", "dpGeometryHistory"]
                            self.runActionsInSilence(validatorToRunList, self.dpUIinst.checkInInstanceList, False) #fix
                            self.wellDoneIO(exportedList[-1])
                        except:
                            self.notWorkedWellIO(exportedList[-1])
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
