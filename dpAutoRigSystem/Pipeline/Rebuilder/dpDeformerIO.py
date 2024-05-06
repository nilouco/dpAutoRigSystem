# importing libraries:
from maya import cmds
from maya import mel
from .. import dpBaseActionClass
from ...Deforms import dpWeights
import os





from importlib import reload
reload(dpWeights)







# global variables to this module:
CLASS_NAME = "DeformerIO"
TITLE = "r033_deformerIO"
DESCRIPTION = "r034_deformerIODesc"
ICON = "/Icons/dp_deformerIO.png"

DP_DEFORMERIO_VERSION = 1.0


class DeformerIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DEFORMERIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_deformerIO"
        self.startName = "dpDeformer"
        self.importRefName = "dpDeformerIO_Import"
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
                            deformerDataDic = {}
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
                                            deformerDataDic[deformerNode] = self.defWeights.getDeformerInfo(deformerNode)
                                            # Get shape indexes for the deformer so we can query the deformer weights
                                            shapeList = cmds.ls(cmds.deformer(deformerNode, query=True, geometry=True), long=True)
                                            indexList = cmds.deformer(deformerNode, query=True, geometryIndices=True)
                                            shapeToIndexDic = dict(zip(shapeList, indexList))
                                            # update dictionary
                                            deformerDataDic[deformerNode]["shapeList"] = shapeList
                                            deformerDataDic[deformerNode]["indexList"] = indexList
                                            deformerDataDic[deformerNode]["shapeToIndexDic"] = shapeToIndexDic
                                            deformerDataDic[deformerNode]["weights"] = {}
                                            for shape in shapeList:
                                                # Get weights
                                                index = shapeToIndexDic[shape]
                                                weights = self.defWeights.getDeformerWeights(deformerNode, index)
                                                if deformerDataDic[deformerNode]["relatedNode"]: 
                                                    if not deformerType == "ffd":
                                                        # nonLinear because other don't have weights (wrap, shrinkWrap and wire)
                                                        weights = self.defWeights.getDeformerWeights(deformerDataDic[deformerNode]["relatedNode"], index)
                                                deformerDataDic[deformerNode]["weights"][index] = weights
                            try:
                                # export deformer data
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                                self.pipeliner.saveJsonFile(deformerDataDic, jsonName)
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
                        deformerDataDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                        if deformerDataDic:
                            wellImported = True
                            toImportList, notFoundMeshList, changedShapeMeshList = [], [], []
                            for deformerNode in deformerDataDic.keys():
                                # verify if the deformer node exists to recreate it and import data
                                if not cmds.objExists(deformerNode):
                                    # check mesh existing
                                    for shapeNode in deformerDataDic[deformerNode]["shapeList"]:
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
                                        newDefNode = None

                                        # create a new deformer if it doesn't exists
                                        if deformerDataDic[deformerNode]["type"] == "cluster":
                                            newDefNode = cmds.cluster(deformerDataDic[deformerNode]["shapeList"], name=deformerDataDic[deformerNode]["name"])[0] #[cluster, handle]
                                        elif deformerDataDic[deformerNode]["type"] == "deltaMush":
                                            newDefNode = cmds.deltaMush(deformerDataDic[deformerNode]["shapeList"], name=deformerDataDic[deformerNode]["name"])[0] #[deltaMush]
                                        elif deformerDataDic[deformerNode]["type"] == "tension":
                                            newDefNode = cmds.tension(deformerDataDic[deformerNode]["shapeList"], name=deformerDataDic[deformerNode]["name"])[0] #[tension]
                                        elif deformerDataDic[deformerNode]["type"] == "ffd":
                                            latticeList = cmds.lattice(deformerDataDic[deformerNode]["shapeList"], name=deformerDataDic[deformerNode]["name"]) #[set, ffd, base] 
                                            newDefNode = latticeList[0]
                                            self.defWeights.setLatticePoints(latticeList[1], deformerDataDic[deformerNode]["relatedData"]["pointList"])
                                            cmds.rename(latticeList[1], deformerDataDic[deformerNode]["relatedNode"])
                                            cmds.rename(latticeList[2], deformerDataDic[deformerNode]["relatedData"]["baseLatticeMatrix"])
                                        elif deformerDataDic[deformerNode]["type"] == "sculpt":
                                            sculptList = cmds.sculpt(deformerDataDic[deformerNode]["shapeList"], name=deformerDataDic[deformerNode]["name"]) #[sculpt, sculptor, orig]
                                            newDefNode = sculptList[0]
                                            cmds.rename(sculptList[1], deformerDataDic[deformerNode]["relatedData"]["sculptor"])
                                            cmds.rename(sculptList[2], deformerDataDic[deformerNode]["relatedData"]["originLocator"])
                                        elif deformerDataDic[deformerNode]["type"] == "wrap":
                                            cmds.select(deformerDataDic[deformerNode]["shapeList"], deformerDataDic[deformerNode]["relatedNode"])
                                            mel.eval("CreateWrap;")
                                            hist = cmds.listHistory(deformerDataDic[deformerNode]["shapeList"])
                                            wrapList = cmds.ls(hist, type="wrap")[0]
                                            newDefNode = cmds.rename(wrapList, deformerDataDic[deformerNode]["name"])
                                        elif deformerDataDic[deformerNode]["type"] == "shrinkWrap":
                                            newDefNode = cmds.deformer(deformerDataDic[deformerNode]["shapeList"], type=deformerDataDic[deformerNode]["type"], name=deformerDataDic[deformerNode]["name"])[0] #shrinkWrap
                                            for cAttr in ["continuity", "smoothUVs", "keepBorder", "boundaryRule", "keepHardEdge", "propagateEdgeHardness", "keepMapBorders"]:
                                                cmds.connectAttr(deformerDataDic[deformerNode]["relatedNode"]+"."+cAttr, newDefNode+"."+cAttr, force=True)
                                            cmds.connectAttr(deformerDataDic[deformerNode]["relatedNode"]+".worldMesh", newDefNode+".targetGeom", force=True)
                                        elif deformerDataDic[deformerNode]["type"] == "wire":
                                            if not cmds.objExists(deformerDataDic[deformerNode]["relatedNode"]):
                                                isPeriodic = False
                                                if deformerDataDic[deformerNode]["relatedData"]["form"] == 2:
                                                    isPeriodic = True
                                                cmds.curve(name=deformerDataDic[deformerNode]["relatedNode"], periodic=isPeriodic, point=deformerDataDic[deformerNode]["relatedData"]["point"], degree=deformerDataDic[deformerNode]["relatedData"]["degree"], knot=deformerDataDic[deformerNode]["relatedData"]["knot"])
                                            newDefNode = cmds.wire(deformerDataDic[deformerNode]["shapeList"], wire=deformerDataDic[deformerNode]["relatedNode"], name=deformerDataDic[deformerNode]["name"])[0] #wire
                                        elif deformerDataDic[deformerNode]["nonLinear"]:
                                            nonLinearList = cmds.nonLinear(deformerDataDic[deformerNode]["shapeList"], type=deformerDataDic[deformerNode]["nonLinear"], name=deformerDataDic[deformerNode]["name"]) #[def, handle] bend, flare, sine, squash, twist, wave
                                            newDefNode = nonLinearList[0]
                                            cmds.rename(nonLinearList[1], deformerDataDic[deformerNode]["relatedData"])
                                        else: #solidify, proximityWrap, morph, textureDeformer, jiggle
                                            newDefNode = cmds.deformer(deformerDataDic[deformerNode]["shapeList"], type=deformerDataDic[deformerNode]["type"], name=deformerDataDic[deformerNode]["name"])[0]
                                        
                                        # import attribute values
                                        if newDefNode:
                                            for attr in deformerDataDic[deformerNode]["attributes"].keys():
                                                cmds.setAttr(newDefNode+"."+attr, deformerDataDic[deformerNode]["attributes"][attr])

                                        # import deformer weights, except for skinCluster, blendShape, sculpt, wrap
                                        weightsDic = deformerDataDic[deformerNode]["weights"]
                                        if weightsDic:
                                            for s, shape in enumerate(deformerDataDic[deformerNode]["shapeList"]):
                                                if weightsDic[str(s)]:
                                                    # cluster, deltaMush, tension, ffd, shrinkWrap, wire, nonLinear, solidify, proximityWrap, textureDeformer, jiggle
                                                    self.defWeights.setDeformerWeights(deformerDataDic[deformerNode]["name"], weightsDic[str(s)], s)

                                        ##

                                        # TODO
                                        # wrap geometry setup
                                        #
                                        #
                                        

                                    except Exception as e:
                                        self.notWorkedWellIO(self.exportedList[-1]+": "+deformerNode+" - "+str(e))
                                if wellImported:
                                    self.wellDoneIO(', '.join(toImportList))
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(deformerDataDic.keys())))
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
