# importing libraries:
from maya import cmds
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
                        hasDef = False
                        print("meshList = ", meshList)
                        
                        inputDeformerList = cmds.listHistory(meshList, pruneDagObjects=False, interestLevel=True)
                        for deformerType in list(self.defWeights.typeAttrDic.keys()):
                            if cmds.ls(inputDeformerList, type=deformerType):
                                hasDef = True
                                break
                        
                        #deformerTypeList = self.defWeights.getDeformedModelList(deformTypeList=self.defWeights.typeAttrDic.keys())
                        print("inputDeformerList = ", inputDeformerList)
                        #print("deformerTypeList = ", deformerTypeList)
                        #if transformList:

                        if hasDef:

                            # WIP
                            #
                            deformerDataDic = {}


                            progressAmount = 0
                            maxProcess = len(meshList)

                            for deformerType in list(self.defWeights.typeAttrDic.keys()):
                                deformerList = cmds.ls(selection=False, type=deformerType)
                                if deformerList:
                                    for deformerNode in deformerList:
                                        if deformerNode in inputDeformerList:

                                            print("deformerNode =", deformerNode)

                                            deformerDataDic[deformerNode] = self.defWeights.getDeformerData(deformerNode)
                                            

                                            
                                            
                                                
                                            # Get shape indexes for the deformer so we can query the deformer weights
                                            shapeList = cmds.ls(cmds.deformer(deformerNode, query=True, geometry=True), long=True)
                                            indexList = cmds.deformer(deformerNode, query=True, geometryIndices=True)
                                            shapeToIndexDic = dict(zip(shapeList, indexList))
                                            
                                            print("shapeList =", shapeList)
                                            print("indexList =", indexList)
                                            print("shapeToIndexDic =", shapeToIndexDic)

                                            deformerDataDic[deformerNode][deformerType]["shapeList"] = shapeList
                                            deformerDataDic[deformerNode][deformerType]["indexList"] = indexList
                                            deformerDataDic[deformerNode][deformerType]["shapeToIndexDic"] = shapeToIndexDic
                                            
                                            for shape in shapeList:
                                                print("shape =", shape)
                                                # Get weights
                                                index = shapeToIndexDic[shape]
                                                print("index =", index)
                                                weights = self.defWeights.getDeformerWeights(deformerNode, index)
                                                print("weights =", weights)
                                                deformerDataDic[deformerNode][deformerType]["weights"] = weights
                                                print("deformerDataDic =", deformerDataDic)
                                                #{

                                                #                                        "envelope" : cmds.getAttr()


                                                #}


#                            for meshNode in meshList:
#                                defNodeList = []
#                                histList = cmds.listHistory(meshNode, pruneDagObjects=False, interestLevel=True)
#                                if histList:
#                                    for histNode in histList:
#                                            if cmds.objectType(histNode) == deformerType:
#                                                defNodeList.append(histNode)
#                                                print("meshNode, histNode, deformerType, defNodeList = ", meshNode, histNode, deformerType, defNodeList)


                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
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
                        skinWeightDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                        if skinWeightDic:
                            progressAmount = 0
                            maxProcess = len(skinWeightDic.keys())
                            wellImported = True
                            toImportList, notFoundMeshList, changedTopoMeshList, changedShapeMeshList = [], [], [], []
                            for mesh in skinWeightDic.keys():
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                                if cmds.objExists(mesh):
                                    toImportList.append(mesh)
                                else:
                                    notFoundMeshList.append(mesh)
                            if toImportList:
                                try:
                                    # import skin weights
                                    self.dpUIinst.skin.importSkinWeightsFromFile(toImportList, self.ioPath, self.exportedList[-1])
                                    self.wellDoneIO(', '.join(toImportList))
                                except Exception as e:
                                    self.notWorkedWellIO(self.exportedList[-1]+": "+str(e))
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(skinWeightDic.keys())))
                            if not wellImported:
                                if changedShapeMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" shape "+str(', '.join(changedShapeMeshList)))
                                elif changedTopoMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" topology "+str(', '.join(changedTopoMeshList)))
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
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic

