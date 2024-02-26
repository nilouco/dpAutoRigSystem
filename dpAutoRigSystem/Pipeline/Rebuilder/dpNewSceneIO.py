# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "NewSceneIO"
TITLE = "r025_newSceneIO"
DESCRIPTION = "r026_newSceneIODesc"
ICON = "/Icons/dp_newSceneIO.png"

DP_NEWSCENEIO_VERSION = 1.0


class NewSceneIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_NEWSCENEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_newSceneIO"
        self.startName = "dpNewScene"
        self.firstBTEnable = False
    

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
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            # load alembic plugin
            if self.utils.checkLoadedPlugin("AbcExport") and self.utils.checkLoadedPlugin("AbcImport"):
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
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+' - '+str(meshList)))
                            try:
                                nodeStateDic = self.changeNodeState(meshList, state=1) #has no effect
                                # export alembic
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                ioItems = ' -root '.join(meshList)
                                abcName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".abc"
                                cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+" -file "+abcName)
                                if nodeStateDic:
                                    self.changeNodeState(meshList, findDeformers=False, dic=nodeStateDic) #back deformer as before
                                self.wellDoneIO(', '.join(meshList))
                            except Exception as e:
                                self.notWorkedWellIO(', '.join(meshList)+": "+str(e))
                        else:
                            self.notWorkedWellIO("Render_Grp")
                    else: #import


                        # WIP

                        self.pipeliner.setAssetData(rebuilding=True)
                        cmds.file(newFile=True, force=True)
                        print(self.pipeliner.pipeData)
                        cmds.file(rename=self.pipeliner.assetData["path"]+"/"+self.pipeliner.assetData["assetName"]+"_Rebuilding"+self.pipeliner.assetData["extension"])
                        #ext = cmds.file(type=True, query=True)[0]
                        #return cmds.file(save=True, type=ext)
                        
                        #cmds.tabLayout(self.dpUIinst.allUIs["mainTabLayout"], edit=True, selectTab=self.dpUIinst.allUIs["rebuilderTabLayout"])


                        #self.pipeliner.setAssetData(rebuilding=False)



                        
                        exportedList = self.getExportedList()
                        if exportedList:
                            try:
                                
                                # start a new asset context clean scene
                                self.startNewScene()

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
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic


    def getModelToExportList(self, *args):
        """ Returns a list of higher father mesh node list or the children nodes in Render_Grp.
        """
        meshList = []
        renderGrp = self.utils.getNodeByMessage("renderGrp")
        if renderGrp:
            meshList = cmds.listRelatives(renderGrp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
            if meshList:
                return cmds.listRelatives(renderGrp, children=True, type="transform")
        if not meshList:
            unparentedMeshList = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh")
            if unparentedMeshList:
                for item in unparentedMeshList:
                    if not cmds.objExists(item+".masterGrp"):
                        fatherNode = item[:item[1:].find("|")+1]
                        if fatherNode:
                            if not cmds.objExists(fatherNode+".masterGrp"):
                                if not fatherNode in meshList:
                                    meshList.append(fatherNode)
                return meshList


    def startNewScene(self, *args):
        """
        """
        print("starting a new Asset context clean scene here.... merci... WIP")