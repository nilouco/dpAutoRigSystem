# importing libraries:
from maya import cmds
from .. import dpBaseActionClass
import os

# global variables to this module:
CLASS_NAME = "SkinningIO"
TITLE = "r016_skinningIO"
DESCRIPTION = "r017_skinningIODesc"
ICON = "/Icons/dp_skinningIO.png"

DP_SKINNINGIO_VERSION = 1.0


class SkinningIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SKINNINGIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_skinningIO"
        self.startName = "dpSkinning"
    

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
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                ioSubFolder = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()
                skinningSubFolder = self.getSubFolder()
                if self.firstMode: #export
                    fatherList = None
                    if objList:
                        fatherList = objList
                    else:
                        fatherList = self.getModelToExportList()
                    if fatherList:
                        meshList = self.getMeshTansformToExportList(fatherList)
                        self.pipeliner.removeFolder(ioSubFolder)
                        self.pipeliner.makeDirIfNotExists(ioSubFolder)
                        wellExported = True
                        progressAmount = 0
                        maxProcess = len(meshList)
                        for mesh in meshList:
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                            try:
                                # export xml files
                                self.dpUIinst.skin.exportSkinWeightsToFile(mesh, ioSubFolder)
                            except:
                                self.notWorkedWellIO(', '.join(meshList))
                                wellExported = False
                                break
                        if wellExported:
                            self.wellDoneIO(', '.join(meshList))
                    else:
                        self.notWorkedWellIO("Render_Grp")
                else: #import
                    if skinningSubFolder:
                        exportedList = self.getExportedList(subFolder=skinningSubFolder)
                        if exportedList:
                            wellImported = True
                            progressAmount = 0
                            maxProcess = len(exportedList)
                            for item in exportedList:
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                                try:
                                    meshName = item[:-4] #filename without extention
                                    if cmds.objExists(meshName):
                                        self.dpUIinst.skin.importSkinWeightsFromFile(item[:-4], self.ioPath+"/"+skinningSubFolder)
                                except Exception as e:
                                    self.notWorkedWellIO(item+": "+str(e))
                                    wellImported = False
                                    break
                            cmds.select(clear=True)
                            if wellImported:
                                self.wellDoneIO(', '.join(exportedList))
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
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
        cmds.refresh()
        return self.dataLogDic


    def getMeshTansformToExportList(self, fatherList, *args):
        """ Returns a list of the transform mesh nodes.
        """
        meshList = []
        for item in fatherList:
            meshShapeList = cmds.listRelatives(item, allDescendents=True, children=True, fullPath=True, noIntermediate=True, type="mesh")
            if meshShapeList:
                for meshShape in meshShapeList:
                    meshTransformList = cmds.listRelatives(meshShape, fullPath=True, parent=True)
                    if meshTransformList:
                        if not (meshTransformList[0]) in meshList:
                            meshList.append(meshTransformList[0])
        return meshList


    def getSubFolder(self, *args):
        """ List and return the latest subfolder by sorted naming or None.
        """
        subFolder = None
        if os.path.exists(self.ioPath):
            subFolderList = next(os.walk(self.ioPath))[1]
            if subFolderList:
                subFolderList.sort()
                subFolder = subFolderList[-1]
        return subFolder
