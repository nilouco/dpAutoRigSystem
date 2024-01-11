# importing libraries:
from maya import cmds
from maya import mel
from .. import dpBaseActionClass
import os

# global variables to this module:
CLASS_NAME = "ModelIO"
TITLE = "r003_modelIO"
DESCRIPTION = "r004_modelIODesc"
ICON = "/Icons/dp_modelIO.png"

DP_MODELIO_VERSION = 1.0


class ModelIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_MODELIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_modelIO"
        self.startName = "dpModel"
    

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
        # ensure file is saved
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            # load alembic plugin
            if self.utils.checkLoadedPlugin("AbcExport"):
                self.ioPath = self.getIOPath(self.ioDir)
                if self.firstMode: #export
                    meshList = None
                    ioList = []
                    if objList:
                        meshList = cmds.listRelatives(objList, children=True, allDescendents=True, type="mesh")
                    else:
                        meshList = self.getRenderMeshList(True)
                    if meshList:
                        for meshName in meshList:
                            if not "Orig" in meshName:
                                # get transform node
                                parentNode = cmds.listRelatives(meshName, parent=True)[0]
                                if not parentNode in ioList:
                                    ioList.append(parentNode)
                        if ioList:
                            progressAmount = 0
                            maxProcess = len(ioList)
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                            try:
                                # export alembic
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                ioItems = ' -root '.join(ioList)
                                abcName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".abc"
                                cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -dataFormat ogawa -root "+ioItems+" -file "+abcName)
                                self.wellDoneIO(', '.join(ioList))
                            except:
                                self.notWorkedWellIO(', '.join(ioList))
                        else:
                            self.notWorkedWellIO("Render_Grp")
                    else:
                        self.notWorkedWellIO("Render_Grp")
                else: #import
                    exportedList = None
                    if objList:
                        exportedList = objList
                        if not type(objList) == list:
                            exportedList = [objList]
                    else:
                        exportedList = next(os.walk(self.ioPath))[2]
                    if exportedList:
                        try:
                            # import alembic
                            exportedList.sort()
                            abcToImport = self.ioPath+"/"+exportedList[-1]
                            #cmds.AbcImport(jobArg="-mode import \""+abcToImport+"\"")
                            mel.eval("AbcImport -mode import \""+abcToImport+"\";")
                            # clean up geometries
                            self.runCheckInValidators()
                            self.wellDoneIO(exportedList[-1])
                        except:
                            self.notWorkedWellIO(exportedList[-1])
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['e022_notLoadedPlugin']+"AbcExport")
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic


    def runCheckInValidators(self, *args):
        """ Run checkin validators after importing the model.
        """
        validatorToRunList = [
            "dpUnlockNormals",
            "dpSoftenEdges",
            "dpFreezeTransform",
            "dpGeometryHistory"
        ]
        if self.dpUIinst.checkInInstanceList:
            for validatorToRun in validatorToRunList:
                for vInst in self.dpUIinst.checkInInstanceList:
                    if validatorToRun in str(vInst):
                        vInst.verbose = False
                        vInst.runAction(False) #fix
                        vInst.verbose = True
