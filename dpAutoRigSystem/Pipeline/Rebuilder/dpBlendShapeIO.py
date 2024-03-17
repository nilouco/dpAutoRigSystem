# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "BlendShapeIO"
TITLE = "r030_blendShapeIO"
DESCRIPTION = "r031_blendShapeIODesc"
ICON = "/Icons/dp_blendShapeIO.png"

DP_BLENDSHAPEIO_VERSION = 1.0


class BlendShapeIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_BLENDSHAPEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_blendShapeIO"
        self.startName = "dpBlendShape"
        self.targetName = "dpTarget"
        self.originalName = "dpOriginal"
    

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
                self.targetPath = self.ioPath+"/"+self.targetName
                self.originalPath = self.ioPath+"/"+self.originalName
                if self.ioPath:
                    if self.firstMode: #export
                        bsList = None
                        if objList:
                            bsList = objList
                        else:
                            bsList = cmds.ls(selection=False, type="blendShape")
                        if bsList:
                            bsDic = {}
                            progressAmount = 0
                            maxProcess = len(bsList)
                            for bsNode in bsList:
                                bsDic[bsNode] = {}
                                bsDic[bsNode]["targets"] = {}
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+' - '+bsNode))
                                # get blendShape node info
                                bsDic[bsNode]['geometry'] = cmds.blendShape(bsNode, query=True, geometry=True)
                                bsDic[bsNode]['envelope'] = cmds.getAttr(bsNode+".envelope")
                                bsDic[bsNode]['supportNegativeWeights'] = cmds.getAttr(bsNode+".supportNegativeWeights")
                                targetList = cmds.listAttr(bsNode+".weight", multi=True)
                                if targetList:
                                    for t, target in enumerate(targetList):
                                        weightDic = {}
                                        combination = False
                                        combinationMethod = None
                                        combinationList = []
                                        unitConversionFactor = None
                                        unitConversionInputPlug = None
                                        plug = cmds.listConnections(bsNode+"."+target, destination=False, source=True, plugs=True)
                                        if plug:
                                            plugNode = plug[0][:plug[0].find(".")]
                                            if cmds.objectType(plugNode) == "combinationShape":
                                                combination = True
                                                combinationMethod = cmds.getAttr(plugNode+".combinationMethod")
                                                inputWeightList = cmds.listAttr(plugNode+".inputWeight", multi=True)
                                                if inputWeightList:
                                                    for inputWeight in inputWeightList:
                                                        combinationList.append(cmds.listConnections(plugNode+"."+inputWeight, destination=False, source=True, plugs=True)[0])
                                            elif cmds.objectType(plugNode) == "unitConversion":
                                                unitConversionFactor = cmds.getAttr(plugNode+".conversionFactor")
                                                unitConversionInputPlug = cmds.listConnections(plugNode+".input", destination=False, source=True, plugs=True)[0]
                                        # getting vertex weights if not equal to 1
                                        for s, shapeNode in enumerate(bsDic[bsNode]['geometry']):
                                            vertices = cmds.polyEvaluate(shapeNode, vertex=True)
                                            rawWeightList = cmds.getAttr("{}.inputTarget[{}].inputTargetGroup[{}].targetWeights[0:{}]".format(bsNode, s, t, vertices-1))
                                            if not len(rawWeightList) == rawWeightList.count(1.0):
                                                for w, weight in enumerate(rawWeightList):
                                                    if not weight == 1.0:
                                                        weightDic[w] = weight
                                        # data dictionary to export
                                        bsDic[bsNode]["targets"][t] = { "name"           : target,
                                                                        "exists"         : cmds.objExists(target),
                                                                        "value"          : cmds.getAttr(bsNode+"."+target),
                                                                        "plug"           : plug,
                                                                        "comb"           : combination,
                                                                        "combMethod"     : combinationMethod,
                                                                        "combList"       : combinationList,
                                                                        "unitConvFactor" : unitConversionFactor,
                                                                        "unitConvInput"  : unitConversionInputPlug,
                                                                        "weightDic"     : weightDic
                                                                        }
                                try:
                                    self.pipeliner.makeDirIfNotExists(self.targetPath)
                                    self.pipeliner.makeDirIfNotExists(self.originalPath)
                                    # export blendShape targets as compiled maya file
                                    cmds.blendShape(bsNode, edit=True, export=self.targetPath+"/"+self.targetName+"_"+bsNode+".bs")
                                    # export original mesh transform as alembic file
                                    transformList = []
                                    for geoShape in bsDic[bsNode]["geometry"]:
                                        transformList.append(cmds.listRelatives(geoShape, parent=True, type="transform")[0])
                                    nodeStateDic = self.changeNodeState(transformList, state=1) #has no effect
                                    ioItems = ' -root '.join(transformList)
                                    abcName = self.originalPath+"/"+self.originalName+"_"+bsNode+".abc"
                                    cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+" -file "+abcName)
                                    if nodeStateDic:
                                        self.changeNodeState(bsDic[bsNode]["geometry"], findDeformers=False, dic=nodeStateDic) #back deformer as before
                                except Exception as e:
                                    self.notWorkedWellIO(str(e))
                            try:
                                # export json file
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                                self.pipeliner.saveJsonFile(bsDic, jsonName)
                                self.wellDoneIO(jsonName)
                            except Exception as e:
                                self.notWorkedWellIO(jsonName+": "+str(e))
                        else:
                            self.notWorkedWellIO("BlendShape_Grp")



                    else: #import

                        # WIP
                        #cmds.setAttr('blendShape.it[0].itg[0].tw[0:%d]' % (len(weights) - 1), *weights)


                        try:
                            exportedList = self.getExportedList()
                            if exportedList:
                                exportedList.sort()
                                bsDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if bsDic:
                                    mayaVersion = cmds.about(version=True)
                                    notFoundMeshList = []
                                    # rebuild shaders
                                    for item in bsDic.keys():
                                        if not cmds.objExists(item):
                                            bsNode = cmds.shadingNode(bsDic[item]['material'], asShader=True, name=item)
                                            if bsDic[item]['fileNode']:
                                                fileNode = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name=bsDic[item]['fileNode'])
                                                cmds.connectAttr(fileNode+".outColor", bsNode+"."+bsDic[item]['colorAttr'], force=True)
                                                cmds.setAttr(fileNode+".fileTextureName", bsDic[item]['texture'], type="string")
                                            else:
                                                colorList = bsDic[item]['color']
                                                cmds.setAttr(bsNode+"."+bsDic[item]['colorAttr'], colorList[0], colorList[1], colorList[2], type="double3")
                                            transparencyList = bsDic[item]['transparency']
                                            cmds.setAttr(bsNode+"."+bsDic[item]['transparencyAttr'], transparencyList[0], transparencyList[1], transparencyList[2], type="double3")
                                            if bsDic[item]['specularColor']:
                                                specularColorList = bsDic[item]['specularColor']
                                                cmds.setAttr(bsNode+".specularColor", specularColorList[0], specularColorList[1], specularColorList[2], type="double3")
                                            if bsDic[item]['cosinePower']:
                                                cmds.setAttr(bsNode+".cosinePower", bsDic[item]['cosinePower'])
                                        # apply bsNode to meshes
                                        for mesh in bsDic[item]['assigned']:
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
                self.notWorkedWellIO(self.dpUIinst.lang['e022_notLoadedPlugin']+"AbcExport")
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
