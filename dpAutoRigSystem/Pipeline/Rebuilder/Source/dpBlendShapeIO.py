# importing libraries:
from maya import cmds
from maya import mel
from ... import dpBaseActionClass

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
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_blendShapeIO"
        self.startName = "dpBlendShape"
        self.targetName = "dpTarget"
        self.originalName = "dpOriginal"
        self.extention = "shp"
    

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
                            self.utils.setProgress(max=len(bsList))
                            for bsNode in bsList:
                                self.utils.setProgress(self.dpUIinst.lang[self.title]+": "+bsNode)
                                bsDic[bsNode] = {}
                                bsDic[bsNode]["targets"] = {}
                                # get blendShape node info
                                bsDic[bsNode]['geometry'] = cmds.blendShape(bsNode, query=True, geometry=True)
                                bsDic[bsNode]['envelope'] = cmds.getAttr(bsNode+".envelope")
                                bsDic[bsNode]['supportNegativeWeights'] = cmds.getAttr(bsNode+".supportNegativeWeights")
                                targetList = cmds.listAttr("{}.weight".format(bsNode), multi=True)
                                if targetList:
                                    # prepare index to deleted targets
                                    indexList = cmds.getAttr("{}.weight".format(bsNode), multiIndices=True)
                                    bsDic[bsNode]["indexTargetDic"] = dict(zip(indexList, targetList))
                                    deletedIndexList = []
                                    i = 0 #workaround to avoid deleted target index when importing data
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
                                        for s, shapeNode in enumerate(bsDic[bsNode]["geometry"]):
                                            # write deleted target to compose a clear target list to avoid Maya's garbage issue
                                            while not i == indexList[t]:
                                                bsDic[bsNode]["targets"][i] = {"deleted" : True}
                                                deletedIndexList.append(i)
                                                i += 1
                                            # continue writing relevant or just info data
                                            vertices = cmds.polyEvaluate(shapeNode, vertex=True)
                                            rawWeightList = cmds.getAttr("{}.inputTarget[{}].inputTargetGroup[{}].targetWeights[0:{}]".format(bsNode, s, t, vertices-1))
                                            if not len(rawWeightList) == rawWeightList.count(1.0):
                                                for w, weight in enumerate(rawWeightList):
                                                    if not weight == 1.0:
                                                        weightDic[w] = weight
                                        # data dictionary to export
                                        bsDic[bsNode]["targets"][i] = { "name"           : target,
                                                                        "deleted"        : False,
                                                                        "regenerate"     : cmds.objExists(target),
                                                                        "value"          : cmds.getAttr(bsNode+"."+target),
                                                                        "plug"           : plug,
                                                                        "comb"           : combination,
                                                                        "combMethod"     : combinationMethod,
                                                                        "combList"       : combinationList,
                                                                        "unitConvFactor" : unitConversionFactor,
                                                                        "unitConvInput"  : unitConversionInputPlug,
                                                                        "weightDic"      : weightDic
                                                                        }
                                        bsDic[bsNode]["deletedIndexList"] = deletedIndexList
                                        i += 1
                                try:
                                    self.pipeliner.makeDirIfNotExists(self.targetPath)
                                    self.pipeliner.makeDirIfNotExists(self.originalPath)
                                    # export blendShape targets as compiled maya file
                                    cmds.blendShape(bsNode, edit=True, export=self.targetPath+"/"+self.targetName+"_"+bsNode+"."+self.extention)
                                    # export original mesh transform as alembic file
                                    transformList = []
                                    for geoShape in bsDic[bsNode]["geometry"]:
                                        transformList.append(cmds.listRelatives(geoShape, parent=True, type="transform")[0])
                                    nodeStateDic = self.changeNodeState(transformList, state=1) #has no effect
                                    ioItems = " -root ".join(transformList)
                                    abcName = self.originalPath+"/"+self.originalName+"_"+bsNode+".abc"
                                    cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+" -file "+abcName)
                                    if nodeStateDic:
                                        self.changeNodeState(bsDic[bsNode]["geometry"], findDeformers=False, dic=nodeStateDic) #back deformer as before
                                except Exception as e:
                                    self.notWorkedWellIO(str(e))
                            try:
                                # export json file
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData["currentFileName"]+".json"
                                self.pipeliner.saveJsonFile(bsDic, jsonName)
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
                                bsDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if bsDic:
                                    # not working scriptEditor suppress command...
                                    suppressWarningsState = cmds.scriptEditorInfo(query=True, suppressWarnings=True)
                                    suppressInfoState = cmds.scriptEditorInfo(query=True, suppressInfo=True)
                                    suppressErrorsState = cmds.scriptEditorInfo(query=True, suppressErrors=True)
                                    suppressResultsState = cmds.scriptEditorInfo(query=True, suppressResults=True)
                                    cmds.scriptEditorInfo(suppressWarnings=True, suppressInfo=True, suppressErrors=True, suppressResults=True)
                                    # rebuild blendShapes
                                    for bsNode in bsDic.keys():
                                        # import alembic original mesh if it doesn't exists
                                        originalShapeList = bsDic[bsNode]["geometry"]
                                        for originalShape in originalShapeList:
                                            if not cmds.objExists(originalShape):
                                                try:
                                                    abcToImport = self.originalPath+"/"+self.originalName+"_"+bsNode+".abc"
                                                    mel.eval("AbcImport -mode import \""+abcToImport+"\";")
                                                except:
                                                    self.notWorkedWellIO(self.dpUIinst.lang["r032_notImportedData"]+": "+self.originalName+"_"+bsNode+".abc")
                                        if not cmds.objExists(bsNode):
                                            # create an empty blendShape node
                                            cmds.blendShape(originalShapeList, name=bsNode)
                                            cmds.setAttr(bsNode+".envelope", bsDic[bsNode]["envelope"])
                                            cmds.setAttr(bsNode+".supportNegativeWeights", bsDic[bsNode]["supportNegativeWeights"])
                                            # import targets
                                            try:
                                                # OMG!
                                                print("--------------------------------\nStarting Autodesk not suppressed messages, sorry!\n--------------------------------\n")
                                                cmds.blendShape(bsNode, edit=True, ip=self.targetPath+"/"+self.targetName+"_"+bsNode+"."+self.extention)
                                                #mel.eval('catchQuiet(`blendShape -edit -ip "'+self.targetPath+'/'+self.targetName+'_'+bsNode+'.'+self.extention+'" '+bsNode+'`);')
                                                print("--------------------------------\nEnding Autodesk not suppressed messages, sorry!\n--------------------------------\n")
                                            except Exception as e:
                                                self.notWorkedWellIO(self.dpUIinst.lang["r032_notImportedData"]+": "+self.targetName+"_"+bsNode+"."+self.extention+" - "+str(e))
                                        for i in list(bsDic[bsNode]["indexTargetDic"].keys()):
                                            target = bsDic[bsNode]["indexTargetDic"][i]
                                            # set target value
                                            try:
                                                cmds.setAttr(bsNode+"."+target, bsDic[bsNode]["targets"][i]["value"])
                                            except:
                                                pass #connected combination target
                                            # set target weights
                                            for s, shapeNode in enumerate(bsDic[bsNode]["geometry"]):
                                                for idx in list(bsDic[bsNode]["targets"][i]["weightDic"].keys()):
                                                    cmds.setAttr("{}.inputTarget[{}].inputTargetGroup[{}].targetWeights[{}]".format(bsNode, s, i, idx), bsDic[bsNode]["targets"][i]["weightDic"][idx])
                                            # regenerate target
                                            if bsDic[bsNode]["targets"][i]["regenerate"]:
                                                tgtAlreadyExists = cmds.objExists(target)
                                                tgt = cmds.sculptTarget(bsNode, edit=True, regenerate=True, target=int(i))[0]
                                                if tgtAlreadyExists:
                                                    tgt = cmds.rename("|"+tgt, "dpTemp_"+tgt)
                                                    plugOut = cmds.listConnections(cmds.listRelatives(tgt, children=True, type="mesh")[0]+".worldMesh[0]", destination=True, source=False, plugs=True)[0]
                                                    cmds.connectAttr(cmds.listRelatives(target, children=True, type="mesh")[0]+".worldMesh[0]", plugOut, force=True)
                                                    cmds.delete(tgt)
                                                else:
                                                    cmds.rename(cmds.listRelatives(tgt, children=True, type="mesh")[0], bsDic[bsNode]["targets"][i]["name"]+"Shape")

                                            # TODO
                                                # fix double original mesh / import double targets by group issue = Maya 2024 bug, supposed fixed on Maya 2025
                                                # remove script editor messages from import targets

                                        for d in bsDic[bsNode]["deletedIndexList"]:
                                            cmds.removeMultiInstance("{}.weight[{}]".format(bsNode, d), b=True) #doing nothing... I don't know why, sorry. Maya2024.2 at 2024-03-24
                                    cmds.scriptEditorInfo(suppressWarnings=suppressWarningsState, suppressInfo=suppressInfoState, suppressErrors=suppressErrorsState, suppressResults=suppressResultsState)
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
        self.endProgress()
        self.refreshView()
        return self.dataLogDic
