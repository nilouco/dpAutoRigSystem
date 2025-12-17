# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "TransformationIO"
TITLE = "r037_transformationIO"
DESCRIPTION = "r038_transformationIODesc"
ICON = "/Icons/dp_transformationIO.png"
WIKI = "10-‐-Rebuilder#-transformation"

DP_TRANSFORMATIONIO_VERSION = 1.02


class TransformationIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_TRANSFORMATIONIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_transformationIO"
        self.startName = "dpTransformation"
    

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
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    if self.firstMode: #export
                        transformList = None
                        if objList:
                            transformList = objList
                        else:
                            transformList = cmds.ls(selection=False, long=True, type="transform")
                        if transformList:
                            self.exportDicToJsonFile(self.getTransformDataDic(transformList))
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes'])
                    else: #import
                        transformDic = self.importLatestJsonFile(self.getExportedList())
                        if transformDic:
                            self.importTransformation(transformDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getTransformDataDic(self, itemList, *args):
        """ Return the transform data info to export.
        """
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        # define dictionary to export
        transformDic = {}
        itemList = self.utils.filterTransformList(itemList, filterLattice=False, filterBaseName=False, verbose=self.verbose, title=self.dpUIinst.lang[self.title])
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            useThisTransform = True
            if cmds.objExists(item+".dpNotTransformIO"):
                if cmds.getAttr(item+".dpNotTransformIO") == 1:
                    useThisTransform = False
            if useThisTransform:
                dataDic = self.getTransformation(item)
                dataDic.update(self.getLimit(item))
                if dataDic:
                    transformDic[item] = dataDic
        return transformDic


    def getTransformation(self, item, *args):
        """ Returns a dictionary with the transformation attribute values of the given transform node.
        """
        dic = {}
        needGetData = True
        for attr, default in zip(["tx", "ty",  "tz",  "rx",  "ry",  "rz",  "sx",  "sy",  "sz"], [0, 0, 0, 0, 0, 0, 1, 1, 1]):
            value = cmds.getAttr(item+"."+attr)
            if not value == default:
                if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                    if needGetData:
                        dic = { 
                                "transform" : {},
                                "matrix" : cmds.xform(item, query=True, worldSpace=False, matrix=True)
                                }
                        needGetData = False
                    dic["transform"][attr] = cmds.getAttr(item+"."+attr)
        return dic


    def getLimit(self, item, *args):
        """ Returns a dictionary with the transformation limits if there are.
        """
        dic = {}
        enableList = []
        enableAttrList = ["enableTranslationX", "enableTranslationY", "enableTranslationZ", "enableRotationX", "enableRotationY", "enableRotationZ", "enableScaleX", "enableScaleY", "enableScaleZ"]
        enableList.append(cmds.transformLimits(item, enableTranslationX=True, query=True))
        enableList.append(cmds.transformLimits(item, enableTranslationY=True, query=True))
        enableList.append(cmds.transformLimits(item, enableTranslationZ=True, query=True))
        enableList.append(cmds.transformLimits(item, enableRotationX=True, query=True))
        enableList.append(cmds.transformLimits(item, enableRotationY=True, query=True))
        enableList.append(cmds.transformLimits(item, enableRotationZ=True, query=True))
        enableList.append(cmds.transformLimits(item, enableScaleX=True, query=True))
        enableList.append(cmds.transformLimits(item, enableScaleY=True, query=True))
        enableList.append(cmds.transformLimits(item, enableScaleZ=True, query=True))
        hasTrue = [i for i in enableList if True in i]
        if hasTrue:
            limitList = []
            #limitAttrList = ["translationX", "translationY", "translationZ", "rotationX", "rotationY", "rotationZ", "scaleX", "scaleY", "scaleZ"]
            limitList.append(cmds.transformLimits(item, translationX=True, query=True))
            limitList.append(cmds.transformLimits(item, translationY=True, query=True))
            limitList.append(cmds.transformLimits(item, translationZ=True, query=True))
            limitList.append(cmds.transformLimits(item, rotationX=True, query=True))
            limitList.append(cmds.transformLimits(item, rotationY=True, query=True))
            limitList.append(cmds.transformLimits(item, rotationZ=True, query=True))
            limitList.append(cmds.transformLimits(item, scaleX=True, query=True))
            limitList.append(cmds.transformLimits(item, scaleY=True, query=True))
            limitList.append(cmds.transformLimits(item, scaleZ=True, query=True))
            dic = {"limit" : {}}
            for e, enableAttr in enumerate(enableAttrList):
                if True in enableList[e]:
                    dic["limit"][enableAttr] = [
                                                int(enableList[e][0]), #minEnable
                                                int(enableList[e][1]), #maxEnable
                                                limitList[e][0], #minValue
                                                limitList[e][1] #maxValue
                                            ]
        return dic


    def importTransformation(self, transformDic, *args):
        """ Import transfomation data from given dictionary.
        """
        self.utils.setProgress(max=len(transformDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in transformDic.keys():
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            notFoundNodesList = []
            # check transform
            #if not cmds.objExists(item):
            #    item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                ran = False
                if "transform" in transformDic[item].keys():
                    ran = True
                    for attr in transformDic[item]["transform"].keys():
                        if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                            # unlock attribute
                            wasLocked = cmds.getAttr(item+"."+attr, lock=True)
                            cmds.setAttr(item+"."+attr, lock=False)
                            try:
                                # set transformation value
                                cmds.setAttr(item+"."+attr, transformDic[item]["transform"][attr])
                                # lock attribute again if it was locked
                                cmds.setAttr(item+"."+attr, lock=wasLocked)
                                if not item in wellImportedList:
                                    wellImportedList.append(item)
                            except Exception as e:
                                self.notWorkedWellIO(item+" - "+str(e))
                    cmds.xform(item, worldSpace=False, matrix=transformDic[item]["matrix"])
                if "limit" in transformDic[item].keys():
                    ran = True
                    for limitAttr in transformDic[item]["limit"].keys():
                        try:
                            if limitAttr == "enableTranslationX":
                                cmds.transformLimits(item, enableTranslationX=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], translationX=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableTranslationY":
                                cmds.transformLimits(item, enableTranslationY=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], translationY=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableTranslationZ":
                                cmds.transformLimits(item, enableTranslationZ=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], translationZ=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableRotationX":
                                cmds.transformLimits(item, enableRotationX=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], rotationX=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableRotationY":
                                cmds.transformLimits(item, enableRotationY=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], rotationY=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableRotationZ":
                                cmds.transformLimits(item, enableRotationZ=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], rotationZ=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableScaleX":
                                cmds.transformLimits(item, enableScaleX=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], scaleX=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableScaleY":
                                cmds.transformLimits(item, enableScaleY=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], scaleY=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                            elif limitAttr == "enableScaleZ":
                                cmds.transformLimits(item, enableScaleZ=[transformDic[item]["limit"][limitAttr][0], transformDic[item]["limit"][limitAttr][1]], scaleZ=[transformDic[item]["limit"][limitAttr][2], transformDic[item]["limit"][limitAttr][3]])
                        except Exception as e:
                            self.notWorkedWellIO(item+" - "+str(e))
                if not ran:
                    self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes'])
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(self.latestDataFile)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
