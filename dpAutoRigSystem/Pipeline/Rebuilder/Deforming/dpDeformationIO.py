# importing libraries:
from maya import cmds
from maya import mel
from ... import dpBaseActionClass
from .... Deforms import dpWeights

# global variables to this module:
CLASS_NAME = "DeformationIO"
TITLE = "r033_deformationIO"
DESCRIPTION = "r034_deformationIODesc"
ICON = "/Icons/dp_deformationIO.png"

DP_DEFORMATIONIO_VERSION = 1.0


class DeformationIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DEFORMATIONIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_deformationIO"
        self.startName = "dpDeformation"
        self.defWeights = dpWeights.Weights(self.dpUIinst)
    

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
                    meshList = None
                    if objList:
                        meshList = objList
                    else:
                        meshList = cmds.listRelatives(cmds.ls(selection=False, type="mesh"), parent=True)
                    if meshList:
                        # finding deformers
                        hasDef = False
                        inputDeformerList = cmds.listHistory(meshList, pruneDagObjects=False, interestLevel=True)
                        for deformerType in self.defWeights.typeAttrDic.keys():
                            if cmds.ls(inputDeformerList, type=deformerType):
                                hasDef = True
                                break
                        if hasDef:
                            # Declaring the data dictionary to export it
                            self.deformerDataDic = {}
                            progressAmount = 0
                            maxProcess = len(self.defWeights.typeAttrDic.keys())
                            # run for all deformer types to get info
                            for deformerType in self.defWeights.typeAttrDic.keys():
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                                deformerList = cmds.ls(selection=False, type=deformerType)
                                if deformerList:
                                    for deformerNode in deformerList:
                                        if deformerNode in inputDeformerList:
                                            # get the attributes and values for this deformer node
                                            self.deformerDataDic[deformerNode] = self.defWeights.getDeformerInfo(deformerNode)
                                            # Get shape indexes for the deformer so we can query the deformer weights
                                            shapeList, indexList, shapeToIndexDic = self.defWeights.getShapeToIndexData(deformerNode)
                                            # update dictionary
                                            self.deformerDataDic[deformerNode]["shapeList"] = shapeList
                                            self.deformerDataDic[deformerNode]["indexList"] = indexList
                                            self.deformerDataDic[deformerNode]["shapeToIndexDic"] = shapeToIndexDic
                                            self.deformerDataDic[deformerNode]["weights"] = {}
                                            for shape in shapeList:
                                                # Get weights
                                                index = shapeToIndexDic[shape]
                                                weights = self.defWeights.getDeformerWeights(deformerNode, index)
                                                if self.deformerDataDic[deformerNode]["relatedNode"]: 
                                                    if not deformerType == "ffd":
                                                        # nonLinear because other don't have weights (wrap, shrinkWrap and wire)
                                                        weights = self.defWeights.getDeformerWeights(self.deformerDataDic[deformerNode]["relatedNode"], index)
                                                self.deformerDataDic[deformerNode]["weights"][index] = weights
                                            # componentTag
                                            self.deformerDataDic[deformerNode]["componentTag"] = self.defWeights.checkUseComponentTag(deformerNode)
                            try:
                                # export deformer data
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                                self.pipeliner.saveJsonFile(self.deformerDataDic, jsonName)
                                self.wellDoneIO(jsonName)
                            except Exception as e:
                                self.notWorkedWellIO(', '.join(meshList)+": "+str(e))
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" deformers")
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" mesh")
                else: #import
                    self.exportedList = self.getExportedList()
                    if self.exportedList:
                        self.exportedList.sort()
                        self.deformerDataDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                        if self.deformerDataDic:
                            wellImported = True
                            toImportList, notFoundMeshList, changedShapeMeshList = [], [], []
                            for deformerNode in self.deformerDataDic.keys():
                                # check mesh existing
                                for shapeNode in self.deformerDataDic[deformerNode]["shapeList"]:
                                    if cmds.objExists(shapeNode):
                                        if not deformerNode in toImportList:
                                            toImportList.append(deformerNode)
                                    else:
                                        notFoundMeshList.append(deformerNode)
                            if toImportList:
                                progressAmount = 0
                                maxProcess = len(toImportList)
                                for deformerNode in toImportList:
                                    if self.verbose:
                                        # Update progress window
                                        progressAmount += 1
                                        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                                    try:
                                        wellImported = self.importDeformation(deformerNode, wellImported)
                                    except Exception as e:
                                        self.notWorkedWellIO(self.exportedList[-1]+": "+deformerNode+" - "+str(e))
                                if notFoundMeshList: #call again the same instruction to try create a deformer in a deformer, like a cluster in a lattice.
                                    for deformerNode in notFoundMeshList:
                                        for shapeNode in self.deformerDataDic[deformerNode]["shapeList"]:
                                            if cmds.objExists(shapeNode):
                                                try:
                                                    wellImported = self.importDeformation(deformerNode, wellImported)
                                                except Exception as e:
                                                    self.notWorkedWellIO(self.exportedList[-1]+": "+deformerNode+" - "+str(e))
                                if wellImported:
                                    self.wellDoneIO(', '.join(toImportList))
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(self.deformerDataDic.keys())))
                            if not wellImported:
                                if changedShapeMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" shape "+str(', '.join(changedShapeMeshList)))
                                elif notFoundMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        cmds.select(clear=True)
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic


    def importDeformation(self, deformerNode, wellImported, *args):
        """ Import deformer data creating a new deformer node, set values and weights.
        """
        newDefNode = None
        # verify if the deformer node exists to don't recreate it and import data
        if cmds.objExists(deformerNode):
            newDefNode = deformerNode
            self.defWeights.assignDeformer(deformerNode, self.deformerDataDic[deformerNode]["shapeList"])
        else:
            # create a new deformer if it doesn't exists
            if self.deformerDataDic[deformerNode]["type"] == "cluster":
                newDefNode = cmds.cluster(self.deformerDataDic[deformerNode]["shapeList"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"])[0] #[cluster, handle]
            elif self.deformerDataDic[deformerNode]["type"] == "deltaMush":
                newDefNode = cmds.deltaMush(self.deformerDataDic[deformerNode]["shapeList"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"])[0] #[deltaMush]
            elif self.deformerDataDic[deformerNode]["type"] == "tension":
                newDefNode = cmds.tension(self.deformerDataDic[deformerNode]["shapeList"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"])[0] #[tension]
            elif self.deformerDataDic[deformerNode]["type"] == "ffd":
                latticeList = cmds.lattice(self.deformerDataDic[deformerNode]["shapeList"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"]) #[set, ffd, base] 
                newDefNode = latticeList[0]
                self.defWeights.setLatticePoints(latticeList[1], self.deformerDataDic[deformerNode]["relatedData"]["pointList"])
                cmds.rename(latticeList[1], self.deformerDataDic[deformerNode]["relatedNode"])
                cmds.rename(latticeList[2], self.deformerDataDic[deformerNode]["relatedData"]["baseLatticeMatrix"])
            elif self.deformerDataDic[deformerNode]["type"] == "sculpt":
                sculptList = cmds.sculpt(self.deformerDataDic[deformerNode]["shapeList"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"]) #[sculpt, sculptor, orig]
                newDefNode = sculptList[0]
                cmds.rename(sculptList[1], self.deformerDataDic[deformerNode]["relatedData"]["sculptor"])
                cmds.rename(sculptList[2], self.deformerDataDic[deformerNode]["relatedData"]["originLocator"])
            elif self.deformerDataDic[deformerNode]["type"] == "wrap":
                if cmds.objExists(self.deformerDataDic[deformerNode]["relatedNode"]):
                    cmds.select(self.deformerDataDic[deformerNode]["shapeList"], self.deformerDataDic[deformerNode]["relatedNode"])
                    mel.eval("CreateWrap;")
                    hist = cmds.listHistory(self.deformerDataDic[deformerNode]["shapeList"])
                    wrapList = cmds.ls(hist, type="wrap")[0]
                    newDefNode = cmds.rename(wrapList, self.deformerDataDic[deformerNode]["name"])
            elif self.deformerDataDic[deformerNode]["type"] == "shrinkWrap":
                newDefNode = cmds.deformer(self.deformerDataDic[deformerNode]["shapeList"], type=self.deformerDataDic[deformerNode]["type"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"])[0] #shrinkWrap
                for cAttr in ["continuity", "smoothUVs", "keepBorder", "boundaryRule", "keepHardEdge", "propagateEdgeHardness", "keepMapBorders"]:
                    cmds.connectAttr(self.deformerDataDic[deformerNode]["relatedNode"]+"."+cAttr, newDefNode+"."+cAttr, force=True)
                cmds.connectAttr(self.deformerDataDic[deformerNode]["relatedNode"]+".worldMesh", newDefNode+".targetGeom", force=True)
            elif self.deformerDataDic[deformerNode]["type"] == "wire":
                if not cmds.objExists(self.deformerDataDic[deformerNode]["relatedNode"]):
                    isPeriodic = False
                    if self.deformerDataDic[deformerNode]["relatedData"]["form"] == 2:
                        isPeriodic = True
                    cmds.curve(name=self.deformerDataDic[deformerNode]["relatedNode"], periodic=isPeriodic, point=self.deformerDataDic[deformerNode]["relatedData"]["point"], degree=self.deformerDataDic[deformerNode]["relatedData"]["degree"], knot=self.deformerDataDic[deformerNode]["relatedData"]["knot"])
                newDefNode = cmds.wire(self.deformerDataDic[deformerNode]["shapeList"], wire=self.deformerDataDic[deformerNode]["relatedNode"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"])[0] #wire
            elif self.deformerDataDic[deformerNode]["nonLinear"]:
                nonLinearList = cmds.nonLinear(self.deformerDataDic[deformerNode]["shapeList"], type=self.deformerDataDic[deformerNode]["nonLinear"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"]) #[def, handle] bend, flare, sine, squash, twist, wave
                newDefNode = nonLinearList[0]
                cmds.rename(nonLinearList[1], self.deformerDataDic[deformerNode]["relatedData"])
            else: #solidify, proximityWrap, morph, textureDeformer, jiggle
                newDefNode = cmds.deformer(self.deformerDataDic[deformerNode]["shapeList"], type=self.deformerDataDic[deformerNode]["type"], name=self.deformerDataDic[deformerNode]["name"], useComponentTags=self.deformerDataDic[deformerNode]["componentTag"])[0]
            if self.deformerDataDic[deformerNode]["type"] == "morph":
                if cmds.objExists(self.deformerDataDic[deformerNode]["relatedNode"]):
                    cmds.connectAttr(self.deformerDataDic[deformerNode]["relatedNode"]+".worldMesh[0]", newDefNode+".morphTarget[0]", force=True)
                else:
                    wellImported = False
                    self.notWorkedWellIO(self.exportedList[-1]+": "+deformerNode+" - "+self.deformerDataDic[deformerNode]["relatedNode"])
        # import attribute values
        if newDefNode:
            for attr in self.deformerDataDic[deformerNode]["attributes"].keys():
                try:
                    cmds.setAttr(newDefNode+"."+attr, self.deformerDataDic[deformerNode]["attributes"][attr])
                except:
                    pass #just to avoid try set connected attributes like envelope or curvature.
        # import deformer weights, except for skinCluster, blendShape, sculpt, wrap
        weightsDic = self.deformerDataDic[deformerNode]["weights"]
        if weightsDic:
            for index in self.deformerDataDic[deformerNode]["indexList"]:
                currentIndex = self.defWeights.getCurrentDeformedIndex(deformerNode, self.deformerDataDic[deformerNode]["shapeToIndexDic"], index)
                if weightsDic[str(index)]:
                    # cluster, deltaMush, tension, ffd, shrinkWrap, wire, nonLinear, solidify, proximityWrap, textureDeformer, jiggle
                    self.defWeights.setDeformerWeights(self.deformerDataDic[deformerNode]["name"], weightsDic[str(index)], currentIndex)
        return wellImported
