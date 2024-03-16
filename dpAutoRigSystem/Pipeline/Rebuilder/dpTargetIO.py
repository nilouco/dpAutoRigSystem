# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "TargetIO"
TITLE = "r030_targetIO"
DESCRIPTION = "r031_targetIODesc"
ICON = "/Icons/dp_targetIO.png"

DP_TARGETIO_VERSION = 1.0


class TargetIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_TARGETIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_targetIO"
        self.startName = "dpTarget"
    

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
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    bsList = None
                    if objList:
                        bsList = objList
                    else:
                        bsList = cmds.ls(selection=False, type="blendShape")
                    if bsList:
                        targetDic = {}
                        progressAmount = 0
                        maxProcess = len(bsList)
                        for bsNode in bsList:
                            targetDic[bsNode] = {}
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+' - '+bsNode))
                            targetList = cmds.listAttr(bsNode+".weight", multi=True)
                            if targetList:
                                for target in targetList:
                                    combination = False
                                    combinationList = []
                                    plug = cmds.listConnections(bsNode+"."+target, destination=False, source=True, plugs=True)
                                    if plug:
                                        if ".outputWeight" in plug[0]:
                                            combinationShapeNode = plug[0][:plug[0].find(".outputWeight")]
                                            combination = True
                                            inputWeightList = cmds.listAttr(combinationShapeNode+".inputWeight", multi=True)
                                            if inputWeightList:
                                                for inputWeight in inputWeightList:
                                                    combinationList.append(cmds.listConnections(combinationShapeNode+".inputWeight", destination=False, source=True, plugs=True)[0])

                                    # data dictionary to export
                                    targetDic[bsNode][target] = {"exists" : cmds.objExists(target),
                                                                "weight" : cmds.getAttr(bsNode+"."+target),
                                                                "plug"   : plug,
                                                                "combination" : combination,
                                                                "combinationList" : combinationList
                                                                }




                            cmds.select(clear=True)
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                            self.pipeliner.saveJsonFile(targetDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except Exception as e:
                            self.notWorkedWellIO(jsonName+": "+str(e))
                    else:
                        self.notWorkedWellIO("BlendShape_Grp")



                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            targetDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if targetDic:
                                mayaVersion = cmds.about(version=True)
                                notFoundMeshList = []
                                # rebuild shaders
                                for item in targetDic.keys():
                                    if not cmds.objExists(item):
                                        bsNode = cmds.shadingNode(targetDic[item]['material'], asShader=True, name=item)
                                        if targetDic[item]['fileNode']:
                                            fileNode = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name=targetDic[item]['fileNode'])
                                            cmds.connectAttr(fileNode+".outColor", bsNode+"."+targetDic[item]['colorAttr'], force=True)
                                            cmds.setAttr(fileNode+".fileTextureName", targetDic[item]['texture'], type="string")
                                        else:
                                            colorList = targetDic[item]['color']
                                            cmds.setAttr(bsNode+"."+targetDic[item]['colorAttr'], colorList[0], colorList[1], colorList[2], type="double3")
                                        transparencyList = targetDic[item]['transparency']
                                        cmds.setAttr(bsNode+"."+targetDic[item]['transparencyAttr'], transparencyList[0], transparencyList[1], transparencyList[2], type="double3")
                                        if targetDic[item]['specularColor']:
                                            specularColorList = targetDic[item]['specularColor']
                                            cmds.setAttr(bsNode+".specularColor", specularColorList[0], specularColorList[1], specularColorList[2], type="double3")
                                        if targetDic[item]['cosinePower']:
                                            cmds.setAttr(bsNode+".cosinePower", targetDic[item]['cosinePower'])
                                    # apply bsNode to meshes
                                    for mesh in targetDic[item]['assigned']:
                                        if cmds.objExists(mesh):
                                            if mayaVersion >= "2024":
                                                cmds.hyperShade(assign=item, geometries=mesh)
                                            else:
                                                cmds.select(mesh)
                                                cmds.hyperShade(assign=item)
                                        else:
                                            notFoundMeshList.append(mesh)
                                cmds.select(clear=True)
                                if notFoundMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r011_notFoundMesh']+", ".join(notFoundMeshList))
                                else:
                                    self.wellDoneIO(exportedList[-1])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    except Exception as e:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic
