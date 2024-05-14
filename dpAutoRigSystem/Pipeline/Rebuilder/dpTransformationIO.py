# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "TransformationIO"
TITLE = "r037_transformationIO"
DESCRIPTION = "r038_transformationIODesc"
ICON = "/Icons/dp_transformationIO.png"

DP_TRANSFORMATIONIO_VERSION = 1.0


class TransformationIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_TRANSFORMATIONIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
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
                        progressAmount = 0
                        maxProcess = len(transformList)
                        if self.verbose:
                            # Update progress window
                            progressAmount += 1
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                        # define dictionary to export
                        transformDic = {}
                        transformList = self.utils.filterTransformList(transformList)
                        for item in transformList:
                            dataDic = self.getTransformation(item)
                            if dataDic:
                                transformDic[item] = dataDic
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                            self.pipeliner.saveJsonFile(transformDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except Exception as e:
                            self.notWorkedWellIO(jsonName+": "+str(e))
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes'])
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            transformDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if transformDic:
                                progressAmount = 0
                                maxProcess = len(transformDic.keys())
                                # define lists to check result
                                wellImportedList = []
                                for item in transformDic.keys():
                                    notFoundNodesList = []
                                    # check transformations
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" "+item[item.rfind("|"):]))
                                    if not cmds.objExists(item):
                                        item = item[item.rfind("|")+1:] #short name (after last "|")
                                    if cmds.objExists(item):
                                        for attr in transformDic[item].keys():
                                            # unlock attribute
                                            wasLocked = cmds.getAttr(item+"."+attr, lock=True)
                                            cmds.setAttr(item+"."+attr, lock=False)
                                            try:
                                                # set transformation value
                                                cmds.setAttr(item+"."+attr, transformDic[item][attr])
                                                # lock attribute again if it was locked
                                                cmds.setAttr(item+"."+attr, lock=wasLocked)
                                                if not item in wellImportedList:
                                                    wellImportedList.append(item)
                                            except Exception as e:
                                                self.notWorkedWellIO(item+" - "+str(e))
                                    else:
                                        notFoundNodesList.append(item)
                                if wellImportedList:
                                    self.wellDoneIO(', '.join(wellImportedList))
                                else:
                                    self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
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


    def getTransformation(self, item, *args):
        """ Returns a dictionary with the transformation attribute values of the given transform node.
        """
        dic = {}
        for attr, default in zip(["tx", "ty",  "tz",  "rx",  "ry",  "rz",  "sx",  "sy",  "sz"], [0, 0, 0, 0, 0, 0, 1, 1, 1]):
            value = cmds.getAttr(item+"."+attr)
            if not value == default:
                if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                    dic[attr] = cmds.getAttr(item+"."+attr)
        return dic
